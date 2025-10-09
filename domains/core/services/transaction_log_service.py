"""
TransactionLogService - Service for managing transaction logs.

Provides methods for creating and managing immutable transaction logs
for all domain objects, supporting compliance and audit requirements.

Key Features:
- Immutable transaction log creation
- Change tracking and diff calculation
- Multi-rail source attribution
- SOC2 compliance audit trails
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
import json
import uuid

from domains.ap.models_trans.bill_transaction_log import BillTransactionLog
from domains.ap.models_trans.vendor_transaction_log import VendorTransactionLog
from domains.ap.models_trans.payment_transaction_log import PaymentTransactionLog


class TransactionLogService:
    """
    Service for managing immutable transaction logs.
    
    This service provides methods for creating transaction logs for all domain objects,
    supporting compliance requirements and multi-rail reconciliation.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def _calculate_changes(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate changes between old and new data."""
        changes = {}
        
        # Compare all fields
        all_keys = set(old_data.keys()) | set(new_data.keys())
        
        for key in all_keys:
            old_value = old_data.get(key)
            new_value = new_data.get(key)
            
            if old_value != new_value:
                changes[key] = {
                    "old_value": old_value,
                    "new_value": new_value
                }
        
        return changes
    
    def _serialize_model_data(self, model_instance) -> Dict[str, Any]:
        """Serialize a model instance to JSON-serializable data."""
        if not model_instance:
            return {}
        
        # Get all column attributes
        mapper = inspect(model_instance)
        data = {}
        
        for column in mapper.attrs:
            if hasattr(column, 'key'):
                value = getattr(model_instance, column.key)
                
                # Convert datetime to ISO format
                if isinstance(value, datetime):
                    data[column.key] = value.isoformat()
                # Convert other non-serializable types
                elif hasattr(value, '__dict__'):
                    data[column.key] = str(value)
                else:
                    data[column.key] = value
        
        return data
    
    async def create_bill_transaction_log(
        self,
        bill_id: int,
        transaction_type: str,
        source: str,
        bill_data: Dict[str, Any],
        changes: Optional[Dict[str, Any]] = None,
        created_by_user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        external_id: Optional[str] = None,
        external_sync_token: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BillTransactionLog:
        """Create a transaction log entry for a bill."""
        
        transaction_log = BillTransactionLog(
            bill_id=bill_id,
            transaction_type=transaction_type,
            source=source,
            bill_data=bill_data,
            changes=changes,
            created_at=datetime.utcnow(),
            created_by_user_id=created_by_user_id,
            session_id=session_id,
            external_id=external_id,
            external_sync_token=external_sync_token,
            reason=reason,
            metadata=metadata
        )
        
        self.db.add(transaction_log)
        self.db.commit()
        self.db.refresh(transaction_log)
        
        return transaction_log
    
    async def create_vendor_transaction_log(
        self,
        vendor_id: int,
        transaction_type: str,
        source: str,
        vendor_data: Dict[str, Any],
        changes: Optional[Dict[str, Any]] = None,
        created_by_user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        external_id: Optional[str] = None,
        external_sync_token: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> VendorTransactionLog:
        """Create a transaction log entry for a vendor."""
        
        transaction_log = VendorTransactionLog(
            vendor_id=vendor_id,
            transaction_type=transaction_type,
            source=source,
            vendor_data=vendor_data,
            changes=changes,
            created_at=datetime.utcnow(),
            created_by_user_id=created_by_user_id,
            session_id=session_id,
            external_id=external_id,
            external_sync_token=external_sync_token,
            reason=reason,
            metadata=metadata
        )
        
        self.db.add(transaction_log)
        self.db.commit()
        self.db.refresh(transaction_log)
        
        return transaction_log
    
    async def create_payment_transaction_log(
        self,
        payment_id: int,
        transaction_type: str,
        source: str,
        payment_data: Dict[str, Any],
        changes: Optional[Dict[str, Any]] = None,
        created_by_user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        external_id: Optional[str] = None,
        external_sync_token: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentTransactionLog:
        """Create a transaction log entry for a payment."""
        
        transaction_log = PaymentTransactionLog(
            payment_id=payment_id,
            transaction_type=transaction_type,
            source=source,
            payment_data=payment_data,
            changes=changes,
            created_at=datetime.utcnow(),
            created_by_user_id=created_by_user_id,
            session_id=session_id,
            external_id=external_id,
            external_sync_token=external_sync_token,
            reason=reason,
            metadata=metadata
        )
        
        self.db.add(transaction_log)
        self.db.commit()
        self.db.refresh(transaction_log)
        
        return transaction_log
    
    async def log_bill_sync(
        self,
        bill,
        qbo_bill_data: Dict[str, Any],
        source: str = "qbo",
        created_by_user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BillTransactionLog:
        """Log a bill sync operation with change tracking."""
        
        # Serialize current bill data
        current_bill_data = self._serialize_model_data(bill)
        
        # Calculate changes
        changes = self._calculate_changes(current_bill_data, qbo_bill_data)
        
        # Create transaction log
        return await self.create_bill_transaction_log(
            bill_id=bill.bill_id,
            transaction_type="synced",
            source=source,
            bill_data=qbo_bill_data,
            changes=changes,
            created_by_user_id=created_by_user_id,
            session_id=session_id,
            external_id=qbo_bill_data.get("Id"),
            external_sync_token=qbo_bill_data.get("SyncToken"),
            reason="Sync from external system"
        )
    
    async def log_vendor_sync(
        self,
        vendor,
        qbo_vendor_data: Dict[str, Any],
        source: str = "qbo",
        created_by_user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> VendorTransactionLog:
        """Log a vendor sync operation with change tracking."""
        
        # Serialize current vendor data
        current_vendor_data = self._serialize_model_data(vendor)
        
        # Calculate changes
        changes = self._calculate_changes(current_vendor_data, qbo_vendor_data)
        
        # Create transaction log
        return await self.create_vendor_transaction_log(
            vendor_id=vendor.vendor_id,
            transaction_type="synced",
            source=source,
            vendor_data=qbo_vendor_data,
            changes=changes,
            created_by_user_id=created_by_user_id,
            session_id=session_id,
            external_id=qbo_vendor_data.get("Id"),
            external_sync_token=qbo_vendor_data.get("SyncToken"),
            reason="Sync from external system"
        )
    
    async def log_payment_sync(
        self,
        payment,
        qbo_payment_data: Dict[str, Any],
        source: str = "qbo",
        created_by_user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> PaymentTransactionLog:
        """Log a payment sync operation with change tracking."""
        
        # Serialize current payment data
        current_payment_data = self._serialize_model_data(payment)
        
        # Calculate changes
        changes = self._calculate_changes(current_payment_data, qbo_payment_data)
        
        # Create transaction log
        return await self.create_payment_transaction_log(
            payment_id=payment.payment_id,
            transaction_type="synced",
            source=source,
            payment_data=qbo_payment_data,
            changes=changes,
            created_by_user_id=created_by_user_id,
            session_id=session_id,
            external_id=qbo_payment_data.get("Id"),
            external_sync_token=qbo_payment_data.get("SyncToken"),
            reason="Sync from external system"
        )
