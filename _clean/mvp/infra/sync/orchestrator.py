"""
Sync Orchestrator for MVP

Implements the Smart Sync pattern with policy-driven facade over repositories.
Based on the example_sync_orchestrator_kit pattern but adapted for MVP requirements.

Key Features:
- Policy-driven freshness checks
- STRICT vs CACHED_OK hint handling
- Transaction log integration
- Mirror → Log → Rail ordering
- Hygiene flagging for stale data
"""

from typing import Literal, Callable, Any, Optional, Dict, List
from datetime import datetime
import logging

from .entity_policy import EntityPolicy, FreshnessHint

logger = logging.getLogger(__name__)

class SyncOrchestrator:
    """
    Sync Orchestrator implementing the Smart Sync pattern.
    
    This orchestrator provides policy-driven facade over repositories and handles
    the Smart Sync pattern with proper transaction logging and mirror management.
    
    Smart Sync Pattern:
    1. Check freshness hint (STRICT vs CACHED_OK)
    2. If STRICT or stale → fetch from rail → log INBOUND → upsert mirror → return data
    3. If CACHED_OK and fresh → return mirror data
    4. On error → log failure + flag hygiene + return stale mirror
    """
    
    def __init__(self, entity_policy: Optional[EntityPolicy] = None):
        self.entity_policy = entity_policy or EntityPolicy()
    
    def read_refresh(
        self,
        entity: str,                    # "bills", "invoices", "balances"
        advisor_id: str,               # advisor_id in MVP
        business_id: str,              # business_id in MVP
        hint: FreshnessHint,           # "CACHED_OK" or "STRICT"
        mirror_is_fresh: Callable[[str, str, Dict[str, Any]], bool],
        fetch_remote: Callable[[], tuple[List[Dict[str, Any]], Optional[str]]],
        upsert_mirror: Callable[[List[Dict[str, Any]], Optional[str], datetime], None],
        read_from_mirror: Callable[[], List[Any]],
        log_inbound: Callable[[str, str, str, Optional[str], Optional[int], Optional[str], Optional[str], Optional[str]], None],
        flag_hygiene: Callable[[str, str], None],
    ) -> List[Any]:
        """
        Main Smart Sync method implementing the read-refresh pattern.
        
        Args:
            entity: Entity type (e.g., "bills", "invoices", "balances")
            advisor_id: Advisor identifier
            business_id: Business identifier
            hint: Freshness hint ("CACHED_OK" or "STRICT")
            mirror_is_fresh: Function to check if mirror data is fresh
            fetch_remote: Function to fetch data from rail (returns data, source_version)
            upsert_mirror: Function to upsert data into mirror
            read_from_mirror: Function to read data from mirror
            log_inbound: Function to log inbound transaction
            flag_hygiene: Function to flag hygiene issues
            
        Returns:
            List of domain objects from mirror
        """
        try:
            # Get policy for this entity
            policy = {
                "soft_ttl_seconds": self.entity_policy.get_soft_ttl_seconds(entity),
                "hard_ttl_seconds": self.entity_policy.get_hard_ttl_seconds(entity)
            }
            
            # Check if we should fetch from rail
            should_fetch = (
                hint == "STRICT" or 
                not mirror_is_fresh(advisor_id, business_id, policy)
            )
            
            if should_fetch:
                logger.info(f"Fetching {entity} from rail for advisor {advisor_id}, business {business_id} (hint: {hint})")
                
                # Fetch from rail
                raw_data, source_version = fetch_remote()
                
                # Log inbound transaction
                log_inbound(
                    direction="INBOUND",
                    rail="qbo",  # MVP is QBO-only
                    operation=f"list_{entity}",
                    advisor_id=advisor_id,
                    business_id=business_id,
                    idem_key=None,  # Read operations don't need idempotency
                    http_code=200,  # Assume success for now
                    status="OK",
                    payload_json=str(raw_data) if raw_data else None,
                    source_version=source_version
                )
                
                # Upsert into mirror
                synced_at = datetime.now()
                upsert_mirror(raw_data, source_version, synced_at)
                
                logger.info(f"Successfully synced {len(raw_data)} {entity} records")
                
            else:
                logger.debug(f"Using cached {entity} data for advisor {advisor_id}, business {business_id}")
            
            # Always return from mirror (single source of truth)
            return read_from_mirror()
            
        except Exception as e:
            logger.error(f"Error in sync orchestrator for {entity}: {e}")
            
            # Flag hygiene issue
            flag_hygiene(advisor_id, f"sync_error_{entity}")
            
            # Try to return stale data from mirror
            try:
                stale_data = read_from_mirror()
                logger.warning(f"Returning stale {entity} data due to sync error")
                return stale_data
            except Exception as mirror_error:
                logger.error(f"Failed to read stale data from mirror: {mirror_error}")
                return []
    
    def write_with_log(
        self,
        entity: str,
        advisor_id: str,
        business_id: str,
        operation: str,
        payload: Dict[str, Any],
        execute_write: Callable[[], Dict[str, Any]],
        log_outbound: Callable[[str, str, str, str, Optional[str], Optional[int], Optional[str], Optional[str], Optional[str]], None],
        idem_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute write operation with proper transaction logging.
        
        Args:
            entity: Entity type (e.g., "bills", "invoices", "balances")
            advisor_id: Advisor identifier
            business_id: Business identifier
            operation: Operation name (e.g., "create_payment", "update_bill")
            payload: Write payload
            idem_key: Idempotency key for the operation
            execute_write: Function to execute the write operation
            log_outbound: Function to log outbound transaction
            
        Returns:
            Result of the write operation
        """
        try:
            logger.info(f"Executing {operation} for {entity} (advisor: {advisor_id}, business: {business_id})")
            
            # Execute write operation
            result = execute_write()
            
            # Log outbound transaction
            log_outbound(
                direction="OUTBOUND",
                rail="qbo",  # MVP is QBO-only
                operation=operation,
                advisor_id=advisor_id,
                business_id=business_id,
                idem_key=idem_key,
                http_code=200,  # Assume success for now
                status="OK",
                payload_json=str(payload),
                source_version=None
            )
            
            logger.info(f"Successfully executed {operation}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing {operation}: {e}")
            
            # Log failed transaction
            log_outbound(
                direction="OUTBOUND",
                rail="qbo",
                operation=operation,
                advisor_id=advisor_id,
                business_id=business_id,
                idem_key=idem_key,
                http_code=500,  # Internal server error
                status="FAILED",
                payload_json=str(payload),
                source_version=None
            )
            
            raise
