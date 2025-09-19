from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from domains.integrations.smart_sync import SmartSyncService, SyncStrategy, SyncPriority
from typing import Dict, Any

router = APIRouter()

@router.post("/sync/{platform}/on-demand")
async def sync_on_demand(
    platform: str, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """User explicitly requests a sync."""
    try:
        service = SmartSyncService(db)
        
        # Record user activity
        service.record_user_activity(f"manual_sync_{platform}")
        
        # Perform on-demand sync with high priority
        result = service.sync_platform(
            platform=platform,
            strategy=SyncStrategy.ON_DEMAND,
            priority=SyncPriority.HIGH
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/{platform}/event-triggered")
async def sync_event_triggered(
    platform: str,
    event_type: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Sync triggered by user action (opening dashboard, etc.)."""
    try:
        service = SmartSyncService(db)
        
        # Record user activity
        service.record_user_activity(f"{event_type}_{platform}")
        
        # Perform event-triggered sync
        result = service.sync_platform(
            platform=platform,
            strategy=SyncStrategy.EVENT_TRIGGERED,
            priority=SyncPriority.MEDIUM
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync/{platform}/status")
async def get_sync_status(
    platform: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current sync status for a platform."""
    try:
        service = SmartSyncService(db)
        return service.get_sync_status(platform)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync/status")
async def get_all_sync_status(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get sync status for all platforms."""
    try:
        service = SmartSyncService(db)
        platforms = ["qbo", "jobber", "stripe"]
        
        status = {}
        for platform in platforms:
            status[platform] = service.get_sync_status(platform)
        
        return {
            "overall_status": "healthy" if all(s["last_sync"] for s in status.values()) else "needs_sync",
            "platforms": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/{platform}/test")
async def test_sync(
    platform: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Test sync without actually performing it."""
    try:
        service = SmartSyncService(db)
        
        # Check if sync would run
        would_sync = service.should_sync(
            platform=platform,
            strategy=SyncStrategy.ON_DEMAND,
            priority=SyncPriority.HIGH
        )
        
        return {
            "platform": platform,
            "would_sync": would_sync,
            "status": service.get_sync_status(platform),
            "message": "This endpoint tests sync logic without actually syncing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
