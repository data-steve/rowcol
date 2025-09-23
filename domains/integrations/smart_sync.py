"""
SmartSyncService - Unified Integration Coordinator (ADR-005 Compliant)

This service coordinates data synchronization across external platforms while
following proper architectural principles:

- ADR-001: Domains/Runway separation (this is a domain service)
- ADR-002: Mock-first development with provider patterns
- ADR-003: Multi-tenant isolation with business_id
- ADR-005: Business logic belongs in domain services, not orchestrators

Key Principle: SmartSync ORCHESTRATES but does NOT duplicate business logic.
All data queries and business rules belong in their respective domain services.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import asyncio
from enum import Enum
from dotenv import load_dotenv

from domains.core.services.base_service import TenantAwareService

load_dotenv()

class SyncStrategy(Enum):
    ON_DEMAND = "on_demand"
    SCHEDULED = "scheduled"
    EVENT_TRIGGERED = "event_triggered"
    BACKGROUND = "background"

class SyncPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SmartSyncService(TenantAwareService):
    """
    Unified integration coordinator following ADR-005.
    
    This service orchestrates data synchronization but delegates all business
    logic to the appropriate domain services.
    """
    
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.last_sync = {}
        self.sync_cache = {}
        self.user_activity = {}
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"Initialized SmartSyncService for business {business_id}")

        self.sync_intervals = {
            "qbo": {
                "min_interval": 30,
                "business_hours": 240,
                "month_end": 120,
                "tax_season": 60
            },
        }
    
    async def get_qbo_data_for_digest(self) -> Dict[str, Any]:
        """
        Get QBO data for digest generation using enhanced QBOAPIProvider.
        
        ✅ PROPER: Uses enhanced factory function with automatic realm_id lookup.
        """
        try:
            # Use QBOAPIProvider factory with database session
            from domains.integrations.qbo.qbo_api_provider import get_qbo_provider
            qbo_provider = get_qbo_provider(self.business_id, self.db)
            
            # Get all QBO data with proper error handling
            bills_data = await qbo_provider.get_bills()
            invoices_data = await qbo_provider.get_invoices()
            vendors_data = await qbo_provider.get_vendors()
            customers_data = await qbo_provider.get_customers()
            accounts_data = await qbo_provider.get_accounts()
            company_info = await qbo_provider.get_company_info()
            
            return {
                "bills": bills_data,
                "invoices": invoices_data,
                "vendors": vendors_data,
                "customers": customers_data,
                "accounts": accounts_data,
                "company_info": company_info,
                "synced_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get QBO data for digest: {e}", exc_info=True)
            return {
                "bills": [],
                "invoices": [],
                "vendors": [],
                "customers": [],
                "accounts": [],
                "company_info": {},
                "synced_at": datetime.now().isoformat(),
                "error": str(e)
            }
    
    # Removed _get_balances_from_service - now using proper BalanceService
    
    async def sync_qbo_data(self, strategy: SyncStrategy = SyncStrategy.ON_DEMAND) -> Dict[str, Any]:
        """
        Synchronize data from QBO using the new QBOService.
        
        This method coordinates bulk QBO data sync and updates our domain models
        through the appropriate services.
        """
        try:
            self.logger.info(f"Starting QBO sync with strategy: {strategy.value}")
            
            # Check rate limiting
            if not self._should_sync("qbo", strategy):
                return {"status": "skipped", "reason": "rate_limited"}
            
            # Use QBOAPIProvider factory with database session
            from domains.integrations.qbo.qbo_api_provider import get_qbo_provider
            qbo_provider = get_qbo_provider(self.business_id, self.db)
            
            # Fetch data from QBO API
            bills_data = await qbo_provider.get_bills()
            invoices_data = await qbo_provider.get_invoices()
            
            # Sync bills through domain service
            from domains.ap.services.bill_ingestion import BillService
            bill_service = BillService(self.db, self.business_id)
            synced_bills = 0
            for bill_data in bills_data:
                try:
                    bill_service.ingest_bill_from_qbo(self.business_id, bill_data)
                    synced_bills += 1
                except Exception as e:
                    self.logger.error(f"Failed to ingest bill {bill_data.get('qbo_id')}: {e}")
            
            # Sync invoices through domain service
            from domains.ar.services.invoice import InvoiceService
            invoice_service = InvoiceService(self.db, self.business_id)
            synced_invoices = 0
            for invoice_data in invoices_data:
                try:
                    # Assuming a similar method exists or will be created
                    invoice_service.ingest_invoice_from_qbo(self.business_id, invoice_data)
                    synced_invoices += 1
                except Exception as e:
                    self.logger.error(f"Failed to ingest invoice {invoice_data.get('qbo_id')}: {e}")
            
            # Update last sync time
            self.last_sync["qbo"] = datetime.now()
            
            return {
                "status": "success",
                "synced_bills": synced_bills,
                "synced_invoices": synced_invoices,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"QBO sync failed: {e}", exc_info=True)
            return {"status": "error", "reason": str(e)}
    
    def _should_sync(self, platform: str, strategy: SyncStrategy) -> bool:
        """Check if sync should proceed based on rate limiting and strategy."""
        if strategy == SyncStrategy.ON_DEMAND:
            return True  # Always allow on-demand syncs
        
        last_sync_time = self.last_sync.get(platform)
        if not last_sync_time:
            return True  # Never synced before
        
        min_interval = self.sync_intervals[platform]["min_interval"]
        time_since_sync = (datetime.now() - last_sync_time).total_seconds() / 60
        
        return time_since_sync >= min_interval
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status for all platforms."""
        return {
            "last_sync_times": {
                platform: sync_time.isoformat() if sync_time else None
                for platform, sync_time in self.last_sync.items()
            },
            "cache_status": {
                platform: {
                    "cached_at": cache_data.get("cached_at"),
                    "size": len(cache_data.get("data", []))
                }
                for platform, cache_data in self.sync_cache.items()
            }
        }
