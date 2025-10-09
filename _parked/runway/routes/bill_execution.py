"""
Bill Execution Routes - Parked for Future Ramp Implementation

These routes contain bill approval and payment execution endpoints
that were moved from runway/routes/bills.py to maintain QBO-honest architecture.

QBO is only a ledger rail - it cannot execute payments or approve bills.
These routes will be implemented by Ramp when payment execution is enabled.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime

from infra.database.session import get_db
from infra.auth.auth import get_current_business_id, get_current_user
from domains.ap.schemas.bill import BillApprovalRequest
from _parked.domains.ap.services.bill_payment_service import BillPaymentService

router = APIRouter(prefix="/bills", tags=["A/P Bill Execution - Parked"])

def get_execution_services(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    """Get execution services - will be implemented by Ramp."""
    return {
        "bill_payment_service": BillPaymentService(db, business_id)
    }

@router.put("/{bill_id}/approve")
async def approve_bill(
    bill_id: int,
    approval_data: BillApprovalRequest,
    services: Dict = Depends(get_execution_services),
    current_user: dict = Depends(get_current_user)
):
    """
    Approve a bill for payment - PARKED for Ramp implementation.
    
    This endpoint was moved from runway/routes/bills.py to maintain
    QBO-honest architecture. Will be implemented by Ramp.
    """
    try:
        bill_payment_service = services["bill_payment_service"]
        
        # Future Ramp implementation
        result = await bill_payment_service.approve_bill_for_payment(str(bill_id))
        
        return {
            "message": "Bill approval - will be implemented by Ramp",
            "bill_id": bill_id,
            "status": "parked",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bill approval error: {str(e)}"
        )

@router.post("/{bill_id}/schedule-payment")
async def schedule_bill_payment(
    bill_id: int,
    payment_data: dict,
    services: Dict = Depends(get_execution_services),
    current_user: dict = Depends(get_current_user)
):
    """
    Schedule bill payment - PARKED for Ramp implementation.
    
    This endpoint was moved from runway/routes/bills.py to maintain
    QBO-honest architecture. Will be implemented by Ramp.
    """
    try:
        bill_payment_service = services["bill_payment_service"]
        
        # Future Ramp implementation
        scheduled_date = datetime.fromisoformat(payment_data.get("scheduled_date"))
        result = await bill_payment_service.schedule_payment(str(bill_id), scheduled_date)
        
        return {
            "message": "Bill payment scheduling - will be implemented by Ramp",
            "bill_id": bill_id,
            "status": "parked",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment scheduling error: {str(e)}"
        )
