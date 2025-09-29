"""
AR Collections Service - Basic collections functionality

This service handles basic AR collections operations that are specific to the runway product,
not generic AR domain operations. Moved from domains/ar/ to runway/core/ per ADR-001.

TODO: This service needs to be properly implemented as part of Smart Collections add-on module.
Current implementation is mocked and should not be used in production.
"""

from sqlalchemy.orm import Session
from domains.ar.models.invoice import Invoice as InvoiceModel
from domains.ar.schemas.invoice import Invoice
from datetime import datetime
import logging

class ARCollectionsService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def send_reminder(self, business_id: int, invoice_id: int) -> Invoice:
        """
        TODO: IMPLEMENT PROPER COLLECTIONS FUNCTIONALITY
        
        This is currently mocked and should be implemented as part of Smart Collections add-on module.
        See build_plan_v5.md Phase 2: Smart AR & Collections for proper implementation.
        
        Current mock behavior:
        - Just changes invoice status to "review" 
        - No actual email sending
        - No collection sequence management
        - No customer communication tracking
        
        Proper implementation should include:
        - 3-stage email sequences (30d gentle, 45d urgent, 60d final)
        - Priority scoring based on amount, age, customer history
        - Auto-pause on payment detection
        - Integration with EmailService for actual delivery
        - Collection activity tracking in database
        """
        # TODO: Remove this mock implementation
        try:
            invoice = self.db.query(InvoiceModel).filter(
                InvoiceModel.invoice_id == invoice_id,
                InvoiceModel.business_id == business_id
            ).first()
            if not invoice:
                raise ValueError("Invoice not found")
            
            if invoice.due_date < datetime.utcnow() and invoice.status != "paid":
                self.logger.warning(f"MOCK: Would send reminder for invoice {invoice_id} to customer {invoice.customer_id}")
                # TODO: Replace with real collections logic
                invoice.status = "review"  # Flag for review if disputed
                self.db.commit()
                self.db.refresh(invoice)
            
            return invoice
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Reminder failed: {str(e)}")
