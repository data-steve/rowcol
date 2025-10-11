"""
Test configuration for _clean MVP tests.

This provides:
1. In-memory test database for unit tests
2. Real production database for QBO integration tests
3. Test fixtures for models
4. FastAPI test client setup
"""

import pytest
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ==================== DATABASE CONFIGURATION ====================

# Real production database for QBO integration tests
SQLALCHEMY_DATABASE_URL = 'sqlite:///../../_clean/rowcol.db'

# In-memory test database for unit tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

def get_database_url():
    """Get PRODUCTION database URL. Use for QBO integration tests."""
    return SQLALCHEMY_DATABASE_URL

def get_database_engine():
    """Get PRODUCTION database engine. Use for QBO integration tests."""
    return create_engine(SQLALCHEMY_DATABASE_URL)

# Test database setup
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ==================== TEST DATABASE FIXTURES ====================

@pytest.fixture(scope="function")
def db():
    """
    In-memory test database for unit tests.
    
    This creates a fresh database for each test function and rolls back
    all changes after the test completes.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    
    # TODO: When we have SQLAlchemy models, uncomment this:
    # from infra.db.models import Base
    # Base.metadata.drop_all(bind=connection, checkfirst=True)
    # Base.metadata.create_all(bind=connection)
    
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def db_engine():
    """Production database engine for QBO integration tests."""
    return get_database_engine()


@pytest.fixture
def db_session(db_engine):
    """Production database session for QBO integration tests."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def prod_db():
    """
    Alias for production database session.
    Use this for QBO integration tests that need real tokens.
    """
    engine = get_database_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


# ==================== QBO INTEGRATION TEST FIXTURES ====================

@pytest.fixture
def qbo_realm_id(prod_db):
    """
    Get QBO realm_id from production database for integration tests.
    Skips test if no QBO tokens found.
    """
    result = prod_db.execute(text(
        "SELECT external_id FROM system_integration_tokens "
        "WHERE rail = 'qbo' AND environment = 'sandbox' AND status = 'active' "
        "ORDER BY updated_at DESC LIMIT 1"
    )).fetchone()
    
    if not result:
        pytest.skip("No QBO system tokens found. Run token setup first.")
    
    return result[0]


@pytest.fixture
def qbo_tokens(prod_db):
    """
    Get QBO tokens from production database for integration tests.
    Returns (realm_id, access_token, refresh_token).
    Skips test if no QBO tokens found.
    """
    result = prod_db.execute(text(
        "SELECT external_id, access_token, refresh_token FROM system_integration_tokens "
        "WHERE rail = 'qbo' AND environment = 'sandbox' AND status = 'active' "
        "ORDER BY updated_at DESC LIMIT 1"
    )).fetchone()
    
    if not result:
        pytest.skip("No QBO system tokens found. Run token setup first.")
    
    return result[0], result[1], result[2]


# ==================== FASTAPI TEST CLIENT FIXTURES ====================

# TODO: Uncomment when we have FastAPI app
# @pytest.fixture
# def client(db):
#     """FastAPI test client with test database."""
#     from fastapi.testclient import TestClient
#     from main import app
#     from infra.db.session import get_db
#     
#     def override_get_db():
#         try:
#             yield db
#         finally:
#             pass
#     
#     app.dependency_overrides[get_db] = override_get_db
#     with TestClient(app) as test_client:
#         yield test_client
#     app.dependency_overrides.clear()


# ==================== MODEL TEST FIXTURES ====================

# TODO: Add test fixtures for models once they are created
# Example structure:
#
# @pytest.fixture
# def test_business(db):
#     business = Business(
#         business_id="biz_123",
#         name="Test Business",
#         realm_id="test_realm_123"
#     )
#     db.add(business)
#     db.commit()
#     db.refresh(business)
#     return business
#
# @pytest.fixture
# def test_bill(db, test_business):
#     bill = Bill(
#         business_id=test_business.business_id,
#         qbo_bill_id="bill_001",
#         vendor_name="Test Vendor",
#         amount=500.0,
#         due_date=datetime.utcnow() + timedelta(days=30)
#     )
#     db.add(bill)
#     db.commit()
#     db.refresh(bill)
#     return bill


# ==================== PYTEST CONFIGURATION ====================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "qbo_real_api: mark test as requiring real QBO API access"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
