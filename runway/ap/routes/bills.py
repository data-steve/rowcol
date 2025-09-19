"""
Runway AP Bills API Routes

User-facing API endpoints for bill management workflows.
Orchestrates domains/ap/ services with runway-specific business logic.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Optional

from db.session import get_db
from runway.auth.middleware.auth import get_current_business_id
from domains.ap.services.bill_ingestion import BillService
from domains.ap.services.payment import PaymentService
from domains.integrations.smart_sync import SmartSyncService
from runway.reserves.services.runway_reserve_service import RunwayReserveService
from domains.ap.schemas.bill import BillResponse, BillApprovalRequest
from domains.ap.schemas.payment import PaymentScheduleRequest
from common.exceptions import ValidationError

router = APIRouter(prefix="/bills", tags=["AP Bills"])

def get_services(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    """Get all required services with business context."""
    return {
        "bill_service": BillService(db, business_id),
        "payment_service": PaymentService(db, business_id),
        "smart_sync": SmartSyncService(db, business_id),
        "reserve_service": RunwayReserveService(db, business_id)
    }

@router.get("/", response_model=List[BillResponse])
async def list_bills(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    services: Dict = Depends(get_services)
):
    """
    List bills with filtering and pagination.
    
    Orchestrates bill retrieval with smart QBO sync and runway impact calculation.
    """
    try:
        bill_service = services["bill_service"]
        
        # Get bills with optional filtering
        bills = bill_service.get_bills_for_review(
            status_filter=status_filter,
            limit=limit,
            offset=offset
        )
        
        # Enhance with runway impact for each bill
        enhanced_bills = []
        for bill in bills:
            bill_dict = bill_service._bill_to_dict(bill)
            
            # Add runway impact calculation
            if bill.amount:
                impact_days = bill.amount / 1000  # Simplified calculation
                bill_dict["runway_impact_days"] = impact_days
                bill_dict["priority_score"] = bill_service.calculate_bill_priority(bill)
            
            enhanced_bills.append(bill_dict)
        
        return enhanced_bills
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list bills: {str(e)}"
        )

@router.post("/upload")
async def upload_bill(
    file: UploadFile = File(...),
    vendor_id: Optional[int] = None,
    services: Dict = Depends(get_services)
):
    """
    Upload and process a bill document.
    
    Orchestrates document processing, OCR extraction, and bill creation
    with automatic vendor matching and approval workflow routing.
    """
    try:
        bill_service = services["bill_service"]
        
        # Process the uploaded bill
        result = await bill_service.process_bill(file, vendor_id)
        
        # Trigger smart QBO sync to get latest vendor data
        smart_sync = services["smart_sync"]
        smart_sync.record_user_activity("bill_upload")
        
        return {
            "message": "Bill uploaded and processed successfully",
            "bill_id": result["bill_id"],
            "status": "review_required" if result.get("requires_review") else "processed"
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload bill: {str(e)}"
        )

@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: int,
    services: Dict = Depends(get_services)
):
    """Get detailed bill information with runway impact analysis."""
    try:
        bill_service = services["bill_service"]
        
        bill = bill_service._get_bill_or_raise(bill_id)
        bill_dict = bill_service._bill_to_dict(bill)
        
        # Add enhanced runway analysis
        reserve_service = services["reserve_service"]
        runway_calc = reserve_service.calculate_runway_with_reserves()
        
        bill_dict["runway_analysis"] = {
            "current_runway_days": runway_calc.get("runway_days", 0),
            "impact_if_paid_today": bill.amount / runway_calc.get("daily_burn", 1),
            "recommended_payment_date": bill.due_date,
            "can_delay": bill_service.get_days_until_due(bill) > 7
        }
        
        return bill_dict
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bill: {str(e)}"
        )

@router.put("/{bill_id}/approve")
async def approve_bill(
    bill_id: int,
    approval_data: BillApprovalRequest,
    services: Dict = Depends(get_services)
):
    """
    Approve a bill for payment.
    
    Orchestrates bill approval with runway reserve allocation
    and automatic payment scheduling based on business rules.
    """
    try:
        bill_service = services["bill_service"]
        payment_service = services["payment_service"]
        reserve_service = services["reserve_service"]
        
        # Get the bill
        bill = bill_service._get_bill_or_raise(bill_id)
        
        # Approve the bill
        success = bill_service.approve_bill_entity(
            bill=bill,
            approved_by_user_id="api_user",  # TODO: Get from auth context
            notes=approval_data.notes
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bill cannot be approved in current status"
            )
        
        # Create runway reserve allocation if needed
        if approval_data.allocate_reserve:
            reserve_service.allocate_reserve_for_bill(
                bill_id=bill_id,
                amount=bill.amount
            )
        
        # Schedule payment if requested
        if approval_data.schedule_payment:
            payment = payment_service.create_payment(
                bill_id=bill_id,
                payment_date=approval_data.payment_date or bill.due_date,
                payment_method=approval_data.payment_method or "ach"
            )
            
            return {
                "message": "Bill approved and payment scheduled",
                "bill_id": bill_id,
                "payment_id": payment.payment_id,
                "scheduled_date": payment.payment_date
            }
        
        return {
            "message": "Bill approved successfully",
            "bill_id": bill_id,
            "status": bill.status
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve bill: {str(e)}"
        )

@router.post("/{bill_id}/schedule-payment")
async def schedule_bill_payment(
    bill_id: int,
    payment_data: PaymentScheduleRequest,
    services: Dict = Depends(get_services)
):
    """
    Schedule payment for an approved bill.
    
    Orchestrates payment creation with runway impact analysis,
    reserve allocation, and smart QBO sync coordination.
    """
    try:
        bill_service = services["bill_service"]
        payment_service = services["payment_service"]
        smart_sync = services["smart_sync"]
        
        # Get the bill
        bill = bill_service._get_bill_or_raise(bill_id)
        
        if bill.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bill must be approved before scheduling payment"
            )
        
        # Create the payment
        payment = payment_service.create_payment(
            bill_id=bill_id,
            payment_date=payment_data.payment_date,
            payment_method=payment_data.payment_method,
            payment_account=payment_data.payment_account,
            created_by_user_id="api_user"  # TODO: Get from auth context
        )
        
        # Schedule QBO sync for payment creation
        smart_sync.record_user_activity("payment_scheduled")
        
        return {
            "message": "Payment scheduled successfully",
            "payment_id": payment.payment_id,
            "bill_id": bill_id,
            "scheduled_date": payment.payment_date,
            "amount": float(payment.amount),
            "method": payment.payment_method
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule payment: {str(e)}"
        )

@router.get("/{bill_id}/runway-impact")
async def get_bill_runway_impact(
    bill_id: int,
    services: Dict = Depends(get_services)
):
    """
    Get detailed runway impact analysis for a specific bill.
    
    Shows how paying this bill would affect runway calculations,
    with scenarios for different payment timing options.
    """
    try:
        bill_service = services["bill_service"]
        reserve_service = services["reserve_service"]
        
        bill = bill_service._get_bill_or_raise(bill_id)
        
        # Get current runway calculation
        runway_calc = reserve_service.calculate_runway_with_reserves()
        current_runway = runway_calc.get("runway_days", 0)
        daily_burn = runway_calc.get("daily_burn", 1)
        
        # Calculate impact scenarios
        impact_today = bill.amount / daily_burn
        impact_due_date = impact_today  # Same impact, different timing
        
        return {
            "bill_id": bill_id,
            "bill_amount": float(bill.amount),
            "current_runway_days": current_runway,
            "impact_scenarios": {
                "pay_today": {
                    "runway_reduction_days": impact_today,
                    "new_runway_days": max(0, current_runway - impact_today)
                },
                "pay_on_due_date": {
                    "runway_reduction_days": impact_due_date,
                    "new_runway_days": max(0, current_runway - impact_due_date),
                    "due_date": bill.due_date.isoformat() if bill.due_date else None
                },
                "delay_30_days": {
                    "runway_reduction_days": impact_due_date,
                    "new_runway_days": max(0, current_runway - impact_due_date),
                    "risk_score": "medium" if bill_service.get_days_until_due(bill) > 30 else "high"
                }
            },
            "recommendations": {
                "can_delay": bill_service.get_days_until_due(bill) > 7,
                "priority": bill_service.calculate_bill_priority(bill),
                "suggested_payment_date": bill.due_date.isoformat() if bill.due_date else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate runway impact: {str(e)}"
        )
