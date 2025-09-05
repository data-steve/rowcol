"""
Realistic Variance Test Scenarios

These scenarios are designed to test revenue recognition variance analysis
with realistic contractor payment timing situations:

1. Jobs at different completion stages
2. Customers with different payment behaviors  
3. Clear work vs. cash timing mismatches
4. Proper metadata linking for accurate analysis
"""

def generate_realistic_variance_scenario():
    """
    A realistic contractor scenario with proper work/cash timing mismatches.
    
    This creates the kind of variance analysis contractors actually need:
    - Job A: 75% complete, 50% paid (customer behind)
    - Job B: 50% complete, 80% paid (customer ahead)  
    - Job C: 100% complete, 0% paid (collections issue)
    - Job D: 25% complete, 100% paid (large upfront payment)
    """
    
    company = {
        "name": "Precision Contractors LLC",
        "business_type": "General Contractor", 
        "complexity": "Realistic Variance",
        "owner": "Maria Rodriguez",
        "employees": 12,
        "annual_revenue": 3000000.0
    }
    
    jobs = [
        {
            "id": "JOB_A001",
            "name": "Kitchen Remodel - Johnson Residence", 
            "estimated_revenue": 20000.00,
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "completion_percentage": 75,
            "line_items": [
                {"date": "2025-01-05", "description": "Demo work", "amount": 3000.00},
                {"date": "2025-01-12", "description": "Plumbing rough-in", "amount": 4000.00},
                {"date": "2025-01-18", "description": "Electrical work", "amount": 3500.00},
                {"date": "2025-01-25", "description": "Drywall & paint", "amount": 4500.00},
                # Final 25% not yet completed
            ]
        },
        {
            "id": "JOB_B002", 
            "name": "Bathroom Addition - Smith Home",
            "estimated_revenue": 15000.00,
            "start_date": "2025-01-10",
            "end_date": "2025-02-10", 
            "completion_percentage": 50,  # 50% complete
            "line_items": [
                {"date": "2025-01-15", "description": "Foundation work", "amount": 4000.00},
                {"date": "2025-01-22", "description": "Framing", "amount": 3500.00},
                # Remaining 50% spans into February
            ]
        },
        {
            "id": "JOB_C003",
            "name": "Deck Construction - Wilson Property", 
            "estimated_revenue": 8000.00,
            "start_date": "2025-01-05",
            "end_date": "2025-01-20",
            "completion_percentage": 100,  # 100% complete
            "line_items": [
                {"date": "2025-01-08", "description": "Materials & prep", "amount": 2500.00},
                {"date": "2025-01-15", "description": "Deck construction", "amount": 4000.00},
                {"date": "2025-01-20", "description": "Finishing work", "amount": 1500.00}
            ]
        },
        {
            "id": "JOB_D004",
            "name": "Garage Addition - Brown Residence",
            "estimated_revenue": 25000.00, 
            "start_date": "2025-02-01",
            "end_date": "2025-03-15",
            "completion_percentage": 25,  # 25% complete 
            "line_items": [
                {"date": "2025-02-03", "description": "Site prep & permits", "amount": 3000.00},
                {"date": "2025-02-08", "description": "Foundation pour", "amount": 3250.00},
                # Remaining 75% not yet started
            ]
        }
    ]
    
    # Invoices that reflect actual work completed
    jobber_invoices = [
        # Job A: 75% complete ($15,000 work) - but only invoiced $12,000 so far
        {
            "id": "INV_A001_1",
            "job_id": "JOB_A001", 
            "amount": 8000.00,  # First progress payment
            "paid_date": "2025-01-10"
        },
        {
            "id": "INV_A001_2", 
            "job_id": "JOB_A001",
            "amount": 4000.00,  # Second progress payment  
            "paid_date": None  # Not yet paid!
        },
        
        # Job B: 50% complete ($7,500 work) - but invoiced $12,000 (customer paid ahead)
        {
            "id": "INV_B002_1",
            "job_id": "JOB_B002",
            "amount": 12000.00,  # Large upfront payment
            "paid_date": "2025-01-15"
        },
        
        # Job C: 100% complete ($8,000 work) - invoiced but not paid (collections issue)
        {
            "id": "INV_C003_1", 
            "job_id": "JOB_C003",
            "amount": 8000.00,
            "paid_date": None  # Customer hasn't paid!
        },
        
        # Job D: 25% complete ($6,250 work) - but customer paid full amount upfront
        {
            "id": "INV_D004_1",
            "job_id": "JOB_D004", 
            "amount": 25000.00,  # Full payment upfront
            "paid_date": "2025-01-28"
        }
    ]
    
    # Stripe payments that correspond to actual cash received
    stripe_payments = [
        # Job A: Customer paid first invoice only ($8,000 of $12,000 invoiced)
        {
            "id": "py_A001_1",
            "amount": 800000,  # $8,000 in cents
            "created": "2025-01-10T14:30:00Z",
            "fee": 23500,      # 2.9% + $0.30
            "net": 776500,
            "metadata": {"invoice_id": "INV_A001_1", "job_id": "JOB_A001"}
        },
        
        # Job B: Customer paid upfront ($12,000)
        {
            "id": "py_B002_1", 
            "amount": 1200000,  # $12,000 in cents
            "created": "2025-01-15T09:15:00Z",
            "fee": 35100,       # 2.9% + $0.30
            "net": 1164900,
            "metadata": {"invoice_id": "INV_B002_1", "job_id": "JOB_B002"}
        },
        
        # Job C: No payment yet (collections issue)
        # (no stripe payment record)
        
        # Job D: Customer paid full amount upfront ($25,000)
        {
            "id": "py_D004_1",
            "amount": 2500000,  # $25,000 in cents  
            "created": "2025-01-28T11:45:00Z",
            "fee": 72800,       # 2.9% + $0.30
            "net": 2427200,
            "metadata": {"invoice_id": "INV_D004_1", "job_id": "JOB_D004"}
        }
    ]
    
    qbo_transactions = [
        {
            "id": "QBO_A001",
            "date": "2025-01-06", 
            "vendor": "Home Depot",
            "amount": -1200.00,
            "account": "Materials",
            "memo": "Kitchen demo supplies",
            "job_id": "JOB_A001"
        },
        {
            "id": "QBO_B002",
            "date": "2025-01-16",
            "vendor": "Concrete Supply Co", 
            "amount": -800.00,
            "account": "Materials",
            "memo": "Foundation materials", 
            "job_id": "JOB_B002"
        }
    ]
    
    return {
        "company": company,
        "jobs": jobs, 
        "jobber_invoices": jobber_invoices,
        "stripe_payments": stripe_payments,
        "qbo_transactions": qbo_transactions,
        "reconciliation_challenges": {
            "period_mismatches": ["JOB_B002", "JOB_D004"],  # Span multiple periods
            "bundled_deposits": [],
            "shared_expense_allocation": [],
            "revenue_recognition_complexity": ["All jobs have work vs. cash timing issues"],
            "collections_issues": ["JOB_C003"],
            "prepayment_situations": ["JOB_B002", "JOB_D004"],
            "payment_delays": ["JOB_A001"]
        },
        "expected_variances": {
            "JOB_A001": {
                "work_performed": 15000.00,  # 75% of $20k
                "cash_received": 7765.00,    # $8k minus fees  
                "variance": 7235.00,         # Positive = Accrual needed
                "status": "Customer behind on payments"
            },
            "JOB_B002": {
                "work_performed": 7500.00,   # 50% of $15k
                "cash_received": 11649.00,   # $12k minus fees
                "variance": -4149.00,        # Negative = Deferral needed
                "status": "Customer paid ahead"
            },
            "JOB_C003": {
                "work_performed": 8000.00,   # 100% of $8k
                "cash_received": 0.00,       # No payment yet
                "variance": 8000.00,         # Large positive = Collections issue
                "status": "Collections problem"
            },
            "JOB_D004": {
                "work_performed": 6250.00,   # 25% of $25k  
                "cash_received": 24272.00,   # $25k minus fees
                "variance": -18022.00,       # Large negative = Major deferral
                "status": "Large upfront payment"
            }
        }
    }

