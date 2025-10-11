"""
Invoices Mirror Repository for MVP

Implements InvoicesMirrorRepo interface using SQLAlchemy models for the Smart Sync pattern.
Database-agnostic implementation that works with SQLite (MVP dev) and PostgreSQL (production).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import json
import logging

from ..db.models import MirrorInvoice

logger = logging.getLogger(__name__)

class InvoicesMirrorRepo:
    """Database-agnostic implementation of invoices mirror repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_open(self, advisor_id: str, business_id: str) -> List[Dict[str, Any]]:
        """List open invoices for advisor and business."""
        try:
            invoices = self.db.query(MirrorInvoice).filter(
                and_(
                    MirrorInvoice.advisor_id == advisor_id,
                    MirrorInvoice.business_id == business_id,
                    MirrorInvoice.status == 'OPEN'
                )
            ).order_by(MirrorInvoice.due_date.asc()).all()
            
            result = []
            for invoice in invoices:
                invoice_data = {
                    'invoice_id': invoice.invoice_id,
                    'advisor_id': invoice.advisor_id,
                    'business_id': invoice.business_id,
                    'customer_id': invoice.customer_id,
                    'customer_name': invoice.customer_name,
                    'due_date': invoice.due_date,
                    'amount': float(invoice.amount) if invoice.amount else None,
                    'status': invoice.status,
                    'source_version': invoice.source_version,
                    'last_synced_at': invoice.last_synced_at.isoformat() if invoice.last_synced_at else None,
                }
                
                # Parse JSON data if present
                if invoice.data_json:
                    try:
                        invoice_data.update(json.loads(invoice.data_json))
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON data for invoice {invoice.invoice_id}")
                
                result.append(invoice_data)
            
            return result
        except Exception as e:
            logger.error(f"Failed to list open invoices: {e}")
            return []
    
    def list_all(self, advisor_id: str, business_id: str) -> List[Dict[str, Any]]:
        """List all invoices for advisor and business."""
        try:
            invoices = self.db.query(MirrorInvoice).filter(
                and_(
                    MirrorInvoice.advisor_id == advisor_id,
                    MirrorInvoice.business_id == business_id
                )
            ).order_by(MirrorInvoice.due_date.asc()).all()
            
            result = []
            for invoice in invoices:
                invoice_data = {
                    'invoice_id': invoice.invoice_id,
                    'advisor_id': invoice.advisor_id,
                    'business_id': invoice.business_id,
                    'customer_id': invoice.customer_id,
                    'customer_name': invoice.customer_name,
                    'due_date': invoice.due_date,
                    'amount': float(invoice.amount) if invoice.amount else None,
                    'status': invoice.status,
                    'source_version': invoice.source_version,
                    'last_synced_at': invoice.last_synced_at.isoformat() if invoice.last_synced_at else None,
                }
                
                # Parse JSON data if present
                if invoice.data_json:
                    try:
                        invoice_data.update(json.loads(invoice.data_json))
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON data for invoice {invoice.invoice_id}")
                
                result.append(invoice_data)
            
            return result
        except Exception as e:
            logger.error(f"Failed to list all invoices: {e}")
            return []
    
    def upsert_many(self, advisor_id: str, business_id: str, raw_invoices: List[Dict[str, Any]], 
                   source_version: Optional[str], synced_at: datetime) -> None:
        """Upsert many invoices into mirror."""
        try:
            for invoice_data in raw_invoices:
                # Extract key fields
                invoice_id = invoice_data.get('Id') or invoice_data.get('id')
                if not invoice_id:
                    logger.warning(f"Invoice missing ID, skipping: {invoice_data}")
                    continue
                
                customer_name = invoice_data.get('CustomerRef', {}).get('name', '') if isinstance(invoice_data.get('CustomerRef'), dict) else ''
                due_date = invoice_data.get('DueDate', '')
                amount = invoice_data.get('TotalAmt', 0) or invoice_data.get('amount', 0)
                status = 'OPEN'  # Default status for QBO invoices
                
                # Check if invoice exists
                existing_invoice = self.db.query(MirrorInvoice).filter(
                    and_(
                        MirrorInvoice.invoice_id == str(invoice_id),
                        MirrorInvoice.advisor_id == advisor_id,
                        MirrorInvoice.business_id == business_id
                    )
                ).first()
                
                if existing_invoice:
                    # Update existing invoice
                    existing_invoice.customer_name = customer_name
                    existing_invoice.due_date = due_date
                    existing_invoice.amount = amount
                    existing_invoice.status = status
                    existing_invoice.source_version = source_version
                    existing_invoice.last_synced_at = synced_at
                    existing_invoice.data_json = json.dumps(invoice_data)
                else:
                    # Create new invoice
                    new_invoice = MirrorInvoice(
                        invoice_id=str(invoice_id),
                        advisor_id=advisor_id,
                        business_id=business_id,
                        customer_name=customer_name,
                        due_date=due_date,
                        amount=amount,
                        status=status,
                        source_version=source_version,
                        last_synced_at=synced_at,
                        data_json=json.dumps(invoice_data)
                    )
                    self.db.add(new_invoice)
            
            self.db.commit()
            logger.info(f"Upserted {len(raw_invoices)} invoices for advisor {advisor_id}, business {business_id}")
        except Exception as e:
            logger.error(f"Failed to upsert invoices: {e}")
            self.db.rollback()
            raise
    
    def is_fresh(self, advisor_id: str, business_id: str, policy: Dict[str, Any]) -> bool:
        """Check if mirror data is fresh according to policy."""
        try:
            soft_ttl = policy.get('soft_ttl_seconds', 900)  # 15 minutes default
            hard_ttl = policy.get('hard_ttl_seconds', 3600)
            
            # Get most recent sync time
            latest_invoice = self.db.query(MirrorInvoice).filter(
                and_(
                    MirrorInvoice.advisor_id == advisor_id,
                    MirrorInvoice.business_id == business_id
                )
            ).order_by(desc(MirrorInvoice.last_synced_at)).first()
            
            if not latest_invoice or not latest_invoice.last_synced_at:
                return False  # No data, not fresh
            
            age_seconds = (datetime.now() - latest_invoice.last_synced_at).total_seconds()
            return age_seconds <= soft_ttl
        except Exception as e:
            logger.error(f"Failed to check freshness: {e}")
            return False
    
    def get_by_id(self, advisor_id: str, business_id: str, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get specific invoice by ID."""
        try:
            invoice = self.db.query(MirrorInvoice).filter(
                and_(
                    MirrorInvoice.advisor_id == advisor_id,
                    MirrorInvoice.business_id == business_id,
                    MirrorInvoice.invoice_id == invoice_id
                )
            ).first()
            
            if not invoice:
                return None
            
            invoice_data = {
                'invoice_id': invoice.invoice_id,
                'advisor_id': invoice.advisor_id,
                'business_id': invoice.business_id,
                'customer_id': invoice.customer_id,
                'customer_name': invoice.customer_name,
                'due_date': invoice.due_date,
                'amount': float(invoice.amount) if invoice.amount else None,
                'status': invoice.status,
                'source_version': invoice.source_version,
                'last_synced_at': invoice.last_synced_at.isoformat() if invoice.last_synced_at else None,
            }
            
            # Parse JSON data if present
            if invoice.data_json:
                try:
                    invoice_data.update(json.loads(invoice.data_json))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON data for invoice {invoice_id}")
            
            return invoice_data
        except Exception as e:
            logger.error(f"Failed to get invoice by ID: {e}")
            return None
