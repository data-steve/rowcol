import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from domains.ap.services.bill_ingestion import BillService
from domains.ap.models.bill import Bill

@pytest.fixture
def bill_service(db, test_business):
    """Fixture to create a BillService instance."""
    return BillService(db=db, business_id=test_business.business_id)

def test_runway_impact_suggestion_delayable_bill(bill_service):
    """
    Test the runway impact suggestion for a bill that can be safely delayed.
    This is a unit test for a 'Connective Intelligence' feature.
    """
    due_date = datetime.utcnow() + timedelta(days=10)
    bill = Bill(
        due_date=due_date,
        amount_cents=500000, # Use the column property
        status="approved"
    )
    
    suggestion = bill_service.get_runway_impact_suggestion(bill, runway_days=30)
    
    assert "protect" in suggestion["recommendation"]
    assert suggestion["impact_days"] == 5  # Based on placeholder $1000/day burn rate
    assert suggestion["confidence"] > 0.8

def test_runway_impact_suggestion_overdue_bill(bill_service):
    """Test the runway impact suggestion for an overdue bill."""
    due_date = datetime.utcnow() - timedelta(days=5)
    bill = Bill(
        due_date=due_date,
        amount_cents=200000, # Use the column property
        status="approved"
    )
    
    suggestion = bill_service.get_runway_impact_suggestion(bill, runway_days=30)
    
    assert "cost" in suggestion["recommendation"]
    assert suggestion["impact_days"] == 2
    assert suggestion["confidence"] > 0.9
