# BookClose README

## Overview
BookClose is an automation-first platform designed to streamline the book-to-close process for accounting firms, achieving 70-80% automation of transaction categorization, reconciliation, and audit-ready binder generation. Built on Python/FastAPI, SQLAlchemy (Postgres), React/Tailwind CSS, and integrations with QuickBooks Online (QBO), Plaid, BILL/Melio, and Gusto, BookClose targets the full close lifecycle: Accounts Payable (AP), Accounts Receivable (AR), Bank/Credit Card Transactions, Inventory, Payroll, Pre-Close Review, Month-End Close, Binder Assembly, and Scaling Best Practices. Its deterministic rules engine (PolicyEngineService) and vendor normalization (VendorNormalizationService) power high-coverage automation, self-improve through corrections, and ensure audit-ready outputs with guardrails.

## Why BookClose Matters
- **Automation-First**: Reduces 80% of manual bookkeeping (e.g., categorizing transactions, deduplicating vendors) using rules-based logic, freeing firms for advisory work.
- **Self-Improving**: Captures human corrections as new rules, shrinking the review queue over time.
- **Audit-Ready**: Enforces guardrails (no auto-post to cash/equity, two-step balance sheet writes, immutable logs) for SOC 2 compliance and audit traceability.
- **Scalable**: Multi-tenant, cloud-native (Kubernetes-ready), with modular integrations to QBO, Plaid, and other APIs.

## Features
### Vendor Normalization
- Normalizes vendor names (e.g., strips "WEB AUTHORIZED PMT", uppercases, collapses whitespace).
- Maps vendors to Chart of Accounts (COA) using MCC (primary) and NAICS (fallback) codes.
- Emits `vendor_canonical.csv` (deduplicated vendor table) and `rules.yaml` (categorization rules).

### Transaction Categorization
- Applies layered rules (exact matches, regex, contains, amount/date heuristics, transfer detection) to categorize transactions.
- Outputs categorized transactions with confidence scores, rule explanations, and review flags.
- Supports correction workflows to generate new rules, improving automation over time.
- Integrates with QBO for draft/batch posting, ensuring auditability.

### Key Workflows
- **Vendor Normalization**: Deduplicates vendors (e.g., "AMZN" vs. "Amazon Marketplace") and assigns default GL accounts.
- **Transaction Categorization**: Maps bank/CC transactions to COA (e.g., "STRIPE PAYOUT" → `Clearing:Stripe`, confidence 0.97).
- **Review Queue**: Routes mid-confidence transactions (0.6-0.89) to a UI with Assertion Chips and correction forms.
- **Guardrails**: Prevents auto-posting to sensitive accounts (cash, equity); enforces adjusting JEs for locked periods.
- **Self-Healing**: Handles API failures (QBO rate limits: 100 req/min) with retries, CDC sweeps, and manual fallbacks (CSV uploads).
- **Deliverables**: Generates working binders (Excel), final binders (PDF) with cover, index, tickmark legend, BS/IS tabs, JEs, close summary narrative, management commentary, and AP/AR snapshots.

## Integration with BookClose Stages
- **Stage 0: Automation Engine**: Centralizes rules engine (`PolicyEngineService`), vendor normalization (`VendorNormalizationService`), and data ingestion (`DataIngestionService`). Outputs `rules.yaml` and `vendor_canonical.csv`.
- **Stage 1A: Accounts Payable**: Automates bill ingestion (`BillIngestionService`), payment scheduling (`APPaymentService`), and statement reconciliation (`StatementReconciliationService`) with 80% automation.
- **Stage 1B: Accounts Receivable**: Automates invoice creation (`InvoiceService`), collections (`CollectionsService`), and payment matching (`PaymentApplicationService`) with 80% automation.
- **Stage 1C: Bank & Credit Card Transactions**: Powers transaction matching (`MatchingService`) and transfer detection (`TransferService`) with 80% automation.
- **Stage 1D: Inventory Management**: Tracks items and adjustments (`InventoryService`) with 70% automation.
- **Stage 1E: Payroll & Liabilities**: Automates payroll journals (`PayrollService`) and remittance tracking (`RemittanceService`) with 90% JE automation.
- **Stage 2: Pre-Close Review**: Runs completeness checks (`PreCloseService`), tracks PBC requests (`PBCTrackerService`), and computes close readiness score (% reconciled, exceptions, missing docs).
- **Stage 3: Month-End Close**: Drafts JEs (`AdjustmentService`), detects prepaids (`PrepaidService`), applies cutoffs (`AdjustmentService`), and generates AP/AR snapshots (`TieOutService`) with 90% automation.
- **Stage 4: Binder Assembly**: Generates audit-ready binders with narrative and commentary (`BinderService`).
- **Stage 5: Scaling Best Practices**: Tracks KPIs (automation rate, AR creep, margin compression) via `ObservabilityService` and orchestrates multi-firm tasks (`WorkflowService`).

## Data Model
- **Rule** (rule_id, tenant_id, client_id, priority, match_type=’exact|regex|contains|amount|transfer’, pattern, output{account, class, memo, confidence}, scope=’global|client’): Stores rules from `rules.yaml`.
- **VendorCanonical** (vendor_id, tenant_id, client_id, raw_name, canonical_name, mcc, naics, default_gl_account, confidence): Normalized vendor table.
- **Correction** (correction_id, tenant_id, client_id, txn_id, raw_descriptor, suggested{account, class, confidence}, final{account, class, memo}, rationale, created_by, scope=’client|global’): Human fixes for rule generation.
- **Suggestion** (suggestion_id, tenant_id, client_id, txn_id, top_k[{account, class, confidence}], chosen_idx): Categorization suggestions.
- **Additional Models**: Vendor, Bill, PaymentIntent, VendorStatement, Customer, Invoice, Payment, CreditMemo, BankTransaction, Transfer, Item, InventoryAdjustment, PayrollBatch, PayrollRemittance, PreCloseCheck, Exception, PBCRequest, CloseChecklist, Reconciliation, JournalEntry, Approval, PrepaidSchedule, CutoffWorksheet, Binder, Tickmark, WorkflowTemplate, Metric.

