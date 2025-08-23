# Proof-of-solvability mini‑lab
# ------------------------------------------------------------
# This notebook demonstrates that the core RowCol (Book:Close) features
# are algorithmically straightforward and API‑first feasible.
#
# We simulate data and show:
# 1) Lumped payout -> invoice split (deposit reconciliation) with confidence scoring
# 2) QBO payload construction (Deposit + Fee Expense)
# 3) Expense -> Job mapping heuristics with scores + exceptions queue
# 4) Timesheet -> QBO TimeActivity mapping (Jobber-ish -> QBO payload)
# 5) Deferred revenue schedule generator (prepaid -> monthly recognition)
#
# NOTE: This is runtime Python intended to *demonstrate mechanics*.
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import date, timedelta
from collections import defaultdict
import itertools
import math
import json

# -------------------------------
# Data models (simplified)
# -------------------------------
@dataclass
class Invoice:
    id: str
    job_id: Optional[str]
    amount: float
    issued: date
    closed: bool = False

@dataclass
class Payment:
    id: str
    invoice_id: Optional[str]
    amount: float
    paid: date
    method: str = "card"

@dataclass
class Payout:
    id: str
    gross: float
    fee: float
    net: float
    paid: date

@dataclass
class Expense:
    id: str
    vendor: str
    amount: float
    spend_date: date
    memo: str = ""

@dataclass
class Job:
    id: str
    name: str
    address: str
    scheduled: date

@dataclass
class TimesheetEntry:
    tech_id: str
    job_id: str
    start: date
    hours: float

# -------------------------------
# 1) Deposit reconciliation: split payout across invoices
# -------------------------------

def match_payout_to_invoices(payout: Payout, invoices: List[Invoice], window_days: int = 14, tol: float = 0.01):
    """
    Greedy + search hybrid: find a subset of invoice amounts whose sum ~= payout.gross
    within tolerance (handles tips/refunds via fee/net offsets separately).
    Returns best candidate set + confidence score.
    """
    # Filter invoices near the payout date (simple, realistic heuristic)
    candidates = [inv for inv in invoices if abs((payout.paid - inv.issued).days) <= window_days and not inv.closed]
    amounts = [round(inv.amount, 2) for inv in candidates]

    target = round(payout.gross, 2)

    # Exact subset sum via DP limited by number of candidates (kept small by date window)
    best_subset = None
    best_diff = float("inf")

    # small search: try combinations up to size 7 to keep it quick
    max_k = min(7, len(amounts))
    for k in range(1, max_k + 1):
        for combo in itertools.combinations(range(len(amounts)), k):
            s = round(sum(amounts[i] for i in combo), 2)
            diff = abs(s - target)
            if diff < best_diff:
                best_diff = diff
                best_subset = combo
                if diff <= tol:
                    break
        if best_diff <= tol:
            break

    if best_subset is None:
        # fallback: single closest invoice (rare)
        closest_idx = min(range(len(amounts)), key=lambda i: abs(amounts[i] - target)) if amounts else None
        subset_ids = [candidates[closest_idx].id] if closest_idx is not None else []
        diff = abs((amounts[closest_idx] if closest_idx is not None else 0) - target)
    else:
        subset_ids = [candidates[i].id for i in best_subset]
        diff = best_diff

    # Confidence: closer sum + fewer invoices => higher confidence
    size_penalty = 0.03 * (len(subset_ids) - 1)  # 3% per extra split beyond one
    closeness = max(0.0, 1.0 - (diff / max(1.0, target)))  # normalized closeness
    confidence = max(0.0, min(1.0, closeness - size_penalty))

    return {
        "payout_id": payout.id,
        "matched_invoices": subset_ids,
        "sum_matched": round(sum(inv.amount for inv in invoices if inv.id in subset_ids), 2),
        "target_gross": target,
        "fee": payout.fee,
        "net": payout.net,
        "diff": round(diff, 2),
        "confidence": round(confidence, 3)
    }

# -------------------------------
# 2) QBO payload builders (shape only)
# -------------------------------

def build_qbo_deposit_payload(bank_account_ref: str, undeposited_funds_ref: str, match_result: dict):
    """
    Shapes a minimalistic QBO Deposit object: line items referencing Undeposited Funds,
    and an Expense line for fees (alternatively a JournalEntry could be used).
    """
    lines = []
    for inv_id in match_result["matched_invoices"]:
        lines.append({
            "DetailType": "DepositLineDetail",
            "Amount": None,  # Usually the payment receipt amounts (could fetch Payment objects)
            "DepositLineDetail": {
                "AccountRef": {"value": undeposited_funds_ref},
                "Entity": {"type": "Invoice", "value": inv_id}
            }
        })

    payload = {
        "TxnDate": str(date.today()),
        "DepositToAccountRef": {"value": bank_account_ref},
        "Line": lines,
        "_meta": {"explain": "In production: populate Amount per invoice payment; fee posted as separate Expense or JE."}
    }
    return payload

def build_qbo_fee_expense_payload(bank_fee_account_ref: str, payout: Payout):
    return {
        "TxnDate": str(payout.paid),
        "AccountRef": {"value": bank_fee_account_ref},
        "PrivateNote": f"Processor fee for payout {payout.id}",
        "Line": [{
            "DetailType": "AccountBasedExpenseLineDetail",
            "Amount": round(payout.fee, 2),
            "AccountBasedExpenseLineDetail": {
                "AccountRef": {"value": bank_fee_account_ref}
            }
        }]
    }

# -------------------------------
# 3) Expense -> Job mapping heuristics (+ exceptions queue)
# -------------------------------

