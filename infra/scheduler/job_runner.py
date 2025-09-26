"""
Background Job Runner - Simple, Reliable Task Processing

Handles scheduled and background tasks with retry logic, idempotency,
and proper error handling. Uses provider pattern for scalability.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
import uuid
import json
import traceback

from infra.jobs import JobProvider, get_job_provider

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

@dataclass
class Job:
    """Background job definition."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    function_name: str = ""
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    status: JobStatus = JobStatus.PENDING
    
    # Scheduling
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Retry configuration
    max_retries: int = 3
    retry_count: int = 0
    retry_delay: int = 60  # seconds
    
    # Idempotency
    idempotency_key: Optional[str] = None
    
    # Results and errors
    result: Optional[Any] = None
    error: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    business_id: Optional[str] = None
    created_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "function_name": self.function_name,
            "args": self.args,
            "kwargs": self.kwargs,
            "status": self.status.value,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "idempotency_key": self.idempotency_key,
            "result": json.dumps(self.result) if self.result else None,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "business_id": self.business_id,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        """Create job from dictionary."""
        job = cls(
            id=data["id"],
            name=data["name"],
            function_name=data["function_name"],
            args=tuple(data["args"]),
            kwargs=data["kwargs"],
            status=JobStatus(data["status"]),
            max_retries=data["max_retries"],
            retry_count=data["retry_count"],
            retry_delay=data["retry_delay"],
            idempotency_key=data.get("idempotency_key"),
            error=data.get("error"),
            business_id=data.get("business_id"),
            created_by=data.get("created_by")
        )
        
        # Parse datetime fields
        if data.get("scheduled_at"):
            job.scheduled_at = datetime.fromisoformat(data["scheduled_at"])
        if data.get("started_at"):
            job.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            job.completed_at = datetime.fromisoformat(data["completed_at"])
        if data.get("created_at"):
            job.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            job.updated_at = datetime.fromisoformat(data["updated_at"])
        
        # Parse result
        if data.get("result"):
            try:
                job.result = json.loads(data["result"])
            except json.JSONDecodeError:
                job.result = data["result"]
        
        return job

class JobRunner:
    """Background job runner with retry logic and idempotency."""
    
    def __init__(self, provider: Optional[JobProvider] = None):
        self.provider = provider or get_job_provider()
        self.functions: Dict[str, Callable] = {}
        self.running = False
        
    def register_function(self, name: str, func: Callable):
        """Register a function that can be called by jobs."""
        self.functions[name] = func
        logger.info(f"Registered job function: {name}")
    
    def schedule_job(self, name: str, function_name: str, 
                    scheduled_at: Optional[datetime] = None,
                    args: tuple = (), kwargs: Dict[str, Any] = None,
                    max_retries: int = 3, retry_delay: int = 60,
                    idempotency_key: Optional[str] = None,
                    business_id: Optional[str] = None,
                    created_by: Optional[str] = None) -> Job:
        """Schedule a background job."""
        
        # Check for existing job with same idempotency key
        if idempotency_key:
            existing_job = self.provider.get_job_by_idempotency_key(idempotency_key)
            if existing_job and existing_job.status not in [JobStatus.FAILED, JobStatus.CANCELLED]:
                logger.info(f"Job with idempotency key {idempotency_key} already exists")
                return existing_job
        
        job = Job(
            name=name,
            function_name=function_name,
            args=args,
            kwargs=kwargs or {},
            scheduled_at=scheduled_at or datetime.utcnow(),
            max_retries=max_retries,
            retry_delay=retry_delay,
            idempotency_key=idempotency_key,
            business_id=business_id,
            created_by=created_by
        )
        
        self.provider.save_job(job)
        logger.info(f"Scheduled job: {job.name} ({job.id})")
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return self.provider.get_job(job_id)
    
    def get_jobs(self, status: Optional[JobStatus] = None, 
                business_id: Optional[str] = None,
                limit: int = 100) -> List[Job]:
        """Get jobs with optional filtering."""
        return self.provider.get_jobs(status=status, business_id=business_id, limit=limit)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        job = self.provider.get_job(job_id)
        if not job or job.status != JobStatus.PENDING:
            return False
        
        job.status = JobStatus.CANCELLED
        job.updated_at = datetime.utcnow()
        self.provider.save_job(job)
        logger.info(f"Cancelled job: {job.name} ({job.id})")
        return True
    
    async def run_worker(self, poll_interval: int = 30):
        """Run background worker to process jobs."""
        self.running = True
        logger.info("Background job worker started")
        
        try:
            while self.running:
                await self._process_pending_jobs()
                await asyncio.sleep(poll_interval)
        except Exception as e:
            logger.error(f"Job worker error: {e}", exc_info=True)
        finally:
            self.running = False
            logger.info("Background job worker stopped")
    
    def stop_worker(self):
        """Stop the background worker."""
        self.running = False
    
    async def _process_pending_jobs(self):
        """Process all pending jobs that are due."""
        now = datetime.utcnow()
        pending_jobs = self.provider.get_jobs(status=JobStatus.PENDING)
        
        for job in pending_jobs:
            if job.scheduled_at and job.scheduled_at <= now:
                await self._execute_job(job)
    
    async def _execute_job(self, job: Job):
        """Execute a single job with error handling and retries."""
        if job.function_name not in self.functions:
            error_msg = f"Function '{job.function_name}' not registered"
            logger.error(error_msg)
            job.status = JobStatus.FAILED
            job.error = error_msg
            job.updated_at = datetime.utcnow()
            self.provider.save_job(job)
            return
        
        # Update job status to running
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        self.provider.save_job(job)
        
        try:
            # Execute the function
            func = self.functions[job.function_name]
            logger.info(f"Executing job: {job.name} ({job.id})")
            
            if asyncio.iscoroutinefunction(func):
                result = await func(*job.args, **job.kwargs)
            else:
                result = func(*job.args, **job.kwargs)
            
            # Job completed successfully
            job.status = JobStatus.COMPLETED
            job.result = result
            job.completed_at = datetime.utcnow()
            job.updated_at = datetime.utcnow()
            self.provider.save_job(job)
            
            logger.info(f"Job completed: {job.name} ({job.id})")
            
        except Exception as e:
            error_msg = f"Job execution failed: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            job.error = error_msg
            job.retry_count += 1
            job.updated_at = datetime.utcnow()
            
            # Determine if we should retry
            if job.retry_count < job.max_retries:
                job.status = JobStatus.RETRYING
                job.scheduled_at = datetime.utcnow() + timedelta(seconds=job.retry_delay)
                logger.info(f"Job will retry in {job.retry_delay}s: {job.name} ({job.id})")
            else:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.utcnow()
                logger.error(f"Job failed after {job.retry_count} retries: {job.name} ({job.id})")
            
            self.provider.save_job(job)
    
    def get_job_stats(self) -> Dict[str, int]:
        """Get job statistics."""
        stats = {}
        for status in JobStatus:
            jobs = self.provider.get_jobs(status=status)
            stats[status.value] = len(jobs)
        return stats

# Global job runner instance
_job_runner: Optional[JobRunner] = None

def get_job_runner() -> JobRunner:
    """Get global job runner instance."""
    global _job_runner
    if _job_runner is None:
        _job_runner = JobRunner()
    return _job_runner
