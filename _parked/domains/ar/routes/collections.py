"""
AR Collections routes.
Handles collections and reminders for AR domain.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from domains.ar.services.collections import CollectionsService

router = APIRouter()

@router.post("/collections/remind")
def send_reminder(
    firm_id: str,
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Send a reminder for an overdue invoice."""
    try:
        service = CollectionsService(db)
        invoice = service.send_reminder(firm_id, invoice_id)
        return {"message": "Reminder sent", "invoice_id": invoice_id, "firm_id": firm_id, "status": invoice.status}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send reminder: {str(e)}")
