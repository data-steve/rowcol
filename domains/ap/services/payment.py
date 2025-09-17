"""
PaymentService - Complete Payment Lifecycle Management

Handles payment operations from creation through reconciliation:
- Payment execution with mock and real providers
- Payment status tracking and retry logic  
- Reconciliation with bank transactions
- QBO synchronization
- Runway impact calculations

Enhanced from basic APPaymentService to include comprehensive functionality.
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from domains.core.services.base_service import TenantAwareService
from domains.ap.models.payment import Payment, PaymentStatus, PaymentType
from domains.ap.models.payment_intent import PaymentIntent as PaymentIntentModel
from domains.ap.models.bill import Bill as BillModel
from domains.ap.models.vendor import Vendor
from domains.core.models.user import User
from domains.ap.providers.factories import get_qbo_ap_provider
from common.exceptions import ValidationError, BusinessRuleViolationError

logger = logging.getLogger(__name__)

class PaymentService(TenantAwareService):
    """
    Comprehensive payment service handling the complete payment lifecycle.
    
    Enhanced from APPaymentService to include modern architecture patterns:
    - Tenant isolation (ADR-003)
    - Provider pattern (ADR-002) 
    - Comprehensive business logic
    """
    
    def __init__(self, db: Session, business_id: str, 
                 qbo_provider=None, runway_reserve_service=None):
        """
        Initialize payment service with tenant isolation.
        
        Args:
            db: Database session
            business_id: Business identifier for tenant isolation
            qbo_provider: Optional QBO provider (uses factory if None)
            runway_reserve_service: Optional runway reserve service
        """
        super().__init__(db, business_id)
        
        self.qbo_provider = qbo_provider or get_qbo_ap_provider(business_id)
        self.runway_reserve_service = runway_reserve_service
        
        logger.info(f"Initialized PaymentService for business {business_id}")

    # ==================== PAYMENT BUSINESS LOGIC ====================
    
    def get_payment_total_cost(self, payment: Payment) -> Decimal:
        """Get total cost including fees."""
        return payment.amount + payment.processing_fee
    
    def is_payment_pending(self, payment: Payment) -> bool:
        """Check if payment is pending execution."""
        return payment.status in [PaymentStatus.PENDING, PaymentStatus.SCHEDULED]
    
    def is_payment_executed(self, payment: Payment) -> bool:
        """Check if payment has been executed."""
        return payment.status in [PaymentStatus.EXECUTED, PaymentStatus.RECONCILED]
    
    def get_days_since_execution(self, payment: Payment) -> Optional[int]:
        """Get days since payment was executed."""
        if not payment.execution_date:
            return None
        delta = datetime.utcnow() - payment.execution_date
        return delta.days
    
    def can_payment_be_executed(self, payment: Payment) -> bool:
        """Check if payment can be executed."""
        return payment.status in [PaymentStatus.PENDING, PaymentStatus.SCHEDULED] and not payment.requires_approval
    
    def can_payment_be_cancelled(self, payment: Payment) -> bool:
        """Check if payment can be cancelled."""
        return payment.status in [PaymentStatus.PENDING, PaymentStatus.SCHEDULED]
    
    def execute_payment(self, payment: Payment, confirmation_number: str = None, 
                       processing_fee: Decimal = None) -> bool:
        """Execute payment (business logic extracted from model)."""
        if not self.can_payment_be_executed(payment):
            return False
        
        payment.status = PaymentStatus.EXECUTED
        payment.execution_date = datetime.utcnow()
        payment.confirmation_number = confirmation_number
        
        if processing_fee:
            payment.processing_fee = processing_fee
        
        payment.updated_at = datetime.utcnow()
        
        # Release runway reserves if payment is executed
        if self.runway_reserve_service and payment.bill and payment.bill.is_reserved:
            try:
                self.runway_reserve_service.release_reserve(payment.bill.reserve_allocation_id)
                payment.bill.is_reserved = False
            except Exception as e:
                logger.error(f"Failed to release reserve for payment {payment.payment_id}: {str(e)}")
        
        return True
    
    def fail_payment(self, payment: Payment, reason: str) -> bool:
        """Mark payment as failed (business logic extracted from model)."""
        if payment.status not in [PaymentStatus.PENDING, PaymentStatus.SCHEDULED, PaymentStatus.PROCESSING]:
            return False
        
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = reason
        payment.retry_count += 1
        payment.updated_at = datetime.utcnow()
        return True
    
    def cancel_payment(self, payment: Payment, reason: str = None) -> bool:
        """Cancel payment (business logic extracted from model)."""
        if not self.can_payment_be_cancelled(payment):
            return False
        
        payment.status = PaymentStatus.CANCELLED
        payment.failure_reason = reason
        payment.updated_at = datetime.utcnow()
        
        # Release runway reserves if payment is cancelled
        if self.runway_reserve_service and payment.bill and payment.bill.is_reserved:
            try:
                self.runway_reserve_service.release_reserve(payment.bill.reserve_allocation_id)
                payment.bill.is_reserved = False
            except Exception as e:
                logger.error(f"Failed to release reserve for cancelled payment {payment.payment_id}: {str(e)}")
        
        return True
    
    def reconcile_payment(self, payment: Payment, bank_transaction_id: str, 
                         reconciled_by_user_id: str) -> bool:
        """Reconcile payment with bank transaction (business logic extracted from model)."""
        if not self.is_payment_executed(payment):
            return False
        
        payment.is_reconciled = True
        payment.reconciled_date = datetime.utcnow()
        payment.reconciled_by = reconciled_by_user_id
        payment.bank_transaction_id = bank_transaction_id
        payment.status = PaymentStatus.RECONCILED
        payment.updated_at = datetime.utcnow()
        return True
    
    def calculate_payment_runway_impact(self, payment: Payment) -> Dict[str, Any]:
        """Calculate impact of this payment on runway calculations."""
        impact_multiplier = 1.0 if self.is_payment_executed(payment) else 0.8
        total_cost = self.get_payment_total_cost(payment)
        
        return {
            'cash_impact': float(-total_cost * Decimal(str(impact_multiplier))),
            'execution_date': payment.execution_date.isoformat() if payment.execution_date else None,
            'is_executed': self.is_payment_executed(payment),
            'is_reconciled': payment.is_reconciled,
            'processing_fee': float(payment.processing_fee),
            'payment_method': payment.payment_method,
            'status': payment.status
        }
    
    # ==================== PAYMENT ORCHESTRATION ====================
    
    def create_payment(self, bill_id: int, payment_date: datetime,
                      payment_method: str = "ach", payment_account: str = None,
                      created_by_user_id: str = None) -> Payment:
        """Create a new payment for a bill."""
        try:
            bill = self._get_bill_or_raise(bill_id)
            
            if not bill.vendor:
                raise ValidationError(f"Bill {bill_id} has no associated vendor")
            
            payment = Payment(
                business_id=self.business_id,
                vendor_id=bill.vendor.vendor_id,
                bill_id=bill.bill_id,
                payment_type=PaymentType.BILL_PAYMENT,
                amount=bill.amount,
                payment_date=payment_date,
                payment_method=payment_method,
                payment_account=payment_account,
                status=PaymentStatus.PENDING,
                created_by=created_by_user_id
            )
            
            # Check if approval is required based on amount or vendor
            payment.requires_approval = self._payment_requires_approval(payment)
            
            self.db.add(payment)
            self.db.flush()
            
            logger.info(f"Created payment {payment.payment_id} for bill {bill_id}")
            return payment
            
        except Exception as e:
            logger.error(f"Payment creation failed: {str(e)}")
            raise
    
    def execute_payment_workflow(self, payment_id: int, 
                                confirmation_number: str = None) -> Payment:
        """Execute payment through the full workflow."""
        try:
            payment = self._get_payment_or_raise(payment_id)
            
            if not self.can_payment_be_executed(payment):
                raise BusinessRuleViolationError(
                    f"Payment {payment_id} cannot be executed (status: {payment.status})"
                )
            
            # Mock payment execution (in real implementation, would call payment processor)
            success = self.execute_payment(payment, confirmation_number)
            if not success:
                raise ValidationError(f"Failed to execute payment {payment_id}")
            
            # Sync with QBO if configured
            try:
                self.qbo_provider.sync_payment(payment)
            except Exception as e:
                logger.warning(f"QBO sync failed for payment {payment_id}: {str(e)}")
                # Don't fail the whole payment for QBO sync issues
            
            # Update bill status
            if payment.bill:
                payment.bill.status = "paid"
                payment.bill.payment_reference = confirmation_number
            
            self.db.commit()
            logger.info(f"Successfully executed payment {payment_id}")
            return payment
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Payment execution failed: {str(e)}")
            raise
    
    def payment_to_dict(self, payment: Payment) -> Dict[str, Any]:
        """Convert payment to dictionary for API responses."""
        return {
            'payment_id': payment.payment_id,
            'business_id': payment.business_id,
            'vendor_id': payment.vendor_id,
            'bill_id': payment.bill_id,
            'qbo_payment_id': payment.qbo_payment_id,
            'payment_type': payment.payment_type,
            'amount': float(payment.amount),
            'processing_fee': float(payment.processing_fee),
            'total_cost': float(self.get_payment_total_cost(payment)),
            'payment_date': payment.payment_date.isoformat(),
            'execution_date': payment.execution_date.isoformat() if payment.execution_date else None,
            'payment_method': payment.payment_method,
            'payment_account': payment.payment_account,
            'check_number': payment.check_number,
            'confirmation_number': payment.confirmation_number,
            'status': payment.status,
            'failure_reason': payment.failure_reason,
            'retry_count': payment.retry_count,
            'is_reconciled': payment.is_reconciled,
            'reconciled_date': payment.reconciled_date.isoformat() if payment.reconciled_date else None,
            'bank_transaction_id': payment.bank_transaction_id,
            'batch_id': payment.batch_id,
            'requires_approval': payment.requires_approval,
            'approved_by': payment.approved_by,
            'approved_at': payment.approved_at.isoformat() if payment.approved_at else None,
            'description': payment.description,
            'tags': payment.tags,
            'is_pending': self.is_payment_pending(payment),
            'is_executed': self.is_payment_executed(payment),
            'can_be_executed': self.can_payment_be_executed(payment),
            'can_be_cancelled': self.can_payment_be_cancelled(payment),
            'days_since_execution': self.get_days_since_execution(payment),
            'runway_impact': self.calculate_payment_runway_impact(payment),
            'created_at': payment.created_at.isoformat(),
            'updated_at': payment.updated_at.isoformat()
        }
    
    # ==================== UTILITY METHODS ====================
    
    def _get_payment_or_raise(self, payment_id: int) -> Payment:
        """Get payment by ID or raise ValidationError."""
        return self._get_by_id_or_raise(Payment, payment_id, f"Payment {payment_id} not found")
    
    def _get_bill_or_raise(self, bill_id: int) -> BillModel:
        """Get bill by ID or raise ValidationError."""
        return self._get_by_id_or_raise(BillModel, bill_id, f"Bill {bill_id} not found")
    
    def _payment_requires_approval(self, payment: Payment) -> bool:
        """Determine if payment requires approval based on business rules."""
        # Business rule thresholds - TODO: Make configurable per business
        LARGE_PAYMENT_THRESHOLD = Decimal('5000.00')
        
        if payment.amount >= LARGE_PAYMENT_THRESHOLD:
            return True
        
        # New or unreliable vendor
        if payment.vendor and not payment.vendor.payment_reliability_score:
            return True
        
        # High-risk payment methods
        if payment.payment_method in ['wire', 'international']:
            return True
        
        return False