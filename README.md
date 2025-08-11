Escher Automation Engine for BookClose
Overview
Escher is the deterministic, rules-based automation core for BookClose, a white-label, AI-native platform designed to automate 70-80% of the book-to-close process for accounting firms. Inspired by the need to reduce manual bookkeeping tasks (data entry, categorization, vendor matching, reconciliations), Escher powers BookClose’s ability to act as an "executive assistant" or transaction coordinator, handling repetitive tasks while routing exceptions to human review. By integrating vendor normalization (Escher Vendor Brain) and transaction categorization (Escher Autocode), Escher achieves high-coverage automation, self-improves through corrections, and ensures compliance with audit-ready guardrails.
BookClose, built on Python/FastAPI, SQLAlchemy, React/Tailwind CSS, and integrations with QuickBooks Online (QBO), Plaid, BILL/Melio, and Gusto, targets the full book-to-close lifecycle: Accounts Payable (AP), Accounts Receivable (AR), Bank/Credit Card Transactions, Inventory, Payroll, Pre-Close Review, Month-End Close, Binder Assembly, and Scaling Best Practices. Escher is the backbone for AP and Bank/CC automation, with extensibility to AR, Payroll, and Close processes, delivering 70-80% automation day one and 85-95% within months via correction-driven rule refinement.
Why Escher Matters

Automation-First: Reduces 80% of manual bookkeeping (e.g., categorizing transactions, deduplicating vendors) using deterministic rules, freeing firms for advisory work.
Self-Improving: Captures human corrections as new rules, shrinking the review queue over time (inspired by Gaggle’s feedback loops).
Audit-Ready: Enforces guardrails (no auto-post to cash/equity, two-step balance sheet writes, immutable logs) for SOC 2 compliance and audit traceability.
Scalable: Multi-tenant, cloud-native (Kubernetes-ready), with modular integration to QBO, Plaid, and other APIs.
Differentiated: Leapfrogs competitors like Keeper.app (manual-heavy) and Docyt (self-service) with white-label branding, hybrid coordinator support, and tax-ready outputs.

Features
Escher integrates two key components into BookClose:

Escher Vendor Brain v0.1:
Normalizes vendor names (e.g., strips "WEB AUTHORIZED PMT", uppercases, collapses whitespace).
Maps vendors to Chart of Accounts (COA) using MCC (primary) and NAICS (fallback) codes.
Pulls public data (USASpending) for broad vendor coverage.
Emits vendor_canonical.csv (deduplicated vendor table) and rules.yaml (categorization rules).


Escher Autocode v0.1:
Applies layered rules (exact matches, regex, contains, amount/date heuristics, transfer detection) to categorize transactions.
Outputs categorized transactions with confidence scores, rule explanations, and review flags.
Supports a correction workflow to generate new rules, improving automation over time.
Integrates with QBO for draft/batch posting, ensuring auditability.



Key Automation Workflows

Vendor Normalization: Deduplicates vendors (e.g., "AMZN" vs. "Amazon Marketplace") and assigns default GL accounts.
Transaction Categorization: Maps bank/CC transactions to COA (e.g., "STRIPE PAYOUT" → Clearing:Stripe, confidence 0.97).
Review Queue: Routes mid-confidence transactions (0.6-0.89) to a UI with Assertion Chips and correction forms.
Guardrails: Prevents auto-posting to sensitive accounts (cash, equity); enforces adjusting JEs for locked periods.
Self-Healing: Handles API failures (QBO rate limits: 100 req/min) with retries, CDC sweeps, and manual fallbacks (CSV uploads).

Integration with BookClose
Escher is embedded in BookClose’s microservices architecture, powering automation across multiple stages:

Stage 0: Automation Engine: Centralizes Escher’s rules engine (PolicyEngineService), vendor normalization (VendorNormalizationService), and data ingestion (DataIngestionService). Outputs rules.yaml and vendor_canonical.csv for downstream use.
Stage 1A: Accounts Payable: Enhances BillIngestionService and VendorMasteringService with Escher’s normalization and categorization, achieving 80% automation for bill processing.
Stage 1C: Bank & Credit Card Transactions: Powers MatchingService to categorize transactions (80%) and detect transfers, with a review queue for edge cases.
Stage 3: Month-End Close: Uses Escher rules for journal entry (JE) drafts (AdjustmentService, 90% automation) and anomaly flagging (ReconciliationService).

Data Model

