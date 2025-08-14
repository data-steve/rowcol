"""
Preamble: Implements BankTransactionService for Stage 1C of the Escher project.
Handles creation and listing of bank transactions with tenant isolation and policy engine integration.
Extends BankTransactionService for Stage 1C of the Escher project.
Adds transaction categorization functionality for Slice 2.
References: Stage 1C requirements, services/policy_engine.py, models/bank_transaction.py.
"""
from sqlalchemy.orm import Session
from models.bank_transaction import BankTransaction as BankTransactionModel
from schemas.bank_transaction import BankTransactionCreate, BankTransaction, BankTransactionCategorize
from services.policy_engine import PolicyEngineService
from typing import List, Optional

class BankTransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.policy_engine = PolicyEngineService(db)

    def create_transaction(self, transaction_data: BankTransactionCreate, firm_id: str, client_id: Optional[int] = None) -> BankTransactionModel:
        """
        Create a new bank transaction with tenant isolation and categorization.
        """
        try:
            # Validate firm_id
            if not firm_id:
                raise ValueError("firm_id is required")
            
            # Create transaction
            db_transaction = BankTransactionModel(
                firm_id=firm_id,
                client_id=client_id,
                amount=transaction_data.amount,
                date=transaction_data.date,
                description=transaction_data.description,
                account_id=transaction_data.account_id,
                source=transaction_data.source,
                status="pending"
            )
            
            # Categorize using policy engine
            # Permanent comment: This integration ensures transactions are categorized at creation,
            # linking to suggestions for auditability and compliance.
            suggestion = self.policy_engine.categorize(
                firm_id=firm_id,
                description=transaction_data.description,
                amount=transaction_data.amount,
                client_id=client_id
            )
            
            # Link suggestion
            db_transaction.suggestion_id = suggestion.suggestion_id
            db_transaction.confidence = suggestion.top_k[0]["confidence"] if suggestion.top_k else 0.0
            
            self.db.add(db_transaction)
            self.db.commit()
            self.db.refresh(db_transaction)
            return db_transaction
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Transaction creation failed: {str(e)}")

    def list_transactions(self, firm_id: str, client_id: Optional[int] = None) -> List[BankTransactionModel]:
        """
        List bank transactions with tenant isolation.
        """
        query = self.db.query(BankTransactionModel).filter(
            BankTransactionModel.firm_id == firm_id
        )
        
        if client_id:
            query = query.filter(BankTransactionModel.client_id == client_id)
            
        return query.all()

    def categorize_transaction(self, firm_id: str, categorize_data: BankTransactionCategorize) -> BankTransactionModel:
        """
        Categorize an existing bank transaction using the policy engine.
        """
        try:
            # Fetch transaction with tenant isolation
            transaction = self.db.query(BankTransactionModel).filter(
                BankTransactionModel.transaction_id == categorize_data.transaction_id,
                BankTransactionModel.firm_id == firm_id
            ).first()
            
            if not transaction:
                raise ValueError("Transaction not found or does not belong to firm")
            
            # Use provided description/amount or fall back to existing
            description = categorize_data.description or transaction.description
            amount = categorize_data.amount if categorize_data.amount is not None else transaction.amount
            
            # Categorize using policy engine
            # Permanent comment: This step re-applies rules to update categorization, ensuring compliance with firm-specific policies.
            suggestion = self.policy_engine.categorize(
                firm_id=firm_id,
                description=description,
                amount=amount,
                client_id=transaction.client_id
            )
            
            # Update transaction with new categorization
            transaction.suggestion_id = suggestion.suggestion_id
            transaction.confidence = suggestion.top_k[0]["confidence"] if suggestion.top_k else 0.0
            transaction.account_id = suggestion.top_k[0]["account"] if suggestion.top_k else transaction.account_id
            
            self.db.commit()
            self.db.refresh(transaction)
            return transaction
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Transaction categorization failed: {str(e)}")