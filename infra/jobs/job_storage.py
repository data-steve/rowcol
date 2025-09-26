"""
Job Storage Service - Unified Job Persistence

Consolidates job storage using existing infra/cache and infra/queue infrastructure.
Merges sync_cache.py, job_storage.py, and deduplication.py into a single cohesive
job storage system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging
import hashlib
import uuid

logger = logging.getLogger(__name__)

# ==================== DEDUPLICATION UTILITIES ====================

def _uuid() -> str: 
    return str(uuid.uuid4())

def sha256(*parts: str) -> str:
    """Generate SHA256 hash for deduplication keys."""
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
    return h.hexdigest()

# ==================== SYNC CACHE ====================

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
        """Get cached sync result for a platform."""
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
        """Cache sync result for a platform."""
        ttl = ttl_minutes or self.default_ttl_minutes
        expires_at = datetime.utcnow() + timedelta(minutes=ttl)
        
        self.cache[platform] = {
            'data': data,
            'expires_at': expires_at,
            'cached_at': datetime.utcnow()
        }
        
        self.logger.debug(f"Cached data for {platform} (TTL: {ttl} minutes)")
    
    def invalidate(self, platform: str, key: Optional[str] = None) -> None:
        """Invalidate cache for a platform or specific key."""
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

# ==================== JOB STORAGE PROVIDERS ====================

class JobStorageProvider(ABC):
    """Abstract base class for job storage providers."""
    
    @abstractmethod
    def save_job(self, job_data: Dict[str, Any]) -> bool:
        """Save job data to storage."""
        pass
    
    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data by ID."""
        pass
    
    @abstractmethod
    def get_jobs(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get jobs with optional filtering."""
        pass
    
    @abstractmethod
    def delete_job(self, job_id: str) -> bool:
        """Delete job from storage."""
        pass
    
    @abstractmethod
    def get_job_by_idempotency_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Get job by idempotency key."""
        pass

class CacheBasedJobStorage(JobStorageProvider):
    """
    Job storage using SyncCache for persistence.
    
    Uses the consolidated SyncCache infrastructure for job storage with
    TTL-based expiration and business isolation.
    """
    
    def __init__(self, business_id: str, default_ttl_hours: int = 24):
        self.business_id = business_id
        self.cache = SyncCache(business_id, default_ttl_minutes=default_ttl_hours * 60)
        self.logger = logging.getLogger(f"{__name__}.{business_id}")
        
        # Job indexes for efficient querying
        self._job_indexes = {
            'by_status': {},  # status -> set of job_ids
            'by_business': set(),  # set of job_ids for this business
            'by_idempotency': {}  # idempotency_key -> job_id
        }
    
    def save_job(self, job_data: Dict[str, Any]) -> bool:
        """Save job data to cache with indexing."""
        try:
            job_id = job_data['id']
            status = job_data.get('status', 'pending')
            idempotency_key = job_data.get('idempotency_key')
            
            # Save job data to cache
            self.cache.set(f"job_{job_id}", job_data, ttl_minutes=24 * 60)  # 24 hours
            
            # Update indexes
            self._update_status_index(job_id, status)
            self._job_indexes['by_business'].add(job_id)
            
            if idempotency_key:
                self._job_indexes['by_idempotency'][idempotency_key] = job_id
            
            self.logger.debug(f"Saved job {job_id} to cache")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save job: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data by ID from cache."""
        return self.cache.get("jobs", f"job_{job_id}")
    
    def get_jobs(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get jobs with filtering using indexes."""
        try:
            # Start with all jobs for this business
            candidate_job_ids = self._job_indexes['by_business'].copy()
            
            # Apply status filter
            if filters and 'status' in filters:
                status = filters['status']
                if status in self._job_indexes['by_status']:
                    candidate_job_ids = candidate_job_ids.intersection(
                        self._job_indexes['by_status'][status]
                    )
                else:
                    candidate_job_ids = set()  # No jobs with this status
            
            # Apply business_id filter (already filtered by business)
            if filters and 'business_id' in filters:
                if filters['business_id'] != self.business_id:
                    candidate_job_ids = set()  # Wrong business
            
            # Get job data and sort by created_at
            jobs = []
            for job_id in candidate_job_ids:
                job_data = self.get_job(job_id)
                if job_data:
                    jobs.append(job_data)
            
            # Sort by created_at (newest first)
            jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return jobs[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get jobs: {e}")
            return []
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job from cache and indexes."""
        try:
            # Get job data first to update indexes
            job_data = self.get_job(job_id)
            if not job_data:
                return False
            
            # Remove from cache
            self.cache.invalidate("jobs", f"job_{job_id}")
            
            # Update indexes
            status = job_data.get('status', 'pending')
            self._remove_from_status_index(job_id, status)
            self._job_indexes['by_business'].discard(job_id)
            
            idempotency_key = job_data.get('idempotency_key')
            if idempotency_key and idempotency_key in self._job_indexes['by_idempotency']:
                del self._job_indexes['by_idempotency'][idempotency_key]
            
            self.logger.debug(f"Deleted job {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    def get_job_by_idempotency_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Get job by idempotency key."""
        job_id = self._job_indexes['by_idempotency'].get(key)
        if job_id:
            return self.get_job(job_id)
        return None
    
    def _update_status_index(self, job_id: str, status: str):
        """Update status index for efficient filtering."""
        if status not in self._job_indexes['by_status']:
            self._job_indexes['by_status'][status] = set()
        self._job_indexes['by_status'][status].add(job_id)
    
    def _remove_from_status_index(self, job_id: str, status: str):
        """Remove job from status index."""
        if status in self._job_indexes['by_status']:
            self._job_indexes['by_status'][status].discard(job_id)

class RedisBasedJobStorage(JobStorageProvider):
    """
    Job storage using Redis with deduplication utilities.
    
    Uses Redis for persistence and consolidated deduplication utilities
    for idempotency and deduplication features.
    """
    
    def __init__(self, business_id: str, redis_url: str = None):
        self.business_id = business_id
        self.redis_url = redis_url or "redis://localhost:6379"
        
        try:
            import redis
            self.redis = redis.from_url(self.redis_url)
            self.redis.ping()  # Test connection
            self.logger = logging.getLogger(f"{__name__}.{business_id}")
            self.logger.info(f"Connected to Redis: {self.redis_url}")
        except ImportError:
            raise ImportError("Redis package not installed. Run: pip install redis")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _job_key(self, job_id: str) -> str:
        """Generate Redis key for job."""
        return f"oodaloo:job:{self.business_id}:{job_id}"
    
    def _idempotency_key(self, key: str) -> str:
        """Generate Redis key for idempotency mapping using deduplication utilities."""
        # Use consolidated deduplication for consistent key generation
        return f"oodaloo:idempotency:{self.business_id}:{sha256('job', key)}"
    
    def _jobs_by_status_key(self, status: str) -> str:
        """Generate Redis key for jobs by status."""
        return f"oodaloo:jobs:{self.business_id}:status:{status}"
    
    def save_job(self, job_data: Dict[str, Any]) -> bool:
        """Save job data to Redis with indexing."""
        try:
            job_id = job_data['id']
            status = job_data.get('status', 'pending')
            idempotency_key = job_data.get('idempotency_key')
            
            # Save job data
            job_key = self._job_key(job_id)
            self.redis.set(job_key, json.dumps(job_data))
            
            # Add to status index
            status_key = self._jobs_by_status_key(status)
            self.redis.sadd(status_key, job_id)
            
            # Save idempotency key mapping using deduplication utilities
            if idempotency_key:
                idempotency_redis_key = self._idempotency_key(idempotency_key)
                self.redis.set(idempotency_redis_key, job_id)
            
            self.logger.debug(f"Saved job {job_id} to Redis")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save job: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data by ID from Redis."""
        try:
            job_key = self._job_key(job_id)
            job_data = self.redis.get(job_key)
            
            if job_data:
                return json.loads(job_data)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    def get_jobs(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get jobs with filtering from Redis."""
        try:
            job_ids = set()
            
            # Apply status filter
            if filters and 'status' in filters:
                status = filters['status']
                status_key = self._jobs_by_status_key(status)
                job_ids = set(self.redis.smembers(status_key))
            else:
                # Get all jobs for this business (scan pattern)
                pattern = self._job_key("*")
                job_keys = self.redis.keys(pattern)
                job_ids = {key.split(":")[-1] for key in job_keys}
            
            # Convert to job objects
            jobs = []
            for job_id in job_ids:
                if isinstance(job_id, bytes):
                    job_id = job_id.decode('utf-8')
                job_data = self.get_job(job_id)
                if job_data:
                    jobs.append(job_data)
            
            # Sort by created_at (newest first) and limit
            jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return jobs[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get jobs: {e}")
            return []
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job from Redis and indexes."""
        try:
            # Get job data first to update indexes
            job_data = self.get_job(job_id)
            if not job_data:
                return False
            
            # Remove from Redis
            job_key = self._job_key(job_id)
            self.redis.delete(job_key)
            
            # Remove from status index
            status = job_data.get('status', 'pending')
            status_key = self._jobs_by_status_key(status)
            self.redis.srem(status_key, job_id)
            
            # Remove idempotency key mapping
            idempotency_key = job_data.get('idempotency_key')
            if idempotency_key:
                idempotency_redis_key = self._idempotency_key(idempotency_key)
                self.redis.delete(idempotency_redis_key)
            
            self.logger.debug(f"Deleted job {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    def get_job_by_idempotency_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Get job by idempotency key using deduplication utilities."""
        try:
            idempotency_redis_key = self._idempotency_key(key)
            job_id = self.redis.get(idempotency_redis_key)
            
            if job_id:
                if isinstance(job_id, bytes):
                    job_id = job_id.decode('utf-8')
                return self.get_job(job_id)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get job by idempotency key {key}: {e}")
            return None

def get_job_storage_provider(business_id: str, use_redis: bool = None) -> JobStorageProvider:
    """
    Factory function to get appropriate job storage provider.
    
    Uses consolidated infrastructure instead of custom storage logic.
    """
    if use_redis is None:
        import os
        use_redis = os.getenv("USE_REDIS_JOBS", "false").lower() == "true"
        environment = os.getenv("ENVIRONMENT", "development")
        use_redis = environment == "production" or use_redis
    
    if use_redis:
        try:
            return RedisBasedJobStorage(business_id)
        except Exception as e:
            logger.warning(f"Failed to initialize Redis job storage: {e}")
            logger.info("Falling back to cache-based job storage")
            return CacheBasedJobStorage(business_id)
    else:
        return CacheBasedJobStorage(business_id)
