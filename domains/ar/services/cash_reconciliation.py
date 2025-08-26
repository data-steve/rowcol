"""
Cash Reconciliation Engine for Service Contractors - V1

This engine handles the direct matching of cash deposits (payments) to outstanding invoices,
implementing the sophisticated payment matching algorithm that was previously embedded
in the monolithic reconciliation service.

The Cash Reconciliation Problem:
Service contractors receive payments through various channels (Stripe, checks, ACH) that
often don't align perfectly with individual invoices:
- Customers pay multiple invoices in a single transaction
- Payment processors deduct fees, creating variance
- Payments arrive days or weeks after invoices are issued
- Bundled payments may cover partial invoices or multiple jobs

Algorithm Strategy:

1. **Exact Matching (Highest Confidence)**: 
   - Direct 1:1 amount matches within reasonable time windows
   - Handles the majority of simple, clean payments
   - Immediate auto-matching with high confidence scores

2. **Fuzzy Matching (Medium Confidence)**:
   - Single invoice matches within tight tolerance (3%)
   - Accounts for minor discrepancies, rounding, small fees
   - Temporal weighting favors recent invoices

3. **Bundled Matching (Complex Algorithm)**:
   - Combinatorial search through invoice combinations
   - Fee-aware confidence scoring using actual processor fees
   - Sophisticated pre-filtering and candidate capping
   - Tie-breaking based on simplicity, recency, and variance

Core Innovations:
- **Fee-Aware Scoring**: Prioritizes actual payment fees over estimates
- **Temporal Boosting**: Recent invoices score higher than old ones  
- **Candidate Pre-filtering**: Reduces combinatorial explosion through smart filtering
- **Confidence Transparency**: Detailed rationale for human-in-the-loop review
- **Performance Guardrails**: Caps candidate sets to prevent timeout issues

This service is designed to handle the 80% of payments that can be automatically
matched with high confidence, while flagging the remaining 20% for human review
with detailed context about why matching was difficult.
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

from .types import MatchConfidence, PaymentMatch


class CashReconciliationService:
    """
    Handles the direct matching of cash deposits (payments) to outstanding invoices.
    This service is responsible for the "cash reconciliation" part of the workflow.
    """

    def __init__(self, db: Session):
        self.db = db
        self.confidence_threshold = MatchConfidence.MEDIUM.value
        self.fuzzy_match_tolerance = 0.03  # 3% variance allowed
        self.max_date_variance_days = 30
        self.max_bundle_candidates = 20

    def match_payments_to_invoices(self, stripe_payments: List[Dict], invoices: List[Dict]) -> List[PaymentMatch]:
        """
        Main entry point for the cash reconciliation process.
        Iterates through payments and applies various matching strategies.
        """
        matches = []
        unmatched_payments = []

        for payment in stripe_payments:
            # Strategies are applied in order of confidence: exact -> fuzzy -> bundled
            
            # Try exact amount matching first
            exact_match_invoice = self.find_exact_invoice_match(payment, invoices)
            if exact_match_invoice:
                match = PaymentMatch(
                    stripe_payment_id=payment.get("charge_id", payment.get("id", "unknown")),
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

            # Try fuzzy matching for partial payments or minor discrepancies
            fuzzy_matches = self.find_fuzzy_invoice_matches(payment, invoices)
            if fuzzy_matches:
                best_fuzzy_match = max(fuzzy_matches, key=lambda x: x["confidence"])
                if best_fuzzy_match["confidence"] >= self.confidence_threshold:
                    variance = (payment["amount"] / 100) - best_fuzzy_match["invoice"]["amount"]
                    variance_pct = abs(variance) / best_fuzzy_match["invoice"]["amount"] * 100
                    match = PaymentMatch(
                        stripe_payment_id=payment.get("charge_id", payment.get("id", "unknown")),
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

            # Finally, try to find a bundle of invoices that match the payment
            bundled_match = self.find_bundled_invoice_matches(payment, invoices)
            if bundled_match:
                total_invoice_amount = sum(inv["amount"] for inv in bundled_match["invoices"])
                variance = (payment["amount"] / 100) - total_invoice_amount
                variance_pct = abs(variance) / total_invoice_amount * 100 if total_invoice_amount > 0 else 100
                match = PaymentMatch(
                    stripe_payment_id=payment.get("charge_id", payment.get("id", "unknown")),
                    jobber_invoice_ids=[inv["id"] for inv in bundled_match["invoices"]],
                    job_ids=[inv["job_id"] for inv in bundled_match["invoices"]],
                    confidence=bundled_match["confidence"],
                    match_type="bundled",
                    variance_amount=variance,
                    variance_percentage=variance_pct,
                    requires_human_review=bundled_match["confidence"] < 0.9,  # High confidence bundled matches can auto-match
                    suggested_action="review_bundled_payment" if bundled_match["confidence"] < 0.9 else "auto_match",
                    allocated_fees={},
                    rationale=bundled_match.get("rationale", {"reason": "Bundled invoice match."})
                )
                matches.append(match)
                continue

            # If no strategies succeed, mark the payment as unmatched
            unmatched_payments.append(payment)

        # Handle any remaining unmatched payments
        for payment in unmatched_payments:
            matches.append(PaymentMatch(
                stripe_payment_id=payment.get("charge_id", payment.get("id", "unknown")),
                jobber_invoice_ids=[],
                job_ids=[],
                confidence=MatchConfidence.MANUAL_REVIEW.value,
                match_type="unmatched",
                variance_amount=payment["amount"] / 100,
                variance_percentage=100.0,
                requires_human_review=True,
                suggested_action="manual_investigation_required",
                allocated_fees={},
                rationale={"reason": "No matching invoices found."}
            ))

        return matches

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

        # --- Candidate Pre-filtering ---
        candidates = self._pre_filter_candidates(payment, invoices)
        if not candidates:
            return None

        # --- Dynamic Programming Subset Sum ---
        best_combo = self._find_best_subset_sum(payment_gross, candidates)
        
        if not best_combo:
            return None

        # --- Process the best match found by the DP algorithm ---
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
        """Applies various filters to reduce the search space for bundled matches."""
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
        
        if not candidates: return []

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
        """
        Finds the combination of invoices that sums closest to the payment amount
        using a dynamic programming approach to solve the subset sum problem.
        This is an O(n*W) solution, where n is number of invoices and W is the target amount.
        """
        target_cents = int(payment_gross * 100)
        
        # dp[i] stores a tuple: (list_of_invoices, num_invoices) that sum to i
        dp = {0: ([], 0)} 
        
        # Sort candidates by amount to potentially find simpler matches first
        sorted_candidates = sorted(candidates, key=lambda x: x['amount'], reverse=True)

        for invoice in sorted_candidates:
            invoice_cents = int(invoice["amount"] * 100)
            if invoice_cents <= 0:
                continue
            
            new_dp_entries = {}
            for current_sum, (combo, num_items) in dp.items():
                new_sum = current_sum + invoice_cents
                if new_sum <= target_cents + (self.fuzzy_match_tolerance * target_cents):
                    # If we haven't found a sum for this value yet, or if the new combo is simpler (fewer items), update it.
                    if new_sum not in dp or num_items + 1 < dp[new_sum][1]:
                        new_dp_entries[new_sum] = (combo + [invoice], num_items + 1)
            dp.update(new_dp_entries)

        # Find the best match within the tolerance window
        best_combo = None
        min_variance = float('inf')
        
        lower_bound = int(target_cents * (1.0 - self.fuzzy_match_tolerance))

        for amount_cents in range(target_cents, lower_bound -1, -1):
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

    # --- Helper Methods ---
    def _parse_payment_datetime(self, payment_created_str: str) -> datetime:
        # Simplified for brevity
        if payment_created_str.endswith('Z'):
            payment_created_str = payment_created_str.replace('Z', '+00:00')
        return datetime.fromisoformat(payment_created_str)

    def _is_timing_reasonable(self, payment: Dict, invoice: Dict) -> bool:
        if not invoice.get("paid_date"): return False
        payment_date = self._parse_payment_datetime(payment["created"])
        paid_date = datetime.strptime(invoice["paid_date"], "%Y-%m-%d")
        return abs((payment_date.date() - paid_date.date()).days) <= self.max_date_variance_days

    def _calculate_timing_score(self, payment: Dict, invoice: Dict) -> float:
        if not invoice.get("paid_date"): return 0.0
        payment_date = self._parse_payment_datetime(payment["created"])
        paid_date = datetime.strptime(invoice["paid_date"], "%Y-%m-%d")
        days_diff = abs((payment_date.date() - paid_date.date()).days)
        if days_diff == 0: return 1.0
        elif days_diff <= 7: return 0.9
        elif days_diff <= 30: return 0.7
        else: return 0.3
