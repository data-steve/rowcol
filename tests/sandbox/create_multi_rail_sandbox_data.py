#!/usr/bin/env python3
"""
Multi-Rail Sandbox Data Creation

Creates rich test data for multi-rail integration testing and development.
Part of the Financial Control Plane test infrastructure.

Creates:
- QBO: 100 transactions, 50 vendors, 10 jobs with realistic business patterns
- Stripe: 50 charges, 10 payouts for A/R insights
- Plaid: Mock bank account data for cash verification
- Ramp: Mock A/P transactions for payment execution

Usage:
    python scripts/create_multi_rail_sandbox_data.py
    
    # From project root
    python -m scripts.create_multi_rail_sandbox_data
"""

import requests
import stripe
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
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

    # Update business with QBO integration fields
    from domains.core.models.business import Business
    business = db.query(Business).filter(Business.business_id == "tenant_001").first()
    if business:
        business.qbo_realm_id = "qbo_account_001"
        business.qbo_access_token = access_token
        business.qbo_refresh_token = QBO_REFRESH_TOKEN
        business.qbo_connected_at = datetime.now()
        business.qbo_status = "connected"
        business.qbo_environment = "sandbox"
        business.qbo_token_expires_at = datetime.now() + timedelta(days=180)
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

    return {"qbo_setup": "complete"}

def setup_stripe_sandbox(db: Session) -> Dict[str, Any]:
    """Set up Stripe sandbox with 50 charges, 10 payouts for A/R insights."""
    if not STRIPE_SECRET_KEY:
        raise ValueError("Missing Stripe secret key in .env")

    stripe.api_key = STRIPE_SECRET_KEY

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

    return {"stripe_setup": "complete"}

def setup_plaid_mock_data(db: Session) -> Dict[str, Any]:
    """Set up mock Plaid data for cash verification."""
    # Mock bank account data for testing
    from domains.bank.models.bank_transaction import BankTransaction
    
    # Create mock bank transactions
    for i in range(100):
        transaction = BankTransaction(
            business_id="tenant_001",
            account_id="plaid_account_001",
            transaction_id=f"plaid_txn_{i+1}",
            amount=1000.00 + (i % 10) * 100,
            date=(datetime.now() - timedelta(days=i % 30)).date(),
            description=f"Mock Plaid transaction {i+1}",
            category="Office Supplies",
            subcategory="Software",
            merchant_name=f"Mock Merchant {i+1}",
            account_owner="Test Business",
            account_type="checking"
        )
        db.add(transaction)
    
    db.commit()
    return {"plaid_mock_setup": "complete"}

def setup_ramp_mock_data(db: Session) -> Dict[str, Any]:
    """Set up mock Ramp data for A/P execution."""
    from domains.ap.models.bill import Bill
    
    # Create mock Ramp bills
    for i in range(50):
        bill = Bill(
            business_id="tenant_001",
            vendor_id=f"ramp_vendor_{i+1}",
            bill_number=f"RAMP-{i+1}",
            amount=200.00 + (i % 5) * 50,
            due_date=(datetime.now() + timedelta(days=i % 30)).date(),
            description=f"Mock Ramp bill {i+1}",
            status="pending",
            external_id=f"ramp_bill_{i+1}",
            external_source="ramp"
        )
        db.add(bill)
    
    db.commit()
    return {"ramp_mock_setup": "complete"}

def main():
    """Orchestrate multi-rail sandbox setup."""
    db = SessionLocal()
    try:
        qbo_result = setup_qbo_sandbox(db)
        stripe_result = setup_stripe_sandbox(db)
        plaid_result = setup_plaid_mock_data(db)
        ramp_result = setup_ramp_mock_data(db)
        
        print("Multi-rail sandbox setup complete:", {
            "qbo": qbo_result,
            "stripe": stripe_result,
            "plaid": plaid_result,
            "ramp": ramp_result
        })
    except Exception as e:
        print(f"Error setting up multi-rail sandbox: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
