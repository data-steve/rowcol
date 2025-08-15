from typing import Optional
from sqlalchemy.orm import Session
from domains.ap.models.bill import Bill as BillModel
from domains.ap.schemas.bill import Bill
from domains.ap.services.ocr_adapter import get_ocr_adapter
from domains.core.services.policy_engine import PolicyEngineService
from docs.normalization_tagging.escher_vendor_brain_v0_1.src.cleaners import normalize_descriptor, load_normalize_cfg
from datetime import datetime
import dateutil.parser

class BillIngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.ocr_adapter = get_ocr_adapter()
        self.policy_engine = PolicyEngineService(db)
        self.norm_cfg = load_normalize_cfg("docs/normalization_tagging/escher_vendor_brain_v0_1/config/normalize.yaml")

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

    def ingest_bill(self, file_path: str, firm_id: str, client_id: Optional[int] = None) -> Bill:
        """Ingest a bill via OCR (mocked)."""
        try:
            extracted = self.ocr_adapter.extract_document(file_path)
            raw_vendor = extracted.get("vendor_name", "")
            normalized_name = normalize_descriptor(raw_vendor, self.norm_cfg)
            
            # Categorize via PolicyEngineService
            suggestion = self.policy_engine.categorize(
                firm_id=firm_id,
                description=normalized_name,
                amount=float(extracted.get("amount", 0.0))
            )
            
            # Extract suggestion data
            gl_account = "6000-Expenses"  # Default
            confidence = 0.7  # Default
            
            if suggestion.top_k and len(suggestion.top_k) > 0:
                best_suggestion = suggestion.top_k[0]
                gl_account = best_suggestion.get("account", gl_account)
                confidence = best_suggestion.get("confidence", confidence)
            
            # Parse due date properly
            due_date = self._parse_date(extracted.get("date"))
            
            bill = BillModel(
                firm_id=firm_id,
                client_id=client_id,
                vendor_id=None,  # To be linked by VendorMasteringService
                qbo_bill_id=extracted.get("invoice_number", "mock_" + str(hash(file_path))),
                amount=float(extracted.get("amount", 0.0)),
                due_date=due_date,
                status="review" if confidence < 0.9 else "pending",
                extracted_fields=extracted,  # Direct assignment for JSON field
                gl_account=gl_account,
                confidence=confidence
            )
            self.db.add(bill)
            self.db.commit()
            self.db.refresh(bill)
            return bill
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Bill ingestion failed: {str(e)}")