from fastapi import HTTPException
from sqlalchemy.orm import Session
from domains.core.models.integration import Integration
from domains.core.models.transaction import Transaction
from domains.core.providers import DataProvider, get_data_provider
from db.transaction import db_transaction
from common.exceptions import DataIngestionError, IntegrationError
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataIngestionService:
    def __init__(self, db: Session, data_provider: Optional[DataProvider] = None):
        self.db = db
        self.data_provider = data_provider or get_data_provider()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_platform_data(self, platform: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Fetch data from QBO platform only."""
        if platform != "qbo":
            raise DataIngestionError(f"Unsupported platform: {platform}")
        
        # Find integration for the platform
        integration = self.db.query(Integration).filter_by(platform=platform).first()
        if not integration:
            raise IntegrationError(f"{platform} integration not found")
            
        return self._fetch_qbo_data(integration, credentials)

    def sync_qbo(self, business_id: int, full_sync: bool = False) -> Dict[str, Any]:
        """Sync QBO data for a business."""
        integration = self.db.query(Integration).filter_by(
            business_id=business_id, 
            platform="qbo"
        ).first()
        
        if not integration:
            raise IntegrationError(f"QBO integration not found for business {business_id}")
            
        credentials = {"access_token": integration.access_token}
        return self._fetch_qbo_data(integration, credentials)

    def _fetch_qbo_data(self, integration: Integration, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Fetch QBO transactions via data provider."""
        try:
            # Get transaction data from provider (mock or real)
            transactions_data = self.data_provider.fetch_transactions(credentials)
            
            # Store in database with proper transaction management
            with db_transaction(self.db):
                stored_count = 0
                for txn_data in transactions_data:
                    txn = Transaction(
                        txn_id=txn_data["txn_id"],
                        business_id=integration.business_id,
                        integration_id=integration.integration_id,
                        platform_txn_id=txn_data["txn_id"],
                        type=txn_data["type"],
                        amount=txn_data["amount"],
                        date=txn_data["date"],
                        status="unmatched"
                    )
                    self.db.merge(txn)
                    stored_count += 1
                
                logger.info(f"Stored {stored_count} transactions for business {integration.business_id}")
            
            return {
                "status": "success",
                "transactions_fetched": len(transactions_data),
                "transactions_stored": stored_count,
                "business_id": integration.business_id
            }
            
        except Exception as e:
            logger.error(f"QBO data fetch failed for business {integration.business_id}: {e}", exc_info=True)
            raise DataIngestionError("Failed to fetch QBO data", {"error": str(e)})