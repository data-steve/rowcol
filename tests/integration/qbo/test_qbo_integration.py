"""
QBO Integration Test Suite

Comprehensive testing for QBO integration infrastructure including:
- Connection management and health monitoring
- Token refresh and authentication flows  
- API resilience and circuit breaker patterns
- End-to-end data flow validation
- Production scenario testing

Usage:
    # Run all QBO integration tests
    python -m pytest domains/integrations/qbo/tests/ -v
    
    # Run specific test scenarios
    python -m pytest domains/integrations/qbo/tests/test_qbo_integration.py::TestQBOConnectionManager -v
    
    # Run with real QBO sandbox (requires environment setup)
    QBO_TEST_MODE=sandbox python -m pytest domains/integrations/qbo/tests/ -v
"""

import pytest
import asyncio
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# Add project root to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.models.integration import Integration
from domains.integrations.qbo.client import QBOAPIProvider, get_qbo_provider
from domains.integrations.qbo.health import QBOHealthMonitor
from domains.integrations import SmartSyncService
from common.exceptions import IntegrationError


# Test configuration
TEST_BUSINESS_ID = "test-business-qbo-123"
TEST_REALM_ID = "9341455170902651"
TEST_ACCESS_TOKEN = "test_access_token"
TEST_REFRESH_TOKEN = "test_refresh_token"


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = Mock(spec=Session)
    
    # Mock business
    mock_business = Mock(spec=Business)
    mock_business.business_id = TEST_BUSINESS_ID
    mock_business.name = "Test Agency Inc"
    mock_business.qbo_id = TEST_REALM_ID
    mock_business.qbo_connected = True
    
    # Mock integration
    mock_integration = Mock(spec=Integration)
    mock_integration.business_id = TEST_BUSINESS_ID
    mock_integration.platform = "qbo"
    mock_integration.status = "connected"
    mock_integration.access_token = TEST_ACCESS_TOKEN
    mock_integration.refresh_token = TEST_REFRESH_TOKEN
    mock_integration.token_expires_at = datetime.now() + timedelta(hours=1)
    mock_integration.realm_id = TEST_REALM_ID
    mock_integration.connected_at = datetime.now()
    
    # Configure query behavior
    db.query.return_value.filter.return_value.first.return_value = mock_integration
    
    return db


@pytest.fixture
def qbo_connection_manager(mock_db):
    """QBO connection manager with mocked database."""
    return QBOConnectionManager(mock_db)


@pytest.fixture
def qbo_health_monitor(mock_db):
    """QBO health monitor with mocked database."""
    return QBOHealthMonitor(mock_db)


@pytest.fixture
def sample_qbo_responses():
    """Sample QBO API responses for testing."""
    return {
        "company_info": {
            "QueryResponse": {
                "CompanyInfo": [{
                    "Name": "Test Agency Inc",
                    "CompanyAddr": {"Line1": "123 Test St"},
                    "Country": "US"
                }]
            }
        },
        "bills": {
            "QueryResponse": {
                "Bill": [
                    {
                        "Id": "1",
                        "VendorRef": {"value": "101", "name": "Office Landlord"},
                        "TotalAmt": 5000.00,
                        "Balance": 5000.00,
                        "DueDate": "2025-10-15",
                        "DocNumber": "RENT-001"
                    },
                    {
                        "Id": "2", 
                        "VendorRef": {"value": "102", "name": "Software Co"},
                        "TotalAmt": 1200.00,
                        "Balance": 1200.00,
                        "DueDate": "2025-09-25",
                        "DocNumber": "SW-001"
                    }
                ]
            }
        },
        "invoices": {
            "QueryResponse": {
                "Invoice": [
                    {
                        "Id": "101",
                        "CustomerRef": {"value": "201", "name": "Client A"},
                        "TotalAmt": 8000.00,
                        "Balance": 8000.00,
                        "DueDate": "2025-09-15",
                        "DocNumber": "INV-001"
                    },
                    {
                        "Id": "102",
                        "CustomerRef": {"value": "202", "name": "Client B"},
                        "TotalAmt": 12000.00,
                        "Balance": 6000.00,  # Partially paid
                        "DueDate": "2025-10-01",
                        "DocNumber": "INV-002"
                    }
                ]
            }
        },
        "accounts": {
            "QueryResponse": {
                "Account": [
                    {
                        "Id": "301",
                        "Name": "Checking Account",
                        "AccountType": "Bank",
                        "CurrentBalance": 25000.00,
                        "AcctNum": "****1234"
                    },
                    {
                        "Id": "302",
                        "Name": "Savings Account", 
                        "AccountType": "Bank",
                        "CurrentBalance": 15000.00,
                        "AcctNum": "****5678"
                    }
                ]
            }
        }
    }


