from typing import List, Dict, Any
from sqlalchemy.orm import Session
from domains.ar.models.invoice import Invoice as InvoiceModel
from domains.ar.schemas.invoice import Invoice
from domains.policy.services.policy_engine import PolicyEngineService
from infra.jobs import SmartSyncService
from datetime import datetime, timedelta
from domains.core.services.base_service import TenantAwareService
import logging

logger = logging.getLogger(__name__)

class InvoiceService(TenantAwareService):
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.smart_sync = SmartSyncService(business_id)
        self.policy_engine = PolicyEngineService(db)
    
    # ==================== SMART SYNC DATA METHODS ====================
    
    def get_overdue_invoices(self, days: int = 0) -> List[Dict[str, Any]]:
        """
        Get invoices that are overdue by specified number of days.
        
        Args:
            days: Minimum days overdue (0 = all overdue invoices)
        """
        try:
            today = datetime.utcnow()
            cutoff_date = today - timedelta(days=days)
            
            invoices = self.db.query(InvoiceModel).filter(
                InvoiceModel.business_id == self.business_id,
                InvoiceModel.due_date <= cutoff_date,
                InvoiceModel.status.in_(["sent", "review", "pending"])  # Not paid
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
            logger.error(f"Failed to get overdue invoices: {e}")
            return []
    
    def get_aging_buckets(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get invoices organized by aging buckets."""
        try:
            return {
                "current": self.get_overdue_invoices(-30),  # Not yet due
                "1_30": self.get_overdue_invoices_in_range(1, 30),
                "31_60": self.get_overdue_invoices_in_range(31, 60), 
                "61_90": self.get_overdue_invoices_in_range(61, 90),
                "over_90": self.get_overdue_invoices_in_range(91, 999)
            }
        except Exception as e:
            logger.error(f"Failed to get aging buckets: {e}")
            return {}
    
    def get_overdue_invoices_in_range(self, min_days: int, max_days: int) -> List[Dict[str, Any]]:
        """Get invoices overdue within a specific day range."""
        try:
            from datetime import timedelta
            today = datetime.utcnow()
            min_date = today - timedelta(days=max_days)
            max_date = today - timedelta(days=min_days)
            
            invoices = self.db.query(InvoiceModel).filter(
                InvoiceModel.business_id == self.business_id,
                InvoiceModel.due_date >= min_date,
                InvoiceModel.due_date <= max_date,
                InvoiceModel.status.in_(["sent", "review", "pending"])
            ).all()
            
            return [
                {
                    "qbo_id": invoice.qbo_invoice_id,
                    "customer": invoice.customer.name if invoice.customer else "Unknown Customer",
                    "customer_id": invoice.customer_id,
                    "amount": float(invoice.total),
                    "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                    "status": invoice.status,
                    "balance": float(invoice.total),
                    "aging_days": (today - invoice.due_date).days if invoice.due_date else 0
                }
                for invoice in invoices
            ]
        except Exception as e:
            logger.error(f"Failed to get invoices in range {min_days}-{max_days}: {e}")
            return []

    def create_invoice(self, business_id: int, customer_id: int, issue_date: datetime, due_date: datetime, total: float, lines: List[dict]) -> Invoice:
        """Create an invoice from CSV or manual input."""
        try:
            suggestion = self.policy_engine.categorize(business_id, "invoice", total)
            
            # Extract confidence from top_k
            confidence = suggestion.top_k[0].get("confidence", 0.8) if suggestion.top_k else 0.8
            
            invoice = InvoiceModel(
                business_id=business_id,
                customer_id=customer_id,
                qbo_invoice_id=None,
                issue_date=issue_date,
                due_date=due_date,
                total=total,
                lines=lines,
                status="review" if confidence < 0.9 else "draft",
                confidence=confidence,
                attachment_refs=[]
            )
            self.db.add(invoice)
            
            # QBO sync will be handled by SmartSync in Phase 4
            # For now, we create invoices locally and sync later
            invoice.qbo_invoice_id = f"LOCAL_{invoice.invoice_id}"
            
            self.db.commit()
            self.db.refresh(invoice)
            return invoice
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Invoice creation failed: {str(e)}")

    async def sync_invoices(self, business_id: int) -> List[Invoice]:
        """Sync invoices from QBO via SmartSyncService."""
        try:
            # Use SmartSyncService for sync orchestration
            from domains.qbo.client import QBOClient
            
            # Check if sync is needed
            if not self.smart_sync.should_sync("qbo", "SCHEDULED"):
                cached_data = self.smart_sync.get_cache("qbo")
                if cached_data:
                    return cached_data
            
            # Execute sync with retry logic
            qbo_client = QBOClient(str(business_id))
            qbo_data = await self.smart_sync.execute_with_retry(
                qbo_client.get_invoices, max_attempts=3
            )
            
            qbo_invoices = qbo_data.get("invoices", [])
            
            invoices = []
            for qbo_invoice_data in qbo_invoices:
                invoice = self.db.query(InvoiceModel).filter(
                    InvoiceModel.business_id == business_id,
                    InvoiceModel.qbo_id == qbo_invoice_data.get("Id")
                ).first()
                if not invoice:
                    invoice = InvoiceModel(
                        business_id=business_id,
                        customer_id=int(qbo_invoice_data.get("CustomerRef", {}).get("value", 0)),
                        qbo_id=qbo_invoice_data.get("Id"),
                        issue_date=qbo_invoice_data.get("TxnDate"),
                        due_date=qbo_invoice_data.get("DueDate"),
                        total=float(qbo_invoice_data.get("TotalAmt", 0)),
                        lines=[{"amount": line.get("Amount", 0)} for line in qbo_invoice_data.get("Line", [])],
                        status="draft",
                        attachment_refs=[],
                        confidence=0.9
                    )
                    self.db.add(invoice)
                invoices.append(invoice)
            
            self.db.commit()
            
            # Cache results and record activity
            self.smart_sync.set_cache("qbo", invoices, ttl_minutes=240)
            self.smart_sync.record_user_activity("invoice_sync")
            
            return invoices
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Invoice sync failed: {str(e)}")

    def ingest_invoice_from_qbo(self, business_id: str, qbo_invoice_data: Dict[str, Any]) -> InvoiceModel:
        """
        Ingest an invoice from QBO data structure into our database.
        
        Args:
            business_id: The ID of the business
            qbo_invoice_data: Dictionary containing QBO invoice data
        
        Returns:
            InvoiceModel: The created or updated invoice object
        """
        try:
            qbo_id = qbo_invoice_data.get('qbo_id')
            invoice = self.db.query(InvoiceModel).filter(
                InvoiceModel.qbo_invoice_id == qbo_id,
                InvoiceModel.business_id == business_id
            ).first()
            
            if not invoice:
                invoice = InvoiceModel(
                    business_id=business_id,
                    qbo_invoice_id=qbo_id,
                    total=qbo_invoice_data.get('amount', 0.0),
                    due_date=datetime.fromisoformat(qbo_invoice_data.get('due_date')) if qbo_invoice_data.get('due_date') else None,
                    status=qbo_invoice_data.get('status', 'sent'),
                    customer_id=qbo_invoice_data.get('customer_id')
                )
                self.db.add(invoice)
            else:
                invoice.total = qbo_invoice_data.get('amount', 0.0)
                invoice.due_date = datetime.fromisoformat(qbo_invoice_data.get('due_date')) if qbo_invoice_data.get('due_date') else None
                invoice.status = qbo_invoice_data.get('status', 'sent')
                invoice.customer_id = qbo_invoice_data.get('customer_id')
            
            self.db.commit()
            self.db.refresh(invoice)
            return invoice
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to ingest invoice from QBO: {e}")
            raise ValueError(f"Failed to ingest invoice from QBO: {e}")