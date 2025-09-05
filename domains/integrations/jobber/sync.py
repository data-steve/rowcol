from typing import Dict, Optional
from sqlalchemy.orm import Session
from .client import JobberClient
from domains.core.models.sync_cursor import SyncCursor
from domains.ar.models.invoice import Invoice
from datetime import datetime

class JobberSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.client = JobberClient(db)

    async def sync(self, firm_id: str, commit: bool = False) -> Dict:
        cursor = self.db.query(SyncCursor).filter(
            SyncCursor.firm_id == firm_id,
            SyncCursor.source == "jobber"
        ).first()

        query = """
        query($after: String) {
            invoices(first: 10, after: $after) {
                nodes {
                    id
                    jobId
                    amount
                    paidDate
                    customer { id }
                }
                pageInfo { endCursor hasNextPage }
            }
        }
        """
        result = await self.client.fetch_data(firm_id, query, {"after": cursor.cursor if cursor else None})

        if commit:
            for node in result["invoices"]["nodes"]:
                invoice = self.db.query(Invoice).filter(
                    Invoice.firm_id == firm_id,
                    Invoice.qbo_id == node["id"]
                ).first()
                if not invoice:
                    invoice = Invoice(
                        firm_id=firm_id,
                        customer_id=node["customer"]["id"],
                        qbo_id=node["id"],
                        job_id=node["jobId"],
                        issue_date=datetime.utcnow(),  # Placeholder
                        due_date=datetime.utcnow(),    # Placeholder
                        total=node["amount"],
                        status="paid" if node["paidDate"] else "sent",
                        lines=[],
                        confidence=1.0
                    )
                    self.db.add(invoice)

                if result["invoices"]["pageInfo"]["hasNextPage"]:
                    if not cursor:
                        cursor = SyncCursor(firm_id=firm_id, source="jobber")
                        self.db.add(cursor)
                    cursor.cursor = result["invoices"]["pageInfo"]["endCursor"]

            self.db.commit()

        return result
