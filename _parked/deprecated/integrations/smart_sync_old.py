from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import asyncio
from enum import Enum
from dotenv import load_dotenv

from domains.core.services.base_service import TenantAwareService
from domains.integrations.qbo.qbo_connection_manager import get_qbo_connection_manager

load_dotenv()

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

class SmartSyncService(TenantAwareService):
    """
    Smart sync service that intelligently manages data synchronization with tenant isolation.
    
    Handles QBO sync timing, rate limiting, and context-aware intervals for individual businesses.
    Essential for Phase 1 AP & Payment Orchestration to prevent API rate limit issues.
    """
    
    def __init__(self, db: Session, business_id: str):
        """
        Initialize smart sync service with tenant isolation.
        
        Args:
            db: Database session
            business_id: Business identifier for tenant isolation
        """
        super().__init__(db, business_id)
        self.last_sync = {}  # Track last sync time per platform for this business
        self.sync_cache = {}  # Cache sync results for this business
        self.user_activity = {}  # Track user activity patterns for this business
        self.logger = logging.getLogger(__name__)
        
        # Initialize QBO connection manager
        self.qbo_connection_manager = get_qbo_connection_manager(db)
        
        self.logger.info(f"Initialized SmartSyncService for business {business_id}")
        
        # Sync intervals (in minutes)
        self.sync_intervals = {
            "qbo": {
                "min_interval": 30,      # Don't sync more than every 30 minutes
                "business_hours": 240,   # Every 4 hours during business hours
                "month_end": 120,        # Every 2 hours during month-end
                "tax_season": 60         # Every hour during tax season
            },
            # "jobber": {
            #     "min_interval": 15,      # Jobber can be synced more frequently
            #     "business_hours": 120,   # Every 2 hours
            #     "month_end": 60         # Every hour during month-end
            # },
            # "stripe": {
            #     "min_interval": 5,       # Stripe can be very frequent
            #     "business_hours": 60,    # Every hour
            #     "month_end": 30         # Every 30 minutes during month-end
            # }
        }
    
    def should_sync(self, platform: str, strategy: SyncStrategy, priority: SyncPriority = SyncPriority.MEDIUM) -> bool:
        """Determine if we should sync based on strategy and timing."""
        now = datetime.now()
        last_sync_time = self.last_sync.get(platform)
        
        # If never synced, always sync
        if not last_sync_time:
            return True
        
        # Calculate time since last sync
        time_since_last = (now - last_sync_time).total_seconds() / 60  # minutes
        
        # Get minimum interval for this platform
        min_interval = self.sync_intervals[platform]["min_interval"]
        
        # High priority requests can override timing
        if priority == SyncPriority.HIGH:
            return time_since_last >= (min_interval / 2)  # Allow more frequent syncs for urgent requests
        
        # Check minimum interval
        if time_since_last < min_interval:
            return False
        
        # Strategy-specific logic
        if strategy == SyncStrategy.ON_DEMAND:
            # User explicitly requested sync - allow it
            return True
        
        elif strategy == SyncStrategy.SCHEDULED:
            # Scheduled sync - check business hours and special periods
            return self._should_scheduled_sync(platform, now)
        
        elif strategy == SyncStrategy.EVENT_TRIGGERED:
            # Event-triggered sync - check if user is active
            return self._should_event_sync(platform, now)
        
        elif strategy == SyncStrategy.BACKGROUND:
            # Background sync - only when system is idle
            return self._should_background_sync(platform, now)
        
        return False
    
    def _should_scheduled_sync(self, platform: str, now: datetime) -> bool:
        """Determine if scheduled sync should run."""
        # Check if it's business hours (9 AM - 5 PM)
        is_business_hours = 9 <= now.hour < 17
        
        # Check if it's month-end (last 3 days of month)
        is_month_end = now.day >= 28
        
        # Check if it's tax season (Jan-Apr, Sep-Oct)
        is_tax_season = now.month in [1, 2, 3, 4, 9, 10]
        
        # Get appropriate interval
        if is_tax_season:
            interval = self.sync_intervals[platform]["tax_season"]
        elif is_month_end:
            interval = self.sync_intervals[platform]["month_end"]
        elif is_business_hours:
            interval = self.sync_intervals[platform]["business_hours"]
        else:
            interval = self.sync_intervals[platform]["min_interval"] * 4  # Much less frequent off-hours
        
        # Check if enough time has passed
        last_sync_time = self.last_sync.get(platform)
        if not last_sync_time:
            return True
        
        time_since_last = (now - last_sync_time).total_seconds() / 60
        return time_since_last >= interval
    
    def _should_event_sync(self, platform: str, now: datetime) -> bool:
        """Determine if event-triggered sync should run."""
        # Check if user is actively working
        user_active = self._is_user_active(now)
        
        # If user is active, be more aggressive with syncs
        if user_active:
            min_interval = self.sync_intervals[platform]["min_interval"] / 2
        else:
            min_interval = self.sync_intervals[platform]["min_interval"]
        
        last_sync_time = self.last_sync.get(platform)
        if not last_sync_time:
            return True
        
        time_since_last = (now - last_sync_time).total_seconds() / 60
        return time_since_last >= min_interval
    
    def _should_background_sync(self, platform: str, now: datetime) -> bool:
        """Determine if background sync should run."""
        # Only run background syncs during off-hours or when system is idle
        is_business_hours = 9 <= now.hour < 17
        is_weekend = now.weekday() >= 5
        
        if is_business_hours and not is_weekend:
            # During business hours, only if system is very idle
            return self._is_system_idle()
        else:
            # Off-hours, allow more frequent background syncs
            last_sync_time = self.last_sync.get(platform)
            if not last_sync_time:
                return True
            
            time_since_last = (now - last_sync_time).total_seconds() / 60
            return time_since_last >= (self.sync_intervals[platform]["min_interval"] * 2)
    
    def _is_user_active(self, now: datetime) -> bool:
        """Check if user is actively working."""
        # Check recent user activity (last 30 minutes)
        recent_activity = self.user_activity.get("last_action")
        if not recent_activity:
            return False
        
        time_since_activity = (now - recent_activity).total_seconds() / 60
        return time_since_activity < 30
    
    def _is_system_idle(self) -> bool:
        """Check if system is idle."""
        # This could check CPU usage, active processes, etc.
        # For now, just check if no recent user activity
        return not self._is_user_active(datetime.now())
    
    def record_user_activity(self, activity_type: str):
        """Record user activity for smart sync decisions."""
        now = datetime.now()
        self.user_activity["last_action"] = now
        self.user_activity["last_activity_type"] = activity_type
        
        # Log activity for analytics
        self.logger.info(f"User activity: {activity_type} at {now}")
    
    def sync_platform(self, platform: str, strategy: SyncStrategy, priority: SyncPriority = SyncPriority.MEDIUM) -> Dict[str, Any]:
        """Sync a specific platform with smart timing."""
        if not self.should_sync(platform, strategy, priority):
            return {
                "status": "skipped",
                "reason": "Sync not needed based on timing and strategy",
                "platform": platform,
                "strategy": strategy.value,
                "priority": priority.value
            }
        
        try:
            # Perform the actual sync
            result = self._perform_sync(platform)
            
            # Update last sync time
            self.last_sync[platform] = datetime.now()
            
            # Cache results
            self.sync_cache[platform] = {
                "data": result,
                "timestamp": datetime.now(),
                "strategy": strategy.value
            }
            
            return {
                "status": "success",
                "platform": platform,
                "strategy": strategy.value,
                "priority": priority.value,
                "data": result,
                "synced_at": self.last_sync[platform].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Sync failed for {platform}: {str(e)}")
            return {
                "status": "error",
                "platform": platform,
                "strategy": strategy.value,
                "priority": priority.value,
                "error": str(e)
            }
    
    def _perform_sync(self, platform: str) -> Dict[str, Any]:
        """Perform the actual sync for a platform using proper domain services."""
        if platform == "qbo":
            # Use domain services with QBO API provider (following ADR-002)
            from domains.integrations.qbo.qbo_api_provider import get_qbo_provider
            from domains.integrations.qbo.qbo_auth import qbo_auth
            from domains.core.models.business import Business
            from domains.core.models.integration import Integration
            from domains.ap.services.bill_ingestion import BillService
            from domains.ar.services.invoice import InvoiceService
            from domains.ap.services.vendor import VendorService
            from domains.ar.services.customer import CustomerService
            
            # Check if business has valid QBO connection
            if not qbo_auth.is_connected(self.business_id):
                raise ValueError(f"Business {self.business_id} not connected to QBO")
            
            # Get business and integration info
            business = self.db.query(Business).filter(
                Business.business_id == self.business_id
            ).first()
            
            if not business:
                raise ValueError(f"Business {self.business_id} not found")
            
            integration = self.db.query(Integration).filter(
                Integration.business_id == self.business_id,
                Integration.platform == "qbo"
            ).first()
            
            if not integration or not integration.realm_id:
                raise ValueError(f"QBO integration not properly configured for business {self.business_id}")
            
            # Get QBO API provider (will use mock in development/test)
            qbo_provider = get_qbo_provider(self.business_id, integration.realm_id)
            
            # Use domain services to get data (they handle database operations)
            bill_service = BillService(self.db, self.business_id)
            invoice_service = InvoiceService(self.db, self.business_id)
            vendor_service = VendorService(self.db, self.business_id)
            customer_service = CustomerService(self.db, self.business_id)
            
            # Get data from our domain services (not QBO API directly)
            # The QBO provider is for syncing FROM QBO TO our services
            return {
                "bills": self._get_bills_from_service(bill_service),
                "invoices": self._get_invoices_from_service(invoice_service),
                "vendors": self._get_vendors_from_service(vendor_service),
                "customers": self._get_customers_from_service(customer_service),
                "balances": self._get_balances_from_service(),
                "synced_at": datetime.now().isoformat()
            }
        elif platform == "plaid":
            # Use Plaid integration from domains/integrations
            from domains.integrations.plaid.sync import PlaidSync
            plaid_service = PlaidSync(self.db, self.business_id)
            return plaid_service.sync_accounts()
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    # ==================== DOMAIN SERVICE DATA RETRIEVAL ====================
    
    t calbill, inld be 
            
            return [
                {
                    "qbo_id": bill.qbo_bill_id,
                    "vendor": bill.vendor.name if bill.vendor else "Unknown Vendor",
                    "vendor_id": bill.vendor_id,
                    "amount": float(bill.amount),
                    "due_date": bill.due_date.isoformat() if bill.due_date else None,
                    "status": bill.status,
                    "balance": float(bill.amount)  # Simplified
                }
                for bill in bills
            ]
        except Exception as e:
            self.logger.error(f"Failed to get bills from service: {e}")
            return []
    
    def _get_invoices_from_service(self, invoice_service: 'InvoiceService') -> List[Dict[str, Any]]:
        """Get invoices from InvoiceService (our database, not QBO API)."""
        try:
            from domains.ar.models.invoice import Invoice
            from datetime import datetime, timedelta
            
            # Get overdue invoices (aging > 0 days)
            today = datetime.utcnow()
            invoices = self.db.query(Invoice).filter(
                Invoice.business_id == self.business_id,
                Invoice.due_date < today,
                Invoice.status != "paid"
            ).all()
            
            return [
                {
                    "qbo_id": invoice.qbo_invoice_id,
                    "customer": invoice.customer.name if invoice.customer else "Unknown Customer",
                    "customer_id": invoice.customer_id,
                    "amount": float(invoice.total),
                    "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                    "status": invoice.status,
                    "balance": float(invoice.total),  # Simplified
                    "aging_days": (today - invoice.due_date).days if invoice.due_date else 0
                }
                for invoice in invoices
            ]
        except Exception as e:
            self.logger.error(f"Failed to get invoices from service: {e}")
            return []
    
    def _get_vendors_from_service(self, vendor_service: 'VendorService') -> List[Dict[str, Any]]:
        """Get vendors from VendorService (our database, not QBO API)."""
        try:
            from domains.ap.models.vendor import Vendor
            
            vendors = self.db.query(Vendor).filter(
                Vendor.business_id == self.business_id,
                Vendor.is_active == True
            ).all()
            
            return [
                {
                    "qbo_id": vendor.qbo_vendor_id,
                    "name": vendor.name,
                    "is_active": vendor.is_active,
                    "balance": 0  # Would need to calculate from bills
                }
                for vendor in vendors
            ]
        except Exception as e:
            self.logger.error(f"Failed to get vendors from service: {e}")
            return []
    
    def _get_customers_from_service(self, customer_service: 'CustomerService') -> List[Dict[str, Any]]:
        """Get customers from CustomerService (our database, not QBO API)."""
        try:
            from domains.ar.models.customer import Customer
            
            customers = self.db.query(Customer).filter(
                Customer.business_id == self.business_id,
                Customer.is_active == True
            ).all()
            
            return [
                {
                    "qbo_id": customer.qbo_customer_id,
                    "name": customer.name,
                    "is_active": customer.is_active,
                    "balance": 0  # Would need to calculate from invoices
                }
                for customer in customers
            ]
        except Exception as e:
            self.logger.error(f"Failed to get customers from service: {e}")
            return []
    
    def _get_balances_from_service(self) -> List[Dict[str, Any]]:
        """Get account balances from our database."""
        try:
            from domains.core.models.balance import Balance
            
            balances = self.db.query(Balance).filter(
                Balance.business_id == self.business_id
            ).all()
            
            return [
                {
                    "account_id": balance.qbo_account_id,
                    "current_balance": float(balance.current_balance),
                    "available_balance": float(balance.available_balance),
                    "account_type": balance.account_type
                }
                for balance in balances
            ]
        except Exception as e:
            self.logger.error(f"Failed to get balances from service: {e}")
            return []
    
    # ==================== QBO-SPECIFIC SYNC METHODS ====================
    
    def sync_qbo_bills(self, due_days: int = 30) -> Dict[str, Any]:
        """Sync QBO bills with smart timing."""
        return self.sync_platform("qbo", SyncStrategy.EVENT_TRIGGERED)
    
    def sync_qbo_invoices(self, aging_days: int = 30) -> Dict[str, Any]:
        """Sync QBO invoices with smart timing.""" 
        return self.sync_platform("qbo", SyncStrategy.EVENT_TRIGGERED)
    
    def get_qbo_data_for_digest(self) -> Dict[str, Any]:
        """Get QBO data specifically for digest generation."""
        # Use ON_DEMAND strategy for digest generation (user is waiting)
        result = self.sync_platform("qbo", SyncStrategy.ON_DEMAND, SyncPriority.HIGH)
        
        if result["status"] == "success":
            return result["data"]
        elif result["status"] == "skipped":
            # Return cached data if sync was skipped
            cached = self.sync_cache.get("qbo")
            if cached:
                return cached["data"]
        
        # If no cached data and sync failed, return empty data
        return {"bills": [], "invoices": [], "balances": []}
    
    def get_sync_status(self, platform: str) -> Dict[str, Any]:
        """Get current sync status for a platform."""
        last_sync = self.last_sync.get(platform)
        cached_data = self.sync_cache.get(platform)
        
        return {
            "platform": platform,
            "last_sync": last_sync.isoformat() if last_sync else None,
            "time_since_last": self._get_time_since_last(platform),
            "cached_data": cached_data is not None,
            "cache_age": self._get_cache_age(platform),
            "next_scheduled_sync": self._get_next_scheduled_sync(platform)
        }
    
    def _get_time_since_last(self, platform: str) -> Optional[str]:
        """Get human-readable time since last sync."""
        last_sync = self.last_sync.get(platform)
        if not last_sync:
            return "Never"
        
        now = datetime.now()
        diff = now - last_sync
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    
    def _get_cache_age(self, platform: str) -> Optional[str]:
        """Get human-readable cache age."""
        cached_data = self.sync_cache.get(platform)
        if not cached_data:
            return None
        
        now = datetime.now()
        diff = now - cached_data["timestamp"]
        
        if diff.seconds < 60:
            return f"{diff.seconds} seconds"
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes} minutes"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hours"
    
    def _get_next_scheduled_sync(self, platform: str) -> Optional[str]:
        """Get when the next scheduled sync will run."""
        now = datetime.now()
        last_sync = self.last_sync.get(platform)
        
        if not last_sync:
            return "Immediately"
        
        # Calculate next sync time based on business hours
        if 9 <= now.hour < 17:  # Business hours
            interval = self.sync_intervals[platform]["business_hours"]
        else:  # Off hours
            interval = self.sync_intervals[platform]["min_interval"] * 4
        
        next_sync = last_sync + timedelta(minutes=interval)
        return next_sync.strftime("%Y-%m-%d %H:%M")
