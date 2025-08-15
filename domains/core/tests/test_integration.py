import pytest

def test_automation_routes(client, db):
    response = client.post("/api/automation/vendors/normalize", json={
        "raw_name": "Starbucks1234",
        "firm_id": "550e8400-e29b-41d4-a716-446655440000"
    })
    assert response.status_code == 200
    assert response.json()["canonical_name"] == "Starbucks"

    response = client.post("/api/automation/categorize", json={
        "txn_id": "txn_001",
        "description": "Starbucks",
        "amount": 10.50,
        "firm_id": "550e8400-e29b-41d4-a716-446655440000"
    })
    assert response.status_code == 200
    assert response.json()["txn_id"] == "txn_001"
