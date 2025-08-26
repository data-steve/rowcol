import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from domains.core.models.transaction import Transaction
from domains.core.models.job import Job
from database import SessionLocal
import os

st.set_page_config(page_title="Service Pro Bookkeeper Cockpit", layout="wide")

st.title("🛠️ Service Pro Bookkeeper Cockpit")
st.caption("Automate 70–80% of job-cost matching and triage exceptions fast")

# Initialize database session
@st.cache_resource
def get_database():
    return SessionLocal()

db = get_database()

# Sidebar filters
st.sidebar.header("Filters")
firm_id = st.sidebar.text_input("Firm ID", value="tenant_001")
client_id = st.sidebar.text_input("Client ID (optional)", value="")
status_filter = st.sidebar.selectbox("Status", ["All", "matched", "unmatched", "flagged"])

tabs = st.tabs(["Overview", "Reconciliation", "Categorization", "Exceptions", "Jobs"]) 

# Fetch transactions once for all tabs
query = db.query(Transaction)
if firm_id:
    query = query.filter(Transaction.firm_id == firm_id)
if client_id:
    try:
        query = query.filter(Transaction.client_id == int(client_id))
    except ValueError:
        st.sidebar.warning(f"Invalid client ID: {client_id}")
if status_filter != "All":
    query = query.filter(Transaction.status == status_filter)
txns = query.all()

# --- Overview ---
with tabs[0]:
    col1, col2, col3, col4 = st.columns(4)
    total_txns = len(txns)
    matched_txns = len([t for t in txns if t.status == "matched"])
    flagged_txns = len([t for t in txns if t.status == "flagged"])
    match_rate = (matched_txns / total_txns * 100) if total_txns > 0 else 0

    with col1:
        st.metric("Total Transactions", total_txns)
    with col2:
        st.metric("Auto-Matched", matched_txns, f"{match_rate:.1f}%")
    with col3:
        st.metric("Flagged for Review", flagged_txns)
    with col4:
        st.metric("Match Rate", f"{match_rate:.1f}%", delta="70–80% target" if match_rate < 70 else "✅ Target met")

    st.subheader("📊 All Transactions")
    if txns:
        txn_data = [{
            "Date": t.date.strftime("%Y-%m-%d") if t.date else "N/A",
            "Transaction ID": t.txn_id,
            "Type": t.type,
            "Amount": f"${t.amount:.2f}",
            "Job ID": t.job_id or "Unassigned",
            "Confidence": f"{t.confidence:.2f}" if t.confidence else "0.00",
            "Status": t.status,
            "Platform": t.integration_id or "Manual"
        } for t in txns]
        df = pd.DataFrame(txn_data)

        def highlight_status(row):
            if row['Status'] == 'matched':
                return ['background-color: #d4edda'] * len(row)
            elif row['Status'] == 'flagged':
                return ['background-color: #f8d7da'] * len(row)
            else:
                return ['background-color: #fff3cd'] * len(row)
        st.dataframe(df.style.apply(highlight_status, axis=1), use_container_width=True)
    else:
        st.info("No transactions found. Run ingestion or adjust filters.")

# --- Reconciliation queue ---
with tabs[1]:
    st.subheader("💵 Reconciliation Queue (Deposits)")
    deposits = [t for t in txns if t.type == "deposit" and t.status in ("unmatched", "flagged")]
    if not deposits:
        st.info("No deposits require action.")
    else:
        for i, txn in enumerate(deposits[:25]):
            with st.expander(f"Deposit {txn.txn_id} - ${txn.amount:.2f}"):
                st.text(f"Date: {txn.date.strftime('%Y-%m-%d') if txn.date else 'N/A'} | Status: {txn.status} | Confidence: {txn.confidence or 0:.2f}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Accept Auto-Match", key=f"acc_{i}"):
                        txn.status = "matched"
                        txn.confidence = txn.confidence or 0.95
                        db.commit()
                        st.success("Marked as matched.")
                        st.experimental_rerun()
                with c2:
                    jobs = db.query(Job).filter(Job.firm_id == firm_id).all()
                    job_options = ["Unassigned"] + [f"{j.job_id} - {j.name}" for j in jobs]
                    chosen = st.selectbox("Assign to Job (manual)", job_options, key=f"dep_job_{i}")
                    if st.button("💾 Assign", key=f"dep_assign_{i}"):
                        if chosen != "Unassigned":
                            job_id = chosen.split(" - ")[0]
                            txn.job_id = job_id
                            txn.status = "matched"
                            txn.confidence = 1.0
                            db.commit()
                            st.success(f"Assigned to {job_id}")
                            st.experimental_rerun()

# --- Categorization queue ---
with tabs[2]:
    st.subheader("🏷️ Categorization Queue")
    st.caption("Coming soon: Uncat-style triage (GL suggestions, vendor normalization, confidence, one-click accept)")
    # Placeholder: show non-deposit items needing attention
    candidates = [t for t in txns if t.type in ("charge", "payout") and t.status in ("unmatched", "flagged")]
    if not candidates:
        st.info("No items require categorization.")
    else:
        st.write(f"{len(candidates)} items pending categorization preview.")

# --- Exceptions ---
with tabs[3]:
    st.subheader("🚩 Exceptions (Require Human Review)")
    flagged = [t for t in txns if t.status == "flagged"]
    if not flagged:
        st.success("No flagged transactions.")
    else:
        for i, txn in enumerate(flagged[:50]):
            with st.expander(f"Txn {txn.txn_id} - ${txn.amount:.2f}"):
                st.text(f"Type: {txn.type} | Date: {txn.date.strftime('%Y-%m-%d') if txn.date else 'N/A'} | Confidence: {txn.confidence or 0:.2f}")
                jobs = db.query(Job).filter(Job.firm_id == firm_id).all()
                job_options = ["Unassigned"] + [f"{j.job_id} - {j.name}" for j in jobs]
                chosen = st.selectbox("Assign to Job", job_options, key=f"ex_job_{i}")
                if st.button("Resolve", key=f"ex_res_{i}"):
                    if chosen != "Unassigned":
                        job_id = chosen.split(" - ")[0]
                        txn.job_id = job_id
                    txn.status = "matched"
                    txn.confidence = max(txn.confidence or 0.0, 0.9)
                    db.commit()
                    st.success("Exception resolved.")
                    st.experimental_rerun()

# Job summary
with tabs[4]:
    st.subheader("🏗️ Job Cost Summary")
    jobs = db.query(Job).filter(Job.firm_id == firm_id).all()

    if jobs:
        job_summary = []
        for job in jobs:
            job_txns = [t for t in txns if t.job_id == job.job_id]
            total_cost = sum(t.amount for t in job_txns)
            job_summary.append({
                "Job ID": job.job_id,
                "Job Name": job.name,
                "Status": job.status,
                "Total Cost": f"${total_cost:.2f}",
                "Transaction Count": len(job_txns)
            })
        job_df = pd.DataFrame(job_summary)
        st.dataframe(job_df, use_container_width=True)
    else:
        st.info("No jobs found. Run data ingestion to populate job data.")

# Action buttons
st.subheader("⚡ Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Data"):
        st.rerun()

with col2:
    if st.button("📊 Download Report"):
        # TODO: Implement report generation
        st.info("Report generation coming soon!")

with col3:
    if st.button("⚙️ Run Auto-Categorization"):
        # TODO: Integrate with PolicyEngineService
        st.info("Auto-categorization coming soon!")

# Footer
st.markdown("---")
st.markdown("*ServicePro MVP — Bundled AR Matching & HITL Cockpit*")

# Clean up
db.close()