@pytest.mark.skip(reason="QBOConnectionManager was deleted - replaced by QBOAPIProvider")
class TestQBOConnectionManager:
    """Test QBO connection management functionality."""
    
    @pytest.mark.asyncio
    async def test_ensure_healthy_connection_success(self, qbo_connection_manager):
        """Test successful connection health check."""
        with patch.object(qbo_connection_manager, '_perform_health_check', return_value=True):
            with patch.object(qbo_connection_manager, '_needs_token_refresh', return_value=False):
                result = await qbo_connection_manager.ensure_healthy_connection(TEST_BUSINESS_ID)
                
                assert result is True
                assert TEST_BUSINESS_ID in qbo_connection_manager.connection_health
                
                health = qbo_connection_manager.connection_health[TEST_BUSINESS_ID]
                assert health.status == QBOConnectionStatus.HEALTHY
                assert health.consecutive_failures == 0
    
    @pytest.mark.asyncio
    async def test_ensure_healthy_connection_with_token_refresh(self, qbo_connection_manager):
        """Test connection health check with token refresh."""
        with patch.object(qbo_connection_manager, '_needs_token_refresh', return_value=True):
            with patch.object(qbo_connection_manager, '_refresh_token', return_value=True):
                with patch.object(qbo_connection_manager, '_perform_health_check', return_value=True):
                    result = await qbo_connection_manager.ensure_healthy_connection(TEST_BUSINESS_ID)
                    
                    assert result is True
    
    @pytest.mark.asyncio
    async def test_token_refresh_success(self, qbo_connection_manager, mock_db):
        """Test successful token refresh."""
        # Mock the token refresh HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        
        with patch.object(qbo_connection_manager.session, 'post', return_value=mock_response):
            with patch('os.getenv') as mock_getenv:
                mock_getenv.side_effect = lambda key: {
                    'QBO_CLIENT_ID': 'test_client_id',
                    'QBO_CLIENT_SECRET': 'test_client_secret'
                }.get(key)
                
                result = await qbo_connection_manager._refresh_token(TEST_BUSINESS_ID)
                
                assert result is True
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self, qbo_connection_manager):
        """Test circuit breaker opens after consecutive failures."""
        # Initialize connection health
        await qbo_connection_manager._initialize_connection_health(TEST_BUSINESS_ID)
        
        # Record 5 failures to trigger circuit breaker
        for i in range(5):
            qbo_connection_manager._record_failure(TEST_BUSINESS_ID, f"Test failure {i+1}")
        
        # Circuit breaker should now be open
        assert qbo_connection_manager._is_circuit_open(TEST_BUSINESS_ID) is True
        
        # Connection attempt should be blocked
        result = await qbo_connection_manager.ensure_healthy_connection(TEST_BUSINESS_ID)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_make_qbo_request_success(self, qbo_connection_manager, sample_qbo_responses):
        """Test successful QBO API request."""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_qbo_responses["company_info"]
        
        with patch.object(qbo_connection_manager, 'ensure_healthy_connection', return_value=True):
            with patch.object(qbo_connection_manager.session, 'get', return_value=mock_response):
                result = await qbo_connection_manager.make_qbo_request(
                    TEST_BUSINESS_ID, 
                    f"companyinfo/{TEST_REALM_ID}"
                )
                
                assert result == sample_qbo_responses["company_info"]
    
    @pytest.mark.asyncio
    async def test_make_qbo_request_with_token_refresh(self, qbo_connection_manager, sample_qbo_responses):
        """Test QBO API request with automatic token refresh on 401."""
        # First response: 401 (token expired)
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        
        # Second response: 200 (success after refresh)
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = sample_qbo_responses["company_info"]
        
        with patch.object(qbo_connection_manager, 'ensure_healthy_connection', return_value=True):
            with patch.object(qbo_connection_manager, '_refresh_token', return_value=True):
                with patch.object(qbo_connection_manager.session, 'get', side_effect=[mock_response_401, mock_response_200]):
                    result = await qbo_connection_manager.make_qbo_request(
                        TEST_BUSINESS_ID,
                        f"companyinfo/{TEST_REALM_ID}"
                    )
                    
                    assert result == sample_qbo_responses["company_info"]


