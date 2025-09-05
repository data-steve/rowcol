import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from datetime import datetime, timedelta
import uuid
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from domains.core.models.base import Base
from domains.core.models import *
from domains.ap.models import *
from domains.ar.models import *
from domains.bank.models import *
from domains.policy.models import *
from main import app
from database import get_db
from tests.fixtures.realistic_variance_scenarios import generate_realistic_variance_scenario

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    Base.metadata.drop_all(bind=connection)
    Base.metadata.create_all(bind=connection)
    session = TestingSessionLocal(bind=connection)

    def override_get_db():
        try:
            yield session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db

    try:
        yield session
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_firm(db):
    firm = Firm(
        firm_id=str(uuid.uuid4()),
        name="Test Firm",
        pricing_tier="basic",
        doc_volume=0,
        settings={}
    )
    db.add(firm)
    db.commit()
    return firm

@pytest.fixture
def test_client(db, test_firm):
    client = Client(
        firm_id=test_firm.firm_id,
        name="Test Client",
        industry="retail"
    )
    db.add(client)
    db.commit()
    return client

@pytest.fixture
def test_customer(db, test_firm, test_client):
    customer = Customer(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        qbo_id="mock_customer_001",
        name="Test Customer",
        email="customer@example.com",
        terms="Net 30",
        fingerprint_hash="mock_hash_456"
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@pytest.fixture
def test_invoice(db, test_firm, test_client, test_customer):
    invoice = Invoice(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        customer_id=test_customer.customer_id,
        qbo_id="mock_invoice_001",
        job_id="JOB_A001",
        issue_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=30),
        total=500.0,
        lines=[{"item": "Service", "amount": 500.0}],
        status="sent",
        attachment_refs=[]
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

@pytest.fixture
def test_bank_transaction(db, test_firm, test_client):
    transaction = BankTransaction(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        external_id="tx_001",
        amount=500.0,
        date=datetime.utcnow(),
        description="Test Transaction",
        account_id="acc_001",
        source="plaid",
        processor=ProcessorType.ACH,
        status="pending",
        confidence=0.5
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@pytest.fixture
def test_jobber_integration(db, test_firm):
    integration = Integration(
        firm_id=test_firm.firm_id,
        integration_id=str(uuid.uuid4()),
        platform="jobber",
        access_token="mock_jobber_token",
        refresh_token="mock_jobber_refresh",
        status="active"
    )
    db.add(integration)
    db.commit()
    return integration

@pytest.fixture
def test_plaid_integration(db, test_firm):
    integration = Integration(
        firm_id=test_firm.firm_id,
        integration_id=str(uuid.uuid4()),
        platform="plaid",
        access_token="mock_plaid_token",
        refresh_token="mock_plaid_refresh",
        status="active"
    )
    db.add(integration)
    db.commit()
    return integration

@pytest.fixture
def test_sync_cursor(db, test_firm):
    cursor = SyncCursor(
        id=str(uuid.uuid4()),
        firm_id=test_firm.firm_id,
        source="jobber",
        cursor="mock_cursor"
    )
    db.add(cursor)
    db.commit()
    return cursor

@pytest.fixture
def test_realistic_data(db, test_firm, test_client):
    data = generate_realistic_variance_scenario()
    for invoice in data["jobber_invoices"]:
        db_invoice = Invoice(
            firm_id=test_firm.firm_id,
            client_id=test_client.client_id,
            customer_id=f"CUST_{invoice['id']}",
            qbo_id=invoice["id"],
            job_id=invoice["job_id"],
            issue_date=datetime.strptime("2025-01-01", "%Y-%m-%d"),
            due_date=datetime.strptime("2025-01-31", "%Y-%m-%d"),
            total=invoice["amount"],
            status=invoice["status"],
            lines=[],
            confidence=1.0
        )
        db.add(db_invoice)

    for tx in data["plaid_transactions"]:
        db_tx = BankTransaction(
            firm_id=test_firm.firm_id,
            client_id=test_client.client_id,
            external_id=tx["transaction_id"],
            amount=tx["amount"],
            date=datetime.strptime(tx["date"], "%Y-%m-%d"),
            description=tx["name"],
            account_id=tx["account_id"],
            source="plaid",
            processor=ProcessorType[tx["payment_channel"].upper()],
            status="pending",
            confidence=0.5 if "personal" in tx["name"].lower() else 1.0
        )
        db.add(db_tx)

    db.commit()
    return data
