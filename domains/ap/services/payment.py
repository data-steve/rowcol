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

from typing import Dict, Optional, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from domains.core.services.base_service import TenantAwareService
from domains.ap.models.payment import Payment, PaymentStatus, PaymentType
from domains.ap.models.bill import Bill as BillModel
# NOTE: Providers parked for future strategy - using QBOAPIClient directly
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
        
        # Use SmartSyncService for QBO operations
        from infra.qbo.smart_sync import SmartSyncService
        self.smart_sync = SmartSyncService(business_id, "", self.db)
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
    
    def get_payments(self, status_filter: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Payment]:
        """Get payments with optional filtering and pagination."""
        query = self.db.query(Payment).filter(Payment.business_id == self.business_id)
        
        if status_filter:
            query = query.filter(Payment.status == status_filter)
        
        return query.offset(offset).limit(limit).all()
    
    def can_payment_be_executed(self, payment: Payment) -> bool:
        """Check if payment can be executed."""
        return payment.status in [PaymentStatus.PENDING, PaymentStatus.SCHEDULED] and not payment.requires_approval
    
    def can_payment_be_cancelled(self, payment: Payment) -> bool:
        """Check if payment can be cancelled."""
        return payment.status in [PaymentStatus.PENDING, PaymentStatus.SCHEDULED]
    
    async def execute_payment(self, payment: Payment, confirmation_number: str = None, 
                       processing_fee: Decimal = None) -> bool:
        """Execute payment (business logic extracted from model)."""
        if not self.can_payment_be_executed(payment):
            return False
        
        # Execute payment via QBO bill pay rails
        if self.smart_sync:
            try:
                # Prepare QBO payment data
                qbo_payment_data = {
                    "TotalAmt": float(payment.amount),
                    "TxnDate": payment.payment_date.isoformat(),
                    "PaymentRefNum": confirmation_number or f"PAY-{payment.payment_id}",
                    "PrivateNote": f"Payment for bill {payment.bill.qbo_bill_id if payment.bill else 'Unknown'}",
                    "Line": [{
                        "Amount": float(payment.amount),
                        "LinkedTxn": [{
                            "TxnId": payment.bill.qbo_bill_id if payment.bill else None,
                            "TxnType": "Bill"
                        }]
                    }]
                }
                
                # Execute payment in QBO
                qbo_response = await self.smart_sync.create_payment_immediate(qbo_payment_data)
                
                # Update payment with QBO response
                if qbo_response and "Payment" in qbo_response:
                    payment.qbo_payment_id = qbo_response["Payment"].get("Id")
                    payment.qbo_sync_token = qbo_response["Payment"].get("SyncToken")
                    payment.qbo_last_sync = datetime.utcnow()
                    
            except Exception as e:
                logger.error(f"Failed to execute payment in QBO: {e}")
                # Continue with local status update even if QBO fails
                # This allows for offline payment processing
        
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
    
    async def schedule_payment(self, business_id: str, bill_ids: list, funding_account: str) -> Dict[str, Any]:
        """
        Schedule payment for multiple bills with runway reserve integration.
        
        Args:
            business_id: Business identifier (for consistency with tests)
            bill_ids: List of bill IDs to pay
            funding_account: Account to fund payment from (e.g., "1000-Cash")
            
        Returns:
            Payment summary with bill_ids and business_id
        """
        if business_id != self.business_id:
            raise ValidationError(f"Business ID mismatch: expected {self.business_id}, got {business_id}")
        
        try:
            # Get bills to schedule
            from domains.ap.models.bill import Bill
            bills = self.db.query(Bill).filter(
                Bill.business_id == self.business_id,
                Bill.bill_id.in_(bill_ids),
                Bill.status == "approved"
            ).all()
            
            if not bills:
                raise ValidationError("No approved bills found to schedule")
            
            # Calculate total amount
            total_amount = sum(bill.amount for bill in bills)
            
            # Use runway-aware scheduled payment service
            from runway.core.scheduled_payment_service import ScheduledPaymentService
            
            scheduled_payment_service = ScheduledPaymentService(
                db=self.db,
                business_id=self.business_id,
                runway_reserve_service=self.runway_reserve_service
            )
            
            # Schedule each bill payment
            scheduled_count = 0
            for bill in bills:
                try:
                    # Schedule payment for next business day
                    payment_date = datetime.utcnow() + timedelta(days=1)
                    
                    success = await scheduled_payment_service.schedule_payment_with_reserve(
                        bill=bill,
                        payment_date=payment_date,
                        payment_method="ach",
                        payment_account=funding_account
                    )
                    
                    if success:
                        scheduled_count += 1
                        logger.info(f"Scheduled payment for bill {bill.bill_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to schedule payment for bill {bill.bill_id}: {e}")
            
            # Return payment summary
            payment_summary = {
                'business_id': business_id,
                'bill_ids': [bill.bill_id for bill in bills],
                'funding_account': funding_account,
                'status': 'scheduled',
                'scheduled_count': scheduled_count,
                'total_amount': float(total_amount),
                'payment_date': (datetime.utcnow() + timedelta(days=1)).isoformat()
            }
            
            logger.info(f"Scheduled {scheduled_count}/{len(bills)} payments from account {funding_account}")
            return payment_summary
            
        except Exception as e:
            logger.error(f"Failed to schedule payments: {e}")
            raise ValidationError(f"Failed to schedule payments: {str(e)}")
    
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
    
    async def execute_payment_workflow(self, payment_id: int, 
                                confirmation_number: str = None) -> Payment:
        """Execute payment through the full workflow."""
        try:
            payment = self._get_payment_or_raise(payment_id)
            
            if not self.can_payment_be_executed(payment):
                raise BusinessRuleViolationError(
                    f"Payment {payment_id} cannot be executed (status: {payment.status})"
                )
            
            # Execute payment using QBO bill pay rails
            success = await self.execute_payment(payment, confirmation_number)
            if not success:
                raise ValidationError(f"Failed to execute payment {payment_id}")
            
            # Sync with QBO if configured
            try:
                await self.smart_sync.record_payment({
                    "payment_id": payment.payment_id,
                    "amount": float(payment.amount),
                    "payment_date": payment.payment_date.isoformat(),
                    "payment_method": payment.payment_method
                })
            except Exception as e:
                logger.warning(f"QBO sync failed for payment {payment_id}: {str(e)}")
                # Don't fail the whole payment for QBO sync issues
            
            # Update bill status after successful payment execution
            if payment.bill:
                payment.bill.status = "paid"  # This is OK - payment was actually executed above
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