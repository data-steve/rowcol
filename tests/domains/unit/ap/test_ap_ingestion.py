import pytest
from unittest.mock import patch, MagicMock
from domains.ap.services.ingest import IngestionService

def test_sync_bills_from_qbo(db, test_business):
    """Test syncing bills from QBO via SmartSyncService."""
    ingestion_service = IngestionService(db, test_business.business_id)
    
    # Mock SmartSyncService to return QBO bills data
    with patch.object(ingestion_service.smart_sync, 'sync_qbo_bills') as mock_sync:
        mock_sync.return_value = {
            "bills": [
                {
                    "Id": "qbo_bill_001",
                    "VendorRef": {"name": "Test Vendor 1"},
                    "TotalAmt": 150.00,
                    "DueDate": "2025-10-01"
                },
                {
                    "Id": "qbo_bill_002", 
                    "VendorRef": {"name": "Test Vendor 2"},
                    "TotalAmt": 250.00,
                    "DueDate": "2025-10-15"
                }
            ]
        }
        
        # Mock VendorNormalizationService
        with patch.object(ingestion_service.vendor_service, 'normalize_vendor') as mock_normalize:
            mock_normalize.return_value = MagicMock(id=1)
            
            # Call the method under test
            result = ingestion_service.sync_bills(test_business.business_id)
            
            # Verify the result
            assert result["status"] == "success"
            assert result["synced_bills"] == 2
            
            # Verify SmartSyncService was called
            mock_sync.assert_called_once()
            
            # Verify vendor normalization was called for each bill
            assert mock_normalize.call_count == 2

def test_ingestion_service_initialization(db, test_business):
    """Test IngestionService initialization."""
    service = IngestionService(db, test_business.business_id)
    
    assert service.db == db
    assert service.business_id == test_business.business_id
    assert service.smart_sync is not None
    assert service.vendor_service is not None

def test_parse_date_valid_string(db):
    """Test date parsing with valid string."""
    service = IngestionService(db)
    
    result = service._parse_date("2025-10-01")
    assert result is not None
    assert result.year == 2025
    assert result.month == 10
    assert result.day == 1

def test_parse_date_invalid_string(db):
    """Test date parsing with invalid string."""
    service = IngestionService(db)
    
    result = service._parse_date("invalid-date")
    assert result is None

def test_parse_date_none(db):
    """Test date parsing with None."""
    service = IngestionService(db)
    
    result = service._parse_date(None)
    assert result is None