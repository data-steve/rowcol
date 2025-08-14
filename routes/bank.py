"""
Bank routes for Stage 1C - now with working routing
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.bank_transaction import BankTransactionService
from services.transfer import TransferService
from schemas.bank_transaction import BankTransaction, BankTransactionCreate, BankTransactionCategorize
from schemas.transfer import Transfer, TransferCreate
from database import get_db
from typing import List, Optional

router = APIRouter(prefix="/api/bank", tags=["Bank Transactions", "Transfers"])

@router.post("/transactions", response_model=BankTransaction)
async def create_transaction(
    transaction: BankTransactionCreate,
    firm_id: str,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Create a new bank transaction with tenant isolation."""
    try:
        service = BankTransactionService(db)
        return service.create_transaction(transaction, firm_id, client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions", response_model=List[BankTransaction])
async def list_transactions(
    firm_id: str,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List bank transactions with tenant isolation."""
    service = BankTransactionService(db)
    return service.list_transactions(firm_id, client_id)

@router.post("/transactions/categorize", response_model=BankTransaction)
async def categorize_transaction(
    categorize_data: BankTransactionCategorize,
    firm_id: str,
    db: Session = Depends(get_db)
):
    """Categorize an existing bank transaction with tenant isolation."""
    try:
        service = BankTransactionService(db)
        return service.categorize_transaction(firm_id, categorize_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/transfers", response_model=Transfer)
async def create_transfer(
    transfer: TransferCreate,
    firm_id: str,
    db: Session = Depends(get_db)
):
    """Create a new transfer linking two bank transactions."""
    try:
        service = TransferService(db)
        return service.create_transfer(transfer, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transfers", response_model=List[Transfer])
async def detect_transfers(
    firm_id: str,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Detect and return potential transfers with tenant isolation."""
    try:
        service = TransferService(db)
        return service.detect_transfers(firm_id, client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
