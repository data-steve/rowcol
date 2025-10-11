"""
Entity Policy Configuration for MVP

Defines TTL policies for different entity types in the Smart Sync pattern.
Based on the example_sync_orchestrator_kit pattern but adapted for MVP requirements.
"""

from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Literal, Dict, Optional
import logging

logger = logging.getLogger(__name__)

FreshnessHint = Literal["CACHED_OK", "STRICT"]

@dataclass(frozen=True)
class PolicyItem:
    """Policy configuration for an entity type."""
    soft_ttl_seconds: int
    hard_ttl_seconds: int
    
    @property
    def soft_ttl(self) -> timedelta:
        return timedelta(seconds=self.soft_ttl_seconds)
    
    @property
    def hard_ttl(self) -> timedelta:
        return timedelta(seconds=self.hard_ttl_seconds)

class EntityPolicy:
    """
    Central policy for cached reads and freshness management.
    
    This policy defines TTL configurations for different entity types,
    following the Smart Sync pattern requirements.
    """
    
    def __init__(self) -> None:
        self.policies: Dict[str, PolicyItem] = {
            "bills": PolicyItem(soft_ttl_seconds=300, hard_ttl_seconds=3600),      # 5min soft, 1hr hard
            "invoices": PolicyItem(soft_ttl_seconds=900, hard_ttl_seconds=3600),    # 15min soft, 1hr hard  
            "balances": PolicyItem(soft_ttl_seconds=120, hard_ttl_seconds=600),    # 2min soft, 10min hard
            "vendors": PolicyItem(soft_ttl_seconds=3600, hard_ttl_seconds=86400),   # 1hr soft, 24hr hard
            "customers": PolicyItem(soft_ttl_seconds=3600, hard_ttl_seconds=86400), # 1hr soft, 24hr hard
        }
    
    def get_policy(self, entity: str) -> PolicyItem:
        """Get policy for an entity type."""
        if entity not in self.policies:
            logger.warning(f"No policy found for entity '{entity}', using default")
            return PolicyItem(soft_ttl_seconds=300, hard_ttl_seconds=3600)
        return self.policies[entity]
    
    def is_fresh(self, entity: str, cached_at: datetime, now: Optional[datetime] = None) -> bool:
        """
        Check if cached data is fresh according to soft TTL.
        
        Args:
            entity: Entity type (e.g., 'bills', 'invoices')
            cached_at: When the data was cached
            now: Current time (defaults to datetime.now())
            
        Returns:
            True if data is fresh (within soft TTL), False otherwise
        """
        if now is None:
            now = datetime.now()
        
        policy = self.get_policy(entity)
        age = now - cached_at
        return age <= policy.soft_ttl
    
    def is_stale(self, entity: str, cached_at: datetime, now: Optional[datetime] = None) -> bool:
        """
        Check if cached data is stale according to hard TTL.
        
        Args:
            entity: Entity type (e.g., 'bills', 'invoices')
            cached_at: When the data was cached
            now: Current time (defaults to datetime.now())
            
        Returns:
            True if data is stale (beyond hard TTL), False otherwise
        """
        if now is None:
            now = datetime.now()
        
        policy = self.get_policy(entity)
        age = now - cached_at
        return age > policy.hard_ttl
    
    def should_refresh(self, entity: str, cached_at: datetime, now: Optional[datetime] = None) -> bool:
        """
        Check if data should be refreshed based on soft TTL.
        
        This is an alias for is_fresh() for clarity in different contexts.
        """
        return not self.is_fresh(entity, cached_at, now)
    
    def get_soft_ttl_seconds(self, entity: str) -> int:
        """Get soft TTL in seconds for an entity."""
        return self.get_policy(entity).soft_ttl_seconds
    
    def get_hard_ttl_seconds(self, entity: str) -> int:
        """Get hard TTL in seconds for an entity."""
        return self.get_policy(entity).hard_ttl_seconds
