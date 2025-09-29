from sqlalchemy.orm import Session
from runway.experiences.tray import TrayService
from runway.models.tray_item import TrayItem
from datetime import datetime
import pytest

@pytest.fixture
def test_tray_service():
    """Fixture for test tray service."""
    # This would be properly initialized with test database in real tests
    return None

def test_tray_service_initialization(db: Session, test_business):
    """Test TrayService can be initialized."""
    tray_service = TrayService(db, business_id=test_business.business_id)
    assert tray_service is not None
    assert tray_service.business_id == test_business.business_id

def test_tray_service_has_data_orchestrator(db: Session, test_business):
    """Test TrayService has data orchestrator."""
    tray_service = TrayService(db, business_id=test_business.business_id)
    assert hasattr(tray_service, 'data_orchestrator')
    assert tray_service.data_orchestrator is not None