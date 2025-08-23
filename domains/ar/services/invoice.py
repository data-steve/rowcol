from typing import List, Optional
from sqlalchemy.orm import Session
from quickbooks import QuickBooks
from quickbooks.objects import Invoice as QBOInvoice
from domains.ar.models.invoice import Invoice as InvoiceModel
from domains.ar.schemas.invoice import Invoice
from domains.policy.services.policy_engine import PolicyEngineService
from datetime import datetime
import os
from dotenv import load_dotenv
import json

load_dotenv()

class InvoiceService:
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
        self.policy_engine = PolicyEngineService(db)

    def create_invoice(self, firm_id: str, customer_id: int, issue_date: datetime, due_date: datetime, total: float, lines: List[dict], client_id: Optional[int] = None) -> Invoice:
        """Create an invoice from CSV or manual input."""
        try:
            # Mock CSV parsing
            invoice_data = {
                "customer_id": customer_id,
                "issue_date": issue_date,
                "due_date": due_date,
                "total": total,
                "lines": lines
            }
            suggestion = self.policy_engine.categorize(firm_id, "invoice", total)
            
            # Extract confidence from top_k
            confidence = suggestion.top_k[0].get("confidence", 0.8) if suggestion.top_k else 0.8
            
            invoice = InvoiceModel(
                firm_id=firm_id,
                client_id=client_id,
                customer_id=customer_id,
                qbo_id=None,
                issue_date=issue_date,
                due_date=due_date,
                total=total,
                lines=lines,
                status="review" if confidence < 0.9 else "draft",
                confidence=confidence,
                attachment_refs=[]
            )
            self.db.add(invoice)
            
            # Sync with QBO (if client is configured)
            try:
                qbo_invoice = QBOInvoice()
                qbo_invoice.CustomerRef = {"value": str(customer_id)}
                qbo_invoice.TotalAmt = total
                qbo_invoice.Line = [{"Amount": line["amount"], "DetailType": "SalesItemLineDetail"} for line in lines]
                qbo_invoice.save(qb=self.qbo_client)
                invoice.qbo_id = qbo_invoice.Id
            except Exception as e:
                # QBO sync failed, but we can still create the invoice
                print(f"QBO sync failed: {e}")
                invoice.qbo_id = None
            
            self.db.commit()
            self.db.refresh(invoice)
            return invoice
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Invoice creation failed: {str(e)}")

    def sync_invoices(self, firm_id: str, client_id: Optional[int] = None) -> List[Invoice]:
        """Sync invoices from QBO."""
        try:
            qbo_invoices = QBOInvoice.filter(qb=self.qbo_client)
            invoices = []
            for qbo_invoice in qbo_invoices:
                invoice = self.db.query(InvoiceModel).filter(
                    InvoiceModel.firm_id == firm_id,
                    InvoiceModel.qbo_id == qbo_invoice.Id
                ).first()
                if not invoice:
                    invoice = InvoiceModel(
                        firm_id=firm_id,
                        client_id=client_id,
                        customer_id=int(qbo_invoice.CustomerRef["value"]),
                        qbo_id=qbo_invoice.Id,
                        issue_date=qbo_invoice.TxnDate,
                        due_date=qbo_invoice.DueDate,
                        total=qbo_invoice.TotalAmt,
                        lines=[{"amount": line.Amount} for line in qbo_invoice.Line],
                        status="draft",
                        attachment_refs=[],
                        confidence=0.9
                    )
                    self.db.add(invoice)
                invoices.append(invoice)
            
            self.db.commit()
            return invoices
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Invoice sync failed: {str(e)}")