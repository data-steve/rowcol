"""
QBO Data Service - Unified Data Access Layer

Provides efficient, cached access to QBO data for all runway experiences.
Handles bulk processing for digest emails and individual requests for other experiences.

This replaces the scattered get_X_for_digest() methods across domains with a
centralized, scalable data access layer.
"""

from sqlalchemy.orm import Session
from domains.qbo.client import get_qbo_client
from infra.jobs import SyncStrategy, SyncPriority, SyncTimingManager, SyncCache
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)

class QBODataService:
    """
    Unified QBO data access service for all runway experiences.
    
    Provides experience-specific data methods while sharing common
    infrastructure for sync timing, caching, and bulk processing.
    """
    
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        self.timing_manager = SyncTimingManager(business_id)
        self.cache = SyncCache()
        
    
    def get_bulk_raw_data(self, business_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get raw QBO data for multiple businesses efficiently for bulk processing.
        
        This method is optimized for bulk operations that need to process all businesses
        within QBO rate limits.
        
        Args:
            business_ids: List of business IDs to process
            
        Returns:
            Dict mapping business_id to their raw QBO data
        """
        results = {}
        
        # Process in batches to respect QBO rate limits
        batch_size = 10  # Process 10 businesses at a time
        for i in range(0, len(business_ids), batch_size):
            batch = business_ids[i:i + batch_size]
            
            for business_id in batch:
                try:
                    # Create a new service instance for each business
                    business_service = QBODataService(self.db, business_id)
                    results[business_id] = business_service.get_raw_qbo_data()
                    
                    # Add small delay between businesses to respect rate limits
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Failed to get raw data for business {business_id}: {e}")
                    results[business_id] = {"error": str(e), "bills": [], "invoices": [], "balances": [], "customers": [], "vendors": []}
            
            # Add delay between batches
            if i + batch_size < len(business_ids):
                await asyncio.sleep(1.0)
        
        return results
    
