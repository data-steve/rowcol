from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from domains.ap.models import Bill, Vendor

class BillIngestionService:
    def __init__(self, db: Session):
        self.db = db

    async def process_bill(self, file: UploadFile):
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        # Placeholder: Implement actual PDF processing logic
        vendor = self.db.query(Vendor).filter_by(qbo_id="vendor_001").first()
        if not vendor:
            vendor = Vendor(business_id=1, qbo_id="vendor_001", name="Rent LLC")
            self.db.add(vendor)
        bill = Bill(
            business_id=1,
            qbo_id=f"bill_{file.filename}",
            vendor_id="vendor_001",
            amount=5000.0,
            due_date="2025-09-22",
            status="open"
        )
        self.db.add(bill)
        self.db.commit()
        return {"status": "success", "bill_id": bill.qbo_id}