def score_expense_to_job(exp: Expense, job: Job) -> float:
    score = 0.0
    # Heuristic 1: memo includes job id or name token
    if exp.memo and job.id in exp.memo:
        score += 0.6
    if exp.memo and any(tok.lower() in exp.memo.lower() for tok in job.name.split() if len(tok) > 3):
        score += 0.2
    # Heuristic 2: date proximity
    days = abs((exp.spend_date - job.scheduled).days)
    if days <= 1:
        score += 0.3
    elif days <= 3:
        score += 0.15
    # Heuristic 3: vendor hints (toy: materials vendors get small bump)
    materials_vendors = {"home depot", "lowe's", "grainger"}
    if exp.vendor.lower() in materials_vendors:
        score += 0.1
    return min(1.0, score)

def map_expenses_to_jobs(expenses: List[Expense], jobs: List[Job], threshold: float = 0.65):
    mappings = []
    exceptions = []
    for exp in expenses:
        best_job, best_score = None, 0.0
        for job in jobs:
            s = score_expense_to_job(exp, job)
            if s > best_score:
                best_job, best_score = job, s
        if best_job and best_score >= threshold:
            mappings.append({"expense_id": exp.id, "job_id": best_job.id, "score": round(best_score, 3)})
        else:
            exceptions.append({"expense_id": exp.id, "reason": "low_score", "best_score": round(best_score, 3)})
    return mappings, exceptions

# -------------------------------
# 4) Timesheet -> QBO TimeActivity shaping
# -------------------------------

def build_qbo_timeactivity(entry: TimesheetEntry, qbo_employee_ref: str) -> Dict:
    return {
        "TxnDate": str(entry.start),
        "NameOf": "Employee",
        "EmployeeRef": {"value": qbo_employee_ref},
        "Hours": int(entry.hours),
        "Minutes": int(round((entry.hours - int(entry.hours)) * 60)),
        "ItemRef": {"value": "LABOR"},  # placeholder service item
        "CustomerRef": {"value": entry.job_id},  # projects/jobs in QBO are sub-customers
        "Description": f"Job {entry.job_id} labor"
    }

# -------------------------------
# 5) Deferred revenue schedule (prepaids -> monthly recognition)
# -------------------------------

def make_deferred_schedule(invoice_id: str, amount: float, start: date, months: int) -> List[Dict]:
    per_month = round(amount / months, 2)
    schedule = []
    for m in range(months):
        recog_date = start + timedelta(days=30*m)  # simplified month step
        schedule.append({
            "invoice_id": invoice_id,
            "recognition_date": str(recog_date),
            "amount": per_month,
            "journal_entry": {
                "debit": {"account": "Deferred Revenue", "amount": per_month},
                "credit": {"account": "Revenue", "amount": per_month}
            }
        })
    # Small residual adjustment to last month due to rounding
    residual = round(amount - per_month*months, 2)
    if residual != 0 and schedule:
        schedule[-1]["amount"] = round(schedule[-1]["amount"] + residual, 2)
        schedule[-1]["journal_entry"]["debit"]["amount"] = schedule[-1]["amount"]
        schedule[-1]["journal_entry"]["credit"]["amount"] = schedule[-1]["amount"]
    return schedule

# -------------------------------
# Demo data + run
# -------------------------------

invoices = [
    Invoice("INV-1001", "JOB-1", 200.00, date(2025, 8, 5)),
    Invoice("INV-1002", "JOB-2", 350.00, date(2025, 8, 7)),
    Invoice("INV-1003", "JOB-3", 149.00, date(2025, 8, 8)),
    Invoice("INV-1004", "JOB-4", 89.00,  date(2025, 8, 8)),
]

payout = Payout(id="PO-555", gross=200+350+149, fee=14.27, net=200+350+149-14.27, paid=date(2025, 8, 9))

match_result = match_payout_to_invoices(payout, invoices)

qbo_deposit = build_qbo_deposit_payload(bank_account_ref="BANK-CHK-001", undeposited_funds_ref="ACCT-UF-001", match_result=match_result)
qbo_fee = build_qbo_fee_expense_payload(bank_fee_account_ref="ACCT-BANK-FEE", payout=payout)

jobs = [
    Job("JOB-1", "HVAC Install Main St", "12 Main St", date(2025, 8, 5)),
    Job("JOB-2", "Duct Cleaning Elm Ave", "99 Elm Ave", date(2025, 8, 6)),
    Job("JOB-3", "AC Repair Oak Rd", "17 Oak Rd", date(2025, 8, 7))
]

expenses = [
    Expense("EXP-1", "Home Depot", 124.33, date(2025, 8, 5), memo="JOB-1 copper pipe + fittings"),
    Expense("EXP-2", "Chevron", 62.10, date(2025, 8, 6), memo="Fuel run for Elm Ave crew"),
    Expense("EXP-3", "Grainger", 311.22, date(2025, 8, 9), memo="misc supplies"),
]

mappings, exceptions = map_expenses_to_jobs(expenses, jobs)

timesheets = [
    TimesheetEntry("TECH-7", "JOB-2", date(2025, 8, 6), hours=3.5),
    TimesheetEntry("TECH-8", "JOB-1", date(2025, 8, 5), hours=6.0),
]
qbo_time_payloads = [build_qbo_timeactivity(t, qbo_employee_ref="EMP-xyz") for t in timesheets]

deferred = make_deferred_schedule("INV-2001", amount=2400.00, start=date(2025, 9, 1), months=12)

demo = {
    "deposit_match": match_result,
    "qbo_deposit_payload": qbo_deposit,
    "qbo_fee_expense_payload": qbo_fee,
    "expense_job_mappings": mappings,
    "exceptions_queue": exceptions,
    "timeactivity_payloads": qbo_time_payloads,
    "deferred_revenue_schedule_preview": deferred[:3] + ["...", deferred[-1]]
}

print(json.dumps(demo, indent=2))
