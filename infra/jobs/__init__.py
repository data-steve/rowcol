"""
Job Management Infrastructure - Consolidated

This package provides unified job management, sync coordination, and storage
for the Oodaloo application. Consolidates previously scattered functionality
from cache/, queue/, scheduler/, and utils/sync_strategies.

Key Components:
- SmartSyncService: Main orchestrator for sync operations
- JobScheduler: Job scheduling, providers, and execution
- JobStorage: Unified storage (cache + queue + deduplication)
- SyncStrategies: Sync timing and strategy management
"""

from .smart_sync import SmartSyncService
from .job_scheduler import JobScheduler, JobRunner, JobStatus, Job, JobProvider, get_job_provider
from .job_storage import JobStorageProvider, CacheBasedJobStorage, RedisBasedJobStorage, get_job_storage_provider
from .sync_strategies import SyncStrategy, SyncPriority, SyncTimingManager

__all__ = [
    # Main orchestrator
    "SmartSyncService",
    
    # Job management
    "JobScheduler", "JobRunner", "JobStatus", "Job",
    "JobProvider", "get_job_provider",
    
    # Storage
    "JobStorageProvider", "CacheBasedJobStorage", "RedisBasedJobStorage", "get_job_storage_provider",
    
    # Sync utilities
    "SyncStrategy", "SyncPriority", "SyncTimingManager"
]
