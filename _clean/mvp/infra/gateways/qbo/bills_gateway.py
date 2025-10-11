"""
QBO Bills Gateway Implementation

Implements BillsGateway interface using QBO API and Smart Sync pattern.
Provides QBO-specific implementation of rail-agnostic bills operations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import logging

from domains.ap.gateways import BillsGateway, Bill, ListBillsQuery
from infra.sync.orchestrator import SyncOrchestrator
from infra.repos.ap_repo import BillsMirrorRepo
from infra.rails.qbo.client import QBORawClient
from infra.config.exceptions import IntegrationError

logger = logging.getLogger(__name__)

class QBOBillsGateway(BillsGateway):
    """QBO implementation of BillsGateway using Smart Sync pattern."""
    
    def __init__(self, advisor_id: str, business_id: str, realm_id: str, 
                 sync_orchestrator: SyncOrchestrator, bills_repo: BillsMirrorRepo):
        self.advisor_id = advisor_id
        self.business_id = business_id
        self.realm_id = realm_id
        self.sync_orchestrator = sync_orchestrator
        self.bills_repo = bills_repo
        self.qbo_client = QBORawClient(business_id, realm_id)
        
        logger.info(f"Initialized QBOBillsGateway for advisor {advisor_id}, business {business_id}")
    
    def list(self, query: ListBillsQuery) -> List[Bill]:
        """List bills using Smart Sync pattern."""
        try:
            # Use sync orchestrator to get fresh data
            result = self.sync_orchestrator.read_refresh(
                entity="bills",
                client_id=query.advisor_id,
                hint=query.freshness_hint,
                mirror_is_fresh=lambda e, c, p: self.bills_repo.is_fresh(query.advisor_id, query.business_id, p),
                fetch_remote=lambda: self._fetch_bills_from_qbo(query.status),
                upsert_mirror=lambda raw, ver, ts: self.bills_repo.upsert_many(query.advisor_id, query.business_id, raw, ver, ts),
                read_from_mirror=lambda: self.bills_repo.list_by_status(query.advisor_id, query.business_id, query.status),
                on_hygiene=lambda c, code: self._flag_hygiene(c, code)
            )
            
            # Convert to domain Bill objects
            return [self._convert_to_bill(bill_data) for bill_data in result]
            
        except Exception as e:
            logger.error(f"Failed to list bills: {e}")
            raise IntegrationError(f"Failed to list bills: {e}")
    
    def list_incomplete(self, query: ListBillsQuery) -> List[Bill]:
        """List bills with missing data for Hygiene Tray."""
        try:
            # Get all bills first
            all_bills = self.list(query)
            
            # Filter for incomplete bills
            incomplete_bills = []
            for bill in all_bills:
                if self._is_incomplete(bill):
                    incomplete_bills.append(bill)
            
            return incomplete_bills
            
        except Exception as e:
            logger.error(f"Failed to list incomplete bills: {e}")
            raise IntegrationError(f"Failed to list incomplete bills: {e}")
    
    def list_payment_ready(self, query: ListBillsQuery) -> List[Bill]:
        """List bills ready for payment scheduling for Decision Console."""
        try:
            # Get all bills first
            all_bills = self.list(query)
            
            # Filter for payment-ready bills
            payment_ready_bills = []
            for bill in all_bills:
                if self._is_payment_ready(bill):
                    payment_ready_bills.append(bill)
            
            return payment_ready_bills
            
        except Exception as e:
            logger.error(f"Failed to list payment-ready bills: {e}")
            raise IntegrationError(f"Failed to list payment-ready bills: {e}")
    
    def list_by_due_days(self, query: ListBillsQuery, due_days: int = 30) -> List[Bill]:
        """List bills due within specified days."""
        try:
            # Get all bills first
            all_bills = self.list(query)
            
            # Filter by due date
            from datetime import datetime, timedelta
            cutoff_date = datetime.now().date() + timedelta(days=due_days)
            
            due_bills = []
            for bill in all_bills:
                if bill.due_date and bill.due_date <= cutoff_date:
                    due_bills.append(bill)
            
            return due_bills
            
        except Exception as e:
            logger.error(f"Failed to list bills by due days: {e}")
            raise IntegrationError(f"Failed to list bills by due days: {e}")
    
    def get_by_id(self, advisor_id: str, business_id: str, bill_id: str) -> Optional[Bill]:
        """Get specific bill by ID."""
        try:
            # Check mirror first
            mirror_bill = self.bills_repo.get_by_id(advisor_id, business_id, bill_id)
            
            if mirror_bill:
                return self._convert_to_bill(mirror_bill)
            
            # If not in mirror, fetch from QBO
            qbo_bill = self.qbo_client.get(f"bills/{bill_id}")
            if qbo_bill:
                return self._convert_to_bill(qbo_bill)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get bill {bill_id}: {e}")
            raise IntegrationError(f"Failed to get bill: {e}")
    
    async def update_bill(self, request) -> bool:
        """Update bill in QBO."""
        try:
            # Update in QBO
            result = self.qbo_client.put(f"bills/{request.bill_id}", request.updates)
            
            if result.get("success"):
                # Log the update
                self.sync_orchestrator.write_idempotent(
                    operation="bills.update_bill",
                    client_id=request.advisor_id,
                    idem_key=f"update_bill_{request.bill_id}",
                    call_remote=lambda: result,
                    optimistic_apply=lambda data: self.bills_repo.update(request.advisor_id, request.business_id, request.bill_id, data),
                    on_hygiene=lambda c, code: self._flag_hygiene(c, code)
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update bill: {e}")
            raise IntegrationError(f"Failed to update bill: {e}")
    
    async def get_payment_history(self, bill_id: str) -> List[dict]:
        """Get payment history for a bill (read-only bookkeeping task)."""
        try:
            # Use raw HTTP client to get payment history
            response = self.qbo_client.get(f"bills/{bill_id}/payments")
            return response.get("QueryResponse", {}).get("Payment", [])
        except Exception as e:
            logger.error(f"Failed to get payment history for bill {bill_id}: {e}")
            raise IntegrationError(f"Failed to get payment history: {e}")
    
    def _is_incomplete(self, bill: Bill) -> bool:
        """Check if bill has missing data for Hygiene Tray."""
        return (
            not bill.vendor_name or
            not bill.due_date or
            bill.amount <= 0 or
            not bill.qbo_id
        )
    
    def _is_payment_ready(self, bill: Bill) -> bool:
        """Check if bill is ready for payment scheduling for Decision Console."""
        return (
            bill.vendor_name and
            bill.due_date and
            bill.amount > 0 and
            bill.status in ["OPEN", "SCHEDULED"] and
            bill.qbo_id
        )
    
    def _flag_hygiene(self, client_id: str, code: str):
        """Flag hygiene issue for client."""
        logger.warning(f"Hygiene issue for client {client_id}: {code}")
        # Could integrate with hygiene tracking system here
    
    async def _fetch_bills_from_qbo(self, status: str) -> tuple[List[dict], str]:
        """Fetch bills from QBO API using raw HTTP client."""
        try:
            # Use raw HTTP client to get bills
            response = self.qbo_client.get(f"bills?status={status}")
            return response.get("QueryResponse", {}).get("Bill", []), response.get("time", "")
        except Exception as e:
            logger.error(f"Failed to fetch bills from QBO: {e}")
            raise
    
    def _convert_to_bill(self, data: Dict[str, Any]) -> Bill:
        """Convert QBO or mirror data to domain Bill object."""
        if "Id" in data:  # QBO data
            vendor_ref = data.get("VendorRef", {})
            return Bill(
                bill_id=str(data.get("Id", "")),
                advisor_id=self.advisor_id,
                business_id=self.business_id,
                qbo_id=str(data.get("Id", "")),
                vendor_id=str(vendor_ref.get("value", "")) if vendor_ref else None,
                vendor_name=vendor_ref.get("name", "") if vendor_ref else "",
                due_date=data.get("DueDate"),
                amount=Decimal(str(data.get("TotalAmt", 0))),
                status="OPEN" if data.get("Balance", 0) > 0 else "PAID",
                source_version=data.get("SyncToken", ""),
                last_synced_at=data.get("MetaData", {}).get("LastUpdatedTime")
            )
        else:  # Mirror data
            return Bill(
                bill_id=data["bill_id"],
                advisor_id=data["advisor_id"],
                business_id=data["business_id"],
                qbo_id=data["qbo_id"],
                vendor_id=data.get("vendor_id"),
                vendor_name=data.get("vendor_name", ""),
                due_date=data.get("due_date"),
                amount=Decimal(str(data.get("amount", 0))),
                status=data.get("status", "OPEN"),
                source_version=data.get("source_version", ""),
                last_synced_at=data.get("last_synced_at")
            )
