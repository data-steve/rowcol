#!/usr/bin/env python3
"""
QBO Sandbox Data Creation

Creates rich test data for QBO integration testing and development.
Part of the QBO domain test infrastructure.

Creates:
- QBO: 100 transactions, 50 vendors, 10 jobs with realistic business patterns
- Supports multiple business scenarios for comprehensive testing

Usage:
    python domains/integrations/qbo/create_sandbox_data.py
    
    # From project root
    python -m domains.integrations.qbo.create_sandbox_data
"""

import requests
import stripe
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from infra.qbo.integration_models import Integration
from infra.database.session import SessionLocal
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Credentials from .env
QBO_CLIENT_ID = os.getenv("QBO_CLIENT_ID")
QBO_CLIENT_SECRET = os.getenv("QBO_CLIENT_SECRET")
QBO_ACCESS_TOKEN = os.getenv("QBO_ACCESS_TOKEN")
QBO_REFRESH_TOKEN = os.getenv("QBO_REFRESH_TOKEN")
QBO_REALM_ID = os.getenv("QBO_REALM_ID")
QBO_SANDBOX_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company"

JOBBER_CLIENT_ID = os.getenv("JOBBER_CLIENT_ID")
JOBBER_CLIENT_SECRET = os.getenv("JOBBER_CLIENT_SECRET")
JOBBER_ACCESS_TOKEN = os.getenv("JOBBER_ACCESS_TOKEN")
JOBBER_API_URL = "https://api.getjobber.com/api"

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

def setup_qbo_sandbox(db: Session) -> Dict[str, Any]:
    """Set up QBO sandbox with 100 transactions, 10 jobs, 50 vendors."""
    if not all([QBO_CLIENT_ID, QBO_CLIENT_SECRET, QBO_REALM_ID]):
        raise ValueError("Missing QBO credentials in .env")
    
    # Try to get access token from refresh token if not provided
    access_token = QBO_ACCESS_TOKEN
    if not access_token and QBO_REFRESH_TOKEN:
        try:
            from intuitlib.client import AuthClient
            auth_client = AuthClient(QBO_CLIENT_ID, QBO_CLIENT_SECRET, "http://localhost:8000/callback", "sandbox")
            auth_client.refresh_token = QBO_REFRESH_TOKEN
            auth_client.refresh()
            access_token = auth_client.access_token
            print(f"✅ Refreshed QBO access token: {access_token[:10]}...")
        except Exception as e:
            print(f"⚠️ Could not refresh QBO token: {e}")
            print("⚠️ Using refresh token directly for setup")
            access_token = QBO_REFRESH_TOKEN
    
    if not access_token:
        raise ValueError("No QBO access token or refresh token available")

    integration = Integration(
        integration_id="qbo_001",
        business_id="tenant_001",
        platform="qbo",
        access_token=access_token,
        refresh_token=QBO_REFRESH_TOKEN,
        expires_at=datetime.now() + timedelta(days=180),
        account_id="qbo_account_001",
        status="active"
    )
    db.add(integration)
    db.commit()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Seed 100 transactions (50 deposits, 50 expenses)
    for i in range(50):
        deposit = {
            "Deposit": {
                "TxnDate": (datetime.now() - timedelta(days=i % 30)).strftime("%Y-%m-%d"),
                "TotalAmt": 1000.00 + (i % 10),
                "Line": [{"Amount": 1000.00 + (i % 10), "DetailType": "DepositLineDetail"}]
            }
        }
        expense = {
            "Purchase": {
                "TxnDate": (datetime.now() - timedelta(days=i % 30)).strftime("%Y-%m-%d"),
                "TotalAmt": 200.00 + (i % 5),
                "Line": [{"Amount": 200.00 + (i % 5), "DetailType": "AccountBasedExpenseLineDetail"}]
            }
        }
        requests.post(f"{QBO_SANDBOX_URL}/{QBO_REALM_ID}/deposit", json=deposit, headers=headers)
        requests.post(f"{QBO_SANDBOX_URL}/{QBO_REALM_ID}/purchase", json=expense, headers=headers)

    # Seed 10 jobs (as Classes in QBO)
    for i in range(10):
        job = {
            "Class": {
                "Name": f"Job_{i+1}",
                "Active": True
            }
        }
        requests.post(f"{QBO_SANDBOX_URL}/{QBO_REALM_ID}/class", json=job, headers=headers)

    # Seed 50 vendors
    for i in range(50):
        vendor = {
            "Vendor": {
                "DisplayName": f"Vendor_{i+1}",
                "PrimaryEmailAddr": {"Address": f"vendor{i+1}@example.com"}
            }
        }
        requests.post(f"{QBO_SANDBOX_URL}/{QBO_REALM_ID}/vendor", json=vendor, headers=headers)

    return {"integration_id": integration.integration_id}

