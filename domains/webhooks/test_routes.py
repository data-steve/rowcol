import pytest
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app
from dotenv import load_dotenv
import os
import stripe
import hmac
import hashlib
import json
import time

load_dotenv()

# Set testing environment variable
os.environ["TESTING"] = "true"

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
JOBBER_ACCESS_TOKEN = os.getenv("JOBBER_ACCESS_TOKEN")

@pytest.fixture
def client():
    return TestClient(app)

def test_jobber_webhook(client):
    """Test /webhooks/jobber endpoint."""
    payload = {
        "event": "client.create",
        "data": {
            "id": "client_001",
            "firstName": "Test",
            "lastName": "Client",
            "companyName": "Test Company"
        }
    }
    response = client.post("/webhooks/jobber", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "received"}

def test_stripe_webhook(client):
    """Test /webhooks/stripe endpoint."""
    payload = {
        "id": "evt_test_webhook",
        "type": "charge.succeeded",
        "data": {
            "object": {
                "id": "ch_001",
                "amount": 1000,
                "currency": "usd",
                "metadata": {"invoice_id": "INV-001"}
            }
        }
    }
    timestamp = int(time.time())
    payload_str = json.dumps(payload, separators=(",", ":"))
    signed_payload = f"{timestamp}.{payload_str}"
    signature = hmac.new(
        STRIPE_WEBHOOK_SECRET.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    headers = {
        "stripe-signature": f"t={timestamp},v1={signature}",
        "content-type": "application/json"
    }
    
    response = client.post("/webhooks/stripe", data=payload_str, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "received"}

def test_stripe_webhook_invalid_signature(client):
    """Test /webhooks/stripe with invalid signature."""
    payload = {
        "id": "evt_test_webhook",
        "type": "charge.succeeded",
        "data": {"object": {"id": "ch_001"}}
    }
    headers = {"stripe-signature": "t=123,v1=invalid_signature"}
    
    response = client.post("/webhooks/stripe", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid signature"

def test_jobber_callback(client):
    """Test /auth/jobber/callback endpoint."""
    response = client.get("/auth/jobber/callback?code=test_code")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "received"
    assert response_data["code"] == "test_code"
