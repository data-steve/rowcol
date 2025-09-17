"""
AR Payments routes.
Handles payment application for AR domain.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from domains.ar.services.payment_application import PaymentApplicationService

router = APIRouter()

@router.post("/")
def apply_payment(payment_data: dict, db: Session = Depends(get_db)):
    service = PaymentApplicationService(db)
    return service.apply_payment(**payment_data)
