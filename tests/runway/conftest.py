import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domains.core.models.base import Base
from domains.core.models.business import Business

@pytest.fixture(scope="session")
def db_engine():
    """Fixture for a database engine."""
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Fixture for a database session that includes table creation 
    and a dummy business for tenant-aware services.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    
    # Create tables
    Base.metadata.create_all(bind=connection)
    
    Session = sessionmaker(bind=connection)
    session = Session()
    
    # Create a dummy business for services to initialize
    dummy_business = Business(business_id="test_business", name="Test Business")
    session.add(dummy_business)
    session.commit()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
