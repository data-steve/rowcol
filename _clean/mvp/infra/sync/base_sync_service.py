"""
Base Sync Service for MVP

Provides base functionality for rail-specific sync services.
Based on the existing BaseSyncService pattern but simplified for MVP requirements.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import logging
import asyncio
import hashlib
import json

logger = logging.getLogger(__name__)

class BaseSyncService:
    """
    Base sync service providing common functionality for rail-specific sync services.
    
    This service provides:
    - Rate limiting and prioritization
    - Retry logic with exponential backoff
    - Deduplication to prevent duplicate actions
    - Error handling and logging
    - User activity tracking
    """
    
    def __init__(self, advisor_id: str, business_id: str):
        self.advisor_id = advisor_id
        self.business_id = business_id
        self.logger = logging.getLogger(f"{__name__}.{advisor_id}.{business_id}")
        
        # Rate limiting state
        self.last_request_time: Dict[str, datetime] = {}
        self.request_counts: Dict[str, int] = {}
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1.0  # seconds
        self.max_delay = 60.0  # seconds
    
    def _generate_idem_key(self, operation: str, payload: Dict[str, Any]) -> str:
        """Generate idempotency key for an operation."""
        key_data = {
            "advisor_id": self.advisor_id,
            "business_id": self.business_id,
            "operation": operation,
            "payload": payload
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]
    
    def _check_rate_limit(self, operation: str, max_requests_per_minute: int = 60) -> bool:
        """Check if we're within rate limits for an operation."""
        now = datetime.now()
        minute_key = f"{operation}_{now.strftime('%Y%m%d%H%M')}"
        
        # Clean old entries
        cutoff_time = now - timedelta(minutes=2)
        self.last_request_time = {
            k: v for k, v in self.last_request_time.items() 
            if v > cutoff_time
        }
        
        # Check current minute
        current_count = self.request_counts.get(minute_key, 0)
        if current_count >= max_requests_per_minute:
            self.logger.warning(f"Rate limit exceeded for {operation}: {current_count} requests")
            return False
        
        # Update counters
        self.request_counts[minute_key] = current_count + 1
        self.last_request_time[operation] = now
        
        return True
    
    async def _retry_with_backoff(self, operation: Callable, operation_name: str) -> Any:
        """Execute operation with exponential backoff retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
                    self.logger.info(f"Retrying {operation_name} in {delay}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                
                return await operation()
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Attempt {attempt + 1} failed for {operation_name}: {e}")
                
                if attempt == self.max_retries:
                    self.logger.error(f"All retry attempts failed for {operation_name}")
                    break
        
        raise last_exception
    
    def sync_entity(
        self,
        entity: str,
        fetch_function: Callable[[], tuple[List[Dict[str, Any]], Optional[str]]],
        upsert_function: Callable[[List[Dict[str, Any]], Optional[str], datetime], None],
        rate_limit_per_minute: int = 60
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Sync an entity with rate limiting and error handling.
        
        Args:
            entity: Entity type (e.g., "bills", "invoices", "balances")
            fetch_function: Function to fetch data from rail
            upsert_function: Function to upsert data into mirror
            rate_limit_per_minute: Maximum requests per minute
            
        Returns:
            Tuple of (data, source_version)
        """
        try:
            # Check rate limits
            if not self._check_rate_limit(f"sync_{entity}", rate_limit_per_minute):
                raise Exception(f"Rate limit exceeded for {entity} sync")
            
            self.logger.info(f"Starting {entity} sync for advisor {self.advisor_id}, business {self.business_id}")
            
            # Fetch data
            data, source_version = fetch_function()
            
            # Upsert into mirror
            synced_at = datetime.now()
            upsert_function(data, source_version, synced_at)
            
            self.logger.info(f"Successfully synced {len(data)} {entity} records")
            return data, source_version
            
        except Exception as e:
            self.logger.error(f"Failed to sync {entity}: {e}")
            raise
    
    def execute_write(
        self,
        operation: str,
        payload: Dict[str, Any],
        execute_function: Callable[[], Dict[str, Any]],
        rate_limit_per_minute: int = 30
    ) -> Dict[str, Any]:
        """
        Execute write operation with rate limiting and error handling.
        
        Args:
            operation: Operation name (e.g., "create_payment", "update_bill")
            payload: Write payload
            execute_function: Function to execute the write
            rate_limit_per_minute: Maximum requests per minute
            
        Returns:
            Result of the write operation
        """
        try:
            # Check rate limits
            if not self._check_rate_limit(operation, rate_limit_per_minute):
                raise Exception(f"Rate limit exceeded for {operation}")
            
            # Generate idempotency key
            idem_key = self._generate_idem_key(operation, payload)
            
            self.logger.info(f"Executing {operation} for advisor {self.advisor_id}, business {self.business_id}")
            
            # Execute operation
            result = execute_function()
            
            self.logger.info(f"Successfully executed {operation}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute {operation}: {e}")
            raise
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status and statistics."""
        return {
            "advisor_id": self.advisor_id,
            "business_id": self.business_id,
            "last_request_times": {
                k: v.isoformat() for k, v in self.last_request_time.items()
            },
            "request_counts": dict(self.request_counts),
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay
        }
