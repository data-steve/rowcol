"""
Sync Strategies and Priorities

Generic sync timing and strategy definitions that can be used across
all platforms and services for intelligent data synchronization.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from .enums import SyncStrategy, SyncPriority

logger = logging.getLogger(__name__)

class SyncTimingManager:
    """
    Manages sync timing and intervals for different strategies and priorities.
    
    This replaces the timing logic from SmartSync and provides a generic
    way to determine when syncs should occur across all platforms.
    """
    
    def __init__(self, business_id: str):
        self.business_id = business_id
        self.last_sync = {}  # Track last sync time per platform
        self.user_activity = {}  # Track user activity patterns
        self.logger = logging.getLogger(f"{__name__}.{business_id}")
        
        # Sync intervals (in minutes) - can be overridden per platform
        self.sync_intervals = {
            SyncStrategy.ON_DEMAND: 0,      # Immediate
            SyncStrategy.EVENT_TRIGGERED: 5, # 5 minutes after user action
            SyncStrategy.SCHEDULED: 60,     # 1 hour for scheduled syncs
            SyncStrategy.BACKGROUND: 240    # 4 hours for background syncs
        }
        
        # Priority multipliers for intervals
        self.priority_multipliers = {
            SyncPriority.HIGH: 0.5,    # High priority = faster sync
            SyncPriority.MEDIUM: 1.0,  # Normal speed
            SyncPriority.LOW: 2.0      # Low priority = slower sync
        }
    
    def should_sync(self, platform: str, strategy: SyncStrategy, priority: SyncPriority = SyncPriority.MEDIUM) -> bool:
        """
        Determine if a sync should occur based on strategy, priority, and timing.
        
        Args:
            platform: Platform identifier (e.g., 'qbo', 'plaid')
            strategy: Sync strategy
            priority: Sync priority
            
        Returns:
            True if sync should occur, False otherwise
        """
        now = datetime.utcnow()
        
        if strategy == SyncStrategy.ON_DEMAND:
            return True  # Always sync on demand
        
        if strategy == SyncStrategy.SCHEDULED:
            return self._should_scheduled_sync(platform, now)
        
        if strategy == SyncStrategy.EVENT_TRIGGERED:
            return self._should_event_sync(platform, now)
        
        if strategy == SyncStrategy.BACKGROUND:
            return self._should_background_sync(platform, now)
        
        return False
    
    def _should_scheduled_sync(self, platform: str, now: datetime) -> bool:
        """Check if scheduled sync should occur."""
        if platform not in self.last_sync:
            return True  # First sync
        
        last_sync_time = self.last_sync[platform]
        interval_minutes = self.sync_intervals[SyncStrategy.SCHEDULED]
        
        return (now - last_sync_time).total_seconds() >= (interval_minutes * 60)
    
    def _should_event_sync(self, platform: str, now: datetime) -> bool:
        """Check if event-triggered sync should occur."""
        if platform not in self.last_sync:
            return True  # First sync
        
        last_sync_time = self.last_sync[platform]
        interval_minutes = self.sync_intervals[SyncStrategy.EVENT_TRIGGERED]
        
        # Event syncs should happen more frequently after user activity
        return (now - last_sync_time).total_seconds() >= (interval_minutes * 60)
    
    def _should_background_sync(self, platform: str, now: datetime) -> bool:
        """Check if background sync should occur."""
        if platform not in self.last_sync:
            return True  # First sync
        
        last_sync_time = self.last_sync[platform]
        interval_minutes = self.sync_intervals[SyncStrategy.BACKGROUND]
        
        return (now - last_sync_time).total_seconds() >= (interval_minutes * 60)
    
    def record_sync(self, platform: str, strategy: SyncStrategy, success: bool = True):
        """Record that a sync occurred."""
        self.last_sync[platform] = datetime.utcnow()
        
        if success:
            self.logger.info(f"Recorded successful {strategy.value} sync for {platform}")
        else:
            self.logger.warning(f"Recorded failed {strategy.value} sync for {platform}")
    
    def record_user_activity(self, platform: str):
        """Record user activity to influence sync timing."""
        self.user_activity[platform] = datetime.utcnow()
        self.logger.debug(f"Recorded user activity for {platform}")
    
    def get_next_sync_time(self, platform: str, strategy: SyncStrategy) -> Optional[datetime]:
        """Get the next recommended sync time for a platform."""
        if platform not in self.last_sync:
            return datetime.utcnow()  # Sync immediately if never synced
        
        last_sync = self.last_sync[platform]
        interval_minutes = self.sync_intervals[strategy]
        
        return last_sync + timedelta(minutes=interval_minutes)
    
    def get_sync_status(self, platform: str) -> Dict[str, Any]:
        """Get sync status information for a platform."""
        now = datetime.utcnow()
        
        if platform not in self.last_sync:
            return {
                "platform": platform,
                "last_sync": None,
                "next_sync": datetime.utcnow(),
                "status": "never_synced"
            }
        
        last_sync = self.last_sync[platform]
        time_since_sync = (now - last_sync).total_seconds()
        
        return {
            "platform": platform,
            "last_sync": last_sync.isoformat(),
            "next_sync": self.get_next_sync_time(platform, SyncStrategy.SCHEDULED),
            "minutes_since_sync": int(time_since_sync / 60),
            "status": "synced" if time_since_sync < 3600 else "stale"
        }
