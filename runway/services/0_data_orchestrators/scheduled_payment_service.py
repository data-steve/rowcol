"""
Scheduled Payment Service - Runway-Aware Payment Scheduling

This service handles payment scheduling with runway reserve integration:
- Allocates runway reserves when scheduling payments (earmarking money)
- Creates QBO scheduled payments with future TxnDate
- Integrates with runway calculations for optimal payment timing
- Manages reserve allocation and release lifecycle

This service belongs in runway/ because payment scheduling is a runway decision
about cash flow timing, not a domain operation. It integrates with:
- RunwayReserveService for earmarking money
- RunwayCalculationService for optimal timing
- QBO API for actual payment scheduling
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from runway.services.0_data_orchestrators.reserve_runway import RunwayReserveService
from runway.schemas.runway_reserve import ReserveAllocationCreate
from infra.qbo.smart_sync import SmartSyncService
from common.exceptions import ValidationError
from infra.config import feature_gates

logger = logging.getLogger(__name__)


class ScheduledPaymentService:
    """
    Service for scheduling payments with runway reserve integration.
    
    This service handles the complete lifecycle of scheduled payments:
    1. Allocate runway reserves (earmark money)
    2. Create QBO scheduled payment with future TxnDate
    3. Update bill with reserve allocation details
    4. Handle payment execution → reserve release
    5. Handle payment cancellation → reserve release
    """
    
    def __init__(self, db: Session, business_id: str, runway_reserve_service: RunwayReserveService = None):
        """
        Initialize scheduled payment service.
        
        Args:
            db: Database session
            business_id: Business identifier for tenant isolation
            runway_reserve_service: Runway reserve service for earmarking money
        """
        self.db = db
        self.business_id = business_id
        self.runway_reserve_service = runway_reserve_service
        self.smart_sync = SmartSyncService(business_id, "", db)
        
        logger.info(f"Initialized ScheduledPaymentService for business {business_id}")
    
    async def schedule_payment_with_reserve(self, bill, payment_date: datetime, 
                                          payment_method: str = None, 
                                          payment_account: str = None) -> bool:
        """
        Schedule payment with runway reserve allocation (earmarking).
        
        This method:
        1. Allocates runway reserves to earmark the money
        2. Creates QBO scheduled payment with future TxnDate
        3. Updates bill with reserve allocation details
        
        Args:
            bill: Bill object to schedule payment for
            payment_date: Future date when payment should be executed
            payment_method: Payment method (ach, check, card, wire)
            payment_account: Bank account for payment
            
        Returns:
            True if scheduling successful, False otherwise
        """
        try:
            # 1. ALLOCATE RUNWAY RESERVE (earmark the money) - Only if reserve management is enabled
            allocation_id = None
            if self.runway_reserve_service and feature_gates.can_use_feature("reserve_management"):
                try:
                    allocation_data = ReserveAllocationCreate(
                        reserve_id="operational_reserve",  # TODO: Determine from business rules
                        allocated_amount=bill.amount,
                        purpose=f"Scheduled payment for bill {bill.bill_id}",
                        scheduled_date=payment_date
                    )
                    allocation = self.runway_reserve_service.allocate_reserve(allocation_data)
                    allocation_id = allocation.allocation_id
                    
                    logger.info(f"Allocated reserve {allocation_id} for bill {bill.bill_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to allocate reserve for bill {bill.bill_id}: {e}")
                    # Continue without reserve allocation if it fails
                    # This allows for offline payment scheduling
            else:
                logger.info(f"Reserve management not available - skipping reserve allocation for bill {bill.bill_id}")
            
            # 2. CREATE QBO SCHEDULED PAYMENT - CRITICAL FIX: QBO cannot execute payments!
            if self.smart_sync and bill.qbo_bill_id and feature_gates.can_use_feature("qbo_sync"):
                try:
                    qbo_payment_data = {
                        "TotalAmt": float(bill.amount),
                        "TxnDate": payment_date.isoformat(),  # Future date = scheduled
                        "PaymentRefNum": f"SCHED-{bill.bill_id}-{allocation_id or 'NO-RESERVE'}",
                        "PrivateNote": f"Scheduled payment for bill {bill.qbo_bill_id} (external execution required)",
                        "Line": [{
                            "Amount": float(bill.amount),
                            "LinkedTxn": [{
                                "TxnId": bill.qbo_bill_id,
                                "TxnType": "Bill"
                            }]
                        }]
                    }
                    
                    # CRITICAL FIX: QBO cannot execute payments - only sync records
                    if feature_gates.can_use_feature("scheduled_payment_execution"):
                        # Ramp-enabled: Create actual scheduled payment
                        logger.info(f"Creating scheduled payment via Ramp for bill {bill.bill_id}")
                        # TODO: Implement Ramp scheduled payment creation
                        # ramp_response = await self.ramp_client.create_scheduled_payment(qbo_payment_data)
                    else:
                        # QBO-only mode: Only sync payment record (not execution)
                        logger.info(f"QBO-only mode: Syncing scheduled payment record for bill {bill.bill_id}")
                        qbo_response = await self.smart_sync.sync_payment_record(qbo_payment_data)
                        
                        # Update bill with QBO sync response
                        if qbo_response and "Payment" in qbo_response:
                            bill.qbo_payment_id = qbo_response["Payment"].get("Id")
                            bill.qbo_sync_token = qbo_response["Payment"].get("SyncToken")
                            bill.qbo_last_sync = datetime.utcnow()
                            
                            logger.info(f"Synced QBO payment record {bill.qbo_payment_id} for bill {bill.bill_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to sync QBO payment record for bill {bill.bill_id}: {e}")
                    # Continue with local scheduling even if QBO sync fails
                    # This allows for offline payment scheduling
            
            # 3. UPDATE BILL WITH RESERVE ALLOCATION AND SCHEDULING
            bill.reserve_allocation_id = allocation_id
            bill.is_reserved = allocation_id is not None
            bill.reserve_amount = bill.amount if allocation_id else Decimal('0')
            bill.status = "scheduled"  # Use string to avoid enum issues
            bill.scheduled_payment_date = payment_date
            bill.payment_method = payment_method
            bill.payment_account = payment_account
            bill.updated_at = datetime.utcnow()
            
            logger.info(f"Successfully scheduled payment for bill {bill.bill_id} on {payment_date}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule payment for bill {bill.bill_id}: {e}")
            return False
    
    async def cancel_scheduled_payment(self, bill) -> bool:
        """
        Cancel scheduled payment and release runway reserves.
        
        Args:
            bill: Bill object with scheduled payment
            
        Returns:
            True if cancellation successful, False otherwise
        """
        try:
            # 1. CANCEL QBO SCHEDULED PAYMENT
            if self.smart_sync and bill.qbo_payment_id:
                try:
                    # TODO: Implement QBO payment cancellation
                    # qbo_response = await self.smart_sync.cancel_payment(bill.qbo_payment_id)
                    logger.info(f"Would cancel QBO payment {bill.qbo_payment_id} for bill {bill.bill_id}")
                except Exception as e:
                    logger.error(f"Failed to cancel QBO payment for bill {bill.bill_id}: {e}")
            
            # 2. RELEASE RUNWAY RESERVES
            if self.runway_reserve_service and bill.reserve_allocation_id:
                try:
                    # TODO: Implement reserve release
                    # self.runway_reserve_service.release_allocation(bill.reserve_allocation_id)
                    logger.info(f"Would release reserve allocation {bill.reserve_allocation_id} for bill {bill.bill_id}")
                except Exception as e:
                    logger.error(f"Failed to release reserve allocation for bill {bill.bill_id}: {e}")
            
            # 3. UPDATE BILL STATUS
            bill.status = "approved"  # Back to approved status
            bill.scheduled_payment_date = None
            bill.payment_method = None
            bill.payment_account = None
            bill.reserve_allocation_id = None
            bill.is_reserved = False
            bill.reserve_amount = Decimal('0')
            bill.updated_at = datetime.utcnow()
            
            logger.info(f"Successfully cancelled scheduled payment for bill {bill.bill_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel scheduled payment for bill {bill.bill_id}: {e}")
            return False
    
    def get_optimal_payment_date(self, bill, runway_context: Dict[str, Any] = None) -> datetime:
        """
        Calculate optimal payment date based on runway calculations.
        
        Args:
            bill: Bill object
            runway_context: Current runway data from RunwayCalculationService
            
        Returns:
            Optimal payment date considering runway impact
        """
        # Default to due date if no runway context
        if not runway_context or not bill.due_date:
            return bill.due_date or datetime.utcnow() + timedelta(days=30)
        
        # TODO: Implement optimal timing calculation based on:
        # - Current runway days
        # - Bill amount impact on runway
        # - Cash flow projections
        # - Vendor payment terms
        
        # For now, return due date
        return bill.due_date or datetime.utcnow() + timedelta(days=30)
    
    def get_scheduled_payment_summary(self, business_id: str) -> Dict[str, Any]:
        """
        Get summary of all scheduled payments for a business.
        
        Args:
            business_id: Business identifier
            
        Returns:
            Summary of scheduled payments with reserve allocations
        """
        try:
            from domains.ap.models.bill import Bill
            
            scheduled_bills = self.db.query(Bill).filter(
                Bill.business_id == business_id,
                Bill.status == "scheduled",
                Bill.scheduled_payment_date.isnot(None)
            ).all()
            
            total_scheduled = sum(bill.amount for bill in scheduled_bills)
            total_reserved = sum(bill.reserve_amount for bill in scheduled_bills)
            
            return {
                "business_id": business_id,
                "scheduled_count": len(scheduled_bills),
                "total_scheduled_amount": float(total_scheduled),
                "total_reserved_amount": float(total_reserved),
                "scheduled_payments": [
                    {
                        "bill_id": bill.bill_id,
                        "amount": float(bill.amount),
                        "scheduled_date": bill.scheduled_payment_date.isoformat(),
                        "reserve_allocation_id": bill.reserve_allocation_id,
                        "is_reserved": bill.is_reserved
                    }
                    for bill in scheduled_bills
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get scheduled payment summary for business {business_id}: {e}")
            return {
                "business_id": business_id,
                "scheduled_count": 0,
                "total_scheduled_amount": 0.0,
                "total_reserved_amount": 0.0,
                "scheduled_payments": []
            }
