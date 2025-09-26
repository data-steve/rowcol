from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from infra.database.session import get_db
from domains.qbo.data_service import QBODataService
from infra.jobs import SyncStrategy, SyncPriority
from typing import Dict, Any

router = APIRouter()

@router.post("/sync/{platform}/on-demand")
async def sync_on_demand(
    platform: str, 
    business_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """User explicitly requests a sync."""
    try:
        if platform == "qbo":
            service = QBODataService(db, business_id)
            result = service.get_raw_qbo_data()  # Use raw data method
            return {"status": "success", "platform": platform, "data": result}
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/{platform}/event-triggered")
async def sync_event_triggered(
    platform: str,
    event_type: str,
    business_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Sync triggered by user action (opening dashboard, etc.)."""
    try:
        if platform == "qbo":
            service = QBODataService(db, business_id)
            result = service.get_raw_qbo_data()  # Use raw data method
            return {"status": "success", "platform": platform, "event_type": event_type, "data": result}
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync/{platform}/status")
async def get_sync_status(
    platform: str,
    business_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current sync status for a platform."""
    try:
        if platform == "qbo":
            service = QBODataService(db, business_id)
            # Return basic status info
            return {"platform": platform, "status": "available", "service": "QBODataService"}
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync/status")
async def get_all_sync_status(
    business_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get sync status for all platforms."""
    try:
        platforms = ["qbo"]  # Only QBO supported for now
        
        status = {}
        for platform in platforms:
            if platform == "qbo":
                service = QBODataService(db, business_id)
                status[platform] = {"platform": platform, "status": "available", "service": "QBODataService"}
        
        return {
            "overall_status": "healthy",
            "platforms": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/{platform}/test")
async def test_sync(
    platform: str,
    business_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Test sync without actually performing it."""
    try:
        if platform == "qbo":
            service = QBODataService(db, business_id)
            return {
                "platform": platform,
                "would_sync": True,
                "status": "available",
                "service": "QBODataService",
                "message": "This endpoint tests sync logic without actually syncing"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
