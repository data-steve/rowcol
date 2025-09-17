import pytest
from unittest.mock import patch, MagicMock
from domains.ap.services.ingest import IngestionService
from domains.ap.models.bill import Bill as BillModel

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def ingestion_service(mock_db):
    return IngestionService(mock_db)

def test_sync_bills_from_qbo(ingestion_service, mock_db):
    # Mock the QuickBooks client
    with patch('domains.ap.services.ingest.QuickBooks') as mock_qbo_client:
        mock_qbo_instance = MagicMock()
        
        # Create mock QBO Bill objects
        mock_qbo_bill1 = MagicMock()
        mock_qbo_bill1.Id = "1"
        mock_qbo_bill1.VendorRef.name = "Vendor 1"
        mock_qbo_bill1.TotalAmt = 100.0
        mock_qbo_bill1.DueDate = "2025-10-01"

        mock_qbo_bill2 = MagicMock()
        mock_qbo_bill2.Id = "2"
        mock_qbo_bill2.VendorRef.name = "Vendor 2"
        mock_qbo_bill2.TotalAmt = 200.0
        mock_qbo_bill2.DueDate = "2025-10-15"
        
        # Use a class method mock for filter
        with patch('domains.ap.services.ingest.QBOBill.filter') as mock_bill_filter:
            mock_bill_filter.return_value = [mock_qbo_bill1, mock_qbo_bill2]
            mock_qbo_client.return_value = mock_qbo_instance

            # Mock VendorNormalizationService
            with patch('domains.ap.services.ingest.VendorNormalizationService') as mock_vendor_service:
                mock_vendor_instance = MagicMock()
                # Assume normalize_vendor returns a mock schema object
                mock_vendor_instance.normalize_vendor.return_value = MagicMock(vendor_id=1)
                mock_vendor_service.return_value = mock_vendor_instance

                # Call the method under test
                ingestion_service.sync_bills("test_business_id")

                # Assert that bills were queried from QBO
                mock_bill_filter.assert_called_once_with(qb=mock_qbo_instance)
                
                # Assert that bills were added to the database
                assert mock_db.add.call_count == 2
                mock_db.commit.assert_called() # Called once at the end