@pytest.mark.skip(reason="QBOHealthMonitor tests need to be updated for new architecture")
class TestQBOHealthMonitor:
    """Test QBO health monitoring functionality."""
    
    @pytest.mark.asyncio
    async def test_get_health_summary(self, qbo_health_monitor, qbo_connection_manager):
        """Test health summary generation."""
        # Initialize some connection health data
        await qbo_connection_manager._initialize_connection_health(TEST_BUSINESS_ID)
        qbo_connection_manager._record_success(TEST_BUSINESS_ID)
        
        # Patch the connection manager in health monitor
        qbo_health_monitor.connection_manager = qbo_connection_manager
        
        summary = await qbo_health_monitor.get_health_summary()
        
        assert summary.total_businesses == 1
        assert summary.healthy_connections == 1
        assert summary.overall_health_percentage == 100.0
    
    @pytest.mark.asyncio
    async def test_alert_generation_on_failures(self, qbo_health_monitor, qbo_connection_manager):
        """Test alert generation when connections fail."""
        # Initialize connection and record failures
        await qbo_connection_manager._initialize_connection_health(TEST_BUSINESS_ID)
        for i in range(3):  # Trigger warning threshold
            qbo_connection_manager._record_failure(TEST_BUSINESS_ID, f"Test failure {i+1}")
        
        qbo_health_monitor.connection_manager = qbo_connection_manager
        
        # Generate alerts
        await qbo_health_monitor._generate_alerts()
        
        # Check that alerts were created
        assert TEST_BUSINESS_ID in qbo_health_monitor.active_alerts
        alerts = qbo_health_monitor.active_alerts[TEST_BUSINESS_ID]
        assert len(alerts) > 0
        assert any(alert.alert_type == "connection_degraded" for alert in alerts)
    
    @pytest.mark.asyncio
    async def test_get_business_health_details(self, qbo_health_monitor, qbo_connection_manager):
        """Test getting detailed health information for a business."""
        # Initialize connection health
        await qbo_connection_manager._initialize_connection_health(TEST_BUSINESS_ID)
        qbo_health_monitor.connection_manager = qbo_connection_manager
        
        details = await qbo_health_monitor.get_business_health_details(TEST_BUSINESS_ID)
        
        assert details is not None
        assert details["business_id"] == TEST_BUSINESS_ID
        assert "health" in details
        assert "active_alerts" in details
        assert "integration_details" in details


