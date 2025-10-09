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

# REMOVED: create_invoice endpoint - moved to _parked/runway/routes/invoice_execution.py
# QBO is only a ledger rail - it cannot create invoices
# Invoice creation moved to _parked/ for future Stripe implementation

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
