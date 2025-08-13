import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from datetime import datetime, timedelta
import uuid

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