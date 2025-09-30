"""
Job Providers - Storage backends for background jobs

Now uses unified infra/queue infrastructure for consistent storage
across all job providers instead of custom storage logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import os
import logging
from typing import TYPE_CHECKING
from infra.jobs import get_job_storage_provider

logger = logging.getLogger(__name__)

# Import Job and JobStatus with forward reference to avoid circular imports
if TYPE_CHECKING:
    from infra.scheduler.job_runner import Job, JobStatus

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
    """In-memory job storage using unified infra/queue infrastructure."""
    
    def __init__(self, business_id: str = "default"):
        self.business_id = business_id
        # Use unified storage infrastructure
        self.storage = get_job_storage_provider(business_id, use_redis=False)
    
    def save_job(self, job: "Job") -> None:
        """Save job using unified storage."""
        job_data = job.to_dict()
        success = self.storage.save_job(job_data)
        if success:
            logger.debug(f"Saved job to unified storage: {job.id}")
        else:
            logger.error(f"Failed to save job: {job.id}")
    
    def get_job(self, job_id: str) -> Optional["Job"]:
        """Get job by ID from unified storage."""
        from infra.scheduler.job_runner import Job  # Import here to avoid circular import
        
        job_data = self.storage.get_job(job_id)
        if job_data:
            return Job.from_dict(job_data)
        return None
    
    def get_jobs(self, status: Optional["JobStatus"] = None,
                business_id: Optional[str] = None, 
                limit: int = 100) -> List["Job"]:
        """Get jobs from unified storage with filtering."""
        from infra.scheduler.job_runner import Job  # Import here to avoid circular import
        
        filters = {}
        if status:
            filters['status'] = status.value
        if business_id:
            filters['business_id'] = business_id
        
        job_data_list = self.storage.get_jobs(filters, limit)
        return [Job.from_dict(job_data) for job_data in job_data_list]
    
    def get_job_by_idempotency_key(self, key: str) -> Optional["Job"]:
        """Get job by idempotency key from unified storage."""
        from infra.scheduler.job_runner import Job  # Import here to avoid circular import
        
        job_data = self.storage.get_job_by_idempotency_key(key)
        if job_data:
            return Job.from_dict(job_data)
        return None
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job from unified storage."""
        return self.storage.delete_job(job_id)

class RedisJobProvider(JobProvider):
    """Redis-based job storage using unified infra/queue infrastructure."""
    
    def __init__(self, business_id: str = "default", redis_url: str = None):
        self.business_id = business_id
        # Use unified storage infrastructure with Redis
        self.storage = get_job_storage_provider(business_id, use_redis=True)
    
    def save_job(self, job: "Job") -> None:
        """Save job using unified storage."""
        job_data = job.to_dict()
        success = self.storage.save_job(job_data)
        if success:
            logger.debug(f"Saved job to unified Redis storage: {job.id}")
        else:
            logger.error(f"Failed to save job: {job.id}")
    
    def get_job(self, job_id: str) -> Optional["Job"]:
        """Get job by ID from unified storage."""
        from infra.scheduler.job_runner import Job  # Import here to avoid circular import
        
        job_data = self.storage.get_job(job_id)
        if job_data:
            return Job.from_dict(job_data)
        return None
    
    def get_jobs(self, status: Optional["JobStatus"] = None,
                business_id: Optional[str] = None,
                limit: int = 100) -> List["Job"]:
        """Get jobs from unified storage with filtering."""
        from infra.scheduler.job_runner import Job  # Import here to avoid circular import
        
        filters = {}
        if status:
            filters['status'] = status.value
        if business_id:
            filters['business_id'] = business_id
        
        job_data_list = self.storage.get_jobs(filters, limit)
        return [Job.from_dict(job_data) for job_data in job_data_list]
    
    def get_job_by_idempotency_key(self, key: str) -> Optional["Job"]:
        """Get job by idempotency key from unified storage."""
        from infra.scheduler.job_runner import Job  # Import here to avoid circular import
        
        job_data = self.storage.get_job_by_idempotency_key(key)
        if job_data:
            return Job.from_dict(job_data)
        return None
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job from unified storage."""
        return self.storage.delete_job(job_id)

def get_job_provider(business_id: str = "default") -> JobProvider:
    """Factory function to get appropriate job provider using unified infrastructure."""
    use_redis = os.getenv("USE_REDIS_JOBS", "false").lower() == "true"
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production" or use_redis:
        try:
            return RedisJobProvider(business_id)
        except Exception as e:
            logger.warning(f"Failed to initialize Redis job provider: {e}")
            logger.info("Falling back to in-memory job provider")
            return InMemoryJobProvider(business_id)
    else:
        return InMemoryJobProvider(business_id)
