from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.invoice import InvoiceService
from services.collections import CollectionsService
from services.payment_application import PaymentApplicationService
from services.adjustment import AdjustmentService
from schemas.invoice import Invoice, InvoiceCreate
from schemas.payment import Payment, PaymentCreate
from schemas.credit_memo import CreditMemo, CreditMemoCreate
from models.invoice import Invoice as InvoiceModel
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_db

class InvoiceCreateRequest(BaseModel):
    customer_id: int
    issue_date: datetime
    due_date: datetime
    total: float
    lines: Optional[list] = None

router = APIRouter(prefix="/api/ar", tags=["AR"])

@router.post("/invoices", response_model=Invoice)
async def create_invoice(request: InvoiceCreateRequest, firm_id: str, client_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Create an invoice."""
    service = InvoiceService(db)
    try:
        return service.create_invoice(
            firm_id, request.customer_id, request.issue_date, request.due_date, request.total, request.lines, client_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/invoices/{id}", response_model=Invoice)
async def get_invoice(id: int, firm_id: str, db: Session = Depends(get_db)):
    """Get invoice details."""
    invoice = db.query(InvoiceModel).filter(InvoiceModel.invoice_id == id, InvoiceModel.firm_id == firm_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.patch("/invoices/{id}", response_model=Invoice)
async def update_invoice(id: int, firm_id: str, status: Optional[str] = None, db: Session = Depends(get_db)):
    """Update invoice status."""
    invoice = db.query(InvoiceModel).filter(InvoiceModel.invoice_id == id, InvoiceModel.firm_id == firm_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if status:
        invoice.status = status
    db.commit()
    db.refresh(invoice)
    return invoice

@router.post("/collections/remind", response_model=Invoice)
async def send_reminder(invoice_id: int, firm_id: str, client_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Send a reminder for an overdue invoice."""
    service = CollectionsService(db)
    try:
        return service.send_reminder(firm_id, invoice_id, client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/payments/apply", response_model=Payment)
async def apply_payment(request: PaymentCreate, firm_id: str, client_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Apply a payment to invoices."""
    service = PaymentApplicationService(db)
    try:
        return service.apply_payment(
            firm_id, request.amount, request.date, request.method, request.customer_id, client_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/credits", response_model=CreditMemo)
async def create_credit_memo(request: CreditMemoCreate, firm_id: str, client_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Create a credit memo."""
    service = AdjustmentService(db)
    try:
        return service.create_credit_memo(firm_id, request.invoice_id, request.amount, request.reason, client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))