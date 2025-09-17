import pytest
from unittest.mock import MagicMock, patch
from domains.core.services.qbo_integration import QBOIntegrationService
from domains.core.models.business import Business

@pytest.fixture
def mock_auth_client():
    business = MagicMock()
    business.client_id = "test_client_id"
    business.qbo_realm_id = "test_realm_id"
    business.qbo_access_token = "test_access_token"
    business.qbo_refresh_token = "test_refresh_token"
    
    with patch('domains.core.services.qbo_integration.AuthClient') as MockAuthClient:
        # We'll configure the instance of the mock in the test functions
        # This allows us to have different mock behaviors for different tests
        yield MockAuthClient

@pytest.fixture
def qbo_integration(mock_auth_client, test_business):
    return QBOIntegrationService(test_business)

def test_init(test_business, mock_auth_client):
    qbo_integration = QBOIntegrationService(test_business)
    mock_auth_client.assert_called_once_with(
        client_id=None,  # client_id is now loaded from env
        refresh_token=test_business.qbo_refresh_token,
        realm_id=test_business.qbo_realm_id
    )
    assert qbo_integration.qbo_client is not None

def test_refresh_token_success(qbo_integration, mock_auth_client):
    # Configure the mock AuthClient instance for this test
    mock_instance = mock_auth_client.return_value
    mock_instance.refresh.return_value = True
    mock_instance.access_token = "new_access_token"
    
    result = qbo_integration.refresh_token()
    
    assert result is True
    mock_instance.refresh.assert_called_once()
    assert qbo_integration.business.qbo_access_token == "new_access_token"

def test_refresh_token_failure(qbo_integration, mock_auth_client):
    # Configure the mock AuthClient instance for this test
    mock_instance = mock_auth_client.return_value
    mock_instance.refresh.return_value = False
    
    result = qbo_integration.refresh_token()
    
    assert result is False
    mock_instance.refresh.assert_called_once()
    # Ensure token was not updated
    assert qbo_integration.business.qbo_access_token != "new_access_token"

def test_get_company_info_success(qbo_integration, mock_auth_client):
    # Configure the mock AuthClient instance for this test
    mock_instance = mock_auth_client.return_value
    mock_company_info = MagicMock()
    mock_company_info.CompanyName = "Test Company"
    mock_company_info.Country = "US"
    
    with patch('domains.core.services.qbo_integration.CompanyInfo.get') as mock_get:
        mock_get.return_value = mock_company_info
        
        company_info = qbo_integration.get_company_info()
        
        assert company_info is not None
        assert company_info.CompanyName == "Test Company"
        mock_get.assert_called_once_with(qbo_integration.qbo_client)

def test_get_company_info_failure(qbo_integration, mock_auth_client):
    # Configure the mock AuthClient instance for this test
    mock_instance = mock_auth_client.return_value
    
    with patch('domains.core.services.qbo_integration.CompanyInfo.get') as mock_get:
        mock_get.side_effect = Exception("Failed to fetch company info")
        
        company_info = qbo_integration.get_company_info()
        
        assert company_info is None
        mock_get.assert_called_once_with(qbo_integration.qbo_client)
