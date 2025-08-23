from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio
import logging
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()

class SyncStrategy(Enum):
    """Different sync strategies based on user needs."""
    ON_DEMAND = "on_demand"           # User explicitly requests sync
    SCHEDULED = "scheduled"           # Background scheduled sync
    EVENT_TRIGGERED = "event_triggered"  # Sync triggered by user action
    BACKGROUND = "background"         # Low-priority background sync

class SyncPriority(Enum):
    """Sync priority levels."""
    HIGH = "high"       # User is actively waiting
    MEDIUM = "medium"   # Important but not urgent
    LOW = "low"         # Background maintenance

class SmartSyncService:
    """Smart sync service that intelligently manages data synchronization."""
    
    def __init__(self, db: Session):
        self.db = db
        self.last_sync = {}  # Track last sync time per platform
        self.sync_cache = {}  # Cache sync results
        self.user_activity = {}  # Track user activity patterns
        self.logger = logging.getLogger(__name__)
        
        # Sync intervals (in minutes)
        self.sync_intervals = {
            "qbo": {
                "min_interval": 30,      # Don't sync more than every 30 minutes
                "business_hours": 240,   # Every 4 hours during business hours
                "month_end": 120,        # Every 2 hours during month-end
                "tax_season": 60         # Every hour during tax season
            },
            "jobber": {
                "min_interval": 15,      # Jobber can be synced more frequently
                "business_hours": 120,   # Every 2 hours
                "month_end": 60         # Every hour during month-end
            },
            "stripe": {
                "min_interval": 5,       # Stripe can be very frequent
                "business_hours": 60,    # Every hour
                "month_end": 30         # Every 30 minutes during month-end
            }
        }
    
    def should_sync(self, platform: str, strategy: SyncStrategy, priority: SyncPriority = SyncPriority.MEDIUM) -> bool:
        """Determine if we should sync based on strategy and timing."""
        now = datetime.now()
        last_sync_time = self.last_sync.get(platform)
        
        # If never synced, always sync
        if not last_sync_time:
            return True
        
        # Calculate time since last sync
        time_since_last = (now - last_sync_time).total_seconds() / 60  # minutes
        
        # Get minimum interval for this platform
        min_interval = self.sync_intervals[platform]["min_interval"]
        
        # High priority requests can override timing
        if priority == SyncPriority.HIGH:
            return time_since_last >= (min_interval / 2)  # Allow more frequent syncs for urgent requests
        
        # Check minimum interval
        if time_since_last < min_interval:
            return False
        
        # Strategy-specific logic
        if strategy == SyncStrategy.ON_DEMAND:
            # User explicitly requested sync - allow it
            return True
        
        elif strategy == SyncStrategy.SCHEDULED:
            # Scheduled sync - check business hours and special periods
            return self._should_scheduled_sync(platform, now)
        
        elif strategy == SyncStrategy.EVENT_TRIGGERED:
            # Event-triggered sync - check if user is active
            return self._should_event_sync(platform, now)
        
        elif strategy == SyncStrategy.BACKGROUND:
            # Background sync - only when system is idle
            return self._should_background_sync(platform, now)
        
        return False
    
    def _should_scheduled_sync(self, platform: str, now: datetime) -> bool:
        """Determine if scheduled sync should run."""
        # Check if it's business hours (9 AM - 5 PM)
        is_business_hours = 9 <= now.hour < 17
        
        # Check if it's month-end (last 3 days of month)
        is_month_end = now.day >= 28
        
        # Check if it's tax season (Jan-Apr, Sep-Oct)
        is_tax_season = now.month in [1, 2, 3, 4, 9, 10]
        
        # Get appropriate interval
        if is_tax_season:
            interval = self.sync_intervals[platform]["tax_season"]
        elif is_month_end:
            interval = self.sync_intervals[platform]["month_end"]
        elif is_business_hours:
            interval = self.sync_intervals[platform]["business_hours"]
        else:
            interval = self.sync_intervals[platform]["min_interval"] * 4  # Much less frequent off-hours
        
        # Check if enough time has passed
        last_sync_time = self.last_sync.get(platform)
        if not last_sync_time:
            return True
        
        time_since_last = (now - last_sync_time).total_seconds() / 60
        return time_since_last >= interval
    
    def _should_event_sync(self, platform: str, now: datetime) -> bool:
        """Determine if event-triggered sync should run."""
        # Check if user is actively working
        user_active = self._is_user_active(now)
        
        # If user is active, be more aggressive with syncs
        if user_active:
            min_interval = self.sync_intervals[platform]["min_interval"] / 2
        else:
            min_interval = self.sync_intervals[platform]["min_interval"]
        
        last_sync_time = self.last_sync.get(platform)
        if not last_sync_time:
            return True
        
        time_since_last = (now - last_sync_time).total_seconds() / 60
        return time_since_last >= min_interval
    
    def _should_background_sync(self, platform: str, now: datetime) -> bool:
        """Determine if background sync should run."""
        # Only run background syncs during off-hours or when system is idle
        is_business_hours = 9 <= now.hour < 17
        is_weekend = now.weekday() >= 5
        
        if is_business_hours and not is_weekend:
            # During business hours, only if system is very idle
            return self._is_system_idle()
        else:
            # Off-hours, allow more frequent background syncs
            last_sync_time = self.last_sync.get(platform)
            if not last_sync_time:
                return True
            
            time_since_last = (now - last_sync_time).total_seconds() / 60
            return time_since_last >= (self.sync_intervals[platform]["min_interval"] * 2)
    
    def _is_user_active(self, now: datetime) -> bool:
        """Check if user is actively working."""
        # Check recent user activity (last 30 minutes)
        recent_activity = self.user_activity.get("last_action")
        if not recent_activity:
            return False
        
        time_since_activity = (now - recent_activity).total_seconds() / 60
        return time_since_activity < 30
    
    def _is_system_idle(self) -> bool:
        """Check if system is idle."""
        # This could check CPU usage, active processes, etc.
        # For now, just check if no recent user activity
        return not self._is_user_active(datetime.now())
    
    def record_user_activity(self, activity_type: str):
        """Record user activity for smart sync decisions."""
        now = datetime.now()
        self.user_activity["last_action"] = now
        self.user_activity["last_activity_type"] = activity_type
        
        # Log activity for analytics
        self.logger.info(f"User activity: {activity_type} at {now}")
    
    def sync_platform(self, platform: str, strategy: SyncStrategy, priority: SyncPriority = SyncPriority.MEDIUM) -> Dict[str, Any]:
        """Sync a specific platform with smart timing."""
        if not self.should_sync(platform, strategy, priority):
            return {
                "status": "skipped",
                "reason": "Sync not needed based on timing and strategy",
                "platform": platform,
                "strategy": strategy.value,
                "priority": priority.value
            }
        
        try:
            # Perform the actual sync
            result = self._perform_sync(platform)
            
            # Update last sync time
            self.last_sync[platform] = datetime.now()
            
            # Cache results
            self.sync_cache[platform] = {
                "data": result,
                "timestamp": datetime.now(),
                "strategy": strategy.value
            }
            
            return {
                "status": "success",
                "platform": platform,
                "strategy": strategy.value,
                "priority": priority.value,
                "data": result,
                "synced_at": self.last_sync[platform].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Sync failed for {platform}: {str(e)}")
            return {
                "status": "error",
                "platform": platform,
                "strategy": strategy.value,
                "priority": priority.value,
                "error": str(e)
            }
    
    def _perform_sync(self, platform: str) -> Dict[str, Any]:
        """Perform the actual sync for a platform."""
        if platform == "qbo":
            from .qbo_integration import QBOIntegrationService
            service = QBOIntegrationService(self.db)
            return {
                "transactions": service.fetch_transactions(),
                "jobs": service.fetch_jobs(),
                "vendors": service.fetch_vendors()
            }
        elif platform == "jobber":
            # TODO: Implement Jobber sync
            return {"status": "not_implemented"}
        elif platform == "stripe":
            # TODO: Implement Stripe sync
            return {"status": "not_implemented"}
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def get_sync_status(self, platform: str) -> Dict[str, Any]:
        """Get current sync status for a platform."""
        last_sync = self.last_sync.get(platform)
        cached_data = self.sync_cache.get(platform)
        
        return {
            "platform": platform,
            "last_sync": last_sync.isoformat() if last_sync else None,
            "time_since_last": self._get_time_since_last(platform),
            "cached_data": cached_data is not None,
            "cache_age": self._get_cache_age(platform),
            "next_scheduled_sync": self._get_next_scheduled_sync(platform)
        }
    
    def _get_time_since_last(self, platform: str) -> Optional[str]:
        """Get human-readable time since last sync."""
        last_sync = self.last_sync.get(platform)
        if not last_sync:
            return "Never"
        
        now = datetime.now()
        diff = now - last_sync
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    
    def _get_cache_age(self, platform: str) -> Optional[str]:
        """Get human-readable cache age."""
        cached_data = self.sync_cache.get(platform)
        if not cached_data:
            return None
        
        now = datetime.now()
        diff = now - cached_data["timestamp"]
        
        if diff.seconds < 60:
            return f"{diff.seconds} seconds"
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes} minutes"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hours"
    
    def _get_next_scheduled_sync(self, platform: str) -> Optional[str]:
        """Get when the next scheduled sync will run."""
        now = datetime.now()
        last_sync = self.last_sync.get(platform)
        
        if not last_sync:
            return "Immediately"
        
        # Calculate next sync time based on business hours
        if 9 <= now.hour < 17:  # Business hours
            interval = self.sync_intervals[platform]["business_hours"]
        else:  # Off hours
            interval = self.sync_intervals[platform]["min_interval"] * 4
        
        next_sync = last_sync + timedelta(minutes=interval)
        return next_sync.strftime("%Y-%m-%d %H:%M")
