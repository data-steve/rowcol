import pytest
from unittest.mock import patch, MagicMock
from domains.ap.services.ap_ingestion import IngestionService

@pytest.mark.asyncio
async def test_sync_bills_from_qbo(db, test_business):
    """Test syncing bills from QBO via SmartSyncService."""
    ingestion_service = IngestionService(db, test_business.business_id)
    
    # Mock SmartSyncService to return QBO bills data
    with patch('domains.integrations.smart_sync.SmartSyncService.sync_qbo_data') as mock_sync:
        mock_sync.return_value = {
            "status": "success",
            "synced_bills": 2,
            "synced_invoices": 0,
            "timestamp": "2025-09-22T23:00:00"
        }
        
        # Mock VendorNormalizationService
        with patch.object(ingestion_service.vendor_service, 'normalize_vendor') as mock_normalize:
            mock_normalize.return_value = MagicMock(id=1)
            
            # Call the method under test
            result = await ingestion_service.sync_bills(test_business.business_id)
            
            # Verify the result
            assert result["status"] == "success"
            assert result["synced_bills"] == 2
            
            # Verify SmartSyncService was called
            mock_sync.assert_called_once()
            
            # Note: Current implementation doesn't call vendor normalization directly
            # as it delegates to BillService for individual bill processing

def test_ingestion_service_initialization(db, test_business):
    """Test IngestionService initialization."""
    service = IngestionService(db, test_business.business_id)
    
    assert service.db == db
    assert service.business_id == test_business.business_id
    assert service.smart_sync is not None
    assert service.vendor_service is not None

def test_parse_date_valid_string(db, test_business):
    """Test date parsing with valid string."""
    service = IngestionService(db, test_business.business_id)
    
    result = service._parse_date("2025-10-01")
    assert result is not None
    assert result.year == 2025
    assert result.month == 10
    assert result.day == 1

def test_parse_date_invalid_string(db, test_business):
    """Test date parsing with invalid string."""
    service = IngestionService(db, test_business.business_id)
    
    result = service._parse_date("invalid-date")
    assert result is None

def test_parse_date_none(db, test_business):
    """Test date parsing with None."""
    service = IngestionService(db, test_business.business_id)
    
    result = service._parse_date(None)
    assert result is None