## Confidence and Routing
- **≥0.9**: Auto-post to QBO (draft mode).
- **0.6-0.89**: Route to review queue (`categorization_queue.html`) with explainability (rule_id, prior matches).
- **<0.6**: Flag for manual context, with minimal guess.

## Setup Instructions
### Prerequisites
- **Python**: 3.10+
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Dependencies**: Poetry as package and environment manager: `pyproject.toml`:
  ```bash
  poetry add fastapi sqlalchemy pydantic pytest pandas pyyaml requests boto3 scikit-learn transformers httpx opentelemetry-api
  ```
- **API Keys**: QBO, Plaid, BILL/Melio, Gusto, AWS (Textract for OCR).
- **Data**: 12-18 months of client CSVs (bank, CC, AP/AR, payroll); optional vendor/customer lists, POS exports.

### Installation
1. Clone the repository:
   ```bash
   git clone <bookclose-repo-url>
   cd bookclose
   ```
2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables (`.env`):
   ```plaintext
   DATABASE_URL=postgresql://user:pass@localhost:5432/bookclose
   QBO_API_KEY=<your-key>
   PLAID_CLIENT_ID=<your-id>
   PLAID_SECRET=<your-secret>
   BILL_API_KEY=<your-key>
   GUSTO_API_KEY=<your-key>
   AWS_ACCESS_KEY_ID=<your-key>
   AWS_SECRET_ACCESS_KEY=<your-secret>
   ```
5. Initialize the database:
   ```bash
   python src/manage.py migrate
   ```
6. Seed initial rules and vendor data:
   ```bash
   python src/manage.py seed --rules config/rules.yaml --vendors data/vendor_canonical.csv
   ```

### Running the Application
1. Start the FastAPI server:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```
2. Access the UI at `http://localhost:8000` for the review cockpit.
3. Import CSVs to kick off automation:
   ```bash
   python src/manage.py import-csv --path data/raw/bank_transactions.csv
   ```
4. View Swagger docs at `http://localhost:8000/docs` for API details.

### Directory Structure
```
bookclose/
├── config/
│   └── rules.yaml              # Categorization rules
├── data/
│   ├── raw/                    # Input CSVs (bank, CC, etc.)
│   ├── processed/              # Normalized data
│   └── out/                    # Artifacts (vendor_canonical.csv, mcc_to_coa_map.csv)
├── src/
│   ├── main.py                 # FastAPI app
│   ├── models/                 # SQLAlchemy models (Rule, VendorCanonical, etc.)
│   ├── services/               # Services (PolicyEngineService, VendorNormalizationService, etc.)
│   ├── routes/                 # API endpoints
│   └── templates/              # React/Tailwind UI (bill_review.html, categorization_queue.html)
├── tests/                      # Pytest unit and integration tests
└── requirements.txt            # Dependencies
```

## Usage
### Ingest Data
- Upload CSVs via `/api/automation/categorize` or CLI:
  ```bash
  python src/manage.py import-csv --path data/raw/bank_transactions.csv
  ```
- BookClose normalizes vendors and categorizes transactions, outputting suggestions with confidence.

### Review Queue
- Access `categorization_queue.html` to review mid-confidence (0.6-0.89) transactions.
- Submit corrections with rationale to improve rules via `/api/automation/corrections`.

### Automate Workflows
- **AP (Stage 1A)**: Bills categorized (`BillIngestionService`), payments scheduled (`APPaymentService`), statements reconciled (`StatementReconciliationService`).
- **AR (Stage 1B)**: Invoices created (`InvoiceService`), payments matched (`PaymentApplicationService`), collections automated (`CollectionsService`).
- **Bank/CC (Stage 1C)**: Transactions matched (`MatchingService`), transfers detected (`TransferService`).
- **Inventory (Stage 1D)**: Items tracked, adjustments posted (`InventoryService`).
- **Payroll (Stage 1E)**: Journals posted (`PayrollService`), remittances tracked (`RemittanceService`).
- **Pre-Close (Stage 2)**: Run checks (`PreCloseService`), track PBCs (`PBCTrackerService`), compute readiness score.
- **Close (Stage 3)**: Draft JEs (`AdjustmentService`), detect prepaids/cutoffs (`PrepaidService`, `AdjustmentService`), generate AP/AR snapshots (`TieOutService`).
- **Binder (Stage 4)**: Generate binders with narrative and commentary (`BinderService`).
- **Scaling (Stage 5)**: Track KPIs (`ObservabilityService`), orchestrate tasks (`WorkflowService`).

### Monitor and Scale
- Use `workflow_dashboard.html` to track tasks and SLAs.
- Metrics (automation rate, cycle time, AR creep, margin compression) available via `/api/observability/metrics`.

## Expected Ramp
- **Month 1**: 70-80% automation with 100-300 base rules; juniors clear review queue.
- **Month 2**: Corrections refine rules; POS/payroll JEs standardized (85-90% automation).
- **Month 3+**: Edge cases minimized; ML suggestions (optional) lift coverage