from typing import Optional
from sqlalchemy.orm import Session
from models.vendor_canonical import VendorCanonical as VendorCanonicalModel
from schemas.vendor_canonical import VendorCanonical
import re

class VendorNormalizationService:
    def __init__(self, db: Session):
        self.db = db

    def normalize_vendor(self, raw_name: str, firm_id: str, client_id: Optional[int] = None) -> VendorCanonical:
        """Normalize vendor name and map to COA."""
        cleaned_name = re.sub(r'\d{4,}$', '', raw_name)
        cleaned_name = re.sub(r'\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?', '', cleaned_name)
        cleaned_name = re.sub(r'\b(POS|ACH|WEB)\b', '', cleaned_name, flags=re.IGNORECASE)
        cleaned_name = cleaned_name.strip()

        existing = self.db.query(VendorCanonicalModel).filter(
            VendorCanonicalModel.firm_id == firm_id,
            VendorCanonicalModel.raw_name == raw_name
        ).first()

        if existing:
            return VendorCanonical.from_orm(existing)

        # Mock MCC/NAICS and GL account mapping (to be expanded in Phase 1)
        mcc = "5812" if "food" in cleaned_name.lower() else None
        naics = "722511" if "food" in cleaned_name.lower() else None
        default_gl_account = "6000-Expenses" if "food" in cleaned_name.lower() else None

        vendor = VendorCanonicalModel(
            firm_id=firm_id,
            client_id=client_id,
            raw_name=raw_name,
            canonical_name=cleaned_name,
            mcc=mcc,
            naics=naics,
            default_gl_account=default_gl_account,
            confidence=0.9  # Mock confidence
        )
        self.db.add(vendor)
        self.db.commit()
        self.db.refresh(vendor)
        return VendorCanonical.from_orm(vendor)

    def export_to_csv(self, firm_id: str) -> str:
        """Export VendorCanonical to CSV string."""
        vendors = self.db.query(VendorCanonicalModel).filter(VendorCanonicalModel.firm_id == firm_id).all()
        csv_lines = ["vendor_id,firm_id,client_id,raw_name,canonical_name,mcc,naics,default_gl_account,confidence"]
        for vendor in vendors:
            csv_lines.append(
                f"{vendor.vendor_id},{vendor.firm_id},{vendor.client_id or ''},"
                f"{vendor.raw_name},{vendor.canonical_name},{vendor.mcc or ''},"
                f"{vendor.naics or ''},{vendor.default_gl_account or ''},{vendor.confidence}"
            )
        return "\n".join(csv_lines)