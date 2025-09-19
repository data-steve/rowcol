from sqlalchemy.orm import Session
from domains.bank.models import BankTransaction
from domains.policy.services.policy_engine import PolicyEngineService
from domains.bank.schemas.bank_transaction import BankTransactionCreate, BankTransactionCategorize
from fastapi import HTTPException
from typing import List

class BankTransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.policy_engine = PolicyEngineService(db)

    def create_transaction(self, transaction_data: BankTransactionCreate, firm_id: str, client_id: str = None) -> BankTransaction:
        """Create a new bank transaction."""
        transaction = BankTransaction(
            amount=transaction_data.amount,
            date=transaction_data.date,
            description=transaction_data.description,
            source=transaction_data.source,
            firm_id=firm_id,
            client_id=client_id
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def list_transactions(self, firm_id: str, client_id: str = None) -> List[BankTransaction]:
        """List bank transactions with tenant isolation."""
        query = self.db.query(BankTransaction).filter_by(firm_id=firm_id)
        if client_id:
            query = query.filter_by(client_id=client_id)
        return query.all()

    def categorize_transaction(self, categorize_data: BankTransactionCategorize, firm_id: str) -> dict:
        """Categorize a bank transaction."""
        transaction = self.db.query(BankTransaction).filter_by(
            id=categorize_data.transaction_id,
            firm_id=firm_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Simple categorization logic
        category = "Office Expenses"  # Default category
        if "starbucks" in transaction.description.lower():
            category = "Meals & Entertainment"
        elif "gas" in transaction.description.lower():
            category = "Travel"
        
        return {
            "transaction_id": transaction.id,
            "category": category,
            "confidence": 0.8
        }

    def process_transaction(self, transaction_id: int):
        """Legacy method for processing transactions."""
        transaction = self.db.query(BankTransaction).filter_by(id=transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        # Apply policy engine rules (placeholder)
        result = self.policy_engine.apply_rules(transaction)
        self.db.commit()
        return {"status": "processed", "transaction_id": transaction_id, "result": result}
