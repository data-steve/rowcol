"""
AR Payments routes.
Handles payment application for AR domain.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from domains.ar.services.payment_application import PaymentApplicationService
from domains.ar.schemas.payment_application import PaymentApplicationCreate
from datetime import datetime

router = APIRouter()

@router.post("/payments/apply")
def apply_payment(
    payment: PaymentApplicationCreate,
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    """Apply a payment to invoices."""
    try:
        service = PaymentApplicationService(db)
        result = service.apply_payment(
            firm_id=firm_id,
            amount=payment.amount,
            date=payment.date,
            method=payment.method,
            customer_id=payment.customer_id
        )
        return {"message": "Payment applied successfully", "payment_id": result.payment_id}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to apply payment: {str(e)}")
