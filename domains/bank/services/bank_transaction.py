from sqlalchemy.orm import Session
from domains.ap.services.bill_ingestion import BillIngestionService
from domains.bank.models import BankTransaction
from domains.policy.services.policy_engine import PolicyEngineService
from fastapi import HTTPException

class BankTransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.policy_engine = PolicyEngineService(db)

    def process_transaction(self, transaction_id: int):
        transaction = self.db.query(BankTransaction).filter_by(id=transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        # Apply policy engine rules (placeholder)
        result = self.policy_engine.apply_rules(transaction)
        self.db.commit()
        return {"status": "processed", "transaction_id": transaction_id, "result": result}
