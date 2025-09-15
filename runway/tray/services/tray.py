from typing import List, Optional
from sqlalchemy.orm import Session
from domains.bank.models.bank_transaction import BankTransaction
from domains.ar.models.invoice import Invoice
from runway.tray.models.tray_item import TrayItem
from datetime import datetime, timedelta

class TrayService:
    def __init__(self, db: Session):
        self.db = db

    def get_tray_items(self, business_id: int) -> List[dict]:
        items = self.db.query(TrayItem).filter(
            TrayItem.business_id == business_id,
            TrayItem.status == "pending"
        ).all()
        return [
            {
                "id": t.id,
                "type": t.type,
                "qbo_id": t.qbo_id,
                "status": t.status,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None
            } for t in items
        ]

    def confirm_action(self, business_id: int, tray_item_id: int, action: str, invoice_ids: Optional[List[int]] = None):
        item = self.db.query(TrayItem).filter(
            TrayItem.business_id == business_id,
            TrayItem.id == tray_item_id
        ).first()
        if not item:
            raise ValueError("Tray item not found")
        if action == "confirm":
            item.status = "resolved"
            # Link to invoices if provided
        elif action == "split":
            pass
        self.db.commit()
        return item
