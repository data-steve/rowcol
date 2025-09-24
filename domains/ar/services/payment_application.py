"""
Payment Application Service for AR domain.
Handles payment application to invoices with tenant isolation.
"""
from sqlalchemy.orm import Session
from domains.ar.models.payment import Payment as PaymentModel
from datetime import datetime
from typing import Optional

class PaymentApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def apply_payment(self, business_id: int, amount: float, date: datetime, method: str, customer_id: Optional[int] = None) -> PaymentModel:
        """
        Apply a payment to invoices with tenant isolation.
        """
        try:
            # Create payment record
            payment = PaymentModel(
                business_id=business_id,
                customer_id=customer_id,
                amount=amount,
                payment_date=date,
                payment_method=method,
                status="matched"  # AR payments use "matched" status
            )
            
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)
            return payment
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Payment application failed: {str(e)}")

    def get_payment(self, payment_id: int, business_id: int) -> PaymentModel:
        """
        Get payment by ID with tenant isolation.
        """
        payment = self.db.query(PaymentModel).filter(
            PaymentModel.payment_id == payment_id,
            PaymentModel.business_id == business_id
        ).first()
        
        if not payment:
            raise ValueError("Payment not found or does not belong to business")
        
        return payment
