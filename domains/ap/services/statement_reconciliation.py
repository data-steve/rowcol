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

    def reconcile_statement(self, firm_id: str, vendor_id: int, file_ref: str, 
                           period: date, client_id: Optional[int] = None, 
                           parsed_invoices: list = None) -> VendorStatement:
        """Reconcile a vendor statement with QBO data."""
        try:
            # Use provided parsed invoices or mock data for development
            if not parsed_invoices:
                # Mock statement parsing - replace with actual PDF/document parsing
                parsed_invoices = self._parse_statement_mock(file_ref)
            
            # Fetch QBO aging report
            qbo_invoices = self._fetch_qbo_bills(vendor_id)
            
            # Compare for mismatches
            mismatches = self._find_reconciliation_mismatches(parsed_invoices, qbo_invoices)
            
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
    
    def _parse_statement_mock(self, file_ref: str) -> list:
        """Mock statement parsing - replace with actual PDF/document parsing."""
        # TODO: Implement actual statement parsing logic
        return [
            {"invoice_no": f"INV{hash(file_ref) % 1000}", "amount": 100.0, "date": "2025-08-01"},
            {"invoice_no": f"INV{hash(file_ref) % 1000 + 1}", "amount": 200.0, "date": "2025-08-02"}
        ]
    
    def _fetch_qbo_bills(self, vendor_id: int) -> list:
        """Fetch QBO bills for vendor."""
        try:
            qbo_bills = self.qbo_client.query(f"SELECT * FROM Bill WHERE VendorRef = '{vendor_id}'")
            return [
                {"invoice_no": bill.Id, "amount": bill.TotalAmt, "date": str(bill.DueDate)} 
                for bill in qbo_bills
            ]
        except Exception:
            # Return empty list if QBO query fails (development/testing)
            return []
    
    def _find_reconciliation_mismatches(self, parsed_invoices: list, qbo_invoices: list) -> list:
        """Find mismatches between statement and QBO data."""
        qbo_invoice_nos = {q["invoice_no"] for q in qbo_invoices}
        
        mismatches = []
        for inv in parsed_invoices:
            if inv["invoice_no"] not in qbo_invoice_nos:
                mismatches.append({
                    "invoice_no": inv["invoice_no"], 
                    "status": "missing in QBO",
                    "amount": inv["amount"]
                })
        
        return mismatches