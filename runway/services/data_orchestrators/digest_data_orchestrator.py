"""
Digest Data Orchestrator

Manages data pulling and state management for the Digest weekly analysis experience,
with flexible configuration to support TestDrive, onboarding, and A/B testing.

This orchestrator follows the ADR-006 Data Orchestrator Pattern:
- Pulls historical data for business analysis
- Manages digest state (progress, insights, recommendations)
- Provides clean interface between DigestService and domain services
- Maintains ADR-001 domain separation principles
- Ensures multi-tenant safety with business_id scoping
- Supports flexible configuration for A/B testing and experimentation
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from domains.qbo.services.sync_service import QBOSyncService
from domains.core.models.business import Business
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class DigestConfig:
    """Configuration for digest behavior - enables A/B testing and experimentation."""
    
    # Core parameters
    trigger_type: str = "weekly"  # "weekly", "test_drive", "onboarding"
    time_window: str = "full_history"  # "last_4_weeks", "full_history", "custom"
    custom_start_date: Optional[datetime] = None
    custom_end_date: Optional[datetime] = None
    
    # Functionality controls
    preview_mode: bool = False  # True = read-only, False = full functionality
    show_actions: bool = True  # Show action buttons or just insights
    show_historical_trends: bool = True  # Show trends over time
    
    # Content controls
    max_issues_shown: int = 50  # Limit overwhelming issues
    priority_threshold: str = "medium"  # "low", "medium", "high"
    include_recommendations: bool = True
    
    # A/B testing parameters
    experiment_variant: Optional[str] = None  # "A", "B", "C", etc.
    user_segment: Optional[str] = None  # "new_user", "returning", etc.
    
    # Email/notification controls
    send_email: bool = True
    email_template: str = "standard"  # "standard", "test_drive", "onboarding"
    
    @classmethod
    def for_test_drive(cls, variant: str = "A") -> "DigestConfig":
        """Pre-configured for TestDrive with A/B testing support."""
        if variant == "A":
            return cls(
                trigger_type="test_drive",
                time_window="last_4_weeks",
                preview_mode=True,
                show_actions=False,
                max_issues_shown=20,
                experiment_variant="A"
            )
        elif variant == "B":
            return cls(
                trigger_type="test_drive", 
                time_window="full_history",
                preview_mode=True,
                show_actions=False,
                max_issues_shown=50,
                experiment_variant="B"
            )
        else:
            # Default to variant A
            return cls(
                trigger_type="test_drive",
                time_window="last_4_weeks",
                preview_mode=True,
                show_actions=False,
                max_issues_shown=20,
                experiment_variant=variant
            )
    
    @classmethod
    def for_weekly(cls) -> "DigestConfig":
        """Pre-configured for weekly digest."""
        return cls(
            trigger_type="weekly",
            time_window="full_history",
            preview_mode=False,
            show_actions=True,
            max_issues_shown=100
        )
    
    @classmethod
    def for_onboarding(cls) -> "DigestConfig":
        """Pre-configured for onboarding experience."""
        return cls(
            trigger_type="onboarding",
            time_window="last_4_weeks",
            preview_mode=True,
            show_actions=False,
            max_issues_shown=30,
            include_recommendations=True
        )


class DigestDataOrchestrator:
    """
    Data orchestrator for Digest experience with flexible configuration.
    
    Handles weekly digest analysis, TestDrive previews, and onboarding experiences
    with configurable behavior for A/B testing and experimentation.
    Manages digest state (progress, insights, recommendations) with
    proper multi-tenant isolation.
    """
    
    def __init__(self, db: Session):
        self.db = db  # No instance state - stateless service
        # Initialize SmartSyncService for QBO data
        self.smart_sync = QBOSyncService("", "", db)
    
    async def get_digest_data(self, business_id: str, config: DigestConfig) -> Dict[str, Any]:
        """
        Get digest data with flexible configuration for A/B testing.
        
        Args:
            business_id: The business to get data for
            config: DigestConfig with all tunable parameters
            
        Returns:
            Dictionary containing digest data and state
        """
        try:
            # Route to appropriate implementation based on config
            if config.trigger_type == "test_drive":
                return await self._get_test_drive_digest(business_id, config)
            elif config.trigger_type == "onboarding":
                return await self._get_onboarding_digest(business_id, config)
            elif config.trigger_type == "weekly":
                return await self._get_weekly_digest(business_id, config)
            else:
                return await self._get_standard_digest(business_id, config)
                
        except Exception as e:
            logger.error(f"Error getting digest data for business {business_id}: {e}")
            raise
    
    async def _get_test_drive_digest(self, business_id: str, config: DigestConfig) -> Dict[str, Any]:
        """Get TestDrive digest data with configurable scope."""
        try:
            # Initialize SmartSyncService with business_id
            smart_sync = QBOSyncService(business_id, "", self.db)
            
            # Determine date range based on config
            if config.time_window == "last_4_weeks":
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(weeks=4)
            elif config.time_window == "full_history":
                start_date = None  # Get all historical data
                end_date = datetime.utcnow()
            else:
                start_date = config.custom_start_date
                end_date = config.custom_end_date or datetime.utcnow()
            
            # Pull data from QBO with date filtering
            bills_data = await smart_sync.get_bills()
            invoices_data = await smart_sync.get_invoices()
            company_info = await smart_sync.get_company_info()
            
            # Extract and filter data
            bills = self._filter_data_by_date(bills_data.get("bills", []), start_date, end_date)
            invoices = self._filter_data_by_date(invoices_data.get("invoices", []), start_date, end_date)
            balances = company_info.get("balances", [])
            
            # Get current digest state
            digest_state = await self._get_digest_state(business_id)
            
            # Apply content controls
            bills = bills[:config.max_issues_shown]
            invoices = invoices[:config.max_issues_shown]
            
            logger.info(f"Retrieved TestDrive digest data for business {business_id}: "
                       f"{len(bills)} bills, {len(invoices)} invoices, variant {config.experiment_variant}")
            
            return {
                "bills": bills,
                "invoices": invoices,
                "balances": balances,
                "digest_state": digest_state,
                "config": {
                    "trigger_type": config.trigger_type,
                    "time_window": config.time_window,
                    "preview_mode": config.preview_mode,
                    "show_actions": config.show_actions,
                    "experiment_variant": config.experiment_variant
                },
                "business_id": business_id,
                "data_type": "test_drive",
                "synced_at": self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error getting TestDrive digest data for business {business_id}: {e}")
            raise
    
    async def _get_weekly_digest(self, business_id: str, config: DigestConfig) -> Dict[str, Any]:
        """Get weekly digest data with full functionality."""
        try:
            # Initialize SmartSyncService with business_id
            smart_sync = QBOSyncService(business_id, "", self.db)
            
            # Pull full historical data for weekly analysis
            bills_data = await smart_sync.get_bills()
            invoices_data = await smart_sync.get_invoices()
            company_info = await smart_sync.get_company_info()
            
            # Extract the actual data arrays
            bills = bills_data.get("bills", [])
            invoices = invoices_data.get("invoices", [])
            balances = company_info.get("balances", [])
            
            # Get current digest state
            digest_state = await self._get_digest_state(business_id)
            
            logger.info(f"Retrieved weekly digest data for business {business_id}: "
                       f"{len(bills)} bills, {len(invoices)} invoices")
            
            return {
                "bills": bills,
                "invoices": invoices,
                "balances": balances,
                "digest_state": digest_state,
                "config": {
                    "trigger_type": config.trigger_type,
                    "time_window": config.time_window,
                    "preview_mode": config.preview_mode,
                    "show_actions": config.show_actions
                },
                "business_id": business_id,
                "data_type": "weekly",
                "synced_at": self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error getting weekly digest data for business {business_id}: {e}")
            raise
    
    async def _get_onboarding_digest(self, business_id: str, config: DigestConfig) -> Dict[str, Any]:
        """Get onboarding digest data with limited scope."""
        try:
            # Similar to TestDrive but with onboarding-specific configuration
            return await self._get_test_drive_digest(business_id, config)
            
        except Exception as e:
            logger.error(f"Error getting onboarding digest data for business {business_id}: {e}")
            raise
    
    async def _get_standard_digest(self, business_id: str, config: DigestConfig) -> Dict[str, Any]:
        """Get standard digest data with custom configuration."""
        try:
            # Default to weekly digest behavior
            return await self._get_weekly_digest(business_id, config)
            
        except Exception as e:
            logger.error(f"Error getting standard digest data for business {business_id}: {e}")
            raise
    
    def _filter_data_by_date(self, data: List[Dict[str, Any]], 
                           start_date: Optional[datetime], 
                           end_date: Optional[datetime]) -> List[Dict[str, Any]]:
        """Filter data by date range."""
        if not start_date and not end_date:
            return data
        
        filtered_data = []
        for item in data:
            # Extract date from item (adjust field names as needed)
            item_date_str = item.get("created_at") or item.get("date") or item.get("due_date")
            if not item_date_str:
                continue
                
            try:
                item_date = datetime.fromisoformat(item_date_str.replace('Z', '+00:00'))
                
                if start_date and item_date < start_date:
                    continue
                if end_date and item_date > end_date:
                    continue
                    
                filtered_data.append(item)
            except (ValueError, TypeError):
                # Skip items with invalid dates
                continue
        
        return filtered_data
    
    async def update_digest_progress(self, business_id: str, progress: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update digest progress and insights.
        
        Args:
            business_id: The business the progress is for
            progress: Progress data (current_step, insights, recommendations)
            
        Returns:
            Updated digest data with progress updated
        """
        try:
            # Update the progress in digest state
            await self._update_digest_progress(business_id, progress)
            
            # Return updated digest data (using default config)
            config = DigestConfig.for_weekly()
            return await self.get_digest_data(business_id, config)
            
        except Exception as e:
            logger.error(f"Error updating digest progress for business {business_id}: {e}")
            raise
    
    async def _get_digest_state(self, business_id: str) -> Dict[str, Any]:
        """Get the current digest state for a business.
        
        SECURITY: All state operations are scoped by business_id to ensure
        complete isolation between businesses in multi-tenant environment.
        """
        try:
            # CRITICAL: Always filter by business_id for multi-tenant safety
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                return {
                    "current_step": "start",
                    "progress_percentage": 0,
                    "insights": [],
                    "recommendations": [],
                    "completed_at": None,
                    "last_analyzed": None
                }
            
            # For now, store digest state in business metadata
            # In the future, this could be a separate DigestState model
            if hasattr(business, 'metadata') and business.metadata:
                metadata = json.loads(business.metadata) if isinstance(business.metadata, str) else business.metadata
                return metadata.get('digest_state', {
                    "current_step": "start",
                    "progress_percentage": 0,
                    "insights": [],
                    "recommendations": [],
                    "completed_at": None,
                    "last_analyzed": None
                })
            
            return {
                "current_step": "start",
                "progress_percentage": 0,
                "insights": [],
                "recommendations": [],
                "completed_at": None,
                "last_analyzed": None
            }
            
        except Exception as e:
            logger.error(f"Error getting digest state for business {business_id}: {e}")
            return {
                "current_step": "start",
                "progress_percentage": 0,
                "insights": [],
                "recommendations": [],
                "completed_at": None,
                "last_analyzed": None
            }
    
    async def _update_digest_progress(self, business_id: str, progress: Dict[str, Any]) -> None:
        """Update digest progress and insights.
        
        SECURITY: All state operations are scoped by business_id to ensure
        complete isolation between businesses in multi-tenant environment.
        """
        try:
            # CRITICAL: Always filter by business_id for multi-tenant safety
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                raise ValueError(f"Business {business_id} not found")
            
            # Get current digest state
            current_state = await self._get_digest_state(business_id)
            
            # Update progress
            current_state.update({
                **progress,
                "updated_at": self._get_current_timestamp()
            })
            
            # Update business metadata
            metadata = json.loads(business.metadata) if business.metadata else {}
            metadata['digest_state'] = current_state
            business.metadata = json.dumps(metadata)
            
            self.db.commit()
            
            logger.info(f"Updated digest progress for business {business_id}")
            
        except Exception as e:
            logger.error(f"Error updating digest progress for business {business_id}: {e}")
            raise
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat()
