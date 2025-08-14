from typing import List, Optional
from sqlalchemy.orm import Session
from quickbooks import QuickBooks
from quickbooks.objects import Payment as QBOPayment
from models.payment import Payment as PaymentModel
from models.invoice import Invoice as InvoiceModel
from schemas.payment import Payment
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class PaymentApplicationService:
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

    def apply_payment(self, firm_id: str, amount: float, date: datetime, method: str, customer_id: int, client_id: Optional[int] = None) -> Payment:
        """Apply a payment to matching invoices."""
        try:
            # Find matching invoices
            invoices = self.db.query(InvoiceModel).filter(
                InvoiceModel.firm_id == firm_id,
                InvoiceModel.customer_id == customer_id,
                InvoiceModel.status != "paid",
                InvoiceModel.total <= amount
            ).all()
            
            invoice_ids = [inv.invoice_id for inv in invoices]
            if not invoice_ids:
                raise ValueError("No matching invoices found")
            
            payment = PaymentModel(
                firm_id=firm_id,
                client_id=client_id,
                invoice_ids=invoice_ids,
                amount=amount,
                date=date,
                method=method
            )
            self.db.add(payment)
            
            # Sync with QBO (if client is configured)
            try:
                qbo_payment = QBOPayment()
                qbo_payment.CustomerRef = {"value": str(customer_id)}
                qbo_payment.TotalAmt = amount
                qbo_payment.Line = [{"Amount": inv.total, "LinkedTxn": [{"TxnId": inv.qbo_id, "TxnType": "Invoice"}]} for inv in invoices]
                qbo_payment.save(qb=self.qbo_client)
                payment.qbo_id = qbo_payment.Id
            except Exception as e:
                # QBO sync failed, but we can still create the payment
                print(f"QBO sync failed: {e}")
                payment.qbo_id = None
            
            for inv in invoices:
                inv.status = "paid"
            
            self.db.commit()
            self.db.refresh(payment)
            return payment
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Payment application failed: {str(e)}")