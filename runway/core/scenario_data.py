"""
Shared Business Scenario Data

This module provides realistic business scenario data that can be used for:
1. Integration testing with real QBO APIs
2. Test drive demo experiences
3. Unit testing with mocked data
4. Documentation and examples

The scenarios represent typical Oodaloo target customers across different industries.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class BusinessScenario:
    """Standardized business scenario data structure."""
    name: str
    description: str
    business_profile: Dict[str, Any]
    bank_accounts: List[Dict[str, Any]]
    recurring_bills: List[Dict[str, Any]]
    outstanding_invoices: List[Dict[str, Any]]
    vendor_data_issues: List[Dict[str, Any]]
    seasonal_patterns: Dict[str, float]
    cash_flow_challenges: Dict[str, Any]
    test_objectives: List[str]
    success_criteria: Dict[str, Any]


class BusinessScenarioProvider:
    """Provides standardized business scenarios for testing and demos."""
    
    @staticmethod
    def get_marketing_agency_scenario() -> BusinessScenario:
        """
        Digital Marketing Agency - Typical Oodaloo target customer
        - $50K/month revenue, seasonal fluctuations
        - High software costs (20+ SaaS subscriptions)
        - Irregular client payments
        - Mix of retainer and project-based billing
        """
        return BusinessScenario(
            name="marketing_agency",
            description="Digital Marketing Agency - High AR, moderate AP, seasonal cash flow",
            business_profile={
                "name": "Pixel Perfect Marketing",
                "industry": "Digital Marketing",
                "employee_count": 8,
                "monthly_revenue": 50000,
                "runway_target_months": 6
            },
            bank_accounts=[
                {
                    "name": "Operating Account",
                    "account_type": "Checking",
                    "current_balance": 75000.00,
                    "qbo_id": "QBO_BANK_001"
                },
                {
                    "name": "Payroll Account", 
                    "account_type": "Checking",
                    "current_balance": 25000.00,
                    "qbo_id": "QBO_BANK_002"
                },
                {
                    "name": "Tax Savings",
                    "account_type": "Savings", 
                    "current_balance": 15000.00,
                    "qbo_id": "QBO_BANK_003"
                }
            ],
            recurring_bills=[
                # Software subscriptions (high SaaS costs)
                {"vendor": "HubSpot", "amount": 1200, "frequency": "monthly", "due_day": 1, "category": "Software"},
                {"vendor": "Adobe Creative Cloud", "amount": 600, "frequency": "monthly", "due_day": 15, "category": "Software"},
                {"vendor": "Google Workspace", "amount": 144, "frequency": "monthly", "due_day": 5, "category": "Software"},
                {"vendor": "Slack", "amount": 80, "frequency": "monthly", "due_day": 10, "category": "Software"},
                {"vendor": "Zoom", "amount": 50, "frequency": "monthly", "due_day": 20, "category": "Software"},
                
                # Office & Operations
                {"vendor": "WeWork", "amount": 3500, "frequency": "monthly", "due_day": 1, "category": "Rent"},
                {"vendor": "Verizon Business", "amount": 280, "frequency": "monthly", "due_day": 25, "category": "Utilities"},
                {"vendor": "PG&E", "amount": 150, "frequency": "monthly", "due_day": 15, "category": "Utilities"},
                
                # Payroll (biggest expense)
                {"vendor": "ADP Payroll", "amount": 22000, "frequency": "bi-weekly", "due_day": [1, 15], "category": "Payroll"},
                
                # Marketing & Growth
                {"vendor": "Google Ads", "amount": 5000, "frequency": "monthly", "due_day": 1, "category": "Marketing", "variable": True},
                {"vendor": "Facebook Ads", "amount": 3000, "frequency": "monthly", "due_day": 1, "category": "Marketing", "variable": True}
            ],
            outstanding_invoices=[
                # Mix of retainer and project invoices with different payment terms
                {"client": "TechStart Inc", "amount": 8000, "invoice_date": "2025-08-15", "terms": "NET 30", "type": "retainer"},
                {"client": "Local Restaurant Group", "amount": 12000, "invoice_date": "2025-08-20", "terms": "NET 15", "type": "project"},
                {"client": "E-commerce Startup", "amount": 6000, "invoice_date": "2025-08-25", "terms": "NET 30", "type": "retainer"},
                {"client": "Healthcare Practice", "amount": 15000, "invoice_date": "2025-08-10", "terms": "NET 30", "type": "project", "overdue_days": 5},
                {"client": "SaaS Company", "amount": 4500, "invoice_date": "2025-08-28", "terms": "NET 15", "type": "retainer"}
            ],
            vendor_data_issues=[
                # Common QBO data quality problems
                {"issue": "duplicate_vendors", "vendors": ["Google Inc", "Google LLC", "Google Ads"]},
                {"issue": "inconsistent_naming", "vendors": ["Adobe Systems Inc", "Adobe Inc", "Adobe Creative"]},
                {"issue": "missing_categories", "count": 8},
                {"issue": "uncategorized_transactions", "count": 23}
            ],
            seasonal_patterns={
                "q4_revenue_boost": 1.4,  # 40% higher in Q4
                "q1_revenue_dip": 0.7,    # 30% lower in Q1  
                "summer_slowdown": 0.85   # 15% lower in summer
            },
            cash_flow_challenges={
                "client_payment_delays": 15,  # Average 15 days late
                "seasonal_revenue_swings": 0.4,  # 40% seasonal variation
                "saas_cost_creep": 0.1  # 10% monthly SaaS cost increases
            },
            test_objectives=[
                "Verify high-volume invoice processing",
                "Test seasonal cash flow patterns", 
                "Validate AR aging calculations",
                "Check payment timing optimization",
                "Test vendor normalization with real QBO data quality issues"
            ],
            success_criteria={
                "expected_runway_days": 120,
                "min_data_quality_score": 85,
                "min_health_score": 90,
                "min_accuracy": 92
            }
        )
    
    @staticmethod
    def get_construction_contractor_scenario() -> BusinessScenario:
        """
        Construction Contractor - Cash flow intensive business
        - Project-based revenue with long payment cycles
        - Material costs paid upfront
        - Equipment financing
        - Seasonal workforce fluctuations
        """
        return BusinessScenario(
            name="construction_contractor",
            description="Construction Contractor - Large projects, equipment purchases, progress billing",
            business_profile={
                "name": "Elite Construction Services",
                "industry": "Construction",
                "employee_count": 15,
                "monthly_revenue": 120000,  # Higher revenue but lower margins
                "runway_target_months": 4   # Shorter runway due to cash intensity
            },
            bank_accounts=[
                {
                    "name": "Operating Account",
                    "account_type": "Checking", 
                    "current_balance": 45000.00,  # Lower cash despite higher revenue
                    "qbo_id": "QBO_BANK_001"
                },
                {
                    "name": "Equipment Account",
                    "account_type": "Checking",
                    "current_balance": 25000.00,
                    "qbo_id": "QBO_BANK_002"  
                }
            ],
            recurring_bills=[
                # Equipment financing (major cash drain)
                {"vendor": "CAT Financial", "amount": 4500, "frequency": "monthly", "due_day": 5, "category": "Equipment"},
                {"vendor": "John Deere Credit", "amount": 2800, "frequency": "monthly", "due_day": 10, "category": "Equipment"},
                
                # Materials (variable, project-dependent)
                {"vendor": "Home Depot Pro", "amount": 8000, "frequency": "monthly", "due_day": 15, "category": "Materials", "variable": True},
                {"vendor": "Lowe's Pro", "amount": 5000, "frequency": "monthly", "due_day": 20, "category": "Materials", "variable": True},
                
                # Payroll (seasonal workforce)
                {"vendor": "ADP Payroll", "amount": 45000, "frequency": "bi-weekly", "due_day": [1, 15], "category": "Payroll", "seasonal": True},
                
                # Insurance (high for construction)
                {"vendor": "State Farm Business", "amount": 2200, "frequency": "monthly", "due_day": 1, "category": "Insurance"},
                
                # Fuel & Transportation
                {"vendor": "Shell Fleet", "amount": 3500, "frequency": "monthly", "due_day": 25, "category": "Fuel"}
            ],
            outstanding_invoices=[
                # Large project invoices with slow payment cycles
                {"client": "City of San Francisco", "amount": 85000, "invoice_date": "2025-07-15", "terms": "NET 60", "type": "municipal", "overdue_days": 15},
                {"client": "Westfield Properties", "amount": 45000, "invoice_date": "2025-08-01", "terms": "NET 45", "type": "commercial"},
                {"client": "Johnson Residential", "amount": 28000, "invoice_date": "2025-08-10", "terms": "NET 30", "type": "residential"},
                {"client": "Metro Shopping Center", "amount": 120000, "invoice_date": "2025-08-20", "terms": "NET 45", "type": "commercial"}
            ],
            vendor_data_issues=[
                {"issue": "duplicate_vendors", "vendors": ["Home Depot", "Home Depot Pro", "HD Pro"]},
                {"issue": "inconsistent_naming", "vendors": ["Lowe's Companies Inc", "Lowe's Pro", "Lowe's"]},
                {"issue": "missing_categories", "count": 12},
                {"issue": "uncategorized_transactions", "count": 35}
            ],
            seasonal_patterns={
                "winter_slowdown": 0.6,  # 40% reduction in winter
                "spring_peak": 1.3,      # 30% increase in spring
                "summer_steady": 1.1     # 10% increase in summer
            },
            cash_flow_challenges={
                "material_upfront_costs": 0.6,  # 60% of project costs paid upfront
                "payment_delay_average": 45,    # Average 45 days to get paid
                "seasonal_workforce_factor": 0.3  # 30% workforce reduction in winter
            },
            test_objectives=[
                "Test large transaction amounts",
                "Verify progress billing handling",
                "Check equipment purchase categorization",
                "Validate project-based cash flow",
                "Test tray priority scoring with construction cash flow challenges"
            ],
            success_criteria={
                "expected_runway_days": 90,
                "min_data_quality_score": 80,
                "min_health_score": 85,
                "min_accuracy": 88
            }
        )
    
    @staticmethod
    def get_professional_services_scenario() -> BusinessScenario:
        """
        Professional Services Firm (Law, Consulting, Accounting)
        - Retainer-based revenue
        - High-value individual transactions
        - Professional liability costs
        - Knowledge worker payroll
        """
        return BusinessScenario(
            name="professional_services",
            description="Professional Services - Recurring revenue, low inventory, predictable expenses",
            business_profile={
                "name": "Strategic Business Advisors",
                "industry": "Business Consulting", 
                "employee_count": 12,
                "monthly_revenue": 80000,
                "runway_target_months": 8  # Higher runway target for stability
            },
            bank_accounts=[
                {
                    "name": "Operating Account",
                    "account_type": "Checking",
                    "current_balance": 120000.00,  # Higher cash reserves
                    "qbo_id": "QBO_BANK_001"
                },
                {
                    "name": "Client Trust Account", 
                    "account_type": "Checking",
                    "current_balance": 85000.00,   # Client retainers held in trust
                    "qbo_id": "QBO_BANK_002"
                }
            ],
            recurring_bills=[
                # Professional services overhead
                {"vendor": "Downtown Office Tower", "amount": 8500, "frequency": "monthly", "due_day": 1, "category": "Rent"},
                {"vendor": "Professional Liability Ins", "amount": 1800, "frequency": "monthly", "due_day": 5, "category": "Insurance"},
                {"vendor": "Westlaw", "amount": 450, "frequency": "monthly", "due_day": 10, "category": "Software"},
                {"vendor": "Microsoft 365", "amount": 180, "frequency": "monthly", "due_day": 15, "category": "Software"},
                
                # High-value knowledge worker payroll
                {"vendor": "ADP Payroll", "amount": 35000, "frequency": "bi-weekly", "due_day": [1, 15], "category": "Payroll"},
                
                # Marketing & Business Development
                {"vendor": "LinkedIn Sales Navigator", "amount": 200, "frequency": "monthly", "due_day": 20, "category": "Marketing"}
            ],
            outstanding_invoices=[
                # High-value retainer and project invoices
                {"client": "Fortune 500 Corp", "amount": 25000, "invoice_date": "2025-08-01", "terms": "NET 30", "type": "retainer"},
                {"client": "Private Equity Fund", "amount": 45000, "invoice_date": "2025-08-05", "terms": "NET 15", "type": "project"},
                {"client": "Tech Startup Series B", "amount": 18000, "invoice_date": "2025-08-15", "terms": "NET 30", "type": "project"},
                {"client": "Manufacturing Company", "amount": 12000, "invoice_date": "2025-08-20", "terms": "NET 30", "type": "retainer"}
            ],
            vendor_data_issues=[
                {"issue": "duplicate_vendors", "vendors": ["Microsoft Corporation", "Microsoft Inc", "Microsoft 365"]},
                {"issue": "inconsistent_naming", "vendors": ["Thomson Reuters", "Westlaw", "TR Legal"]},
                {"issue": "missing_categories", "count": 3},
                {"issue": "uncategorized_transactions", "count": 8}
            ],
            seasonal_patterns={
                "q4_client_retention": 1.2,  # 20% higher in Q4
                "q1_new_business": 0.8,      # 20% lower in Q1
                "summer_vacation_dip": 0.9   # 10% lower in summer
            },
            cash_flow_challenges={
                "retainer_management": 0.3,  # 30% of revenue in retainers
                "project_payment_cycles": 30,  # Average 30 days to payment
                "client_trust_compliance": True  # Must maintain trust account compliance
            },
            test_objectives=[
                "Test recurring revenue patterns",
                "Verify retainer handling",
                "Check time-based billing",
                "Validate trust account management",
                "Test high-value transaction processing"
            ],
            success_criteria={
                "expected_runway_days": 180,
                "min_data_quality_score": 90,
                "min_health_score": 95,
                "min_accuracy": 95
            }
        )
    
    @staticmethod
    def get_ecommerce_business_scenario() -> BusinessScenario:
        """
        E-commerce Business - High transaction volume
        - High transaction volume
        - Inventory management
        - Payment processor integration
        - Seasonal patterns
        """
        return BusinessScenario(
            name="ecommerce_business",
            description="E-commerce Business - High transaction volume, inventory management",
            business_profile={
                "name": "Online Retail Store",
                "industry": "E-commerce",
                "employee_count": 12,
                "monthly_revenue": 180000,
                "runway_target_months": 5
            },
            bank_accounts=[
                {
                    "name": "Operating Account",
                    "account_type": "Checking",
                    "current_balance": 95000.00,
                    "qbo_id": "QBO_BANK_001"
                },
                {
                    "name": "Inventory Account",
                    "account_type": "Checking",
                    "current_balance": 35000.00,
                    "qbo_id": "QBO_BANK_002"
                }
            ],
            recurring_bills=[
                # E-commerce platform costs
                {"vendor": "Shopify Plus", "amount": 2000, "frequency": "monthly", "due_day": 1, "category": "Platform"},
                {"vendor": "Stripe", "amount": 5400, "frequency": "monthly", "due_day": 1, "category": "Payment Processing", "variable": True},
                
                # Inventory & Fulfillment
                {"vendor": "Amazon FBA", "amount": 12000, "frequency": "monthly", "due_day": 15, "category": "Fulfillment", "variable": True},
                {"vendor": "UPS Shipping", "amount": 3500, "frequency": "monthly", "due_day": 20, "category": "Shipping", "variable": True},
                
                # Marketing & Growth
                {"vendor": "Google Ads", "amount": 8000, "frequency": "monthly", "due_day": 1, "category": "Marketing", "variable": True},
                {"vendor": "Facebook Ads", "amount": 5000, "frequency": "monthly", "due_day": 1, "category": "Marketing", "variable": True},
                
                # Operations
                {"vendor": "ADP Payroll", "amount": 28000, "frequency": "bi-weekly", "due_day": [1, 15], "category": "Payroll"}
            ],
            outstanding_invoices=[
                # B2B wholesale invoices
                {"client": "Wholesale Distributor A", "amount": 25000, "invoice_date": "2025-08-01", "terms": "NET 30", "type": "wholesale"},
                {"client": "Wholesale Distributor B", "amount": 18000, "invoice_date": "2025-08-10", "terms": "NET 15", "type": "wholesale"},
                {"client": "Corporate Account", "amount": 12000, "invoice_date": "2025-08-15", "terms": "NET 30", "type": "corporate"}
            ],
            vendor_data_issues=[
                {"issue": "duplicate_vendors", "vendors": ["Google Inc", "Google LLC", "Google Ads"]},
                {"issue": "inconsistent_naming", "vendors": ["Facebook Inc", "Meta Platforms", "Facebook Ads"]},
                {"issue": "missing_categories", "count": 15},
                {"issue": "uncategorized_transactions", "count": 45}
            ],
            seasonal_patterns={
                "q4_holiday_peak": 2.5,  # 150% higher in Q4
                "q1_post_holiday": 0.6,  # 40% lower in Q1
                "summer_slowdown": 0.8   # 20% lower in summer
            },
            cash_flow_challenges={
                "inventory_cash_tied_up": 0.4,  # 40% of cash tied up in inventory
                "payment_processor_delays": 2,   # 2-day delay for payment processing
                "seasonal_inventory_swings": 0.6  # 60% inventory variation seasonally
            },
            test_objectives=[
                "Test high-volume transaction processing",
                "Verify inventory-related expenses",
                "Check payment processor integration",
                "Validate seasonal patterns",
                "Test variable cost handling"
            ],
            success_criteria={
                "expected_runway_days": 100,
                "min_data_quality_score": 75,
                "min_health_score": 80,
                "min_accuracy": 85
            }
        )
    
    @staticmethod
    def get_consulting_firm_scenario() -> BusinessScenario:
        """
        Consulting Firm - Project-based billing
        - Project-based billing
        - Travel expenses
        - Contractor payments
        - Milestone billing
        """
        return BusinessScenario(
            name="consulting_firm",
            description="Consulting Firm - Project-based billing, travel expenses, contractor payments",
            business_profile={
                "name": "Strategic Consulting Group", 
                "industry": "Consulting",
                "employee_count": 8,
                "monthly_revenue": 120000,
                "runway_target_months": 10
            },
            bank_accounts=[
                {
                    "name": "Operating Account",
                    "account_type": "Checking",
                    "current_balance": 150000.00,
                    "qbo_id": "QBO_BANK_001"
                }
            ],
            recurring_bills=[
                # Consulting overhead
                {"vendor": "WeWork", "amount": 2400, "frequency": "monthly", "due_day": 1, "category": "Rent"},
                {"vendor": "ADP Payroll", "amount": 45000, "frequency": "bi-weekly", "due_day": [1, 15], "category": "Payroll"},
                
                # Travel & Client Work
                {"vendor": "American Express Business", "amount": 8000, "frequency": "monthly", "due_day": 15, "category": "Travel", "variable": True},
                {"vendor": "Uber Business", "amount": 1200, "frequency": "monthly", "due_day": 20, "category": "Travel", "variable": True},
                
                # Software & Tools
                {"vendor": "Microsoft 365", "amount": 120, "frequency": "monthly", "due_day": 10, "category": "Software"},
                {"vendor": "Slack", "amount": 80, "frequency": "monthly", "due_day": 5, "category": "Software"}
            ],
            outstanding_invoices=[
                # High-value project invoices
                {"client": "Fortune 500 Client", "amount": 75000, "invoice_date": "2025-08-01", "terms": "NET 30", "type": "project"},
                {"client": "Private Equity Fund", "amount": 45000, "invoice_date": "2025-08-10", "terms": "NET 15", "type": "project"},
                {"client": "Tech Startup", "amount": 25000, "invoice_date": "2025-08-20", "terms": "NET 30", "type": "project"}
            ],
            vendor_data_issues=[
                {"issue": "duplicate_vendors", "vendors": ["American Express", "Amex", "American Express Business"]},
                {"issue": "inconsistent_naming", "vendors": ["Uber Technologies", "Uber", "Uber Business"]},
                {"issue": "missing_categories", "count": 5},
                {"issue": "uncategorized_transactions", "count": 12}
            ],
            seasonal_patterns={
                "q4_client_planning": 1.3,  # 30% higher in Q4
                "q1_execution": 1.1,        # 10% higher in Q1
                "summer_slowdown": 0.7      # 30% lower in summer
            },
            cash_flow_challenges={
                "project_payment_cycles": 30,  # Average 30 days to payment
                "travel_expense_reimbursement": 15,  # 15 days for travel reimbursement
                "contractor_payment_timing": 7  # 7 days for contractor payments
            },
            test_objectives=[
                "Test project-based revenue",
                "Verify contractor payments",
                "Check travel expense handling",
                "Validate milestone billing",
                "Test variable expense management"
            ],
            success_criteria={
                "expected_runway_days": 200,
                "min_data_quality_score": 88,
                "min_health_score": 92,
                "min_accuracy": 93
            }
        )
    
    @staticmethod
    def get_all_scenarios() -> List[BusinessScenario]:
        """Get all available business scenarios."""
        return [
            BusinessScenarioProvider.get_marketing_agency_scenario(),
            BusinessScenarioProvider.get_construction_contractor_scenario(),
            BusinessScenarioProvider.get_professional_services_scenario(),
            BusinessScenarioProvider.get_ecommerce_business_scenario(),
            BusinessScenarioProvider.get_consulting_firm_scenario()
        ]
    
    @staticmethod
    def get_scenario_by_name(name: str) -> BusinessScenario:
        """Get a specific scenario by name."""
        scenarios = {s.name: s for s in BusinessScenarioProvider.get_all_scenarios()}
        if name not in scenarios:
            raise ValueError(f"Unknown scenario: {name}. Available: {list(scenarios.keys())}")
        return scenarios[name]
