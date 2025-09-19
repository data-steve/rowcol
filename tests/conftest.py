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
