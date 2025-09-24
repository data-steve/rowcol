"""
Runway AP Payments API Routes

User-facing API endpoints for payment execution and tracking.
Orchestrates domains/ap/ payment services with runway impact analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime

from db.session import get_db
from runway.infrastructure.auth.middleware.auth import get_current_business_id
from domains.ap.services.payment import PaymentService
from domains.integrations import SmartSyncService
from runway.core.reserve_runway import RunwayReserveService
from domains.ap.schemas.payment import PaymentResponse, PaymentExecutionRequest
from common.exceptions import BusinessRuleViolationError

router = APIRouter(tags=["AP Payments"])

def get_services(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    """Get all required services with business context."""
    return {
        "payment_service": PaymentService(db, business_id),
        "smart_sync": SmartSyncService(db, business_id),
        "reserve_service": RunwayReserveService(db, business_id)
    }

@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    services: Dict = Depends(get_services)
):
    """
    List payments with filtering and runway impact analysis.
    
    Shows payment status, execution progress, and runway impact calculations.
    """
    try:
        payment_service = services["payment_service"]
        
        # Get payments using the payment service
        payments = payment_service.get_payments(
            status_filter=status_filter,
            limit=limit,
            offset=offset
        )
        
        enhanced_payments = []
        for payment in payments:
            payment_dict = payment_service.payment_to_dict(payment)
            
            # Add runway impact analysis
            impact = payment_service.calculate_payment_runway_impact(payment)
            payment_dict["runway_impact"] = impact
            
            enhanced_payments.append(payment_dict)
        
        return enhanced_payments
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list payments: {str(e)}"
        )

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    services: Dict = Depends(get_services)
):
    """Get detailed payment information with execution status and runway impact."""
    try:
        payment_service = services["payment_service"]
        
        payment = payment_service._get_payment_or_raise(payment_id)
        payment_dict = payment_service.payment_to_dict(payment)
        
        # Add enhanced analysis
        reserve_service = services["reserve_service"]
        runway_calc = reserve_service.calculate_runway_with_reserves()
        
        payment_dict["execution_analysis"] = {
            "can_execute": payment_service.can_payment_be_executed(payment),
            "can_cancel": payment_service.can_payment_be_cancelled(payment),
            "requires_approval": payment.requires_approval,
            "days_until_scheduled": (payment.payment_date - datetime.utcnow()).days if payment.payment_date else None,
            "runway_impact_on_execution": payment_service.calculate_payment_runway_impact(payment)
        }
        
        return payment_dict
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment: {str(e)}"
        )

@router.post("/{payment_id}/execute")
async def execute_payment(
    payment_id: int,
    execution_data: PaymentExecutionRequest,
    services: Dict = Depends(get_services)
):
    """
    Execute a scheduled payment.
    
    Orchestrates payment execution with QBO sync, reserve release,
    and runway impact tracking.
    """
    try:
        payment_service = services["payment_service"]
        smart_sync = services["smart_sync"]
        reserve_service = services["reserve_service"]
        
        # Execute the payment workflow
        payment = payment_service.execute_payment_workflow(
            payment_id=payment_id,
            confirmation_number=execution_data.confirmation_number
        )
        
        # Record user activity for smart sync
        smart_sync.record_user_activity("payment_executed")
        
        # Trigger QBO sync for payment recording
        sync_result = smart_sync.sync_platform("qbo", smart_sync.SyncStrategy.EVENT_TRIGGERED)
        
        return {
            "message": "Payment executed successfully",
            "payment_id": payment_id,
            "confirmation_number": payment.confirmation_number,
            "execution_date": payment.execution_date.isoformat(),
            "amount": float(payment.amount),
            "qbo_sync_status": sync_result.get("status", "pending"),
            "runway_impact": payment_service.calculate_payment_runway_impact(payment)
        }
        
    except BusinessRuleViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute payment: {str(e)}"
        )

@router.post("/{payment_id}/cancel")
async def cancel_payment(
    payment_id: int,
    reason: Optional[str] = None,
    services: Dict = Depends(get_services)
):
    """
    Cancel a scheduled payment.
    
    Releases any allocated reserves and updates runway calculations.
    """
    try:
        payment_service = services["payment_service"]
        
        payment = payment_service._get_payment_or_raise(payment_id)
        
        success = payment_service.cancel_payment(
            payment=payment,
            reason=reason or "Cancelled via API"
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment cannot be cancelled in current status"
            )
        
        return {
            "message": "Payment cancelled successfully",
            "payment_id": payment_id,
            "status": payment.status,
            "cancellation_reason": payment.failure_reason
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel payment: {str(e)}"
        )

@router.get("/pending", response_model=List[PaymentResponse])
async def get_pending_payments(
    services: Dict = Depends(get_services)
):
    """
    Get all pending payments requiring attention.
    
    Shows payments that need approval, are scheduled for execution,
    or require reconciliation.
    """
    try:
        payment_service = services["payment_service"]
        
        # Get pending payments using the payment service
        pending_payments = payment_service.get_payments(status_filter="pending")
        
        enhanced_payments = []
        for payment in pending_payments:
            payment_dict = payment_service.payment_to_dict(payment)
            
            # Add action recommendations
            payment_dict["recommended_actions"] = []
            
            if payment_service.can_payment_be_executed(payment):
                payment_dict["recommended_actions"].append("execute")
            
            if payment.requires_approval:
                payment_dict["recommended_actions"].append("approve")
            
            if payment_service.is_payment_executed(payment) and not payment.is_reconciled:
                payment_dict["recommended_actions"].append("reconcile")
            
            enhanced_payments.append(payment_dict)
        
        return enhanced_payments
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending payments: {str(e)}"
        )

@router.post("/batch-execute")
async def batch_execute_payments(
    payment_ids: List[int],
    services: Dict = Depends(get_services)
):
    """
    Execute multiple payments in batch.
    
    Orchestrates batch payment execution with coordinated QBO sync
    and comprehensive runway impact analysis.
    """
    try:
        payment_service = services["payment_service"]
        smart_sync = services["smart_sync"]
        
        results = []
        total_amount = 0
        
        for payment_id in payment_ids:
            try:
                payment = payment_service.execute_payment_workflow(payment_id)
                results.append({
                    "payment_id": payment_id,
                    "status": "executed",
                    "confirmation_number": payment.confirmation_number,
                    "amount": float(payment.amount)
                })
                total_amount += payment.amount
                
            except Exception as e:
                results.append({
                    "payment_id": payment_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Single QBO sync for all payments
        smart_sync.record_user_activity("batch_payment_execution")
        sync_result = smart_sync.sync_platform("qbo", smart_sync.SyncStrategy.ON_DEMAND)
        
        executed_count = len([r for r in results if r["status"] == "executed"])
        failed_count = len([r for r in results if r["status"] == "failed"])
        
        return {
            "message": f"Batch execution completed: {executed_count} executed, {failed_count} failed",
            "total_amount_executed": float(total_amount),
            "execution_results": results,
            "qbo_sync_status": sync_result.get("status", "pending")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute batch payments: {str(e)}"
        )

@router.get("/{payment_id}/runway-impact")
async def get_payment_runway_impact(
    payment_id: int,
    services: Dict = Depends(get_services)
):
    """
    Get detailed runway impact analysis for a specific payment.
    
    Shows current impact, execution scenarios, and reserve implications.
    """
    try:
        payment_service = services["payment_service"]
        reserve_service = services["reserve_service"]
        
        payment = payment_service._get_payment_or_raise(payment_id)
        
        # Get comprehensive runway analysis
        runway_calc = reserve_service.calculate_runway_with_reserves()
        payment_impact = payment_service.calculate_payment_runway_impact(payment)
        
        return {
            "payment_id": payment_id,
            "payment_amount": float(payment.amount),
            "processing_fee": float(payment.processing_fee),
            "total_cost": float(payment_service.get_payment_total_cost(payment)),
            "current_status": payment.status,
            "runway_analysis": {
                "current_runway_days": runway_calc.get("runway_days", 0),
                "impact_on_execution": payment_impact,
                "reserve_status": {
                    "is_reserved": payment.bill.is_reserved if payment.bill else False,
                    "reserve_amount": float(payment.bill.reserve_amount) if payment.bill else 0
                }
            },
            "execution_readiness": {
                "can_execute": payment_service.can_payment_be_executed(payment),
                "requires_approval": payment.requires_approval,
                "scheduled_date": payment.payment_date.isoformat() if payment.payment_date else None,
                "days_until_execution": (payment.payment_date - datetime.utcnow()).days if payment.payment_date else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate payment runway impact: {str(e)}"
        )
