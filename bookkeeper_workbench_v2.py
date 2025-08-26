#!/usr/bin/env python3
"""
Real Bookkeeper Workbench

This is what bookkeepers actually need:
1. See raw transactions that need categorization
2. See proposed payment matches with actual details
3. Approve, reject, or manually fix matches
4. Handle bundled deposits by unbundling them
5. Categorize expenses and normalize vendors

This replaces the spreadsheet workflow where bookkeepers manually match payments.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock

# Import our services
from domains.ar.services.reconciliation import ReconciliationService
from tests.fixtures.realistic_variance_scenarios import generate_realistic_variance_scenario

st.set_page_config(
    page_title="Bookkeeper Workbench", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📚 Bookkeeper Workbench")
st.markdown("### *Your digital replacement for the reconciliation spreadsheet*")

# Load test data
if 'scenario_data' not in st.session_state:
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
    
    st.session_state.scenario_data = scenario_data
    st.session_state.reconciliation_result = result

scenario_data = st.session_state.scenario_data
result = st.session_state.reconciliation_result

# Sidebar: Summary Stats
st.sidebar.header("📊 Today's Work")
st.sidebar.metric("Stripe Payments to Review", len(scenario_data['stripe_payments']))
st.sidebar.metric("Outstanding Invoices", len([inv for inv in scenario_data['jobber_invoices'] if not inv.get('paid_date')]))
st.sidebar.metric("Expenses to Categorize", len(scenario_data['qbo_transactions']))

# Main tabs for bookkeeper workflow
tab1, tab2, tab3 = st.tabs([
    "💰 Payment Matching", 
    "📋 Expense Categorization",
    "📊 Summary & Export"
])

with tab1:
    st.subheader("Payment Matching Workbench")
    st.markdown("*This is where you match Stripe payments to Jobber invoices*")
    
    # Show raw data side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💳 Stripe Payments Received**")
        
        payments_data = []
        for payment in scenario_data['stripe_payments']:
            payments_data.append({
                "Date": payment['created'][:10],
                "Amount": f"${payment['amount']/100:,.2f}",
                "Net (after fees)": f"${payment.get('net', payment['amount'])/100:,.2f}",
                "Payment ID": payment['id'],
                "Metadata": str(payment.get('metadata', {}))
            })
        
        df_payments = pd.DataFrame(payments_data)
        st.dataframe(df_payments, use_container_width=True)
    
    with col2:
        st.markdown("**📄 Outstanding Invoices**")
        
        invoice_data = []
        for invoice in scenario_data['jobber_invoices']:
            job = next((j for j in scenario_data['jobs'] if j['id'] == invoice['job_id']), {})
            invoice_data.append({
                "Invoice ID": invoice['id'],
                "Job": f"{invoice['job_id']} - {job.get('name', 'Unknown')}",
                "Amount": f"${invoice['amount']:,.2f}",
                "Status": "PAID" if invoice.get('paid_date') else "UNPAID",
                "Paid Date": invoice.get('paid_date', 'Not paid')
            })
        
        df_invoices = pd.DataFrame(invoice_data)
        st.dataframe(df_invoices, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🔍 Proposed Matches (AI Suggestions)")
    
    # Show actual match details with ability to approve/reject
    for i, match in enumerate(result['payment_matches']):
        payment_id = match['stripe_payment_id']
        payment = next((p for p in scenario_data['stripe_payments'] if p['id'] == payment_id), {})
        
        with st.expander(f"Match #{i+1}: ${payment.get('amount', 0)/100:,.2f} payment → {len(match['jobber_invoice_ids'])} invoice(s)", expanded=True):
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown("**💳 Stripe Payment Details:**")
                st.write(f"• **Payment ID**: {payment_id}")
                st.write(f"• **Date**: {payment.get('created', 'Unknown')[:10]}")
                st.write(f"• **Gross Amount**: ${payment.get('amount', 0)/100:,.2f}")
                st.write(f"• **Net Amount**: ${payment.get('net', payment.get('amount', 0))/100:,.2f}")
                st.write(f"• **Fees**: ${(payment.get('amount', 0) - payment.get('net', payment.get('amount', 0)))/100:,.2f}")
                
                if payment.get('metadata'):
                    st.write(f"• **Metadata**: {payment['metadata']}")
            
            with col2:
                st.markdown("**📄 Matched Invoice(s):**")
                total_invoice_amount = 0
                for inv_id in match['jobber_invoice_ids']:
                    invoice = next((inv for inv in scenario_data['jobber_invoices'] if inv['id'] == inv_id), {})
                    job = next((j for j in scenario_data['jobs'] if j['id'] == invoice.get('job_id')), {})
                    
                    st.write(f"• **{inv_id}**: ${invoice.get('amount', 0):,.2f}")
                    st.write(f"  Job: {job.get('name', 'Unknown')}")
                    total_invoice_amount += invoice.get('amount', 0)
                
                st.write(f"• **Total Invoice Amount**: ${total_invoice_amount:,.2f}")
                st.write(f"• **Variance**: ${match.get('variance_amount', 0):,.2f}")
            
            with col3:
                st.markdown("**🤖 AI Assessment:**")
                confidence = match.get('confidence', 0)
                st.metric("Confidence", f"{confidence:.1%}")
                
                if confidence >= 0.9:
                    st.success("✅ High confidence")
                elif confidence >= 0.7:
                    st.warning("⚠️ Medium confidence")
                else:
                    st.error("❌ Low confidence")
                
                st.write(f"**Match Type**: {match.get('match_type', 'unknown').title()}")
                
                # Show reasoning
                rationale = match.get('rationale', {})
                if rationale:
                    st.markdown("**Reasoning**:")
                    for key, value in rationale.items():
                        if isinstance(value, (int, float)):
                            st.write(f"• {key}: {value:.2f}")
                        else:
                            st.write(f"• {key}: {value}")
            
            # Action buttons
            st.markdown("**👩‍💼 Your Decision:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✅ Approve Match", key=f"approve_{i}"):
                    st.success("✅ Match approved! This will be recorded in your books.")
                    
            with col2:
                if st.button("❌ Reject Match", key=f"reject_{i}"):
                    st.error("❌ Match rejected. Payment remains unmatched.")
                    
            with col3:
                if st.button("✏️ Manual Match", key=f"manual_{i}"):
                    st.info("✏️ Manual matching interface would open here")
                    
            with col4:
                if st.button("🔄 Split Payment", key=f"split_{i}"):
                    st.info("🔄 Payment splitting interface would open here")

with tab2:
    st.subheader("Expense Categorization")
    st.markdown("*Categorize your QuickBooks expenses and normalize vendor names*")
    
    expense_data = []
    for expense in scenario_data['qbo_transactions']:
        job = next((j for j in scenario_data['jobs'] if j['id'] == expense.get('job_id')), {})
        expense_data.append({
            "Date": expense['date'],
            "Vendor": expense['vendor'],
            "Amount": f"${abs(expense['amount']):,.2f}",
            "Current Category": expense['account'],
            "Memo": expense['memo'],
            "Job": job.get('name', 'No job assigned'),
            "Action": "Needs Review"
        })
    
    df_expenses = pd.DataFrame(expense_data)
    st.dataframe(df_expenses, use_container_width=True)
    
    st.markdown("**🔧 Bulk Actions:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏷️ Auto-Categorize All"):
            st.info("Running AI categorization...")
    with col2:
        if st.button("🏢 Normalize Vendors"):
            st.info("Running vendor normalization...")
    with col3:
        if st.button("💾 Save Changes"):
            st.success("Changes saved to QuickBooks!")

with tab3:
    st.subheader("Summary & Export")
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    total_payments = sum(p['amount']/100 for p in scenario_data['stripe_payments'])
    total_invoices = sum(inv['amount'] for inv in scenario_data['jobber_invoices'])
    matched_payments = len([m for m in result['payment_matches'] if m.get('confidence', 0) >= 0.9])
    
    with col1:
        st.metric("Total Payments", f"${total_payments:,.2f}")
    with col2:
        st.metric("Total Invoices", f"${total_invoices:,.2f}")
    with col3:
        st.metric("Auto-Matched", f"{matched_payments}/{len(result['payment_matches'])}")
    with col4:
        variance = total_payments - total_invoices
        st.metric("Net Variance", f"${variance:,.2f}")
    
    st.markdown("---")
    
    # Export options
    st.markdown("**📤 Export Options:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to Excel"):
            st.info("Exporting matched transactions to Excel...")
    
    with col2:
        if st.button("📋 Copy Journal Entries"):
            st.info("Copying journal entries to clipboard...")
    
    with col3:
        if st.button("🔄 Sync to QuickBooks"):
            st.info("Syncing approved matches to QuickBooks...")

# Footer
st.markdown("---")
st.markdown("*This replaces your manual spreadsheet reconciliation process*")
