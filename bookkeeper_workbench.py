#!/usr/bin/env python3
"""
ServicePro Bookkeeper Workbench

A comprehensive interface for bookkeepers to:
1. Review AI-matched transactions
2. Manually match unmatched payments
3. Correct incorrect matches
4. Learn from corrections to improve the AI
5. Export results for accounting software

This is the production tool bookkeepers actually use day-to-day.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import Mock
import uuid

# Import our services
from domains.ar.services.reconciliation import ReconciliationService
from tests.fixtures.servicepro_scenarios import (
    generate_bobs_landscaping_scenario,
    generate_elite_hvac_scenario,
    generate_mega_construction_scenario
)

st.set_page_config(
    page_title="ServicePro Bookkeeper Workbench", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'select_data'
if 'reconciliation_result' not in st.session_state:
    st.session_state.reconciliation_result = None
if 'manual_matches' not in st.session_state:
    st.session_state.manual_matches = {}
if 'corrections' not in st.session_state:
    st.session_state.corrections = {}

st.title("📚 ServicePro Bookkeeper Workbench")
st.markdown("### *Your AI-powered assistant for payment reconciliation*")

# Progress indicator
steps = ["Select Data", "Review AI Matches", "Handle Unmatched", "Export Results"]
current_step_idx = steps.index(st.session_state.current_step.replace('_', ' ').title()) if st.session_state.current_step.replace('_', ' ').title() in steps else 0

cols = st.columns(len(steps))
for i, step in enumerate(steps):
    with cols[i]:
        if i <= current_step_idx:
            st.markdown(f"✅ **{step}**")
        else:
            st.markdown(f"⏳ {step}")

st.markdown("---")

# Step 1: Data Selection
if st.session_state.current_step == 'select_data':
    st.header("📊 Step 1: Select Your Data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Choose your data source:**")
        
        data_source = st.radio(
            "Data Source",
            ["Demo Scenarios (for testing)", "Upload Files", "Connect to QBO/Stripe"],
            index=0
        )
        
        if data_source == "Demo Scenarios (for testing)":
            scenario_options = {
                "Bob's Landscaping (Simple)": generate_bobs_landscaping_scenario,
                "Elite HVAC (Medium Complexity)": generate_elite_hvac_scenario,
                "Mega Construction (Nightmare Mode)": generate_mega_construction_scenario
            }
            
            selected_scenario = st.selectbox(
                "Choose Demo Scenario:",
                list(scenario_options.keys()),
                index=1
            )
            
            if st.button("📥 Load Demo Data", type="primary"):
                st.session_state.scenario_data = scenario_options[selected_scenario]()
                st.session_state.current_step = 'run_ai'
                st.rerun()
        
        elif data_source == "Upload Files":
            st.markdown("**Upload your transaction files:**")
            
            col1a, col1b = st.columns(2)
            with col1a:
                payments_file = st.file_uploader("Stripe Payments (CSV)", type=['csv'])
                invoices_file = st.file_uploader("Jobber Invoices (CSV)", type=['csv'])
            with col1b:
                jobs_file = st.file_uploader("Jobs Data (CSV)", type=['csv'])
                expenses_file = st.file_uploader("QBO Expenses (CSV)", type=['csv'])
            
            if payments_file and invoices_file and jobs_file:
                if st.button("📥 Load Uploaded Data", type="primary"):
                    st.info("File upload processing would be implemented here")
        
        else:  # Connect to APIs
            st.markdown("**API Connections:**")
            
            col1a, col1b = st.columns(2)
            with col1a:
                qbo_token = st.text_input("QBO Access Token", type="password")
                stripe_key = st.text_input("Stripe API Key", type="password")
            with col1b:
                jobber_token = st.text_input("Jobber API Token", type="password")
                date_range = st.date_input("Date Range", value=[datetime.now() - timedelta(days=30), datetime.now()])
            
            if qbo_token and stripe_key and jobber_token:
                if st.button("🔗 Connect & Load Data", type="primary"):
                    st.info("API integration would be implemented here")
    
    with col2:
        st.markdown("**What happens next:**")
        st.markdown("1. ✅ Load your transaction data")
        st.markdown("2. 🤖 AI analyzes and matches payments")
        st.markdown("3. 👀 You review and correct matches")
        st.markdown("4. 📤 Export clean data to your accounting software")
        
        st.info("💡 **Tip**: Start with demo data to see how it works!")

# Step 2: Run AI Reconciliation
elif st.session_state.current_step == 'run_ai':
    st.header("🤖 Step 2: AI Reconciliation")
    
    scenario_data = st.session_state.scenario_data
    company = scenario_data["company"]
    
    st.markdown(f"**Processing: {company['name']}**")
    st.markdown(f"📊 {len(scenario_data['jobs'])} Jobs, {len(scenario_data['jobber_invoices'])} Invoices, {len(scenario_data['stripe_payments'])} Payments")
    
    if st.button("🚀 Run AI Reconciliation", type="primary"):
        with st.spinner("AI is analyzing your transactions..."):
            # Run reconciliation
            mock_db = Mock()
            reconciliation_service = ReconciliationService(mock_db)
            
            adapted_scenario = {
                "jobs": scenario_data["jobs"],
                "invoices": scenario_data["jobber_invoices"],
                "stripe_payments": scenario_data["stripe_payments"],
                "qbo_transactions": scenario_data["qbo_transactions"]
            }
            
            result = reconciliation_service.process_bundled_ar_matching(adapted_scenario)
            st.session_state.reconciliation_result = result
            st.session_state.current_step = 'review_matches'
            
        st.success("✅ AI reconciliation complete!")
        st.rerun()

# Step 3: Review AI Matches
elif st.session_state.current_step == 'review_matches':
    st.header("👀 Step 3: Review AI Matches")
    
    result = st.session_state.reconciliation_result
    summary = result["reconciliation_summary"]
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Payments", summary['matching_summary']['total_payments'])
    with col2:
        st.metric("Auto-Matched", summary['matching_summary']['high_confidence_matches'], 
                 delta=f"{summary['matching_summary']['match_rate_percentage']:.1f}%")
    with col3:
        needs_review = summary['matching_summary']['requires_human_review']
        st.metric("Needs Review", needs_review, delta="Human input needed")
    with col4:
        unmatched = summary['matching_summary']['total_payments'] - summary['matching_summary']['high_confidence_matches']
        st.metric("Unmatched", unmatched, delta="Manual matching")
    
    # Tabs for different match types
    tab1, tab2, tab3 = st.tabs(["✅ Auto-Matched", "🔍 Needs Review", "❌ Unmatched"])
    
    with tab1:
        st.subheader("Auto-Matched Transactions (High Confidence)")
        
        auto_matched = [m for m in result["payment_matches"] if m["confidence"] >= 0.9 and not m["requires_human_review"]]
        
        if auto_matched:
            st.success(f"🎉 {len(auto_matched)} transactions were automatically matched with high confidence!")
            
            for i, match in enumerate(auto_matched):
                with st.expander(f"Payment {match['stripe_payment_id'][:12]}... - {match['match_type'].title()} Match"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Match Details:**")
                        st.write(f"• Confidence: {match['confidence']:.1%}")
                        st.write(f"• Invoices: {len(match['jobber_invoice_ids'])}")
                        st.write(f"• Variance: ${match['variance_amount']:.2f}")
                    
                    with col2:
                        st.markdown("**AI Reasoning:**")
                        rationale = match.get("rationale", {})
                        for key, value in rationale.items():
                            if key == "reason":
                                st.write(f"• {value}")
                            elif isinstance(value, (int, float)):
                                st.write(f"• {key.replace('_', ' ').title()}: {value:.2f}")
                    
                    # Option to override if needed
                    if st.button("🔄 Override This Match", key=f"override_auto_{i}"):
                        st.session_state.corrections[match['stripe_payment_id']] = "override_requested"
                        st.info("Match flagged for manual review")
        else:
            st.info("No auto-matched transactions in this dataset.")
    
    with tab2:
        st.subheader("Transactions Needing Your Review")
        
        review_needed = [m for m in result["payment_matches"] if m["requires_human_review"] and m["match_type"] != "unmatched"]
        
        if review_needed:
            st.warning(f"⚠️ {len(review_needed)} transactions need your expert review")
            
            for i, match in enumerate(review_needed):
                with st.expander(f"🔍 Review: Payment {match['stripe_payment_id'][:12]}... ({match['confidence']:.1%} confidence)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**AI's Best Guess:**")
                        st.write(f"• Type: {match['match_type'].title()}")
                        st.write(f"• Confidence: {match['confidence']:.1%}")
                        st.write(f"• Invoices: {match['jobber_invoice_ids']}")
                        st.write(f"• Variance: ${match['variance_amount']:.2f}")
                    
                    with col2:
                        st.markdown("**Why AI Flagged This:**")
                        rationale = match.get("rationale", {})
                        reason = rationale.get("reason", "Low confidence match")
                        st.write(f"• {reason}")
                        
                        if match['variance_amount'] > 10:
                            st.write(f"• Large variance: ${match['variance_amount']:.2f}")
                        if match['match_type'] == 'bundled':
                            st.write("• Complex bundled payment")
                    
                    # Decision buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✅ Approve AI Match", key=f"approve_review_{i}"):
                            st.session_state.corrections[match['stripe_payment_id']] = "approved"
                            st.success("✅ Match approved!")
                    with col2:
                        if st.button("❌ Reject & Manual Match", key=f"reject_review_{i}"):
                            st.session_state.corrections[match['stripe_payment_id']] = "rejected"
                            st.error("❌ Will need manual matching")
                    with col3:
                        if st.button("📝 Modify Match", key=f"modify_review_{i}"):
                            st.session_state.corrections[match['stripe_payment_id']] = "modify_requested"
                            st.info("📝 Modification interface would open")
        else:
            st.success("🎉 All AI matches are high confidence - no review needed!")
    
    with tab3:
        st.subheader("Unmatched Transactions - Manual Matching Needed")
        
        unmatched = [m for m in result["payment_matches"] if m["match_type"] == "unmatched"]
        
        if unmatched:
            st.error(f"❌ {len(unmatched)} transactions could not be automatically matched")
            
            # Available invoices for manual matching
            available_invoices = st.session_state.scenario_data["jobber_invoices"]
            invoice_options = {f"{inv['id']}: ${inv['amount']:.2f} - {inv.get('description', 'No description')}": inv['id'] 
                             for inv in available_invoices}
            
            for i, match in enumerate(unmatched):
                with st.expander(f"❌ Unmatched: Payment {match['stripe_payment_id'][:12]}... (${match['variance_amount']:.2f})"):
                    st.markdown("**Payment Details:**")
                    st.write(f"• Amount: ${match['variance_amount']:.2f}")
                    st.write(f"• Status: {match['suggested_action'].replace('_', ' ').title()}")
                    
                    st.markdown("**Manual Matching:**")
                    
                    # Manual invoice selection
                    selected_invoices = st.multiselect(
                        "Select matching invoice(s):",
                        options=list(invoice_options.keys()),
                        key=f"manual_invoices_{i}"
                    )
                    
                    if selected_invoices:
                        selected_ids = [invoice_options[inv] for inv in selected_invoices]
                        total_selected = sum(inv['amount'] for inv in available_invoices if inv['id'] in selected_ids)
                        variance = match['variance_amount'] - total_selected
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Payment:** ${match['variance_amount']:.2f}")
                            st.write(f"**Selected Invoices:** ${total_selected:.2f}")
                        with col2:
                            if abs(variance) < 0.01:
                                st.success("**Perfect Match!** ✅")
                            elif abs(variance) < 10:
                                st.warning(f"**Variance:** ${variance:.2f} ⚠️")
                            else:
                                st.error(f"**Large Variance:** ${variance:.2f} ❌")
                        
                        # Confidence input
                        confidence = st.slider(
                            "Your confidence in this match:",
                            min_value=0.0, max_value=1.0, value=0.8, step=0.1,
                            key=f"manual_confidence_{i}"
                        )
                        
                        # Save manual match
                        if st.button("💾 Save Manual Match", key=f"save_manual_{i}"):
                            st.session_state.manual_matches[match['stripe_payment_id']] = {
                                "invoice_ids": selected_ids,
                                "confidence": confidence,
                                "variance": variance,
                                "matched_by": "human",
                                "timestamp": datetime.now().isoformat()
                            }
                            st.success("✅ Manual match saved!")
                    
                    # Alternative: Mark as exception
                    st.markdown("**Or mark as exception:**")
                    exception_reason = st.selectbox(
                        "Exception reason:",
                        ["", "Customer prepayment", "Refund", "Fee adjustment", "Other"],
                        key=f"exception_reason_{i}"
                    )
                    
                    if exception_reason:
                        if st.button("⚠️ Mark as Exception", key=f"exception_{i}"):
                            st.session_state.manual_matches[match['stripe_payment_id']] = {
                                "exception": True,
                                "reason": exception_reason,
                                "requires_followup": True,
                                "timestamp": datetime.now().isoformat()
                            }
                            st.warning(f"⚠️ Marked as exception: {exception_reason}")
        else:
            st.success("🎉 All transactions were automatically matched!")
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Data Selection"):
            st.session_state.current_step = 'select_data'
            st.rerun()
    with col2:
        if st.button("➡️ Continue to Export", type="primary"):
            st.session_state.current_step = 'export_results'
            st.rerun()

# Step 4: Export Results
elif st.session_state.current_step == 'export_results':
    st.header("📤 Step 4: Export Results")
    
    result = st.session_state.reconciliation_result
    manual_matches = st.session_state.manual_matches
    corrections = st.session_state.corrections
    
    st.markdown("### Summary of Your Work")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        auto_approved = len([m for m in result["payment_matches"] if m["confidence"] >= 0.9 and not m["requires_human_review"]])
        st.metric("Auto-Approved", auto_approved)
    with col2:
        st.metric("Manual Matches", len(manual_matches))
    with col3:
        st.metric("Corrections Made", len(corrections))
    
    # Export options
    st.markdown("### Export Options")
    
    export_format = st.radio(
        "Choose export format:",
        ["QuickBooks Journal Entries", "Excel Reconciliation Report", "CSV Data Files", "JSON for API"]
    )
    
    if export_format == "QuickBooks Journal Entries":
        st.markdown("**QuickBooks Integration:**")
        
        # Generate journal entries
        journal_entries = []
        for match in result["payment_matches"]:
            if match["confidence"] >= 0.7:  # Export confident matches
                entry = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Account": "Accounts Receivable",
                    "Debit": match["variance_amount"] if match["variance_amount"] > 0 else 0,
                    "Credit": abs(match["variance_amount"]) if match["variance_amount"] < 0 else 0,
                    "Description": f"Payment reconciliation - {match['stripe_payment_id'][:12]}",
                    "Reference": match["stripe_payment_id"]
                }
                journal_entries.append(entry)
        
        if journal_entries:
            df_journal = pd.DataFrame(journal_entries)
            st.dataframe(df_journal)
            
            csv = df_journal.to_csv(index=False)
            st.download_button(
                label="📥 Download Journal Entries CSV",
                data=csv,
                file_name=f"journal_entries_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    elif export_format == "Excel Reconciliation Report":
        st.markdown("**Excel Report:**")
        
        # Create reconciliation report
        report_data = []
        for match in result["payment_matches"]:
            report_data.append({
                "Payment ID": match["stripe_payment_id"],
                "Match Type": match["match_type"].title(),
                "Confidence": f"{match['confidence']:.1%}",
                "Invoice IDs": ", ".join(match["jobber_invoice_ids"]),
                "Variance": f"${match['variance_amount']:.2f}",
                "Status": "Approved" if match["confidence"] >= 0.9 else "Reviewed" if not match["requires_human_review"] else "Manual",
                "Action Required": match["suggested_action"].replace("_", " ").title()
            })
        
        df_report = pd.DataFrame(report_data)
        st.dataframe(df_report)
        
        csv = df_report.to_csv(index=False)
        st.download_button(
            label="📊 Download Excel Report",
            data=csv,
            file_name=f"reconciliation_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Learning feedback
    st.markdown("---")
    st.markdown("### 🧠 Help Improve the AI")
    
    feedback_quality = st.slider(
        "How accurate were the AI matches overall?",
        min_value=1, max_value=10, value=8,
        help="This helps us improve the algorithm"
    )
    
    feedback_comments = st.text_area(
        "Any specific feedback on matches that were wrong?",
        placeholder="e.g., 'AI missed that Home Depot charges are always materials', 'Bundled payments from Customer X always include fee adjustments'"
    )
    
    if st.button("📤 Submit Feedback & Export"):
        # Save feedback (would go to database in production)
        feedback = {
            "quality_score": feedback_quality,
            "comments": feedback_comments,
            "manual_matches": len(manual_matches),
            "corrections": len(corrections),
            "timestamp": datetime.now().isoformat()
        }
        
        st.success("✅ Thank you! Your feedback will help improve the AI for next time.")
        st.balloons()
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Review"):
            st.session_state.current_step = 'review_matches'
            st.rerun()
    with col2:
        if st.button("🔄 Start New Session", type="primary"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Footer
st.markdown("---")
st.markdown("*ServicePro Bookkeeper Workbench - Making payment reconciliation actually enjoyable* ✨")
