from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from db.session import get_db
from runway.auth.middleware.auth import get_current_business_id
from runway.tray.services.tray import TrayService

router = APIRouter(tags=["Tray"])

def get_tray_service(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
) -> TrayService:
    """Get tray service with business context."""
    return TrayService(db, business_id)

@router.get("/")
async def get_tray_items(
    enhanced: bool = True,
    tray_service: TrayService = Depends(get_tray_service)
):
    """
    Get tray items with optional enhanced Must Pay vs Can Delay categorization.
    
    Args:
        enhanced: If True, includes runway impact analysis and payment categorization
    """
    try:
        business_id = int(tray_service.business_id) if tray_service.business_id else 1
        
        if enhanced:
            items = tray_service.get_enhanced_tray_items(business_id, include_runway_analysis=True)
        else:
            items = tray_service.get_tray_items(business_id)
        
        return {
            "tray_items": items,
            "total_count": len(items),
            "enhanced_analysis": enhanced,
            "categories": {
                "must_pay": len([item for item in items if item.get("payment_category") == "must_pay"]),
                "can_delay": len([item for item in items if item.get("payment_category") == "can_delay"])
            } if enhanced else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tray items: {str(e)}"
        )

@router.get("/categorized")
async def get_categorized_tray_items(
    category: Optional[str] = None,
    tray_service: TrayService = Depends(get_tray_service)
):
    """
    Get tray items filtered by payment category (must_pay or can_delay).
    
    Args:
        category: Filter by 'must_pay' or 'can_delay', or None for all
    """
    try:
        business_id = int(tray_service.business_id) if tray_service.business_id else 1
        enhanced_items = tray_service.get_enhanced_tray_items(business_id, include_runway_analysis=True)
        
        if category:
            filtered_items = [item for item in enhanced_items if item.get("payment_category") == category]
        else:
            filtered_items = enhanced_items
        
        # Group by category for summary
        must_pay_items = [item for item in enhanced_items if item.get("payment_category") == "must_pay"]
        can_delay_items = [item for item in enhanced_items if item.get("payment_category") == "can_delay"]
        
        return {
            "filtered_items": filtered_items,
            "filter_applied": category,
            "summary": {
                "must_pay": {
                    "count": len(must_pay_items),
                    "total_amount": sum(item.get("amount", 0) for item in must_pay_items),
                    "overdue_count": len([item for item in must_pay_items if item.get("urgency_level") == "critical"])
                },
                "can_delay": {
                    "count": len(can_delay_items),
                    "total_amount": sum(item.get("amount", 0) for item in can_delay_items),
                    "potential_savings": sum(item.get("runway_impact", {}).get("impact_days", 0) for item in can_delay_items)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get categorized tray items: {str(e)}"
        )

@router.get("/{item_id}/payment-analysis")
async def get_payment_analysis(
    item_id: int,
    tray_service: TrayService = Depends(get_tray_service)
):
    """
    Get detailed payment decision analysis for a specific tray item.
    
    Shows runway impact, payment scenarios, and decision factors.
    """
    try:
        business_id = int(tray_service.business_id) if tray_service.business_id else 1
        
        # Get the specific tray item
        tray_items = tray_service.get_tray_items(business_id)
        target_item = next((item for item in tray_items if item.get("id") == item_id), None)
        
        if not target_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tray item {item_id} not found"
            )
        
        # Create bill data for analysis
        bill_data = {
            "amount": target_item.get("amount", 0),
            "due_date": target_item.get("due_date"),
            "vendor_name": target_item.get("description", "Unknown"),
            "type": target_item.get("type", "")
        }
        
        # Get comprehensive analysis
        analysis = tray_service.get_payment_decision_analysis(bill_data)
        
        return {
            "tray_item_id": item_id,
            "analysis": analysis,
            "generated_at": tray_service._get_current_timestamp()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment analysis: {str(e)}"
        )

@router.post("/{item_id}/categorize")
async def categorize_tray_item(
    item_id: int,
    tray_service: TrayService = Depends(get_tray_service)
):
    """
    Get or update categorization for a specific tray item.
    
    Returns Must Pay vs Can Delay analysis for the item.
    """
    try:
        business_id = int(tray_service.business_id) if tray_service.business_id else 1
        
        # Get the specific tray item
        tray_items = tray_service.get_tray_items(business_id)
        target_item = next((item for item in tray_items if item.get("id") == item_id), None)
        
        if not target_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tray item {item_id} not found"
            )
        
        # Create bill data for categorization
        bill_data = {
            "amount": target_item.get("amount", 0),
            "due_date": target_item.get("due_date"),
            "vendor_name": target_item.get("description", "Unknown"),
            "type": target_item.get("type", "")
        }
        
        # Get categorization
        category = tray_service.categorize_bill_urgency(bill_data)
        
        return {
            "tray_item_id": item_id,
            "category": category,
            "reasoning": "Based on amount, due date, vendor type, and current runway position",
            "bill_data": bill_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to categorize tray item: {str(e)}"
        )

@router.post("/{item_id}/confirm")
async def confirm_tray_action(
    item_id: int,
    action: str,
    invoice_ids: Optional[List[int]] = None,
    tray_service: TrayService = Depends(get_tray_service)
):
    """
    Confirm an action on a tray item with enhanced tracking.
    
    Records the action and updates any related runway impact calculations.
    """
    try:
        business_id = int(tray_service.business_id) if tray_service.business_id else 1
        
        result = tray_service.confirm_action(business_id, item_id, action, invoice_ids)
        
        return {
            "message": f"Action '{action}' confirmed for tray item {item_id}",
            "result": result,
            "timestamp": tray_service._get_current_timestamp()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm action: {str(e)}"
        )

@router.get("/runway-impact/summary")
async def get_tray_runway_impact_summary(
    tray_service: TrayService = Depends(get_tray_service)
):
    """
    Get summary of runway impact from all tray items.
    
    Shows total potential impact and categorization breakdown.
    """
    try:
        business_id = int(tray_service.business_id) if tray_service.business_id else 1
        enhanced_items = tray_service.get_enhanced_tray_items(business_id, include_runway_analysis=True)
        
        must_pay_items = [item for item in enhanced_items if item.get("payment_category") == "must_pay"]
        can_delay_items = [item for item in enhanced_items if item.get("payment_category") == "can_delay"]
        
        must_pay_impact = sum(item.get("runway_impact", {}).get("impact_days", 0) for item in must_pay_items)
        can_delay_impact = sum(item.get("runway_impact", {}).get("impact_days", 0) for item in can_delay_items)
        
        must_pay_amount = sum(item.get("amount", 0) for item in must_pay_items)
        can_delay_amount = sum(item.get("amount", 0) for item in can_delay_items)
        
        return {
            "summary": {
                "total_items": len(enhanced_items),
                "must_pay": {
                    "count": len(must_pay_items),
                    "total_amount": must_pay_amount,
                    "runway_impact_days": must_pay_impact
                },
                "can_delay": {
                    "count": len(can_delay_items),
                    "total_amount": can_delay_amount,
                    "runway_impact_days": can_delay_impact,
                    "potential_runway_extension": can_delay_impact
                }
            },
            "recommendations": [
                {
                    "type": "immediate_action",
                    "message": f"Focus on {len(must_pay_items)} must-pay items totaling ${must_pay_amount:,.2f}",
                    "priority": "high"
                },
                {
                    "type": "cash_flow_optimization",
                    "message": f"Consider delaying {len(can_delay_items)} items to extend runway by {can_delay_impact:.1f} days",
                    "priority": "medium"
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get runway impact summary: {str(e)}"
        )
