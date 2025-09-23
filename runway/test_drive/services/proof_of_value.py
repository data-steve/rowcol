"""
Proof of Value Service

Handles "Test Drive" functionality that demonstrates Oodaloo's value to prospects
and new users through historical analysis and data quality insights.

This is separate from core onboarding to maintain clear separation of concerns:
- Onboarding = User setup, QBO connection, business profile
- Test Drive = Proof of value, demos, historical analysis

Features:
- Runway Replay: Retroactive 4-week runway analysis
- Hygiene Score: Data quality assessment with runway impact
- Value Demonstration: Shows what Oodaloo would have recommended
"""

from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.models.integration import Integration
from domains.integrations.qbo.qbo_api_provider import get_qbo_provider
from runway.core.services.runway_calculator import RunwayCalculator
from runway.core.services.data_quality_analyzer import DataQualityAnalyzer
from config.business_rules import RunwayAnalysisSettings, DataQualityThresholds, ProofOfValueThresholds
from common.exceptions import BusinessNotFoundError
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ProofOfValueService:
    """Service for generating proof-of-value demonstrations."""
    
    def __init__(self, db: Session):
        self.db = db
        # Initialize core analytics services
        self._runway_calculators = {}  # Cache calculators per business
        self._data_quality_analyzers = {}  # Cache analyzers per business
    
    def generate_runway_replay(self, business_id: str = None, industry: str = "software_agency", use_sandbox: bool = False) -> Dict[str, Any]:
        """
        Generate a retroactive 4-week runway digest showing insights and data patterns Oodaloo would have surfaced.
        
        This is a "Test Drive" feature that demonstrates value by showing historical insights.
        Can work with real business data OR demo data for prospects.
        """
        try:
            logger.info(f"Generating runway replay for business {business_id} or industry {industry}")
            
            # Check if this is a real business, sandbox, or demo scenario
            if business_id:
                business = self.db.query(Business).filter(Business.business_id == business_id).first()
                if not business:
                    raise BusinessNotFoundError(f"Business {business_id} not found")
                business_name = business.name
                # Use real QBO data
                qbo_data = self._get_real_qbo_data(business_id)
            elif use_sandbox:
                # Use QBO sandbox with sample data
                business_name = self._get_demo_business_name(industry)
                qbo_data = self._get_qbo_sandbox_data(industry)
            else:
                # Use demo data for test drive
                business_name = self._get_demo_business_name(industry)
                qbo_data = self._get_demo_qbo_data(industry)
            
            # Get runway calculator for this business
            runway_calculator = self._get_runway_calculator(business_id or f"demo_{industry}")
            
            # Use core service for historical runway analysis
            weeks_data = runway_calculator.calculate_historical_runway(weeks_back=4, qbo_data=qbo_data)
            
            # Use core service for test drive formatting
            weeks_data = runway_calculator.format_for_presentation(weeks_data, format_type="test_drive")
            
            total_runway_protected = sum(week["runway_protected_days"] for week in weeks_data)
            total_insights = sum(len(week["insights_shown"]) for week in weeks_data)
            critical_catches = sum(1 for week in weeks_data if week["critical_issues"] > 0)
            
            replay_summary = {
                "business_name": business_name,
                "replay_period": "Past 4 weeks",
                "generated_at": datetime.now().isoformat(),
                "total_runway_protected_days": total_runway_protected,
                "total_insights": total_insights,
                "critical_catches": critical_catches,
                "weeks": weeks_data,
                "proof_statement": self._generate_proof_statement(
                    total_runway_protected, total_insights, critical_catches
                ),
                "test_drive_type": "runway_replay"
            }
            
            logger.info(f"Runway replay generated: {total_runway_protected} days protected, {total_insights} insights surfaced")
            return replay_summary
            
        except BusinessNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate runway replay for {business_id}: {e}", exc_info=True)
            return {
                "business_name": business.name if 'business' in locals() else "Unknown",
                "error": "Could not generate full replay",
                "message": "We're still setting up your historical analysis. Your weekly digest will start next week!",
                "generated_at": datetime.now().isoformat(),
                "test_drive_type": "runway_replay"
            }
    
    def generate_hygiene_score(self, business_id: str) -> Dict[str, Any]:
        """
        Generate a data hygiene score showing QBO data quality issues.
        
        This demonstrates value by showing how fixing data quality improves runway accuracy.
        """
        try:
            logger.info(f"Generating hygiene score for business {business_id}")
            
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                raise BusinessNotFoundError(f"Business {business_id} not found")
            
            # Get data quality analyzer for this business
            data_quality_analyzer = self._get_data_quality_analyzer(business_id)
            
            # Get QBO data for analysis using QBOAPIProvider directly
            qbo_provider = get_qbo_provider(business_id, self.db)
            qbo_data = {
                "bills": qbo_provider.get_bills(),
                "invoices": qbo_provider.get_invoices(),
                "vendors": qbo_provider.get_vendors(),
                "customers": qbo_provider.get_customers(),
                "accounts": qbo_provider.get_accounts(),
                "company_info": qbo_provider.get_company_info()
            }
            
            # Use core service for hygiene score calculation
            hygiene_analysis = data_quality_analyzer.calculate_hygiene_score(qbo_data)
            
            # Extract results for test drive format
            issues = hygiene_analysis.get("issues", [])
            total_runway_impact_days = hygiene_analysis.get("total_runway_impact_days", 0)
            hygiene_score = hygiene_analysis.get("hygiene_score", 50)
            health_level = hygiene_analysis.get("health_level", "unknown")
            health_message = hygiene_analysis.get("health_message", "Analysis unavailable")
            priority_fixes = hygiene_analysis.get("priority_fixes", [])
            
            hygiene_result = {
                "business_name": business.name,
                "hygiene_score": hygiene_score,
                "health_level": health_level,
                "health_message": health_message,
                "total_issues_found": len(issues),
                "total_runway_impact_days": round(total_runway_impact_days, 1),
                "issues": issues,
                "priority_fixes": priority_fixes,
                "summary_statement": data_quality_analyzer.generate_summary_for_context(
                    hygiene_analysis, context="test_drive"
                ),
                "generated_at": datetime.now().isoformat(),
                "test_drive_type": "hygiene_score"
            }
            
            logger.info(f"Hygiene score generated: {hygiene_score}/100, {len(issues)} issues, +{total_runway_impact_days:.1f} days potential")
            return hygiene_result
            
        except BusinessNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate hygiene score for {business_id}: {e}", exc_info=True)
            return {
                "business_name": business.name if 'business' in locals() else "Unknown",
                "hygiene_score": 50,
                "health_level": "unknown",
                "health_message": "We're still analyzing your QBO data quality.",
                "error": "Could not complete full analysis",
                "generated_at": datetime.now().isoformat(),
                "test_drive_type": "hygiene_score"
            }
    
    def generate_qbo_sandbox_test_drive(self, industry: str = "software_agency") -> Dict[str, Any]:
        """
        Generate test drive using QBO sandbox with realistic sample data.
        
        This is the most realistic test drive option - uses actual QBO sandbox
        with pre-populated sample data that looks like a real business.
        """
        return self.generate_runway_replay(
            business_id=None, 
            industry=industry, 
            use_sandbox=True
        )
    
    def _get_runway_calculator(self, business_id: str) -> RunwayCalculator:
        """Get or create runway calculator for business."""
        if business_id not in self._runway_calculators:
            self._runway_calculators[business_id] = RunwayCalculator(self.db, business_id)
        return self._runway_calculators[business_id]
    
    def _get_data_quality_analyzer(self, business_id: str) -> DataQualityAnalyzer:
        """Get or create data quality analyzer for business."""
        if business_id not in self._data_quality_analyzers:
            self._data_quality_analyzers[business_id] = DataQualityAnalyzer(self.db, business_id)
        return self._data_quality_analyzers[business_id]
    
    def _get_real_qbo_data(self, business_id: str) -> Dict[str, Any]:
        """Get real QBO data for existing business."""
        # This would use QBOAPIProvider for real data
        # For now, return empty data
        return {
            "bills": [],
            "invoices": [],
            "vendors": [],
            "customers": [],
            "accounts": [],
            "company_info": {}
        }
    
    def _get_qbo_sandbox_data(self, industry: str = "software_agency") -> Dict[str, Any]:
        """Get QBO sandbox data with realistic sample data for test drive."""
        # This would connect to QBO sandbox with sample data
        # For now, return enhanced demo data that looks like real QBO sandbox
        return self._get_demo_qbo_data(industry)
    
    def _get_demo_business_name(self, industry: str) -> str:
        """Get demo business name based on industry."""
        demo_names = {
            "software_agency": "TechFlow Solutions",
            "consulting_firm": "Strategic Partners LLC",
            "ecommerce": "Digital Commerce Co",
            "restaurant": "Bistro Excellence",
            "retail": "Urban Retail Group"
        }
        return demo_names.get(industry, "Demo Business")
    
    def _get_demo_qbo_data(self, industry: str) -> Dict[str, Any]:
        """Get realistic demo QBO data based on industry."""
        if industry == "software_agency":
            return {
                "bills": [
                    {
                        "qbo_id": "1",
                        "vendor_ref": {"value": "1", "name": "AWS"},
                        "amount": 2500.00,
                        "due_date": "2024-01-15",
                        "txn_date": "2024-01-01",
                        "balance": 2500.00,
                        "doc_number": "BILL-001",
                        "memo": "Cloud hosting services"
                    },
                    {
                        "qbo_id": "2",
                        "vendor_ref": {"value": "2", "name": "Office Rent Co"},
                        "amount": 4500.00,
                        "due_date": "2024-01-01",
                        "txn_date": "2023-12-15",
                        "balance": 4500.00,
                        "doc_number": "BILL-002",
                        "memo": "Monthly office rent"
                    },
                    {
                        "qbo_id": "3",
                        "vendor_ref": {"value": "3", "name": "Software Licenses Inc"},
                        "amount": 1200.00,
                        "due_date": "2024-01-20",
                        "txn_date": "2024-01-05",
                        "balance": 1200.00,
                        "doc_number": "BILL-003",
                        "memo": "Monthly software licenses"
                    }
                ],
                "invoices": [
                    {
                        "qbo_id": "1",
                        "customer_ref": {"value": "1", "name": "Acme Corp"},
                        "amount": 15000.00,
                        "due_date": "2024-01-10",
                        "txn_date": "2023-12-20",
                        "balance": 15000.00,
                        "doc_number": "INV-001",
                        "memo": "Q4 Development Services"
                    },
                    {
                        "qbo_id": "2",
                        "customer_ref": {"value": "2", "name": "TechStart LLC"},
                        "amount": 8500.00,
                        "due_date": "2024-01-25",
                        "txn_date": "2024-01-01",
                        "balance": 8500.00,
                        "doc_number": "INV-002",
                        "memo": "Mobile App Development"
                    }
                ],
                "accounts": [
                    {
                        "qbo_id": "1",
                        "name": "Business Checking",
                        "account_type": "Bank",
                        "account_sub_type": "Checking",
                        "current_balance": 25000.00,
                        "active": True
                    },
                    {
                        "qbo_id": "2",
                        "name": "Business Savings",
                        "account_type": "Bank",
                        "account_sub_type": "Savings",
                        "current_balance": 15000.00,
                        "active": True
                    }
                ],
                "company_info": {
                    "qbo_id": "1",
                    "company_name": "TechFlow Solutions",
                    "legal_name": "TechFlow Solutions Inc",
                    "country": "US"
                }
            }
        else:
            # Default demo data for other industries
            return {
                "bills": [],
                "invoices": [],
                "accounts": [{"current_balance": 10000.00}],
                "company_info": {"company_name": "Demo Business"}
            }
    
    # NOTE: All generic data transformation moved to core domain services
    # This service now focuses ONLY on test drive-specific marketing language
    
    # NOTE: Date checking functions moved to core analytics services
    # This service now focuses only on test drive presentation and marketing language
    
    def _generate_proof_statement(self, total_protected: float, total_insights: int, 
                                 critical_catches: int) -> str:
        """
        Generate a compelling proof statement by combining ALL applicable achievements.
        
        Unlike the previous flawed if/elif logic, this builds a statement that acknowledges
        all significant achievements since they are independent metrics.
        """
        achievements = []
        
        # Check each achievement independently
        if total_protected > ProofOfValueThresholds.SIGNIFICANT_RUNWAY_PROTECTION:
            achievements.append(f"protected {total_protected:.0f} days of runway")
        
        if total_insights > ProofOfValueThresholds.MANY_INSIGHTS_THRESHOLD:
            achievements.append(f"surfaced {total_insights} strategic insights")
        
        if critical_catches > 0:
            achievements.append(f"flagged {critical_catches} critical issue{'s' if critical_catches > 1 else ''}")
        
        # Build combined statement based on what was achieved
        if len(achievements) >= 2:
            # Multiple significant achievements - combine them
            last_achievement = achievements.pop()
            combined = ", ".join(achievements) + f", and {last_achievement}"
            return f"In just 4 weeks, Oodaloo would have {combined}!"
        elif len(achievements) == 1:
            # Single significant achievement
            return f"Over the past 4 weeks, Oodaloo would have {achievements[0]}."
        else:
            # No major achievements, but still positive
            if total_insights > 0:
                return f"Oodaloo would have provided {total_insights} data insights to help optimize your cash flow over the past month."
            else:
                return "Your cash flow management has been solid! Oodaloo would help you monitor and maintain this strong runway position."
    
    # NOTE: Hygiene summary generation moved to DataQualityAnalyzer.generate_summary_for_context()
    # This service now uses the core service method with context="test_drive"
