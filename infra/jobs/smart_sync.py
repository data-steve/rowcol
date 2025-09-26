"""
SmartSyncService - Unified Sync Orchestrator

Main orchestrator for sync operations that wraps all job management infrastructure.
Provides a clean interface for sync operations without domain logic coupling.
"""

from typing import Dict, Any, Optional
import logging
from .job_storage import SyncCache
from .sync_strategies import SyncTimingManager
from .enums import SyncStrategy, SyncPriority

logger = logging.getLogger(__name__)

class SmartSyncService:
    """
    Unified sync orchestrator that provides a clean interface for sync operations.
    
    This service wraps all the job management infrastructure (caching, timing, storage)
    into a single, easy-to-use interface. It does NOT contain domain logic - it's
    purely an infrastructure orchestrator.
    """
    
    def __init__(self, business_id: str):
        self.business_id = business_id
        self.timing_manager = SyncTimingManager(business_id)
        self.cache = SyncCache(business_id)
        self.logger = logging.getLogger(f"{__name__}.{business_id}")
    
    # ==================== SYNC TIMING ====================
    
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
        return self.timing_manager.should_sync(platform, strategy, priority)
    
    def record_sync(self, platform: str, strategy: SyncStrategy, success: bool = True):
        """Record that a sync occurred."""
        self.timing_manager.record_sync(platform, strategy, success)
    
    def record_user_activity(self, activity: str):
        """Record user activity to influence sync timing."""
        self.timing_manager.record_user_activity(activity)
    
    def get_sync_status(self, platform: str) -> Dict[str, Any]:
        """Get sync status information for a platform."""
        return self.timing_manager.get_sync_status(platform)
    
    def get_next_sync_time(self, platform: str, strategy: SyncStrategy) -> Optional[str]:
        """Get the next recommended sync time for a platform."""
        next_time = self.timing_manager.get_next_sync_time(platform, strategy)
        return next_time.isoformat() if next_time else None
    
    # ==================== CACHING ====================
    
    def get_cache(self, platform: str, key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached sync result for a platform.
        
        Args:
            platform: Platform identifier (e.g., 'qbo', 'plaid')
            key: Optional specific cache key within platform
            
        Returns:
            Cached data or None if not found/expired
        """
        return self.cache.get(platform, key)
    
    def set_cache(self, platform: str, data: Dict[str, Any], ttl_minutes: Optional[int] = None) -> None:
        """
        Cache sync result for a platform.
        
        Args:
            platform: Platform identifier
            data: Data to cache
            ttl_minutes: Time to live in minutes (uses default if None)
        """
        self.cache.set(platform, data, ttl_minutes)
    
    def invalidate_cache(self, platform: str, key: Optional[str] = None) -> None:
        """
        Invalidate cache for a platform or specific key.
        
        Args:
            platform: Platform identifier
            key: Optional specific key to invalidate
        """
        self.cache.invalidate(platform, key)
    
    def is_cache_valid(self, platform: str) -> bool:
        """Check if cache entry is valid (exists and not expired)."""
        return self.cache.is_valid(platform)
    
    def get_cache_info(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get detailed cache information for a platform."""
        return self.cache.get_cache_info(platform)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear_all()
    
    # ==================== CONVENIENCE METHODS ====================
    
    def sync_with_cache(self, platform: str, strategy: SyncStrategy, 
                       priority: SyncPriority = SyncPriority.MEDIUM,
                       sync_function: callable = None, 
                       cache_key: Optional[str] = None,
                       ttl_minutes: int = 60) -> Optional[Dict[str, Any]]:
        """
        Perform sync with caching logic.
        
        Args:
            platform: Platform identifier
            strategy: Sync strategy
            priority: Sync priority
            sync_function: Function to call for actual sync
            cache_key: Optional specific cache key
            ttl_minutes: Cache TTL in minutes
            
        Returns:
            Cached data or result from sync_function
        """
        # Check if we should sync
        if not self.should_sync(platform, strategy, priority):
            self.logger.debug(f"Sync not needed for {platform} with {strategy.value}")
            return self.get_cache(platform, cache_key)
        
        # Check cache first
        cached_data = self.get_cache(platform, cache_key)
        if cached_data:
            self.logger.debug(f"Returning cached data for {platform}")
            return cached_data
        
        # Perform sync if function provided
        if sync_function:
            try:
                result = sync_function()
                self.set_cache(platform, result, ttl_minutes)
                self.record_sync(platform, strategy, success=True)
                return result
            except Exception as e:
                self.logger.error(f"Sync failed for {platform}: {e}")
                self.record_sync(platform, strategy, success=False)
                return None
        
        return None
    
    def get_platform_status(self, platform: str) -> Dict[str, Any]:
        """Get comprehensive status for a platform including sync and cache info."""
        sync_status = self.get_sync_status(platform)
        cache_info = self.get_cache_info(platform)
        
        return {
            "platform": platform,
            "sync": sync_status,
            "cache": cache_info,
            "business_id": self.business_id
        }
    
    def get_all_platforms_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all platforms that have been synced or cached."""
        platforms = set()
        
        # Get platforms from sync timing
        platforms.update(self.timing_manager.last_sync.keys())
        
        # Get platforms from cache
        platforms.update(self.cache.cache.keys())
        
        return {
            platform: self.get_platform_status(platform)
            for platform in platforms
        }
    
    def reset_platform(self, platform: str) -> None:
        """Reset all sync and cache data for a platform."""
        # Clear sync timing
        if platform in self.timing_manager.last_sync:
            del self.timing_manager.last_sync[platform]
        
        if platform in self.timing_manager.user_activity:
            del self.timing_manager.user_activity[platform]
        
        # Clear cache
        self.cache.invalidate(platform)
        
        self.logger.info(f"Reset all data for platform: {platform}")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get comprehensive service statistics."""
        return {
            "business_id": self.business_id,
            "sync_stats": {
                "platforms_tracked": len(self.timing_manager.last_sync),
                "user_activities": len(self.timing_manager.user_activity)
            },
            "cache_stats": self.cache.get_stats(),
            "platforms": list(set(
                list(self.timing_manager.last_sync.keys()) + 
                list(self.cache.cache.keys())
            ))
        }
