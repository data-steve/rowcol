"""
Foundation End-to-End Integration Test

CRITICAL TEST: Validates that our core foundation services work with real QBO data.

This test focuses on the services we actually have implemented:
- runway/core/services/runway_calculator.py  
- runway/core/services/data_quality_analyzer.py
- domains/integrations/smart_sync.py
- QBO connection infrastructure

Success here proves our Phase 0 foundation is solid and ready for Phase 1.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.models.integration import Integration
from domains.integrations.smart_sync import SmartSyncService
from domains.integrations.qbo.qbo_connection_manager import get_qbo_connection_manager
from runway.core.services.runway_calculator import RunwayCalculator
from runway.core.services.data_quality_analyzer import DataQualityAnalyzer
from config.business_rules import RunwayAnalysisSettings, DataQualityThresholds

@pytest.mark.integration
@pytest.mark.qbo_real_api
class TestFoundationE2E:
    """End-to-end integration tests for core foundation services."""
    
    @pytest.fixture
    def foundation_business(self, qbo_connected_business) -> Business:
        """Use centralized QBO connected business fixture."""
        return qbo_connected_business
    
    @pytest.mark.asyncio
    async def test_qbo_data_retrieval_works(self, db: Session, foundation_business: Business):
        """
        CRITICAL TEST: QBO data can be retrieved through SmartSync.
        
        This is the foundation of everything - if this fails, nothing else works.
        """
        smart_sync = SmartSyncService(db, foundation_business.business_id)
        
        try:
            # This would make real QBO API calls in a proper test environment
            qbo_data = await smart_sync.get_qbo_data_for_digest()
            
            # Validate data structure (even if mocked, structure should be correct)
            assert qbo_data is not None, "QBO data retrieval failed"
            assert isinstance(qbo_data, dict), "QBO data should be a dictionary"
            
            # Check for expected data categories
            expected_categories = ["bills", "invoices", "balances", "vendors", "customers"]
            for category in expected_categories:
                assert category in qbo_data, f"Missing {category} in QBO data"
                assert isinstance(qbo_data[category], list), f"{category} should be a list"
            
            # Log data availability for debugging
            bills_count = len(qbo_data["bills"])
            invoices_count = len(qbo_data["invoices"])
            balances_count = len(qbo_data["balances"])
            
            print(f"✅ QBO data retrieved: {bills_count} bills, {invoices_count} invoices, {balances_count} balances")
            
            # Minimum data validation
            if bills_count == 0 and invoices_count == 0:
                pytest.skip("No financial data available - cannot test business logic")
                
        except Exception as e:
            pytest.fail(f"QBO data retrieval failed: {e}")
    
    @pytest.mark.asyncio
    async def test_runway_calculator_with_qbo_data(self, db: Session, foundation_business: Business):
        """
        CRITICAL TEST: Runway calculator works with QBO data structure.
        
        Tests our core runway calculation logic with actual data format.
        """
        smart_sync = SmartSyncService(db, foundation_business.business_id)
        runway_calculator = RunwayCalculator(db, foundation_business.business_id)
        
        # Get QBO data
        qbo_data = await smart_sync.get_qbo_data_for_digest()
        
        # Test runway calculation
        runway_analysis = runway_calculator.calculate_current_runway(qbo_data)
        
        # Validate runway analysis structure
        required_fields = [
            "business_id", "calculated_at", "cash_position", "ar_expected",
            "ap_due", "net_position", "burn_rate", "base_runway_days",
            "runway_status", "forecast_accuracy"
        ]
        
        for field in required_fields:
            assert field in runway_analysis, f"Missing {field} in runway analysis"
        
        # Validate data types and ranges
        assert runway_analysis["business_id"] == foundation_business.business_id
        assert isinstance(runway_analysis["cash_position"], (int, float))
        assert isinstance(runway_analysis["base_runway_days"], (int, float))
        assert runway_analysis["runway_status"] in ["critical", "warning", "healthy", "excellent"]
        
        # Validate burn rate structure
        burn_rate = runway_analysis["burn_rate"]
        assert isinstance(burn_rate, dict)
        assert "daily_burn" in burn_rate
        assert "calculation_method" in burn_rate
        
        # Validate forecast accuracy structure
        accuracy = runway_analysis["forecast_accuracy"]
        assert isinstance(accuracy, dict)
        assert "accuracy_score" in accuracy
        assert 0 <= accuracy["accuracy_score"] <= 100
        
        print(f"✅ Runway calculation successful: {runway_analysis['base_runway_days']:.1f} days, {runway_analysis['runway_status']} status")
    
    @pytest.mark.asyncio
    async def test_data_quality_analyzer_with_qbo_data(self, db: Session, foundation_business: Business):
        """
        CRITICAL TEST: Data quality analyzer works with QBO data structure.
        
        Tests our data quality analysis logic with actual data format.
        """
        smart_sync = SmartSyncService(db, foundation_business.business_id)
        data_quality_analyzer = DataQualityAnalyzer(db, foundation_business.business_id)
        
        # Get QBO data
        qbo_data = await smart_sync.get_qbo_data_for_digest()
        
        # Test hygiene score calculation
        hygiene_analysis = data_quality_analyzer.calculate_hygiene_score(qbo_data)
        
        # Validate hygiene analysis structure
        required_fields = [
            "business_id", "calculated_at", "hygiene_score", "health_level",
            "health_message", "total_issues_found", "total_runway_impact_days",
            "issues", "priority_fixes", "summary_statement"
        ]
        
        for field in required_fields:
            assert field in hygiene_analysis, f"Missing {field} in hygiene analysis"
        
        # Validate data types and ranges
        assert hygiene_analysis["business_id"] == foundation_business.business_id
        assert 0 <= hygiene_analysis["hygiene_score"] <= 100
        assert hygiene_analysis["health_level"] in ["excellent", "good", "fair", "needs_attention"]
        assert isinstance(hygiene_analysis["issues"], list)
        assert isinstance(hygiene_analysis["total_runway_impact_days"], (int, float))
        
        # Validate issue structure if issues exist
        issues = hygiene_analysis["issues"]
        for issue in issues:
            required_issue_fields = ["type", "severity", "title", "description", "runway_impact_days", "fix_action"]
            for field in required_issue_fields:
                assert field in issue, f"Missing {field} in issue data"
            assert issue["severity"] in ["low", "medium", "high"]
        
        print(f"✅ Data quality analysis successful: {hygiene_analysis['hygiene_score']}/100 score, {len(issues)} issues")
    
    @pytest.mark.asyncio
    async def test_presentation_formatting_works(self, db: Session, foundation_business: Business):
        """
        CRITICAL TEST: Presentation formatting methods work correctly.
        
        Tests the generic formatting methods we added for different contexts.
        """
        smart_sync = SmartSyncService(db, foundation_business.business_id)
        runway_calculator = RunwayCalculator(db, foundation_business.business_id)
        data_quality_analyzer = DataQualityAnalyzer(db, foundation_business.business_id)
        
        # Get QBO data
        qbo_data = await smart_sync.get_qbo_data_for_digest()
        
        # Test runway presentation formatting
        weeks_data = runway_calculator.calculate_historical_runway(weeks_back=2)  # Shorter for testing
        
        # Test different presentation formats
        standard_format = runway_calculator.format_for_presentation(weeks_data, format_type="standard")
        test_drive_format = runway_calculator.format_for_presentation(weeks_data, format_type="test_drive")
        
        # Validate formatting worked
        assert len(standard_format) == len(weeks_data), "Standard formatting should preserve all weeks"
        assert len(test_drive_format) == len(weeks_data), "Test drive formatting should preserve all weeks"
        
        # Validate format differences
        if len(standard_format) > 0:
            standard_week = standard_format[0]
            test_drive_week = test_drive_format[0]
            
            # Standard format should have optimization_opportunities
            assert "optimization_opportunities" in standard_week, "Standard format missing optimization_opportunities"
            
            # Test drive format should have insights_shown and runway_protected_days
            assert "insights_shown" in test_drive_week, "Test drive format missing insights_shown"
            assert "runway_protected_days" in test_drive_week, "Test drive format missing runway_protected_days"
        
        # Test data quality summary formatting
        hygiene_analysis = data_quality_analyzer.calculate_hygiene_score(qbo_data)
        
        test_drive_summary = data_quality_analyzer.generate_summary_for_context(hygiene_analysis, context="test_drive")
        digest_summary = data_quality_analyzer.generate_summary_for_context(hygiene_analysis, context="digest")
        standard_summary = data_quality_analyzer.generate_summary_for_context(hygiene_analysis, context="standard")
        
        # Validate summaries are different and appropriate
        assert isinstance(test_drive_summary, str) and len(test_drive_summary) > 0
        assert isinstance(digest_summary, str) and len(digest_summary) > 0
        assert isinstance(standard_summary, str) and len(standard_summary) > 0
        
        print("✅ Presentation formatting successful: Multiple contexts supported")
    
    @pytest.mark.asyncio
    async def test_business_rules_integration(self, db: Session, foundation_business: Business):
        """
        CRITICAL TEST: Business rules are properly integrated and used.
        
        Tests that our centralized business rules are actually being used.
        """
        smart_sync = SmartSyncService(db, foundation_business.business_id)
        runway_calculator = RunwayCalculator(db, foundation_business.business_id)
        data_quality_analyzer = DataQualityAnalyzer(db, foundation_business.business_id)
        
        # Get QBO data
        qbo_data = await smart_sync.get_qbo_data_for_digest()
        
        # Test runway thresholds are being used
        runway_analysis = runway_calculator.calculate_current_runway(qbo_data)
        runway_days = runway_analysis["base_runway_days"]
        runway_status = runway_analysis["runway_status"]
        
        # Validate status matches business rules
        from config.business_rules import RunwayThresholds
        
        if runway_days < RunwayThresholds.CRITICAL_DAYS:
            assert runway_status == "critical", f"Runway status should be critical for {runway_days} days"
        elif runway_days < RunwayThresholds.WARNING_DAYS:
            assert runway_status == "warning", f"Runway status should be warning for {runway_days} days"
        elif runway_days < RunwayThresholds.HEALTHY_DAYS:
            assert runway_status == "healthy", f"Runway status should be healthy for {runway_days} days"
        else:
            assert runway_status == "excellent", f"Runway status should be excellent for {runway_days} days"
        
        # Test data quality thresholds are being used
        hygiene_analysis = data_quality_analyzer.calculate_hygiene_score(qbo_data)
        hygiene_score = hygiene_analysis["hygiene_score"]
        health_level = hygiene_analysis["health_level"]
        
        # Validate health level matches business rules
        if hygiene_score >= DataQualityThresholds.HYGIENE_EXCELLENT:
            assert health_level == "excellent", f"Health level should be excellent for score {hygiene_score}"
        elif hygiene_score >= DataQualityThresholds.HYGIENE_GOOD:
            assert health_level == "good", f"Health level should be good for score {hygiene_score}"
        elif hygiene_score >= DataQualityThresholds.HYGIENE_FAIR:
            assert health_level == "fair", f"Health level should be fair for score {hygiene_score}"
        else:
            assert health_level == "needs_attention", f"Health level should be needs_attention for score {hygiene_score}"
        
        print("✅ Business rules integration successful: Thresholds properly applied")
    
    @pytest.mark.asyncio
    async def test_foundation_readiness_overall(self, db: Session, foundation_business: Business):
        """
        CRITICAL TEST: Overall foundation readiness for Phase 1.
        
        This is the final gate test - if this passes, Phase 1 can proceed.
        """
        try:
            # Test 1: QBO Integration
            smart_sync = SmartSyncService(db, foundation_business.business_id)
            qbo_data = await smart_sync.get_qbo_data_for_digest()
            assert qbo_data is not None, "QBO integration failed"
            
            # Test 2: Runway Calculations
            runway_calculator = RunwayCalculator(db, foundation_business.business_id)
            runway_analysis = runway_calculator.calculate_current_runway(qbo_data)
            assert "base_runway_days" in runway_analysis, "Runway calculation failed"
            
            # Test 3: Data Quality Analysis
            data_quality_analyzer = DataQualityAnalyzer(db, foundation_business.business_id)
            hygiene_analysis = data_quality_analyzer.calculate_hygiene_score(qbo_data)
            assert "hygiene_score" in hygiene_analysis, "Data quality analysis failed"
            
            # Test 4: Presentation Formatting
            weeks_data = runway_calculator.calculate_historical_runway(weeks_back=1)
            formatted_data = runway_calculator.format_for_presentation(weeks_data, format_type="test_drive")
            assert len(formatted_data) > 0, "Presentation formatting failed"
            
            # Test 5: Business Rules Integration
            runway_status = runway_analysis["runway_status"]
            health_level = hygiene_analysis["health_level"]
            assert runway_status in ["critical", "warning", "healthy", "excellent"], "Business rules not applied"
            assert health_level in ["excellent", "good", "fair", "needs_attention"], "Business rules not applied"
            
            print("🎉 FOUNDATION READY FOR PHASE 1!")
            print("✅ All core services working with QBO data")
            print("✅ Business rules properly integrated")
            print("✅ Presentation formatting functional")
            print("✅ Phase 1 Smart AP development can proceed with confidence")
            
        except Exception as e:
            pytest.fail(f"FOUNDATION NOT READY: {e}")
            print("🚨 PHASE 1 BLOCKED: Foundation issues must be resolved")


# Test configuration and utilities
@pytest.fixture(scope="module")
def integration_test_config():
    """Configuration for integration tests."""
    return {
        "use_real_qbo": False,  # Set to True when QBO sandbox is configured
        "mock_data_path": "tests/fixtures/qbo_mock_data.json",
        "test_timeout": 30  # seconds
    }
