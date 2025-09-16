from intuitlib.client import AuthClient
from sqlalchemy.orm import Session
from domains.core.models.balance import Balance
from domains.core.models.business import Business
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import json
from dotenv import load_dotenv

load_dotenv()

class QBOIntegration:
    def __init__(self, business: Business):
        self.business = business
        self.tenant_id = business.qbo_id
        self.auth_client = AuthClient(
            os.getenv("QBO_CLIENT_ID"),
            os.getenv("QBO_CLIENT_SECRET"),
            os.getenv("QBO_REDIRECT_URI"),
            "sandbox"
        )

    def get_bills(self, db: Session, due_days: int = 14) -> List[Dict[str, Any]]:
        from domains.ap.models.bill import Bill
        today = datetime.utcnow().date()
        return [
            {"qbo_id": b.qbo_id, "vendor": b.vendor_id, "amount": b.amount, "due_date": b.due_date}
            for b in db.query(Bill).filter(
                Bill.business_id == self.business.client_id,
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
                Invoice.business_id == self.business.client_id,
                Invoice.due_date < datetime.utcnow() - timedelta(days=aging_days),
                Invoice.status != "paid"
            ).all()
        ]

    def fetch_balances(self, db: Session) -> None:
        # Mock QBO Balances API for Phase 0
        mock_balances = [
            {"AccountId": "123", "CurrentBalance": 6000.0, "AvailableBalance": 5500.0, "AccountType": "checking", "Date": "2025-09-15T00:00:00"},
            {"AccountId": "456", "CurrentBalance": 2000.0, "AvailableBalance": 1800.0, "AccountType": "savings", "Date": "2025-09-15T00:00:00"}
        ]
        for bal in mock_balances:
            db.add(Balance(
                business_id=self.business.client_id,
                qbo_account_id=bal["AccountId"],
                current_balance=bal["CurrentBalance"],
                available_balance=bal["AvailableBalance"],
                snapshot_date=datetime.fromisoformat(bal["Date"]),
                account_type=bal["AccountType"]
            ))
        db.commit()

    def handle_webhook(self, payload: Dict) -> str:
        return "OK"
