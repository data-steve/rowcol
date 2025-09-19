"""
Preamble: Implements TransferService for Stage 1C of the Escher project.
Handles transfer detection and creation with tenant isolation.
References: Stage 1C requirements, models/transfer.py, services/bank_transaction.py.
"""
from sqlalchemy.orm import Session
from domains.bank.models.transfer import Transfer as TransferModel
from domains.bank.models.bank_transaction import BankTransaction as BankTransactionModel
from domains.bank.schemas.transfer import TransferCreate
from typing import List

class TransferService:
    def __init__(self, db: Session):
        self.db = db

    def create_transfer(self, transfer_data: TransferCreate, business_id: int) -> TransferModel:
        """
        Create a new transfer linking two bank transactions with tenant isolation.
        """
        try:
            # Validate business_id
            if not business_id:
                raise ValueError("business_id is required")
            
            # Validate transactions exist and belong to business
            source_txn = self.db.query(BankTransactionModel).filter(
                BankTransactionModel.transaction_id == transfer_data.source_transaction_id,
                BankTransactionModel.business_id == business_id
            ).first()
            
            destination_txn = self.db.query(BankTransactionModel).filter(
                BankTransactionModel.transaction_id == transfer_data.destination_transaction_id,
                BankTransactionModel.business_id == business_id
            ).first()
            
            if not source_txn or not destination_txn:
                raise ValueError("One or both transactions not found or do not belong to business")
            
            # Validate amount consistency
            if abs(source_txn.amount) != abs(transfer_data.amount) or abs(destination_txn.amount) != abs(transfer_data.amount):
                raise ValueError("Transfer amount must match transaction amounts")
            
            # Create transfer
            db_transfer = TransferModel(
                business_id=business_id,
                source_transaction_id=transfer_data.source_transaction_id,
                destination_transaction_id=transfer_data.destination_transaction_id,
                amount=transfer_data.amount,
                date=transfer_data.date,
                description=transfer_data.description
            )
            
            self.db.add(db_transfer)
            self.db.commit()
            self.db.refresh(db_transfer)
            return db_transfer
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Transfer creation failed: {str(e)}")

    def detect_transfers(self, business_id: int) -> List[TransferModel]:
        """
        Detect potential transfers by matching equal and opposite transactions.
        """
        try:
            # Query transactions with tenant isolation
            query = self.db.query(BankTransactionModel).filter(
                BankTransactionModel.business_id == business_id,
                BankTransactionModel.status == "pending"
            )
            
            transactions = query.all()
            
            transfers = []
            # Permanent comment: This simple matching algorithm checks for equal and opposite amounts
            # within a 7-day window, suitable for basic transfer detection. Enhance with ML for production.
            for i, txn1 in enumerate(transactions):
                for txn2 in transactions[i+1:]:
                    if (
                        abs(txn1.amount) == abs(txn2.amount) and
                        txn1.amount == -txn2.amount and
                        abs((txn1.date - txn2.date).days) <= 7
                    ):
                        transfer = TransferModel(
                            business_id=business_id,
                            source_transaction_id=txn1.transaction_id,
                            destination_transaction_id=txn2.transaction_id,
                            amount=abs(txn1.amount),
                            date=min(txn1.date, txn2.date),
                            description=f"Transfer between {txn1.description} and {txn2.description}"
                        )
                        transfers.append(transfer)
            
            for transfer in transfers:
                self.db.add(transfer)
            self.db.commit()
            
            return transfers
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Transfer detection failed: {str(e)}")