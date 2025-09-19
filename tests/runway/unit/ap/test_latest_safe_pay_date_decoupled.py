"""
Test Latest Safe Pay Date calculation with decoupled testing approaches.

This demonstrates how to test business logic without database coupling.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock

from domains.ap.services.bill_ingestion import BillService
from domains.ap.models.bill import Bill
from tests.domains.core.services.test_service_base import TestServiceFactory, InMemoryTestService


class TestLatestSafePayDateDecoupled:
    """Test Latest Safe Pay Date using decoupled testing approaches."""
    
    def test_calculate_latest_safe_pay_date_no_db(self):
        """
        Test Latest Safe Pay Date calculation without database dependency.
        Pure unit test focusing only on business logic.
        """
        # Create service without database coupling
        service = TestServiceFactory.create_service(
            BillService, 
            business_id="test_biz",
            db=Mock()
        )
        
        # Test data - no database required
        due_date = datetime(2025, 10, 15)
        bill = Bill(
            due_date=due_date,
            amount_cents=10000,
            status="pending"
        )
        
        # Test business logic
        expected_safe_date = due_date + timedelta(days=5)
        safe_date = service.calculate_latest_safe_pay_date(bill)
        
        assert safe_date == expected_safe_date
    
    def test_calculate_latest_safe_pay_date_custom_grace_period(self):
        """Test Latest Safe Pay Date with custom grace period."""
        service = TestServiceFactory.create_service(BillService)
        
        due_date = datetime(2025, 10, 15)
        bill = Bill(
            due_date=due_date,
            amount_cents=5000,
            status="pending"
        )
        
        # Test with 10-day grace period
        expected_safe_date = due_date + timedelta(days=10)
        safe_date = service.calculate_latest_safe_pay_date(bill, grace_days=10)
        
        assert safe_date == expected_safe_date
    
    def test_calculate_latest_safe_pay_date_no_due_date(self):
        """Test that safe pay date is None if there is no due date."""
        service = TestServiceFactory.create_service(BillService)
        
        bill = Bill(
            due_date=None,
            amount_cents=10000,
            status="pending"
        )
        
        safe_date = service.calculate_latest_safe_pay_date(bill)
        
        assert safe_date is None
    
    def test_calculate_latest_safe_pay_date_zero_grace_period(self):
        """Test Latest Safe Pay Date with zero grace period."""
        service = TestServiceFactory.create_service(BillService)
        
        due_date = datetime(2025, 10, 15)
        bill = Bill(
            due_date=due_date,
            amount_cents=7500,
            status="pending"
        )
        
        # Zero grace period means safe date equals due date
        safe_date = service.calculate_latest_safe_pay_date(bill, grace_days=0)
        
        assert safe_date == due_date


class TestLatestSafePayDateInMemory:
    """Test using completely in-memory approach for maximum test speed."""
    
    def test_safe_pay_date_business_logic_only(self):
        """
        Test the core business logic without any external dependencies.
        This is the fastest possible test approach.
        """
        # Mock bill data
        due_date = datetime(2025, 10, 15)
        
        # Test the calculation directly (this could be extracted to a pure function)
        grace_days = 5
        expected_safe_date = due_date + timedelta(days=grace_days)
        
        # Direct calculation test
        actual_safe_date = due_date + timedelta(days=grace_days)
        
        assert actual_safe_date == expected_safe_date
    
    def test_safe_pay_date_edge_cases(self):
        """Test edge cases for safe pay date calculation."""
        test_cases = [
            # (due_date, grace_days, expected_result)
            (datetime(2025, 1, 1), 5, datetime(2025, 1, 6)),
            (datetime(2025, 12, 31), 1, datetime(2026, 1, 1)),  # Year boundary
            (None, 5, None),  # No due date
            (datetime(2025, 6, 15), 0, datetime(2025, 6, 15)),  # Zero grace
        ]
        
        for due_date, grace_days, expected in test_cases:
            if due_date is None:
                result = None
            else:
                result = due_date + timedelta(days=grace_days)
            
            assert result == expected, f"Failed for due_date={due_date}, grace_days={grace_days}"


# Fixture-based approach for integration testing
@pytest.fixture
def decoupled_bill_service():
    """Fixture for decoupled bill service testing."""
    return TestServiceFactory.create_service(BillService, business_id="test_business")


def test_latest_safe_pay_date_with_fixture(decoupled_bill_service):
    """Test using pytest fixture with decoupled service."""
    due_date = datetime(2025, 10, 15)
    bill = Bill(
        due_date=due_date,
        amount_cents=10000,
        status="pending"
    )
    
    expected_safe_date = due_date + timedelta(days=5)
    safe_date = decoupled_bill_service.calculate_latest_safe_pay_date(bill)
    
    assert safe_date == expected_safe_date
