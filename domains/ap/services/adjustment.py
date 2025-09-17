from typing import Optional
from sqlalchemy.orm import Session
from quickbooks import QuickBooks
from quickbooks.objects import CreditMemo as QBOCreditMemo
from domains.ar.models.credit_memo import CreditMemo as CreditMemoModel
from domains.ar.schemas.credit_memo import CreditMemo
from config.business_rules import AdjustmentSettings
import os
from dotenv import load_dotenv

load_dotenv()

class AdjustmentService:
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

    def create_credit_memo(self, firm_id: str, invoice_id: int, amount: float, reason: str, client_id: Optional[int] = None) -> CreditMemo:
        """Create a credit memo for an invoice."""
        try:
            credit_memo = CreditMemoModel(
                firm_id=firm_id,
                client_id=client_id,
                invoice_id=invoice_id,
                amount=amount,
                reason=reason,
                status="review" if amount > AdjustmentSettings.REVIEW_THRESHOLD_AMOUNT else "applied"
            )
            self.db.add(credit_memo)
            
            # Sync with QBO (if client is configured)
            try:
                qbo_credit_memo = QBOCreditMemo()
                qbo_credit_memo.CustomerRef = {"value": str(invoice_id)}
                qbo_credit_memo.TotalAmt = amount
                qbo_credit_memo.save(qb=self.qbo_client)
                credit_memo.qbo_id = qbo_credit_memo.Id
            except Exception as e:
                # QBO sync failed, but we can still create the credit memo
                print(f"QBO sync failed: {e}")
                credit_memo.qbo_id = None
            
            self.db.commit()
            self.db.refresh(credit_memo)
            return credit_memo
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Credit memo creation failed: {str(e)}")