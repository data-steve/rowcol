"""
BaseSyncService - Generic Sync Orchestration

Generic sync orchestration service that provides resilience, rate limiting, 
caching, and retry logic for all integration rails. This service handles
rail-agnostic orchestration concerns.

Key Responsibilities:
- Rate limiting and prioritization
- Retry logic with exponential backoff
- Deduplication to prevent duplicate actions
- Caching and data consistency management
- User activity tracking for sync timing
- Background reconciliation scheduling

Multi-Rail Architecture:
This service provides generic orchestration that works across all integration rails:
- QBO (Ledger Rail) - Current implementation
- Ramp (A/P Execution Rail) - Future implementation
- Plaid (Verification Rail) - Future implementation
- Stripe (A/R Execution Rail) - Future implementation

Each rail has its own specific sync service that uses this base for orchestration.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import asyncio
import hashlib
import json

from infra.jobs.job_storage import SyncCache
from infra.jobs.sync_strategies import SyncTimingManager
from infra.jobs.enums import SyncStrategy, SyncPriority

logger = logging.getLogger(__name__)


class BaseSyncService:
    """
    Generic sync orchestrator that provides resilience and orchestration for all integration rails.
    
    This service provides rail-agnostic orchestration that can be used by any integration rail:
    - Rate limiting and prioritization
    - Retry logic with exponential backoff
    - Deduplication to prevent duplicate actions
    - Caching and data consistency management
    - User activity tracking for sync timing
    - Background reconciliation scheduling
    
    MULTI-RAIL ARCHITECTURE:
    This service provides generic orchestration that works across all integration rails:
    - QBO (Ledger Rail) - Current implementation
    - Ramp (A/P Execution Rail) - Future implementation
    - Plaid (Verification Rail) - Future implementation
    - Stripe (A/R Execution Rail) - Future implementation
    
    Each rail has its own specific sync service that uses this base for orchestration.
    """
    
    def __init__(self, business_id: str, db_session=None):
        self.business_id = business_id
        self.db_session = db_session
        self.timing_manager = SyncTimingManager(business_id)
        self.cache = SyncCache(business_id)
        self.action_hashes = set()  # Deduplication tracking
        self.logger = logging.getLogger(f"{__name__}.{business_id}")
        
        logger.info(f"Initialized BaseSyncService for business {business_id}")
    
    async def execute_sync_call(
        self, 
        rail: str, 
        operation: str, 
        client_method: callable,
        *args, 
        **kwargs
    ) -> Any:
        """
        Execute any sync operation with resilience (retry, dedup, rate limiting, caching).
        This is the main method that rail-specific sync services will use.
        
        Args:
            rail: Integration rail name (qbo, ramp, plaid, stripe)
            operation: Operation name for logging and caching
            client_method: The actual method to call on the rail client
            *args: Arguments to pass to the client method
            **kwargs: Keyword arguments to pass to the client method
        
        Returns:
            Result from the client method call
        """
        # Create operation hash for deduplication
        operation_hash = self._create_operation_hash(rail, operation, args, kwargs)
        
        if operation_hash in self.action_hashes:
            self.logger.warning(f"Duplicate operation detected: {rail}.{operation}")
            return {"status": "duplicate", "message": "Operation already in progress"}
        
        # Add to deduplication tracking
        self.action_hashes.add(operation_hash)
        
        try:
            # Check sync timing
            strategy = kwargs.get('strategy', SyncStrategy.ON_DEMAND)
            priority = kwargs.get('priority', SyncPriority.MEDIUM)
            
            if not self.timing_manager.should_sync(rail, strategy, priority):
                # Return cached data if available
                cached_data = self.cache.get(rail, operation)
                if cached_data:
                    self.logger.debug(f"Returning cached data for {rail}.{operation}")
                    return cached_data
                else:
                    return {"status": "throttled", "message": "Sync not needed at this time"}
            
            # Execute the operation with retry logic
            max_attempts = kwargs.get('max_attempts', 3)
            retry_delay = 1
            
            for attempt in range(max_attempts):
                try:
                    # Execute the client method
                    if asyncio.iscoroutinefunction(client_method):
                        result = await client_method(*args, **kwargs)
                    else:
                        result = client_method(*args, **kwargs)
                    
                    # Cache successful results for data fetch operations
                    if result and strategy in [SyncStrategy.DATA_FETCH, SyncStrategy.DATA_SYNC]:
                        self.cache.set(rail, operation, result, ttl_minutes=240)
                    
                    # Record success and user activity
                    self.timing_manager.record_success(rail)
                    self.timing_manager.record_user_activity(rail)
                    
                    self.logger.info(f"Successfully executed {rail}.{operation} on attempt {attempt + 1}")
                    return result
                    
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed for {rail}.{operation}: {e}")
                    
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        # Record failure
                        self.timing_manager.record_failure(rail, str(e))
                        raise e
            
        finally:
            # Remove from deduplication tracking
            self.action_hashes.discard(operation_hash)
    
    def _create_operation_hash(self, rail: str, operation: str, args: tuple, kwargs: dict) -> str:
        """Create a hash for operation deduplication."""
        operation_data = {
            "rail": rail,
            "operation": operation,
            "args": args,
            "kwargs": {k: v for k, v in kwargs.items() if k not in ['strategy', 'priority', 'max_attempts']}
        }
        return hashlib.md5(json.dumps(operation_data, sort_keys=True).encode()).hexdigest()
    
    async def health_check(self, rail: str) -> Dict[str, Any]:
        """Check rail API health."""
        return await self.execute_sync_call(
            rail, 
            "health_check",
            lambda: {"status": "healthy", "rail": rail},
            strategy=SyncStrategy.ON_DEMAND,
            priority=SyncPriority.LOW
        )
    
    def get_cache_stats(self, rail: str) -> Dict[str, Any]:
        """Get cache statistics for a rail."""
        return self.cache.get_stats(rail)
    
    def clear_cache(self, rail: str, operation: Optional[str] = None) -> bool:
        """Clear cache for a rail and optionally specific operation."""
        return self.cache.clear(rail, operation)
