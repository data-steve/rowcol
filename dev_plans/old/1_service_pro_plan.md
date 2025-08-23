
### Revised Development Plan: Service Pro Bookkeeping MVP with Jobber/Stripe Integrations
**Overview**:
- **Goal**: Build a sellable MVP in 4-6 weeks (~80-100h solo) for Service Pro SMBs, automating 70-80% of job-cost matching (receipts, payroll, reimbursements) with Jobber/Stripe integrations for **Bundled AR Deposit Reconciliation**, plus **Job-Cost Reporting**, **Uncat-style Categorization**, **Expense/PO → Job Matching**, **Payroll → Job Sync**, **Field Reimbursements**, and **Owner KPI Dashboard**. Validate with QBO sandbox and land 1-2 beta clients ($99-$199/mo).
- **Scope**: Focus on Jobber/Stripe for AR deposits, extensible schema for ServiceTitan/HouseCall Pro, QBO for core bookkeeping, Streamlit dashboard for demos, human-in-the-loop (HITL) review for accuracy.
- **GTM Wedge**: Free “Job-Cost Shadow Scan” (read-only QBO/Jobber dashboard via Streamlit) to hook clients, upselling $99-$199/mo hybrid service (AI + Upwork freelancer reviews).
- **Tech Stack**: Python, FastAPI, SQLAlchemy (SQLite dev, Postgres prod), Streamlit, QBO API, Jobber API, Stripe API, Tesseract (OCR), pandas, Pydantic, Pytest, Redis (audit logs).
- **Design Principles**:
  - **Extensible Schema**: Models (`Integration`, `Transaction`, `Job`) support Jobber, Stripe, and future platforms (ServiceTitan, HouseCall Pro, Jobber Pay).
  - **Real APIs**: Integrate QBO/Jobber/Stripe sandbox for ingestion, keep CSV/OCR for non-API data.
  - **HITL**: Uncat-style owner prompts for low-confidence categorizations (<0.9).
  - **Guardrails**: Read-only QBO/Jobber/Stripe (no writes), KMS encryption, Redis audit logs, handle voids/lags.
  - **Lean Demo**: Streamlit for MVP UI, defer React for production.
- **Validation Plan**: Q4 2025, 1-2 SC Service Pro clients, 3-5 jobs each, validating job-cost matching and dashboard delivery.
- **Pricing**: Free Shadow Scan, $99/mo (basic, <50 docs/mo), $199/mo (advanced, 50-200 docs/mo, human review).

### Stage 0: Core Automation with Jobber/Stripe Integrations
*Goal*: Ingest QBO/Jobber/Stripe data, categorize receipts/payroll/reimbursements to jobs (70-80%), flag for review, normalize vendors (USASpending/SAM.gov), output demo dashboard. *Effort: ~30h*
- **Models**:
  - **[X] Existing**: `Rule`, `VendorCanonical`, `Correction`, `Suggestion`, `PolicyProfile`, `Document`, `DocumentType`, `Firm`, `Client`, `Task`.
  - [ ] New: `Integration` (`integration_id`, `tenant_id`, `client_id`, `platform` [qbo, jobber, stripe, servicetitan, housecallpro], `access_token`, `refresh_token`, `expires_at`, `account_id`, `status`) for extensible API connections. *Effort: 2h*.
  - [ ] New: `Transaction` (`txn_id`, `tenant_id`, `client_id`, `integration_id`, `platform_txn_id`, `type` [deposit, expense, payroll, reimbursement], `amount`, `date`, `vendor_id`, `job_id`, `confidence`, `status` [matched, unmatched, flagged]). *Effort: 2h*.
  - [ ] New: `Job` (`job_id`, `tenant_id`, `client_id`, `integration_id`, `platform_job_id`, `name`, `status`, `start_date`, `end_date`). *Effort: 2h*.
