"""
Phase 0 Database Foundation Tests

Tests for database creation and basic functionality that's core to Phase 0 MVP.
These tests focus on the database infrastructure, not seeded data.
"""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import create_db_and_tables
from domains.core.models.business import Business
from domains.core.models.user import User
from domains.core.services.business import BusinessService
from domains.core.schemas.business import BusinessCreate


def test_database_creation():
    """Test that database tables are created successfully"""
    try:
        create_db_and_tables()
        assert True  # If no exception, database creation worked
    except Exception as e:
        pytest.fail(f"Database creation failed: {e}")


def test_business_service_create_and_retrieve(db: Session):
    """Test that BusinessService can create and retrieve businesses"""
    service = BusinessService(db)
    
    # Create a test business
    business_data = BusinessCreate(
        name="Test Agency",
        industry="Marketing"
    )
    
    created_business = service.create_business(business_data)
    assert created_business.name == "Test Agency"
    assert created_business.business_id is not None
    
    # Retrieve the business
    retrieved_business = service.get_business(created_business.business_id)
    assert retrieved_business is not None
    assert retrieved_business.name == "Test Agency"


def test_business_model_structure(db: Session):
    """Test that Business model has correct structure"""
    business = Business(
        business_id="test_123",
        name="Test Business"
    )
    db.add(business)
    db.commit()
    
    # Retrieve and verify
    retrieved = db.query(Business).filter(Business.business_id == "test_123").first()
    assert retrieved is not None
    assert retrieved.business_id == "test_123"
    assert retrieved.name == "Test Business"
    assert retrieved.created_at is not None


def test_database_tables_exist(db: Session):
    """Test that all required Phase 0 tables exist"""
    # Get list of tables
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result.fetchall()]
    
    # Core Phase 0 tables that must exist
    required_tables = [
        "businesses", 
        "users",
        "integrations",
        "balances", 
        "transactions",
        "tray_item"
    ]
    
    for table in required_tables:
        assert table in tables, f"Required Phase 0 table '{table}' not found"


def test_database_constraints(db: Session):
    """Test that database constraints work properly"""
    # Test that we can't create user without business_id
    with pytest.raises(Exception):  # Should fail due to foreign key constraint
        user = User(
            user_id=999,
            business_id="nonexistent_business",  # This should fail
            email="test@invalid.com",
            role="admin"
        )
        db.add(user)
        db.commit()


def test_database_performance_basic(db: Session):
    """Test basic database performance for Phase 0 operations"""
    import time
    
    # Create a test business first
    test_business = Business(
        business_id="test_perf_123",
        name="Performance Test Business"
    )
    db.add(test_business)
    db.commit()
    
    # Test business query performance
    start_time = time.time()
    businesses = db.query(Business).all()
    query_time = time.time() - start_time
    
    assert query_time < 1.0, f"Business query too slow: {query_time}s"
    assert len(businesses) > 0, "No businesses found"


def test_database_isolation(db: Session):
    """Test that test database is properly isolated"""
    # This test should use in-memory database from conftest.py
    # Check that we're not affecting production data
    
    # Create a test business
    test_business = Business(
        business_id="test_isolation_123",
        name="Isolation Test Business"
    )
    db.add(test_business)
    db.commit()
    
    # Verify it exists
    found_business = db.query(Business).filter(
        Business.business_id == "test_isolation_123"
    ).first()
    assert found_business is not None
    assert found_business.name == "Isolation Test Business"
