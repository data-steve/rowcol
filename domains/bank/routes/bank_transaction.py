"""
Bank Transaction Routes for Oodaloo

PURPOSE: Simple bank transaction management for single business owners
- Import bank transactions from QBO
- Basic categorization for cash flow tracking
- Cash flow summaries for runway calculations

SCOPE: Oodaloo Phase 2-3 (single business owner)
NOT: Multi-client allocation, complex automation (that's RowCol - see _parked/)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from domains.bank.services.bank_transaction import BankTransactionService
from domains.bank.schemas.bank_transaction import (
    BankTransactionResponse, 
    BankTransactionCategorize,
    CashFlowSummary
)
from runway.infrastructure.middleware.auth import get_current_business_id

router = APIRouter()

@router.get("/transactions", response_model=List[BankTransactionResponse])
def get_recent_transactions(
    limit: int = 50,
    business_id: str = Depends(get_current_business_id),
    db: Session = Depends(get_db)
):
    """Get recent bank transactions for cash flow review."""
    service = BankTransactionService(db, business_id)
    transactions = service.get_recent_transactions(limit)
    return transactions

@router.get("/transactions/uncategorized", response_model=List[BankTransactionResponse])
def get_uncategorized_transactions(
    business_id: str = Depends(get_current_business_id),
    db: Session = Depends(get_db)
):
    """Get transactions that need categorization."""
    service = BankTransactionService(db, business_id)
    transactions = service.get_uncategorized_transactions()
    return transactions

@router.patch("/transactions/{transaction_id}/categorize")
def categorize_transaction(
    transaction_id: str,
    categorize_data: BankTransactionCategorize,
    business_id: str = Depends(get_current_business_id),
    db: Session = Depends(get_db)
):
    """Categorize a bank transaction."""
    service = BankTransactionService(db, business_id)
    try:
        transaction = service.categorize_transaction(transaction_id, categorize_data.category)
        return {"success": True, "transaction_id": transaction.id, "category": transaction.category}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/cash-flow-summary", response_model=CashFlowSummary)
def get_cash_flow_summary(
    days: int = 30,
    business_id: str = Depends(get_current_business_id),
    db: Session = Depends(get_db)
):
    """Get cash flow summary for runway calculations."""
    service = BankTransactionService(db, business_id)
    summary = service.get_cash_flow_summary(days)
    return summary

# TODO: Phase 3 - QBO Integration Routes
# @router.post("/import-from-qbo")
# def import_from_qbo(business_id: str = Depends(get_current_business_id), db: Session = Depends(get_db)):
#     """Import latest transactions from QBO bank feeds."""
#     service = BankTransactionService(db, business_id)
#     # TODO: Integrate with QBO API
#     pass

# PARKED for RowCol:
# - Multi-client transaction allocation
# - Complex automation and rules
# - Transfer detection across accounts
# - Approval workflows
