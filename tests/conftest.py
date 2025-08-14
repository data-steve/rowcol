import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from datetime import datetime, timedelta
import uuid
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Ensure project root is on sys.path so 'models' is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.base import Base
import models  # noqa: F401 - register mappers
from main import app
from database import get_db
from models.service import Service
from models.engagement import Engagement
from models.task import Task
from models.firm import Firm
from models.client import Client
from models.staff import Staff
from models.user import User
from models.bill import Bill
from models.vendor import Vendor
from models.customer import Customer
from models.invoice import Invoice

# QBO Mock Fixture
@pytest.fixture(scope="session")
def mock_qbo():
    """Centralized QBO mock fixture for consistent testing."""
    with patch('quickbooks.QuickBooks') as mock_qbo_class:
        # Create mock QBO client instance
        mock_qbo_instance = Mock()
        mock_qbo_class.return_value = mock_qbo_instance
        
        # Configure mock responses for common operations
        mock_qbo_instance.sandbox = True
        
        # Mock successful API responses
        mock_qbo_instance.company_info = Mock()
        mock_qbo_instance.company_info.CompanyName = "Test Company"
        
        # Mock invoice creation
        mock_invoice = Mock()
        mock_invoice.Id = "qbo_inv_123"
        mock_invoice.save.return_value = mock_invoice
        mock_qbo_instance.objects.Invoice.return_value = mock_invoice
        
        # Mock credit memo creation
        mock_credit_memo = Mock()
        mock_credit_memo.Id = "qbo_cm_456"
        mock_credit_memo.save.return_value = mock_credit_memo
        mock_qbo_instance.objects.CreditMemo.return_value = mock_credit_memo
        
        # Mock payment creation
        mock_payment = Mock()
        mock_payment.Id = "qbo_pay_789"
        mock_payment.save.return_value = mock_payment
        mock_qbo_instance.objects.Payment.return_value = mock_payment
        
        # Mock bill creation
        mock_bill = Mock()
        mock_bill.Id = "qbo_bill_101"
        mock_bill.save.return_value = mock_bill
        mock_qbo_instance.objects.Bill.return_value = mock_bill
        
        # Mock vendor creation
        mock_vendor = Mock()
        mock_vendor.Id = "qbo_vendor_202"
        mock_vendor.save.return_value = mock_vendor
        mock_qbo_instance.objects.Vendor.return_value = mock_vendor
        
        yield mock_qbo_instance

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    # Ensure fresh schema each test
    Base.metadata.drop_all(bind=connection)
    Base.metadata.create_all(bind=connection)
    session = TestingSessionLocal(bind=connection)

    # Override FastAPI dependency to use the in-memory session
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
    """Test client fixture with database dependency override."""
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
        settings={},
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
def test_service(db, test_firm):
    service = Service(
        firm_id=test_firm.firm_id,
        name="Test Service",
        description="Test service description",
        price=1000.0,
        complexity_score=1.0,
        task_sequence=[{"step_type": "intake", "micro_tasks": ["collect_qbo_access"]}],
        tier="basic",
        automation_score=0.0,
        client_instructions="Test instructions"
    )
    db.add(service)
    db.commit()
    return service

@pytest.fixture
def test_engagement(db, test_firm, test_client, test_service):
    engagement = Engagement(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        service_type="bookkeeping",
        due_date=datetime.utcnow() + timedelta(days=30),
        user_input={"qbo_account": "12345"},
    )
    db.add(engagement)
    db.commit()
    return engagement

@pytest.fixture
def test_staff(db, test_firm):
    user = User(
        firm_id=test_firm.firm_id,
        role="staff",
        email="test@example.com",
        training_level="junior"
    )
    db.add(user)
    db.commit()
    
    staff = Staff(
        firm_id=test_firm.firm_id,
        user_id=user.user_id,
        role="bookkeeper",
        training_level="junior"
    )
    db.add(staff)
    db.commit()
    return staff

@pytest.fixture
def test_task(db, test_firm, test_client, test_service, test_engagement):
    task = Task(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        engagement_id=test_engagement.engagement_id,
        service_id=test_service.service_id,
        type="intake",
        status="pending",
        priority="medium",
        micro_tasks=["collect_qbo_access"],
        estimated_hours=1.0
    )
    db.add(task)
    db.commit()
    return task

@pytest.fixture
def test_bill(db, test_firm, test_client):
    from models.bill import Bill as BillModel
    bill = Bill(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        vendor_id=None,
        qbo_bill_id="mock_bill_001",
        amount=150.0,
        due_date=datetime.utcnow() + timedelta(days=30),
        status="pending",
        extracted_fields={"vendor_name": "Starbucks", "amount": "150.00", "date": "2025-01-15"},
        gl_account="6000-Expenses",
        confidence=0.9
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill

@pytest.fixture
def test_vendor(db, test_firm, test_client):
    from models.vendor import Vendor as VendorModel
    vendor = Vendor(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        canonical_id=None,
        qbo_id="mock_vendor_001",
        w9_status="pending",
        default_gl_account="6000-Expenses",
        terms="Net 30",
        fingerprint_hash="mock_hash_123"
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

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