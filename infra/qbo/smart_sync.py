"""
SmartSyncService - QBO-Specific Sync Orchestrator

QBO-specific orchestration service that provides resilience, rate limiting, 
caching, and retry logic for all QBO operations. This service is the central
coordination point for all QBO interactions.

Key Responsibilities:
- Rate limiting and prioritization
- Retry logic with exponential backoff
- Deduplication to prevent duplicate actions
- Caching and data consistency management
- User activity tracking for sync timing
- Background reconciliation scheduling
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


class SmartSyncService:
    """
    QBO-specific sync orchestrator that provides resilience and orchestration for all QBO operations.
    
    This service wraps the QBORawClient with:
    - Rate limiting and prioritization
    - Retry logic with exponential backoff
    - Deduplication to prevent duplicate actions
    - Caching and data consistency management
    - User activity tracking for sync timing
    - Background reconciliation scheduling
    """
    
    def __init__(self, business_id: str, realm_id: str, db_session=None):
        self.business_id = business_id
        self.realm_id = realm_id
        self.db_session = db_session
        self.timing_manager = SyncTimingManager(business_id)
        self.cache = SyncCache(business_id)
        self.qbo_client = None  # Lazy initialization to avoid circular imports
        self.action_hashes = set()  # Deduplication tracking
        self.logger = logging.getLogger(f"{__name__}.{business_id}")
        
        logger.info(f"Initialized SmartSyncService for business {business_id}, realm {realm_id}")
    
    def _get_qbo_client(self):
        """Lazy initialization of QBORawClient to avoid circular imports."""
        if self.qbo_client is None:
            from .client import QBORawClient
            self.qbo_client = QBORawClient(self.business_id, self.realm_id, self.db_session)
        return self.qbo_client
    
    async def execute_qbo_call(self, operation: str, *args, **kwargs) -> Any:
        """
        Execute any QBO operation with resilience (retry, dedup, rate limiting, caching).
        This is the main method that domain services will use to interact with QBO.
        """
        # Create operation hash for deduplication
        operation_hash = self._create_operation_hash(operation, args, kwargs)
        
        if operation_hash in self.action_hashes:
            self.logger.warning(f"Duplicate operation detected: {operation}")
            return {"status": "duplicate", "message": "Operation already in progress"}
        
        # Add to deduplication tracking
        self.action_hashes.add(operation_hash)
        
        try:
            # Check sync timing
            strategy = kwargs.get('strategy', SyncStrategy.ON_DEMAND)
            priority = kwargs.get('priority', SyncPriority.MEDIUM)
            
            if not self.timing_manager.should_sync("qbo", strategy, priority):
                # Return cached data if available
                cached_data = self.cache.get("qbo", operation)
                if cached_data:
                    self.logger.debug(f"Returning cached data for {operation}")
                    return cached_data
                else:
                    return {"status": "throttled", "message": "Sync not needed at this time"}
            
            # Execute the operation with retry logic
            max_attempts = kwargs.get('max_attempts', 3)
            retry_delay = 1
            
            for attempt in range(max_attempts):
                try:
                    # Get the method from QBORawClient
                    qbo_client = self._get_qbo_client()
                    method = getattr(qbo_client, operation)
                    
                    # Execute the method
                    if asyncio.iscoroutinefunction(method):
                        result = await method(*args, **kwargs)
                    else:
                        result = method(*args, **kwargs)
                    
                    # Cache successful results
                    if result and operation in ['get_bills_from_qbo', 'get_invoices_from_qbo', 'get_customers_from_qbo']:
                        self.cache.set("qbo", operation, result, ttl_minutes=240)
                    
                    # Record success
                    self.timing_manager.record_success("qbo")
                    
                    self.logger.info(f"Successfully executed {operation} on attempt {attempt + 1}")
                    return result
                    
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed for {operation}: {e}")
                    
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        # Record failure
                        self.timing_manager.record_failure("qbo", str(e))
                        raise e
            
        finally:
            # Remove from deduplication tracking
            self.action_hashes.discard(operation_hash)
    
    def _create_operation_hash(self, operation: str, args: tuple, kwargs: dict) -> str:
        """Create a hash for operation deduplication."""
        operation_data = {
            "operation": operation,
            "args": args,
            "kwargs": {k: v for k, v in kwargs.items() if k not in ['strategy', 'priority', 'max_attempts']}
        }
        return hashlib.md5(json.dumps(operation_data, sort_keys=True).encode()).hexdigest()
    
    # ==================== CONVENIENCE METHODS ====================
    
    async def get_bills_for_digest(self, due_days: int = 30) -> Dict[str, Any]:
        """Get bills for digest generation with appropriate strategy."""
        return await self.execute_qbo_call(
            "get_bills_from_qbo", 
            due_days=due_days,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.HIGH
        )
    
    async def get_invoices_for_digest(self, aging_days: int = 30) -> Dict[str, Any]:
        """Get invoices for digest generation with appropriate strategy."""
        return await self.execute_qbo_call(
            "get_invoices_from_qbo",
            aging_days=aging_days,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.HIGH
        )
    
    async def get_customers_for_digest(self) -> Dict[str, Any]:
        """Get customers for digest generation with appropriate strategy."""
        return await self.execute_qbo_call(
            "get_customers_from_qbo",
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.MEDIUM
        )
    
    async def get_vendors_for_digest(self) -> Dict[str, Any]:
        """Get vendors for digest generation with appropriate strategy."""
        return await self.execute_qbo_call(
            "get_vendors_from_qbo",
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.MEDIUM
        )
    
    async def get_accounts_for_digest(self) -> Dict[str, Any]:
        """Get accounts for digest generation with appropriate strategy."""
        return await self.execute_qbo_call(
            "get_accounts_from_qbo",
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.MEDIUM
        )
    
    async def get_company_info_for_digest(self) -> Dict[str, Any]:
        """Get company info for digest generation with appropriate strategy."""
        return await self.execute_qbo_call(
            "get_company_info_from_qbo",
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.HIGH
        )
    
    async def get_all_data(self) -> Dict[str, Any]:
        """Get all QBO data for comprehensive analysis."""
        return await self.execute_qbo_call(
            "get_all_data",
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.HIGH
        )
    
    async def create_payment_immediate(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment immediately with high priority."""
        return await self.execute_qbo_call(
            "create_payment_in_qbo",
            payment_data=payment_data,
            strategy=SyncStrategy.IMMEDIATE,
            priority=SyncPriority.HIGH
        )
    
    async def record_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record payment in QBO with high priority."""
        return await self.execute_qbo_call(
            "record_payment",
            payment_data=payment_data,
            strategy=SyncStrategy.IMMEDIATE,
            priority=SyncPriority.HIGH
        )
    
    async def get_bills(self, since_date: datetime = None) -> Dict[str, Any]:
        """Get bills with optional date filter."""
        return await self.execute_qbo_call(
            "get_bills",
            since_date=since_date,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.MEDIUM
        )
    
    async def get_invoices(self, since_date: datetime = None) -> Dict[str, Any]:
        """Get invoices with optional date filter."""
        return await self.execute_qbo_call(
            "get_invoices",
            since_date=since_date,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.MEDIUM
        )
    
    async def get_status(self, action_type: str, entity_id: str) -> Dict[str, Any]:
        """Get status of an action in QBO."""
        return await self.execute_qbo_call(
            "get_status",
            action_type=action_type,
            entity_id=entity_id,
            strategy=SyncStrategy.ON_DEMAND,
            priority=SyncPriority.MEDIUM
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check QBO API health."""
        return await self.execute_qbo_call(
            "health_check",
            strategy=SyncStrategy.ON_DEMAND,
            priority=SyncPriority.LOW
        )
    
    # ==================== LEGACY COMPATIBILITY ====================
    
    async def execute_with_retry(self, func, *args, max_attempts: int = 3, **kwargs):
        """Legacy method for backward compatibility."""
        self.logger.warning("execute_with_retry is deprecated, use execute_qbo_call instead")
        
        # Create operation hash for deduplication
        operation_hash = self._create_operation_hash(func.__name__, args, kwargs)
        
        if operation_hash in self.action_hashes:
            self.logger.warning(f"Duplicate operation detected: {func.__name__}")
            return {"status": "duplicate", "message": "Operation already in progress"}
        
        self.action_hashes.add(operation_hash)
        
        try:
            retry_delay = 1
            for attempt in range(max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    self.timing_manager.record_success("qbo")
                    return result
                    
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        self.timing_manager.record_failure("qbo", str(e))
                        raise e
                        
        finally:
            self.action_hashes.discard(operation_hash)
    
    def should_sync(self, platform: str, strategy: str) -> bool:
        """Legacy method for backward compatibility."""
        self.logger.warning("should_sync is deprecated, use timing_manager.should_sync instead")
        return self.timing_manager.should_sync(platform, strategy, SyncPriority.MEDIUM)
    
    def get_cache(self, platform: str, operation: str = None) -> Any:
        """Legacy method for backward compatibility."""
        self.logger.warning("get_cache is deprecated, use cache.get instead")
        return self.cache.get(platform, operation)
    
    def set_cache(self, platform: str, operation: str, data: Any, ttl_minutes: int = 240) -> None:
        """Legacy method for backward compatibility."""
        self.logger.warning("set_cache is deprecated, use cache.set instead")
        self.cache.set(platform, operation, data, ttl_minutes)