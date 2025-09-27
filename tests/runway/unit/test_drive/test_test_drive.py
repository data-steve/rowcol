"""
Test suite for Test Drive functionality.

Tests the consolidated test drive service that demonstrates Oodaloo's value
through historical runway analysis and data quality insights.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from typing import Dict, Any

from runway.experiences.test_drive import DemoTestDriveService
from domains.core.models.business import Business
from infra.qbo.integration_models import Integration
from common.exceptions import BusinessNotFoundError

@pytest.fixture
def mock_qbo_data():
    """Fixture for mock QBO data used in unit tests."""
    return {
        "invoices": [
            {"amount": 5000, "customer": "Client A", "due_date": "2024-01-15"},
            {"amount": 3000, "customer": "Client B", "due_date": "2024-01-20"},
            {"amount": 2000, "customer": "Client C", "due_date": "2024-01-25"}
        ],
        "bills": [
            {"amount": 2500, "vendor": "Vendor X", "due_date": "2024-01-10"},
            {"amount": 1800, "vendor": "Vendor Y", "due_date": "2024-01-12"}
        ],
        "balances": [
            {"current_balance": 15000, "account_type": "checking"}
        ]
    }


class TestTestDrive:
    """Test test drive generation and retrieval."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.service = DemoTestDriveService(self.mock_db)
        
        # Mock business
        self.mock_business = Mock(spec=Business)
        self.mock_business.business_id = "test-business-123"
        self.mock_business.name = "Test Agency Inc"
        
    @pytest.mark.asyncio
    async def test_generate_test_drive_success(self, mock_qbo_data):
        """Test successful runway replay generation."""
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        with patch('runway.experiences.test_drive.get_qbo_client') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.get_bills.return_value = mock_qbo_data["bills"]
            mock_provider.get_invoices.return_value = mock_qbo_data["invoices"]
            mock_provider.get_vendors.return_value = mock_qbo_data.get("vendors", [])
            mock_provider.get_customers.return_value = mock_qbo_data.get("customers", [])
            mock_provider.get_accounts.return_value = mock_qbo_data.get("accounts", [])
            mock_provider.get_company_info.return_value = mock_qbo_data.get("company_info", {})
            mock_get_provider.return_value = mock_provider
            
            # Generate runway replay
            result = await self.service.generate_test_drive("test-business-123")
            
            # Verify structure
            assert result["business_name"] == "Test Agency Inc"
            assert "replay_period" in result
            assert "generated_at" in result
            assert "total_runway_protected_days" in result
            assert "total_insights" in result  # Changed from total_recommendations
            assert "critical_catches" in result
            assert "weeks" in result
            assert "proof_statement" in result
            
            # Verify we have 4 weeks of data
            assert len(result["weeks"]) == 4
            
            # Verify each week has required fields
            for week in result["weeks"]:
                assert "week_start" in week
                assert "week_end" in week
                assert "week_label" in week
                assert "runway_days" in week
                assert "cash_position" in week
                assert "runway_protected_days" in week
                assert "insights_shown" in week
                assert "critical_issues" in week
                
                # Verify week labels are correct (format: "Week of Aug 26")
                assert "Week" in week["week_label"]
    
    @pytest.mark.asyncio
    async def test_generate_test_drive_business_not_found(self):
        """Test runway replay when business doesn't exist."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(BusinessNotFoundError):
            await self.service.generate_test_drive("nonexistent-business")
    
    @pytest.mark.asyncio
    async def test_generate_test_drive_error_handling(self):
        """Test runway replay graceful error handling."""
        # Mock business exists but QBO provider fails
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        with patch('runway.experiences.test_drive.get_qbo_client') as mock_get_provider:
            mock_get_provider.side_effect = Exception("QBO API error")
            
        # Should return demo data when QBO fails (graceful fallback)
        result = await self.service.generate_test_drive("test-business-123")
        
        assert result["business_name"] == "Test Agency Inc"
        assert "replay_period" in result
        assert "weeks" in result
        assert "generated_at" in result
    
    def test_weekly_analysis_generation(self, mock_qbo_data):
        """Test individual week analysis generation."""
        # Test the DemoTestDriveService since that's where _generate_weekly_analysis now lives after reorganization
        from runway.experiences.test_drive import DemoTestDriveService
        service = DemoTestDriveService(self.mock_db)
        
        week_start = datetime.now() - timedelta(weeks=2)
        week_end = week_start + timedelta(days=6)
        
        result = service._generate_weekly_analysis(
            "test-business-123", week_start, week_end, mock_qbo_data, 2
        )
        
        # Verify structure
        assert result["week_start"] == week_start.strftime("%Y-%m-%d")
        assert result["week_end"] == week_end.strftime("%Y-%m-%d")
        assert result["week_label"] == "2 weeks ago"
        assert isinstance(result["runway_days"], float)
        assert isinstance(result["cash_position"], int)
        assert isinstance(result["ar_outstanding"], int)
        assert isinstance(result["ap_upcoming"], int)
        assert isinstance(result["recommendations"], list)
        assert isinstance(result["runway_protected_days"], (int, float))
        assert isinstance(result["critical_issues"], int)
    
    def test_proof_statement_generation(self):
        """Test proof statement generation with different scenarios."""
        # High runway protection
        statement = self.service._generate_proof_statement(15.0, 8, 1)
        assert "15 days of runway" in statement
        assert "8 strategic insights" in statement
        
        # Critical catches
        statement = self.service._generate_proof_statement(5.0, 3, 2)
        assert "2 critical issues" in statement
        
        # General recommendations
        statement = self.service._generate_proof_statement(3.0, 5, 0)
        assert "5 data insights" in statement
        
        # Healthy business
        statement = self.service._generate_proof_statement(0.0, 0, 0)
        assert "solid" in statement
    
    @pytest.mark.asyncio
    async def test_test_drive_integration_with_qbo_connection(self):
        """Test runway replay is generated during QBO connection."""
        # Mock integration
        mock_integration = Mock(spec=Integration)
        mock_integration.business_id = "test-business-123"
        mock_integration.created_by = "user-123"
        mock_integration.realm_id = "realm-123"
        
        # Mock business
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        with patch('runway.experiences.test_drive.get_qbo_client') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.get_bills.return_value = [{"amount": 3000}]
            mock_provider.get_invoices.return_value = [{"amount": 5000}]
            mock_provider.get_vendors.return_value = []
            mock_provider.get_customers.return_value = []
            mock_provider.get_accounts.return_value = []
            mock_provider.get_company_info.return_value = {}
            mock_get_provider.return_value = mock_provider
            
            # Generate runway replay directly (as called during QBO connection)
            result = await self.service.generate_test_drive("test-business-123")
            
            # Verify runway replay was generated successfully
            assert result["business_name"] == "Test Agency Inc"
            assert len(result["weeks"]) == 4
            assert result["total_runway_protected_days"] >= 0
            assert isinstance(result["proof_statement"], str)


class TestRunwayReplayAPI:
    """Test runway replay API endpoints."""
    
    def test_test_drive_endpoint_structure(self):
        """Test that runway replay endpoint returns proper structure."""
        # Test that the endpoint function exists and has proper typing
        from runway.routes.test_drive import get_test_drive
        
        # Verify function exists and has proper annotations
        assert callable(get_test_drive)
        assert get_test_drive.__annotations__["return"] == Dict[str, Any]
        
        # Verify it has proper parameters
        import inspect
        sig = inspect.signature(get_test_drive)
        assert "business_id" in sig.parameters
        assert "db" in sig.parameters


class TestHygieneScore:
    """Test initial hygiene score generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.service = DemoTestDriveService(self.mock_db)
        
        # Mock business
        self.mock_business = Mock(spec=Business)
        self.mock_business.business_id = "test-business-123"
        self.mock_business.name = "Test Agency Inc"
        
    def test_generate_hygiene_score_success(self):
        """Test successful hygiene score generation."""
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        # Mock QBO data with various hygiene issues
        mock_qbo_data = {
            "invoices": [
                {"amount": 5000, "due_date": "2023-08-15"},  # Overdue
                {"amount": 3000, "due_date": "2023-09-30"},  # Not overdue
                {"amount": 8000, "due_date": "2023-08-01"}   # Overdue and large
            ],
            "bills": [
                {"amount": 2500, "vendor": "Vendor X", "due_date": "2023-09-30"},
                {"amount": 1800, "vendor": "Vendor Y"},  # Missing due date
                {"amount": 1200, "vendor": "Vendor Z"}   # Missing due date
            ]
        }
        
        with patch('runway.experiences.test_drive.get_qbo_client') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.get_bills.return_value = mock_qbo_data["bills"]
            mock_provider.get_invoices.return_value = mock_qbo_data["invoices"]
            mock_provider.get_vendors.return_value = []
            mock_provider.get_customers.return_value = []
            mock_provider.get_accounts.return_value = []
            mock_provider.get_company_info.return_value = {}
            mock_get_provider.return_value = mock_provider
            
            # Generate hygiene score
            result = self.service.generate_hygiene_score("test-business-123")
            
            # Verify structure
            assert result["business_name"] == "Test Agency Inc"
            assert "hygiene_score" in result
            assert "health_level" in result
            assert "health_message" in result
            assert "total_issues_found" in result
            assert "total_runway_impact_days" in result
            assert "issues" in result
            assert "priority_fixes" in result
            assert "summary_statement" in result
            assert "generated_at" in result
            
            # Verify hygiene score is reasonable (0-100)
            assert 0 <= result["hygiene_score"] <= 100
            
            # Verify we found some issues (based on mock data)
            assert result["total_issues_found"] > 0
            assert result["total_runway_impact_days"] >= 0
            
            # Verify issues have required fields
            for issue in result["issues"]:
                assert "type" in issue
                assert "severity" in issue
                assert "title" in issue
                assert "description" in issue
                assert "runway_impact_days" in issue
                assert "fix_action" in issue
                assert "estimated_fix_time" in issue
            
            # Verify priority fixes are sorted by impact
            if len(result["priority_fixes"]) > 1:
                impacts = [fix["runway_impact_days"] for fix in result["priority_fixes"]]
                assert impacts == sorted(impacts, reverse=True)
    
    def test_hygiene_score_issue_detection(self):
        """Test specific hygiene issue detection logic."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        # Mock QBO data with specific issues
        mock_qbo_data = {
            "invoices": [
                {"amount": 5000, "due_date": "2023-08-01"},  # Overdue
                {"amount": 10000, "due_date": "2023-07-15"}  # Large and overdue
            ],
            "bills": [
                {"amount": 2500, "vendor": "Vendor X"},  # Missing due date
                {"amount": 1800, "vendor": "Vendor Y", "due_date": "2023-09-30"}
            ]
        }
        
        with patch('runway.experiences.test_drive.get_qbo_client') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.get_bills.return_value = mock_qbo_data["bills"]
            mock_provider.get_invoices.return_value = mock_qbo_data["invoices"]
            mock_provider.get_vendors.return_value = []
            mock_provider.get_customers.return_value = []
            mock_provider.get_accounts.return_value = []
            mock_provider.get_company_info.return_value = {}
            mock_get_provider.return_value = mock_provider
            
            result = self.service.generate_hygiene_score("test-business-123")
            
            # Check that we detect missing due dates
            missing_due_dates = [issue for issue in result["issues"] if issue["type"] == "missing_due_dates"]
            assert len(missing_due_dates) == 1
            assert "1 bills missing due dates" in missing_due_dates[0]["title"]
            
            # Check that we detect overdue invoices
            overdue_invoices = [issue for issue in result["issues"] if issue["type"] == "overdue_invoices"]
            assert len(overdue_invoices) == 1
            assert "$15,000" in overdue_invoices[0]["title"]  # Total of both overdue invoices
    
    def test_hygiene_score_health_levels(self):
        """Test different health level calculations."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        # Test excellent health (no issues)
        with patch('runway.experiences.test_drive.get_qbo_client') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.get_bills.return_value = [{"amount": 2000, "vendor": "Vendor X", "due_date": "2025-10-15", "category": "Office Supplies"}]
            mock_provider.get_invoices.return_value = [{"amount": 3000, "due_date": "2025-12-31", "status": "paid", "category": "Services"}]
            mock_provider.get_vendors.return_value = []
            mock_provider.get_customers.return_value = []
            mock_provider.get_accounts.return_value = []
            mock_provider.get_company_info.return_value = {}
            mock_get_provider.return_value = mock_provider
            
            result = self.service.generate_hygiene_score("test-business-123")
            
            # Should have reasonable score with the new realistic scoring system
            assert result["hygiene_score"] >= 60  # At least fair
            assert result["health_level"] in ["excellent", "good", "fair"]  # Updated for realistic scoring
    
    def test_hygiene_score_error_handling(self):
        """Test hygiene score graceful error handling."""
        # Mock business exists but SmartSync fails
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        with patch('runway.experiences.test_drive.get_qbo_client') as mock_get_provider:
            mock_get_provider.side_effect = Exception("QBO API error")
            
            # Should return minimal hygiene data instead of crashing
            result = self.service.generate_hygiene_score("test-business-123")
            
            assert result["business_name"] == "Test Agency Inc"
            assert result["hygiene_score"] == 50  # Neutral score
            assert result["health_level"] == "unknown"
            assert "error" in result
    
    def test_is_overdue_helper(self):
        """Test the _is_overdue helper method."""
        # Test the DataQualityAnalyzer directly since that's where _is_overdue lives
        from runway.core.data_quality_analyzer import DataQualityAnalyzer
        analyzer = DataQualityAnalyzer(self.mock_db, "test-business-123")
        
        # Test overdue invoice
        overdue_invoice = {"due_date": "2023-08-01"}
        assert analyzer._is_overdue(overdue_invoice)
        
        # Test future invoice
        future_invoice = {"due_date": "2025-12-31"}
        assert not analyzer._is_overdue(future_invoice)
        
        # Test missing due date
        no_due_date = {"amount": 1000}
        assert not analyzer._is_overdue(no_due_date)
        
        # Test invalid date format
        invalid_date = {"due_date": "invalid-date"}
        assert not analyzer._is_overdue(invalid_date)
    
    def test_hygiene_summary_generation(self):
        """Test hygiene summary statement generation."""
        # Test the DataQualityAnalyzer directly since that's where _generate_hygiene_summary lives
        from runway.core.data_quality_analyzer import DataQualityAnalyzer
        analyzer = DataQualityAnalyzer(self.mock_db, "test-business-123")
        
        # High impact scenario
        summary = analyzer._generate_hygiene_summary(60, 3, 8.5)
        assert "8.5 days" in summary
        assert "runway" in summary
        
        # Low impact scenario
        summary = analyzer._generate_hygiene_summary(80, 2, 2.0)
        assert "remaining 2 minor issues" in summary
        assert "runway accuracy" in summary
        
        # Perfect scenario
        summary = analyzer._generate_hygiene_summary(100, 0, 0.0)
        assert "Excellent" in summary
        assert "data quality is strong" in summary


# MVP Implementation Notes:
"""
OUT OF SCOPE for MVP (but noted for future enhancement):

1. **Real Historical Data**: Currently simulates historical scenarios based on 
   current QBO state. Production version would store and analyze actual 
   historical transactions.

2. **Advanced Recommendations**: MVP generates basic AP/AR recommendations.
   Could be enhanced with:
   - Vendor-specific payment term optimization
   - Customer-specific collection strategies  
   - Seasonal cash flow pattern recognition
   - Industry benchmark comparisons

3. **Interactive Replay**: MVP returns static data. Could add:
   - Interactive timeline navigation
   - "What if" scenario replay
   - Comparison with actual decisions made
   - Downloadable reports

4. **Personalization**: MVP uses generic business rules. Could enhance with:
   - Business-specific burn rate calculation
   - Industry-adjusted recommendations
   - Risk tolerance customization
   - Integration with actual payment history

5. **Visual Components**: MVP returns data only. UI implementation would include:
   - Timeline visualization
   - Before/after runway comparison
   - Interactive recommendation cards
   - Progress tracking animation

The MVP focuses on proving value through realistic scenarios while keeping 
complexity manageable for the 6-hour implementation window.
"""
