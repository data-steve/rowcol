from typing import Dict, Optional
from sqlalchemy.orm import Session
from domains.integrations.qbo.service import SmartSyncService
from domains.ap.models.bill import Bill as BillModel
from domains.vendor_normalization.models import VendorCanonical as VendorCanonicalModel
from domains.vendor_normalization.services import VendorNormalizationService
from domains.vendor_normalization.lib.cleaners import normalize_descriptor, load_normalize_cfg
from datetime import datetime
import dateutil.parser
import os

class IngestionService:
    def __init__(self, db: Session, business_id: str = None):
        self.db = db
        self.business_id = business_id
        self.smart_sync = SmartSyncService(db, business_id) if business_id else None
            
        # OCR is handled by QBO; no local OCRAdapter needed
        self.vendor_service = VendorNormalizationService(db)
        self.norm_cfg = load_normalize_cfg("domains/vendor_normalization/scripts/config/normalize.yaml")

    # Token refresh is now handled centrally by QBOAuth and SmartSyncService
    # Individual services should not manage tokens directly

    def _parse_date(self, date_value) -> Optional[datetime]:
        """Parse date value to datetime object."""
        if date_value is None:
            return None
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            try:
                return dateutil.parser.parse(date_value)
            except (ValueError, TypeError):
                return None
        return None

    def sync_bills(self, business_id: str, full_sync: bool = False) -> Dict:
        """Sync bills from QBO via SmartSyncService and store in database."""
        if not self.smart_sync:
            # Fallback for when business_id wasn't provided in constructor
            self.smart_sync = SmartSyncService(self.db, str(business_id))
        
        try:
            # Use SmartSyncService to get QBO bills data
            qbo_data = self.smart_sync.sync_qbo_bills()
            bills_data = qbo_data.get("bills", [])
            synced_bills = []
            
            for qbo_bill_data in bills_data:
                # Normalize vendor name using vendor_normalization domain
                raw_vendor = qbo_bill_data.get("VendorRef", {}).get("name", "")
                
                # Check for existing vendor
                vendor = self.db.query(VendorCanonicalModel).filter(
                    VendorCanonicalModel.business_id == business_id,
                    VendorCanonicalModel.raw_name == raw_vendor
                ).first()
                
                if not vendor:
                    # Create new vendor using VendorNormalizationService
                    vendor_schema = self.vendor_service.normalize_vendor(raw_vendor, business_id)
                    vendor = self.db.query(VendorCanonicalModel).filter(
                        VendorCanonicalModel.id == vendor_schema.id
                    ).first()

                # Create or update bill
                bill = self.db.query(BillModel).filter(
                    BillModel.qbo_bill_id == qbo_bill_data.get("Id"),
                    BillModel.business_id == business_id
                ).first()
                
                # Parse due date properly
                due_date = self._parse_date(qbo_bill_data.get("DueDate"))
                
                if not bill:
                    bill = BillModel(
                        business_id=business_id,
                        vendor_id=vendor.id if vendor else None,
                        qbo_bill_id=qbo_bill_data.get("Id"),
                        amount_cents=int(float(qbo_bill_data.get("TotalAmt", 0)) * 100),
                        due_date=due_date,
                        status="pending"
                    )
                    self.db.add(bill)
                else:
                    bill.amount_cents = int(float(qbo_bill_data.get("TotalAmt", 0)) * 100)
                    bill.due_date = due_date
                    bill.vendor_id = vendor.id if vendor else None
                
                synced_bills.append(bill)
            
            self.db.commit()
            return {"status": "success", "synced_bills": len(synced_bills)}
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"QBO bill sync failed: {str(e)}")
