from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_engagement(test_firm, test_client, test_service):
    engagement_data = {
        "firm_id": test_firm.firm_id,
        "client_id": test_client.client_id,
        "service_type": "bookkeeping",
        "due_date": "2025-12-31T23:59:59",
        "user_input": {"qbo_account": "12345"}
    }
    response = client.post("/api/engagements", json=engagement_data)
    assert response.status_code == 200
    assert response.json()["engagement_id"] is not None

def test_sign_engagement(test_engagement):
    response = client.post(
        f"/api/engagements/{test_engagement.engagement_id}/sign?firm_id={test_engagement.firm_id}",
        json={"signer_id": 1, "signature_data": "/s/John Doe"}
    )
    assert response.status_code == 200
    assert response.json()["e_signature"]["signature_data"] == "/s/John Doe"