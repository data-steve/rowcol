from typing import List
from sqlalchemy.orm import Session
from domains.ar.models.invoice import Invoice as InvoiceModel
from domains.ar.schemas.invoice import Invoice
from domains.policy.services.policy_engine import PolicyEngineService
from domains.integrations.smart_sync import SmartSyncService
from datetime import datetime

class InvoiceService:
    def __init__(self, db: Session, business_id: str = None):
        self.db = db
        self.business_id = business_id
        self.smart_sync = SmartSyncService(db, business_id) if business_id else None
        self.policy_engine = PolicyEngineService(db)

    def create_invoice(self, business_id: int, customer_id: int, issue_date: datetime, due_date: datetime, total: float, lines: List[dict]) -> Invoice:
        """Create an invoice from CSV or manual input."""
        try:
            suggestion = self.policy_engine.categorize(business_id, "invoice", total)
            
            # Extract confidence from top_k
            confidence = suggestion.top_k[0].get("confidence", 0.8) if suggestion.top_k else 0.8
            
            invoice = InvoiceModel(
                business_id=business_id,
                customer_id=customer_id,
                qbo_invoice_id=None,
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
                # TODO: Implement QBO invoice sync in Phase 4
                # qbo_invoice = QBOInvoice()
                # qbo_invoice.CustomerRef = {"value": str(customer_id)}
                # qbo_invoice.TotalAmt = total
                # qbo_invoice.Line = [{"Amount": line["amount"], "DetailType": "SalesItemLineDetail"} for line in lines]
                # qbo_invoice.save(qb=self.qbo_client)
                # invoice.qbo_invoice_id = qbo_invoice.Id
                invoice.qbo_invoice_id = f"MOCK_QBO_{invoice.invoice_id}"  # Mock QBO ID for Phase 0-3
            except Exception as e:
                # QBO sync failed, but we can still create the invoice
                print(f"QBO sync failed: {e}")
                invoice.qbo_invoice_id = None
            
            self.db.commit()
            self.db.refresh(invoice)
            return invoice
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Invoice creation failed: {str(e)}")

    def sync_invoices(self, business_id: int) -> List[Invoice]:
        """Sync invoices from QBO via SmartSyncService."""
        try:
            if not self.smart_sync:
                # Fallback for when business_id wasn't provided in constructor
                self.smart_sync = SmartSyncService(self.db, str(business_id))
            
            # Use SmartSyncService to get QBO invoices data
            qbo_data = self.smart_sync.get_qbo_data_for_digest()
            qbo_invoices = qbo_data.get("invoices", [])
            
            invoices = []
            for qbo_invoice_data in qbo_invoices:
                invoice = self.db.query(InvoiceModel).filter(
                    InvoiceModel.business_id == business_id,
                    InvoiceModel.qbo_id == qbo_invoice_data.get("Id")
                ).first()
                if not invoice:
                    invoice = InvoiceModel(
                        business_id=business_id,
                        customer_id=int(qbo_invoice_data.get("CustomerRef", {}).get("value", 0)),
                        qbo_id=qbo_invoice_data.get("Id"),
                        issue_date=qbo_invoice_data.get("TxnDate"),
                        due_date=qbo_invoice_data.get("DueDate"),
                        total=float(qbo_invoice_data.get("TotalAmt", 0)),
                        lines=[{"amount": line.get("Amount", 0)} for line in qbo_invoice_data.get("Line", [])],
                        status="draft",
                        attachment_refs=[],
                        confidence=0.9
                    )
                    self.db.add(invoice)
                invoices.append(invoice)
            
            self.db.commit()
            
            # Record sync activity
            self.smart_sync.record_user_activity("invoice_sync")
            
            return invoices
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Invoice sync failed: {str(e)}")