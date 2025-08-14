from typing import Optional
from sqlalchemy.orm import Session
from models.invoice import Invoice as InvoiceModel
from schemas.invoice import Invoice
from datetime import datetime
import logging

class CollectionsService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def send_reminder(self, firm_id: str, invoice_id: int, client_id: Optional[int] = None) -> Invoice:
        """Send a reminder for an overdue invoice (mocked)."""
        try:
            invoice = self.db.query(InvoiceModel).filter(
                InvoiceModel.invoice_id == invoice_id,
                InvoiceModel.firm_id == firm_id
            ).first()
            if not invoice:
                raise ValueError("Invoice not found")
            
            if invoice.due_date < datetime.utcnow() and invoice.status != "paid":
                self.logger.info(f"Sending reminder for invoice {invoice_id} to customer {invoice.customer_id}")
                invoice.status = "review"  # Flag for review if disputed
                self.db.commit()
                self.db.refresh(invoice)
            
            return invoice
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Reminder failed: {str(e)}")