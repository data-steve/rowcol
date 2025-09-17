"""
AR Invoices routes.
Handles invoice creation and management for AR domain.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from domains.ar.services.invoice import InvoiceService

router = APIRouter()

@router.post("/")
def create_invoice(invoice_data: dict, db: Session = Depends(get_db)):
    service = InvoiceService(db)
    return service.create_invoice(**invoice_data)

@router.get("/")
def get_invoices(business_id: int, db: Session = Depends(get_db)):
    service = InvoiceService(db)
    return service.sync_invoices(business_id)
