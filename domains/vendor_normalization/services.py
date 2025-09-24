from typing import Optional, List
from sqlalchemy.orm import Session
from domains.vendor_normalization.models import VendorCanonical as VendorCanonicalModel
from domains.ap.models.vendor_category import VendorCategory
from domains.vendor_normalization.schemas import VendorCanonical
import re

class VendorNormalizationService:
    def __init__(self, db: Session):
        self.db = db

    def create_vendor_canonical(self, vendor: VendorCanonical) -> VendorCanonical:
        """Create a new vendor canonical."""
        db_vendor = VendorCanonicalModel(**vendor.dict())
        self.db.add(db_vendor)
        self.db.commit()
        self.db.refresh(db_vendor)
        return db_vendor

    def get_vendor(self, vendor_id: int):
        return self.db.query(VendorCanonicalModel).filter(VendorCanonicalModel.vendor_id == vendor_id).first()

    def list_vendor_canonicals(self, business_id: int) -> List[VendorCanonical]:
        """List all vendor canonicals for a business."""
        vendors = self.db.query(VendorCanonicalModel).filter(
            VendorCanonicalModel.business_id == business_id
        ).all()
        return vendors

    def normalize_vendor(self, raw_name: str, business_id: int) -> VendorCanonical:
        """Normalize vendor name and map to COA using real vendor categories."""
        cleaned_name = re.sub(r'\d{4,}$', '', raw_name)
        cleaned_name = re.sub(r'\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?', '', cleaned_name)
        cleaned_name = re.sub(r'\b(POS|ACH|WEB)\b', '', cleaned_name, flags=re.IGNORECASE)
        cleaned_name = cleaned_name.strip()

        existing = self.db.query(VendorCanonicalModel).filter(
            VendorCanonicalModel.business_id == business_id,
            VendorCanonicalModel.raw_name == raw_name
        ).first()

        # Calculate real confidence based on vendor category matching
        confidence = self._calculate_confidence(raw_name, cleaned_name)
        
        # Get vendor category and default GL account
        vendor_category = self._get_vendor_category(cleaned_name)
        default_gl_account = vendor_category.default_gl_account if vendor_category else "6000-Expenses"

        if existing:
            # Update existing vendor
            existing.raw_name = raw_name
            existing.canonical_name = cleaned_name
            existing.confidence = confidence
            existing.default_gl_account = default_gl_account
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new vendor
            vendor = VendorCanonicalModel(
                business_id=business_id,
                raw_name=raw_name,
                canonical_name=cleaned_name,
                confidence=confidence,
                default_gl_account=default_gl_account
            )
            self.db.add(vendor)
            self.db.commit()
            self.db.refresh(vendor)
            return vendor

    def _calculate_confidence(self, raw_name: str, cleaned_name: str) -> float:
        """Calculate confidence score based on real factors."""
        base_confidence = 0.5
        
        # Boost confidence for longer, more descriptive names
        if len(cleaned_name) > 10:
            base_confidence += 0.1
        
        # Boost confidence if vendor category can be determined
        if self._get_vendor_category(cleaned_name):
            base_confidence += 0.2
        
        # Boost confidence if name contains business indicators
        business_indicators = ["inc", "llc", "corp", "company", "co", "ltd", "associates", "partners"]
        if any(indicator in cleaned_name.lower() for indicator in business_indicators):
            base_confidence += 0.1
        
        # Reduce confidence for very short or generic names
        if len(cleaned_name) < 5:
            base_confidence -= 0.2
        
        # Reduce confidence for names with lots of numbers/special chars
        special_char_ratio = len(re.findall(r'[^a-zA-Z\s]', raw_name)) / len(raw_name) if raw_name else 0
        if special_char_ratio > 0.3:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.1), 1.0)

    def _get_vendor_category(self, vendor_name: str) -> Optional[VendorCategory]:
        """Get vendor category based on vendor name patterns."""
        if not vendor_name:
            return None
        
        # Simple keyword matching - could be enhanced with ML
        vendor_lower = vendor_name.lower()
        
        if any(word in vendor_lower for word in ["office", "supply", "staples", "amazon", "target", "walmart"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Office Supplies"
            ).first()
        elif any(word in vendor_lower for word in ["legal", "law", "attorney", "cpa", "accountant", "consulting"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Professional Services"
            ).first()
        elif any(word in vendor_lower for word in ["software", "tech", "computer", "it", "microsoft", "google", "apple"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Technology"
            ).first()
        elif any(word in vendor_lower for word in ["travel", "airline", "hotel", "restaurant", "entertainment"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Travel & Entertainment"
            ).first()
        elif any(word in vendor_lower for word in ["marketing", "advertising", "media", "print", "design"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Marketing & Advertising"
            ).first()
        elif any(word in vendor_lower for word in ["insurance", "coverage", "policy"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Insurance"
            ).first()
        elif any(word in vendor_lower for word in ["utility", "electric", "water", "gas", "internet", "phone"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Utilities"
            ).first()
        elif any(word in vendor_lower for word in ["rent", "lease", "property", "real estate"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Rent & Leasing"
            ).first()
        elif any(word in vendor_lower for word in ["payroll", "hr", "human resources", "benefits"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Payroll Services"
            ).first()
        elif any(word in vendor_lower for word in ["tax", "irs", "filing", "preparation"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Tax Services"
            ).first()
        
        return None

    def export_to_csv(self, business_id: int) -> str:
        """Export VendorCanonical to CSV string."""
        vendors = self.db.query(VendorCanonicalModel).filter(VendorCanonicalModel.business_id == business_id).all()
        csv_lines = ["vendor_id,business_id,raw_name,canonical_name,mcc,naics,default_gl_account,confidence"]
        for vendor in vendors:
            csv_lines.append(
                f"{vendor.vendor_id},{vendor.business_id},"
                f"{vendor.raw_name},{vendor.canonical_name},{vendor.mcc or ''},"
                f"{vendor.naics or ''},{vendor.default_gl_account or ''},{vendor.confidence}"
            )
        return "\n".join(csv_lines)