#!/usr/bin/env python3
"""
Job Reconciliation Summary

This creates the summary that bookkeepers actually want to see:
- One row per job
- Total work completed vs total cash received
- Clear status of each job (Complete, Partial, Overpaid, etc.)
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from unittest.mock import Mock

from domains.ar.services.reconciliation import ReconciliationService
from tests.fixtures.realistic_variance_scenarios import generate_realistic_variance_scenario

def create_job_summary(scenario_data: Dict, result: Dict) -> List[Dict]:
    """Create a job-by-job summary that makes sense to bookkeepers."""
    
    job_summaries = []
    
    for job in scenario_data['jobs']:
        job_id = job['id']
        
        # Get all invoices for this job
        job_invoices = [inv for inv in scenario_data['jobber_invoices'] if inv['job_id'] == job_id]
        total_invoiced = sum(inv['amount'] for inv in job_invoices)
        
        # Get all payments for this job
        job_payments = []
        total_paid = 0.0
        for payment in scenario_data['stripe_payments']:
            for invoice in job_invoices:
                if payment.get('metadata', {}).get('invoice_id') == invoice['id']:
                    job_payments.append(payment)
                    total_paid += payment.get('net', payment['amount']) / 100
        
        # Calculate work completed (from line items or completion percentage)
        if 'line_items' in job:
            work_completed = sum(item['amount'] for item in job['line_items'])
        else:
            completion_pct = job.get('completion_percentage', 0) / 100
            work_completed = job['estimated_revenue'] * completion_pct
        
        # Determine status
        if total_paid == 0:
            if work_completed > 0:
                status = "🔴 UNPAID (Collections needed)"
            else:
                status = "⚪ NOT STARTED"
        elif abs(total_paid - work_completed) < 50:  # Within $50
            status = "✅ BALANCED"
        elif total_paid > work_completed:
            status = "🟡 PREPAID (Customer ahead)"
        else:
            status = "🔴 UNDERPAID (Customer behind)"
        
        variance = work_completed - total_paid
        
        job_summaries.append({
            "Job ID": job_id,
            "Job Name": job['name'],
            "Work Completed": work_completed,
            "Cash Received": total_paid,
            "Variance": variance,
            "Status": status,
            "Total Invoiced": total_invoiced,
            "Payment Count": len(job_payments),
            "Completion %": f"{job.get('completion_percentage', 0)}%"
        })
    
    return job_summaries

st.set_page_config(page_title="Job Reconciliation Summary", layout="wide")

st.title("🎯 Job Reconciliation Summary")
st.markdown("### *One row per job - the view bookkeepers actually want*")

# Load data
scenario_data = generate_realistic_variance_scenario()
mock_db = Mock()
service = ReconciliationService(mock_db)

adapted = {
    'jobs': scenario_data['jobs'],
    'invoices': scenario_data['jobber_invoices'], 
    'stripe_payments': scenario_data['stripe_payments'],
    'qbo_transactions': scenario_data['qbo_transactions']
}

result = service.process_bundled_ar_matching(adapted)

# Create job summary
job_summaries = create_job_summary(scenario_data, result)

# Display as table
st.subheader("📊 Job-by-Job Status")

df = pd.DataFrame(job_summaries)

# Format currency columns
for col in ['Work Completed', 'Cash Received', 'Variance', 'Total Invoiced']:
    df[col] = df[col].apply(lambda x: f"${x:,.2f}")

st.dataframe(df, use_container_width=True)

# Add explanations
st.markdown("---")
st.subheader("📖 What This Means")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Status Meanings:**
    - ✅ **BALANCED**: Work and payments match (within $50)
    - 🔴 **UNPAID**: Work done but no payment received
    - 🔴 **UNDERPAID**: Customer owes money for completed work
    - 🟡 **PREPAID**: Customer paid ahead of work completion
    - ⚪ **NOT STARTED**: No work done yet
    """)

with col2:
    st.markdown("""
    **Variance Explanation:**
    - **Positive variance** = Customer owes you money (A/R)
    - **Negative variance** = You owe customer work (Deferred Revenue)
    - **Zero variance** = Perfect balance
    
    *This shows the actual business situation, not accounting complexity.*
    """)

# Summary totals
st.markdown("---")
st.subheader("💼 Business Summary")

total_work = sum(summary['Work Completed'] for summary in job_summaries)
total_cash = sum(summary['Cash Received'] for summary in job_summaries)
net_variance = total_work - total_cash

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Work Completed", f"${total_work:,.2f}")
with col2:
    st.metric("Total Cash Received", f"${total_cash:,.2f}")
with col3:
    if net_variance > 0:
        st.metric("Net A/R (Owed to you)", f"${net_variance:,.2f}")
    elif net_variance < 0:
        st.metric("Deferred Revenue (Work owed)", f"${abs(net_variance):,.2f}")
    else:
        st.metric("Perfect Balance!", "$0.00")

# Copy button
if st.button("📋 Copy Job Summary"):
    # Raw data for copying
    raw_data = []
    for summary in job_summaries:
        raw_data.append({
            "job_id": summary["Job ID"],
            "job_name": summary["Job Name"],
            "work_completed": summary["Work Completed"],
            "cash_received": summary["Cash Received"],
            "variance": summary["Variance"],
            "status": summary["Status"]
        })
    
    df_raw = pd.DataFrame(raw_data)
    st.code(df_raw.to_string(index=False), language=None)
    st.success("✅ Raw data shown above - select and copy!")