def setup_jobber_sandbox(db: Session) -> Dict[str, Any]:
    """Set up Jobber sandbox with 10 jobs, 20 invoices, 5 payments, 50 clients, 20 expenses, 10 timesheets."""
    if not all([JOBBER_CLIENT_ID, JOBBER_CLIENT_SECRET, JOBBER_ACCESS_TOKEN]):
        raise ValueError("Missing Jobber credentials in .env")

    integration = Integration(
        integration_id="jobber_001",
        business_id="tenant_001",
        platform="jobber",
        access_token=JOBBER_ACCESS_TOKEN,
        refresh_token=os.getenv("JOBBER_REFRESH_TOKEN", "mock_refresh"),
        expires_at=datetime.now() + timedelta(days=180),
        account_id="jobber_account_001",
        status="active"
    )
    db.add(integration)
    db.commit()

    headers = {
        "Authorization": f"Bearer {JOBBER_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-JOBBER-GRAPHQL-VERSION": "2025-01-20"
    }

    # Seed 50 clients
    for i in range(50):
        client = {
            "clientCreate": {
                "firstName": f"Client_{i+1}",
                "lastName": "Test",
                "companyName": f"Test Company {i+1}",
                "emails": [{"address": f"client{i+1}@example.com"}]
            }
        }
        requests.post(f"{JOBBER_API_URL}/graphql", json={"query": "mutation($input: ClientCreateInput!) { clientCreate(input: $input) { id } }", "variables": {"input": client["clientCreate"]}}, headers=headers)

    # Seed 10 jobs
    for i in range(10):
        job = {
            "jobCreate": {
                "title": f"Job_{i+1}",
                "status": "ACTIVE",
                "startDate": (datetime.now() - timedelta(days=i % 30)).strftime("%Y-%m-%d"),
                "clientId": f"client_{(i % 50)+1}"
            }
        }
        requests.post(f"{JOBBER_API_URL}/graphql", json={"query": "mutation($input: JobCreateInput!) { jobCreate(input: $input) { id } }", "variables": {"input": job["jobCreate"]}}, headers=headers)

    # Seed 20 invoices
    for i in range(20):
        invoice = {
            "invoiceCreate": {
                "number": f"INV-{i+1}",
                "totalAmount": 500.00 + (i % 10),
                "jobId": f"job_{(i % 10)+1}",
                "clientId": f"client_{(i % 50)+1}"
            }
        }
        requests.post(f"{JOBBER_API_URL}/graphql", json={"query": "mutation($input: InvoiceCreateInput!) { invoiceCreate(input: $input) { id } }", "variables": {"input": invoice["invoiceCreate"]}}, headers=headers)

    # Seed 5 payments
    for i in range(5):
        payment = {
            "paymentCreate": {
                "amount": 2000.00 + (i % 5) * 100,
                "invoiceIds": [f"INV-{j}" for j in range(i*4+1, i*4+5)],
                "clientId": f"client_{(i % 50)+1}",
                "paymentDate": (datetime.now() - timedelta(days=i % 30)).strftime("%Y-%m-%d")
            }
        }
        requests.post(f"{JOBBER_API_URL}/graphql", json={"query": "mutation($input: PaymentCreateInput!) { paymentCreate(input: $input) { id } }", "variables": {"input": payment["paymentCreate"]}}, headers=headers)

    # Seed 20 expenses
    for i in range(20):
        expense = {
            "expenseCreate": {
                "amount": 200.00 + (i % 5),
                "description": f"Expense for Job_{(i % 10)+1}",
                "jobId": f"job_{(i % 10)+1}",
                "date": (datetime.now() - timedelta(days=i % 30)).strftime("%Y-%m-%d")
            }
        }
        requests.post(f"{JOBBER_API_URL}/graphql", json={"query": "mutation($input: ExpenseCreateInput!) { expenseCreate(input: $input) { id } }", "variables": {"input": expense["expenseCreate"]}}, headers=headers)

    # Seed 10 timesheets
    for i in range(10):
        timesheet = {
            "timesheetCreate": {
                "hours": 8.0 + (i % 3),
                "jobId": f"job_{(i % 10)+1}",
                "date": (datetime.now() - timedelta(days=i % 30)).strftime("%Y-%m-%d")
            }
        }
        requests.post(f"{JOBBER_API_URL}/graphql", json={"query": "mutation($input: TimesheetCreateInput!) { timesheetCreate(input: $input) { id } }", "variables": {"input": timesheet["timesheetCreate"]}}, headers=headers)

    return {"integration_id": integration.integration_id}

def setup_stripe_sandbox(db: Session) -> Dict[str, Any]:
    """Set up Stripe sandbox with 50 charges, 10 payouts."""
    if not STRIPE_SECRET_KEY:
        raise ValueError("Missing Stripe secret key in .env")

    stripe.api_key = STRIPE_SECRET_KEY

    integration = Integration(
        integration_id="stripe_001",
        business_id="tenant_001",
        platform="stripe",
        access_token=STRIPE_SECRET_KEY,
        refresh_token=None,
        expires_at=None,
        account_id="stripe_account_001",
        status="active"
    )
    db.add(integration)
    db.commit()

    # Seed 50 charges
    for i in range(50):
        stripe.Charge.create(
            amount=1000 + (i % 10) * 100,
            currency="usd",
            source="tok_visa",
            description=f"Test charge {i+1}",
            metadata={"invoice_id": f"INV-{i+1}", "customer_id": f"cus_{i+1}"}
        )

    # Seed 10 payouts
    for i in range(10):
        stripe.Payout.create(
            amount=5000 + (i % 5) * 1000,
            currency="usd",
            description=f"Test payout {i+1}",
            metadata={"payout_id": f"POUT-{i+1}"}
        )

    return {"integration_id": integration.integration_id}

def main():
    """Orchestrate sandbox setup."""
    db = SessionLocal()
    try:
        qbo_result = setup_qbo_sandbox(db)
        jobber_result = setup_jobber_sandbox(db)
        stripe_result = setup_stripe_sandbox(db)
        print("Sandbox setup complete:", {
            "qbo": qbo_result,
            "jobber": jobber_result,
            "stripe": stripe_result
        })
    except Exception as e:
        print(f"Error setting up sandboxes: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()