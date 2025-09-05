from typing import List, Optional
from sqlalchemy.orm import Session
from domains.bank.models.bank_transaction import BankTransaction
from domains.ar.models.invoice import Invoice

class TrayService:
    def __init__(self, db: Session):
        self.db = db

    def get_tray_items(self, firm_id: str) -> List[dict]:
        unmatched = self.db.query(BankTransaction).filter(
            BankTransaction.firm_id == firm_id,
            BankTransaction.status == "pending"
        ).all()
        return [
            {
                "id": t.transaction_id,
                "amount": t.amount,
                "description": t.description,
                "suggested_action": t.unbundle_meta.get("suggested_action", "manual_investigation") if t.unbundle_meta else "manual_investigation",
                "confidence": t.confidence
            } for t in unmatched
        ]

    def confirm_action(self, firm_id: str, transaction_id: int, action: str, invoice_ids: Optional[List[int]] = None):
        transaction = self.db.query(BankTransaction).filter(
            BankTransaction.firm_id == firm_id,
            BankTransaction.transaction_id == transaction_id
        ).first()
        if not transaction:
            raise ValueError("Transaction not found")

        if action == "confirm":
            transaction.status = "matched"
            transaction.invoice_ids = invoice_ids or []
        elif action == "split":
            # Placeholder for split logic
            pass

        self.db.commit()
        return transaction
