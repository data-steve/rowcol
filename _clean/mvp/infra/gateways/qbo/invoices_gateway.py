"""
QBO Invoices Gateway Implementation

Implements InvoicesGateway interface using QBO API and Smart Sync pattern.
Provides QBO-specific implementation of rail-agnostic invoices operations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import logging

from domains.ar.gateways import InvoicesGateway, Invoice, ListInvoicesQuery
from infra.sync.orchestrator import SyncOrchestrator
from infra.repos.ar_repo import InvoicesMirrorRepo
from infra.rails.qbo.client import QBORawClient
from infra.config.exceptions import IntegrationError

logger = logging.getLogger(__name__)

class QBOInvoicesGateway(InvoicesGateway):
    """QBO implementation of InvoicesGateway using Smart Sync pattern."""
    
    def __init__(self, advisor_id: str, business_id: str, realm_id: str, 
                 sync_orchestrator: SyncOrchestrator, invoices_repo: InvoicesMirrorRepo):
        self.advisor_id = advisor_id
        self.business_id = business_id
        self.realm_id = realm_id
        self.sync_orchestrator = sync_orchestrator
        self.invoices_repo = invoices_repo
        self.qbo_client = QBORawClient(business_id, realm_id)
        
        logger.info(f"Initialized QBOInvoicesGateway for advisor {advisor_id}, business {business_id}")
    
    def list(self, query: ListInvoicesQuery) -> List[Invoice]:
        """List invoices using Smart Sync pattern."""
        try:
            # Use sync orchestrator to get fresh data
            result = self.sync_orchestrator.read_refresh(
                entity="invoices",
                client_id=query.advisor_id,
                hint=query.freshness_hint,
                mirror_is_fresh=lambda e, c, p: self.invoices_repo.is_fresh(query.advisor_id, query.business_id, p),
                fetch_remote=lambda: self._fetch_invoices_from_qbo(query.status),
                upsert_mirror=lambda raw, ver, ts: self.invoices_repo.upsert_many(query.advisor_id, query.business_id, raw, ver, ts),
                read_from_mirror=lambda: self.invoices_repo.list_by_status(query.advisor_id, query.business_id, query.status),
                on_hygiene=lambda c, code: self._flag_hygiene(c, code)
            )
            
            # Convert to domain Invoice objects
            return [self._convert_to_invoice(invoice_data) for invoice_data in result]
            
        except Exception as e:
            logger.error(f"Failed to list invoices: {e}")
            raise IntegrationError(f"Failed to list invoices: {e}")
    
    def list_incomplete(self, query: ListInvoicesQuery) -> List[Invoice]:
        """List invoices with missing data for Hygiene Tray."""
        try:
            # Get all invoices first
            all_invoices = self.list(query)
            
            # Filter for incomplete invoices
            incomplete_invoices = []
            for invoice in all_invoices:
                if self._is_incomplete(invoice):
                    incomplete_invoices.append(invoice)
            
            return incomplete_invoices
            
        except Exception as e:
            logger.error(f"Failed to list incomplete invoices: {e}")
            raise IntegrationError(f"Failed to list incomplete invoices: {e}")
    
    def list_collections_ready(self, query: ListInvoicesQuery) -> List[Invoice]:
        """List invoices ready for collections attention for Decision Console."""
        try:
            # Get all invoices first
            all_invoices = self.list(query)
            
            # Filter for collections-ready invoices (30+ days overdue)
            from datetime import datetime, timedelta
            cutoff_date = datetime.now().date() - timedelta(days=30)
            
            collections_ready_invoices = []
            for invoice in all_invoices:
                if self._is_collections_ready(invoice, cutoff_date):
                    collections_ready_invoices.append(invoice)
            
            return collections_ready_invoices
            
        except Exception as e:
            logger.error(f"Failed to list collections-ready invoices: {e}")
            raise IntegrationError(f"Failed to list collections-ready invoices: {e}")
    
    def list_by_aging_days(self, query: ListInvoicesQuery, aging_days: int = 30) -> List[Invoice]:
        """List invoices by aging days."""
        try:
            # Get all invoices first
            all_invoices = self.list(query)
            
            # Filter by aging days
            from datetime import datetime, timedelta
            cutoff_date = datetime.now().date() - timedelta(days=aging_days)
            
            aging_invoices = []
            for invoice in all_invoices:
                if invoice.due_date and invoice.due_date <= cutoff_date:
                    aging_invoices.append(invoice)
            
            return aging_invoices
            
        except Exception as e:
            logger.error(f"Failed to list invoices by aging days: {e}")
            raise IntegrationError(f"Failed to list invoices by aging days: {e}")
    
    def get_by_id(self, advisor_id: str, business_id: str, invoice_id: str) -> Optional[Invoice]:
        """Get specific invoice by ID."""
        try:
            # Check mirror first
            mirror_invoice = self.invoices_repo.get_by_id(advisor_id, business_id, invoice_id)
            
            if mirror_invoice:
                return self._convert_to_invoice(mirror_invoice)
            
            # If not in mirror, fetch from QBO
            qbo_invoice = self.qbo_client.get(f"invoices/{invoice_id}")
            if qbo_invoice:
                return self._convert_to_invoice(qbo_invoice)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get invoice {invoice_id}: {e}")
            raise IntegrationError(f"Failed to get invoice: {e}")
    
    async def update_invoice(self, request) -> bool:
        """Update invoice in QBO."""
        try:
            # Update in QBO
            result = self.qbo_client.put(f"invoices/{request.invoice_id}", request.updates)
            
            if result.get("success"):
                # Log the update
                self.sync_orchestrator.write_idempotent(
                    operation="invoices.update_invoice",
                    client_id=request.advisor_id,
                    idem_key=f"update_invoice_{request.invoice_id}",
                    call_remote=lambda: result,
                    optimistic_apply=lambda data: self.invoices_repo.update(request.advisor_id, request.business_id, request.invoice_id, data),
                    on_hygiene=lambda c, code: self._flag_hygiene(c, code)
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update invoice: {e}")
            raise IntegrationError(f"Failed to update invoice: {e}")
    
    async def get_payment_history(self, invoice_id: str) -> List[dict]:
        """Get payment history for an invoice (read-only bookkeeping task)."""
        try:
            # Use raw HTTP client to get payment history
            response = self.qbo_client.get(f"invoices/{invoice_id}/payments")
            return response.get("QueryResponse", {}).get("Payment", [])
        except Exception as e:
            logger.error(f"Failed to get payment history for invoice {invoice_id}: {e}")
            raise IntegrationError(f"Failed to get payment history: {e}")
    
    def _is_incomplete(self, invoice: Invoice) -> bool:
        """Check if invoice has missing data for Hygiene Tray."""
        return (
            not invoice.customer_name or
            not invoice.due_date or
            invoice.amount <= 0 or
            not invoice.qbo_id
        )
    
    def _is_collections_ready(self, invoice: Invoice, cutoff_date) -> bool:
        """Check if invoice is ready for collections attention (30+ days overdue)."""
        return (
            invoice.customer_name and
            invoice.due_date and
            invoice.amount > 0 and
            invoice.status in ["OPEN", "PARTIAL"] and
            invoice.qbo_id and
            invoice.due_date <= cutoff_date  # 30+ days overdue
        )
    
    def _flag_hygiene(self, client_id: str, code: str):
        """Flag hygiene issue for client."""
        logger.warning(f"Hygiene issue for client {client_id}: {code}")
        # Could integrate with hygiene tracking system here
    
    async def _fetch_invoices_from_qbo(self, status: str) -> tuple[List[dict], str]:
        """Fetch invoices from QBO API using raw HTTP client."""
        try:
            # Use raw HTTP client to get invoices
            response = self.qbo_client.get(f"invoices?status={status}")
            invoices_data = response.get("QueryResponse", {}).get("Invoice", [])
            return invoices_data, response.get("time", "")
        except Exception as e:
            logger.error(f"Failed to fetch invoices from QBO: {e}")
            raise
    
    def _convert_to_invoice(self, data: Dict[str, Any]) -> Invoice:
        """Convert QBO or mirror data to domain Invoice object."""
        if "Id" in data:  # QBO data
            customer_ref = data.get("CustomerRef", {})
            return Invoice(
                invoice_id=str(data.get("Id", "")),
                advisor_id=self.advisor_id,
                business_id=self.business_id,
                qbo_id=str(data.get("Id", "")),
                customer_id=str(customer_ref.get("value", "")) if customer_ref else None,
                customer_name=customer_ref.get("name", "") if customer_ref else "",
                due_date=data.get("DueDate"),
                amount=Decimal(str(data.get("TotalAmt", 0))),
                status="OPEN" if data.get("Balance", 0) > 0 else "PAID",
                source_version=data.get("SyncToken", ""),
                last_synced_at=data.get("MetaData", {}).get("LastUpdatedTime")
            )
        else:  # Mirror data
            return Invoice(
                invoice_id=data["invoice_id"],
                advisor_id=data["advisor_id"],
                business_id=data["business_id"],
                qbo_id=data["qbo_id"],
                customer_id=data.get("customer_id"),
                customer_name=data.get("customer_name", ""),
                due_date=data.get("due_date"),
                amount=Decimal(str(data.get("amount", 0))),
                status=data.get("status", "OPEN"),
                source_version=data.get("source_version", ""),
                last_synced_at=data.get("last_synced_at")
            )
