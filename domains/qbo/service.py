"""
QBOBulkScheduledService - Bulk and Scheduled QBO Operations

This service handles bulk data synchronization and scheduled operations for QBO.
It's separate from SmartSyncService which handles retry/error handling utilities.

Key Responsibilities:
- Bulk data synchronization from QBO
- Scheduled background operations
- Large dataset processing
- Batch operations for efficiency
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import asyncio
from dotenv import load_dotenv
from infra.jobs import BulkSyncStrategy

from domains.core.services.base_service import TenantAwareService
from .client import get_qbo_client

load_dotenv()

class QBOBulkScheduledService(TenantAwareService):
    """
    Handles bulk and scheduled QBO operations.
    
    This service is focused on:
    - Bulk data synchronization
    - Scheduled background operations
    - Large dataset processing
    - Batch operations for efficiency
    """
    
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.logger = logging.getLogger(__name__)
        self.batch_size = 100  # Process in batches to avoid memory issues
        
        # QBO client will be initialized as needed
        
        self.logger.info(f"Initialized QBOBulkScheduledService for business {business_id}")
    
    async def get_qbo_data_for_digest(self) -> Dict[str, Any]:
        """
        Get QBO data formatted for digest generation.
        
        This method provides the data structure expected by digest services.
        It's a core utility method used throughout the application.
        
        Returns:
            Dict containing bills, invoices, and other QBO data
        """
        try:
            # Get QBO client
            qbo_client = get_qbo_client(self.business_id, self.db)
            
            # Get all data in one batch call
            batch_data = await qbo_client.get_all_data_batch()
            
            return {
                "bills": batch_data.get("bills", []),
                "invoices": batch_data.get("invoices", []),
                "balances": [],  # TODO: Add balances data when QBO provider supports it
                "vendors": batch_data.get("vendors", []),
                "customers": batch_data.get("customers", []),
                "accounts": batch_data.get("accounts", []),
                "company_info": batch_data.get("company_info", {}),
                "timestamp": datetime.now().isoformat(),
                "business_id": self.business_id
            }
        except Exception as e:
            self.logger.error(f"Failed to get QBO data for digest: {e}", exc_info=True)
            return {
                "bills": [],
                "invoices": [],
                "balances": [],
                "vendors": [],
                "customers": [],
                "accounts": [],
                "company_info": {},
                "timestamp": datetime.now().isoformat(),
                "business_id": self.business_id,
                "error": str(e)
            }
    
    async def bulk_sync_qbo_data(self, strategy: BulkSyncStrategy = BulkSyncStrategy.FULL_SYNC) -> Dict[str, Any]:
        """
        Perform bulk synchronization of QBO data.
        
        Args:
            strategy: The bulk sync strategy to use
            
        Returns:
            Dict containing sync results and statistics
        """
        try:
            self.logger.info(f"Starting bulk QBO sync with strategy: {strategy.value}")
            
            # Use QBO client for API calls with retry/error handling
            qbo_client = get_qbo_client(self.business_id, self.db)
            
            # Get all data in one batch call for efficiency
            batch_data = await qbo_client.get_all_data_batch()
            
            # Extract data from batch response
            qbo_calls = {
                "bills": {"status": "success", "data": batch_data.get("bills", [])},
                "invoices": {"status": "success", "data": batch_data.get("invoices", [])},
                "vendors": {"status": "success", "data": batch_data.get("vendors", [])},
                "customers": {"status": "success", "data": batch_data.get("customers", [])},
                "accounts": {"status": "success", "data": batch_data.get("accounts", [])}
            }
            
            # Check for errors in QBO calls
            for call_type, result in qbo_calls.items():
                if result.get("status") == "error":
                    self.logger.error(f"QBO {call_type} call failed: {result.get('error')}")
                    return {
                        "status": "error",
                        "strategy": strategy.value,
                        "error": f"QBO {call_type} call failed: {result.get('error')}",
                        "completed_at": datetime.now().isoformat()
                    }
            
            sync_results = {
                "strategy": strategy.value,
                "started_at": datetime.now().isoformat(),
                "bills": {"synced": 0, "errors": 0, "skipped": 0},
                "invoices": {"synced": 0, "errors": 0, "skipped": 0},
                "vendors": {"synced": 0, "errors": 0, "skipped": 0},
                "customers": {"synced": 0, "errors": 0, "skipped": 0},
                "accounts": {"synced": 0, "errors": 0, "skipped": 0}
            }
            
            # Sync bills in batches
            if strategy in [BulkSyncStrategy.FULL_SYNC, BulkSyncStrategy.SELECTIVE]:
                bills_result = await self._bulk_sync_bills(qbo_calls["bills"]["data"])
                sync_results["bills"].update(bills_result)
            
            # Sync invoices in batches
            if strategy in [BulkSyncStrategy.FULL_SYNC, BulkSyncStrategy.SELECTIVE]:
                invoices_result = await self._bulk_sync_invoices(qbo_calls["invoices"]["data"])
                sync_results["invoices"].update(invoices_result)
            
            # Sync vendors in batches
            if strategy in [BulkSyncStrategy.FULL_SYNC, BulkSyncStrategy.SELECTIVE]:
                vendors_result = await self._bulk_sync_vendors(qbo_calls["vendors"]["data"])
                sync_results["vendors"].update(vendors_result)
            
            # Sync customers in batches
            if strategy in [BulkSyncStrategy.FULL_SYNC, BulkSyncStrategy.SELECTIVE]:
                customers_result = await self._bulk_sync_customers(qbo_calls["customers"]["data"])
                sync_results["customers"].update(customers_result)
            
            # Sync accounts in batches
            if strategy in [BulkSyncStrategy.FULL_SYNC, BulkSyncStrategy.SELECTIVE]:
                accounts_result = await self._bulk_sync_accounts(qbo_calls["accounts"]["data"])
                sync_results["accounts"].update(accounts_result)
            
            sync_results["completed_at"] = datetime.now().isoformat()
            sync_results["status"] = "success"
            
            self.logger.info(f"Bulk QBO sync completed: {sync_results}")
            return sync_results
            
        except Exception as e:
            self.logger.error(f"Bulk QBO sync failed: {e}", exc_info=True)
            return {
                "status": "error",
                "strategy": strategy.value,
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
    
    async def _bulk_sync_bills(self, bills_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Sync bills in batches using smart sync utilities."""
        try:
            from domains.ap.services.bill_ingestion import BillService
            bill_service = BillService(self.db, self.business_id)
            
            synced = 0
            errors = 0
            skipped = 0
            
            # Process in batches
            for i in range(0, len(bills_data), self.batch_size):
                batch = bills_data[i:i + self.batch_size]
                
                for bill_data in batch:
                    try:
                        # Check if bill already exists
                        existing_bill = self.db.query(
                            self.db.query(BillService.model).filter(
                                self.db.query(BillService.model).qbo_bill_id == bill_data.get('qbo_id')
                            ).first()
                        )
                        
                        if existing_bill:
                            skipped += 1
                            continue
                        
                        # Ingest new bill
                        bill_service.ingest_bill_from_qbo(self.business_id, bill_data)
                        synced += 1
                        
                    except Exception as e:
                        self.logger.error(f"Failed to sync bill {bill_data.get('qbo_id')}: {e}")
                        errors += 1
            
            return {"synced": synced, "errors": errors, "skipped": skipped}
            
        except Exception as e:
            self.logger.error(f"Bulk bills sync failed: {e}")
            return {"synced": 0, "errors": 1, "skipped": 0}
    
    async def _bulk_sync_invoices(self, invoices_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Sync invoices in batches using smart sync utilities."""
        try:
            from domains.ar.services.invoice import InvoiceService
            invoice_service = InvoiceService(self.db, self.business_id)
            
            synced = 0
            errors = 0
            skipped = 0
            
            # Process in batches
            for i in range(0, len(invoices_data), self.batch_size):
                batch = invoices_data[i:i + self.batch_size]
                
                for invoice_data in batch:
                    try:
                        # Check if invoice already exists
                        existing_invoice = self.db.query(
                            self.db.query(InvoiceService.model).filter(
                                self.db.query(InvoiceService.model).qbo_invoice_id == invoice_data.get('qbo_id')
                            ).first()
                        )
                        
                        if existing_invoice:
                            skipped += 1
                            continue
                        
                        # Ingest new invoice
                        invoice_service.ingest_invoice_from_qbo(self.business_id, invoice_data)
                        synced += 1
                        
                    except Exception as e:
                        self.logger.error(f"Failed to sync invoice {invoice_data.get('qbo_id')}: {e}")
                        errors += 1
            
            return {"synced": synced, "errors": errors, "skipped": skipped}
            
        except Exception as e:
            self.logger.error(f"Bulk invoices sync failed: {e}")
            return {"synced": 0, "errors": 1, "skipped": 0}
    
    async def _bulk_sync_vendors(self, vendors_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Sync vendors in batches using smart sync utilities."""
        try:
            from domains.ap.services.vendor import VendorService
            vendor_service = VendorService(self.db, self.business_id)
            
            synced = 0
            errors = 0
            skipped = 0
            
            # Process in batches
            for i in range(0, len(vendors_data), self.batch_size):
                batch = vendors_data[i:i + self.batch_size]
                
                for vendor_data in batch:
                    try:
                        # Check if vendor already exists
                        existing_vendor = self.db.query(
                            self.db.query(VendorService.model).filter(
                                self.db.query(VendorService.model).qbo_vendor_id == vendor_data.get('qbo_id')
                            ).first()
                        )
                        
                        if existing_vendor:
                            skipped += 1
                            continue
                        
                        # Ingest new vendor
                        vendor_service.ingest_vendor_from_qbo(self.business_id, vendor_data)
                        synced += 1
                        
                    except Exception as e:
                        self.logger.error(f"Failed to sync vendor {vendor_data.get('qbo_id')}: {e}")
                        errors += 1
            
            return {"synced": synced, "errors": errors, "skipped": skipped}
            
        except Exception as e:
            self.logger.error(f"Bulk vendors sync failed: {e}")
            return {"synced": 0, "errors": 1, "skipped": 0}
    
    async def _bulk_sync_customers(self, customers_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Sync customers in batches using smart sync utilities."""
        try:
            from domains.ar.services.customer import CustomerService
            customer_service = CustomerService(self.db, self.business_id)
            
            synced = 0
            errors = 0
            skipped = 0
            
            # Process in batches
            for i in range(0, len(customers_data), self.batch_size):
                batch = customers_data[i:i + self.batch_size]
                
                for customer_data in batch:
                    try:
                        # Check if customer already exists
                        existing_customer = self.db.query(
                            self.db.query(CustomerService.model).filter(
                                self.db.query(CustomerService.model).qbo_customer_id == customer_data.get('qbo_id')
                            ).first()
                        )
                        
                        if existing_customer:
                            skipped += 1
                            continue
                        
                        # Ingest new customer
                        customer_service.ingest_customer_from_qbo(self.business_id, customer_data)
                        synced += 1
                        
                    except Exception as e:
                        self.logger.error(f"Failed to sync customer {customer_data.get('qbo_id')}: {e}")
                        errors += 1
            
            return {"synced": synced, "errors": errors, "skipped": skipped}
            
        except Exception as e:
            self.logger.error(f"Bulk customers sync failed: {e}")
            return {"synced": 0, "errors": 1, "skipped": 0}
    
    async def _bulk_sync_accounts(self, accounts_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Sync accounts in batches using smart sync utilities."""
        try:
            from domains.core.services.balance_service import BalanceService
            balance_service = BalanceService(self.db, self.business_id)
            
            synced = 0
            errors = 0
            skipped = 0
            
            # Process in batches
            for i in range(0, len(accounts_data), self.batch_size):
                batch = accounts_data[i:i + self.batch_size]
                
                for account_data in batch:
                    try:
                        # Check if account already exists
                        existing_account = self.db.query(
                            self.db.query(BalanceService.model).filter(
                                self.db.query(BalanceService.model).qbo_account_id == account_data.get('qbo_id')
                            ).first()
                        )
                        
                        if existing_account:
                            skipped += 1
                            continue
                        
                        # Ingest new account
                        balance_service.ingest_account_from_qbo(self.business_id, account_data)
                        synced += 1
                        
                    except Exception as e:
                        self.logger.error(f"Failed to sync account {account_data.get('qbo_id')}: {e}")
                        errors += 1
            
            return {"synced": synced, "errors": errors, "skipped": skipped}
            
        except Exception as e:
            self.logger.error(f"Bulk accounts sync failed: {e}")
            return {"synced": 0, "errors": 1, "skipped": 0}
    
    async def scheduled_sync(self) -> Dict[str, Any]:
        """
        Perform scheduled background sync.
        
        This method is called by a scheduler (e.g., Celery, cron) to perform
        regular background synchronization.
        """
        try:
            self.logger.info("Starting scheduled QBO sync")
            
            # Use incremental strategy for scheduled syncs
            result = await self.bulk_sync_qbo_data(BulkSyncStrategy.INCREMENTAL)
            
            # Log scheduled sync completion
            self.logger.info(f"Scheduled QBO sync completed: {result}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Scheduled QBO sync failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get statistics about recent sync operations."""
        # This would typically query a sync_log table
        # For now, return basic info
        return {
            "last_bulk_sync": None,  # Would be populated from sync_log
            "total_synced_today": 0,  # Would be calculated from sync_log
            "sync_frequency": "daily",  # Would be configurable
            "next_scheduled_sync": None,  # Would be calculated from schedule
            "rate_limit_status": "available"  # Would be populated from QBO client
        }
    
    
