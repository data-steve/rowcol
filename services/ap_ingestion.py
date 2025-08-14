from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from quickbooks.objects import Bill as QBOBill
from models.bill import Bill as BillModel
from models.vendor_canonical import VendorCanonical as VendorCanonicalModel
from schemas.bill import Bill
from schemas.vendor_canonical import VendorCanonical
from services.vendor_normalization import VendorNormalizationService
from .ocr_adapter import get_ocr_adapter
import os
from dotenv import load_dotenv
from docs.normalization_tagging.escher_vendor_brain_v0_1.src.cleaners import normalize_descriptor, load_normalize_cfg
from datetime import datetime
import dateutil.parser
import json

load_dotenv()

class APIngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_client = AuthClient(
            client_id=os.getenv("QBO_CLIENT_ID"),
            client_secret=os.getenv("QBO_CLIENT_SECRET"),
            redirect_uri=os.getenv("QBO_REDIRECT_URI", "http://localhost:8000/callback"),
            environment="sandbox"
        )
        
        # Set tokens from environment
        access_token = os.getenv("QBO_ACCESS_TOKEN")
        refresh_token = os.getenv("QBO_REFRESH_TOKEN")
        realm_id = os.getenv("QBO_REALM_ID")
        
        if access_token and refresh_token and realm_id:
            self.auth_client.access_token = access_token
            self.auth_client.refresh_token = refresh_token
            self.auth_client.realm_id = realm_id
            
            # Initialize QBO client
            self.qbo_client = QuickBooks(
                sandbox=True,
                consumer_key=os.getenv("QBO_CLIENT_ID"),
                consumer_secret=os.getenv("QBO_CLIENT_SECRET"),
                access_token=access_token,
                access_token_secret=refresh_token,
                company_id=realm_id
            )
        else:
            # For testing or when tokens aren't available
            self.qbo_client = None
            
        self.ocr_adapter = get_ocr_adapter()
        self.vendor_service = VendorNormalizationService(db)
        self.norm_cfg = load_normalize_cfg("docs/normalization_tagging/escher_vendor_brain_v0_1/config/normalize.yaml")

    def refresh_token(self):
        """Refresh QBO access token."""
        try:
            self.auth_client.refresh()
            # Update .env or database with new tokens
            os.environ["QBO_ACCESS_TOKEN"] = self.auth_client.access_token
            os.environ["QBO_REFRESH_TOKEN"] = self.auth_client.refresh_token
            # TODO: Store in qbo_tokens table
        except Exception as e:
            raise ValueError(f"Token refresh failed: {str(e)}")

    def _parse_date(self, date_value) -> Optional[datetime]:
        """Parse date value to datetime object."""
        if date_value is None:
            return None
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            try:
                return dateutil.parser.parse(date_value)
            except:
                return None
        return None

    def sync_bills(self, firm_id: str, client_id: Optional[int] = None, full_sync: bool = False) -> Dict:
        """Sync bills from QBO and store in database."""
        if not self.qbo_client:
            return {"status": "error", "message": "QBO client not configured"}
        
        # Check if QBO client has a valid session
        if not hasattr(self.qbo_client, 'session') or self.qbo_client.session is None:
            return {"status": "error", "message": "QBO client session not properly configured"}
            
        try:
            # Fetch bills from QBO
            bills = QBOBill.filter(qb=self.qbo_client)
            synced_bills = []
            
            for qbo_bill in bills:
                # Normalize vendor name using escher_vendor_brain
                raw_vendor = qbo_bill.VendorRef.name if qbo_bill.VendorRef else ""
                normalized_name = normalize_descriptor(raw_vendor, self.norm_cfg)
                
                # Check for existing vendor
                vendor = self.db.query(VendorCanonicalModel).filter(
                    VendorCanonicalModel.firm_id == firm_id,
                    VendorCanonicalModel.raw_name == raw_vendor
                ).first()
                
                if not vendor:
                    # Create new vendor using VendorNormalizationService
                    vendor_schema = self.vendor_service.normalize_vendor(raw_vendor, firm_id, client_id)
                    vendor = self.db.query(VendorCanonicalModel).filter(
                        VendorCanonicalModel.vendor_id == vendor_schema.vendor_id
                    ).first()

                # Create or update bill
                bill = self.db.query(BillModel).filter(
                    BillModel.qbo_bill_id == qbo_bill.Id,
                    BillModel.firm_id == firm_id
                ).first()
                
                # Parse due date properly
                due_date = self._parse_date(qbo_bill.DueDate)
                
                if not bill:
                    bill = BillModel(
                        firm_id=firm_id,
                        client_id=client_id,
                        vendor_id=vendor.vendor_id if vendor else None,
                        qbo_bill_id=qbo_bill.Id,
                        amount=qbo_bill.TotalAmt,
                        due_date=due_date,
                        status="pending",
                        gl_account="6000-Expenses" if "food" in normalized_name.lower() else None,
                        confidence=0.9 if "food" in normalized_name.lower() else 0.7
                    )
                    self.db.add(bill)
                else:
                    bill.amount = qbo_bill.TotalAmt
                    bill.due_date = due_date
                    bill.vendor_id = vendor.vendor_id if vendor else None
                
                synced_bills.append(bill)
            
            self.db.commit()
            return {"status": "success", "synced_bills": len(synced_bills), "bills": [bill.dict() for bill in synced_bills]}
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"QBO bill sync failed: {str(e)}")

    def ingest_document(self, file_path: str, firm_id: str, client_id: Optional[int] = None) -> Bill:
        """Ingest a document (mock OCR for now)."""
        extracted = self.ocr_adapter.extract_document(file_path)
        raw_vendor = extracted.get("vendor_name", "")
        normalized_name = normalize_descriptor(raw_vendor, self.norm_cfg)
        
        vendor = self.vendor_service.normalize_vendor(raw_vendor, firm_id, client_id)
        
        # Parse date properly
        due_date = self._parse_date(extracted.get("date"))
        
        bill = BillModel(
            firm_id=firm_id,
            client_id=client_id,
            vendor_id=vendor.vendor_id,
            qbo_bill_id=extracted.get("invoice_number", "mock_" + str(hash(file_path))),
            amount=float(extracted.get("amount", 0.0)),
            due_date=due_date,
            status="pending",
            extracted_fields=extracted,  # Direct assignment for JSON field
            gl_account="6000-Expenses" if "food" in normalized_name.lower() else None,
            confidence=0.9 if "food" in normalized_name.lower() else 0.7
        )
        self.db.add(bill)
        self.db.commit()
        self.db.refresh(bill)
        return bill