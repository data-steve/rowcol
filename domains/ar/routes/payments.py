"""
AR Payments routes.
Handles payment application for AR domain.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from domains.ar.services.payment_application import PaymentApplicationService
from domains.ar.services.adjustment import AdjustmentService
from datetime import datetime

router = APIRouter()

@router.post("/payments/apply")
def apply_payment(payment_data: dict, business_id: str, db: Session = Depends(get_db)):
    service = PaymentApplicationService(db, business_id)
    return service.apply_payment(
        business_id=business_id,
        amount=payment_data["amount"],
        date=datetime.fromisoformat(payment_data["date"].replace('Z', '+00:00')),
        method=payment_data["method"],
        customer_id=payment_data.get("customer_id")
    )

@router.post("/credits")
def create_credit_memo(credit_data: dict, business_id: str, db: Session = Depends(get_db)):
    service = AdjustmentService(db, business_id)
    return service.create_credit_memo(
        business_id=business_id,
        invoice_id=credit_data["invoice_id"],
        amount=credit_data["amount"],
        reason=credit_data["reason"]
    )
