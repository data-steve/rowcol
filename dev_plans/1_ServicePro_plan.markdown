# BookClose Development Plan: Service Pro Bookkeeping MVP & Mature Phases

**Checksum**: 9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5

## Overview
- **Goal**: Build a sellable MVP in 4-6 weeks (~90-110h solo) for Service Pro SMBs ($2M–$10M, construction/HVAC/plumbing), targeting Jobber/QBO marketplaces and direct-to-bookkeeper sales. Automate 70-80% of job-cost matching (deposits, expenses, reimbursements) with Jobber/Stripe/QBO integrations for **Tier 1** (Bundled AR Deposit Reconciliation, Uncat-style Expense Categorization) and **Tier 2** (Job-Cost Reporting, Expense/PO → Job Matching, Payroll → Job Sync, Field Reimbursements). Validate with 1-2 beta clients ($99–$199/mo) in Q4 2025. Mature phases add pre-close validation, audit logging, and schema prep for future platforms.
- **Scope**: Prioritize Tier 1 (Jobber invoices/payments, Stripe charges/payouts, QBO deposits/expenses) and Tier 2 (timesheets, expense-to-job mapping). Use mostly abstract schema (`Integration`, `Transaction`, `Job`) for extensibility to future CRMs (Housecall Pro, ServiceTitan, Salesforce, ServiceM8, Zoho CRM) and payments (JobberPay, Square). Defer full integrations to Q1 2026 (post-MVP).
- **GTM Wedge**: Free “Job-Cost Shadow Scan” (read-only QBO/Jobber dashboard via Streamlit) to hook clients, upselling $99/mo (basic, <50 docs/mo) or $199/mo (advanced, 50-200 docs/mo with human review).
- **Tech Stack**: Python, FastAPI, SQLAlchemy (SQLite dev, Postgres prod), Streamlit, QBO API, Jobber GraphQL API, Stripe API, Tesseract (OCR), pandas, Pydantic, Pytest, Redis (audit logs, queues).
- **Design Principles**:
  - **Extensible Schema**: `Integration`, `Transaction`, `Job` models with `platform`, `platform_txn_id`, `metadata` fields support Jobber/Stripe/QBO and 80-90% of future platforms (Housecall Pro, ServiceTitan, etc.). Plan lightweight refactor (~10h) post-MVP for complex CRMs (e.g., Salesforce).
  - **Real APIs**: Use QBO/Jobber/Stripe sandboxes for ingestion, CSV/OCR for non-API data.
  - **HITL (Uncat-style)**: Prompt owners via Streamlit/email for low-confidence matches (<0.9).
  - **Guardrails**: Read-only APIs, KMS encryption, Redis audit logs, handle voids/lags (±$0.01, ±3 days).
  - **Lean UI**: Streamlit for MVP (`job_cost_dashboard.py`), defer React for production.
- **Validation Plan**: Q4 2025, 1-2 SC clients (3-5 jobs each), validating 70%+ match rate, <20% overrides.
- **Pricing**: Free Shadow Scan, $99/mo (basic, <50 docs/mo), $199/mo (advanced, 50-200 docs/mo, human review).
- **KPIs**: Auto-matched % (70-80%), override rate (<20%), doc processing time (<5s/doc), report generation time (<10 mins).

### Clarification: Revenue Recognition vs Bundled AR Reconciliation
- We explicitly prioritize **Bundled AR Deposit Reconciliation** for ServicePro MVP. Revenue Recognition (RevRec) is out-of-scope for MVP and should not block AR automation.
- Bundled AR Recon objective: Given Jobber invoices and Stripe lump-sum deposits (with fees and timing differences), match deposits to one or more invoices using date windows and fee-aware tolerance, producing high-confidence matches and HITL for low-confidence cases.
- RevRec objective (future): Determine when to recognize revenue independent of cash timing (percentage of completion, milestones, deferrals/accruals). Useful for advisors, but separate from AR matching.

