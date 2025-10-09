import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from domains.ap.services.bill import BillService
from domains.ap.models.bill import Bill, BillPriority

@pytest.fixture
def bill_service(db, test_business):
    """Fixture to create a BillService instance."""
    return BillService(db=db, business_id=test_business.business_id)

def test_payment_priority_intelligence_overdue(bill_service):
    """
    Test that an overdue bill is marked as URGENT.
    This is a test for a 'Workflow Intelligence' feature.
    """
    bill = Bill(
        due_date=datetime.utcnow() - timedelta(days=1),
        amount_cents=10000 # Use the column property
    )
    priority = bill_service.calculate_bill_priority(bill)
    assert priority == BillPriority.URGENT

def test_payment_priority_intelligence_high_amount(bill_service):
    """Test that a high-amount bill is marked as HIGH priority."""
    bill = Bill(
        due_date=datetime.utcnow() + timedelta(days=30),
        amount_cents=500100 # Use the column property
    )
    priority = bill_service.calculate_bill_priority(bill)
    assert priority == BillPriority.HIGH

def test_payment_priority_intelligence_due_soon(bill_service):
    """Test that a bill due soon is marked as HIGH priority."""
    bill = Bill(
        due_date=datetime.utcnow() + timedelta(days=3),
        amount_cents=50000 # Use the column property
    )
    priority = bill_service.calculate_bill_priority(bill)
    assert priority == BillPriority.HIGH

def test_payment_priority_intelligence_medium(bill_service):
    """Test that a bill with a moderate due date is MEDIUM priority."""
    bill = Bill(
        due_date=datetime.utcnow() + timedelta(days=15),
        amount_cents=50000 # Use the column property
    )
    priority = bill_service.calculate_bill_priority(bill)
    assert priority == BillPriority.MEDIUM
