"""
QBO Data Service - Unified Data Access Layer

Provides efficient, cached access to QBO data for all runway experiences.
Handles bulk processing for digest emails and individual requests for other experiences.

This replaces the scattered get_X_for_digest() methods across domains with a
centralized, scalable data access layer.
"""

from sqlalchemy.orm import Session
from domains.qbo.client import get_qbo_client
from infra.jobs import SmartSyncService
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
        self.smart_sync = SmartSyncService(business_id)
        
    
    def get_digest_data(self) -> Dict[str, Any]:
        """
        Get QBO data formatted specifically for digest experience.
        
        Returns:
            Dict containing digest-specific QBO data
        """
        # Get raw QBO data using SmartSyncService
        qbo_data = self.smart_sync.get_qbo_data_for_digest()
        
        # Format for digest experience
        return {
            "bills": qbo_data.get("bills", []),
            "invoices": qbo_data.get("invoices", []),
            "balances": qbo_data.get("balances", []),
            "customers": qbo_data.get("customers", []),
            "vendors": qbo_data.get("vendors", []),
            "synced_at": qbo_data.get("synced_at", datetime.utcnow().isoformat())
        }
    
    def get_tray_data(self) -> Dict[str, Any]:
        """
        Get QBO data formatted specifically for tray experience.
        
        Returns:
            Dict containing tray-specific QBO data
        """
        # Get raw QBO data using SmartSyncService
        qbo_data = self.smart_sync.get_qbo_data_for_digest()
        
        # Format for tray experience
        return {
            "bills": qbo_data.get("bills", []),
            "invoices": qbo_data.get("invoices", []),
            "synced_at": qbo_data.get("synced_at", datetime.utcnow().isoformat())
        }
    
    def get_test_drive_data(self) -> Dict[str, Any]:
        """
        Get QBO data formatted specifically for test_drive experience.
        
        Returns:
            Dict containing test_drive-specific QBO data
        """
        # Get raw QBO data using SmartSyncService
        qbo_data = self.smart_sync.get_qbo_data_for_digest()
        
        # Format for test_drive experience
        return {
            "bills": qbo_data.get("bills", []),
            "invoices": qbo_data.get("invoices", []),
            "balances": qbo_data.get("balances", []),
            "customers": qbo_data.get("customers", []),
            "vendors": qbo_data.get("vendors", []),
            "synced_at": qbo_data.get("synced_at", datetime.utcnow().isoformat())
        }
    
