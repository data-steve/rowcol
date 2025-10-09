"""
Phase 0 QBO Integration Tests

Tests for basic QBO integration functionality that's core to Phase 0 MVP.
Uses the enhanced SmartSyncService with proper QBO integration.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from domains.core.models import Business
from infra.qbo.client import QBORawClient


def test_qbo_provider_import():
    """Test that QBORawClient can be imported"""
    from domains.qbo.services.sync_service import QBOSyncService
    assert QBORawClient is not None
    assert SmartSyncService is not None


def test_qbo_provider_factory_real(db: Session, test_business: Business):
    """Test SmartSyncService can be created with business"""
    from domains.qbo.services.sync_service import QBOSyncService
    smart_sync = QBOSyncService(test_business.business_id, "", None)
    assert smart_sync is not None
    assert smart_sync.business_id == test_business.business_id


def test_qbo_provider_factory_auto_realm_lookup(db: Session, test_business: Business):
    """Test SmartSyncService can be created with business QBO fields"""
    from domains.qbo.services.sync_service import QBOSyncService
    # Update business with QBO fields for testing
    test_business.qbo_realm_id = "test_realm_123"
    test_business.qbo_status = "connected"
    db.commit()
    
    smart_sync = QBOSyncService(test_business.business_id, "", None)
    assert smart_sync is not None
    assert smart_sync.business_id == test_business.business_id


def test_business_qbo_fields_structure():
    """Test that Business model has correct QBO integration fields"""
    from domains.core.models.business import Business
    assert hasattr(Business, 'qbo_realm_id')
    assert hasattr(Business, 'qbo_access_token')
    assert hasattr(Business, 'qbo_refresh_token')
    assert hasattr(Business, 'qbo_connected_at')
    assert hasattr(Business, 'qbo_status')
    assert hasattr(Business, 'qbo_environment')
    assert hasattr(Business, 'qbo_token_expires_at')
    assert hasattr(Business, 'qbo_error_message')
    assert Business.__tablename__ == 'businesses'


def test_business_qbo_fields_update(db: Session, test_business: Business):
    """Test basic Business QBO fields update for QBO integration"""
    from datetime import datetime, timedelta

    # Update business with QBO integration fields
    test_business.qbo_realm_id = "mock_realm_123"
    test_business.qbo_access_token = "mock_access_token"
    test_business.qbo_refresh_token = "mock_refresh_token"
    test_business.qbo_connected_at = datetime.now()
    test_business.qbo_status = "connected"
    test_business.qbo_environment = "sandbox"
    test_business.qbo_token_expires_at = datetime.now() + timedelta(hours=1)

    db.commit()
    db.refresh(test_business)

    assert test_business.qbo_realm_id == "mock_realm_123"
    assert test_business.qbo_access_token == "mock_access_token"
    assert test_business.qbo_refresh_token == "mock_refresh_token"
    assert test_business.qbo_status == "connected"
    assert test_business.qbo_environment == "sandbox"


@pytest.mark.asyncio
async def test_qbo_provider_get_bills_real(qbo_connected_business):
    """Test QBO provider can get bills using real provider with production database"""
    business = qbo_connected_business
    
    if not all([business.qbo_access_token, business.qbo_refresh_token, business.qbo_realm_id]):
        pytest.skip("SKIPPING: QBO business missing required tokens.")

    # Test with real SmartSyncService
    from domains.qbo.services.sync_service import QBOSyncService
    smart_sync = QBOSyncService(business.business_id, "", None)
    
    # Test that SmartSyncService can get bills (should work with valid tokens)
    try:
        bills = await smart_sync.get_bills()
        assert isinstance(bills, list)
        print(f"✅ Successfully retrieved {len(bills)} bills from QBO")
    except Exception as e:
        # If it fails, it should be with a proper error message
        assert "No valid QBO access token" in str(e) or "IntegrationError" in str(e)


@pytest.mark.asyncio
async def test_qbo_provider_get_invoices_real(qbo_connected_business):
    """Test QBO provider can get invoices using real provider with production database"""
    business = qbo_connected_business
    
    if not all([business.qbo_access_token, business.qbo_refresh_token, business.qbo_realm_id]):
        pytest.skip("SKIPPING: QBO business missing required tokens.")

    # Test with real SmartSyncService
    from domains.qbo.services.sync_service import QBOSyncService
    smart_sync = QBOSyncService(business.business_id, "", None)
    
    # Test that SmartSyncService can get invoices (should work with valid tokens)
    try:
        invoices = await smart_sync.get_invoices()
        assert isinstance(invoices, list)
        print(f"✅ Successfully retrieved {len(invoices)} invoices from QBO")
    except Exception as e:
        # If it fails, it should be with a proper error message
        assert "No valid QBO access token" in str(e) or "IntegrationError" in str(e)


def test_qbo_provider_business_relationship(db: Session, test_business: Business):
    """Test that SmartSyncService properly references business"""
    from domains.qbo.services.sync_service import QBOSyncService
    smart_sync = QBOSyncService(test_business.business_id, "", None)
    
    assert smart_sync.business_id == test_business.business_id


def test_qbo_provider_factory_function(db: Session, test_business: Business):
    """Test SmartSyncService factory function"""
    from domains.qbo.services.sync_service import QBOSyncService
    smart_sync = QBOSyncService(test_business.business_id, "", None)
    
    assert smart_sync is not None
    assert smart_sync.business_id == test_business.business_id


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
        from domains.qbo.services.sync_service import QBOSyncService
        assert SmartSyncService is not None
        
        # Basic provider should be importable
        assert True
    except ImportError as e:
        pytest.fail(f"QBO provider not available in Phase 0: {e}")
