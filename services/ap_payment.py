from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from quickbooks import QuickBooks
from quickbooks.objects import Payment, Bill
from models.payment_intent import PaymentIntent as PaymentIntentModel
from models.bill import Bill as BillModel
from schemas.payment_intent import PaymentIntent
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class APPaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.qbo_client = QuickBooks(
            sandbox=True,
            consumer_key=os.getenv("QBO_CLIENT_ID"),
            consumer_secret=os.getenv("QBO_CLIENT_SECRET"),
            access_token=os.getenv("QBO_ACCESS_TOKEN"),
            access_token_secret=os.getenv("QBO_REFRESH_TOKEN"),
            company_id=os.getenv("QBO_REALM_ID")
        )

    def schedule_payment(self, firm_id: str, bill_ids: List[int], funding_account: str, client_id: Optional[int] = None) -> PaymentIntent:
        """Schedule a payment for bills via QBO."""
        try:
            bills = self.db.query(BillModel).filter(BillModel.bill_id.in_(bill_ids), BillModel.firm_id == firm_id).all()
            if not bills:
                raise ValueError("No valid bills found")
            
            total_amount = sum(bill.amount for bill in bills)
            payment_intent = PaymentIntentModel(
                firm_id=firm_id,
                client_id=client_id,
                bill_ids=bill_ids,  # Direct assignment for JSON field
                provider="qbo",
                total_amount=total_amount,
                funding_account=funding_account,
                status="pending",
                issued_at=datetime.utcnow()
            )
            self.db.add(payment_intent)
            
            # Create QBO payment
            qbo_payment = Payment()
            qbo_payment.TotalAmt = total_amount
            qbo_payment.CustomerRef = {"value": bills[0].vendor_id} if bills[0].vendor_id else None
            qbo_payment.Line = [{"Amount": bill.amount, "LinkedTxn": [{"TxnId": bill.qbo_bill_id, "TxnType": "Bill"}]} for bill in bills]
            qbo_payment.save(qb=self.qbo_client)
            
            payment_intent.status = "issued"
            for bill in bills:
                bill.status = "paid"
            
            self.db.commit()
            self.db.refresh(payment_intent)
            return payment_intent
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Payment scheduling failed: {str(e)}")