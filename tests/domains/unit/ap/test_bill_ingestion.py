from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta
from main import app
from domains.ap.services.bill_ingestion import BillService
from domains.ap.models.bill import Bill as BillModel, BillStatus, BillPriority
from domains.ap.models.vendor import Vendor

client = TestClient(app)

def test_bill_service_initialization(db, test_business):
    """Test that BillService can be initialized properly."""
    bill_service = BillService(db, test_business.business_id, validate_business=False)
    assert bill_service is not None
    assert bill_service.business_id == test_business.business_id

def test_calculate_bill_priority_overdue(db, test_business):
    """Test bill priority calculation for overdue bills."""
    bill_service = BillService(db, test_business.business_id, validate_business=False)
    
    # Create overdue bill
    overdue_bill = BillModel(
        business_id=test_business.business_id,
        bill_id="test_overdue_001",
        amount_cents=250000,  # $2500
        due_date=datetime.utcnow() - timedelta(days=5),
        status=BillStatus.PENDING
    )
    
    priority = bill_service.calculate_bill_priority(overdue_bill)
    assert priority == BillPriority.URGENT

def test_calculate_bill_priority_high_amount(db, test_business):
    """Test bill priority calculation for high-amount bills."""
    bill_service = BillService(db, test_business.business_id, validate_business=False)
    
    # Create high-amount bill due in 30 days
    high_amount_bill = BillModel(
        business_id=test_business.business_id,
        bill_id="test_high_amount_001",
        amount_cents=600000,  # $6000 - above HIGH_AMOUNT_THRESHOLD
        due_date=datetime.utcnow() + timedelta(days=30),
        status=BillStatus.PENDING
    )
    
    priority = bill_service.calculate_bill_priority(high_amount_bill)
    assert priority == BillPriority.HIGH

def test_is_bill_overdue(db, test_business):
    """Test overdue bill detection."""
    bill_service = BillService(db, test_business.business_id, validate_business=False)
    
    # Overdue bill
    overdue_bill = BillModel(
        business_id=test_business.business_id,
        bill_id="test_overdue_002",
        amount_cents=100000,
        due_date=datetime.utcnow() - timedelta(days=1),
        status=BillStatus.PENDING
    )
    
    # Not overdue bill
    future_bill = BillModel(
        business_id=test_business.business_id,
        bill_id="test_future_001",
        amount_cents=100000,
        due_date=datetime.utcnow() + timedelta(days=1),
        status=BillStatus.PENDING
    )
    
    assert bill_service.is_bill_overdue(overdue_bill)
    assert not bill_service.is_bill_overdue(future_bill)

@patch('domains.ap.services.bill_ingestion.get_document_processor')
def test_ingest_document(mock_get_processor, db, test_business):
    """Test document ingestion functionality."""
    # Mock document processor
    mock_processor = MagicMock()
    mock_processor.extract_bill_data.return_value = {
        'amount': 150.00,
        'due_date': datetime.utcnow() + timedelta(days=30),
        'vendor_name': 'Test Vendor',
        'invoice_number': 'INV-001'
    }
    mock_get_processor.return_value = mock_processor
    
    bill_service = BillService(db, test_business.business_id, validate_business=False)
    
    # Test document ingestion
    file_data = b"fake pdf content"
    filename = "test_invoice.pdf"
    
    with patch.object(bill_service, '_create_bill_from_document') as mock_create:
        mock_bill = BillModel(
            business_id=test_business.business_id,
            bill_id="test_ingested_001",
            amount_cents=15000
        )
        mock_create.return_value = mock_bill
        
        result = bill_service.ingest_document(file_data, filename)
        
        assert result == mock_bill
        mock_processor.extract_bill_data.assert_called_once_with(file_data, filename)
        mock_create.assert_called_once()