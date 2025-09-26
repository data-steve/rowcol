"""
Runway Background Jobs - Scheduled Task Management

This package handles background job processing for the Runway product,
including digest generation, data sync, and maintenance tasks.

Uses a simple in-memory job queue for development with Redis backend
ready for production scaling.
"""

from .job_runner import JobRunner, JobStatus, Job
from .job_providers import InMemoryJobProvider, RedisJobProvider, get_job_provider
from infra.jobs import SyncStrategy, SyncPriority, SyncTimingManager

__all__ = [
    "JobRunner", "JobStatus", "Job",
    "InMemoryJobProvider", "RedisJobProvider", "get_job_provider",
    "SyncStrategy", "SyncPriority", "SyncTimingManager"
]
