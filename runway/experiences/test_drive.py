"""
Test Drive Service

Centralized service for test drive functionality that demonstrates Oodaloo's value 
to prospects and new users through historical analysis and data quality insights.

This consolidates all test drive logic from both onboarding and test_drive subdomains.

Features:
- Test Drive: Retroactive 4-week runway analysis
- Hygiene Score: Data quality assessment with runway impact
- Value Demonstration: Shows what Oodaloo would have recommended
- Demo Data: Static demo data for prospects
- Sandbox Data: QBO sandbox integration for realistic demos
"""

from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.models.integration import Integration
from domains.integrations.qbo.client import get_qbo_client
from typing import Dict, Any, Optional
from runway.core.scenario_data import BusinessScenarioProvider, BusinessScenario
from runway.core.runway_calculator import RunwayCalculator
from runway.core.data_quality_analyzer import DataQualityAnalyzer
from config import RunwayAnalysisSettings, DataQualityThresholds, ProofOfValueThresholds
from common.exceptions import BusinessNotFoundError
from typing import List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DemoTestDriveService:
    """Centralized service for test drive demonstrations and historical analysis."""
    
    def __init__(self, db: Session):
        self.db = db
        # Initialize core analytics services
        self._runway_calculators = {}  # Cache calculators per business
        self._data_quality_analyzers = {}  # Cache analyzers per business
    
    async def generate_test_drive(self, business_id: str = None, industry: str = "software_agency", use_sandbox: bool = False) -> Dict[str, Any]:
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
            weeks_data = await runway_calculator.calculate_historical_runway(weeks_back=4, qbo_data=qbo_data)
            
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
                "test_drive_type": "test_drive"
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
                "test_drive_type": "test_drive"
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
            
            # Get QBO data for analysis using QBOAPIClient directly
            qbo_client = get_qbo_client(business_id, self.db)
            qbo_data = {
                "bills": qbo_client.get_bills(),
                "invoices": qbo_client.get_invoices(),
                "vendors": qbo_client.get_vendors(),
                "customers": qbo_client.get_customers(),
                "accounts": qbo_client.get_accounts(),
                "company_info": qbo_client.get_company_info()
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
        return self.generate_test_drive(
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
        # This would use QBOAPIClient for real data
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
    
    def _generate_weekly_analysis(self, business_id: str, week_start: datetime, week_end: datetime, 
                                qbo_data: Dict[str, Any], weeks_ago: int) -> Dict[str, Any]:
        """
        Generate analysis for a specific week period.
        
        This delegates to RunwayCalculator for the core analysis logic and adds 
        test drive presentation formatting.
        
        Args:
            business_id: Business identifier
            week_start: Start of the week
            week_end: End of the week  
            qbo_data: QBO data for analysis
            weeks_ago: How many weeks ago this was (for labeling)
            
        Returns:
            Dict containing week-specific analysis formatted for test drive
        """
        runway_calculator = self._get_runway_calculator(business_id)
        
        # Delegate core calculation to RunwayCalculator
        week_analysis = runway_calculator.calculate_weekly_analysis(
            week_start=week_start,
            week_end=week_end,
            qbo_data=qbo_data
        )
        
        # Add test drive specific formatting and labels
        week_analysis["week_label"] = f"{weeks_ago} weeks ago" if weeks_ago > 1 else ("1 week ago" if weeks_ago == 1 else "This week")
        
        return week_analysis
    
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
"""
Test Drive Demo Data Service

This service provides realistic business scenario data for the test drive experience.
It uses the shared scenario data from runway.core.scenario_data to ensure consistency
between tests, demos, and documentation.

The demo data is designed to showcase Oodaloo's capabilities across different
business types and industries.
"""


class DemoDataService:
    """
    Service for providing demo data for test drive experiences.
    
    This service transforms shared scenario data into formats suitable for
    test drive demonstrations, including QBO-mock data and UI-friendly formats.
    """
    
    def __init__(self):
        self.scenario_provider = BusinessScenarioProvider()
    
    def get_demo_scenarios(self) -> List[Dict[str, Any]]:
        """Get all available demo scenarios for test drive."""
        scenarios = self.scenario_provider.get_all_scenarios()
        return [self._format_for_demo(scenario) for scenario in scenarios]
    
    def get_demo_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Get a specific demo scenario by name."""
        scenario = self.scenario_provider.get_scenario_by_name(scenario_name)
        return self._format_for_demo(scenario)
    
    def get_industry_scenarios(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get scenarios grouped by industry for demo selection."""
        scenarios = self.get_demo_scenarios()
        industry_groups = {}
        
        for scenario in scenarios:
            industry = scenario["business_profile"]["industry"]
            if industry not in industry_groups:
                industry_groups[industry] = []
            industry_groups[industry].append(scenario)
        
        return industry_groups
    
    def generate_qbo_mock_data(self, scenario_name: str) -> Dict[str, Any]:
        """
        Generate QBO-mock data for a specific scenario.
        
        This creates realistic QBO API response data that can be used
        to simulate QBO integration during test drive demos.
        """
        scenario = self.scenario_provider.get_scenario_by_name(scenario_name)
        
        return {
            "company_info": {
                "id": f"QBO_COMPANY_{scenario.name.upper()}",
                "name": scenario.business_profile["name"],
                "industry": scenario.business_profile["industry"]
            },
            "accounts": self._format_qbo_accounts(scenario.bank_accounts),
            "bills": self._format_qbo_bills(scenario.recurring_bills),
            "invoices": self._format_qbo_invoices(scenario.outstanding_invoices),
            "vendors": self._extract_vendors(scenario.recurring_bills),
            "customers": self._extract_customers(scenario.outstanding_invoices),
            "data_quality_issues": scenario.vendor_data_issues,
            "seasonal_patterns": scenario.seasonal_patterns,
            "cash_flow_challenges": scenario.cash_flow_challenges
        }
    
    def _format_for_demo(self, scenario: BusinessScenario) -> Dict[str, Any]:
        """Format scenario data for demo display."""
        return {
            "id": scenario.name,
            "name": scenario.business_profile["name"],
            "description": scenario.description,
            "industry": scenario.business_profile["industry"],
            "employee_count": scenario.business_profile["employee_count"],
            "monthly_revenue": scenario.business_profile["monthly_revenue"],
            "runway_target_months": scenario.business_profile["runway_target_months"],
            "demo_highlights": self._get_demo_highlights(scenario),
            "complexity_score": self._calculate_complexity_score(scenario),
            "test_objectives": scenario.test_objectives,
            "success_criteria": scenario.success_criteria
        }
    
    def _get_demo_highlights(self, scenario: BusinessScenario) -> List[str]:
        """Get key highlights for demo presentation."""
        highlights = []
        
        # Revenue highlights
        revenue = scenario.business_profile["monthly_revenue"]
        if revenue >= 100000:
            highlights.append("High-revenue business with complex cash flow")
        elif revenue >= 50000:
            highlights.append("Mid-market business with growth challenges")
        else:
            highlights.append("Small business with operational efficiency needs")
        
        # Industry-specific highlights
        industry = scenario.business_profile["industry"]
        if industry == "Digital Marketing":
            highlights.append("High SaaS costs and seasonal revenue swings")
        elif industry == "Construction":
            highlights.append("Project-based billing with equipment financing")
        elif industry == "Business Consulting":
            highlights.append("Retainer-based revenue with trust account management")
        elif industry == "E-commerce":
            highlights.append("High transaction volume with inventory management")
        elif industry == "Consulting":
            highlights.append("Project-based billing with travel expenses")
        
        # Cash flow challenges
        if scenario.cash_flow_challenges:
            if "payment_delay_average" in scenario.cash_flow_challenges:
                delay = scenario.cash_flow_challenges["payment_delay_average"]
                highlights.append(f"Average {delay}-day payment delays")
            
            if "seasonal_revenue_swings" in scenario.cash_flow_challenges:
                swings = scenario.cash_flow_challenges["seasonal_revenue_swings"]
                highlights.append(f"{swings*100:.0f}% seasonal revenue variation")
        
        return highlights
    
    def _calculate_complexity_score(self, scenario: BusinessScenario) -> int:
        """Calculate complexity score (1-10) for demo difficulty."""
        score = 5  # Base score
        
        # Revenue complexity
        revenue = scenario.business_profile["monthly_revenue"]
        if revenue >= 200000:
            score += 2
        elif revenue >= 100000:
            score += 1
        
        # Bill/invoice complexity
        bill_count = len(scenario.recurring_bills)
        invoice_count = len(scenario.outstanding_invoices)
        
        if bill_count >= 20 or invoice_count >= 30:
            score += 2
        elif bill_count >= 10 or invoice_count >= 15:
            score += 1
        
        # Data quality issues
        total_issues = sum(issue.get("count", 1) for issue in scenario.vendor_data_issues)
        if total_issues >= 20:
            score += 2
        elif total_issues >= 10:
            score += 1
        
        # Seasonal patterns
        if scenario.seasonal_patterns:
            max_variation = max(scenario.seasonal_patterns.values())
            if max_variation >= 1.5:
                score += 1
        
        return min(10, max(1, score))
    
    def _format_qbo_accounts(self, bank_accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format bank accounts as QBO Account entities."""
        qbo_accounts = []
        for account in bank_accounts:
            qbo_accounts.append({
                "Id": account["qbo_id"],
                "Name": account["name"],
                "AccountType": account["account_type"],
                "CurrentBalance": account["current_balance"],
                "Active": True,
                "MetaData": {
                    "CreateTime": "2025-01-01T00:00:00Z",
                    "LastUpdatedTime": "2025-01-01T00:00:00Z"
                }
            })
        return qbo_accounts
    
    def _format_qbo_bills(self, recurring_bills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format recurring bills as QBO Bill entities."""
        qbo_bills = []
        for i, bill in enumerate(recurring_bills):
            qbo_bills.append({
                "Id": f"QBO_BILL_{i+1:03d}",
                "DocNumber": f"BILL-{i+1:03d}",
                "TxnDate": "2025-08-01",
                "DueDate": f"2025-08-{bill['due_day']:02d}",
                "TotalAmt": bill["amount"],
                "Balance": bill["amount"],
                "PrivateNote": f"Recurring {bill['frequency']} bill",
                "VendorRef": {
                    "value": f"QBO_VENDOR_{i+1:03d}",
                    "name": bill["vendor"]
                },
                "Line": [{
                    "Id": f"QBO_LINE_{i+1:03d}",
                    "Amount": bill["amount"],
                    "DetailType": "ItemBasedExpenseLineDetail",
                    "ItemBasedExpenseLineDetail": {
                        "ItemRef": {
                            "value": f"QBO_ITEM_{i+1:03d}",
                            "name": bill["category"]
                        }
                    }
                }],
                "MetaData": {
                    "CreateTime": "2025-01-01T00:00:00Z",
                    "LastUpdatedTime": "2025-01-01T00:00:00Z"
                }
            })
        return qbo_bills
    
    def _format_qbo_invoices(self, outstanding_invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format outstanding invoices as QBO Invoice entities."""
        qbo_invoices = []
        for i, invoice in enumerate(outstanding_invoices):
            qbo_invoices.append({
                "Id": f"QBO_INVOICE_{i+1:03d}",
                "DocNumber": f"INV-{i+1:03d}",
                "TxnDate": invoice["invoice_date"],
                "DueDate": self._calculate_due_date(invoice["invoice_date"], invoice["terms"]),
                "TotalAmt": invoice["amount"],
                "Balance": invoice["amount"],
                "PrivateNote": f"{invoice['type']} invoice",
                "CustomerRef": {
                    "value": f"QBO_CUSTOMER_{i+1:03d}",
                    "name": invoice["client"]
                },
                "Line": [{
                    "Id": f"QBO_LINE_{i+1:03d}",
                    "Amount": invoice["amount"],
                    "DetailType": "SalesItemLineDetail",
                    "SalesItemLineDetail": {
                        "ItemRef": {
                            "value": f"QBO_ITEM_{i+1:03d}",
                            "name": "Services"
                        }
                    }
                }],
                "MetaData": {
                    "CreateTime": "2025-01-01T00:00:00Z",
                    "LastUpdatedTime": "2025-01-01T00:00:00Z"
                }
            })
        return qbo_invoices
    
    def _extract_vendors(self, recurring_bills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract unique vendors from recurring bills."""
        vendors = []
        seen_vendors = set()
        
        for i, bill in enumerate(recurring_bills):
            vendor_name = bill["vendor"]
            if vendor_name not in seen_vendors:
                vendors.append({
                    "Id": f"QBO_VENDOR_{i+1:03d}",
                    "Name": vendor_name,
                    "Active": True,
                    "Vendor1099": False,
                    "MetaData": {
                        "CreateTime": "2025-01-01T00:00:00Z",
                        "LastUpdatedTime": "2025-01-01T00:00:00Z"
                    }
                })
                seen_vendors.add(vendor_name)
        
        return vendors
    
    def _extract_customers(self, outstanding_invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract unique customers from outstanding invoices."""
        customers = []
        seen_customers = set()
        
        for i, invoice in enumerate(outstanding_invoices):
            customer_name = invoice["client"]
            if customer_name not in seen_customers:
                customers.append({
                    "Id": f"QBO_CUSTOMER_{i+1:03d}",
                    "Name": customer_name,
                    "Active": True,
                    "MetaData": {
                        "CreateTime": "2025-01-01T00:00:00Z",
                        "LastUpdatedTime": "2025-01-01T00:00:00Z"
                    }
                })
                seen_customers.add(customer_name)
        
        return customers
    
    def _calculate_due_date(self, invoice_date: str, terms: str) -> str:
        """Calculate due date based on invoice date and payment terms."""
        from datetime import datetime
        
        # Parse invoice date
        inv_date = datetime.strptime(invoice_date, "%Y-%m-%d")
        
        # Parse terms
        if "NET 15" in terms:
            days = 15
        elif "NET 30" in terms:
            days = 30
        elif "NET 45" in terms:
            days = 45
        elif "NET 60" in terms:
            days = 60
        else:
            days = 30  # Default
        
        due_date = inv_date + timedelta(days=days)
        return due_date.strftime("%Y-%m-%d")
