"""
AR Invoices routes.
Handles invoice creation and management for AR domain.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from infra.database.session import get_db
from domains.ar.services.invoice import InvoiceService
from datetime import datetime

router = APIRouter()

@router.post("/invoices")
def create_invoice(invoice_data: dict, business_id: str, db: Session = Depends(get_db)):
    service = InvoiceService(db, business_id)
    return service.create_invoice(
        business_id=business_id,
        customer_id=invoice_data["customer_id"],
        issue_date=datetime.fromisoformat(invoice_data["issue_date"].replace('Z', '+00:00')),
        due_date=datetime.fromisoformat(invoice_data["due_date"].replace('Z', '+00:00')),
        total=invoice_data["total"],
        lines=invoice_data["lines"]
    )

@router.get("/")
def get_invoices(business_id: int, db: Session = Depends(get_db)):
    service = InvoiceService(db, str(business_id))
    return service.sync_invoices(business_id)

@router.post("/collections/remind")
def send_collection_reminder(business_id: str, invoice_id: str, db: Session = Depends(get_db)):
    """Send collection reminder using CollectionsService."""
    from domains.ar.services.collections import CollectionsService
    
    try:
        collections_service = CollectionsService(db, business_id)
        result = collections_service.send_reminder(invoice_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send reminder: {str(e)}")
