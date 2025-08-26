"""
Unit tests for DataIngestionService

Tests the core functionality of platform data ingestion without
complex integration scenarios.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from domains.core.services.data_ingestion import DataIngestionService
from domains.core.models.integration import Integration
from domains.core.models.transaction import Transaction
from domains.core.models.job import Job


class TestDataIngestionService:
    """Unit tests for DataIngestionService core functionality."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        db = Mock()
        db.query.return_value.filter_by.return_value.first.return_value = None
        return db
    
    @pytest.fixture
    def service(self, mock_db):
        """DataIngestionService instance with mocked database."""
        return DataIngestionService(mock_db)
    
    @pytest.fixture
    def mock_integration(self):
        """Mock integration object."""
        integration = Mock(spec=Integration)
        integration.integration_id = "test_integration"
        integration.firm_id = "firm_001"
        integration.client_id = 1
        integration.access_token = "test_token"
        integration.platform = "jobber"
        return integration
    
    def test_fetch_platform_data_unsupported_platform(self, service):
        """Test that unsupported platforms raise HTTPException."""
        with pytest.raises(Exception):  # HTTPException from FastAPI
            service.fetch_platform_data("unsupported", {})
    
    def test_fetch_platform_data_routes_correctly(self, service):
        """Test that fetch_platform_data routes to correct methods."""
        with patch.object(service, '_fetch_qbo_data') as mock_qbo:
            mock_qbo.return_value = {"test": "qbo"}
            result = service.fetch_platform_data("qbo", {})
            assert result == {"test": "qbo"}
            mock_qbo.assert_called_once()
        
        with patch.object(service, '_fetch_jobber_data') as mock_jobber:
            mock_jobber.return_value = {"test": "jobber"}
            result = service.fetch_platform_data("jobber", {})
            assert result == {"test": "jobber"}
            mock_jobber.assert_called_once()
        
        with patch.object(service, '_fetch_stripe_data') as mock_stripe:
            mock_stripe.return_value = {"test": "stripe"}
            result = service.fetch_platform_data("stripe", {})
            assert result == {"test": "stripe"}
            mock_stripe.assert_called_once()
    
    def test_parse_jobber_date_formats(self, service):
        """Test Jobber date parsing handles various formats."""
        # ISO format with Z
        result = service._parse_jobber_date("2025-01-15T10:30:00Z")
        assert result == "2025-01-15"
        
        # ISO format with timezone
        result = service._parse_jobber_date("2025-01-15T10:30:00+00:00")
        assert result == "2025-01-15"
        
        # Simple date format
        result = service._parse_jobber_date("2025-01-15")
        assert result == "2025-01-15"
        
        # None input
        result = service._parse_jobber_date(None)
        assert result is None
        
        # Invalid format (should not crash)
        result = service._parse_jobber_date("invalid-date")
        # The current implementation returns the string as-is for simple formats
        assert result == "invalid-date"
    
    def test_parse_jobber_jobs_valid_data(self, service, mock_integration):
        """Test parsing valid Jobber job data."""
        jobs_data = {
            "data": {
                "jobs": {
                    "edges": [
                        {
                            "node": {
                                "id": "job_123",
                                "title": "Test Job",
                                "status": "ACTIVE",
                                "startDate": "2025-01-15T09:00:00Z",
                                "endDate": "2025-01-20T17:00:00Z"
                            }
                        }
                    ]
                }
            }
        }
        
        result = service._parse_jobber_jobs(jobs_data, mock_integration)
        
        assert len(result) == 1
        job = result[0]
        assert job["job_id"] == "JOB_job_123"
        assert job["name"] == "Test Job"
        assert job["platform_job_id"] == "job_123"
        assert job["status"] == "active"
        assert job["start_date"] == "2025-01-15"
        assert job["end_date"] == "2025-01-20"
    
    def test_parse_jobber_jobs_empty_data(self, service, mock_integration):
        """Test parsing empty Jobber job data."""
        jobs_data = {"data": {"jobs": {"edges": []}}}
        result = service._parse_jobber_jobs(jobs_data, mock_integration)
        assert result == []
        
        # Test missing data structure
        jobs_data = {}
        result = service._parse_jobber_jobs(jobs_data, mock_integration)
        assert result == []
    
    def test_parse_jobber_invoices_valid_data(self, service, mock_integration):
        """Test parsing valid Jobber invoice data."""
        invoices_data = {
            "data": {
                "invoices": {
                    "edges": [
                        {
                            "node": {
                                "id": "inv_456",
                                "invoiceNumber": "INV-001",
                                "status": "PAID",
                                "issueDate": "2025-01-15T09:00:00Z",
                                "paidDate": "2025-01-20T10:00:00Z",
                                "totalAmount": 1500.00,
                                "job": {"id": "job_123", "title": "Test Job"}
                            }
                        }
                    ]
                }
            }
        }
        
        result = service._parse_jobber_invoices(invoices_data, mock_integration)
        
        assert len(result) == 1
        invoice = result[0]
        assert invoice["txn_id"] == "INV_inv_456"
        assert invoice["amount"] == 1500.00
        assert invoice["job_id"] == "JOB_job_123"
        assert invoice["platform_txn_id"] == "inv_456"
        assert invoice["type"] == "invoice"
        assert invoice["date"] == "2025-01-15"
    
    def test_parse_stripe_charges_valid_data(self, service, mock_integration):
        """Test parsing valid Stripe charge data."""
        charges_data = {
            "data": [
                {
                    "id": "ch_123",
                    "amount": 250000,  # $2500 in cents
                    "created": 1641024000  # 2022-01-01 08:00:00 UTC
                }
            ]
        }
        
        result = service._parse_stripe_charges(charges_data, mock_integration)
        
        assert len(result) == 1
        charge = result[0]
        assert charge["txn_id"] == "CHG_ch_123"
        assert charge["amount"] == 2500.00  # Converted from cents
        assert charge["platform_txn_id"] == "ch_123"
        assert charge["type"] == "charge"
        assert charge["date"] == "2022-01-01"
    
    def test_parse_stripe_payouts_valid_data(self, service, mock_integration):
        """Test parsing valid Stripe payout data."""
        payouts_data = {
            "data": [
                {
                    "id": "po_456",
                    "amount": 500000,  # $5000 in cents
                    "created": 1641024000
                }
            ]
        }
        
        result = service._parse_stripe_payouts(payouts_data, mock_integration)
        
        assert len(result) == 1
        payout = result[0]
        assert payout["txn_id"] == "POUT_po_456"
        assert payout["amount"] == 5000.00
        assert payout["platform_txn_id"] == "po_456"
        assert payout["type"] == "payout"
        assert payout["date"] == "2022-01-01"
    
    def test_generate_simple_jobber_mock_data(self, service, mock_integration):
        """Test generation of simple Jobber mock data."""
        result = service._generate_simple_jobber_mock_data(mock_integration)
        
        assert "jobs" in result
        assert "invoices" in result
        assert len(result["jobs"]) == 5
        assert len(result["invoices"]) == 10
        
        # Check job structure
        job = result["jobs"][0]
        assert "job_id" in job
        assert "name" in job
        assert "platform_job_id" in job
        assert "status" in job
        assert job["status"] == "active"
        
        # Check invoice structure
        invoice = result["invoices"][0]
        assert "txn_id" in invoice
        assert "amount" in invoice
        assert "job_id" in invoice
        assert "platform_txn_id" in invoice
        assert "type" in invoice
        assert invoice["type"] == "invoice"
    
    def test_generate_simple_stripe_mock_data(self, service, mock_integration):
        """Test generation of simple Stripe mock data."""
        result = service._generate_simple_stripe_mock_data(mock_integration)
        
        assert "charges" in result
        assert "payouts" in result
        assert len(result["charges"]) == 20
        assert len(result["payouts"]) == 5
        
        # Check charge structure
        charge = result["charges"][0]
        assert "txn_id" in charge
        assert "amount" in charge
        assert "platform_txn_id" in charge
        assert "type" in charge
        assert charge["type"] == "charge"
        
        # Check payout structure
        payout = result["payouts"][0]
        assert "txn_id" in payout
        assert "amount" in payout
        assert "platform_txn_id" in payout
        assert "type" in payout
        assert payout["type"] == "payout"
    
    @patch('requests.post')
    def test_fetch_jobber_data_api_success(self, mock_post, service, mock_db, mock_integration):
        """Test successful Jobber API call."""
        # Setup mocks
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_integration
        
        # Mock API responses
        mock_jobs_response = Mock()
        mock_jobs_response.raise_for_status.return_value = None
        mock_jobs_response.json.return_value = {
            "data": {"jobs": {"edges": []}}
        }
        
        mock_invoices_response = Mock()
        mock_invoices_response.raise_for_status.return_value = None
        mock_invoices_response.json.return_value = {
            "data": {"invoices": {"edges": []}}
        }
        
        mock_post.side_effect = [mock_jobs_response, mock_invoices_response]
        
        result = service._fetch_jobber_data({})
        
        assert "jobs" in result
        assert "invoices" in result
        assert mock_post.call_count == 2
    
    @patch('requests.post')
    def test_fetch_jobber_data_api_failure_fallback(self, mock_post, service, mock_db, mock_integration):
        """Test Jobber API failure falls back to mock data."""
        # Setup mocks
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_integration
        
        # Mock API failure
        from requests.exceptions import RequestException
        mock_post.side_effect = RequestException("API Error")
        
        result = service._fetch_jobber_data({})
        
        # Should fallback to mock data
        assert "jobs" in result
        assert "invoices" in result
        assert len(result["jobs"]) == 5  # Mock data has 5 jobs
    
    @patch('requests.get')
    def test_fetch_stripe_data_api_success(self, mock_get, service, mock_db, mock_integration):
        """Test successful Stripe API call."""
        # Setup mocks
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_integration
        
        # Mock API responses
        mock_charges_response = Mock()
        mock_charges_response.raise_for_status.return_value = None
        mock_charges_response.json.return_value = {"data": []}
        
        mock_payouts_response = Mock()
        mock_payouts_response.raise_for_status.return_value = None
        mock_payouts_response.json.return_value = {"data": []}
        
        mock_get.side_effect = [mock_charges_response, mock_payouts_response]
        
        result = service._fetch_stripe_data({})
        
        assert "charges" in result
        assert "payouts" in result
        assert mock_get.call_count == 2
    
    @patch('requests.get')
    def test_fetch_stripe_data_api_failure_fallback(self, mock_get, service, mock_db, mock_integration):
        """Test Stripe API failure falls back to mock data."""
        # Setup mocks
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_integration
        
        # Mock API failure
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("API Error")
        
        result = service._fetch_stripe_data({})
        
        # Should fallback to mock data
        assert "charges" in result
        assert "payouts" in result
        assert len(result["charges"]) == 20  # Mock data has 20 charges
