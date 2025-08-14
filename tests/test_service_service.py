import pytest
from sqlalchemy.orm import Session
from services.service import ServiceService
from schemas.service import ServiceCreate

@pytest.fixture
def service_service(db: Session):
    return ServiceService(db)

def test_create_service(service_service, test_firm):
    service_data = ServiceCreate(
        name="Test Service",
        price=1000.0,
        task_sequence=[{"step_type": "reconcile", "micro_tasks": []}],
        tier="basic",
        firm_id=test_firm.firm_id
    )
    service = service_service.create_service(service_data)
    assert service.service_id is not None
    assert service.name == "Test Service"

def test_preview_service(service_service, test_firm, db: Session):
    service_data = ServiceCreate(
        name="Test Service",
        price=1000.0,
        task_sequence=[{"step_type": "reconcile", "micro_tasks": []}],
        tier="basic",
        firm_id=test_firm.firm_id
    )
    service = service_service.create_service(service_data)
    preview = service_service.preview_service(service.service_id, test_firm.firm_id)
    assert preview["service_id"] == service.service_id
    assert "compliance_requirements" in preview