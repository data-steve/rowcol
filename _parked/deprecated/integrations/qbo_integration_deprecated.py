"""
DEPRECATED: This file violates ADR-002 by mixing production and mock data.

Use instead:
- domains/integrations/qbo/qbo_api_provider.py (Production QBO API calls)
- Domain services (BillService, InvoiceService, etc.) for business logic
- MockQBOAPIProvider for testing

This file will be removed in a future cleanup.
"""

from sqlalchemy.orm import Session
from domains.core.models.balance import Balance
from domains.core.models.business import Business
from .qbo_auth import qbo_auth
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QBOIntegration:
    """QBO integration with centralized authentication and token management.
    
    Uses the centralized QBOAuth service for all token operations,
    eliminating the anti-pattern of individual auth client management.
    """
    
    def __init__(self, business: Business):
        self.business = business
        self.tenant_id = business.qbo_id
        self.business_id = business.business_id

    def _get_authenticated_client(self) -> Optional[str]:
        """Get a valid access token through centralized auth."""
        return qbo_auth.get_valid_token(self.business_id)

    def get_bills(self, db: Session, due_days: int = 14) -> List[Dict[str, Any]]:
        from domains.ap.models.bill import Bill
        today = datetime.utcnow().date()
        return [
            {"qbo_id": b.qbo_id, "vendor": b.vendor_id, "amount": b.amount, "due_date": b.due_date}
            for b in db.query(Bill).filter(
                Bill.business_id == self.business.business_id,
                Bill.due_date <= datetime.utcnow() + timedelta(days=due_days),
                Bill.status != "paid"
            ).all()
        ]

    def get_invoices(self, db: Session, aging_days: int = 30) -> List[Dict[str, Any]]:
        from domains.ar.models.invoice import Invoice
        today = datetime.utcnow().date()
        return [
            {"qbo_id": i.qbo_id, "customer": i.customer_id, "amount": i.total, "due_date": i.due_date, "aging_days": (today - i.due_date.date()).days}
            for i in db.query(Invoice).filter(
                Invoice.business_id == self.business.business_id,
                Invoice.due_date < datetime.utcnow() - timedelta(days=aging_days),
                Invoice.status != "paid"
            ).all()
        ]

    def get_vendors(self, db: Session) -> List[Dict[str, Any]]:
        """Get vendors from the database."""
        from domains.ap.models.vendor import Vendor
        return [
            {"qbo_id": v.qbo_vendor_id, "name": v.name, "is_active": v.is_active}
            for v in db.query(Vendor).filter(
                Vendor.business_id == self.business.business_id,
                Vendor.is_active == True
            ).all()
        ]

    def get_customers(self, db: Session) -> List[Dict[str, Any]]:
        """Get customers from the database."""
        from domains.ar.models.customer import Customer
        return [
            {"qbo_id": c.qbo_customer_id, "name": c.name, "is_active": c.is_active}
            for c in db.query(Customer).filter(
                Customer.business_id == self.business.business_id,
                Customer.is_active == True
            ).all()
        ]

    def fetch_balances(self, db: Session) -> List[Dict[str, Any]]:
        """Get account balances from the database."""
        # Mock QBO Balances API for Phase 0 - return list structure
        mock_balances = [
            {"AccountId": "123", "CurrentBalance": 6000.0, "AvailableBalance": 5500.0, "AccountType": "checking", "Date": "2025-09-15T00:00:00"},
            {"AccountId": "456", "CurrentBalance": 2000.0, "AvailableBalance": 1800.0, "AccountType": "savings", "Date": "2025-09-15T00:00:00"}
        ]
        
        # Ensure Balance records exist in database
        for bal in mock_balances:
            existing_balance = db.query(Balance).filter(
                Balance.business_id == self.business.business_id,
                Balance.qbo_account_id == bal["AccountId"]
            ).first()
            
            if not existing_balance:
                db.add(Balance(
                    business_id=self.business.business_id,
                    qbo_account_id=bal["AccountId"],
                    current_balance=bal["CurrentBalance"],
                    available_balance=bal["AvailableBalance"],
                    snapshot_date=datetime.fromisoformat(bal["Date"]),
                    account_type=bal["AccountType"]
                ))
        db.commit()
        
        # Return list of balance data
        return [
            {
                "account_id": bal["AccountId"],
                "current_balance": bal["CurrentBalance"],
                "available_balance": bal["AvailableBalance"],
                "account_type": bal["AccountType"]
            }
            for bal in mock_balances
        ]

    def handle_webhook(self, payload: Dict) -> str:
        return "OK"
