from typing import Dict, Optional
from sqlalchemy.orm import Session
from domains.ap.models.vendor_statement import VendorStatement as VendorStatementModel
from domains.ap.schemas.vendor_statement import VendorStatement
from quickbooks import QuickBooks
import os
from dotenv import load_dotenv
import json
from datetime import date

load_dotenv()

class StatementReconciliationService:
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

    def reconcile_statement(self, firm_id: str, vendor_id: int, file_ref: str, period: date, client_id: Optional[int] = None) -> VendorStatement:
        """Reconcile a vendor statement (mocked for now)."""
        try:
            # Mock statement parsing
            parsed_invoices = [
                {"invoice_no": "INV123", "amount": 100.0, "date": "2025-08-01"},
                {"invoice_no": "INV124", "amount": 200.0, "date": "2025-08-02"}
            ]
            
            # Fetch QBO aging report (simplified)
            qbo_bills = self.qbo_client.query("SELECT * FROM Bill WHERE VendorRef = '{}'".format(vendor_id))
            qbo_invoices = [{"invoice_no": bill.Id, "amount": bill.TotalAmt, "date": str(bill.DueDate)} for bill in qbo_bills]
            
            # Compare for mismatches
            mismatches = [
                {"invoice_no": inv["invoice_no"], "status": "missing in QBO"}
                for inv in parsed_invoices
                if inv["invoice_no"] not in [q["invoice_no"] for q in qbo_invoices]
            ]
            
            statement = VendorStatementModel(
                firm_id=firm_id,
                client_id=client_id,
                vendor_id=vendor_id,
                period=period,
                file_ref=file_ref,
                parsed_invoices=parsed_invoices,
                mismatches=mismatches
            )
            self.db.add(statement)
            self.db.commit()
            self.db.refresh(statement)
            return statement
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Statement reconciliation failed: {str(e)}")