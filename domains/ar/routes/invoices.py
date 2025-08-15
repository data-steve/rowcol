"""
AR Invoices routes.
Handles invoice creation and management for AR domain.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from domains.ar.models.invoice import Invoice as InvoiceModel
from domains.ar.schemas.invoice import InvoiceCreate, Invoice
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/invoices", response_model=Invoice)
def create_invoice(
    invoice: InvoiceCreate,
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    """Create a new invoice."""
    try:
        db_invoice = InvoiceModel(
            firm_id=firm_id,
            client_id=client_id,
            customer_id=invoice.customer_id,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            total=invoice.total,
            lines=invoice.lines,
            status="draft"
        )
        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)
        return db_invoice
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create invoice: {str(e)}")

@router.get("/invoices", response_model=List[Invoice])
def list_invoices(
    firm_id: str,
    client_id: str = None,
    db: Session = Depends(get_db)
):
    """List invoices for a firm."""
    query = db.query(InvoiceModel).filter(InvoiceModel.firm_id == firm_id)
    if client_id:
        query = query.filter(InvoiceModel.client_id == client_id)
    return query.all()
