"""
ServicePro Test Fixtures - Realistic Contractor Business Scenarios

These scenarios focus on the messy reality of how contractors actually work:
- Jobs that span multiple months
- Customers who pay multiple invoices in one lump sum
- Shared expenses across multiple jobs
- Period mismatches (work done in March, paid in April)
- Equipment rentals shared across jobs
- Crew members working multiple jobs per day

This is the complexity that makes accountants fall back to Excel.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import json


def generate_bobs_landscaping_scenario() -> Dict[str, Any]:
    """
    Bob's Landscaping - Simple contractor, clean books
    - 5 residential jobs
    - Each job invoiced separately
    - Customers pay promptly
    - Minimal shared expenses
    """
    company = {
        "name": "Bob's Landscaping",
        "complexity": "simple",
        "description": "Small residential landscaper, clean books"
    }
    
    jobs = [
        {
            "id": "JOB_001",
            "name": "Smith Backyard Renovation",
            "customer": "John Smith",
            "start_date": "2025-01-15",
            "end_date": "2025-01-18",
            "estimated_revenue": 2500.00,
            "status": "completed"
        },
        {
            "id": "JOB_002", 
            "name": "Johnson Lawn Installation",
            "customer": "Mary Johnson",
            "start_date": "2025-01-20",
            "end_date": "2025-01-22",
            "estimated_revenue": 1800.00,
            "status": "completed"
        },
        {
            "id": "JOB_003",
            "name": "Davis Tree Trimming", 
            "customer": "Bob Davis",
            "start_date": "2025-01-25",
            "end_date": "2025-01-25",
            "estimated_revenue": 800.00,
            "status": "completed"
        }
    ]
    
    jobber_invoices = [
        {
            "id": "INV_001",
            "job_id": "JOB_001",
            "amount": 2500.00,
            "issue_date": "2025-01-18",
            "paid_date": "2025-01-25",
            "status": "paid"
        },
        {
            "id": "INV_002",
            "job_id": "JOB_002", 
            "amount": 1800.00,
            "issue_date": "2025-01-22",
            "paid_date": "2025-01-28",
            "status": "paid"
        },
        {
            "id": "INV_003",
            "job_id": "JOB_003",
            "amount": 800.00,
            "issue_date": "2025-01-25",
            "paid_date": "2025-02-01",
            "status": "paid"
        }
    ]
    
    stripe_payments = [
        {
            "id": "py_001",
            "amount": 250000,  # $2500 in cents
            "created": "2025-01-25T14:30:00Z",
            "fee": 7525,  # 2.9% + 30¢
            "net": 242475,
            "metadata": {"invoice_id": "INV_001"}
        },
        {
            "id": "py_002", 
            "amount": 180000,  # $1800 in cents
            "created": "2025-01-28T16:45:00Z",
            "fee": 5520,
            "net": 174480,
            "metadata": {"invoice_id": "INV_002"}
        },
        {
            "id": "py_003",
            "amount": 80000,   # $800 in cents
            "created": "2025-02-01T10:15:00Z", 
            "fee": 2350,
            "net": 77650,
            "metadata": {"invoice_id": "INV_003"}
        }
    ]
    
    qbo_transactions = [
        {
            "id": "QBO_001",
            "date": "2025-01-16",
            "vendor": "Home Depot",
            "amount": -450.00,
            "account": "Uncategorized Expense",
            "memo": "Mulch and plants for Smith job",
            "job_id": "JOB_001"
        },
        {
            "id": "QBO_002",
            "date": "2025-01-21",
            "vendor": "Seed & Sod Co",
            "amount": -320.00, 
            "account": "Uncategorized Expense",
            "memo": "Sod for Johnson lawn",
            "job_id": "JOB_002"
        }
    ]
    
    return {
        "company": company,
        "jobs": jobs,
        "jobber_invoices": jobber_invoices,
        "stripe_payments": stripe_payments,
        "qbo_transactions": qbo_transactions,
        "reconciliation_challenges": {
            "period_mismatches": [],
            "bundled_deposits": [],
            "shared_expense_allocation": [],
            "revenue_recognition_complexity": []
        }
    }


def generate_elite_hvac_scenario() -> Dict[str, Any]:
    """
    Elite HVAC Services - Medium complexity
    - Mix of residential and commercial jobs
    - Some customers pay multiple invoices together
    - Equipment rentals shared across jobs
    - Minor period mismatches
    """
    company = {
        "name": "Elite HVAC Services",
        "complexity": "medium",
        "description": "Growing HVAC contractor with some bundled payments"
    }
    
    jobs = [
        {
            "id": "JOB_H001",
            "name": "Office Building HVAC Upgrade",
            "customer": "Downtown Properties LLC",
            "start_date": "2025-01-10",
            "end_date": "2025-02-15",
            "estimated_revenue": 15000.00,
            "status": "in_progress"
        },
        {
            "id": "JOB_H002",
            "name": "Restaurant Kitchen Ventilation", 
            "customer": "Tony's Pizza",
            "start_date": "2025-01-20",
            "end_date": "2025-01-25",
            "estimated_revenue": 8500.00,
            "status": "completed"
        },
        {
            "id": "JOB_H003",
            "name": "Residential AC Repair",
            "customer": "Downtown Properties LLC",  # Same customer as JOB_H001
            "start_date": "2025-01-28",
            "end_date": "2025-01-29",
            "estimated_revenue": 2200.00,
            "status": "completed"
        }
    ]
    
    invoices = [
        {
            "id": "INV_H001",
            "job_id": "JOB_H001",
            "amount": 7500.00,  # Progress billing 1
            "issue_date": "2025-01-31",
            "paid_date": "2025-02-05",
            "status": "paid"
        },
        {
            "id": "INV_H002",
            "job_id": "JOB_H001", # Changed from JOB_H002 to create progress billing
            "amount": 8500.00,   # Progress billing 2
            "issue_date": "2025-01-25", 
            "paid_date": "2025-02-05",  # Same payment date as INV_H001
            "status": "paid"
        },
        {
            "id": "INV_H003",
            "job_id": "JOB_H003",
            "amount": 2200.00,
            "issue_date": "2025-01-29",
            "paid_date": "2025-02-05",  # Same customer, same payment
            "status": "paid"
        }
    ]
    
    # Customer pays multiple invoices in one lump sum - classic bundled payment
    stripe_payments = [
        {
            "id": "py_hvac_001",
            "amount": 1820000,  # $18,200 total for all three invoices
            "created": "2025-02-05T11:30:00Z",
            "fee": 52810,  # 2.9% + 30¢ 
            "net": 1767190,
            "metadata": {
                "invoice_ids": ["INV_H001", "INV_H002", "INV_H003"],
                "customer": "Downtown Properties LLC"
            }
        }
    ]
    
    qbo_transactions = [
        {
            "id": "QBO_H001",
            "date": "2025-01-15",
            "vendor": "HVAC Supply Co",
            "amount": -3200.00,
            "account": "Uncategorized Expense", 
            "memo": "Ductwork for office building",
            "job_id": "JOB_H001"
        },
        {
            "id": "QBO_H002",
            "date": "2025-01-22",
            "vendor": "United Rentals",
            "amount": -450.00,
            "account": "Uncategorized Expense",
            "memo": "Lift rental - multiple jobs",  # Shared expense!
            "job_id": "SHARED"  # This needs to be allocated
        },
        {
            "id": "QBO_H003",
            "date": "2025-01-23",
            "vendor": "Restaurant Equipment Co",
            "amount": -2100.00,
            "account": "Uncategorized Expense",
            "memo": "Ventilation hood for Tony's",
            "job_id": "JOB_H002"
        }
    ]
    
    return {
        "company": company,
        "jobs": jobs,
        "jobber_invoices": invoices,
        "stripe_payments": stripe_payments,
        "qbo_transactions": qbo_transactions,
        "reconciliation_challenges": {
            "period_mismatches": [
                {"description": "Work done in January, invoiced in February", "jobs": ["JOB_H001"]}
            ],
            "bundled_deposits": [
                {"description": "Customer paid 3 invoices in one $18,200 payment", "payment_id": "py_hvac_001"}
            ],
            "shared_expense_allocation": [
                {"description": "Lift rental used across multiple jobs", "transaction_id": "QBO_H002"}
            ],
            "revenue_recognition_complexity": [
                {"description": "Multi-month project with partial billing", "job_id": "JOB_H001"}
            ]
        }
    }


def generate_mega_construction_scenario() -> Dict[str, Any]:
    """
    Mega Construction LLC - Nightmare complexity
    - Multiple long-term projects spanning months
    - Customers bundle payments across multiple jobs
    - Shared equipment, materials, and crew costs
    - Major period mismatches
    - Progress billing vs. final payments
    
    This is the scenario that makes accountants say "I've seen this before"
    """
    company = {
        "name": "Mega Construction LLC", 
        "complexity": "nightmare",
        "description": "Large contractor with complex multi-month projects and bundled everything"
    }
    
    jobs = [
        {
            "id": "JOB_M001",
            "name": "Shopping Center Renovation",
            "customer": "Retail Properties Inc",
            "start_date": "2025-01-05", 
            "end_date": "2025-04-30",
            "estimated_revenue": 85000.00,
            "status": "in_progress"
        },
        {
            "id": "JOB_M002",
            "name": "Office Complex Parking Lot",
            "customer": "Retail Properties Inc",  # Same customer
            "start_date": "2025-02-01",
            "end_date": "2025-03-15", 
            "estimated_revenue": 45000.00,
            "status": "in_progress"
        },
        {
            "id": "JOB_M003",
            "name": "Warehouse Foundation Repair",
            "customer": "Industrial Holdings Co",
            "start_date": "2025-01-15",
            "end_date": "2025-02-28",
            "estimated_revenue": 32000.00,
            "status": "in_progress"
        },
        {
            "id": "JOB_M004",
            "name": "Restaurant Build-out",
            "customer": "Food Service Group",
            "start_date": "2025-01-20",
            "end_date": "2025-03-10",
            "estimated_revenue": 28000.00,
            "status": "in_progress"
        }
    ]
    
    # Progress billing - multiple invoices per job
    invoices = [
        # Shopping Center - Progress payments
        {
            "id": "INV_M001_1",
            "job_id": "JOB_M001", 
            "amount": 25000.00,  # 30% down payment
            "issue_date": "2025-01-10",
            "paid_date": "2025-02-15",
            "status": "paid"
        },
        {
            "id": "INV_M001_2",
            "job_id": "JOB_M001",
            "amount": 30000.00,  # Progress payment
            "issue_date": "2025-02-01", 
            "paid_date": "2025-02-15",  # Paid same day as down payment
            "status": "paid"
        },
        
        # Parking Lot - Single invoice
        {
            "id": "INV_M002_1", 
            "job_id": "JOB_M002",
            "amount": 20000.00,  # Partial payment
            "issue_date": "2025-02-10",
            "paid_date": "2025-02-15",  # Same customer, same payment date
            "status": "paid"
        },
        
        # Warehouse - Progress payments
        {
            "id": "INV_M003_1",
            "job_id": "JOB_M003",
            "amount": 15000.00,
            "issue_date": "2025-01-25",
            "paid_date": "2025-02-10",
            "status": "paid"
        },
        
        # Restaurant - Progress payment
        {
            "id": "INV_M004_1",
            "job_id": "JOB_M004",
            "amount": 12000.00,
            "issue_date": "2025-02-01",
            "paid_date": "2025-03-05",
            "status": "paid"
        }
    ]
    
    # Massive bundled payments - customers paying multiple invoices together
    stripe_payments = [
        {
            "id": "py_mega_001",
            "amount": 7500000,  # $75,000 - Retail Properties paying 3 invoices at once
            "created": "2025-02-15T09:00:00Z",
            "fee": 217500,  # 2.9% + 30¢
            "net": 7282500,
            "metadata": {
                "invoice_ids": ["INV_M001_1", "INV_M001_2", "INV_M002_1"],
                "customer": "Retail Properties Inc",
                "note": "Payment for shopping center down payment, progress payment, and parking lot"
            }
        },
        {
            "id": "py_mega_002",
            "amount": 1500000,  # $15,000 - Industrial Holdings
            "created": "2025-02-10T14:30:00Z", 
            "fee": 43530,
            "net": 1456470,
            "metadata": {
                "invoice_ids": ["INV_M003_1"],
                "customer": "Industrial Holdings Co"
            }
        },
        {
            "id": "py_mega_003",
            "amount": 1200000,  # $12,000 - Food Service Group
            "created": "2025-03-05T16:15:00Z",
            "fee": 34830,
            "net": 1165170,
            "metadata": {
                "invoice_ids": ["INV_M004_1"],
                "customer": "Food Service Group"
            }
        }
    ]
    
    # Tons of shared expenses - the accountant's nightmare
    qbo_transactions = [
        # Materials shared across jobs
        {
            "id": "QBO_M001",
            "date": "2025-01-08",
            "vendor": "Concrete Supply Co",
            "amount": -8500.00,
            "account": "Uncategorized Expense",
            "memo": "Concrete delivery - multiple projects",
            "job_id": "SHARED"  # Needs allocation across JOB_M001, JOB_M003
        },
        {
            "id": "QBO_M002", 
            "date": "2025-01-12",
            "vendor": "Equipment Rental Plus",
            "amount": -2400.00,
            "account": "Uncategorized Expense",
            "memo": "Excavator rental - January",
            "job_id": "SHARED"  # Used on JOB_M001, JOB_M003, JOB_M004
        },
        
        # Job-specific expenses
        {
            "id": "QBO_M003",
            "date": "2025-01-15",
            "vendor": "Electrical Contractors Inc",
            "amount": -4200.00,
            "account": "Uncategorized Expense", 
            "memo": "Shopping center electrical work",
            "job_id": "JOB_M001"
        },
        {
            "id": "QBO_M004",
            "date": "2025-01-18",
            "vendor": "Steel & Rebar Co",
            "amount": -3800.00,
            "account": "Uncategorized Expense",
            "memo": "Rebar for warehouse foundation",
            "job_id": "JOB_M003"
        },
        
        # More shared expenses
        {
            "id": "QBO_M005",
            "date": "2025-01-25",
            "vendor": "Fuel Express",
            "amount": -850.00,
            "account": "Uncategorized Expense",
            "memo": "Fuel for all crews - January",
            "job_id": "SHARED"  # Needs allocation by crew hours
        },
        {
            "id": "QBO_M006",
            "date": "2025-02-01",
            "vendor": "Safety Supply Co",
            "amount": -650.00,
            "account": "Uncategorized Expense",
            "memo": "Safety equipment and supplies",
            "job_id": "SHARED"  # Allocation by job count
        },
        
        # Equipment rental spanning multiple months
        {
            "id": "QBO_M007",
            "date": "2025-02-05",
            "vendor": "Equipment Rental Plus", 
            "amount": -2400.00,
            "account": "Uncategorized Expense",
            "memo": "Excavator rental - February",
            "job_id": "SHARED"  # Same equipment, different month
        }
    ]
    
    return {
        "company": company,
        "jobs": jobs,
        "jobber_invoices": invoices,
        "stripe_payments": stripe_payments,
        "qbo_transactions": qbo_transactions,
        "reconciliation_challenges": {
            "period_mismatches": [
                {"description": "Work done in January, invoiced in February, paid in March", "jobs": ["JOB_M001", "JOB_M004"]},
                {"description": "Multi-month projects with progress billing", "jobs": ["JOB_M001", "JOB_M002", "JOB_M003"]}
            ],
            "bundled_deposits": [
                {"description": "Customer paid $75K covering 3 different invoices across 2 jobs", "payment_id": "py_mega_001"},
                {"description": "Progress payments and down payments mixed together", "payment_id": "py_mega_001"}
            ],
            "shared_expense_allocation": [
                {"description": "Concrete delivery shared across shopping center and warehouse", "transaction_id": "QBO_M001"},
                {"description": "Excavator rental used on 3 different jobs", "transaction_id": "QBO_M002"},
                {"description": "Fuel costs need allocation by crew hours across all active jobs", "transaction_id": "QBO_M005"},
                {"description": "Safety equipment allocated by job count", "transaction_id": "QBO_M006"}
            ],
            "revenue_recognition_complexity": [
                {"description": "4-month project with multiple progress payments", "job_id": "JOB_M001"},
                {"description": "Overlapping project timelines with shared resources", "jobs": ["JOB_M001", "JOB_M002", "JOB_M003", "JOB_M004"]}
            ]
        }
    }


def get_all_test_scenarios() -> List[Dict[str, Any]]:
    """Get all test scenarios for comprehensive testing."""
    return [
        generate_bobs_landscaping_scenario(),
        generate_elite_hvac_scenario(), 
        generate_mega_construction_scenario()
    ]


def save_test_scenarios_to_file(filename: str = "servicepro_test_scenarios.json"):
    """Save all test scenarios to a JSON file for use in tests."""
    scenarios = get_all_test_scenarios()
    
    with open(filename, "w") as f:
        json.dump(scenarios, f, indent=2, default=str)
    
    print(f"✅ ServicePro test scenarios saved to {filename}")
    
    # Print summary
    for scenario in scenarios:
        company = scenario["company"]
        challenges = scenario["reconciliation_challenges"]
        
        print(f"\n📊 {company['name']} ({company['complexity']})")
        print(f"   Jobs: {len(scenario['jobs'])}")
        print(f"   Invoices: {len(scenario['jobber_invoices'])}")
        print(f"   Stripe Payments: {len(scenario['stripe_payments'])}")
        print(f"   QBO Transactions: {len(scenario['qbo_transactions'])}")
        print(f"   Period Mismatches: {len(challenges['period_mismatches'])}")
        print(f"   Bundled Deposits: {len(challenges['bundled_deposits'])}")
        print(f"   Shared Expenses: {len(challenges['shared_expense_allocation'])}")


if __name__ == "__main__":
    save_test_scenarios_to_file()