class TestSmartSyncServiceIntegration:
    """Test SmartSyncService integration with QBO infrastructure."""
    
    def test_smart_sync_initialization(self, mock_db):
        """Test SmartSyncService initializes properly."""
        smart_sync = SmartSyncService(mock_db, TEST_BUSINESS_ID)
        
        assert smart_sync.business_id == TEST_BUSINESS_ID
        assert smart_sync.db is not None
        assert hasattr(smart_sync, 'batch_size')
    
    @pytest.mark.asyncio
    @patch('domains.integrations.qbo.client.get_qbo_provider')
    async def test_get_qbo_data_for_digest_healthy_connection(self, mock_get_provider, mock_db):
        """Test digest data retrieval with healthy QBO connection."""
        # Mock QBO provider
        mock_provider = AsyncMock()
        mock_provider.get_all_data_batch.return_value = {
            "bills": [],
            "invoices": [], 
            "customers": [],
            "vendors": [],
            "accounts": [],
            "company_info": {}
        }
        mock_get_provider.return_value = mock_provider
        
        smart_sync = SmartSyncService(mock_db, TEST_BUSINESS_ID)
        result = await smart_sync.get_qbo_data_for_digest()
        
        assert "bills" in result
        assert "invoices" in result
        assert "business_id" in result
        assert "timestamp" in result


