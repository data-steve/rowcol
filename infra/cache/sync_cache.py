"""
Sync Result Caching

Generic caching utilities for sync results that can be used across
all platforms and services for intelligent data caching.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

class SyncCache:
    """
    Manages caching of sync results with TTL and business isolation.
    
    This replaces the caching logic from SmartSync and provides a generic
    way to cache sync results across all platforms.
    """
    
    def __init__(self, business_id: str, default_ttl_minutes: int = 60):
        self.business_id = business_id
        self.default_ttl_minutes = default_ttl_minutes
        self.cache = {}  # In-memory cache: {platform: {data, expires_at}}
        self.logger = logging.getLogger(f"{__name__}.{business_id}")
    
    def get(self, platform: str, key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached sync result for a platform.
        
        Args:
            platform: Platform identifier (e.g., 'qbo', 'plaid')
            key: Optional specific cache key within platform
            
        Returns:
            Cached data or None if not found/expired
        """
        if platform not in self.cache:
            return None
        
        cache_entry = self.cache[platform]
        
        # Check if expired
        if datetime.utcnow() > cache_entry['expires_at']:
            self.logger.debug(f"Cache expired for {platform}")
            del self.cache[platform]
            return None
        
        # Return specific key or entire platform data
        if key:
            return cache_entry['data'].get(key)
        else:
            return cache_entry['data']
    
    def set(self, platform: str, data: Dict[str, Any], ttl_minutes: Optional[int] = None) -> None:
        """
        Cache sync result for a platform.
        
        Args:
            platform: Platform identifier
            data: Data to cache
            ttl_minutes: Time to live in minutes (uses default if None)
        """
        ttl = ttl_minutes or self.default_ttl_minutes
        expires_at = datetime.utcnow() + timedelta(minutes=ttl)
        
        self.cache[platform] = {
            'data': data,
            'expires_at': expires_at,
            'cached_at': datetime.utcnow()
        }
        
        self.logger.debug(f"Cached data for {platform} (TTL: {ttl} minutes)")
    
    def invalidate(self, platform: str, key: Optional[str] = None) -> None:
        """
        Invalidate cache for a platform or specific key.
        
        Args:
            platform: Platform identifier
            key: Optional specific key to invalidate
        """
        if platform not in self.cache:
            return
        
        if key:
            # Remove specific key
            if key in self.cache[platform]['data']:
                del self.cache[platform]['data'][key]
                self.logger.debug(f"Invalidated key '{key}' for {platform}")
        else:
            # Remove entire platform cache
            del self.cache[platform]
            self.logger.debug(f"Invalidated entire cache for {platform}")
    
    def is_valid(self, platform: str) -> bool:
        """Check if cache entry is valid (exists and not expired)."""
        if platform not in self.cache:
            return False
        
        return datetime.utcnow() <= self.cache[platform]['expires_at']
    
    def get_cache_age(self, platform: str) -> Optional[str]:
        """Get age of cache entry in human-readable format."""
        if platform not in self.cache:
            return None
        
        cached_at = self.cache[platform]['cached_at']
        age_seconds = (datetime.utcnow() - cached_at).total_seconds()
        
        if age_seconds < 60:
            return f"{int(age_seconds)} seconds"
        elif age_seconds < 3600:
            return f"{int(age_seconds / 60)} minutes"
        else:
            return f"{int(age_seconds / 3600)} hours"
    
    def get_cache_info(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get detailed cache information for a platform."""
        if platform not in self.cache:
            return None
        
        entry = self.cache[platform]
        now = datetime.utcnow()
        
        return {
            "platform": platform,
            "cached_at": entry['cached_at'].isoformat(),
            "expires_at": entry['expires_at'].isoformat(),
            "age": self.get_cache_age(platform),
            "is_valid": self.is_valid(platform),
            "ttl_remaining_minutes": max(0, (entry['expires_at'] - now).total_seconds() / 60),
            "data_keys": list(entry['data'].keys()) if isinstance(entry['data'], dict) else None
        }
    
    def clear_all(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        self.logger.info(f"Cleared all cache for business {self.business_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.utcnow()
        valid_entries = 0
        expired_entries = 0
        
        for platform, entry in self.cache.items():
            if now <= entry['expires_at']:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "business_id": self.business_id,
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "platforms": list(self.cache.keys())
        }
