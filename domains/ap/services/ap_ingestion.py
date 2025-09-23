from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from domains.core.services.base_service import TenantAwareService
from domains.integrations.smart_sync import SmartSyncService
from domains.ap.models.bill import Bill as BillModel, BillStatus
from domains.vendor_normalization.models import VendorCanonical as VendorCanonicalModel
from domains.ap.schemas.bill import Bill
from domains.vendor_normalization.services import VendorNormalizationService
from domains.vendor_normalization.lib.cleaners import load_normalize_cfg
from common.exceptions import ValidationError, QBOSyncError
from db.transaction import db_transaction
from datetime import datetime
import dateutil.parser
import logging

logger = logging.getLogger(__name__)

class IngestionService(TenantAwareService):
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        # TODO: Complete refactor to use SmartSyncService instead of direct QBO client
        # This addresses the critical architectural violation identified in code audit
        self.smart_sync = SmartSyncService(db, business_id)
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

    async def sync_bills(self, business_id: str, full_sync: bool = False) -> Dict:
        """Sync bills from QBO using SmartSyncService and process them via BillService."""
        try:
            from domains.integrations.smart_sync import SmartSyncService
            from domains.ap.services.bill_ingestion import BillService
            smart_sync = SmartSyncService(self.db, business_id)
            bill_service = BillService(self.db, business_id)
            sync_result = await smart_sync.sync_qbo_data()
            
            if sync_result.get('status') != 'success':
                return {"status": "error", "message": sync_result.get('reason', 'Unknown error')}
            
            # No need for additional processing here as BillService handles ingestion via SmartSync
            return {
                "status": "success",
                "synced_bills": sync_result.get('synced_bills', 0),
                "bills": []  # SmartSync and BillService handle the ingestion
            }
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"QBO bill sync failed: {str(e)}")

    def ingest_document(self, file_path: str, business_id: int) -> Bill:
        """Ingest a document (mock OCR for now)."""
        # Document ingestion logic here (if any)
        pass