- **Services**:
  - **[X] DataIngestionService**: Ingest QBO txns, COA, vendors, projects. Handle CSVs (`bank_template.csv`, `vendor_template.csv`, `payroll_template.csv`). Supports voids, lags (amount ±$0.01, date ±3 days).
    - [ ] Add Jobber API: Pull jobs, customers, invoices, payments (lump-sum deposits). Map Jobber `invoice_id` to `Transaction.platform_txn_id`. *Effort: 5h*.
    - [ ] Add Stripe API: Pull charges, payouts (lump-sum deposits). Map Stripe `charge_id`/`payout_id` to `Transaction.platform_txn_id`. *Effort: 5h*.
    - [ ] Handle bundled deposits: Parse Jobber/Stripe metadata (e.g., `invoice_number`, `customer_id`) to match QBO deposits. Flag unmatched for HITL. *Effort: 5h*.
  - **[X] PolicyEngineService**: Categorize txns (vendor prior 0.4, MCC 0.2, amount 0.2, history 0.1). Flag <0.9 for review.
    - [ ] Add Service Pro rules: Map “Home Depot” → “Materials”, “fuel” → “Reimbursements”, payroll by crew → job. Use USASpending/SAM.gov for vendor normalization (NAICS codes). *Effort: 3h*.
  - **[X] DocumentManagementService**: Process receipts (OCR via Tesseract, CSV). Link to txns.
    - [ ] Enhance OCR for job codes, crew IDs on receipts (e.g., regex for “Job #123”). *Effort: 3h*.
  - **[X] DocumentReviewService**: Queue for manual review.
    - [ ] Add Uncat-style HITL: Prompt owners for job code confirmation via email/Streamlit. *Effort: 3h*.
- **Routes**:
  - **[X] Existing**: `/api/ingest/qbo`, `/api/automation/categorize`, `/api/documents/upload`, `/api/review/documents`.
  - [ ] New: `/api/ingest/jobber` (POST), `/api/ingest/stripe` (POST) to sync jobs, payments. *Effort: 3h*.
  - [ ] New: `/api/jobs/list` (GET) to fetch QBO/Jobber jobs. *Effort: 2h*.
- **Template**: [ ] `job_cost_dashboard.py` (Streamlit) – Table of txns (date, vendor, amount, job code, confidence), flagged exceptions, Match % (e.g., 75%), KPI widgets (margin per crew/week/job type). *Effort: 10h*.
- **Tests**: [ ] Update Pytest for Jobber/Stripe ingestion, Service Pro rules. Test with QBO/Jobber/Stripe sandbox + CSVs (100 receipts, 10 payroll batches). Goal: 70% auto-matched, <20% overrides. *Effort: 8h*.
- **Docs**: [ ] Update README for Jobber/Stripe setup, Service Pro rules, USASpending/SAM.gov. *Effort: 2h*.
- **Extensibility**:
  - Schema (`Integration`, `Transaction`, `Job`) uses `platform` field to support ServiceTitan, HouseCall Pro, Jobber Pay without changes.
  - `DataIngestionService` abstracts API calls (e.g., `fetch_platform_data(platform, credentials)`), reusable for new integrations.
- **KPIs**: % txns auto-matched (70-80%), override rate (<20%), doc processing time.


### Stage 1: Pre-Close Validation & Escalation
*Goal*: Run pre-close checks, classify tier 1 vs. tier 2 issues, bundle evidence for controller handoff, support HITL categorization. *Effort: ~20h*
- **Models**:
  - **[X] Existing**: `PreCloseCheck`, `Exception`, `PBCRequest`, `Task`.
  - [ ] New: `EscalationPackage` (`package_id`, `tenant_id`, `client_id`, `exception_id`, `docs`, `notes`, `status`). *Effort: 2h*.
  - [ ] New: `IntegrityIssue` (`issue_id`, `tenant_id`, `client_id`, `type` [recon, cutoff, coverage, variance], `description`, `tier` [1, 2], `evidence_refs`). *Effort: 2h*.
- **Services**:
  - **[X] PreCloseService**: Check missing receipts, unmatched txns (>500 not tied to jobs).
    - [ ] Add checks for Jobber/Stripe deposits, unmatched payroll/reimbursements. *Effort: 3h*.
  - **[X] PBCTrackerService**: Track missing docs, assign tasks.
    - [ ] Extend for HITL owner prompts (job code confirmation). *Effort: 3h*.
  - [ ] New: `TierClassificationService`: Classify issues (tier 1: missing doc, mislabel; tier 2: complex recon). *Effort: 4h*.
  - [ ] New: `EvidencePackagingService`: Bundle txns, docs, notes for tier 2 handoff. *Effort: 4h*.
  - [ ] New: `EscalationWorkflowService`: Route tier 1 to bookkeeper, tier 2 to controller. *Effort: 4h*.
- **Routes**:
  - **[X] Existing**: `/api/preclose/checks`, `/api/preclose/pbc`.
  - [ ] New: `/api/escalations/tier2` (POST) for controller handoff. *Effort: 2h*.
- **Template**: [ ] Extend `job_cost_dashboard.py` – Add tabs for exceptions, PBC status, tier 1/2 issues. *Effort: 5h*.
- **Tests**: [ ] Update Pytest for tier classification, escalation, Jobber/Stripe checks. Goal: 90% check pass rate, <5% false positives. *Effort: 5h*.
- **Docs**: [ ] Update README for Service Pro checks, escalation. *Effort: 2h*.
- **KPIs**: % PBC items on time, exception resolution time, tier 2 escalation rate (<10%).

### Stage 2: Job-Cost Reporting & Owner KPI Dashboard
*Goal*: Generate job-cost reports (PDF/Excel) and KPI dashboard (margins per crew/week/job type). Mock JEs for demos. *Effort: ~20h*
- **Models**:
  - [ ] New: `JobCostReport` (`report_id`, `tenant_id`, `client_id`, `period`, `jobs[{job_id, total_cost, labor_cost, material_cost, reimbursement_cost, unmatched}]`, `status`). *Effort: 2h*.
- **Services**:
  - [ ] New: `ReportService`: Generate report (Jinja2 for PDF/Excel): List jobs, matched txns (labor, materials, reimbursements), unmatched flags, Match Score. Mock JEs. *Effort: 8h*.
  - [ ] New: `OwnerKPIService`: Calculate margins per crew/week/job type. *Effort: 4h*.
- **Routes**:
  - [ ] New: `/api/reports/job-cost` (POST) – Compile report, return URL. *Effort: 2h*.
  - [ ] New: `/api/kpis/owner` (GET) – Fetch margins. *Effort: 2h*.
- **Template**: [ ] Update `job_cost_dashboard.py` – Add “Download Report” button, KPI bar charts. *Effort: 3h*.
- **Tests**: [ ] Pytest for ReportService, OwnerKPIService. *Effort: 3h*.
- **Docs**: [ ] README for reports, KPIs. *Effort: 2h*.
- **KPIs**: Report generation time (<10 mins), KPI accuracy, client response rate (10-20%).

### Stage 3: Audit Logging
*Goal*: Log all mutation operations (AR, expenses, payroll, reimbursements). *Effort: ~15h*
- **Models**: [X] `AuditLog` (`log_id`, `firm_id`, `client_id`, `user_id`, `operation`, `entity_type`, `entity_id`, `changes`, `timestamp`).
  - [ ] Extend for Jobber/Stripe txns, job-cost mutations. *Effort: 1h*.
- **Services**: [X] `AuditLogService`: Log mutations, retrieve/filter logs.
  - [ ] Integrate with Jobber/Stripe ingestion, job-cost services. *Effort: 3h*.
- **Routes**: [X] `/api/audit/logs` (GET, POST).
  - [ ] Add filters for Jobber/Stripe entities. *Effort: 1h*.
- **Template**: [ ] Port `audit_log_queue.html` to `audit_log_queue.py` (Streamlit). *Effort: 3h*.
- **Tests**: [ ] Update Pytest for Jobber/Stripe logs. *Effort: 3h*.
- **Docs**: [ ] Update README for Jobber/Stripe entities. *Effort: 1h*.
- **KPIs**: Log completeness (100%), retrieval time, filter accuracy.

### Requirements for Prioritized Features
1. **Bundled AR Deposit Reconciliation (17)**:
   - **Need**: Match lump-sum deposits from Jobber/Stripe to QBO without itemized line-outs.
   - **Solution**: `DataIngestionService` pulls Jobber invoices/payments, Stripe charges/payouts. `PolicyEngineService` maps deposits to QBO using metadata (e.g., Jobber `invoice_number`, Stripe `customer_id`). Flag unmatched for HITL. Extensible for ServiceTitan/HouseCall Pro via `Integration.platform`. *Effort: 15h (Stage 0)*.
   - **KPIs**: % deposits matched (70-80%), override rate (<20%).
2. **Job-Cost Reporting (20)**:
   - **Need**: Per-job profitability (labor, materials, reimbursements).
   - **Solution**: `ReportService` generates PDF/Excel reports with matched txns, unmatched flags, mock JEs. Uses `Job` and `Transaction` models. *Effort: 8h (Stage 2)*.
   - **KPIs**: Report generation time (<10 mins), accuracy.
3. **Uncat-style Categorization (20)**:
   - **Need**: Owner-driven HITL labeling for low-confidence txns.
   - **Solution**: `DocumentReviewService` prompts owners via Streamlit/email for job code confirmation. `PolicyEngineService` learns from corrections. *Effort: 6h (Stage 0-1)*.
   - **KPIs**: Override rate (<20%), owner response time.
4. **Expense/PO → Job Matching (20)**:
   - **Need**: Tag Home Depot runs, subcontractor invoices to jobs.
   - **Solution**: `PolicyEngineService` uses rules (vendor, MCC, job codes) and OCR (`DocumentManagementService`) to match expenses/POs to `Job`. Flag <0.9 for HITL. *Effort: 6h (Stage 0)*.
   - **KPIs**: % expenses matched (70-80%), override rate.
5. **Payroll → Job Sync (20)**:
   - **Need**: Match crew hours to jobs.
   - **Solution**: `DataIngestionService` ingests payroll CSVs or QBO payroll data. `PolicyEngineService` maps to `Job` using crew IDs, job codes. *Effort: 5h (Stage 0)*.
   - **KPIs**: % payroll matched (70-80%), override rate.
6. **Field Reimbursements (17)**:
   - **Need**: Log fuel, supplies to correct jobs.
   - **Solution**: `DocumentManagementService` processes reimbursement receipts (OCR for job codes). `PolicyEngineService` matches to `Job`. *Effort: 5h (Stage 0)*.
   - **KPIs**: % reimbursements matched (70-80%), override rate.
7. **Owner KPI Dashboard (14)**:
   - **Need**: Margins per crew/week/job type.
   - **Solution**: `OwnerKPIService` calculates KPIs from `JobCostReport`. `job_cost_dashboard.py` displays bar charts. *Effort: 7h (Stage 2)*.
   - **KPIs**: Client response rate (10-20%), KPI accuracy.

### Validation Plan (4-6 Weeks, ~80-100h)
1. **Week 1: Sandbox & Data (20h)**:
   - Set up QBO/Jobber/Stripe sandbox (Intuit Developer, Jobber OAuth, Stripe test keys). *Effort: 5h*.
   - Update `DataIngestionService` for APIs. Pull USASpending/SAM.gov vendors. *Effort: 10h*.
   - Run Pytest (90% pass rate). *Effort: 5h*.
2. **Weeks 2-3: Dashboard & Enhancements (30h)**:
   - Build `job_cost_dashboard.py`: Txns, exceptions, KPIs, reports. *Effort: 10h*.
   - Enhance `PolicyEngineService`, `DocumentManagementService` for Service Pro rules, OCR. *Effort: 10h*.
   - Test with sandbox + CSVs (100 receipts, 10 payroll batches). Goal: 70% match rate. *Effort: 10h*.
3. **Weeks 4-5: Pilot & Escalation (30h)**:
   - Source 1 test client (Upwork, $200 for QBO/Jobber data). Run ingestion, categorization, reports. *Effort: 10h*.
   - Test tier classification, HITL prompts, escalations. *Effort: 10h*.
   - Outreach: Email 10 SC contractors (Home Builders Association) for Shadow Scan demos. *Effort: 10h*.
4. **Week 6: Beta & Polish (20h)**:
   - Polish dashboard (visuals, e.g., Chart.js). *Effort: 5h*.
   - Integrate audit logging for Jobber/Stripe. *Effort: 5h*.
   - Land 1-2 betas ($99-$199/mo). *Effort: 10h*.

### Effort Summary
- **Total**: ~85-105h (~1.5-2 months solo, faster with Upwork SWE/bookkeeper).
- **Breakdown**:
  - Stage 0: 30h
  - Stage 1: 20h
  - Stage 2: 20h
  - Stage 3: 15h
  - Validation: 20h
- **Team**: You (backend, APIs), Upwork SWE (0.5, frontend/tests, $30/hr), Upwork bookkeeper (0.5, reviews, $20-40/hr).
- **Pilot**: Q4 2025, 1-2 SC clients, 3-5 jobs each.
