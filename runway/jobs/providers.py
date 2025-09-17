"""
Job Providers - Storage backends for background jobs

Supports both in-memory (development) and Redis (production) storage
with the same interface for easy switching.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Import Job and JobStatus with forward reference to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from runway.jobs.job_runner import Job, JobStatus

class JobProvider(ABC):
    """Abstract base class for job storage providers."""
    
    @abstractmethod
    def save_job(self, job: "Job") -> None:
        """Save a job to storage."""
        pass
    
    @abstractmethod
    def get_job(self, job_id: str) -> Optional["Job"]:
        """Get job by ID."""
        pass
    
    @abstractmethod
    def get_jobs(self, status: Optional["JobStatus"] = None, 
                business_id: Optional[str] = None,
                limit: int = 100) -> List["Job"]:
        """Get jobs with optional filtering."""
        pass
    
    @abstractmethod
    def get_job_by_idempotency_key(self, key: str) -> Optional["Job"]:
        """Get job by idempotency key."""
        pass
    
    @abstractmethod
    def delete_job(self, job_id: str) -> bool:
        """Delete a job from storage."""
        pass

class InMemoryJobProvider(JobProvider):
    """In-memory job storage for development."""
    
    def __init__(self):
        self.jobs: Dict[str, "Job"] = {}
        self.idempotency_keys: Dict[str, str] = {}  # key -> job_id
    
    def save_job(self, job: "Job") -> None:
        """Save job to memory."""
        self.jobs[job.id] = job
        if job.idempotency_key:
            self.idempotency_keys[job.idempotency_key] = job.id
        logger.debug(f"Saved job to memory: {job.id}")
    
    def get_job(self, job_id: str) -> Optional["Job"]:
        """Get job by ID from memory."""
        return self.jobs.get(job_id)
    
    def get_jobs(self, status: Optional["JobStatus"] = None,
                business_id: Optional[str] = None, 
                limit: int = 100) -> List["Job"]:
        """Get jobs from memory with filtering."""
        jobs = list(self.jobs.values())
        
        # Filter by status
        if status:
            jobs = [job for job in jobs if job.status == status]
        
        # Filter by business_id
        if business_id:
            jobs = [job for job in jobs if job.business_id == business_id]
        
        # Sort by created_at (newest first) and limit
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        return jobs[:limit]
    
    def get_job_by_idempotency_key(self, key: str) -> Optional["Job"]:
        """Get job by idempotency key from memory."""
        job_id = self.idempotency_keys.get(key)
        if job_id:
            return self.jobs.get(job_id)
        return None
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job from memory."""
        job = self.jobs.pop(job_id, None)
        if job and job.idempotency_key:
            self.idempotency_keys.pop(job.idempotency_key, None)
        return job is not None

class RedisJobProvider(JobProvider):
    """Redis-based job storage for production."""
    
    def __init__(self, redis_url: str = None):
        try:
            import redis
            self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis = redis.from_url(self.redis_url)
            self.redis.ping()  # Test connection
            logger.info(f"Connected to Redis: {self.redis_url}")
        except ImportError:
            raise ImportError("Redis package not installed. Run: pip install redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _job_key(self, job_id: str) -> str:
        """Generate Redis key for job."""
        return f"oodaloo:job:{job_id}"
    
    def _idempotency_key(self, key: str) -> str:
        """Generate Redis key for idempotency mapping."""
        return f"oodaloo:idempotency:{key}"
    
    def _jobs_by_status_key(self, status: "JobStatus") -> str:
        """Generate Redis key for jobs by status."""
        return f"oodaloo:jobs:status:{status.value}"
    
    def _jobs_by_business_key(self, business_id: str) -> str:
        """Generate Redis key for jobs by business."""
        return f"oodaloo:jobs:business:{business_id}"
    
    def save_job(self, job: "Job") -> None:
        """Save job to Redis."""
        from runway.jobs.job_runner import Job  # Import here to avoid circular import
        
        # Save job data
        job_key = self._job_key(job.id)
        job_data = json.dumps(job.to_dict())
        self.redis.set(job_key, job_data)
        
        # Add to status index
        status_key = self._jobs_by_status_key(job.status)
        self.redis.sadd(status_key, job.id)
        
        # Add to business index if business_id exists
        if job.business_id:
            business_key = self._jobs_by_business_key(job.business_id)
            self.redis.sadd(business_key, job.id)
        
        # Save idempotency key mapping
        if job.idempotency_key:
            idempotency_key = self._idempotency_key(job.idempotency_key)
            self.redis.set(idempotency_key, job.id)
        
        logger.debug(f"Saved job to Redis: {job.id}")
    
    def get_job(self, job_id: str) -> Optional["Job"]:
        """Get job by ID from Redis."""
        from runway.jobs.job_runner import Job  # Import here to avoid circular import
        
        job_key = self._job_key(job_id)
        job_data = self.redis.get(job_key)
        
        if job_data:
            job_dict = json.loads(job_data)
            return Job.from_dict(job_dict)
        
        return None
    
    def get_jobs(self, status: Optional["JobStatus"] = None,
                business_id: Optional[str] = None,
                limit: int = 100) -> List["Job"]:
        """Get jobs from Redis with filtering."""
        job_ids = set()
        
        if status:
            status_key = self._jobs_by_status_key(status)
            job_ids = set(self.redis.smembers(status_key))
        
        if business_id:
            business_key = self._jobs_by_business_key(business_id)
            business_job_ids = set(self.redis.smembers(business_key))
            
            if job_ids:
                job_ids = job_ids.intersection(business_job_ids)
            else:
                job_ids = business_job_ids
        
        # If no filters, get all jobs (this is expensive, should be avoided)
        if not job_ids and not status and not business_id:
            pattern = self._job_key("*")
            job_keys = self.redis.keys(pattern)
            job_ids = {key.split(":")[-1] for key in job_keys}
        
        # Convert to Job objects
        jobs = []
        for job_id in job_ids:
            if isinstance(job_id, bytes):
                job_id = job_id.decode('utf-8')
            job = self.get_job(job_id)
            if job:
                jobs.append(job)
        
        # Sort by created_at (newest first) and limit
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        return jobs[:limit]
    
    def get_job_by_idempotency_key(self, key: str) -> Optional["Job"]:
        """Get job by idempotency key from Redis."""
        idempotency_key = self._idempotency_key(key)
        job_id = self.redis.get(idempotency_key)
        
        if job_id:
            if isinstance(job_id, bytes):
                job_id = job_id.decode('utf-8')
            return self.get_job(job_id)
        
        return None
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job from Redis."""
        job = self.get_job(job_id)
        if not job:
            return False
        
        # Remove from all indexes
        job_key = self._job_key(job_id)
        self.redis.delete(job_key)
        
        status_key = self._jobs_by_status_key(job.status)
        self.redis.srem(status_key, job_id)
        
        if job.business_id:
            business_key = self._jobs_by_business_key(job.business_id)
            self.redis.srem(business_key, job_id)
        
        if job.idempotency_key:
            idempotency_key = self._idempotency_key(job.idempotency_key)
            self.redis.delete(idempotency_key)
        
        return True

def get_job_provider() -> JobProvider:
    """Factory function to get appropriate job provider."""
    use_redis = os.getenv("USE_REDIS_JOBS", "false").lower() == "true"
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production" or use_redis:
        try:
            return RedisJobProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize Redis job provider: {e}")
            logger.info("Falling back to in-memory job provider")
            return InMemoryJobProvider()
    else:
        return InMemoryJobProvider()
