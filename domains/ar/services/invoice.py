"""
QBO-Honest AR Invoice Service

This service provides basic CRUD operations for invoice mirroring from QBO.
It does NOT include advanced features that QBO doesn't support:
- No invoice creation (QBO doesn't allow it)
- No advanced categorization (moved to parked/)
- No policy engine integration (moved to parked/)

This service focuses on what QBO actually provides:
- Sync invoices from QBO
- Basic CRUD on local copies
- Simple querying and filtering
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from domains.ar.models.invoice import Invoice as InvoiceModel
from domains.ar.schemas.invoice import Invoice
from domains.qbo.services.sync_service import QBOSyncService
from infra.qbo.qbo_mapper import QBOMapper
from datetime import datetime, timedelta
from domains.core.services.base_service import TenantAwareService
import logging

logger = logging.getLogger(__name__)

class InvoiceService(TenantAwareService):
    """
    QBO-honest AR invoice service for basic CRUD operations.
    
    This service only provides functionality that QBO actually supports:
    - Sync invoices from QBO (read-only)
    - Basic CRUD on local copies
    - Simple querying and filtering
    
    Advanced features moved to _parked/:
    - Invoice creation (QBO doesn't allow it)
    - Advanced categorization (policy engine)
    - Complex business logic (moved to runway/)
    """
    
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.smart_sync = QBOSyncService(business_id, "", self.db)
        # Note: policy_engine removed - moved to _parked/
    
    # ==================== QBO SYNC METHODS ====================
    
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
            logger.error(f"Error getting overdue invoices: {e}")
            return []
    
    def get_invoices_by_aging_days(self, aging_days: int = 30) -> List[Dict[str, Any]]:
        """
        Get invoices by aging days (how long they've been outstanding).
        
        Args:
            aging_days: Minimum days outstanding
        """
        try:
            today = datetime.utcnow()
            cutoff_date = today - timedelta(days=aging_days)
            
            invoices = self.db.query(InvoiceModel).filter(
                InvoiceModel.business_id == self.business_id,
                InvoiceModel.due_date <= cutoff_date,
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
            logger.error(f"Error getting invoices by aging: {e}")
            return []
    
    def get_invoice_by_qbo_id(self, qbo_id: str) -> Optional[Dict[str, Any]]:
        """
        Get invoice by QBO ID.
        
        Args:
            qbo_id: QBO invoice ID
        """
        try:
            invoice = self.db.query(InvoiceModel).filter(
                InvoiceModel.business_id == self.business_id,
                InvoiceModel.qbo_invoice_id == qbo_id
            ).first()
            
            if not invoice:
                return None
            
            return {
                "qbo_id": invoice.qbo_invoice_id,
                "customer": invoice.customer.name if invoice.customer else "Unknown Customer",
                "customer_id": invoice.customer_id,
                "amount": float(invoice.total),
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "status": invoice.status,
                "balance": float(invoice.total),
                "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
                "updated_at": invoice.updated_at.isoformat() if invoice.updated_at else None
            }
        except Exception as e:
            logger.error(f"Error getting invoice by QBO ID {qbo_id}: {e}")
            return None
    
    def get_invoices_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get all invoices for a specific customer.
        
        Args:
            customer_id: Customer ID
        """
        try:
            invoices = self.db.query(InvoiceModel).filter(
                InvoiceModel.business_id == self.business_id,
                InvoiceModel.customer_id == customer_id
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
                    "created_at": invoice.created_at.isoformat() if invoice.created_at else None
                }
                for invoice in invoices
            ]
        except Exception as e:
            logger.error(f"Error getting invoices for customer {customer_id}: {e}")
            return []
    
    def get_invoices_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get invoices by status.
        
        Args:
            status: Invoice status (sent, paid, overdue, etc.)
        """
        try:
            invoices = self.db.query(InvoiceModel).filter(
                InvoiceModel.business_id == self.business_id,
                InvoiceModel.status == status
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
                    "created_at": invoice.created_at.isoformat() if invoice.created_at else None
                }
                for invoice in invoices
            ]
        except Exception as e:
            logger.error(f"Error getting invoices by status {status}: {e}")
            return []
    
    # ==================== QBO SYNC INTEGRATION ====================
    
    # NOTE: Sync operations moved to QBOSyncService
    # Use domains/qbo/services/sync_service.py for QBO sync operations
    
    # ==================== BASIC CRUD OPERATIONS ====================
    
    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get invoice by local ID.
        
        Args:
            invoice_id: Local invoice ID
        """
        try:
            invoice = self.db.query(InvoiceModel).filter(
                InvoiceModel.business_id == self.business_id,
                InvoiceModel.invoice_id == invoice_id
            ).first()
            
            if not invoice:
                return None
            
            return {
                "invoice_id": invoice.invoice_id,
                "qbo_id": invoice.qbo_invoice_id,
                "customer": invoice.customer.name if invoice.customer else "Unknown Customer",
                "customer_id": invoice.customer_id,
                "amount": float(invoice.total),
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "status": invoice.status,
                "balance": float(invoice.total),
                "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
                "updated_at": invoice.updated_at.isoformat() if invoice.updated_at else None
            }
        except Exception as e:
            logger.error(f"Error getting invoice {invoice_id}: {e}")
            return None
    
    def update_invoice_status(self, invoice_id: str, status: str) -> bool:
        """
        Update invoice status.
        
        Args:
            invoice_id: Local invoice ID
            status: New status
        """
        try:
            invoice = self.db.query(InvoiceModel).filter(
                InvoiceModel.business_id == self.business_id,
                InvoiceModel.invoice_id == invoice_id
            ).first()
            
            if not invoice:
                return False
            
            invoice.status = status
            invoice.updated_at = datetime.utcnow()
            self.db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error updating invoice status {invoice_id}: {e}")
            return False
    
    def delete_invoice(self, invoice_id: str) -> bool:
        """
        Delete invoice (soft delete by setting status to 'deleted').
        
        Args:
            invoice_id: Local invoice ID
        """
        try:
            invoice = self.db.query(InvoiceModel).filter(
                InvoiceModel.business_id == self.business_id,
                InvoiceModel.invoice_id == invoice_id
            ).first()
            
            if not invoice:
                return False
            
            # Soft delete - don't actually delete from database
            invoice.status = 'deleted'
            invoice.updated_at = datetime.utcnow()
            self.db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting invoice {invoice_id}: {e}")
            return False