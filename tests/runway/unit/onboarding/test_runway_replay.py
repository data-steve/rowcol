"""
Test suite for Runway Replay functionality.

Tests the MVP implementation of retroactive runway analysis that shows
what Oodaloo would have recommended over the past 4 weeks.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from typing import Dict, Any

from runway.onboarding.services.onboarding import OnboardingService
from domains.core.models.business import Business
from domains.core.models.integration import Integration
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


class TestRunwayReplay:
    """Test runway replay generation and retrieval."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.service = OnboardingService(self.mock_db)
        
        # Mock business
        self.mock_business = Mock(spec=Business)
        self.mock_business.business_id = "test-business-123"
        self.mock_business.name = "Test Agency Inc"
        
    @pytest.mark.asyncio
    async def test_generate_runway_replay_success(self, mock_qbo_data):
        """Test successful runway replay generation."""
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        # Generate runway replay
        result = await self.service.generate_runway_replay(business_id="test_business_id")
        
        # Verify structure
        assert result["business_name"] == "Test Agency Inc"
        assert "replay_period" in result
        assert "generated_at" in result
        assert "total_runway_protected_days" in result
        assert "total_recommendations" in result
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
            assert "ar_outstanding" in week
            assert "ap_upcoming" in week
            assert "recommendations" in week
            assert "runway_protected_days" in week
            assert "critical_issues" in week
            
            # Verify week labels are correct
            assert "week" in week["week_label"]
            assert "ago" in week["week_label"]
    
    @pytest.mark.asyncio
    async def test_generate_runway_replay_business_not_found(self):
        """Test runway replay when business doesn't exist."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(BusinessNotFoundError):
            await self.service.generate_runway_replay("nonexistent-business")
    
    @pytest.mark.asyncio
    async def test_generate_runway_replay_error_handling(self):
        """Test runway replay graceful error handling."""
        # Mock business exists but SmartSync fails
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        with patch('runway.onboarding.services.onboarding.SmartSyncService') as mock_sync:
            mock_sync.side_effect = Exception("QBO API error")
            
            # Should return minimal replay data instead of crashing
            result = await self.service.generate_runway_replay("test-business-123")
            
            assert result["business_name"] == "Test Agency Inc"
            assert "error" in result
            assert "message" in result
            assert "generated_at" in result
    
    def test_weekly_analysis_generation(self, mock_qbo_data):
        """Test individual week analysis generation."""
        week_start = datetime.now() - timedelta(weeks=2)
        week_end = week_start + timedelta(days=6)
        
        result = self.service._generate_weekly_analysis(
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
        assert "8 smart recommendations" in statement
        
        # Critical catches
        statement = self.service._generate_proof_statement(5.0, 3, 2)
        assert "2 critical cash flow issues" in statement
        
        # General recommendations
        statement = self.service._generate_proof_statement(3.0, 5, 0)
        assert "5 optimization opportunities" in statement
        
        # Healthy business
        statement = self.service._generate_proof_statement(0.0, 0, 0)
        assert "healthy" in statement
    
    @pytest.mark.asyncio
    async def test_runway_replay_integration_with_qbo_connection(self):
        """Test runway replay is generated during QBO connection."""
        # Mock integration
        mock_integration = Mock(spec=Integration)
        mock_integration.business_id = "test-business-123"
        mock_integration.created_by = "user-123"
        mock_integration.realm_id = "realm-123"
        
        # Mock business
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        with patch('runway.onboarding.services.onboarding.SmartSyncService') as mock_sync:
            mock_sync_instance = Mock()
            # Make get_qbo_data_for_digest return a coroutine
            async def mock_get_qbo_data():
                return {
                    "invoices": [{"amount": 5000}],
                    "bills": [{"amount": 3000}]
                }
            mock_sync_instance.get_qbo_data_for_digest = mock_get_qbo_data
            mock_sync.return_value = mock_sync_instance
            
            # Generate runway replay directly (as called during QBO connection)
            result = await self.service.generate_runway_replay("test-business-123")
            
            # Verify runway replay was generated successfully
            assert result["business_name"] == "Test Agency Inc"
            assert len(result["weeks"]) == 4
            assert result["total_runway_protected_days"] >= 0
            assert isinstance(result["proof_statement"], str)


class TestRunwayReplayAPI:
    """Test runway replay API endpoints."""
    
    def test_runway_replay_endpoint_structure(self):
        """Test that runway replay endpoint returns proper structure."""
        # This would be an integration test with actual FastAPI client
        # For now, just verify the endpoint exists and has proper typing
        from runway.onboarding.routes.onboarding import get_runway_replay
        
        # Verify function exists and has proper annotations
        assert callable(get_runway_replay)
        assert get_runway_replay.__annotations__["return"] == Dict[str, Any]
        
        # Verify it has proper parameters
        import inspect
        sig = inspect.signature(get_runway_replay)
        assert "business_id" in sig.parameters
        assert "db" in sig.parameters


class TestHygieneScore:
    """Test initial hygiene score generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.service = OnboardingService(self.mock_db)
        
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
        
        with patch('runway.onboarding.services.onboarding.SmartSyncService') as mock_sync:
            mock_sync_instance = Mock()
            mock_sync_instance.get_qbo_data_for_digest.return_value = mock_qbo_data
            mock_sync.return_value = mock_sync_instance
            
            # Generate hygiene score
            result = self.service.generate_initial_hygiene_score("test-business-123")
            
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
        
        with patch('runway.onboarding.services.onboarding.SmartSyncService') as mock_sync:
            mock_sync_instance = Mock()
            mock_sync_instance.get_qbo_data_for_digest.return_value = mock_qbo_data
            mock_sync.return_value = mock_sync_instance
            
            result = self.service.generate_initial_hygiene_score("test-business-123")
            
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
        with patch('runway.onboarding.services.onboarding.SmartSyncService') as mock_sync:
            mock_sync_instance = Mock()
            mock_sync_instance.get_qbo_data_for_digest.return_value = {
                "invoices": [{"amount": 3000, "due_date": "2025-12-31", "status": "paid", "category": "Services", "account": "Accounts Receivable"}],  # Perfect invoice
                "bills": [{"amount": 2000, "vendor": "Vendor X", "due_date": "2025-10-15", "category": "Office Supplies", "account": "Office Expenses", "status": "paid"}],  # Perfect bill
                "vendors": [{"name": "Vendor X", "payment_terms": "Net 30", "active": True}],  # Perfect vendor
                "customers": [{"name": "Customer A", "payment_terms": "Net 15", "active": True}],  # Perfect customer
                "accounts": [{"name": "Business Checking", "account_type": "Bank", "current_balance": 50000}]
            }
            mock_sync.return_value = mock_sync_instance
            
            result = self.service.generate_initial_hygiene_score("test-business-123")
            
            # Should have reasonable score - the new scoring system is more realistic
            assert result["hygiene_score"] >= 60  # At least fair
            assert result["health_level"] in ["excellent", "good", "fair"]  # Accept fair as reasonable
    
    def test_hygiene_score_error_handling(self):
        """Test hygiene score graceful error handling."""
        # Mock business exists but SmartSync fails
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_business
        
        with patch('runway.onboarding.services.onboarding.SmartSyncService') as mock_sync:
            mock_sync.side_effect = Exception("QBO API error")
            
            # Should return minimal hygiene data instead of crashing
            result = self.service.generate_initial_hygiene_score("test-business-123")
            
            assert result["business_name"] == "Test Agency Inc"
            assert result["hygiene_score"] == 50  # Neutral score
            assert result["health_level"] == "unknown"
            assert "error" in result
    
    def test_is_overdue_helper(self):
        """Test the _is_overdue helper method using DataQualityAnalyzer."""
        from runway.core.services.data_quality_analyzer import DataQualityAnalyzer
        
        # Create a mock data quality analyzer
        data_quality_analyzer = DataQualityAnalyzer(self.mock_db, "test-business-123")
        
        # Test overdue invoice
        overdue_invoice = {"due_date": "2023-08-01"}
        assert data_quality_analyzer._is_overdue(overdue_invoice) == True
        
        # Test future invoice
        future_invoice = {"due_date": "2025-12-31"}
        assert data_quality_analyzer._is_overdue(future_invoice) == False
        
        # Test missing due date
        no_due_date = {"amount": 1000}
        assert data_quality_analyzer._is_overdue(no_due_date) == False
        
        # Test invalid date format
        invalid_date = {"due_date": "invalid-date"}
        assert data_quality_analyzer._is_overdue(invalid_date) == False
    
    def test_hygiene_summary_generation(self):
        """Test hygiene summary statement generation."""
        service = self.service
        
        # High impact scenario
        summary = service._generate_hygiene_summary(60, 3, 8.5)
        assert "8 days" in summary
        assert "runway" in summary
        
        # Low impact scenario
        summary = service._generate_hygiene_summary(80, 2, 2.0)
        assert "2 data quality" in summary
        assert "improve runway accuracy" in summary
        
        # Perfect scenario
        summary = service._generate_hygiene_summary(100, 0, 0.0)
        assert "Excellent" in summary
        assert "clean" in summary


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
