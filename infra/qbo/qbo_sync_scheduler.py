"""
QBO Sync Scheduler - Background Sync Job Configuration

Configures and manages QBO sync jobs using the existing JobScheduler infrastructure.
Sets up 15-minute sync schedule for bills, invoices, vendors, and company info.

Key Features:
- Uses existing JobScheduler (not Celery)
- 15-minute sync schedule for MVP data architecture
- Integrates with new BaseSyncService + QBOSyncService architecture
- Transaction log integration for audit trails
- Error handling and retry logic
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infra.jobs.job_scheduler import JobScheduler, JobRunner
from infra.qbo.qbo_sync_jobs import register_qbo_sync_jobs
from infra.database.session import get_db
from domains.core.models.business import Business

logger = logging.getLogger(__name__)


class QBOSyncScheduler:
    """
    QBO sync job scheduler that manages background sync operations.
    
    This scheduler uses the existing JobScheduler infrastructure to run
    QBO sync jobs every 15 minutes for all connected businesses.
    """
    
    def __init__(self):
        self.job_scheduler = JobScheduler()
        self.job_runner = JobRunner()
        self.running = False
        
        # Register QBO sync job functions
        register_qbo_sync_jobs(self.job_runner)
        
        logger.info("QBO Sync Scheduler initialized")
    
    async def start_scheduler(self, poll_interval: int = 30):
        """
        Start the QBO sync scheduler.
        
        Args:
            poll_interval: How often to check for scheduled jobs (seconds)
        """
        self.running = True
        logger.info("QBO Sync Scheduler started")
        
        try:
            while self.running:
                await self._schedule_sync_jobs()
                await asyncio.sleep(poll_interval)
        except Exception as e:
            logger.error(f"QBO Sync Scheduler error: {e}", exc_info=True)
        finally:
            self.running = False
            logger.info("QBO Sync Scheduler stopped")
    
    def stop_scheduler(self):
        """Stop the QBO sync scheduler."""
        self.running = False
        logger.info("QBO Sync Scheduler stop requested")
    
    async def _schedule_sync_jobs(self):
        """Schedule QBO sync jobs for all connected businesses."""
        try:
            # Get database session
            db = next(get_db())
            
            # Get all businesses with QBO connections
            businesses = db.query(Business).filter(
                Business.qbo_realm_id.isnot(None)
            ).all()
            
            if not businesses:
                logger.debug("No businesses with QBO connections found")
                db.close()
                return
            
            current_time = datetime.utcnow()
            
            for business in businesses:
                try:
                    # Check if we need to schedule sync jobs for this business
                    await self._schedule_business_sync_jobs(business, current_time)
                    
                except Exception as e:
                    logger.error(f"Error scheduling sync jobs for business {business.business_id}: {e}")
                    continue
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error in _schedule_sync_jobs: {e}", exc_info=True)
    
    async def _schedule_business_sync_jobs(self, business: Business, current_time: datetime):
        """Schedule sync jobs for a specific business."""
        business_id = business.business_id
        realm_id = business.qbo_realm_id
        
        # Check if sync jobs are already scheduled for this business
        existing_jobs = self.job_runner.get_jobs(
            status=None,  # Get all statuses
            business_id=business_id,
            limit=10
        )
        
        # Filter for QBO sync jobs scheduled in the last 20 minutes
        recent_sync_jobs = [
            job for job in existing_jobs
            if job.name.startswith("QBO Sync") and 
            job.scheduled_at and 
            (current_time - job.scheduled_at).total_seconds() < 1200  # 20 minutes
        ]
        
        if recent_sync_jobs:
            logger.debug(f"Sync jobs already scheduled for business {business_id}")
            return
        
        # Schedule individual sync jobs
        sync_time = current_time + timedelta(minutes=1)  # Start in 1 minute
        
        # Schedule bills sync
        self.job_scheduler.schedule_job(
            name="QBO Sync Bills",
            function_name="sync_qbo_bills",
            scheduled_at=sync_time,
            args=(business_id, realm_id),
            max_retries=3,
            retry_delay=300,  # 5 minutes
            idempotency_key=f"qbo_sync_bills_{business_id}_{current_time.strftime('%Y%m%d_%H%M')}",
            created_by="system"
        )
        
        # Schedule invoices sync
        self.job_scheduler.schedule_job(
            name="QBO Sync Invoices",
            function_name="sync_qbo_invoices",
            scheduled_at=sync_time + timedelta(minutes=1),
            args=(business_id, realm_id),
            max_retries=3,
            retry_delay=300,
            idempotency_key=f"qbo_sync_invoices_{business_id}_{current_time.strftime('%Y%m%d_%H%M')}",
            created_by="system"
        )
        
        # Schedule vendors sync
        self.job_scheduler.schedule_job(
            name="QBO Sync Vendors",
            function_name="sync_qbo_vendors",
            scheduled_at=sync_time + timedelta(minutes=2),
            args=(business_id, realm_id),
            max_retries=3,
            retry_delay=300,
            idempotency_key=f"qbo_sync_vendors_{business_id}_{current_time.strftime('%Y%m%d_%H%M')}",
            created_by="system"
        )
        
        # Schedule company info sync
        self.job_scheduler.schedule_job(
            name="QBO Sync Company Info",
            function_name="sync_qbo_company_info",
            scheduled_at=sync_time + timedelta(minutes=3),
            args=(business_id, realm_id),
            max_retries=3,
            retry_delay=300,
            idempotency_key=f"qbo_sync_company_info_{business_id}_{current_time.strftime('%Y%m%d_%H%M')}",
            created_by="system"
        )
        
        logger.info(f"Scheduled QBO sync jobs for business {business_id}")
    
    async def run_worker(self, poll_interval: int = 30):
        """
        Run the job worker to process scheduled jobs.
        
        Args:
            poll_interval: How often to check for jobs to process (seconds)
        """
        logger.info("QBO Sync Job Worker started")
        await self.job_runner.run_worker(poll_interval)
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """Get sync job statistics."""
        stats = self.job_runner.get_job_stats()
        
        # Add QBO-specific stats
        qbo_jobs = self.job_runner.get_jobs(limit=100)
        qbo_sync_jobs = [job for job in qbo_jobs if job.name.startswith("QBO Sync")]
        
        stats["qbo_sync_jobs"] = len(qbo_sync_jobs)
        stats["qbo_sync_jobs_by_status"] = {}
        
        for job in qbo_sync_jobs:
            status = job.status.value
            if status not in stats["qbo_sync_jobs_by_status"]:
                stats["qbo_sync_jobs_by_status"][status] = 0
            stats["qbo_sync_jobs_by_status"][status] += 1
        
        return stats
    
    def get_business_sync_status(self, business_id: str) -> Dict[str, Any]:
        """Get sync status for a specific business."""
        jobs = self.job_runner.get_jobs(business_id=business_id, limit=50)
        qbo_jobs = [job for job in jobs if job.name.startswith("QBO Sync")]
        
        return {
            "business_id": business_id,
            "total_jobs": len(qbo_jobs),
            "jobs_by_status": {
                job.status.value: len([j for j in qbo_jobs if j.status == job.status])
                for job in qbo_jobs
            },
            "recent_jobs": [
                {
                    "name": job.name,
                    "status": job.status.value,
                    "scheduled_at": job.scheduled_at.isoformat() if job.scheduled_at else None,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "error": job.error
                }
                for job in sorted(qbo_jobs, key=lambda x: x.created_at, reverse=True)[:10]
            ]
        }


# ==================== GLOBAL INSTANCE ====================

_qbo_sync_scheduler: Optional[QBOSyncScheduler] = None

def get_qbo_sync_scheduler() -> QBOSyncScheduler:
    """Get global QBO sync scheduler instance."""
    global _qbo_sync_scheduler
    if _qbo_sync_scheduler is None:
        _qbo_sync_scheduler = QBOSyncScheduler()
    return _qbo_sync_scheduler


# ==================== STARTUP FUNCTIONS ====================

async def start_qbo_sync_scheduler():
    """Start the QBO sync scheduler (for application startup)."""
    scheduler = get_qbo_sync_scheduler()
    await scheduler.start_scheduler()


async def start_qbo_sync_worker():
    """Start the QBO sync worker (for application startup)."""
    scheduler = get_qbo_sync_scheduler()
    await scheduler.run_worker()


def stop_qbo_sync_scheduler():
    """Stop the QBO sync scheduler (for application shutdown)."""
    scheduler = get_qbo_sync_scheduler()
    scheduler.stop_scheduler()
