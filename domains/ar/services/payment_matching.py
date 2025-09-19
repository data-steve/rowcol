"""
Payment Matching Service - AR Payment Processing and Reconciliation

This service handles AR payment business logic with sophisticated matching algorithms:
- Payment receipt and processing
- Multi-tier invoice matching: exact → fuzzy → bundled
- Confidence-based matching with scoring algorithms
- Deposit reconciliation with bank transactions
- Payment allocation across multiple invoices
- Payment dispute and adjustment handling

Incorporates proven algorithms from cash_reconciliation.py for robust payment matching.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from domains.ar.models.payment import ARPayment
from domains.core.services.base_service import TenantAwareService
from enum import Enum


class MatchConfidence(Enum):
    """Confidence levels for payment matching."""
    HIGH = 0.9
    MEDIUM = 0.7
    LOW = 0.5
    MANUAL_REVIEW = 0.0


class PaymentMatchingService(TenantAwareService):
    """
    Service for AR payment matching and reconciliation.
    
    Handles payment processing, invoice matching, and deposit reconciliation
    for accurate accounts receivable management.
    """
    
    def __init__(self, db: Session, business_id: str):
        super().__init__(business_id)
        self.db = db
        # Matching algorithm configuration
        self.confidence_threshold = MatchConfidence.MEDIUM.value
        self.fuzzy_match_tolerance = 0.03  # 3% variance allowed
        self.max_date_variance_days = 30
        self.max_bundle_candidates = 20
    
    def get_unallocated_amount(self, payment: ARPayment) -> float:
        """Calculate amount not yet allocated to invoices."""
        net_amount = payment.amount + payment.adjustment_amount
        
        if not payment.allocation_details:
            return net_amount
        
        allocated = sum(
            allocation.get("amount", 0) 
            for allocation in payment.allocation_details.get("allocations", [])
        )
        
        return net_amount - allocated
    
    def is_overpayment(self, payment: ARPayment) -> bool:
        """Check if this is an overpayment (more than invoice total)."""
        if payment.primary_invoice and payment.primary_invoice.total:
            net_amount = payment.amount + payment.adjustment_amount
            return net_amount > payment.primary_invoice.total
        return False
    
    def allocate_to_invoice(self, payment: ARPayment, invoice_id: int, amount: float, notes: str = None):
        """
        Allocate payment amount to a specific invoice.
        
        Args:
            payment: ARPayment instance
            invoice_id: ID of invoice to allocate to
            amount: Amount to allocate
            notes: Optional notes about allocation
        """
        if payment.allocation_details is None:
            payment.allocation_details = {"allocations": []}
        
        allocation = {
            "invoice_id": invoice_id,
            "amount": amount,
            "date": datetime.utcnow().isoformat(),
            "notes": notes
        }
        
        payment.allocation_details["allocations"].append(allocation)
        
        # Update allocation status
        total_allocated = sum(
            alloc.get("amount", 0) 
            for alloc in payment.allocation_details["allocations"]
        )
        
        net_amount = payment.amount + payment.adjustment_amount
        payment.is_fully_allocated = (total_allocated >= net_amount)
        
        # Update status if fully allocated
        if payment.is_fully_allocated and payment.status == "pending":
            payment.status = "matched"
        
        self.db.commit()
    
    def get_allocation_summary(self, payment: ARPayment) -> Dict[str, Any]:
        """Get summary of payment allocations."""
        net_amount = payment.amount + payment.adjustment_amount
        
        if not payment.allocation_details:
            return {
                "total_allocated": 0.0,
                "unallocated": net_amount,
                "allocation_count": 0,
                "allocations": []
            }
        
        allocations = payment.allocation_details.get("allocations", [])
        total_allocated = sum(alloc.get("amount", 0) for alloc in allocations)
        
        return {
            "total_allocated": total_allocated,
            "unallocated": net_amount - total_allocated,
            "allocation_count": len(allocations),
            "allocations": allocations
        }
    
    def auto_match_to_invoices(self, payment: ARPayment, customer_invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Automatically match payment to customer invoices using sophisticated three-tier algorithm.
        
        Matching strategies (in order):
        1. Exact amount match - highest confidence
        2. Fuzzy amount match - medium confidence with tolerance
        3. Bundled invoice match - multiple invoices that sum to payment amount
        
        Args:
            payment: ARPayment instance
            customer_invoices: List of customer's outstanding invoices
        
        Returns:
            Dictionary with matching results and confidence
        """
        if not customer_invoices:
            return {
                "matched": False,
                "confidence": MatchConfidence.MANUAL_REVIEW.value,
                "method": "no_invoices",
                "allocations": [],
                "requires_human_review": True,
                "rationale": {"reason": "No invoices available for matching"}
            }
        
        # Strategy 1: Exact amount match (highest confidence)
        exact_match = self._find_exact_invoice_match(payment, customer_invoices)
        if exact_match:
            self.allocate_to_invoice(payment, exact_match["invoice_id"], payment.amount)
            payment.primary_invoice_id = exact_match["invoice_id"]
            payment.matching_confidence = MatchConfidence.HIGH.value
            payment.matching_method = "exact"
            
            return {
                "matched": True,
                "confidence": MatchConfidence.HIGH.value,
                "method": "exact_amount",
                "allocations": [{"invoice_id": exact_match["invoice_id"], "amount": payment.amount}],
                "variance_amount": 0.0,
                "variance_percentage": 0.0,
                "requires_human_review": False,
                "rationale": {"reason": "Exact amount match within reasonable time frame"}
            }
        
        # Strategy 2: Fuzzy amount match (medium confidence)
        fuzzy_matches = self._find_fuzzy_invoice_matches(payment, customer_invoices)
        if fuzzy_matches:
            best_fuzzy = max(fuzzy_matches, key=lambda x: x["confidence"])
            if best_fuzzy["confidence"] >= self.confidence_threshold:
                invoice = best_fuzzy["invoice"]
                variance = payment.amount - invoice["balance"]
                variance_pct = abs(variance) / invoice["balance"] * 100
                
                self.allocate_to_invoice(payment, invoice["invoice_id"], payment.amount)
                payment.primary_invoice_id = invoice["invoice_id"]
                payment.matching_confidence = best_fuzzy["confidence"]
                payment.matching_method = "fuzzy"
                
                return {
                    "matched": True,
                    "confidence": best_fuzzy["confidence"],
                    "method": "fuzzy_amount",
                    "allocations": [{"invoice_id": invoice["invoice_id"], "amount": payment.amount}],
                    "variance_amount": variance,
                    "variance_percentage": variance_pct,
                    "requires_human_review": variance_pct > 5.0,
                    "rationale": {
                        "reason": "Fuzzy amount match within tolerance",
                        "confidence_score": best_fuzzy["confidence"],
                        "variance": variance,
                        "variance_percentage": variance_pct
                    }
                }
        
        # Strategy 3: Bundled invoice match (multiple invoices)
        bundled_match = self._find_bundled_invoice_matches(payment, customer_invoices)
        if bundled_match:
            # Allocate across all matched invoices
            for invoice in bundled_match["invoices"]:
                self.allocate_to_invoice(payment, invoice["invoice_id"], invoice["balance"])
            
            payment.primary_invoice_id = bundled_match["invoices"][0]["invoice_id"]
            payment.matching_confidence = bundled_match["confidence"]
            payment.matching_method = "bundled"
            
            allocations = [
                {"invoice_id": inv["invoice_id"], "amount": inv["balance"]} 
                for inv in bundled_match["invoices"]
            ]
            
            return {
                "matched": True,
                "confidence": bundled_match["confidence"],
                "method": "bundled_invoices",
                "allocations": allocations,
                "variance_amount": bundled_match["variance"],
                "variance_percentage": bundled_match.get("variance_percentage", 0),
                "requires_human_review": bundled_match["confidence"] < MatchConfidence.HIGH.value,
                "rationale": bundled_match.get("rationale", {"reason": "Bundled invoice match"})
            }
        
        # No good match found - requires manual review
        return {
            "matched": False,
            "confidence": MatchConfidence.MANUAL_REVIEW.value,
            "method": "unmatched",
            "allocations": [],
            "variance_amount": payment.amount,
            "variance_percentage": 100.0,
            "requires_human_review": True,
            "rationale": {"reason": "No matching invoices found within confidence thresholds"}
        }
    
    def reconcile_with_bank_transaction(self, payment: ARPayment, bank_transaction_id: str, deposit_date: datetime = None):
        """
        Reconcile payment with bank transaction.
        
        Args:
            payment: ARPayment instance
            bank_transaction_id: ID of corresponding bank transaction
            deposit_date: Date when deposited (defaults to now)
        """
        payment.bank_transaction_id = bank_transaction_id
        payment.deposit_date = deposit_date or datetime.utcnow()
        payment.reconciliation_date = datetime.utcnow()
        payment.is_reconciled = True
        
        # Update status if not already processed
        if payment.status in ["pending", "matched"]:
            payment.status = "reconciled"
        
        self.db.commit()
    
    def create_dispute(self, payment: ARPayment, reason: str, dispute_date: datetime = None):
        """
        Create a dispute for this payment.
        
        Args:
            payment: ARPayment instance
            reason: Reason for dispute
            dispute_date: Date of dispute (defaults to now)
        """
        payment.is_disputed = True
        payment.dispute_reason = reason
        payment.dispute_date = dispute_date or datetime.utcnow()
        payment.status = "disputed"
        
        self.db.commit()
    
    def apply_adjustment(self, payment: ARPayment, adjustment_amount: float, reason: str):
        """
        Apply an adjustment (write-off, discount) to the payment.
        
        Args:
            payment: ARPayment instance
            adjustment_amount: Amount of adjustment (can be negative)
            reason: Reason for adjustment
        """
        payment.adjustment_amount += adjustment_amount
        
        # Add to notes
        adjustment_note = f"Adjustment: ${adjustment_amount:.2f} - {reason}"
        if payment.notes:
            payment.notes += f"\n{adjustment_note}"
        else:
            payment.notes = adjustment_note
        
        self.db.commit()
    
    def process_incoming_payment(self, 
                                customer_id: int,
                                amount: float,
                                payment_method: str,
                                reference_number: str = None,
                                received_date: datetime = None) -> ARPayment:
        """
        Process a new incoming payment.
        
        Args:
            customer_id: ID of paying customer
            amount: Payment amount
            payment_method: Method of payment
            reference_number: Check number, transaction ID, etc.
            received_date: When payment was received
            
        Returns:
            Created ARPayment instance
        """
        payment = ARPayment(
            business_id=self.business_id,
            customer_id=customer_id,
            amount=amount,
            payment_date=datetime.utcnow(),
            received_date=received_date or datetime.utcnow(),
            payment_method=payment_method,
            reference_number=reference_number,
            status="pending",
            processing_status="unprocessed"
        )
        
        self.db.add(payment)
        self.db.commit()
        
        return payment
    
    def get_unmatched_payments(self, customer_id: int = None) -> List[ARPayment]:
        """
        Get payments that haven't been matched to invoices.
        
        Args:
            customer_id: Optional filter by customer
            
        Returns:
            List of unmatched payments
        """
        query = self.db.query(ARPayment).filter(
            ARPayment.business_id == self.business_id,
            ARPayment.status == "pending",
            ~ARPayment.is_fully_allocated
        )
        
        if customer_id:
            query = query.filter(ARPayment.customer_id == customer_id)
        
        return query.all()
    
    def get_payment_summary(self, payment: ARPayment) -> Dict[str, Any]:
        """
        Get comprehensive payment summary.
        
        Args:
            payment: ARPayment instance
            
        Returns:
            Dictionary with payment summary data
        """
        return {
            "payment_id": payment.payment_id,
            "customer_id": payment.customer_id,
            "amount": payment.amount,
            "net_amount": payment.amount + payment.adjustment_amount,
            "unallocated_amount": self.get_unallocated_amount(payment),
            "status": payment.status,
            "processing_status": payment.processing_status,
            "payment_method": payment.payment_method,
            "reference_number": payment.reference_number,
            "received_date": payment.received_date,
            "is_reconciled": payment.is_reconciled,
            "is_fully_allocated": payment.is_fully_allocated,
            "is_overpayment": self.is_overpayment(payment),
            "matching_confidence": payment.matching_confidence,
            "matching_method": payment.matching_method,
            "allocation_summary": self.get_allocation_summary(payment)
        }
    
    # ============================================================================
    # Sophisticated Matching Algorithm Methods (from cash_reconciliation.py)
    # ============================================================================
    
    def _find_exact_invoice_match(self, payment: ARPayment, invoices: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find invoice with exact amount match within reasonable timing."""
        for invoice in invoices:
            if abs(invoice.get("balance", 0) - payment.amount) < 0.01:
                if self._is_timing_reasonable(payment, invoice):
                    return invoice
        return None
    
    def _find_fuzzy_invoice_matches(self, payment: ARPayment, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find invoices with fuzzy amount matches within tolerance."""
        matches = []
        for invoice in invoices:
            balance = invoice.get("balance", 0)
            if balance <= 0:
                continue
                
            variance = abs(balance - payment.amount)
            variance_pct = variance / balance if balance > 0 else 1.0
            
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
    
    def _find_bundled_invoice_matches(self, payment: ARPayment, invoices: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find combination of invoices that sum to payment amount using dynamic programming."""
        candidates = self._pre_filter_candidates(payment, invoices)
        if not candidates:
            return None
        
        best_combo = self._find_best_subset_sum(payment.amount, candidates)
        if not best_combo:
            return None
        
        combo_total = sum(inv.get("balance", 0) for inv in best_combo)
        variance = payment.amount - combo_total
        combo_size = len(best_combo)
        
        confidence = self._calculate_bundled_confidence(payment.amount, combo_total, variance, combo_size)
        
        if confidence < MatchConfidence.MEDIUM.value:
            return None
        
        avg_days = sum(inv.get("days_from_payment", 0) for inv in best_combo) / combo_size
        
        return {
            "invoices": [
                {k: v for k, v in inv.items() if k != "days_from_payment"} 
                for inv in best_combo
            ],
            "confidence": confidence,
            "total_amount": combo_total,
            "variance": variance,
            "variance_percentage": abs(variance) / combo_total * 100 if combo_total > 0 else 100,
            "rationale": {
                "confidence_score": confidence,
                "amount_total": combo_total,
                "variance": variance,
                "combo_size": combo_size,
                "avg_days_from_payment": round(avg_days, 2)
            }
        }
    
    def _pre_filter_candidates(self, payment: ARPayment, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Pre-filter invoice candidates for bundled matching."""
        candidates = []
        payment_date = payment.received_date or payment.payment_date
        
        for invoice in invoices:
            # Skip invoices with zero balance
            if invoice.get("balance", 0) <= 0:
                continue
            
            # Calculate timing difference
            invoice_date_str = invoice.get("due_date")
            if invoice_date_str:
                try:
                    if isinstance(invoice_date_str, str):
                        invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d")
                    else:
                        invoice_date = invoice_date_str
                    
                    days_diff = abs((payment_date.date() - invoice_date.date()).days)
                    if days_diff <= self.max_date_variance_days:
                        inv_copy = dict(invoice)
                        inv_copy["days_from_payment"] = days_diff
                        candidates.append(inv_copy)
                except (ValueError, AttributeError):
                    # Include invoice if date parsing fails (don't exclude on bad data)
                    inv_copy = dict(invoice)
                    inv_copy["days_from_payment"] = 0
                    candidates.append(inv_copy)
            else:
                # Include invoice if no due date
                inv_copy = dict(invoice)
                inv_copy["days_from_payment"] = 0
                candidates.append(inv_copy)
        
        # Filter by amount upper bound
        upper_band = payment.amount * (1.0 + self.fuzzy_match_tolerance)
        candidates = [inv for inv in candidates if inv.get("balance", 0) <= upper_band]
        
        # Sort by timing (closest first) and limit
        candidates.sort(key=lambda inv: inv.get("days_from_payment", 9999))
        return candidates[:self.max_bundle_candidates]
    
    def _find_best_subset_sum(self, target_amount: float, candidates: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """Find best combination of invoices using dynamic programming subset sum algorithm."""
        target_cents = int(target_amount * 100)
        dp = {0: ([], 0)}  # amount_cents -> (invoice_combo, num_items)
        
        sorted_candidates = sorted(candidates, key=lambda x: x.get('balance', 0), reverse=True)
        
        for invoice in sorted_candidates:
            invoice_cents = int(invoice.get("balance", 0) * 100)
            if invoice_cents <= 0:
                continue
            
            new_dp_entries = {}
            for current_sum, (combo, num_items) in dp.items():
                new_sum = current_sum + invoice_cents
                tolerance_cents = int(self.fuzzy_match_tolerance * target_cents)
                
                if new_sum <= target_cents + tolerance_cents:
                    # Prefer combinations with fewer items
                    if new_sum not in dp or num_items + 1 < dp[new_sum][1]:
                        new_dp_entries[new_sum] = (combo + [invoice], num_items + 1)
            
            dp.update(new_dp_entries)
        
        # Find best match (closest to target, fewest items)
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
    
    def _calculate_bundled_confidence(self, payment_amount: float, combo_total: float, variance: float, combo_size: int) -> float:
        """Calculate confidence score for bundled invoice matches."""
        if abs(variance) <= 0.01:
            return MatchConfidence.HIGH.value
        
        # Variance as percentage of total
        variance_pct = abs(variance) / combo_total if combo_total > 0 else 1.0
        
        if variance_pct <= 0.02:  # 2% variance
            return MatchConfidence.HIGH.value
        elif variance_pct <= 0.05:  # 5% variance
            return MatchConfidence.MEDIUM.value
        elif variance_pct <= self.fuzzy_match_tolerance:
            return MatchConfidence.LOW.value
        else:
            return MatchConfidence.MANUAL_REVIEW.value
    
    def _is_timing_reasonable(self, payment: ARPayment, invoice: Dict[str, Any]) -> bool:
        """Check if payment timing is reasonable relative to invoice date."""
        invoice_date_str = invoice.get("due_date")
        if not invoice_date_str:
            return True  # No date constraint
        
        try:
            payment_date = payment.received_date or payment.payment_date
            if isinstance(invoice_date_str, str):
                invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d")
            else:
                invoice_date = invoice_date_str
            
            days_diff = abs((payment_date.date() - invoice_date.date()).days)
            return days_diff <= self.max_date_variance_days
        except (ValueError, AttributeError):
            return True  # Don't exclude on bad data
    
    def _calculate_timing_score(self, payment: ARPayment, invoice: Dict[str, Any]) -> float:
        """Calculate timing score for payment-to-invoice correlation."""
        invoice_date_str = invoice.get("due_date")
        if not invoice_date_str:
            return 0.5  # Neutral score if no date
        
        try:
            payment_date = payment.received_date or payment.payment_date
            if isinstance(invoice_date_str, str):
                invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d")
            else:
                invoice_date = invoice_date_str
            
            days_diff = abs((payment_date.date() - invoice_date.date()).days)
            
            if days_diff == 0:
                return 1.0
            elif days_diff <= 7:
                return 0.9
            elif days_diff <= 30:
                return 0.7
            else:
                return 0.3
        except (ValueError, AttributeError):
            return 0.5  # Neutral score on bad data
