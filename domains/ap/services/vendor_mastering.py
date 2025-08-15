from sqlalchemy.orm import Session
from quickbooks import QuickBooks
from quickbooks.objects import Vendor as QBOVendor
from domains.ap.models.vendor import Vendor as VendorModel
from domains.ap.models.vendor_canonical import VendorCanonical as VendorCanonicalModel
from domains.ap.schemas.vendor import Vendor
from domains.ap.schemas.vendor_canonical import VendorCanonical
from docs.normalization_tagging.escher_vendor_brain_v0_1.src.cleaners import build_vendor_canonical, fuzzy_match_descriptors, normalize_descriptor, load_normalize_cfg
from typing import Optional, List
import pandas as pd
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

class VendorMasteringService:
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
        self.norm_cfg = load_normalize_cfg("docs/normalization_tagging/escher_vendor_brain_v0_1/config/normalize.yaml")

    def sync_vendors(self, firm_id: str, client_id: Optional[int] = None) -> List[Vendor]:
        """Sync vendors from QBO and deduplicate."""
        try:
            qbo_vendors = QBOVendor.filter(qb=self.qbo_client)
            synced_vendors = []
            
            for qbo_vendor in qbo_vendors:
                raw_name = qbo_vendor.DisplayName
                normalized_name = normalize_descriptor(raw_name, self.norm_cfg)
                fingerprint = hashlib.md5(raw_name.encode()).hexdigest()
                
                vendor = self.db.query(VendorModel).filter(
                    VendorModel.firm_id == firm_id,
                    VendorModel.qbo_id == qbo_vendor.Id
                ).first()
                
                if not vendor:
                    canonical = self.db.query(VendorCanonicalModel).filter(
                        VendorCanonicalModel.firm_id == firm_id,
                        VendorCanonicalModel.canonical_name == normalized_name
                    ).first()
                    if not canonical:
                        canonical = VendorCanonicalModel(
                            firm_id=firm_id,
                            client_id=client_id,
                            raw_name=raw_name,
                            canonical_name=normalized_name,
                            confidence=0.9
                        )
                        self.db.add(canonical)
                        self.db.flush()
                    
                    vendor = VendorModel(
                        firm_id=firm_id,
                        client_id=client_id,
                        canonical_id=canonical.vendor_id,
                        qbo_id=qbo_vendor.Id,
                        w9_status="pending",
                        default_gl_account="6000-Expenses" if "food" in normalized_name.lower() else None,
                        terms=qbo_vendor.Terms or "Net 30",
                        fingerprint_hash=fingerprint
                    )
                    self.db.add(vendor)
                else:
                    vendor.terms = qbo_vendor.Terms or vendor.terms
                    vendor.w9_status = vendor.w9_status or "pending"
                
                synced_vendors.append(vendor)
            
            self.deduplicate_vendors(firm_id)
            self.db.commit()
            return synced_vendors
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Vendor sync failed: {str(e)}")

    def deduplicate_vendors(self, firm_id: str) -> None:
        """Deduplicate vendors using fuzzy matching from escher_vendor_brain."""
        vendor_table = build_vendor_canonical()
        existing_vendors = self.db.query(VendorModel).filter(VendorModel.firm_id == firm_id).all()
        descriptors = pd.Series([v.raw_name for v in existing_vendors])
        
        matches = fuzzy_match_descriptors(descriptors, vendor_table, score_cutoff=90)
        
        for _, match in matches.iterrows():
            if match["vendor_canonical"]:
                vendor = self.db.query(VendorModel).filter(
                    VendorModel.firm_id == firm_id,
                    VendorModel.raw_name == match["descriptor_norm"]
                ).first()
                if vendor:
                    canonical = self.db.query(VendorCanonicalModel).filter(
                        VendorCanonicalModel.firm_id == firm_id,
                        VendorCanonicalModel.canonical_name == match["vendor_canonical"]
                    ).first()
                    if canonical:
                        vendor.canonical_id = canonical.vendor_id
                        vendor.confidence = match["score"] / 100.0
        
        self.db.commit()