import pytest
import requests
from database import SessionLocal
from scripts.setup_sandboxes import setup_qbo_sandbox, setup_jobber_sandbox, setup_stripe_sandbox
import stripe
from dotenv import load_dotenv
import os

load_dotenv()

QBO_ACCESS_TOKEN = os.getenv("QBO_ACCESS_TOKEN")
QBO_REALM_ID = os.getenv("QBO_REALM_ID")
QBO_SANDBOX_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company"
JOBBER_ACCESS_TOKEN = os.getenv("JOBBER_ACCESS_TOKEN")
JOBBER_API_URL = "https://api.getjobber.com/api"
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def test_setup_qbo_sandbox(db_session):
    """Test QBO sandbox setup: 100 txns, 10 jobs, 50 vendors."""
    result = setup_qbo_sandbox(db_session)
    assert result["integration_id"] == "qbo_001"

    headers = {"Authorization": f"Bearer {QBO_ACCESS_TOKEN}", "Accept": "application/json"}
    
    # Verify 100 transactions (50 deposits, 50 expenses)
    response = requests.get(f"{QBO_SANDBOX_URL}/{QBO_REALM_ID}/query?query=SELECT * FROM Deposit", headers=headers)
    assert len(response.json().get("QueryResponse", {}).get("Deposit", [])) == 50
    response = requests.get(f"{QBO_SANDBOX_URL}/{QBO_REALM_ID}/query?query=SELECT * FROM Purchase", headers=headers)
    assert len(response.json().get("QueryResponse", {}).get("Purchase", [])) == 50

    # Verify 10 jobs (Classes)
    response = requests.get(f"{QBO_SANDBOX_URL}/{QBO_REALM_ID}/query?query=SELECT * FROM Class", headers=headers)
    assert len(response.json().get("QueryResponse", {}).get("Class", [])) == 10

    # Verify 50 vendors
    response = requests.get(f"{QBO_SANDBOX_URL}/{QBO_REALM_ID}/query?query=SELECT * FROM Vendor", headers=headers)
    assert len(response.json().get("QueryResponse", {}).get("Vendor", [])) == 50

def test_setup_jobber_sandbox(db_session):
    """Test Jobber sandbox setup: 50 clients, 10 jobs, 20 invoices, 5 payments, 20 expenses, 10 timesheets."""
    result = setup_jobber_sandbox(db_session)
    assert result["integration_id"] == "jobber_001"

    headers = {
        "Authorization": f"Bearer {JOBBER_ACCESS_TOKEN}",
        "Accept": "application/json",
        "X-JOBBER-GRAPHQL-VERSION": "2025-01-20"
    }

    # Verify 50 clients
    query = "query { clients { nodes { id } } }"
    response = requests.post(f"{JOBBER_API_URL}/graphql", json={"query": query}, headers=headers)
    assert len(response.json().get("data", {}).get("clients", {}).get("nodes", [])) == 50

    # Verify 10 jobs
    query = "query { jobs { nodes { id } } }"
    response = requests.post(f"{JOBBER_API_URL}/graphql", json={"query": query}, headers=headers)
    assert len(response.json().get("data", {}).get("jobs", {}).get("nodes", [])) == 10

    # Verify 20 invoices
    query = "query { invoices { nodes { id } } }"
    response = requests.post(f"{JOBBER_API_URL}/graphql", json={"query": query}, headers=headers)
    assert len(response.json().get("data", {}).get("invoices", {}).get("nodes", [])) == 20

    # Verify 5 payments
    query = "query { payments { nodes { id } } }"
    response = requests.post(f"{JOBBER_API_URL}/graphql", json={"query": query}, headers=headers)
    assert len(response.json().get("data", {}).get("payments", {}).get("nodes", [])) == 5

    # Verify 20 expenses
    query = "query { expenses { nodes { id } } }"
    response = requests.post(f"{JOBBER_API_URL}/graphql", json={"query": query}, headers=headers)
    assert len(response.json().get("data", {}).get("expenses", {}).get("nodes", [])) == 20

    # Verify 10 timesheets
    query = "query { timesheets { nodes { id } } }"
    response = requests.post(f"{JOBBER_API_URL}/graphql", json={"query": query}, headers=headers)
    assert len(response.json().get("data", {}).get("timesheets", {}).get("nodes", [])) == 10

def test_setup_stripe_sandbox(db_session):
    """Test Stripe sandbox setup: 50 charges, 10 payouts."""
    stripe.api_key = STRIPE_SECRET_KEY
    result = setup_stripe_sandbox(db_session)
    assert result["integration_id"] == "stripe_001"

    # Verify 50 charges
    charges = stripe.Charge.list(limit=100)
    assert len(charges.data) == 50
    assert all(c.metadata.get("invoice_id") for c in charges.data)

    # Verify 10 payouts
    payouts = stripe.Payout.list(limit=100)
    assert len(payouts.data) == 10
    assert all(p.metadata.get("payout_id") for p in payouts.data)