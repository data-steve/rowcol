import pytest
from unittest.mock import patch, MagicMock
from domains.ap.services.bill import BillService
import asyncio
from domains.core.models import Business


# NOTE: Sync operations moved to QBOSyncService
# This test is outdated - sync methods removed from BillService
# Use domains/qbo/services/sync_service.py for QBO sync operations

def test_bill_service_initialization(db, test_business):
    """Test BillService initialization."""
    service = BillService(db, test_business.business_id)
    
    assert service.db == db
    assert service.business_id == test_business.business_id

def test_parse_date_valid_string(db, test_business):
    """Test date parsing with valid string."""
    service = BillService(db, test_business.business_id)
    
    result = service._parse_date("2025-10-01")
    assert result is not None
    assert result.year == 2025
    assert result.month == 10
    assert result.day == 1

def test_parse_date_invalid_string(db, test_business):
    """Test date parsing with invalid string."""
    service = BillService(db, test_business.business_id)
    
    result = service._parse_date("invalid-date")
    assert result is None

def test_parse_date_none(db, test_business):
    """Test date parsing with None."""
    service = BillService(db, test_business.business_id)
    
    result = service._parse_date(None)
    assert result is None