## MVP Phase (4-6 Weeks, ~90-110h)
Focus on Tier 1 (Bundled AR Deposit Reconciliation, Uncat-style Expense Categorization) and Tier 2 (Job-Cost Reporting, Expense/PO → Job Matching, Payroll → Job Sync, Field Reimbursements) with Jobber/Stripe/QBO integrations. Build a mostly abstract schema for future extensibility.

### Stage 0: Core Automation with Jobber/Stripe/QBO (Tier 1)
*Goal*: Ingest Jobber/Stripe/QBO data, match lump-sum deposits, categorize expenses (70-80%), flag for Uncat-style HITL review, normalize vendors (USASpending/SAM.gov), output demo dashboard. *Effort: ~40h*
- **Models**:
  - **[X] Existing**: `Rule`, `VendorCanonical`, `Correction`, `Suggestion`, `PolicyProfile`, `Document`, `DocumentType`, `Firm`, `Client`, `Task`.
  - **[X] New**: `Integration` (`integration_id`, `tenant_id`, `client_id`, `platform` [qbo, jobber, stripe, servicetitan, housecallpro, salesforce, servicem8, zoho], `access_token`, `refresh_token`, `expires_at`, `account_id`, `status`, `metadata`). *Effort: 2h*.
  - **[X] New**: `Transaction` (`txn_id`, `tenant_id`, `client_id`, `integration_id`, `platform_txn_id`, `type` [deposit, expense, reimbursement, payroll], `amount`, `date`, `vendor_id`, `job_id`, `confidence`, `status` [matched, unmatched, flagged], `metadata`). *Effort: 2h*.
  - **[X] New**: `Job` (`job_id`, `tenant_id`, `client_id`, `integration_id`, `platform_job_id`, `name`, `status`, `start_date`, `end_date`, `metadata`). *Effort: 2h*.
