"""
Bank domain routes for transaction management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from domains.bank.schemas.bank_transaction import BankTransactionCreate, BankTransaction
from domains.bank.schemas.transfer import TransferCreate
from domains.bank.services.bank_transaction import BankTransactionService
from domains.bank.schemas.bank_transaction import BankTransactionCategorize

router = APIRouter()

@router.post("/transactions", response_model=BankTransaction)
def create_transaction(
    transaction: BankTransactionCreate,
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    service = BankTransactionService(db)
    return service.create_transaction(transaction, firm_id, client_id)

@router.get("/transactions", response_model=List[BankTransaction])
def list_transactions(
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    service = BankTransactionService(db)
    return service.list_transactions(firm_id, client_id)

@router.post("/transactions/categorize")
def categorize_transaction(
    categorize_data: BankTransactionCategorize,
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    service = BankTransactionService(db)
    return service.categorize_transaction(firm_id, categorize_data)

@router.post("/transfers")
def create_transfer(
    transfer_data: TransferCreate,
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    service = BankTransactionService(db)
    return service.create_transfer(firm_id, client_id)

@router.get("/transfers")
def detect_transfers(
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    service = BankTransactionService(db)
    return service.detect_transfers(firm_id, client_id)
