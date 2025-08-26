#!/usr/bin/env python3
"""
ServicePro Reconciliation Dashboard

A compelling Streamlit interface that demonstrates the power of our
bundled payment matching and shared expense allocation for contractors.

This is the "demo that sells itself" - showing bookkeepers exactly
how the system handles complex scenarios they currently do in Excel.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
from unittest.mock import Mock

# Import our services
from domains.ar.services.reconciliation import ReconciliationService
from tests.fixtures.servicepro_scenarios import (
    generate_bobs_landscaping_scenario,
    generate_elite_hvac_scenario,
    generate_mega_construction_scenario
)
from tests.fixtures.realistic_variance_scenarios import (
    generate_realistic_variance_scenario,
    generate_simple_balanced_scenario
)

st.set_page_config(
    page_title="ServicePro Reconciliation Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.confidence-high { color: #28a745; font-weight: bold; }
.confidence-medium { color: #ffc107; font-weight: bold; }
.confidence-low { color: #dc3545; font-weight: bold; }
.manual-review { color: #6c757d; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🔧 ServicePro Reconciliation Dashboard")
st.markdown("### *See how AI handles the complex payment matching that breaks Excel*")

# Sidebar: Scenario Selection
st.sidebar.header("🎯 Demo Scenarios")
st.sidebar.markdown("Select a contractor scenario to see the reconciliation in action:")

scenario_options = {
    "Realistic Variance Analysis": generate_realistic_variance_scenario,
    "Simple Balanced Scenario": generate_simple_balanced_scenario,
    "Bob's Landscaping (Simple)": generate_bobs_landscaping_scenario,
    "Elite HVAC (Medium Complexity)": generate_elite_hvac_scenario,
    "Mega Construction (Nightmare Mode)": generate_mega_construction_scenario
}

selected_scenario = st.sidebar.selectbox(
    "Choose Scenario:",
    list(scenario_options.keys()),
    index=0  # Default to realistic variance scenario
)

# Load the selected scenario
scenario_data = scenario_options[selected_scenario]()
company = scenario_data["company"]
challenges = scenario_data["reconciliation_challenges"]

# Company Info
st.sidebar.markdown(f"**{company['name']}**")
st.sidebar.markdown(f"*{company.get('business_type', 'Service Contractor')} - {company['complexity']} Complexity*")
st.sidebar.markdown(f"📊 {len(scenario_data['jobs'])} Jobs, {len(scenario_data['jobber_invoices'])} Invoices")
st.sidebar.markdown(f"💰 {len(scenario_data['stripe_payments'])} Payments, {len(scenario_data['qbo_transactions'])} Expenses")

# Main Dashboard
if st.sidebar.button("🚀 Run Reconciliation", type="primary"):
    with st.spinner("Running AI reconciliation..."):
        # Mock database session
        mock_db = Mock()
        reconciliation_service = ReconciliationService(mock_db)
        
        # Adapt scenario data
        adapted_scenario = {
            "jobs": scenario_data["jobs"],
            "invoices": scenario_data["jobber_invoices"],
            "stripe_payments": scenario_data["stripe_payments"],
            "qbo_transactions": scenario_data["qbo_transactions"]
        }
        
        # Run reconciliation
        result = reconciliation_service.process_bundled_ar_matching(adapted_scenario)
        
        # Store results in session state
        st.session_state.reconciliation_result = result
        st.session_state.scenario_data = scenario_data

# Display results if available
if hasattr(st.session_state, 'reconciliation_result'):
    result = st.session_state.reconciliation_result
    scenario_data = st.session_state.scenario_data
    summary = result["reconciliation_summary"]
    
    st.success("✅ Reconciliation Complete!")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Match Rate",
            f"{summary['matching_summary']['match_rate_percentage']:.1f}%",
            delta="vs 20% manual rate"
        )
    
    with col2:
        st.metric(
            "High Confidence Matches",
            summary['matching_summary']['high_confidence_matches'],
            delta="Auto-approved"
        )
    
    with col3:
        st.metric(
            "Requires Review",
            summary['matching_summary']['requires_human_review'],
            delta="HITL needed"
        )
    
    with col4:
        total_variance = summary['revenue_recognition_summary']['total_variance']
        st.metric(
            "Total Variance",
            f"${total_variance:,.2f}",
            delta="Accruals/Deferrals"
        )
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Payment Matching", 
        "📊 Revenue Recognition", 
        "🔄 Shared Expenses",
        "🎯 HITL Review"
    ])
    
    with tab1:
        st.subheader("Payment Matching Results")
        
        # Payment matches table
        matches_data = []
        for match in result["payment_matches"]:
            confidence_class = "confidence-high" if match["confidence"] >= 0.9 else \
                             "confidence-medium" if match["confidence"] >= 0.7 else \
                             "confidence-low" if match["confidence"] >= 0.5 else "manual-review"
            
            matches_data.append({
                "Payment ID": match["stripe_payment_id"][:12] + "...",
                "Type": match["match_type"].title(),
                "Invoices": len(match["jobber_invoice_ids"]),
                "Confidence": f"{match['confidence']:.1%}",
                "Variance": f"${match['variance_amount']:.2f}",
                "Action": match["suggested_action"].replace("_", " ").title(),
                "Review": "✅" if not match["requires_human_review"] else "🔍"
            })
        
        if matches_data:
            df_matches = pd.DataFrame(matches_data)
            st.dataframe(df_matches, use_container_width=True)
            
            # Confidence distribution chart
            confidence_counts = {}
            for match in result["payment_matches"]:
                if match["confidence"] >= 0.9:
                    confidence_counts["High (90%+)"] = confidence_counts.get("High (90%+)", 0) + 1
                elif match["confidence"] >= 0.7:
                    confidence_counts["Medium (70-90%)"] = confidence_counts.get("Medium (70-90%)", 0) + 1
                elif match["confidence"] >= 0.5:
                    confidence_counts["Low (50-70%)"] = confidence_counts.get("Low (50-70%)", 0) + 1
                else:
                    confidence_counts["Manual Review"] = confidence_counts.get("Manual Review", 0) + 1
            
            fig = px.pie(
                values=list(confidence_counts.values()),
                names=list(confidence_counts.keys()),
                title="Confidence Distribution",
                color_discrete_map={
                    "High (90%+)": "#28a745",
                    "Medium (70-90%)": "#ffc107", 
                    "Low (50-70%)": "#fd7e14",
                    "Manual Review": "#dc3545"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Revenue Recognition Analysis")
        
        # Explanation of what this means
        st.info("""
        **📖 Revenue Recognition Variance Analysis:**
        - **Work Performed**: Revenue earned based on job completion/milestones (what you should book)
        - **Cash Received**: Actual payments received for this period (what you actually got)
        - **Variance**: Cash vs. Work difference - this is your **variance analysis** showing timing mismatches
        - **Positive Variance**: Work done but not paid yet → **Accrual** (A/R increase)
        - **Negative Variance**: Paid but work not done yet → **Deferral** (Deferred Revenue liability)
        
        *This analysis helps identify cash flow timing vs. revenue recognition timing - critical for GAAP compliance.*
        """)
        
        if result["revenue_recognition_entries"]:
            rev_data = []
            for entry in result["revenue_recognition_entries"]:
                variance = entry['variance_amount']
                # Determine status based on variance
                if variance > 0:
                    status = "🔴 Unpaid Work"
                elif variance < 0:
                    status = "🟡 Prepaid Work"  
                else:
                    status = "✅ Balanced"
                    
                rev_data.append({
                    "Job ID": entry["job_id"],
                    "Period": entry["period"],
                    "Work Performed": f"${entry['work_performed_amount']:,.2f}",
                    "Cash Received": f"${entry['cash_received_amount']:,.2f}",
                    "Variance": f"${variance:,.2f}",
                    "Status": status,
                    "Method": entry["recognition_method"].replace("_", " ").title(),
                    "Accrual": "✅" if entry["requires_accrual"] else "❌",
                    "Deferral": "✅" if entry["requires_deferral"] else "❌"
                })
            
            df_revenue = pd.DataFrame(rev_data)
            st.dataframe(df_revenue, use_container_width=True)
            
            # Add copy button for the table
            if st.button("📋 Copy Revenue Recognition Table", key="copy_revenue_table"):
                # Convert to raw data for copying
                raw_data = []
                for entry in result["revenue_recognition_entries"]:
                    raw_data.append({
                        "job_id": entry["job_id"],
                        "period": entry["period"],
                        "work_performed_amount": entry["work_performed_amount"],
                        "cash_received_amount": entry["cash_received_amount"],
                        "variance_amount": entry["variance_amount"],
                        "recognition_method": entry["recognition_method"],
                        "requires_accrual": entry["requires_accrual"],
                        "requires_deferral": entry["requires_deferral"]
                    })
                df_copy = pd.DataFrame(raw_data)
                st.code(df_copy.to_string(index=False), language=None)
                st.success("✅ Raw table data shown above - you can select and copy this text!")
                
            # Summary explanation
            total_work = sum(entry["work_performed_amount"] for entry in result["revenue_recognition_entries"])
            total_cash = sum(entry["cash_received_amount"] for entry in result["revenue_recognition_entries"])
            net_variance = total_work - total_cash
            
            st.markdown("---")
            st.markdown("**📊 Summary Explanation:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Work Done", f"${total_work:,.2f}")
            with col2:
                st.metric("Total Cash Received", f"${total_cash:,.2f}")
            with col3:
                variance_label = "Unpaid Work" if net_variance > 0 else "Overpayments" if net_variance < 0 else "Perfect Balance"
                st.metric("Net Variance", f"${net_variance:,.2f}", delta=variance_label)
                
            if abs(net_variance) > 0:
                if net_variance > 0:
                    st.warning(f"⚠️ **${net_variance:,.2f} in unpaid work** - You've completed work but haven't been paid yet. This creates an Accounts Receivable (money owed to you).")
                else:
                    st.info(f"💰 **${abs(net_variance):,.2f} in prepayments** - You've been paid for work not yet completed. This creates Deferred Revenue (you owe work/service).")
            else:
                st.success("✅ **Perfect balance** - Work performed matches payments received!")
        else:
            st.info("No revenue recognition entries for this scenario.")
    
    with tab3:
        st.subheader("Shared Expense Allocation")
        
        if result["shared_expense_allocations"]:
            expense_data = []
            for expense in result["shared_expense_allocations"]:
                expense_data.append({
                    "Description": expense["description"],
                    "Amount": f"${expense['total_amount']:,.2f}",
                    "Jobs Affected": len(expense["affected_job_ids"]),
                    "Allocation Method": expense["allocation_method"].replace("_", " ").title(),
                    "Review Required": "🔍" if expense["requires_manual_allocation"] else "✅"
                })
            
            df_expenses = pd.DataFrame(expense_data)
            st.dataframe(df_expenses, use_container_width=True)
            
            # Allocation method distribution
            allocation_methods = {}
            for expense in result["shared_expense_allocations"]:
                method = expense["allocation_method"].replace("_", " ").title()
                allocation_methods[method] = allocation_methods.get(method, 0) + 1
            
            fig = px.bar(
                x=list(allocation_methods.keys()),
                y=list(allocation_methods.values()),
                title="Allocation Methods Used",
                labels={"x": "Allocation Method", "y": "Number of Expenses"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No shared expenses identified for this scenario.")
    
    with tab4:
        st.subheader("Human-in-the-Loop Review Interface")
        st.markdown("*This is where bookkeepers review flagged transactions*")
        
        # Show transactions that need review
        review_needed = [match for match in result["payment_matches"] if match["requires_human_review"]]
        
        if review_needed:
            st.warning(f"⚠️ {len(review_needed)} transactions need your review")
            
            for i, match in enumerate(review_needed):
                with st.expander(f"Review Payment {match['stripe_payment_id'][:12]}... ({match['match_type']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Payment Details:**")
                        st.write(f"• Amount: ${match['variance_amount'] + sum(inv.get('amount', 0) for inv in scenario_data['jobber_invoices'] if inv['id'] in match['jobber_invoice_ids']):,.2f}")
                        st.write(f"• Confidence: {match['confidence']:.1%}")
                        st.write(f"• Variance: ${match['variance_amount']:,.2f}")
                    
                    with col2:
                        st.markdown("**AI Rationale:**")
                        rationale = match.get("rationale", {})
                        for key, value in rationale.items():
                            if isinstance(value, (int, float)):
                                st.write(f"• {key.replace('_', ' ').title()}: {value:.2f}")
                            else:
                                st.write(f"• {key.replace('_', ' ').title()}: {value}")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✅ Approve", key=f"approve_{i}"):
                            st.success("Transaction approved!")
                    with col2:
                        if st.button("❌ Reject", key=f"reject_{i}"):
                            st.error("Transaction rejected - will require manual matching")
                    with col3:
                        if st.button("📝 Modify", key=f"modify_{i}"):
                            st.info("Modification interface would open here")
        else:
            st.success("🎉 No transactions need review - all were handled automatically!")

# Scenario Details (Always visible)
st.markdown("---")
st.subheader("📋 Scenario Details")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Business Challenges:**")
    if challenges["bundled_deposits"]:
        st.write(f"• {len(challenges['bundled_deposits'])} bundled deposits")
    if challenges["period_mismatches"]:
        st.write(f"• {len(challenges['period_mismatches'])} period mismatches")
    if challenges["shared_expense_allocation"]:
        st.write(f"• {len(challenges['shared_expense_allocation'])} shared expenses")
    if challenges.get("progress_billing"):
        st.write("• Progress billing complexity")

with col2:
    st.markdown("**What This Replaces:**")
    st.write("• Manual Excel reconciliation")
    st.write("• Hours of payment matching")
    st.write("• Guesswork on shared expenses")
    st.write("• Period-end adjustment confusion")
    st.write("• Revenue recognition errors")

# Footer
st.markdown("---")
st.markdown("*Built with ❤️ for service contractors who deserve better than Excel*")
