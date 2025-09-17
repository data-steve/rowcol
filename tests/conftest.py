import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from domains.core.models.base import Base
from domains.core.models import Business, Balance, Notification, Integration, Transaction, User
from domains.ap.models import Bill, Vendor
from domains.ap.models.payment import Payment as APPayment
from domains.ar.models import Invoice, Customer
from domains.ar.models.payment import Payment as ARPayment
from runway.tray.models.tray_item import TrayItem

from main import app
from db.session import SessionLocal, engine, get_db

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
        qbo_id="vendor_001",
        name="Rent LLC"
    )
    db.add(vendor)
    bill = Bill(
        business_id=test_business.business_id,
        qbo_id="bill_001",
        vendor_id="vendor_001",
        amount=5000.0,
        due_date=datetime.utcnow() + timedelta(days=14),
        status="open"
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill

@pytest.fixture
def test_invoice(db, test_business):
    customer = Customer(
        business_id=test_business.business_id,
        qbo_id="customer_001",
        name="Pine Valley HOA",
        email="hoa@example.com"
    )
    db.add(customer)
    invoice = Invoice(
        business_id=test_business.business_id,
        qbo_id="inv_009",
        customer_id="customer_001",
        total=1983.34,
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
