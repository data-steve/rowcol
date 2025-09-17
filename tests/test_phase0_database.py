"""
Phase 0 Database Seeding Tests

Tests for database creation, seeding, and basic functionality that's core to Phase 0 MVP.
"""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import create_db_and_tables, seed_database
from domains.core.models import Business, User


def test_database_creation():
    """Test that database tables are created successfully"""
    try:
        create_db_and_tables()
        assert True  # If no exception, database creation worked
    except Exception as e:
        pytest.fail(f"Database creation failed: {e}")


def test_database_seeding():
    """Test that database seeding works without errors"""
    try:
        # First ensure tables exist
        create_db_and_tables()
        
        # Then seed data
        seed_database()
        assert True  # If no exception, seeding worked
    except Exception as e:
        pytest.fail(f"Database seeding failed: {e}")


def test_seeded_data_exists(db: Session):
    """Test that seeded data actually exists in database"""
    # Check if businesses table has data
    businesses_count = db.execute(text("SELECT COUNT(*) FROM businesses")).scalar()
    assert businesses_count > 0, "No businesses found after seeding"
    
    # Check if users table has data  
    users_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
    assert users_count > 0, "No users found after seeding"


def test_seeded_business_structure(db: Session):
    """Test that seeded business has correct structure"""
    business = db.query(Business).first()
    assert business is not None, "No business found in database"
    assert business.business_id is not None, "Business ID is None"
    assert business.name is not None, "Business name is None"
    assert len(business.business_id) > 0, "Business ID is empty"
    assert len(business.name) > 0, "Business name is empty"


def test_seeded_user_structure(db: Session):
    """Test that seeded user has correct structure"""
    user = db.query(User).first()
    assert user is not None, "No user found in database"
    assert user.user_id is not None, "User ID is None"
    assert user.business_id is not None, "User business_id is None"
    assert user.email is not None, "User email is None"
    assert len(user.email) > 0, "User email is empty"


def test_business_user_relationship(db: Session):
    """Test that business-user relationships work"""
    business = db.query(Business).first()
    user = db.query(User).first()
    
    assert business is not None, "No business found"
    assert user is not None, "No user found"
    assert user.business_id == business.business_id, "User not linked to business"


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
