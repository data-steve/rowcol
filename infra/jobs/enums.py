"""
Job and Sync Enums - Common enumerations for job management

Consolidates job and sync related enums to eliminate duplication and ensure consistency.
"""

from enum import Enum

class SyncStrategy(Enum):
    """Different sync strategies based on user needs."""
    ON_DEMAND = "on_demand"           # User explicitly requests sync
    SCHEDULED = "scheduled"           # Background scheduled sync
    EVENT_TRIGGERED = "event_triggered"  # Sync triggered by user action
    BACKGROUND = "background"         # Low-priority background sync

class SyncPriority(Enum):
    """Sync priority levels."""
    HIGH = "high"       # User is actively waiting
    MEDIUM = "medium"   # Important but not urgent
    LOW = "low"         # Background maintenance

class BulkSyncStrategy(Enum):
    """Bulk sync strategies for different scenarios."""
    FULL_SYNC = "full_sync"           # Complete data refresh
    INCREMENTAL = "incremental"        # Only new/changed data
    SELECTIVE = "selective"            # Specific data types only
    SCHEDULED = "scheduled"            # Background scheduled sync

class JobStatus(Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobPriority(Enum):
    """Job priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
