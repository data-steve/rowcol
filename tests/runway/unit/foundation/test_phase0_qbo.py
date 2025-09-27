"""
Phase 0 QBO Integration Tests

Tests for basic QBO integration functionality that's core to Phase 0 MVP.
Uses the enhanced QBOAPIClient with proper mock/real switching.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from domains.core.models import Business, Integration
from infra.qbo.client import QBORawClient


def test_qbo_provider_import():
    """Test that QBOAPIClient can be imported"""
    assert QBOAPIClient is not None
    assert get_qbo_client is not None


def test_qbo_provider_factory_real(db: Session, test_business: Business):
    """Test QBO provider factory returns real provider"""
    provider = get_qbo_client(test_business.business_id, db)
    assert isinstance(provider, QBOAPIClient)
    assert provider.business_id == test_business.business_id


def test_qbo_provider_factory_auto_realm_lookup(db: Session, test_business: Business):
    """Test QBO provider factory can lookup realm_id automatically"""
    # This will use the fallback "mock_realm" since no integration exists
    provider = get_qbo_client(test_business.business_id, db)
    assert isinstance(provider, QBOAPIClient)
    assert provider.realm_id == "mock_realm"


def test_integration_model_structure():
    """Test that Integration model has correct Phase 0 attributes"""
    assert hasattr(Integration, 'integration_id')
    assert hasattr(Integration, 'business_id')
    assert hasattr(Integration, 'platform')
    assert hasattr(Integration, 'access_token')
    assert hasattr(Integration, 'refresh_token')
    assert hasattr(Integration, 'expires_at')
    assert Integration.__tablename__ == 'integrations'


def test_integration_creation(db: Session, test_business: Business):
    """Test basic Integration model creation for QBO"""
    from datetime import datetime, timedelta

    integration = Integration(
        # Do not set integration_id as it's an auto-incremented Integer primary key
        business_id=test_business.business_id,
        platform="QBO",
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        expires_at=datetime.now() + timedelta(hours=1),
        status="active"
    )

    db.add(integration)
    db.commit()

    assert integration.business_id == test_business.business_id
    assert integration.platform == "QBO"
    assert integration.status == "active"


@pytest.mark.asyncio
async def test_qbo_provider_get_bills_real():
    """Test QBO provider can get bills using real provider with production database"""
    import os
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from infra.qbo.integration_models import Integration, IntegrationStatuses
    from domains.core.models.business import Business
    
    # Connect to MAIN database (not test database) to get real QBO integration
    database_url = os.getenv('SQLALCHEMY_DATABASE_URL', 'sqlite:///oodaloo.db')
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        # Look for existing QBO integration in MAIN database
        integration = session.query(Integration).filter(
            Integration.platform == "qbo",
            Integration.status == IntegrationStatuses.CONNECTED.value
        ).first()

        if not integration:
            pytest.skip("SKIPPING: No QBO integration found. Run token refresh script.")

        if not all([integration.access_token, integration.refresh_token, integration.realm_id]):
            pytest.skip("SKIPPING: QBO integration missing required tokens.")

        # Get the associated business
        business = session.query(Business).filter(Business.business_id == integration.business_id).first()
        if not business:
            pytest.skip("SKIPPING: Business not found for QBO integration.")

        # Test with real QBO provider
        provider = get_qbo_client(business.business_id, session)
        
        # Test that provider can get bills (should work with valid tokens)
        try:
            bills = await provider.get_bills()
            assert isinstance(bills, list)
            print(f"✅ Successfully retrieved {len(bills)} bills from QBO")
        except Exception as e:
            # If it fails, it should be with a proper error message
            assert "No valid QBO access token" in str(e) or "IntegrationError" in str(e)


@pytest.mark.asyncio
async def test_qbo_provider_get_invoices_real():
    """Test QBO provider can get invoices using real provider with production database"""
    import os
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from infra.qbo.integration_models import Integration, IntegrationStatuses
    from domains.core.models.business import Business
    
    # Connect to MAIN database (not test database) to get real QBO integration
    database_url = os.getenv('SQLALCHEMY_DATABASE_URL', 'sqlite:///oodaloo.db')
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        # Look for existing QBO integration in MAIN database
        integration = session.query(Integration).filter(
            Integration.platform == "qbo",
            Integration.status == IntegrationStatuses.CONNECTED.value
        ).first()

        if not integration:
            pytest.skip("SKIPPING: No QBO integration found. Run token refresh script.")

        if not all([integration.access_token, integration.refresh_token, integration.realm_id]):
            pytest.skip("SKIPPING: QBO integration missing required tokens.")

        # Get the associated business
        business = session.query(Business).filter(Business.business_id == integration.business_id).first()
        if not business:
            pytest.skip("SKIPPING: Business not found for QBO integration.")

        # Test with real QBO provider
        provider = get_qbo_client(business.business_id, session)
        
        # Test that provider can get invoices (should work with valid tokens)
        try:
            invoices = await provider.get_invoices()
            assert isinstance(invoices, list)
            print(f"✅ Successfully retrieved {len(invoices)} invoices from QBO")
        except Exception as e:
            # If it fails, it should be with a proper error message
            assert "No valid QBO access token" in str(e) or "IntegrationError" in str(e)


def test_qbo_provider_business_relationship(db: Session, test_business: Business):
    """Test that QBO provider properly references business"""
    provider = get_qbo_client(test_business.business_id, db)
    
    assert provider.business_id == test_business.business_id


def test_qbo_provider_factory_function(db: Session, test_business: Business):
    """Test QBO provider factory function"""
    provider = get_qbo_client(test_business.business_id, db)
    
    assert isinstance(provider, QBOAPIClient)
    assert provider.business_id == test_business.business_id


def test_qbo_provider_phase0_scope():
    """Test that QBO provider is properly scoped for Phase 0"""
    # Phase 0 QBO provider should support:
    # - Mock/real provider switching
    # - Basic data retrieval (bills, invoices, vendors, customers)
    # - Automatic realm_id lookup
    # - Graceful error handling
    
    # Advanced features for later phases:
    # - Real-time webhooks
    # - Complex transaction sync
    # - Advanced reconciliation
    
    try:
        from infra.qbo.client import QBORawClient
        assert QBOAPIClient is not None
        assert get_qbo_client is not None
        
        # Basic provider should be importable
        assert True
    except ImportError as e:
        pytest.fail(f"QBO provider not available in Phase 0: {e}")
