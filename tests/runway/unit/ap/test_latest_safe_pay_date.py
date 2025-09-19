import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from domains.ap.services.bill_ingestion import BillService
from domains.ap.models.bill import Bill

@pytest.fixture
def bill_service(db, test_business):
    """Fixture to create a BillService instance."""
    return BillService(db=db, business_id=test_business.business_id)

def test_calculate_latest_safe_pay_date(bill_service):
    """
    Test the 'Latest Safe Pay Date' calculation.
    This is a unit test for a 'smart' product feature.
    """
    due_date = datetime(2025, 10, 15)
    bill = Bill(
        due_date=due_date,
        amount_cents=10000, # Use the column property
        status="pending"
    )
    
    # Standard grace period is 5 days
    expected_safe_date = due_date + timedelta(days=5)
    
    safe_date = bill_service.calculate_latest_safe_pay_date(bill)
    
    assert safe_date == expected_safe_date

def test_calculate_latest_safe_pay_date_no_due_date(bill_service):
    """Test that safe pay date is None if there is no due date."""
    bill = Bill(
        due_date=None,
        amount_cents=10000, # Use the column property
        status="pending"
    )
    
    safe_date = bill_service.calculate_latest_safe_pay_date(bill)
    
    assert safe_date is None
