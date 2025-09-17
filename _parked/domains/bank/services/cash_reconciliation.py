"""
Cash Reconciliation Engine for Service Contractors - V1

This engine handles the direct matching of cash deposits (payments) to outstanding invoices,
implementing the sophisticated payment matching algorithm that was previously embedded
in the monolithic reconciliation service.
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import uuid
import math
from enum import Enum
from itertools import combinations
from domains.bank.models.bank_transaction import BankTransaction
from domains.ar.services.types import MatchConfidence, PaymentMatch
from domains.identity_graph import services as ig, consolidate as igc


class CashReconciliationService:
    def __init__(self, db: Session):
        self.db = db
        self.confidence_threshold = MatchConfidence.MEDIUM.value
        self.fuzzy_match_tolerance = 0.03  # 3% variance allowed
        self.max_date_variance_days = 30
        self.max_bundle_candidates = 20

    def match_payments_to_invoices(self, transactions: List[Any], invoices: List[Dict]) -> List[PaymentMatch]:
        """
        Main entry point for the cash reconciliation process.
        Iterates through payments or bank transactions and applies various matching strategies.
        """
        if isinstance(transactions[0], BankTransaction):
            transactions_dict = [
                {
                    "amount": t.amount * 100,  # Convert to cents
                    "created": t.date.isoformat(),
                    "id": t.external_id or str(t.transaction_id),
                    "fee": t.unbundle_meta.get("fee", 0) if t.unbundle_meta else 0
                } for t in transactions
            ]
        else:
            transactions_dict = transactions

        matches = []
        unmatched_transactions = []

        for tx in transactions_dict:
            # Strategies: exact -> fuzzy -> bundled
            exact_match_invoice = self.find_exact_invoice_match(tx, invoices)
            if exact_match_invoice:
                match = PaymentMatch(
                    stripe_payment_id=tx.get("id", "unknown"),
                    jobber_invoice_ids=[exact_match_invoice["id"]],
                    job_ids=[exact_match_invoice["job_id"]],
                    confidence=MatchConfidence.HIGH.value,
                    match_type="exact",
                    variance_amount=0.0,
                    variance_percentage=0.0,
                    requires_human_review=False,
                    suggested_action="auto_match",
                    allocated_fees={},
                    rationale={"reason": "Exact amount match within reasonable time frame."}
                )
                matches.append(match)
                continue

            fuzzy_matches = self.find_fuzzy_invoice_matches(tx, invoices)
            if fuzzy_matches:
                best_fuzzy_match = max(fuzzy_matches, key=lambda x: x["confidence"])
                if best_fuzzy_match["confidence"] >= self.confidence_threshold:
                    variance = (tx["amount"] / 100) - best_fuzzy_match["invoice"]["amount"]
                    variance_pct = abs(variance) / best_fuzzy_match["invoice"]["amount"] * 100
                    match = PaymentMatch(
                        stripe_payment_id=tx.get("id", "unknown"),
                        jobber_invoice_ids=[best_fuzzy_match["invoice"]["id"]],
                        job_ids=[best_fuzzy_match["invoice"]["job_id"]],
                        confidence=best_fuzzy_match["confidence"],
                        match_type="fuzzy",
                        variance_amount=variance,
                        variance_percentage=variance_pct,
                        requires_human_review=variance_pct > 5.0,
                        suggested_action="review_variance" if variance_pct > 5.0 else "auto_match",
                        allocated_fees={},
                        rationale={
                            "reason": "Fuzzy amount match within tolerance.",
                            "confidence_score": best_fuzzy_match["confidence"],
                            "variance": variance,
                            "variance_percentage": variance_pct
                        }
                    )
                    matches.append(match)
                    continue

            bundled_match = self.find_bundled_invoice_matches(tx, invoices)
            if bundled_match:
                total_invoice_amount = sum(inv["amount"] for inv in bundled_match["invoices"])
                variance = (tx["amount"] / 100) - total_invoice_amount
                variance_pct = abs(variance) / total_invoice_amount * 100 if total_invoice_amount > 0 else 100
                match = PaymentMatch(
                    stripe_payment_id=tx.get("id", "unknown"),
                    jobber_invoice_ids=[inv["id"] for inv in bundled_match["invoices"]],
                    job_ids=[inv["job_id"] for inv in bundled_match["invoices"]],
                    confidence=bundled_match["confidence"],
                    match_type="bundled",
                    variance_amount=variance,
                    variance_percentage=variance_pct,
                    requires_human_review=bundled_match["confidence"] < 0.9,
                    suggested_action="review_bundled_payment" if bundled_match["confidence"] < 0.9 else "auto_match",
                    allocated_fees={},
                    rationale=bundled_match.get("rationale", {"reason": "Bundled invoice match."})
                )
                matches.append(match)
                continue

            unmatched_transactions.append(tx)

        for tx in unmatched_transactions:
            matches.append(PaymentMatch(
                stripe_payment_id=tx.get("id", "unknown"),
                jobber_invoice_ids=[],
                job_ids=[],
                confidence=MatchConfidence.MANUAL_REVIEW.value,
                match_type="unmatched",
                variance_amount=tx["amount"] / 100,
                variance_percentage=100.0,
                requires_human_review=True,
                suggested_action="manual_investigation_required",
                allocated_fees={},
                rationale={"reason": "No matching invoices found."}
            ))

        return matches

    def save_matches(self, matches: List[PaymentMatch], firm_id: str):
        for match in matches:
            transaction = self.db.query(BankTransaction).filter(
                BankTransaction.firm_id == firm_id,
                BankTransaction.external_id == match.stripe_payment_id
            ).first()
            if transaction:
                transaction.invoice_ids = match.jobber_invoice_ids
                transaction.unbundle_meta = match.rationale
                transaction.confidence = match.confidence
                transaction.status = "matched" if not match.requires_human_review else "pending"
        self.db.commit()

    def find_exact_invoice_match(self, payment: Dict, invoices: List[Dict]) -> Optional[Dict]:
        payment_amount = payment["amount"] / 100
        for invoice in invoices:
            if abs(invoice["amount"] - payment_amount) < 0.01:
                if self._is_timing_reasonable(payment, invoice):
                    return invoice
        return None

    def find_fuzzy_invoice_matches(self, payment: Dict, invoices: List[Dict]) -> List[Dict]:
        payment_amount = payment["amount"] / 100
        matches = []
        for invoice in invoices:
            variance = abs(invoice["amount"] - payment_amount)
            variance_pct = variance / invoice["amount"] if invoice["amount"] > 0 else 1.0
            if variance_pct <= self.fuzzy_match_tolerance:
                timing_score = self._calculate_timing_score(payment, invoice)
                amount_score = 1.0 - variance_pct
                overall_confidence = (amount_score * 0.7) + (timing_score * 0.3)
                if overall_confidence >= MatchConfidence.LOW.value:
                    matches.append({
                        "invoice": invoice,
                        "confidence": overall_confidence,
                        "variance": variance,
                        "variance_percentage": variance_pct * 100
                    })
        return sorted(matches, key=lambda x: x["confidence"], reverse=True)

    def find_bundled_invoice_matches(self, payment: Dict, invoices: List[Dict]) -> Optional[Dict]:
        payment_gross = payment["amount"] / 100
        payment_fee = payment.get("fee", 0) / 100
        payment_date = self._parse_payment_datetime(payment["created"])

        candidates = self._pre_filter_candidates(payment, invoices)
        if not candidates:
            return None

        best_combo = self._find_best_subset_sum(payment_gross, candidates)

        if not best_combo:
            return None

        combo_total = sum(inv["amount"] for inv in best_combo)
        variance = payment_gross - combo_total
        combo_size = len(best_combo)

        confidence = self._calculate_fee_aware_confidence(payment_gross, payment_fee, combo_total, variance, combo_size)

        if confidence < MatchConfidence.MEDIUM.value:
            return None

        avg_days = sum(inv.get("days_from_payment", 0) for inv in best_combo) / combo_size
        tiebreak_score = (combo_size, avg_days, abs(variance))

        return {
            "invoices": [dict({k: v for k, v in inv.items() if k != "days_from_payment"}) for inv in best_combo],
            "confidence": confidence,
            "total_amount": combo_total,
            "variance": variance,
            "rationale": {
                "confidence_score": confidence,
                "amount_total": combo_total,
                "variance": variance,
                "payment_fee": payment_fee,
                "combo_size": combo_size,
                "avg_days_from_payment": round(avg_days, 2),
                "tiebreak_score": tiebreak_score
            }
        }

    def _pre_filter_candidates(self, payment: Dict, invoices: List[Dict]) -> List[Dict]:
        payment_gross = payment["amount"] / 100
        payment_date = self._parse_payment_datetime(payment["created"])

        candidates = []
        for invoice in invoices:
            invoice_date_str = invoice.get("paid_date") or invoice.get("due_date")
            if not invoice_date_str:
                continue

            try:
                invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d")
            except ValueError:
                continue

            days_diff = abs((payment_date.date() - invoice_date.date()).days)
            if days_diff <= self.max_date_variance_days:
                inv_copy = dict(invoice)
                inv_copy["days_from_payment"] = days_diff
                candidates.append(inv_copy)

        if not candidates:
            return []

        payment_customer = payment.get("metadata", {}).get("customer")
        if payment_customer:
            customer_candidates = [inv for inv in candidates if inv.get("customer") == payment_customer]
            if len(customer_candidates) > 0:
                candidates = customer_candidates

        upper_band = payment_gross * (1.0 + self.fuzzy_match_tolerance)
        candidates = [inv for inv in candidates if inv["amount"] <= upper_band]

        candidates.sort(key=lambda inv: inv.get("days_from_payment", 9999))

        return candidates[:self.max_bundle_candidates]

    def _find_best_subset_sum(self, payment_gross: float, candidates: List[Dict]) -> Optional[List[Dict]]:
        target_cents = int(payment_gross * 100)
        dp = {0: ([], 0)}

        sorted_candidates = sorted(candidates, key=lambda x: x['amount'], reverse=True)

        for invoice in sorted_candidates:
            invoice_cents = int(invoice["amount"] * 100)
            if invoice_cents <= 0:
                continue

            new_dp_entries = {}
            for current_sum, (combo, num_items) in dp.items():
                new_sum = current_sum + invoice_cents
                if new_sum <= target_cents + (self.fuzzy_match_tolerance * target_cents):
                    if new_sum not in dp or num_items + 1 < dp[new_sum][1]:
                        new_dp_entries[new_sum] = (combo + [invoice], num_items + 1)
            dp.update(new_dp_entries)

        best_combo = None
        min_variance = float('inf')

        lower_bound = int(target_cents * (1.0 - self.fuzzy_match_tolerance))

        for amount_cents in range(target_cents, lower_bound - 1, -1):
            if amount_cents in dp:
                variance = abs(target_cents - amount_cents)
                if variance < min_variance:
                    min_variance = variance
                    best_combo = dp[amount_cents][0]

        return best_combo

    def _calculate_fee_aware_confidence(self, payment_gross: float, payment_fee: float, combo_total: float, variance: float, combo_size: int) -> float:
        if abs(variance) <= 0.01:
            return MatchConfidence.HIGH.value

        if payment_fee > 0:
            fee_diff = abs(abs(variance) - payment_fee)
            if fee_diff <= 0.50:
                return MatchConfidence.HIGH.value
            else:
                confidence = MatchConfidence.HIGH.value - (fee_diff / max(payment_fee, 1.0))
                return max(MatchConfidence.LOW.value, confidence)

        expected_stripe_fee = (combo_total * 0.029) + 0.30
        fee_diff = abs(abs(variance) - expected_stripe_fee)

        if fee_diff <= 0.50:
            return MatchConfidence.HIGH.value
        elif fee_diff <= 2.00:
            confidence = MatchConfidence.HIGH.value - (fee_diff / expected_stripe_fee)
            return max(MatchConfidence.MEDIUM.value, confidence)
        elif abs(variance) <= payment_gross * 0.05:
            return MatchConfidence.MEDIUM.value
        else:
            return MatchConfidence.LOW.value

    def _parse_payment_datetime(self, payment_created_str: str) -> datetime:
        if payment_created_str.endswith('Z'):
            payment_created_str = payment_created_str.replace('Z', '+00:00')
        return datetime.fromisoformat(payment_created_str)

    def _is_timing_reasonable(self, payment: Dict, invoice: Dict) -> bool:
        if not invoice.get("paid_date"):
            return False
        payment_date = self._parse_payment_datetime(payment["created"])
        paid_date = datetime.strptime(invoice["paid_date"], "%Y-%m-%d")
        return abs((payment_date.date() - paid_date.date()).days) <= self.max_date_variance_days

    def _calculate_timing_score(self, payment: Dict, invoice: Dict) -> float:
        if not invoice.get("paid_date"):
            return 0.0
        payment_date = self._parse_payment_datetime(payment["created"])
        paid_date = datetime.strptime(invoice["paid_date"], "%Y-%m-%d")
        days_diff = abs((payment_date.date() - paid_date.date()).days)
        if days_diff == 0:
            return 1.0
        elif days_diff <= 7:
            return 0.9
        elif days_diff <= 30:
            return 0.7
        else:
            return 0.3



    def persist_graph_and_ledger(self, company_id: str, tx: dict, match: PaymentMatch, bank_account_id: str, bank_posted_date_iso: str):
        # Create/lookup identities
        # Settlement (bank txn)
        settle_fp = ig.fingerprint("SETTLEMENT", provider="PLAID",
                                account_id=bank_account_id,
                                amount_cents=abs(int(tx["amount"])),  # cents
                                posted_date=bank_posted_date_iso,
                                merchant_norm=(tx.get("merchant") or ""))
        settle_id = ig.upsert_identity(self.db, company_id, "SETTLEMENT", settle_fp)

        # Payout (if tx originated from processor; optional now)
        payout_id = None
        if match.match_type in ("bundled","fuzzy","exact"):   # treat as processor-origin if metadata says so
            payout_fp = ig.fingerprint("PAYOUT", provider=(tx.get("provider") or "UNKNOWN"),
                                    external_id=tx.get("id","unknown"))
            payout_id = ig.upsert_identity(self.db, company_id, "PAYOUT", payout_fp)
            ig.add_edge(self.db, company_id, payout_id, settle_id, "SETTLES")

        # Invoices/Payments (ops)
        for inv_id in match.jobber_invoice_ids:
            inv_fp = ig.fingerprint("INVOICE", provider="JOBBER", external_id=str(inv_id))
            inv_ident = ig.upsert_identity(self.db, company_id, "INVOICE", inv_fp)
            # Optional: CHARGE/REFUND layer later; for now you can edge invoice→payout for explain
            if payout_id:
                ig.add_edge(self.db, company_id, inv_ident, payout_id, "COMPOSED_OF")

        # Link raw_event if you’re creating them (optional right now)
        # ig.link_raw(...)

        # Ledger: one INFLOW at bank settlement date
        net_cents = int(tx["amount"])  # signed? make positive inflow
        igc.consolidate_payout_settlement(self.db, company_id, payout_id or settle_id, settle_id, abs(net_cents), bank_posted_date_iso)
        self.db.commit()
