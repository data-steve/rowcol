#!/usr/bin/env python3
"""
Generate realistic test data for service contractor reconciliation testing.
This creates the complex scenarios that don't "line up cleanly" that real accountants face.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import random

@dataclass
class JobLineItem:
    description: str
    amount: float
    date: str
    team: str
    completion_percentage: float = 100.0

@dataclass
class Job:
    id: str
    title: str
    customer: str
    start_date: str
    end_date: str
    total_value: float
    status: str
    line_items: List[JobLineItem]
    payment_terms: str
    
@dataclass
class Invoice:
    id: str
    job_id: str
    invoice_date: str
    due_date: str
    amount: float
    status: str
    paid_date: str = None
    stripe_payment_id: str = None

@dataclass
class StripePayment:
    charge_id: str
    amount: int  # in cents
    fee: int     # in cents
    net: int     # in cents
    created: str
    payout_date: str
    description: str
    metadata: Dict[str, str]
    status: str = "succeeded"

@dataclass
class QBOTransaction:
    type: str
    date: str
    amount: float
    account: str
    memo: str
    vendor: str = None
    job_class: str = None
    reference: str = None

class RealisticTestDataGenerator:
    """
    Generate realistic service contractor data that creates the reconciliation challenges
    that make accountants fall back to Excel.
    """
    
    def __init__(self):
        self.company_name = "Elite Landscaping Services"
        self.teams = ["Team A", "Team B", "Team C"]
        self.customers = [
            "Westfield Properties LLC",
            "Johnson Residential",
            "Pine Valley HOA",
            "Metro Commercial Group",
            "Sunset Gardens Inc",
            "Heritage Property Management"
        ]
        
        # Stripe fee calculation: 2.9% + $0.30
        self.stripe_rate = 0.029
        self.stripe_fixed_fee = 0.30
        
        # Random seed for reproducible test data
        random.seed(42)
    
    def calculate_stripe_fee(self, amount: float) -> tuple:
        """Calculate Stripe fee and net amount"""
        fee = (amount * self.stripe_rate) + self.stripe_fixed_fee
        net = amount - fee
        return round(fee, 2), round(net, 2)
    
    def generate_complex_jobs(self) -> List[Job]:
        """Generate jobs with realistic complexity that causes reconciliation challenges"""
        
        jobs = []
        
        # Job #1: Multi-period job with delayed payment (spans Feb-Mar, paid in April)
        job1_line_items = [
            JobLineItem("Site Preparation & Excavation", 4500.00, "2024-02-20", "Team A", 100.0),
            JobLineItem("Landscape Installation Phase 1", 3600.00, "2024-03-05", "Team A", 100.0),
            JobLineItem("Landscape Installation Phase 2", 3600.00, "2024-03-08", "Team B", 100.0),
            JobLineItem("Irrigation System Install", 2300.00, "2024-03-15", "Team A", 100.0),
            JobLineItem("Final Cleanup & Touch-ups", 1000.00, "2024-03-20", "Team B", 100.0)
        ]
        
        jobs.append(Job(
            id="JOB_001_MALL_RENO",
            title="Suburban Mall Renovation",
            customer="Westfield Properties LLC",
            start_date="2024-02-15",
            end_date="2024-03-20",
            total_value=15000.00,
            status="completed",
            line_items=job1_line_items,
            payment_terms="50% upfront, 50% on completion"
        ))
        
        # Job #2: Clean single-period job (good for comparison)
        job2_line_items = [
            JobLineItem("Backyard Design & Planning", 800.00, "2024-03-05", "Team B", 100.0),
            JobLineItem("Soil Preparation", 600.00, "2024-03-06", "Team B", 100.0),
            JobLineItem("Plant Installation", 1200.00, "2024-03-10", "Team B", 100.0),
            JobLineItem("Mulching & Final Details", 600.00, "2024-03-12", "Team B", 100.0)
        ]
        
        jobs.append(Job(
            id="JOB_002_BACKYARD",
            title="Residential Backyard Project",
            customer="Johnson Residential",
            start_date="2024-03-05",
            end_date="2024-03-12",
            total_value=3200.00,
            status="completed",
            line_items=job2_line_items,
            payment_terms="Net 30"
        ))
        
        # Job #3: Recurring + emergency work (mixed revenue recognition)
        job3_line_items = [
            JobLineItem("Monthly Maintenance - March", 1200.00, "2024-03-01", "Team C", 100.0),
            JobLineItem("Emergency Storm Cleanup", 800.00, "2024-03-18", "Team C", 100.0)
        ]
        
        jobs.append(Job(
            id="JOB_003_MAINTENANCE",
            title="Commercial Property Maintenance",
            customer="Metro Commercial Group",
            start_date="2024-03-01",
            end_date="2024-03-31",
            total_value=2000.00,
            status="ongoing",
            line_items=job3_line_items,
            payment_terms="Monthly in advance + Net 15 for emergency work"
        ))
        
        # Job #4: Multi-installment payment (percentage of completion nightmare)
        job4_line_items = [
            JobLineItem("Property Assessment & Planning", 1275.00, "2024-03-10", "Team A", 100.0),
            JobLineItem("Landscape Renovation - Property 1", 2125.00, "2024-03-15", "Team B", 100.0),
            JobLineItem("Landscape Renovation - Property 2", 2125.00, "2024-03-18", "Team C", 100.0),
            JobLineItem("Landscape Renovation - Property 3", 2125.00, "2024-03-22", "Team A", 100.0),
            JobLineItem("Final Inspection & Warranty Setup", 850.00, "2024-03-25", "Team B", 100.0)
        ]
        
        jobs.append(Job(
            id="JOB_004_HOA_MULTI",
            title="Multi-Property HOA Contract",
            customer="Pine Valley HOA",
            start_date="2024-03-10",
            end_date="2024-03-25",
            total_value=8500.00,
            status="completed",
            line_items=job4_line_items,
            payment_terms="30% upfront, 70% in 3 equal installments"
        ))
        
        return jobs
    
    def generate_invoices_with_timing_issues(self, jobs: List[Job]) -> List[Invoice]:
        """Generate invoices with realistic timing delays and complications"""
        
        invoices = []
        
        # Job #1: Two invoices with payment timing issues
        invoices.extend([
            Invoice(
                id="INV_001_MALL_50PCT",
                job_id="JOB_001_MALL_RENO",
                invoice_date="2024-02-25",
                due_date="2024-02-25",  # Due immediately (50% upfront)
                amount=7500.00,
                status="paid",
                paid_date="2024-02-28"
            ),
            Invoice(
                id="INV_002_MALL_FINAL",
                job_id="JOB_001_MALL_RENO", 
                invoice_date="2024-03-20",
                due_date="2024-03-20",  # Due on completion
                amount=7500.00,
                status="paid",
                paid_date="2024-04-03"  # LATE PAYMENT - creates period mismatch!
            )
        ])
        
        # Job #2: Single invoice, paid on time
        invoices.append(Invoice(
            id="INV_003_BACKYARD",
            job_id="JOB_002_BACKYARD",
            invoice_date="2024-03-15",
            due_date="2024-04-14",  # Net 30
            amount=3200.00,
            status="paid",
            paid_date="2024-03-28"  # Paid early
        ))
        
        # Job #3: Two invoices - recurring and emergency
        invoices.extend([
            Invoice(
                id="INV_004_MAINTENANCE_MAR",
                job_id="JOB_003_MAINTENANCE",
                invoice_date="2024-02-25",
                due_date="2024-03-01",  # Paid in advance
                amount=1200.00,
                status="paid",
                paid_date="2024-03-01"
            ),
            Invoice(
                id="INV_005_EMERGENCY",
                job_id="JOB_003_MAINTENANCE",
                invoice_date="2024-03-20",
                due_date="2024-04-04",  # Net 15
                amount=800.00,
                status="paid",
                paid_date="2024-04-05"  # Paid 1 day late, crosses month boundary
            )
        ])
        
        # Job #4: Four invoices for installment payments
        invoices.extend([
            Invoice(
                id="INV_006_HOA_UPFRONT",
                job_id="JOB_004_HOA_MULTI",
                invoice_date="2024-03-05",
                due_date="2024-03-05",  # 30% upfront
                amount=2550.00,
                status="paid",
                paid_date="2024-03-08"
            ),
            Invoice(
                id="INV_007_HOA_INST1",
                job_id="JOB_004_HOA_MULTI",
                invoice_date="2024-03-15",
                due_date="2024-03-20",  # First installment
                amount=1983.33,
                status="paid",
                paid_date="2024-03-22"  # Paid 2 days late
            ),
            Invoice(
                id="INV_008_HOA_INST2",
                job_id="JOB_004_HOA_MULTI",
                invoice_date="2024-03-25",
                due_date="2024-04-05",  # Second installment
                amount=1983.33,
                status="paid",
                paid_date="2024-04-07"  # Paid 2 days late, next month
            ),
            Invoice(
                id="INV_009_HOA_INST3",
                job_id="JOB_004_HOA_MULTI",
                invoice_date="2024-04-05",
                due_date="2024-04-20",  # Third installment
                amount=1983.34,  # Slightly higher to account for rounding
                status="pending",
                paid_date=None  # Not paid yet!
            )
        ])
        
        return invoices
    
    def generate_stripe_payments_with_fees(self, invoices: List[Invoice]) -> List[StripePayment]:
        """Generate Stripe payments with realistic fee calculations and timing"""
        
        payments = []
        
        for invoice in invoices:
            if invoice.status == "paid" and invoice.paid_date:
                fee_amount, net_amount = self.calculate_stripe_fee(invoice.amount)
                
                # Convert to cents for Stripe
                amount_cents = int(invoice.amount * 100)
                fee_cents = int(fee_amount * 100)
                net_cents = int(net_amount * 100)
                
                # Calculate payout date (T+2 business days)
                paid_date = datetime.strptime(invoice.paid_date, "%Y-%m-%d")
                payout_date = self.calculate_payout_date(paid_date)
                
                payment = StripePayment(
                    charge_id=f"ch_{uuid.uuid4().hex[:24]}",
                    amount=amount_cents,
                    fee=fee_cents,
                    net=net_cents,
                    created=f"{invoice.paid_date}T{random.randint(9, 17)}:{random.randint(10, 59)}:00Z",
                    payout_date=payout_date.strftime("%Y-%m-%d"),
                    description=f"Payment for {invoice.id}",
                    metadata={
                        "invoice_id": invoice.id,
                        "job_id": invoice.job_id,
                        "customer": "various"  # Would be populated from job data
                    }
                )
                
                payments.append(payment)
        
        return payments
    
    def calculate_payout_date(self, payment_date: datetime) -> datetime:
        """Calculate Stripe payout date (T+2 business days)"""
        payout_date = payment_date
        business_days_added = 0
        
        while business_days_added < 2:
            payout_date += timedelta(days=1)
            # Skip weekends
            if payout_date.weekday() < 5:  # Monday = 0, Friday = 4
                business_days_added += 1
        
        return payout_date
    
    def generate_qbo_transactions_with_complications(self, stripe_payments: List[StripePayment]) -> List[QBOTransaction]:
        """Generate QBO transactions that create reconciliation challenges"""
        
        qbo_transactions = []
        
        # Group payments by payout date for bundled deposits
        payout_groups = {}
        for payment in stripe_payments:
            payout_date = payment.payout_date
            if payout_date not in payout_groups:
                payout_groups[payout_date] = []
            payout_groups[payout_date].append(payment)
        
        # Create bundled bank deposits (this is where it gets messy)
        for payout_date, payments in payout_groups.items():
            total_net = sum(p.net for p in payments) / 100  # Convert back to dollars
            total_fees = sum(p.fee for p in payments) / 100
            
            # Bank deposit (net amount)
            qbo_transactions.append(QBOTransaction(
                type="Deposit",
                date=payout_date,
                amount=total_net,
                account="Business Checking",
                memo=f"Stripe payout - {len(payments)} payments",
                reference=f"STRIPE_PAYOUT_{payout_date.replace('-', '')}"
            ))
            
            # Stripe fees expense
            qbo_transactions.append(QBOTransaction(
                type="Expense",
                date=payout_date,
                amount=total_fees,
                account="Credit Card Processing Fees",
                vendor="Stripe",
                memo=f"Processing fees for {len(payments)} payments",
                reference=f"STRIPE_FEES_{payout_date.replace('-', '')}"
            ))
        
        # Add shared expenses that need job allocation
        shared_expenses = [
            QBOTransaction(
                type="Expense",
                date="2024-03-10",
                amount=2400.00,
                account="Materials - Landscape",
                vendor="Green Thumb Supplies",
                memo="Mulch delivery - multiple jobs",
                reference="INV_GTS_2024_0310"
            ),
            QBOTransaction(
                type="Expense",
                date="2024-03-12",
                amount=600.00,
                account="Equipment Rental",
                vendor="Heavy Equipment Rentals",
                memo="Excavator rental - 3 days",
                reference="RENTAL_HER_2024_0312"
            ),
            QBOTransaction(
                type="Expense",
                date="2024-03-15",
                amount=380.00,
                account="Vehicle Expenses",
                vendor="Shell Gas Station",
                memo="Fuel for all crews - March",
                reference="FUEL_MARCH_2024"
            )
        ]
        
        qbo_transactions.extend(shared_expenses)
        
        return qbo_transactions
    
    def generate_reconciliation_challenges(self) -> Dict[str, Any]:
        """Generate the complete dataset that creates real reconciliation challenges"""
        
        print("🏗️ Generating realistic service contractor test data...")
        
        # Generate all the interconnected data
        jobs = self.generate_complex_jobs()
        invoices = self.generate_invoices_with_timing_issues(jobs)
        stripe_payments = self.generate_stripe_payments_with_fees(invoices)
        qbo_transactions = self.generate_qbo_transactions_with_complications(stripe_payments)
        
        # Calculate the reconciliation challenges this creates
        challenges = self.analyze_reconciliation_challenges(jobs, invoices, stripe_payments, qbo_transactions)
        
        dataset = {
            "company": self.company_name,
            "period": "March 2024",
            "jobs": [asdict(job) for job in jobs],
            "invoices": [asdict(invoice) for invoice in invoices],
            "stripe_payments": [asdict(payment) for payment in stripe_payments],
            "qbo_transactions": [asdict(txn) for txn in qbo_transactions],
            "reconciliation_challenges": challenges
        }
        
        return dataset
    
    def analyze_reconciliation_challenges(self, jobs: List[Job], invoices: List[Invoice], 
                                        stripe_payments: List[StripePayment], 
                                        qbo_transactions: List[QBOTransaction]) -> Dict[str, Any]:
        """Analyze what makes this data challenging to reconcile"""
        
        challenges = {
            "period_mismatches": [],
            "bundled_deposits": [],
            "fee_allocation_needed": [],
            "shared_expense_allocation": [],
            "revenue_recognition_complexity": []
        }
        
        # Identify period mismatches
        for job in jobs:
            work_months = set()
            payment_months = set()
            
            for line_item in job.line_items:
                work_months.add(line_item.date[:7])  # YYYY-MM
            
            job_invoices = [inv for inv in invoices if inv.job_id == job.id]
            for invoice in job_invoices:
                if invoice.paid_date:
                    payment_months.add(invoice.paid_date[:7])
            
            if work_months != payment_months:
                challenges["period_mismatches"].append({
                    "job_id": job.id,
                    "work_periods": list(work_months),
                    "payment_periods": list(payment_months),
                    "complexity": "high" if len(work_months) > 1 or len(payment_months) > 1 else "medium"
                })
        
        # Identify bundled deposits
        payout_dates = {}
        for payment in stripe_payments:
            if payment.payout_date not in payout_dates:
                payout_dates[payment.payout_date] = []
            payout_dates[payment.payout_date].append(payment)
        
        for payout_date, payments in payout_dates.items():
            if len(payments) > 1:
                challenges["bundled_deposits"].append({
                    "payout_date": payout_date,
                    "payment_count": len(payments),
                    "total_amount": sum(p.amount for p in payments) / 100,
                    "total_fees": sum(p.fee for p in payments) / 100,
                    "jobs_affected": list(set(p.metadata["job_id"] for p in payments))
                })
        
        # Identify fee allocation complexity
        total_fees = sum(p.fee for p in stripe_payments) / 100
        challenges["fee_allocation_needed"].append({
            "total_stripe_fees": total_fees,
            "jobs_count": len(jobs),
            "allocation_method": "proportional_by_payment_amount"
        })
        
        # Identify shared expenses
        shared_expense_types = ["Materials - Landscape", "Equipment Rental", "Vehicle Expenses"]
        for txn in qbo_transactions:
            if txn.account in shared_expense_types:
                challenges["shared_expense_allocation"].append({
                    "expense_type": txn.account,
                    "amount": txn.amount,
                    "date": txn.date,
                    "allocation_method": "needs_manual_allocation"
                })
        
        # Revenue recognition complexity
        for job in jobs:
            if len(job.line_items) > 1:
                start_month = job.start_date[:7]
                end_month = job.end_date[:7]
                
                complexity_level = "low"
                if start_month != end_month:
                    complexity_level = "high"
                elif job.payment_terms not in ["Net 30", "Due on receipt"]:
                    complexity_level = "medium"
                
                challenges["revenue_recognition_complexity"].append({
                    "job_id": job.id,
                    "spans_multiple_periods": start_month != end_month,
                    "payment_terms": job.payment_terms,
                    "complexity_level": complexity_level,
                    "recommended_method": "percentage_completion" if complexity_level == "high" else "milestone"
                })
        
        return challenges

def main():
    generator = RealisticTestDataGenerator()
    dataset = generator.generate_reconciliation_challenges()
    
    # Save to file
    output_file = "realistic_test_data.json"
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✅ Realistic test data generated: {output_file}")
    
    # Print summary of challenges
    challenges = dataset["reconciliation_challenges"]
    print("\n📊 Reconciliation Challenges Created:")
    print(f"   Period Mismatches: {len(challenges['period_mismatches'])}")
    print(f"   Bundled Deposits: {len(challenges['bundled_deposits'])}")
    print(f"   Shared Expenses: {len(challenges['shared_expense_allocation'])}")
    print(f"   Complex Revenue Recognition: {len(challenges['revenue_recognition_complexity'])}")
    
    # Calculate totals
    total_revenue = sum(job["total_value"] for job in dataset["jobs"])
    total_stripe_fees = sum(payment["fee"] for payment in dataset["stripe_payments"]) / 100
    
    print("\n💰 Financial Summary:")
    print(f"   Total Contract Value: ${total_revenue:,.2f}")
    print(f"   Total Stripe Fees: ${total_stripe_fees:.2f}")
    print(f"   Jobs: {len(dataset['jobs'])}")
    print(f"   Invoices: {len(dataset['invoices'])}")
    print(f"   Stripe Payments: {len(dataset['stripe_payments'])}")
    print(f"   QBO Transactions: {len(dataset['qbo_transactions'])}")

if __name__ == "__main__":
    main()