- **Services**:
  - **[X] DataIngestionService**: Ingest QBO transactions, COA, vendors, projects; Jobber jobs, customers, invoices, payments; Stripe charges, payouts. Handle CSVs (`bank_template.csv`, `vendor_template.csv`, `payroll_template.csv`). Supports voids, lags (±$0.01, ±3 days).
    - [X] Jobber API: Pull `invoices`, `payments` (lump-sum deposits) via GraphQL. Map `invoice_id` to `Transaction.platform_txn_id`. *Effort: 5h*.
    - [X] Stripe API: Pull `charges`, `payouts`. Map `charge_id`/`payout_id` to `Transaction.platform_txn_id`. *Effort: 5h*.
    - [X] Deposit Reconciliation: Match Jobber/Stripe lump-sum deposits to QBO deposits using `match_payout_to_invoices` (14-day window, 0.01 tolerance). Store results in `Transaction` (confidence, status). Flag <0.9 for HITL. *Effort: 6h*.
  - **[X] PolicyEngineService**: Categorize transactions (vendor prior 0.4, MCC 0.2, amount 0.2, history 0.1). Use `score_expense_to_job` heuristics (memo 0.6, job name 0.2, date proximity 0.3, vendor hints 0.1, threshold 0.65).
    - [X] Service Pro Rules: Map "Home Depot" → "Materials", "fuel" → "Reimbursements". Flag <0.9 for HITL. *Effort: 4h*.
    - [ ] **NEW**: Vendor Normalization & Data-Driven Categorization: Download USASpending/SAM.gov procurement data, extract vendor patterns and NAICS-based categorization rules. Build canonical vendor master and industry-specific classifiers. Test against real-world data for accuracy boost. *Effort: 12h*.
  - **[X] DocumentManagementService**: Process receipts via Tesseract OCR, CSVs. Link to `Transaction`.
    - [ ] Enhance OCR: Extract job codes, crew IDs (regex: “Job #\d+”). *Effort: 3h*.
  - **[X] DocumentReviewService**: Queue low-confidence transactions for review.
    - [ ] Uncat-style HITL: Streamlit/email prompts for owner job code confirmation. Learn from corrections via `Correction` model. *Effort: 4h*.
- **Routes**:
  - **[X] Existing**: `/api/ingest/qbo`, `/api/automation/categorize`, `/api/documents/upload`, `/api/review/documents`.
  - [ ] New: `/api/ingest/jobber` (POST), `/api/ingest/stripe` (POST) for jobs, payments. *Effort: 3h*.
  - [ ] New: `/api/jobs/list` (GET) for QBO/Jobber jobs. *Effort: 2h*.
- **Webhooks**:
  - [ ] New: `/webhooks/jobber` (POST): Handle `invoice.created`, `payment.created`. *Effort: 2h*.
  - [ ] New: `/webhooks/stripe` (POST): Handle `charge.succeeded`, `payout.created`. *Effort: 2h*.
- **Template**:
  - [ ] `job_cost_dashboard.py` (Streamlit): Table (date, vendor, amount, job code, confidence), flagged exceptions, Match % (70-80%), Uncat-style HITL prompts (“Assign EXP-1 to Job #123?”). *Effort: 10h*.
- **Tests**:
  - [X] Realistic Test Data Generation: Created complex scenarios with period mismatches, bundled deposits, shared expenses, and revenue recognition complexity. *Effort: 3h*.
  - [ ] Update `test_routes.py`: Test Jobber (`invoice.create`, `payment.create`), Stripe (`charge.succeeded`, `payout.created`), deposit matching, expense categorization. Use sandbox data (50 clients, 10 jobs, 20 invoices, 5 payments, 20 expenses). Goal: 70% auto-matched, <20% overrides. *Effort: 8h*.
  - [ ] Extend `test_setup_sandboxes.py`: Seed Jobber (50 clients, 10 jobs, 20 invoices, 5 payments, 20 expenses), Stripe (50 charges, 10 payouts). *Effort: 2h*.
- **Docs**:
  - [ ] Update README: Jobber/Stripe setup, Uncat HITL, Service Pro rules, USASpending/SAM.gov. *Effort: 2h*.
- **Extensibility**:
  - Schema (`Integration`, `Transaction`, `Job`) uses `platform`, `platform_txn_id`, `metadata` fields for Housecall Pro, ServiceTitan, Salesforce, ServiceM8, Zoho CRM, JobberPay, Square. Refactor post-MVP for complex mappings (e.g., Salesforce `Invoice__c`).
  - `DataIngestionService` abstracts API calls (`fetch_platform_data(platform, credentials)`), reusable for new platforms.
- **KPIs**: Auto-matched % (70-80%), override rate (<20%), doc processing time (<5s/doc).

### Uncat-Style Categorization & Vendor Normalization (Detailed Requirements)
**Goal**: Automate 70-80% of expense categorization with clear, reviewable rules and learning from corrections.

- **Inputs**:
  - QBO expenses and bank transactions (description, amount, date, vendor, memo)
  - Canonical vendor master and categories (seeded in `data/seed_data.sql`)
  - External sources (USASpending/SAM.gov, NAICS) for vendor patterns (future enhancement)

- **Rules & Signals (weights target)**:
  - Vendor canonical match (0.40)
  - MCC/NAICS and vendor patterns (0.20)
  - Amount and historical category frequency (0.20)
  - Date/text proximity to jobs (0.10)
  - Memo patterns (0.10)
  - Threshold: ≥0.65 suggest; ≥0.90 auto-apply; below threshold → HITL

- **Vendor Normalization**:
  - Normalize raw vendor strings to canonical vendors and default GL accounts
  - Examples: "Home Depot" → Materials; fuel patterns → Reimbursements; insurance → Insurance & Permits
  - Maintain confidence and provenance; rules data-driven from seed + learned corrections

- **Learning from Corrections**:
  - Every human correction generates a runtime rule (scoped to firm/client) with idempotent storage
  - Conflict resolution by priority and specificity; audit trail retained

- **Outputs**:
  - Suggestion payload with `top_k`, confidence, selected account, rationale
  - HITL queue entries for <0.90 confidence

### HITL “Cockpit” UX for Bookkeepers (Workflow Spec)
**Goal**: Minimize handle-time for cleanup; accelerate to analysis.

- **Core Views**:
  - Reconciliation queue: deposits ↔ invoices matches with confidence, fee allocation preview, approve/review actions
  - Categorization queue: expense rows with suggested account, confidence, vendor, job hints, one-click accept/override
  - Exceptions view: unmatched deposits/expenses, aging, reason codes

- **Interactions**:
  - Keyboard-first triage (J/K to navigate, A to approve, R to route to review)
  - Inline edits (GL account, job tag), sticky idempotency
  - Bulk actions for repeated vendors/time windows

- **Guidance & Rationale**:
  - Explain match: show components (date diff, amount variance, vendor match, prior history)
  - Confidence bars, fee allocation details, bundled composition

- **Guardrails**:
  - Everything preview-first; commits require explicit confirm and audit log
  - Multi-tenant isolation by `firm_id`/`client_id`

### Stage 1: Job-Cost Reporting & Sync (Tier 2)
*Goal*: Generate job-cost reports (labor, materials, reimbursements) and sync payroll/timesheets to jobs. Output mock QBO payloads. *Effort: ~20h*
- **Models**:
  - **[X] Existing**: `Job`, `Transaction`, `Rule`, `Correction`.
  - [ ] New: `JobCostReport` (`report_id`, `tenant_id`, `client_id`, `period`, `jobs[{job_id, total_cost, labor_cost, material_cost, reimbursement_cost, unmatched}]`, `status`). *Effort: 2h*.
- **Services**:
  - **[X] DataIngestionService**:
    - [ ] Ingest QBO payroll or CSVs (`payroll_template.csv`). Map crew hours to `Job` using `build_qbo_timeactivity`. *Effort: 3h*.
  - **[X] PolicyEngineService**:
    - [ ] Map payroll/reimbursements to `Job` using crew IDs, job codes (`score_expense_to_job` heuristics). *Effort: 3h*.
  - [ ] New: `ReportService`: Generate PDF/Excel reports (Jinja2) with matched transactions (labor, materials, reimbursements), unmatched flags, mock QBO TimeActivity payloads (`build_qbo_timeactivity`). *Effort: 5h*.
- **Routes**:
  - [ ] New: `/api/reports/job-cost` (POST): Compile report, return URL. *Effort: 2h*.
- **Template**:
  - [ ] Update `job_cost_dashboard.py`: Add job-cost tab (labor, materials, reimbursements), “Download Report” button. *Effort: 3h*.
- **Tests**:
  - [ ] Update `test_routes.py`: Test payroll sync, job-cost reports. Goal: 70% payroll/reimbursement match rate, <20% overrides. *Effort: 3h*.
- **Docs**:
  - [ ] Update README: Job-cost reporting, payroll sync. *Effort: 2h*.
- **KPIs**: Report generation time (<10 mins), match rate (70-80%), override rate (<20%).

## Mature Phase (~50h)
Enhance MVP with pre-close validation and audit logging to ensure reliability and scalability for beta clients.

### Stage 2: Pre-Close Validation & Escalation
*Goal*: Run pre-close checks, classify tier 1 vs. tier 2 issues, bundle evidence for controller handoff, support Uncat-style HITL. *Effort: ~25h*
- **Models**:
  - **[X] Existing**: `PreCloseCheck`, `Exception`, `PBCRequest`, `Task`.
  - [ ] New: `EscalationPackage` (`package_id`, `tenant_id`, `client_id`, `exception_id`, `docs`, `notes`, `status`). *Effort: 2h*.
  - [ ] New: `IntegrityIssue` (`issue_id`, `tenant_id`, `client_id`, `type` [recon, cutoff, coverage, variance], `description`, `tier` [1, 2], `evidence_refs`). *Effort: 2h*.
- **Services**:
  - **[X] PreCloseService**: Check missing receipts, unmatched transactions (>500 not tied to jobs).
    - [ ] Add checks for Jobber/Stripe deposits, unmatched expenses/reimbursements. *Effort: 3h*.
  - **[X] PBCTrackerService**: Track missing docs, assign tasks.
    - [ ] Extend for Uncat-style HITL: Owner prompts for job code confirmation. *Effort: 3h*.
  - [ ] New: `TierClassificationService`: Classify issues (tier 1: missing doc, mislabel; tier 2: complex recon). *Effort: 3h*.
  - [ ] New: `EvidencePackagingService`: Bundle transactions, docs, notes for tier 2 handoff. *Effort: 3h*.
- **Routes**:
  - **[X] Existing**: `/api/preclose/checks`, `/api/preclose/pbc`.
  - [ ] New: `/api/escalations/tier2` (POST): Controller handoff. *Effort: 2h*.
- **Template**:
  - [ ] Update `job_cost_dashboard.py`: Add tabs for exceptions, PBC status, tier 1/2 issues. *Effort: 4h*.
- **Tests**:
  - [ ] Update `test_routes.py`: Test tier classification, HITL, escalations. Goal: 90% check pass rate, <5% false positives. *Effort: 3h*.
- **Docs**:
  - [ ] Update README: Pre-close checks, Uncat HITL, escalation. *Effort: 2h*.
- **KPIs**: PBC items on time (90%), exception resolution time (<24h), tier 2 escalation rate (<10%).

### Stage 3: Audit Logging
*Goal*: Log all mutation operations (deposits, expenses, payroll, job-costing). *Effort: ~15h*
- **Models**:
  - **[X] AuditLog** (`log_id`, `firm_id`, `client_id`, `user_id`, `operation`, `entity_type`, `entity_id`, `changes`, `timestamp`).
    - [ ] Extend for Jobber/Stripe transactions, job-cost mutations. *Effort: 1h*.
- **Services**:
  - **[X] AuditLogService**: Log mutations, retrieve/filter logs.
    - [ ] Integrate with Jobber/Stripe ingestion, job-cost services. *Effort: 3h*.
- **Routes**:
  - **[X] /api/audit/logs** (GET, POST).
    - [ ] Add filters for Jobber/Stripe entities. *Effort: 1h*.
- **Template**:
  - [ ] Port `audit_log_queue.html` to `audit_log_queue.py` (Streamlit). *Effort: 3h*.
- **Tests**:
  - [ ] Update `test_routes.py`: Test Jobber/Stripe logs. *Effort: 3h*.
- **Docs**:
  - [ ] Update README: Jobber/Stripe audit logs. *Effort: 1h*.
- **KPIs**: Log completeness (100%), retrieval time (<1s), filter accuracy (100%).

## Validation Plan (Q4 2025, ~20h)
- **Week 1: Sandbox & Data (20h)**:
  - Set up QBO/Jobber/Stripe sandboxes (Intuit Developer, Jobber OAuth, Stripe test keys). *Effort: 5h*.
  - Update `DataIngestionService` for APIs, pull USASpending/SAM.gov vendors. *Effort: 10h*.
  - Run `test_routes.py`, `test_setup_sandboxes.py` (90% pass rate). *Effort: 5h*.
- **Weeks 2-3: Dashboard & Enhancements (35h)**:
  - Build `job_cost_dashboard.py`: Transactions, Uncat HITL, job-cost tab, exceptions, KPIs. *Effort: 10h*.
  - Enhance `PolicyEngineService` (Service Pro rules, `score_expense_to_job`), `DocumentManagementService` (OCR for job codes). *Effort: 15h*.
  - Test with sandbox + CSVs (100 receipts, 20 expenses, 10 timesheets). Goal: 70% match rate, <20% overrides. *Effort: 10h*.
- **Weeks 4-5: Pilot & Escalation (25h)**:
  - Source 1 test client (Upwork, $200 for QBO/Jobber data). Run ingestion, categorization, reports. *Effort: 8h*.
  - Test Uncat HITL, tier classification, escalations. *Effort: 7h*.
  - Outreach: Email 10 SC contractors (Home Builders Association) for Shadow Scan demos. *Effort: 10h*.
- **Week 6: Beta & Polish (20h)**:
  - Polish `job_cost_dashboard.py` (Chart.js visuals). *Effort: 5h*.
  - Integrate audit logging for Jobber/Stripe. *Effort: 5h*.
  - Land 1-2 betas ($99–$199/mo). *Effort: 10h*.

## Requirements for Prioritized Features
1. **Bundled AR Deposit Reconciliation (Tier 1)**:
   - **Need**: Match Jobber/Stripe lump-sum deposits to QBO without itemized line-outs.
   - **Solution**: `DataIngestionService` pulls Jobber `invoices`, `payments`, Stripe `charges`, `payouts`. `PolicyEngineService` uses `match_payout_to_invoices` (14-day window, 0.01 tolerance). Flag <0.9 for Uncat HITL. *Effort: 16h (Stage 0)*.
   - **KPIs**: Deposits matched (70-80%), override rate (<20%).
2. **Uncat-style Expense Categorization (Tier 1)**:
   - **Need**: Auto-categorize expenses from QBO uncategorized account, prompt owners for low-confidence matches.
   - **Solution**: `PolicyEngineService` uses `score_expense_to_job` (vendor 0.4, MCC 0.2, amount 0.2, history 0.1, memo 0.6, date proximity 0.3, vendor hints 0.1, threshold 0.65). `DocumentReviewService` prompts via Streamlit/email. *Effort: 11h (Stage 0)*.
   - **KPIs**: Expenses matched (70-80%), override rate (<20%), response time (<24h).
3. **Job-Cost Reporting (Tier 2)**:
   - **Need**: Per-job profitability (labor, materials, reimbursements).
   - **Solution**: `ReportService` generates PDF/Excel reports with matched transactions, unmatched flags, mock TimeActivity payloads (`build_qbo_timeactivity`). *Effort: 8h (Stage 1)*.
   - **KPIs**: Report generation time (<10 mins), accuracy (70-80%).
4. **Expense/PO → Job Matching (Tier 2)**:
   - **Need**: Tag Home Depot runs, subcontractor invoices to jobs.
   - **Solution**: `PolicyEngineService` uses `score_expense_to_job`. `DocumentManagementService` extracts job codes via OCR. Flag <0.9 for HITL. *Effort: 7h (Stage 0-1)*.
   - **KPIs**: Expenses matched (70-80%), override rate (<20%).
5. **Payroll → Job Sync (Tier 2)**:
   - **Need**: Match crew hours to jobs.
   - **Solution**: `DataIngestionService` ingests QBO payroll or CSVs. `PolicyEngineService` maps to `Job` using `build_qbo_timeactivity`. *Effort: 7h (Stage 1)*.
   - **KPIs**: Payroll matched (70-80%), override rate (<20%).
6. **Field Reimbursements (Tier 2)**:
   - **Need**: Log fuel, supplies to jobs.
   - **Solution**: `DocumentManagementService` processes reimbursement receipts (OCR for job codes). `PolicyEngineService` matches to `Job`. *Effort: 5h (Stage 0)*.
   - **KPIs**: Reimbursements matched (70-80%), override rate (<20%).

## Effort Summary
- **Total**: ~90-110h (~4-6 weeks solo, faster with Upwork SWE/bookkeeper).
- **Breakdown**:
  - Stage 0 (Tier 1): 40h
  - Stage 1 (Tier 2): 20h
  - Stage 2 (Pre-Close): 25h
  - Stage 3 (Audit): 15h
  - Validation: 20h
- **Team**: You (backend, APIs), Upwork SWE (0.5, frontend/tests, $30/hr), Upwork bookkeeper (0.5, reviews, $20-40/hr).
- **Pilot**: Q4 2025, 1-2 SC clients (3-5 jobs each).

## Guardrails
- **Security**: KMS encryption for tokens, PII restricted, Redis audit logs, SHA-256 document hashes.
- **Edge Cases**: Handle multi-currency (QBO ExchangeRate), voids (soft-delete), locked books (CompanyInfo), lags (±$0.01, ±3 days), OCR errors (low-confidence flags).
- **Scalability**: Multi-tenant models (`firm_id`, `client_id`), abstract API calls, task routing by role.
- **Constraints**: No payroll processing, no tax prep, no ERP integrations in MVP.