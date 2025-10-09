"""
QBOSyncService - QBO-Specific Sync Service

QBO-specific sync service that provides business logic and convenience methods
for QBO operations. This service uses BaseSyncService for orchestration and
provides QBO-specific business logic.

Key Responsibilities:
- QBO-specific business logic and data transformation
- Convenience methods for common QBO operations
- Integration with QBO client and domain models
- Transaction log integration for audit trails

This service replaces the monolithic SmartSyncService by separating
QBO-specific business logic from generic orchestration.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta

from infra.jobs.base_sync_service import BaseSyncService
from infra.jobs.enums import SyncStrategy, SyncPriority
from infra.qbo.client import QBORawClient
from domains.core.services.transaction_log_service import TransactionLogService

logger = logging.getLogger(__name__)


class QBOSyncService:
    """
    QBO-specific sync service with business logic and convenience methods.
    
    This service provides QBO-specific business logic while using BaseSyncService
    for generic orchestration (rate limiting, retry logic, caching, etc.).
    
    ARCHITECTURE:
    - Uses BaseSyncService for generic orchestration
    - Uses QBORawClient for raw QBO API calls
    - Provides QBO-specific business logic and convenience methods
    - Integrates with domain models and transaction logs
    """
    
    def __init__(self, business_id: str, realm_id: str, db_session=None):
        self.business_id = business_id
        self.realm_id = realm_id
        self.db_session = db_session
        self.base_sync = BaseSyncService(business_id, db_session)
        self.qbo_client = QBORawClient(business_id, realm_id, db_session)
        self.transaction_log_service = TransactionLogService(db_session)
        self.logger = logging.getLogger(f"{__name__}.{business_id}")
        
        logger.info(f"Initialized QBOSyncService for business {business_id}, realm {realm_id}")
    
    # ==================== BILLS ====================
    
    async def get_bills_by_due_days(self, due_days: int = 30) -> Dict[str, Any]:
        """Get bills from QBO filtered by due days with appropriate strategy."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_bills_by_due_days",
            self.qbo_client.get_bills_from_qbo,
            due_days=due_days,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.HIGH
        )
    
    async def get_bills_by_date(self, since_date: datetime = None) -> Dict[str, Any]:
        """Get bills with optional date filter."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_bills_by_date",
            self.qbo_client.get_bills,
            since_date=since_date,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.MEDIUM
        )
    
    async def get_bills(self) -> Dict[str, Any]:
        """Get bills with default due days filter (30 days) - backward compatibility method."""
        return await self.get_bills_by_due_days()
    
    # ==================== INVOICES ====================
    
    async def get_invoices_by_aging_days(self, aging_days: int = 30) -> Dict[str, Any]:
        """Get invoices from QBO filtered by aging days with appropriate strategy."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_invoices_by_aging_days",
            self.qbo_client.get_invoices_from_qbo,
            aging_days=aging_days,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.HIGH
        )
    
    async def get_invoices_by_date(self, since_date: datetime = None) -> Dict[str, Any]:
        """Get invoices with optional date filter."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_invoices_by_date",
            self.qbo_client.get_invoices,
            since_date=since_date,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.MEDIUM
        )
    
    async def get_invoices(self) -> Dict[str, Any]:
        """Get invoices with default aging days filter (30 days) - backward compatibility method."""
        return await self.get_invoices_by_aging_days()
    
    # ==================== CUSTOMERS ====================
    
    async def get_customers(self) -> Dict[str, Any]:
        """Get customers from QBO with appropriate strategy."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_customers",
            self.qbo_client.get_customers_from_qbo,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.MEDIUM
        )
    
    # ==================== VENDORS ====================
    
    async def get_vendors(self) -> Dict[str, Any]:
        """Get vendors from QBO with appropriate strategy."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_vendors",
            self.qbo_client.get_vendors_from_qbo,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.MEDIUM
        )
    
    # ==================== ACCOUNTS ====================
    
    async def get_accounts(self) -> Dict[str, Any]:
        """Get accounts from QBO with appropriate strategy."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_accounts",
            self.qbo_client.get_accounts_from_qbo,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.MEDIUM
        )
    
    # ==================== COMPANY INFO ====================
    
    async def get_company_info(self) -> Dict[str, Any]:
        """Get company info from QBO with appropriate strategy."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_company_info",
            self.qbo_client.get_company_info_from_qbo,
            strategy=SyncStrategy.DATA_FETCH,
            priority=SyncPriority.HIGH
        )
    
    # ==================== PAYMENTS ====================
    
    async def create_payment_immediate(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment immediately with high priority."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "create_payment_immediate",
            self.qbo_client.create_payment_in_qbo,
            payment_data=payment_data,
            strategy=SyncStrategy.IMMEDIATE,
            priority=SyncPriority.HIGH
        )
    
    async def record_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record payment in QBO with high priority."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "record_payment",
            self.qbo_client.record_payment,
            payment_data=payment_data,
            strategy=SyncStrategy.IMMEDIATE,
            priority=SyncPriority.HIGH
        )
    
    async def sync_payment_record(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync payment record to QBO (read-only sync, no execution)."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "sync_payment_record",
            self.qbo_client.sync_payment_record,
            payment_data=payment_data,
            strategy=SyncStrategy.DATA_SYNC,
            priority=SyncPriority.MEDIUM
        )
    
    # ==================== STATUS AND HEALTH ====================
    
    async def get_status(self, action_type: str, entity_id: str) -> Dict[str, Any]:
        """Get status of an action in QBO."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_status",
            self.qbo_client.get_status,
            action_type=action_type,
            entity_id=entity_id,
            strategy=SyncStrategy.ON_DEMAND,
            priority=SyncPriority.MEDIUM
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check QBO API health."""
        return await self.base_sync.health_check("qbo")
    
    # ==================== REPORTS ====================
    
    async def get_kpi_data(self) -> Dict[str, Any]:
        """Get KPI data for dashboard calculations with orchestration."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_kpi_data",
            self.qbo_client.get_kpi_data,
            strategy=SyncStrategy.ON_DEMAND,
            priority=SyncPriority.HIGH
        )
    
    async def get_aging_report(self) -> Dict[str, Any]:
        """Get detailed aging report data with orchestration."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_aging_report",
            self.qbo_client.get_aging_report,
            strategy=SyncStrategy.ON_DEMAND,
            priority=SyncPriority.HIGH
        )
    
    async def get_payment_history(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """Get payment history for a specific entity with orchestration."""
        return await self.base_sync.execute_sync_call(
            "qbo",
            "get_payment_history",
            self.qbo_client.get_payment_history,
            entity_type=entity_type,
            entity_id=entity_id,
            strategy=SyncStrategy.ON_DEMAND,
            priority=SyncPriority.MEDIUM
        )
    
    # ==================== CONVENIENCE METHODS ====================
    
    async def get_qbo_data_for_digest(self) -> Dict[str, Any]:
        """Get all QBO data needed for digest calculations."""
        bills_data = await self.get_bills()
        invoices_data = await self.get_invoices()
        company_info = await self.get_company_info()
        
        return {
            "bills": bills_data,
            "invoices": invoices_data,
            "company_info": company_info
        }
    
    # ==================== SYNC WITH TRANSACTION LOGS ====================
    
    async def sync_bill_with_log(
        self, 
        bill, 
        qbo_bill_data: Dict[str, Any],
        created_by_user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sync bill data and create transaction log entry."""
        
        # Map QBO data to our format
        from infra.qbo.qbo_mapper import QBOMapper
        mapped_data = QBOMapper.map_bill_data(qbo_bill_data)
        
        # Update mirror model
        bill.qbo_bill_id = mapped_data['qbo_id']
        bill.qbo_sync_token = mapped_data['sync_token']
        bill.qbo_last_sync = datetime.utcnow()
        bill.bill_number = mapped_data['doc_number']
        bill.amount_cents = int(mapped_data['amount'] * 100)  # Convert to cents
        bill.due_date = mapped_data['due_date']
        bill.issue_date = mapped_data['txn_date']
        bill.private_note = mapped_data['private_note']
        bill.updated_at = datetime.utcnow()
        
        # Update status based on balance
        if mapped_data['balance'] > 0:
            bill.status = 'unpaid'
        else:
            bill.status = 'paid'
        
        # Save mirror model
        self.db_session.commit()
        
        # Create transaction log entry
        transaction_log = await self.transaction_log_service.log_bill_sync(
            bill=bill,
            qbo_bill_data=qbo_bill_data,
            source="qbo",
            created_by_user_id=created_by_user_id,
            session_id=session_id
        )
        
        return {
            "bill": bill,
            "transaction_log": transaction_log,
            "status": "synced"
        }
    
    async def sync_vendor_with_log(
        self, 
        vendor, 
        qbo_vendor_data: Dict[str, Any],
        created_by_user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sync vendor data and create transaction log entry."""
        
        # Map QBO data to our format
        from infra.qbo.qbo_mapper import QBOMapper
        mapped_data = QBOMapper.map_vendor_data(qbo_vendor_data)
        
        # Update mirror model
        vendor.qbo_vendor_id = mapped_data['qbo_id']
        vendor.qbo_sync_token = mapped_data['sync_token']
        vendor.qbo_last_sync = datetime.utcnow()
        vendor.name = mapped_data['name']
        vendor.legal_name = mapped_data['company_name']
        vendor.email = mapped_data['email']
        vendor.phone = mapped_data['phone']
        vendor.contact_name = mapped_data.get('contact_name')
        vendor.updated_at = datetime.utcnow()
        
        # Update billing address if available
        if mapped_data.get('billing_address'):
            vendor.billing_address = mapped_data['billing_address']
        
        # Save mirror model
        self.db_session.commit()
        
        # Create transaction log entry
        transaction_log = await self.transaction_log_service.log_vendor_sync(
            vendor=vendor,
            qbo_vendor_data=qbo_vendor_data,
            source="qbo",
            created_by_user_id=created_by_user_id,
            session_id=session_id
        )
        
        return {
            "vendor": vendor,
            "transaction_log": transaction_log,
            "status": "synced"
        }
    
    async def sync_payment_with_log(
        self, 
        payment, 
        qbo_payment_data: Dict[str, Any],
        created_by_user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sync payment data and create transaction log entry."""
        
        # Map QBO data to our format
        from infra.qbo.qbo_mapper import QBOMapper
        mapped_data = QBOMapper.map_payment_data(qbo_payment_data)
        
        # Update mirror model
        payment.qbo_payment_id = mapped_data['qbo_id']
        payment.qbo_sync_token = mapped_data['sync_token']
        payment.qbo_last_sync = datetime.utcnow()
        payment.amount_cents = int(mapped_data['amount'] * 100)  # Convert to cents
        payment.payment_date = mapped_data['txn_date']
        payment.payment_ref_num = mapped_data['payment_ref_num']
        payment.private_note = mapped_data['private_note']
        payment.payment_method = mapped_data['payment_method']
        payment.updated_at = datetime.utcnow()
        
        # Save mirror model
        self.db_session.commit()
        
        # Create transaction log entry
        transaction_log = await self.transaction_log_service.log_payment_sync(
            payment=payment,
            qbo_payment_data=qbo_payment_data,
            source="qbo",
            created_by_user_id=created_by_user_id,
            session_id=session_id
        )
        
        return {
            "payment": payment,
            "transaction_log": transaction_log,
            "status": "synced"
        }
    
    # ==================== CACHE MANAGEMENT ====================
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for QBO."""
        return self.base_sync.get_cache_stats("qbo")
    
    def clear_cache(self, operation: Optional[str] = None) -> bool:
        """Clear cache for QBO and optionally specific operation."""
        return self.base_sync.clear_cache("qbo", operation)
