from typing import Dict, Optional, List, Any
from sqlalchemy.orm import Session
from domains.core.services.base_service import TenantAwareService
from infra.qbo.smart_sync import SmartSyncService
from domains.ap.models.bill import Bill as BillModel, BillStatus
from domains.vendor_normalization.models import VendorCanonical as VendorCanonicalModel
from domains.ap.schemas.bill import Bill
from domains.vendor_normalization.services import VendorNormalizationService
from domains.vendor_normalization.lib.cleaners import load_normalize_cfg
from common.exceptions import ValidationError, QBOSyncError
from infra.database.transaction import db_transaction
from datetime import datetime
import dateutil.parser
import logging

logger = logging.getLogger(__name__)

class IngestionService(TenantAwareService):
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        # Use SmartSyncService for QBO orchestration
        self.smart_sync = SmartSyncService(business_id, "", db)
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

    async def sync_bills(self, business_id: str) -> Dict[str, Any]:
        """Sync bills from QBO using SmartSyncService and process them via BillService."""
        try:
            from domains.ap.services.bill_ingestion import BillService

            # Use SmartSyncService for orchestration
            smart_sync = SmartSyncService(business_id, "", self.db)
            bill_service = BillService(self.db, business_id)
            
            # Get QBO data using SmartSyncService
            qbo_data = await smart_sync.get_bills_for_digest()
            
            # Process bills through BillService
            processed_bills = []
            for bill_data in qbo_data:
                try:
                    processed_bill = bill_service._process_qbo_bill(bill_data)
                    if processed_bill:
                        processed_bills.append(processed_bill)
                except Exception as e:
                    logger.error(f"Error processing bill {bill_data.get('id', 'unknown')}: {e}")
            
            return {
                "status": "success",
                "synced_count": len(processed_bills),
                "skipped_count": len(qbo_data) - len(processed_bills),
                "errors": len(qbo_data) - len(processed_bills)
            }
        except Exception as e:
            logger.error(f"Error syncing bills for business {business_id}: {e}", exc_info=True)
            # Re-raising as ValueError is not ideal, but keeping consistent with original code
            raise ValueError(f"QBO bill sync failed: {str(e)}")