"""
Bank Transaction Service for Oodaloo

PURPOSE: Handle bank feed transactions for single business owners
- Import bank transactions from QBO bank feeds
- Simple expense categorization for cash flow tracking
- Support runway calculations with actual bank data

SCOPE: Oodaloo Phase 2-3 (single business owner)
NOT: Multi-client expense allocation (that's RowCol complexity - see _parked/)
"""

from sqlalchemy.orm import Session
from domains.bank.models import BankTransaction
from domains.core.services.base_service import TenantAwareService
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class BankTransactionService(TenantAwareService):
    """
    Simple bank transaction service for Oodaloo business owners.
    
    Core Use Cases:
    1. Import bank transactions from QBO bank feeds
    2. Basic expense categorization (Office, Travel, etc.)
    3. Cash flow tracking for runway calculations
    4. Simple transaction search and filtering
    """
    
    def __init__(self, db: Session, business_id: str, validate_business: bool = True):
        super().__init__(db, business_id, validate_business)
    
    def import_from_qbo(self, qbo_transactions: List[dict]) -> List[BankTransaction]:
        """
        Import bank transactions from QBO bank feeds.
        
        Phase 3: Replace with real QBO API integration
        Phase 1-2: Mock data for development
        """
        imported_transactions = []
        
        for qbo_txn in qbo_transactions:
            transaction = BankTransaction(
                business_id=self.business_id,
                qbo_transaction_id=qbo_txn.get('Id'),
                amount_cents=int(Decimal(str(qbo_txn['Amount'])) * 100),
                description=qbo_txn.get('Description', ''),
                transaction_date=datetime.fromisoformat(qbo_txn['Date']),
                account_name=qbo_txn.get('AccountName', ''),
                source='qbo_bank_feed'
            )
            
            self.db.add(transaction)
            imported_transactions.append(transaction)
        
        self.db.commit()
        return imported_transactions
    
    def get_recent_transactions(self, limit: int = 50) -> List[BankTransaction]:
        """Get recent transactions for cash flow review."""
        return self.db.query(BankTransaction)\
            .filter_by(business_id=self.business_id)\
            .order_by(BankTransaction.transaction_date.desc())\
            .limit(limit)\
            .all()
    
    def get_uncategorized_transactions(self) -> List[BankTransaction]:
        """Get transactions that need categorization."""
        return self.db.query(BankTransaction)\
            .filter_by(business_id=self.business_id, category=None)\
            .order_by(BankTransaction.transaction_date.desc())\
            .all()
    
    def categorize_transaction(self, transaction_id: str, category: str) -> BankTransaction:
        """
        Simple transaction categorization for business owners.
        
        Categories: Office, Travel, Marketing, Equipment, etc.
        NOT: Complex GL account mapping (that's RowCol complexity)
        """
        transaction = self.db.query(BankTransaction)\
            .filter_by(id=transaction_id, business_id=self.business_id)\
            .first()
        
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        transaction.category = category
        self.db.commit()
        return transaction
    
    def get_cash_flow_summary(self, days: int = 30) -> dict:
        """
        Get cash flow summary for runway calculations.
        
        Returns simple in/out totals, not complex P&L analysis.
        """
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        transactions = self.db.query(BankTransaction)\
            .filter_by(business_id=self.business_id)\
            .filter(BankTransaction.transaction_date >= start_date)\
            .all()
        
        total_in = sum(t.amount_cents for t in transactions if t.amount_cents > 0)
        total_out = sum(abs(t.amount_cents) for t in transactions if t.amount_cents < 0)
        
        return {
            'period_days': days,
            'total_in_cents': total_in,
            'total_out_cents': total_out,
            'net_flow_cents': total_in - total_out,
            'transaction_count': len(transactions)
        }

# TODO: Phase 3 - QBO Bank Feed Integration
# - Real-time bank feed imports via QBO API
# - Automatic transaction deduplication
# - Bank account reconciliation helpers

# TODO: Phase 2 - Smart Categorization  
# - Simple ML-based category suggestions
# - Learn from user's categorization patterns
# - Common expense pattern recognition

# PARKED for RowCol:
# - Multi-client transaction allocation
# - Complex GL account mapping
# - Audit trail and approval workflows
# - Cross-client expense reporting