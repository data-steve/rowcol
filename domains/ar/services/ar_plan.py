from sqlalchemy.orm import Session
from domains.ar.models.invoice import Invoice as InvoiceModel
from domains.ar.schemas.invoice import Invoice
from datetime import datetime
import logging

class ARPlanService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def send_reminder(self, business_id: int, invoice_id: int) -> Invoice:
        """Send a reminder for an overdue invoice (mocked)."""
        try:
            invoice = self.db.query(InvoiceModel).filter(
                InvoiceModel.invoice_id == invoice_id,
                InvoiceModel.business_id == business_id
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