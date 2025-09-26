"""
Job Storage Service - Unified Job Persistence

Provides job storage using existing infra/cache and infra/queue infrastructure.
Replaces the custom storage logic in job providers with centralized, consistent storage.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging
from infra.cache.sync_cache import SyncCache
from infra.queue.deduplication import sha256

logger = logging.getLogger(__name__)

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
    Job storage using infra/cache/sync_cache for persistence.
    
    Uses the existing SyncCache infrastructure for job storage with
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
    Job storage using Redis with infra/queue deduplication utilities.
    
    Uses Redis for persistence and infra/queue utilities for idempotency
    and deduplication features.
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
        """Generate Redis key for idempotency mapping using infra/queue utilities."""
        # Use infra/queue deduplication for consistent key generation
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
            
            # Save idempotency key mapping using infra/queue utilities
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
        """Get job by idempotency key using infra/queue utilities."""
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
    
    Uses existing infra infrastructure instead of custom storage logic.
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


