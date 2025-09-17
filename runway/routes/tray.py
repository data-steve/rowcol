from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from db.session import get_db
from runway.tray.services.tray import TrayService
from runway.middleware.auth import verify_token

router = APIRouter(prefix="/runway/tray", tags=["tray"])

# Pydantic schemas for request/response
class ActionConfirmationRequest(BaseModel):
    action: str
    confirmation_data: Optional[Dict[str, Any]] = None

class TrayItemResponse(BaseModel):
    id: int
    type: str
    qbo_id: Optional[str]
    status: str
    priority: str
    priority_score: int
    due_date: Optional[str]
    qbo_deep_link: str
    allowed_roles: List[str]
    actions: List[Dict[str, Any]]
    runway_impact: Dict[str, Any]

class TrayActionResponse(BaseModel):
    item_id: int
    action: str
    status: str
    result: Dict[str, Any]
    qbo_sync_status: str
    timestamp: str

class TraySummaryResponse(BaseModel):
    total_items: int
    by_priority: Dict[str, int]
    by_type: Dict[str, int]
    total_runway_impact: Dict[str, Any]
    urgent_count: int

@router.get("/items", response_model=List[TrayItemResponse])
async def get_tray_items(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get prioritized tray items for a business."""
    try:
        tray_service = TrayService(db)
        items = tray_service.get_tray_items(business_id)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tray items: {str(e)}"
        )

@router.get("/summary", response_model=TraySummaryResponse)
async def get_tray_summary(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get summary of tray items by priority and type."""
    try:
        tray_service = TrayService(db)
        summary = tray_service.get_tray_summary(business_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tray summary: {str(e)}"
        )

@router.post("/items/{tray_item_id}/confirm", response_model=TrayActionResponse)
async def confirm_tray_action(
    tray_item_id: int,
    business_id: str,
    request: ActionConfirmationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Confirm an action on a tray item with QBO integration."""
    try:
        tray_service = TrayService(db)
        result = tray_service.confirm_action(
            business_id=business_id,
            tray_item_id=tray_item_id,
            action=request.action,
            confirmation_data=request.confirmation_data
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm action: {str(e)}"
        )

@router.get("/items/{tray_item_id}/actions")
async def get_item_actions(
    tray_item_id: int,
    business_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get available actions for a specific tray item."""
    try:
        tray_service = TrayService(db)
        items = tray_service.get_tray_items(business_id)
        
        # Find the specific item
        item = next((item for item in items if item["id"] == tray_item_id), None)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tray item not found"
            )
        
        return {
            "item_id": tray_item_id,
            "actions": item["actions"],
            "runway_impact": item["runway_impact"],
            "qbo_deep_link": item["qbo_deep_link"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve item actions: {str(e)}"
        )

@router.get("/health")
async def tray_health_check():
    """Health check endpoint for tray service."""
    return {
        "service": "tray",
        "status": "healthy",
        "features": [
            "priority_scoring",
            "qbo_deep_links", 
            "action_confirmation",
            "runway_impact_calculation"
        ]
    }
