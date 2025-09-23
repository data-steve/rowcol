import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from domains.core.models.base import Base
from domains.core.models import Business, Balance, Integration
from domains.ap.models import Bill, Vendor
from domains.ap.models.payment import Payment as APPayment
from domains.ar.models import Invoice, Customer
from domains.ar.models.payment import Payment as ARPayment
from runway.tray.models.tray_item import TrayItem

from main import app
from db.session import SessionLocal, get_db

import os
from dotenv import load_dotenv

load_dotenv()

# QBO Sandbox Credentials for Integration Tests
QBO_CLIENT_ID = os.getenv('QBO_CLIENT_ID', 'test_client_id')
QBO_CLIENT_SECRET = os.getenv('QBO_CLIENT_SECRET', 'test_client_secret')
QBO_REDIRECT_URI = os.getenv('QBO_REDIRECT_URI', 'http://localhost:8000/callback')
QBO_SANDBOX_BASE_URL = 'https://sandbox-quickbooks.api.intuit.com'

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    
    # Clean up and create tables
    Base.metadata.drop_all(bind=connection)
    Base.metadata.create_all(bind=connection)
    
    db_session = SessionLocal(bind=connection)

    yield db_session

    db_session.close()
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
def test_business(db):
    business = Business(
        business_id="biz_123",
        name="Test Agency",
        qbo_id="test123",
        industry="agency"
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business

@pytest.fixture
def test_balance(db, test_business):
    balance = Balance(
        business_id=test_business.business_id,
        qbo_account_id="123",
        current_balance=6000.0,
        available_balance=5500.0,
        snapshot_date=datetime.utcnow(),
        account_type="checking"
    )
    db.add(balance)
    db.commit()
    db.refresh(balance)
    return balance

@pytest.fixture
def test_bill(db, test_business):
    vendor = Vendor(
        business_id=test_business.business_id,
        qbo_vendor_id="vendor_001",
        name="Rent LLC"
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    
    bill = Bill(
        business_id=test_business.business_id,
        qbo_bill_id="bill_001",
        vendor_id=vendor.vendor_id,
        amount_cents=500000,  # $5000.00
        due_date=datetime.utcnow() + timedelta(days=14),
        status="pending"
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill

@pytest.fixture
def test_invoice(db, test_business):
    customer = Customer(
        business_id=test_business.business_id,
        qbo_customer_id="customer_001",
        name="Pine Valley HOA",
        email="hoa@example.com"
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    invoice = Invoice(
        business_id=test_business.business_id,
        qbo_invoice_id="inv_009",
        customer_id=customer.customer_id,
        total=1983.34,  # $1983.34
        issue_date=datetime.utcnow() - timedelta(days=50),
        due_date=datetime.utcnow() - timedelta(days=42),
        status="open"
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

@pytest.fixture
def test_tray_item(db, test_business):
    tray_item = TrayItem(
        business_id=test_business.business_id,
        type="bill",
        qbo_id="bill_001",
        status="pending",
        priority="high",
        due_date=datetime.utcnow()
    )
    db.add(tray_item)
    db.commit()
    db.refresh(tray_item)
    return tray_item

@pytest.fixture
def test_integration(db, test_business):
    integration = Integration(
        business_id=test_business.business_id,
        integration_id="int_001",
        platform="qbo",
        access_token="mock_qbo_token",
        refresh_token="mock_qbo_refresh",
        status="active"
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration

@pytest.fixture
def test_ap_payment(db, test_business, test_bill):
    payment = APPayment(
        business_id=test_business.business_id,
        qbo_id="pay_001",
        vendor_id="vendor_001",
        bill_id="bill_001",
        amount=5000.0,
        payment_date=datetime.utcnow(),
        status="pending"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@pytest.fixture
def test_ar_payment(db, test_business, test_invoice):
    payment = ARPayment(
        business_id=test_business.business_id,
        qbo_id="ar_pay_001",
        customer_id="customer_001",
        invoice_id="inv_009",
        amount=1983.34,
        payment_date=datetime.utcnow(),
        status="pending"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

# Note: test_firm and test_client concepts removed in Oodaloo v2
# All tests should use test_business (ICP) directly

@pytest.fixture
def test_customer(db, test_business):
    """Create a test customer for AR tests."""
    customer = Customer(
        business_id=test_business.business_id,
        qbo_customer_id="customer_test_001",
        name="Test Customer",
        email="customer@test.com"
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@pytest.fixture
def test_vendor(db, test_business):
    """Create a test vendor for AP tests."""
    vendor = Vendor(
        business_id=test_business.business_id,
        qbo_vendor_id="vendor_test_001", 
        name="Test Vendor"
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

@pytest.fixture
def mock_qbo():
    """Mock QBO client for integration tests."""
    mock_client = MagicMock()
    mock_client.get_bills.return_value = [
        {"Id": "bill_001", "VendorRef": {"name": "Test Vendor"}, "TotalAmt": 100.0, "DueDate": "2025-10-01"}
    ]
    mock_client.get_invoices.return_value = [
        {"Id": "inv_001", "CustomerRef": {"name": "Test Customer"}, "TotalAmt": 200.0, "DueDate": "2025-10-01"}
    ]
    mock_client.get_customers.return_value = [
        {"Id": "cust_001", "Name": "Test Customer", "Active": True}
    ]
    mock_client.get_vendors.return_value = [
        {"Id": "vend_001", "Name": "Test Vendor", "Active": True}
    ]
    mock_client.create_payment.return_value = {"Id": "mock_payment_001"}
    mock_client.create_bill.return_value = {"Id": "mock_bill_001"}
    mock_client.create_invoice.return_value = {"Id": "mock_invoice_001"}
    
    return mock_client

@pytest.fixture
def mock_qb(mock_qbo):
    """Alias for mock_qbo for legacy compatibility."""
    return mock_qbo

@pytest.fixture
def mock_payment():
    """Mock payment service for payment tests."""
    mock = MagicMock()
    mock.schedule_payment.return_value = {"status": "scheduled", "payment_id": "mock_001"}
    return mock

# Note: Task model is parked - no test_task fixture needed

# ==================== QBO TEST FIXTURES ====================

@pytest.fixture(scope="function")
def qbo_connected_business(db):
    business = Business(
        business_id="test_qbo_business_id",
        name="Test QBO Business",
        industry="Software",
        qbo_id=os.getenv('QBO_REALM_ID', 'test_realm_id')
    )
    db.add(business)
    db.commit()
    db.refresh(business)

    # Add QBO integration with real sandbox credentials if available
    integration = Integration(
        business_id=business.business_id,
        platform="qbo",
        access_token=os.getenv('QBO_ACCESS_TOKEN', 'test_access_token'),
        refresh_token=os.getenv('QBO_REFRESH_TOKEN', 'test_refresh_token'),
        realm_id=os.getenv('QBO_REALM_ID', 'test_realm_id')
    )
    db.add(integration)
    db.commit()
    
    # Add test data using centralized helper
    _add_test_data(db, business)
    
    return business

@pytest.fixture(scope="function") 
def qbo_auth_setup():
    """Setup QBO auth service for tests without creating a business."""
    from domains.integrations.qbo.qbo_auth import qbo_auth
    
    # Clear any existing tokens
    qbo_auth.tokens.clear()
    
    yield qbo_auth
    
    # Cleanup
    qbo_auth.tokens.clear()


def _add_test_data(db, business: Business):
    """Add test data for integration tests."""
    from domains.ap.models.vendor import Vendor
    from domains.ar.models.customer import Customer
    from domains.ap.models.bill import Bill
    from domains.ar.models.invoice import Invoice
    from domains.core.models.balance import Balance
    from decimal import Decimal
    
    # Add test vendors
    vendor1 = Vendor(
        business_id=business.business_id,
        qbo_vendor_id="1",
        name="Office Supplies Co",
        is_active=True
    )
    vendor2 = Vendor(
        business_id=business.business_id,
        qbo_vendor_id="2", 
        name="Software Solutions Inc",
        is_active=True
    )
    db.add_all([vendor1, vendor2])
    db.flush()
    
    # Add test customers
    customer1 = Customer(
        business_id=business.business_id,
        qbo_customer_id="1",
        name="Acme Corp",
        is_active=True
    )
    customer2 = Customer(
        business_id=business.business_id,
        qbo_customer_id="2",
        name="Tech Startup LLC", 
        is_active=True
    )
    db.add_all([customer1, customer2])
    db.flush()
    
    # Add test bills
    bill1 = Bill(
        business_id=business.business_id,
        vendor_id=vendor1.vendor_id,
        qbo_bill_id="1",
        bill_number="BILL-001",
        amount_cents=25000,  # $250
        due_date=datetime.now() + timedelta(days=15),
        status="pending"
    )
    bill2 = Bill(
        business_id=business.business_id,
        vendor_id=vendor2.vendor_id,
        qbo_bill_id="2",
        bill_number="BILL-002", 
        amount_cents=150000,  # $1500
        due_date=datetime.now() + timedelta(days=30),
        status="pending"
    )
    db.add_all([bill1, bill2])
    
    # Add test invoices
    invoice1 = Invoice(
        business_id=business.business_id,
        customer_id=customer1.customer_id,
        qbo_invoice_id="1",
        issue_date=datetime.now() - timedelta(days=30),
        due_date=datetime.now() - timedelta(days=15),  # Overdue
        total=5000.00,
        status="sent"
    )
    invoice2 = Invoice(
        business_id=business.business_id,
        customer_id=customer2.customer_id,
        qbo_invoice_id="2",
        issue_date=datetime.now() - timedelta(days=20), 
        due_date=datetime.now() - timedelta(days=5),   # Overdue
        total=2500.00,
        status="sent"
    )
    db.add_all([invoice1, invoice2])
    
    # Add test balances
    balance1 = Balance(
        business_id=business.business_id,
        qbo_account_id="1",
        current_balance=15000.00,
        available_balance=15000.00,
        account_type="checking",
        snapshot_date=datetime.now()
    )
    balance2 = Balance(
        business_id=business.business_id,
        qbo_account_id="2",
        current_balance=5000.00,
        available_balance=5000.00,
        account_type="savings",
        snapshot_date=datetime.now()
    )
    db.add_all([balance1, balance2])
    
    db.commit()
