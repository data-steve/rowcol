from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_service(test_firm):
    service_data = {
        "name": "Test Service",
        "price": 1000.0,
        "task_sequence": [{"step_type": "intake", "micro_tasks": []}],
        "tier": "basic",
        "firm_id": test_firm.firm_id
    }
    response = client.post("/api/services", json=service_data)
    assert response.status_code == 200
    assert response.json()["service_id"] is not None

def test_preview_service(test_firm, test_service):
    response = client.get(f"/api/services/{test_service.service_id}/preview?firm_id={test_service.firm_id}")
    assert response.status_code == 200
    assert len(response.json()["compliance_requirements"]) > 0