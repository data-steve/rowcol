"""
Invoice Management Service - Parked for Future Stripe Implementation

This service contains invoice creation methods that were moved from
domain services to maintain QBO-honest architecture.

QBO is only a ledger rail - it cannot create invoices.
These methods will be implemented by Stripe when invoice creation is enabled.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class InvoiceManagementService:
    """
    A/R execution service - will be implemented by Stripe.
    
    This service contains invoice creation methods that were moved from
    the domain service to maintain QBO-honest architecture.
    """
    
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
    
    async def create_invoice(self, customer_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create invoice for customer.
        
        This method was moved from domain services to maintain QBO-honest architecture.
        
        Args:
            customer_id: The ID of the customer
            items: List of invoice items
            
        Returns:
            Dict containing invoice information
        """
        logger.info(f"Invoice creation requested for customer {customer_id} - will be implemented by Stripe")
        
        # Future Stripe integration
        return {
            "status": "parked",
            "message": "Invoice creation will be implemented by Stripe",
            "customer_id": customer_id,
            "invoice_id": f"PARKED-{customer_id}",
            "items": items
        }
    
    async def send_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """
        Send invoice to customer.
        
        This method was moved from domain services to maintain QBO-honest architecture.
        
        Args:
            invoice_id: The ID of the invoice to send
            
        Returns:
            Dict containing send result
        """
        logger.info(f"Invoice sending requested for {invoice_id} - will be implemented by Stripe")
        
        # Future Stripe integration
        return {
            "status": "parked",
            "message": "Invoice sending will be implemented by Stripe",
            "invoice_id": invoice_id,
            "sent_at": None
        }
