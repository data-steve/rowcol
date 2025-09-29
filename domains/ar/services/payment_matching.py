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
from domains.ar.models.payment import ARPayment, Payment as PaymentModel
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
    
    def apply_payment(self, business_id: int, amount: float, date: datetime, method: str, customer_id: Optional[int] = None) -> PaymentModel:
        """
        Apply a payment to invoices with tenant isolation.
        """
        try:
            # Create payment record
            payment = PaymentModel(
                business_id=business_id,
            customer_id=customer_id,
            amount=amount,
                payment_date=date,
                payment_method=method,
                status="matched"  # AR payments use "matched" status
        )
        
        self.db.add(payment)
        self.db.commit()
            self.db.refresh(payment)
        return payment
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Payment application failed: {str(e)}")

    def get_payment(self, payment_id: int, business_id: int) -> PaymentModel:
        """
        Get payment by ID with tenant isolation.
        """
        payment = self.db.query(PaymentModel).filter(
            PaymentModel.payment_id == payment_id,
            PaymentModel.business_id == business_id
        ).first()
        
        if not payment:
            raise ValueError("Payment not found or does not belong to business")
        
        return payment
    
    def get_unallocated_amount(self, payment: ARPayment) -> float:
        """Calculate amount not yet allocated to invoices."""
        net_amount = payment.amount + payment.adjustment_amount