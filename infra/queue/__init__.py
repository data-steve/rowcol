"""
Queue Infrastructure

This package provides queue management, deduplication, and idempotency
functionality for background processing and data synchronization.

Components:
- identity_graph: Sophisticated queue management for deduplication and idempotency
- job_queue: Generic job queue management
- deduplication: Queue deduplication utilities
- idempotency: Idempotency key management
"""

from .deduplication import (
    RawEvent,
    fingerprint,
    upsert_identity,
    link_raw,
    add_edge,
    write_ledger,
    sha256
)
from .job_storage import (
    JobStorageProvider,
    CacheBasedJobStorage,
    RedisBasedJobStorage,
    get_job_storage_provider
)

__all__ = [
    "RawEvent",
    "fingerprint", 
    "upsert_identity",
    "link_raw",
    "add_edge",
    "write_ledger",
    "sha256",
    "JobStorageProvider",
    "CacheBasedJobStorage", 
    "RedisBasedJobStorage",
    "get_job_storage_provider"
]
