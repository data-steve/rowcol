"""
Payroll domain routes for batch management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from domains.payroll.schemas.payroll import PayrollBatchCreate, PayrollBatch, PayrollRemittanceCreate
from domains.payroll.services.payroll import PayrollService

router = APIRouter()

@router.post("/batches", response_model=PayrollBatch)
def create_batch(
    batch: PayrollBatchCreate,
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    service = PayrollService(db)
    return service.create_batch(batch, firm_id, client_id)

@router.post("/remittances")
def create_remittance(
    remittance: PayrollRemittanceCreate,
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    service = PayrollService(db)
    return service.create_remittance(remittance, firm_id)

@router.post("/batches/{batch_id}/reconcile")
def reconcile_batch(
    batch_id: int,
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    service = PayrollService(db)
    return service.reconcile_batch(firm_id, batch_id, client_id)
