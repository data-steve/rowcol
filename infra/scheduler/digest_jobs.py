"""
Digest Job Scheduler - Weekly Email Generation

Handles scheduling and execution of digest email jobs with proper
error handling, retry logic, and business-specific timing.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from infra.scheduler.job_runner import JobRunner, Job, get_job_runner
from runway.experiences.digest import DigestService
from infra.database.session import SessionLocal

logger = logging.getLogger(__name__)

class DigestJobScheduler:
    """Scheduler for digest email jobs."""
    
    def __init__(self, job_runner: Optional[JobRunner] = None):
        self.job_runner = job_runner or get_job_runner()
        self._register_functions()
    
    def _register_functions(self):
        """Register digest job functions with the job runner."""
        self.job_runner.register_function("generate_business_digest", self._generate_business_digest)
        self.job_runner.register_function("send_all_digests", self._send_all_digests)
        self.job_runner.register_function("cleanup_old_digest_jobs", self._cleanup_old_jobs)
    
    def schedule_weekly_digests(self, send_day: str = "monday", send_hour: int = 9) -> List[Job]:
        """Schedule weekly digest emails for all businesses."""
        # Calculate next send time
        next_send_time = self._calculate_next_send_time(send_day, send_hour)
        
        # Schedule the batch job
        job = self.job_runner.schedule_job(
            name="Weekly Digest Batch",
            function_name="send_all_digests",
            scheduled_at=next_send_time,
            max_retries=2,
            retry_delay=3600,  # 1 hour retry delay
            idempotency_key=f"weekly_digest_{next_send_time.strftime('%Y_%W')}"  # Week-based idempotency
        )
        
        # Also schedule cleanup job
        cleanup_job = self.job_runner.schedule_job(
            name="Digest Job Cleanup",
            function_name="cleanup_old_digest_jobs",
            scheduled_at=next_send_time + timedelta(days=1),  # Day after digest
            max_retries=1,
            idempotency_key=f"digest_cleanup_{next_send_time.strftime('%Y_%W')}"
        )
        
        logger.info(f"Scheduled weekly digests for {next_send_time.strftime('%A, %B %d at %I:%M %p')}")
        return [job, cleanup_job]
    
    def schedule_business_digest(self, business_id: str, 
                               scheduled_at: Optional[datetime] = None) -> Job:
        """Schedule digest for a specific business."""
        send_time = scheduled_at or datetime.utcnow()
        
        job = self.job_runner.schedule_job(
            name=f"Digest for Business {business_id}",
            function_name="generate_business_digest",
            args=(business_id,),
            scheduled_at=send_time,
            max_retries=3,
            retry_delay=1800,  # 30 minute retry delay
            business_id=business_id,
            idempotency_key=f"business_digest_{business_id}_{send_time.strftime('%Y_%m_%d')}"
        )
        
        logger.info(f"Scheduled digest for business {business_id} at {send_time}")
        return job
    
    def _calculate_next_send_time(self, send_day: str, send_hour: int) -> datetime:
        """Calculate the next scheduled send time."""
        days_of_week = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        target_weekday = days_of_week.get(send_day.lower(), 0)  # Default to Monday
        now = datetime.utcnow()
        
        # Find next occurrence of target weekday
        days_ahead = target_weekday - now.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        next_send = now + timedelta(days=days_ahead)
        next_send = next_send.replace(hour=send_hour, minute=0, second=0, microsecond=0)
        
        return next_send
    
    async def _generate_business_digest(self, business_id: str) -> Dict[str, Any]:
        """Generate and send digest for a specific business."""
        db = SessionLocal()
        try:
            digest_service = DigestService(db)
            
            # Generate digest
            logger.info(f"Generating digest for business {business_id}")
            result = digest_service.generate_digest(business_id)
            
            if result.get("status") == "success":
                logger.info(f"Digest sent successfully for business {business_id}")
                return {
                    "status": "success",
                    "business_id": business_id,
                    "email_sent": True,
                    "runway_months": result.get("runway_months"),
                    "sent_at": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Digest generation failed for business {business_id}: {result}")
                raise Exception(f"Digest generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error generating digest for business {business_id}: {e}", exc_info=True)
            raise
        finally:
            db.close()
    
    async def _send_all_digests(self) -> Dict[str, Any]:
        """Send digest emails to all active businesses."""
        db = SessionLocal()
        try:
            # Get all active businesses (mock for now)
            # TODO: Replace with real business query
            active_businesses = ["business_1", "business_2", "business_3"]
            
            results = {
                "total_businesses": len(active_businesses),
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            for business_id in active_businesses:
                try:
                    await self._generate_business_digest(business_id)
                    results["successful"] += 1
                    logger.info(f"Digest sent for business {business_id}")
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "business_id": business_id,
                        "error": str(e)
                    })
                    logger.error(f"Failed to send digest for business {business_id}: {e}")
            
            logger.info(f"Batch digest complete: {results['successful']} sent, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch digest sending: {e}", exc_info=True)
            raise
        finally:
            db.close()
    
    async def _cleanup_old_jobs(self) -> Dict[str, Any]:
        """Clean up old digest jobs to prevent storage bloat."""
        cutoff_date = datetime.utcnow() - timedelta(days=30)  # Keep 30 days of job history
        
        # Get old completed jobs
        from infra.scheduler.job_runner import JobStatus
        all_jobs = self.job_runner.get_jobs(limit=1000)  # Get more jobs for cleanup
        
        deleted_count = 0
        for job in all_jobs:
            if (job.status in [JobStatus.COMPLETED, JobStatus.FAILED] and 
                job.completed_at and job.completed_at < cutoff_date and
                "digest" in job.name.lower()):
                
                self.job_runner.provider.delete_job(job.id)
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old digest jobs")
        return {"deleted_jobs": deleted_count, "cutoff_date": cutoff_date.isoformat()}
    
    def get_digest_job_stats(self) -> Dict[str, Any]:
        """Get statistics about digest jobs."""
        from infra.scheduler.job_runner import JobStatus
        
        all_jobs = self.job_runner.get_jobs(limit=1000)
        digest_jobs = [job for job in all_jobs if "digest" in job.name.lower()]
        
        stats = {
            "total_digest_jobs": len(digest_jobs),
            "by_status": {},
            "recent_jobs": []
        }
        
        # Count by status
        for status in JobStatus:
            count = sum(1 for job in digest_jobs if job.status == status)
            stats["by_status"][status.value] = count
        
        # Recent jobs (last 10)
        recent_jobs = sorted(digest_jobs, key=lambda x: x.created_at, reverse=True)[:10]
        stats["recent_jobs"] = [
            {
                "id": job.id,
                "name": job.name,
                "status": job.status.value,
                "created_at": job.created_at.isoformat(),
                "business_id": job.business_id
            }
            for job in recent_jobs
        ]
        
        return stats

# Global digest scheduler instance
_digest_scheduler: Optional[DigestJobScheduler] = None

def get_digest_scheduler() -> DigestJobScheduler:
    """Get global digest scheduler instance."""
    global _digest_scheduler
    if _digest_scheduler is None:
        _digest_scheduler = DigestJobScheduler()
    return _digest_scheduler
