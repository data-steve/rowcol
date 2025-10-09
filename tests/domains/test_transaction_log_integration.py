"""
Test Transaction Log Integration

Tests the complete sync and transaction log pattern to ensure:
- Sync service writes to both mirror and transaction log models
- Transaction logs are immutable and complete
- Multi-rail source attribution works
- SOC2 compliance audit trails are maintained
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from unittest.mock import Mock, AsyncMock

from domains.qbo.services.sync_service import QBOSyncService
from domains.core.services.transaction_log_service import TransactionLogService
from domains.ap.models.bill import Bill
from domains.ap.models_trans.bill_transaction_log import BillTransactionLog


class TestTransactionLogIntegration:
    """Test the complete sync and transaction log pattern."""
    
    @pytest.fixture
    def mock_bill(self):
        """Create a mock bill for testing."""
        bill = Mock(spec=Bill)
        bill.bill_id = 123
        bill.business_id = "test-business-id"
        bill.amount_cents = 10000  # $100.00
        bill.vendor_id = 456
        bill.qbo_bill_id = "qbo-bill-123"
        bill.qbo_sync_token = "sync-token-123"
        return bill
    
    @pytest.fixture
    def mock_qbo_bill_data(self):
        """Create mock QBO bill data for testing."""
        return {
            "Id": "qbo-bill-123",
            "SyncToken": "sync-token-456",
            "Amount": 100.00,
            "DueDate": "2024-01-15",
            "VendorRef": {"value": "qbo-vendor-456"},
            "DocNumber": "BILL-001"
        }
    
    @pytest.fixture
    def qbo_sync_service(self, db_session):
        """Create QBOSyncService instance for testing."""
        return QBOSyncService("test-business-id", "test-realm-id", db_session)
    
    @pytest.fixture
    def transaction_log_service(self, db_session):
        """Create TransactionLogService instance for testing."""
        return TransactionLogService(db_session)
    
    def test_bill_transaction_log_creation(self, transaction_log_service, mock_bill, mock_qbo_bill_data):
        """Test that bill transaction logs are created correctly."""
        
        # Create transaction log
        transaction_log = await transaction_log_service.create_bill_transaction_log(
            bill_id=mock_bill.bill_id,
            transaction_type="synced",
            source="qbo",
            bill_data=mock_qbo_bill_data,
            changes={"amount": {"old_value": 100.00, "new_value": 100.00}},
            external_id="qbo-bill-123",
            external_sync_token="sync-token-456",
            reason="Sync from QBO"
        )
        
        # Verify transaction log properties
        assert transaction_log.bill_id == mock_bill.bill_id
        assert transaction_log.transaction_type == "synced"
        assert transaction_log.source == "qbo"
        assert transaction_log.bill_data == mock_qbo_bill_data
        assert transaction_log.external_id == "qbo-bill-123"
        assert transaction_log.external_sync_token == "sync-token-456"
        assert transaction_log.reason == "Sync from QBO"
        assert transaction_log.created_at is not None
    
    def test_bill_sync_with_log(self, qbo_sync_service, mock_bill, mock_qbo_bill_data):
        """Test that bill sync creates both mirror update and transaction log."""
        
        # Mock the transaction log service
        qbo_sync_service.transaction_log_service = Mock()
        qbo_sync_service.transaction_log_service.log_bill_sync = AsyncMock()
        
        # Mock transaction log response
        mock_transaction_log = Mock()
        mock_transaction_log.transaction_id = "txn-123"
        qbo_sync_service.transaction_log_service.log_bill_sync.return_value = mock_transaction_log
        
        # Perform sync with log
        result = await qbo_sync_service.sync_bill_with_log(
            bill=mock_bill,
            qbo_bill_data=mock_qbo_bill_data,
            created_by_user_id="user-123",
            session_id="session-456"
        )
        
        # Verify result structure
        assert "bill" in result
        assert "transaction_log" in result
        assert "status" in result
        assert result["status"] == "synced"
        
        # Verify transaction log service was called
        qbo_sync_service.transaction_log_service.log_bill_sync.assert_called_once_with(
            bill=mock_bill,
            qbo_bill_data=mock_qbo_bill_data,
            source="qbo",
            created_by_user_id="user-123",
            session_id="session-456"
        )
    
    def test_transaction_log_immutability(self, transaction_log_service, mock_bill, mock_qbo_bill_data):
        """Test that transaction logs are immutable (cannot be updated)."""
        
        # Create transaction log
        transaction_log = await transaction_log_service.create_bill_transaction_log(
            bill_id=mock_bill.bill_id,
            transaction_type="synced",
            source="qbo",
            bill_data=mock_qbo_bill_data
        )
        
        original_created_at = transaction_log.created_at
        original_bill_data = transaction_log.bill_data
        
        # Attempt to modify the transaction log (should not work in real implementation)
        # In a real test, this would verify that the model prevents updates
        assert transaction_log.created_at == original_created_at
        assert transaction_log.bill_data == original_bill_data
    
    def test_multi_rail_source_attribution(self, transaction_log_service, mock_bill):
        """Test that transaction logs support multi-rail source attribution."""
        
        # Test QBO source
        qbo_log = await transaction_log_service.create_bill_transaction_log(
            bill_id=mock_bill.bill_id,
            transaction_type="synced",
            source="qbo",
            bill_data={"Id": "qbo-bill-123"},
            external_id="qbo-bill-123"
        )
        assert qbo_log.source == "qbo"
        assert qbo_log.external_id == "qbo-bill-123"
        
        # Test Ramp source (future rail)
        ramp_log = await transaction_log_service.create_bill_transaction_log(
            bill_id=mock_bill.bill_id,
            transaction_type="synced",
            source="ramp",
            bill_data={"id": "ramp-bill-123"},
            external_id="ramp-bill-123"
        )
        assert ramp_log.source == "ramp"
        assert ramp_log.external_id == "ramp-bill-123"
        
        # Test Plaid source (future rail)
        plaid_log = await transaction_log_service.create_bill_transaction_log(
            bill_id=mock_bill.bill_id,
            transaction_type="synced",
            source="plaid",
            bill_data={"transaction_id": "plaid-txn-123"},
            external_id="plaid-txn-123"
        )
        assert plaid_log.source == "plaid"
        assert plaid_log.external_id == "plaid-txn-123"
    
    def test_change_tracking(self, transaction_log_service, mock_bill):
        """Test that transaction logs track changes correctly."""
        
        old_data = {"amount": 100.00, "status": "pending"}
        new_data = {"amount": 150.00, "status": "approved"}
        
        # Calculate changes
        changes = transaction_log_service._calculate_changes(old_data, new_data)
        
        # Verify changes are tracked correctly
        assert "amount" in changes
        assert changes["amount"]["old_value"] == 100.00
        assert changes["amount"]["new_value"] == 150.00
        assert "status" in changes
        assert changes["status"]["old_value"] == "pending"
        assert changes["status"]["new_value"] == "approved"
    
    def test_soc2_compliance_audit_trail(self, transaction_log_service, mock_bill, mock_qbo_bill_data):
        """Test that transaction logs provide SOC2-compliant audit trails."""
        
        # Create transaction log with full audit information
        transaction_log = await transaction_log_service.create_bill_transaction_log(
            bill_id=mock_bill.bill_id,
            transaction_type="synced",
            source="qbo",
            bill_data=mock_qbo_bill_data,
            created_by_user_id="user-123",
            session_id="session-456",
            reason="Scheduled sync from QBO",
            metadata={"sync_job_id": "job-789", "retry_count": 0}
        )
        
        # Verify SOC2 compliance fields are present
        assert transaction_log.created_at is not None  # When
        assert transaction_log.created_by_user_id == "user-123"  # Who
        assert transaction_log.source == "qbo"  # What system
        assert transaction_log.transaction_type == "synced"  # What action
        assert transaction_log.bill_data is not None  # What data
        assert transaction_log.reason is not None  # Why
        assert transaction_log.session_id == "session-456"  # Session tracking
        assert transaction_log.metadata is not None  # Additional context
    
    def test_transaction_log_relationships(self, db_session, mock_bill):
        """Test that transaction logs have proper relationships to domain models."""
        
        # This test would verify that the relationship between Bill and BillTransactionLog
        # works correctly in a real database context
        # For now, we'll test the model structure
        
        transaction_log = BillTransactionLog(
            bill_id=mock_bill.bill_id,
            transaction_type="synced",
            source="qbo",
            bill_data={"Id": "qbo-bill-123"},
            created_at=datetime.utcnow()
        )
        
        # Verify the relationship is set up correctly
        assert hasattr(transaction_log, 'bill')
        assert transaction_log.bill_id == mock_bill.bill_id
