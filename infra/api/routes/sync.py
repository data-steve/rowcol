from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from infra.database.session import get_db
from infra.qbo.smart_sync import SmartSyncService
from infra.jobs.enums import SyncStrategy, SyncPriority
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
            smart_sync = SmartSyncService(business_id, "", db)
            qbo_client = QBOClient(business_id)
            
            # Check if sync is needed
            if not smart_sync.should_sync("qbo", SyncStrategy.USER_ACTION):
                cached_data = smart_sync.get_cache("qbo")
                if cached_data:
                    return {"status": "success", "platform": platform, "data": cached_data, "cached": True}
            
            # Execute sync with retry logic
            result = await smart_sync.execute_with_retry(
                qbo_client.get_all_data, max_attempts=3
            )
            
            # Cache results
            smart_sync.set_cache("qbo", result, ttl_minutes=240)
            smart_sync.record_user_activity("on_demand_sync")
            
            return {"status": "success", "platform": platform, "data": result, "cached": False}
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
            smart_sync = SmartSyncService(business_id, "", db)
            qbo_client = QBOClient(business_id)
            
            # Check if sync is needed
            if not smart_sync.should_sync("qbo", SyncStrategy.EVENT_TRIGGERED):
                cached_data = smart_sync.get_cache("qbo")
                if cached_data:
                    return {"status": "success", "platform": platform, "event_type": event_type, "data": cached_data, "cached": True}
            
            # Execute sync with retry logic
            result = await smart_sync.execute_with_retry(
                qbo_client.get_all_data, max_attempts=3
            )
            
            # Cache results
            smart_sync.set_cache("qbo", result, ttl_minutes=240)
            smart_sync.record_user_activity(f"event_triggered_sync_{event_type}")
            
            return {"status": "success", "platform": platform, "event_type": event_type, "data": result, "cached": False}
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
            smart_sync = SmartSyncService(business_id, "", db)
            # Return basic status info
            return {
                "platform": platform, 
                "status": "available", 
                "service": "SmartSyncService",
                "can_sync": smart_sync.should_sync("qbo", SyncStrategy.SCHEDULED),
                "cache_status": "available" if smart_sync.get_cache("qbo") else "empty"
            }
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
                smart_sync = SmartSyncService(business_id, "", db)
                status[platform] = {
                    "platform": platform, 
                    "status": "available", 
                    "service": "SmartSyncService",
                    "can_sync": smart_sync.should_sync("qbo", SyncStrategy.SCHEDULED),
                    "cache_status": "available" if smart_sync.get_cache("qbo") else "empty"
                }
        
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
            smart_sync = SmartSyncService(business_id, "", db)
            return {
                "platform": platform,
                "would_sync": smart_sync.should_sync("qbo", SyncStrategy.SCHEDULED),
                "status": "available",
                "service": "SmartSyncService",
                "cache_status": "available" if smart_sync.get_cache("qbo") else "empty",
                "message": "This endpoint tests sync logic without actually syncing"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