def generate_simple_balanced_scenario():
    """
    A simple scenario where work and payments are perfectly balanced.
    
    This should result in zero variance - good for testing the "happy path".
    """
    
    company = {
        "name": "Perfect Timing Contractors",
        "business_type": "Service Contractor",
        "complexity": "Simple", 
        "owner": "John Perfect"
    }
    
    jobs = [
        {
            "id": "JOB_P001",
            "name": "Simple Repair Job",
            "estimated_revenue": 5000.00,
            "start_date": "2025-01-10", 
            "end_date": "2025-01-15",
            "completion_percentage": 100,
            "line_items": [
                {"date": "2025-01-12", "description": "Repair work completed", "amount": 5000.00}
            ]
        }
    ]
    
    jobber_invoices = [
        {
            "id": "INV_P001",
            "job_id": "JOB_P001",
            "amount": 5000.00,
            "paid_date": "2025-01-16"
        }
    ]
    
    stripe_payments = [
        {
            "id": "py_P001",
            "amount": 500000,  # $5,000 in cents
            "created": "2025-01-16T10:00:00Z", 
            "fee": 14800,      # 2.9% + $0.30
            "net": 485200,
            "metadata": {"invoice_id": "INV_P001", "job_id": "JOB_P001"}
        }
    ]
    
    return {
        "company": company,
        "jobs": jobs,
        "jobber_invoices": jobber_invoices, 
        "stripe_payments": stripe_payments,
        "qbo_transactions": [],
        "reconciliation_challenges": {
            "period_mismatches": [],
            "bundled_deposits": [],
            "shared_expense_allocation": [], 
            "revenue_recognition_complexity": []
        },
        "expected_variances": {
            "JOB_P001": {
                "work_performed": 5000.00,
                "cash_received": 4852.00,  # After fees
                "variance": 148.00,        # Small positive due to fees
                "status": "Perfect timing (fees only)"
            }
        }
    }