Rule: Stores rules from rules.yaml (match_type, pattern, output{account, class, memo, confidence}).
VendorCanonical: Tracks normalized vendors with MCC/NAICS mappings.
Correction: Captures human fixes (raw_descriptor, suggested/final accounts, rationale) for rule generation.
Suggestion: Stores top-k categorization suggestions with confidence scores.
Additional Models: Integrated with BookClose’s Vendor, Bill, BankTransaction, JournalEntry, etc., adding rule_id, confidence, and suggestion_id fields.

Confidence and Routing

≥0.9: Auto-post to QBO (draft mode).
0.6-0.89: Route to review queue with explainability (rule_id, prior matches).
<0.6: Flag for manual context, with minimal guess.

Setup Instructions
Prerequisites

Python: 3.10+
Database: SQLite (dev), PostgreSQL (prod)
Dependencies: Install via requirements.txt:pip install fastapi sqlalchemy pydantic pytest pandas pyyaml requests boto3 scikit-learn transformers


API Keys: QBO, Plaid, BILL/Melio, Gusto, AWS (Textract for OCR).
Data: 12-18 months of client CSVs (bank, CC, AP/AR, payroll); optional vendor/customer lists, POS exports.

Installation

Clone the repository:git clone <bookclose-repo-url>
cd bookclose


Set up a virtual environment:python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate


Install dependencies:pip install -r requirements.txt


Configure environment variables (.env):DATABASE_URL=postgresql://user:pass@localhost:5432/bookclose
QBO_API_KEY=<your-key>
PLAID_CLIENT_ID=<your-id>
PLAID_SECRET=<your-secret>
BILL_API_KEY=<your-key>
GUSTO_API_KEY=<your-key>
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>


Initialize the database:python src/manage.py migrate


Seed initial rules and vendor data:python src/manage.py seed --rules config/rules.yaml --vendors data/vendor_canonical.csv



Running the Application

Start the FastAPI server:uvicorn src.main:app --host 0.0.0.0 --port 8000


Access the UI at http://localhost:8000 for the review cockpit.
Import CSVs to kick off automation:python src/manage.py import-csv --path data/raw/bank_transactions.csv


View Swagger docs at http://localhost:8000/docs for API details.

Directory Structure
bookclose/
├── config/
│   └── rules.yaml              # Escher rules for categorization
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

Usage

Ingest Data:
Upload CSVs via /api/automation/categorize or CLI.
Escher normalizes vendors and categorizes transactions, outputting suggestions with confidence.


Review Queue:
Access categorization_queue.html to review mid-confidence (0.6-0.89) transactions.
Submit corrections with rationale to improve rules.


Automate Workflows:
AP: Bills categorized and synced to QBO (Stage 1A).
Bank/CC: Transactions matched with rules; transfers detected (Stage 1C).
Close: JEs drafted and anomalies flagged (Stage 3).


Monitor and Scale:
Use workflow_dashboard.html to track tasks and SLAs.
Metrics (automation rate, cycle time) available via /api/observability/metrics.



Expected Ramp

Month 1: 70-80% automation with 100-300 base rules; juniors clear review queue.
Month 2: Corrections refine rules; POS/payroll JEs standardized (85-90% automation).
Month 3+: Edge cases minimized; ML suggestions (optional) lift coverage to 95%.

Guardrails and Compliance

No Auto-Post to Sensitive Accounts: Cash, retained earnings locked.
Two-Step Balance Sheet Writes: Draft + link to source.
Locked Periods: Late changes via adjusting JEs with memos.
Auditability: Immutable logs, rule_id tracking, SHA-256 hashes for binders.
SOC 2: Encryption, KMS secrets, MFA enforced.

Extensibility

Custom Rules: Add client-specific rules to rules.yaml (e.g., "SYSCO" → COGS:Food for hospitality clients).
ML Integration: Train scikit-learn models on corrections for top-k suggestions (Stage 0, phase 2).
API Extensions: Add tax/CRM modules via modular microservices.

Troubleshooting

API Rate Limits: QBO (100 req/min) handled with retries and Redis queues.
Data Gaps: Use CSV fallbacks for failed API pulls (Plaid, QBO).
Edge Cases: Flag low-confidence (<0.6) transactions for manual review.
Logs: Check /api/observability/metrics for automation rate and errors.

Next Steps

Prototype: Test Stage 0 with a sample CSV to generate initial rules.
MVP: Build Stages 0, 1A, 1C, and 2 (~100 hours) for a demo in 2-3 months.
Contribute: Share anonymized CSVs to refine rules.yaml or request a starter rule set.

License
Proprietary. Contact the BookClose team for licensing details.