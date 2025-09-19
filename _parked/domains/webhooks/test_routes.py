import pytest
from fastapi.testclient import TestClient

from main import app  # Import your FastAPI app
from dotenv import load_dotenv
import os

load_dotenv()

# Set testing environment variable
os.environ["TESTING"] = "true"

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
JOBBER_ACCESS_TOKEN = os.getenv("JOBBER_ACCESS_TOKEN")

@pytest.fixture
def client():
    return TestClient(app)


# def test_stripe_webhook(client):
#     """Test /webhooks/stripe endpoint."""
#     payload = {
#         "id": "evt_test_webhook",
#         "type": "charge.succeeded",
#         "data": {
#             "object": {
#                 "id": "ch_001",
#                 "amount": 1000,
#                 "currency": "usd",
#                 "metadata": {"invoice_id": "INV-001"}
#             }
#         }
#     }
#     timestamp = int(time.time())
#     payload_str = json.dumps(payload, separators=(",", ":"))
#     signed_payload = f"{timestamp}.{payload_str}"
#     signature = hmac.new(
#         STRIPE_WEBHOOK_SECRET.encode(),
#         signed_payload.encode(),
#         hashlib.sha256
#     ).hexdigest()
#     headers = {
#         "stripe-signature": f"t={timestamp},v1={signature}",
#         "content-type": "application/json"
#     }
    
#     response = client.post("/webhooks/stripe", data=payload_str, headers=headers)
#     assert response.status_code == 200
#     assert response.json() == {"status": "received"}

# def test_stripe_webhook_invalid_signature(client):
#     """Test /webhooks/stripe with invalid signature."""
#     payload = {
#         "id": "evt_test_webhook",
#         "type": "charge.succeeded",
#         "data": {"object": {"id": "ch_001"}}
#     }
#     headers = {"stripe-signature": "t=123,v1=invalid_signature"}
    
#     response = client.post("/webhooks/stripe", json=payload, headers=headers)
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Invalid signature"