@pytest.mark.skip(reason="End-to-end tests need to be updated for new QBO architecture")
class TestEndToEndScenarios:
    """End-to-end testing scenarios for QBO integration."""
    
    @pytest.mark.asyncio
    async def test_complete_runway_calculation_flow(self, qbo_connection_manager, sample_qbo_responses):
        """Test complete flow from QBO data to runway calculation."""
        # Mock successful API responses for all required data
        responses = [
            sample_qbo_responses["company_info"],
            sample_qbo_responses["bills"],
            sample_qbo_responses["invoices"], 
            sample_qbo_responses["accounts"]
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        with patch.object(qbo_connection_manager, 'ensure_healthy_connection', return_value=True):
            with patch.object(qbo_connection_manager.session, 'get') as mock_get:
                mock_get.return_value = mock_response
                mock_response.json.side_effect = responses
                
                # Test health check
                is_healthy = await qbo_connection_manager.ensure_healthy_connection(TEST_BUSINESS_ID)
                assert is_healthy
                
                # Test data retrieval
                bills_data = await qbo_connection_manager.make_qbo_request(TEST_BUSINESS_ID, "bills")
                invoices_data = await qbo_connection_manager.make_qbo_request(TEST_BUSINESS_ID, "invoices")
                accounts_data = await qbo_connection_manager.make_qbo_request(TEST_BUSINESS_ID, "accounts")
                
                # Verify data structure
                assert bills_data == sample_qbo_responses["bills"]
                assert invoices_data == sample_qbo_responses["invoices"]
                assert accounts_data == sample_qbo_responses["accounts"]
    
    @pytest.mark.asyncio
    async def test_failure_recovery_scenario(self, qbo_connection_manager):
        """Test system recovery after QBO API failures."""
        # Initialize connection
        await qbo_connection_manager._initialize_connection_health(TEST_BUSINESS_ID)
        
        # Simulate API failures
        with patch.object(qbo_connection_manager, '_perform_health_check', return_value=False):
            # Record failures (but not enough to open circuit breaker)
            for i in range(3):
                result = await qbo_connection_manager.ensure_healthy_connection(TEST_BUSINESS_ID)
                assert result is False
        
        # Verify degraded status
        health = qbo_connection_manager.get_connection_health(TEST_BUSINESS_ID)
        assert health.status == QBOConnectionStatus.DEGRADED
        assert health.consecutive_failures == 3
        
        # Simulate recovery
        with patch.object(qbo_connection_manager, '_perform_health_check', return_value=True):
            result = await qbo_connection_manager.ensure_healthy_connection(TEST_BUSINESS_ID)
            assert result is True
        
        # Verify recovery
        health = qbo_connection_manager.get_connection_health(TEST_BUSINESS_ID)
        assert health.status == QBOConnectionStatus.HEALTHY
        assert health.consecutive_failures == 0


@pytest.mark.skip(reason="Production scenarios need to be updated for new QBO architecture")
class TestProductionScenarios:
    """Production-like testing scenarios."""
    
    @pytest.mark.skipif(
        os.getenv("QBO_TEST_MODE") != "sandbox",
        reason="Requires QBO_TEST_MODE=sandbox environment variable"
    )
    @pytest.mark.asyncio
    async def test_real_qbo_sandbox_connection(self):
        """Test against real QBO sandbox (requires environment setup)."""
        from db.session import SessionLocal
        
        # This test only runs with real QBO sandbox credentials
        db = SessionLocal()
        connection_manager = QBOConnectionManager(db)
        
        try:
            # Test connection health
            is_healthy = await connection_manager.ensure_healthy_connection(TEST_BUSINESS_ID)
            print(f"QBO Sandbox Connection Health: {is_healthy}")
            
            if is_healthy:
                # Test API calls
                company_info = await connection_manager.make_qbo_request(
                    TEST_BUSINESS_ID,
                    f"companyinfo/{TEST_REALM_ID}"
                )
                assert company_info is not None
                print(f"Company Info Retrieved: {company_info.get('QueryResponse', {}).get('CompanyInfo', [{}])[0].get('Name', 'Unknown')}")
                
        finally:
            db.close()
    
    def test_load_testing_simulation(self, qbo_connection_manager):
        """Simulate load testing scenarios."""
        # Test multiple concurrent connection attempts
        import concurrent.futures
        
        async def test_connection():
            return await qbo_connection_manager.ensure_healthy_connection(TEST_BUSINESS_ID)
        
        # Simulate concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(10):
                future = executor.submit(asyncio.run, test_connection())
                futures.append(future)
            
            # Wait for all requests to complete
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
        # All requests should handle concurrency gracefully
        assert len(results) == 10


# Test fixtures for integration testing
@pytest.fixture(scope="session")
def qbo_test_data():
    """Load test data for QBO integration scenarios."""
    return {
        "marketing_agency_scenario": {
            "business_profile": {
                "name": "Creative Marketing Agency",
                "industry": "Marketing",
                "employee_count": 15,
                "monthly_revenue": 85000,
                "runway_target_months": 6
            },
            "qbo_data": {
                "bills": [
                    {"vendor": "Office Landlord", "amount": 5000, "due_date": "2025-10-15"},
                    {"vendor": "Software Licenses", "amount": 1200, "due_date": "2025-09-25"},
                    {"vendor": "Marketing Tools", "amount": 800, "due_date": "2025-10-01"}
                ],
                "invoices": [
                    {"customer": "Tech Startup", "amount": 15000, "due_date": "2025-09-30"},
                    {"customer": "E-commerce Co", "amount": 22000, "due_date": "2025-10-15"},
                    {"customer": "SaaS Company", "amount": 8000, "due_date": "2025-09-20"}
                ],
                "accounts": [
                    {"name": "Operating Account", "balance": 45000},
                    {"name": "Savings Account", "balance": 25000}
                ]
            },
            "expected_runway_days": 120  # ~4 months
        }
    }


# Utility functions for testing
def create_test_integration(db: Session, business_id: str = TEST_BUSINESS_ID) -> Integration:
    """Create a test QBO integration record."""
    integration = Integration(
        business_id=business_id,
        platform="qbo",
        status="connected",
        access_token=TEST_ACCESS_TOKEN,
        refresh_token=TEST_REFRESH_TOKEN,
        token_expires_at=datetime.now() + timedelta(hours=1),
        realm_id=TEST_REALM_ID,
        connected_at=datetime.now()
    )
    db.add(integration)
    db.commit()
    return integration


def create_test_business(db: Session, business_id: str = TEST_BUSINESS_ID) -> Business:
    """Create a test business record."""
    business = Business(
        business_id=business_id,
        name="Test Agency Inc",
        industry="Professional Services",
        qbo_id=TEST_REALM_ID,
        qbo_connected=True
    )
    db.add(business)
    db.commit()
    return business


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
