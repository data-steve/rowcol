# BookClose Comprehensive Plan (Updated with OCR Review and Engagements)

**Checksum**: 4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4

## System Overview
**Overview**: A white-label, automation-first monthly close service for accounting firms, integrating with QBO for transaction ingestion, normalization, reconciliation, and audit-ready binder generation. The MVP targets 70-80% automation of transaction categorization and reconciliation, with a D+5 close SLA, scalable to multi-firm, multi-client operations.
- **Purpose**: Serviceervice for single/double-partner SC accounting firms (1-5 staff, 10-50 clients, <200 txns/mo) in the Upstate, delivering D+5 closes with audit-ready binders (<5 review notes). Focuses on document-heavy workflows (51% spreadsheets, 21% paper per SMB Group 2025) using robust CSV/OCR, QBO/Bill.com APIs, and a review queue for OCR/tagging. Provides advisory insights (close readiness score, AP/AR snapshots, narratives) and task-based PBC scheduling.
- **Tech Stack**: Python, FastAPI, SQLAlchemy (SQLite dev, Postgres prod), React/Tailwind CSS, Pydantic, Pytest, QBO API, Bill.com API, Tesseract + OpenCV (basic OCR), Google Cloud Document AI (advanced OCR), Jinja2 (PDF rendering), Redis, OpenAPI, PyYAML, pandas.
- **Scope**: 80% automation for bookkeeping (categorization, reconciliations), 60-75% for close tasks (reconciliations, JEs, binders). Excludes payroll processing, tax prep, and complex ERPs (NetSuite/SAP). Supports 95% non-API clients (QuickBooks Desktop, Sage, manual ledgers) via CSV/OCR. Includes review queue for OCR/tagging and engagement/task framework for PBC scheduling.
- **Design Principles**: Policy-driven, self-improving (corrections to rules), idempotent ingestion, immutable provenance, human-in-the-loop (HITL) for OCR/tagging review, audit-ready (Evidence Locker, tickmarks: ✓=reconciled, Δ=JE).
- **Price Tiers**:
  - **Tier 1 ($500/mo)**: Low document volume (<50 docs/mo, QBO-native), 80% automation.
  - **Tier 2 ($1000/mo)**: Medium volume (50-200 docs/mo, CSV uploads), 60-75% automation, moderate OCR/tagging review.
  - **Tier 3 ($2000+/mo)**: High volume (>200 docs/mo, paper-heavy), 50-60% automation, upcharge for manual OCR/tagging review and complex JEs.
- **Engagement Framework**: Lightweight engagements for PBC collection and task routing, ensuring scalability to practice management in Phase 3.

## Guardrails
- **Security**: Encrypt tokens (KMS), audit logs, PII restricted (payroll/docs), idempotency for write-backs.
- **Edge Cases**: Handle multi-currency (store txn/home currency, use QBO ExchangeRate), voided txns (soft-delete), locked books (check CompanyInfo), bank feed lags (amount/date tolerance), OCR errors (low-confidence flags).
- **Scalability**: Modular services, normalized COA, tenant isolation (firm_id, client_id), task routing by role.
- **Deliverables**: Excel/PDF binders (Cover, Index, Tickmark Legend, Bank, AR, AP, Prepaids, JEs, Exceptions, Close Summary, Snapshots), JE exports, close readiness score, AP/AR snapshots, narratives.
- **Constraints**: No payroll processing (only reconciliation), no tax prep, no CRM/ERP integrations in MVP.

## Development Patterns & Anti-Patterns (Lessons Learned)
*Based on Stage 0 implementation experience - critical for avoiding common pitfalls*

### 🚫 **ANTI-PATTERNS TO AVOID**

#### **File Naming & Import Chaos**
- ❌ **Don't:** Use folder names as prefixes in filenames (`models_service.py`, `routes_engagement.py`)
- ❌ **Don't:** Bulk rename files without updating ALL imports across the codebase
- ❌ **Don't:** Assume imports will "just work" after file moves
- ✅ **Do:** Use descriptive, unique filenames (`service.py`, `engagement.py`)
- ✅ **Do:** Update imports systematically after any file reorganization

#### **Schema vs. Model Confusion**
- ❌ **Don't:** Use SQLAlchemy models as `response_model` in FastAPI routes
- ❌ **Don't:** Mix Pydantic schemas and SQLAlchemy models in API responses
- ❌ **Don't:** Assume `from_attributes = True` fixes all serialization issues
- ✅ **Do:** Create separate Pydantic schemas (`*Base`, `*Create`, full models)
- ✅ **Do:** Use Pydantic schemas for `response_model`, SQLAlchemy models for database operations
- ✅ **Do:** Alias SQLAlchemy models in routes: `from models import Service as ServiceModel`

#### **Database Schema Mismatches**
- ❌ **Don't:** Create seed data that doesn't match your SQLAlchemy models
- ❌ **Don't:** Assume database columns exist without checking the actual model definitions
- ❌ **Don't:** Use hardcoded field names that don't match the database schema
- ✅ **Do:** Ensure seed data exactly matches your model definitions
- ✅ **Do:** Use consistent field names across models, schemas, and seed data
- ✅ **Do:** Test database seeding before building frontend features

#### **Missing Required Fields**
- ❌ **Don't:** Forget to add required fields like `firm_id` when implementing multi-tenancy
- ❌ **Don't:** Create models that inherit from mixins but don't implement required fields
- ❌ **Don't:** Assume optional fields are truly optional without checking business logic
- ✅ **Do:** Explicitly add all required fields when implementing new features
- ✅ **Do:** Use database constraints to enforce required fields
- ✅ **Do:** Validate that seed data includes all required fields

#### **Complex Dependencies in Templates**
- ❌ **Don't:** Load heavy third-party libraries (drag-and-drop, tour libraries) in basic templates
- ❌ **Don't:** Assume CDN libraries will load correctly or have the expected global variables
- ❌ **Don't:** Mix complex JavaScript with Jinja2 template syntax
- ✅ **Do:** Start with basic React components and add complexity incrementally
- ✅ **Do:** Test external library loading before building complex features
- ✅ **Do:** Use raw JavaScript blocks or escape Jinja2 syntax conflicts

#### **Database Seeding Issues**
- ❌ **Don't:** Call seeding functions multiple times without checking if data already exists
- ❌ **Don't:** Use SQLAlchemy queries to check if tables exist before seeding
- ❌ **Don't:** Assume seeding will work after table creation without proper error handling
- ✅ **Do:** Use raw SQL to check table existence and data counts
- ✅ **Do:** Implement proper error handling in seeding functions
- ✅ **Do:** Test seeding with fresh databases

### ✅ **GOOD PATTERNS TO REPLICATE**

#### **Systematic Problem Solving**
- ✅ **Do:** Fix one issue at a time, test, then move to the next
- ✅ **Do:** Use error messages to guide fixes rather than guessing
- ✅ **Do:** Test APIs directly with `curl` before testing frontend
- ✅ **Do:** Check server logs for detailed error information

#### **Incremental Template Development**
- ✅ **Do:** Start with simple templates that just display data
- ✅ **Do:** Add interactive features only after basic functionality works
- ✅ **Do:** Use console logging to debug frontend data flow
- ✅ **Do:** Test templates in isolation before integrating with complex features

#### **Proper Test Structure**
- ✅ **Do:** Use fixtures for reusable test data
- ✅ **Do:** Mock external API calls to prevent test hangs
- ✅ **Do:** Test database operations with proper setup/teardown
- ✅ **Do:** Use descriptive test names and organize tests logically

#### **Multi-Tenant Architecture**
- ✅ **Do:** Implement `TenantMixin` consistently across all models
- ✅ **Do:** Add `firm_id` filtering to all list endpoints
- ✅ **Do:** Use proper foreign key relationships with explicit constraints
- ✅ **Do:** Test tenant isolation thoroughly

### 🔧 **SPECIFIC TECHNICAL FIXES TO REMEMBER**

#### **FastAPI Response Models**
```python
# ❌ WRONG - Using SQLAlchemy model directly
@router.get("/services", response_model=list[Service])  # Service is SQLAlchemy model

# ✅ CORRECT - Using Pydantic schema
from models import Service as ServiceModel
from schemas import Service as ServiceSchema

@router.get("/services", response_model=list[ServiceSchema])
async def list_services(firm_id: str = None, db: Session = Depends(get_db)):
    query = db.query(ServiceModel)  # Use SQLAlchemy model for queries
    # ... return ServiceSchema objects
```

#### **Database Seeding**
```python
# ❌ WRONG - Using SQLAlchemy to check tables that don't exist yet
def seed_database():
    db = SessionLocal()
    count = db.query(Engagement).count()  # Fails if table doesn't exist

# ✅ CORRECT - Using raw SQL to check table existence
def seed_database():
    conn = sqlite3.connect("bookclose.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='engagements'")
    if cursor.fetchone():
        # Table exists, check data
        cursor.execute("SELECT COUNT(*) FROM engagements")
        count = cursor.fetchone()[0]
        if count == 0:
            # Seed data
```

#### **Template JavaScript Conflicts**
```python
# ❌ WRONG - Jinja2 tries to parse JavaScript object literals
engagement={{ engagement_id: 1, due_date: '2025-12-31T23:59:59' }}

# ✅ CORRECT - Use JavaScript variables to avoid Jinja2 conflicts
const engagementData = {
    engagement_id: 1,
    due_date: '2025-12-31T23:59:59'
};
engagement={engagementData}
```

### 🎯 **KEY TAKEAWAYS FOR FUTURE DEVELOPMENT**

1. **Start Simple:** Build basic CRUD functionality before adding complex business logic
2. **Test Incrementally:** Test each component in isolation before integration
3. **Use Consistent Patterns:** Apply the same architectural patterns across all models/APIs
4. **Validate Data Flow:** Ensure data flows correctly from database → API → frontend
5. **Handle Errors Gracefully:** Implement proper error handling at each layer
6. **Document Assumptions:** Write down what you expect to work before implementing

**Bottom Line:** The foundation is now solid. Future development should focus on building business logic services incrementally, testing each piece thoroughly before moving to the next.

## Close Management Scope
- **What We Do**:
  - **Bookkeeping**: Categorize transactions (80% automation), reconcile bank/CC (90%), manage AP/AR (80%), normalize vendors (Stages 0, 1A, 1B, 1C).
  - **Close Management**: Reconcile subledgers to GL (80%), draft JEs (60-75%), detect prepaids/cutoffs (70%), generate trial balances, produce binders, provide advisory insights (readiness score, AR creep, margin compression) (Stages 2-4).
  - **Payroll Reconciliation**: Post payroll JEs and reconcile liabilities via CSV/QBO Payroll (Stage 1E, 70% automation).
  - **Document Review**: Review/correct OCR outputs (vendor, amount, date, address) and tagging (AP/AR, client-specific), batched by field/type/client (Stage 0).
  - **PBC Scheduling**: Engagement-based task assignments for document collection and review (Stage 2).
- **What We Don’t Do**:
  - **Payroll Processing**: No wage calculations, tax filings, or benefits management.
  - **Tax Preparation**: No tax liability calculations or filings (e.g., Form 1120, 4562).
  - **Complex ERP Workflows**: No NetSuite/SAP integrations (CSV only for MVP).
  - **Non-Standard JEs**: Complex accruals, intercompany transfers, or manual adjustments beyond automation limits (upcharge in Tier 3).
- **Technical Limits**: 60-75% close automation due to manual review (complex JEs, OCR errors, missing PBCs). 95% of SC clients (non-API) need CSV/OCR.

## Stage 0: Automation and Document Engine
*Goal*: Bootstrap vendor normalization, transaction categorization, QBO sync, document processing (CSV/OCR, storage), and OCR/tagging review for single-partner firms. *Effort: ~80h, Dependencies: None*

### Models
- [X] **Rule** (rule_id, tenant_id, client_id, priority, match_type=’exact|regex|contains|amount|transfer’, pattern, output{account, class, memo, confidence}, scope=’global|client’): Stores rules from `rules.yaml`. *Effort: 2h*
- [X] **VendorCanonical** (vendor_id, tenant_id, client_id, raw_name, canonical_name, mcc, naics, default_gl_account, confidence): From `vendor_canonical.csv`. *Effort: 2h*
- [X] **Correction** (correction_id, tenant_id, client_id, txn_id, raw_descriptor, suggested{account, class, confidence}, final{account, class, memo}, rationale, created_by, scope=’client|global’): Human fixes for rule generation. *Effort: 2h*
- [X] **Suggestion** (suggestion_id, tenant_id, client_id, txn_id, top_k[{account, class, confidence}], chosen_idx): Rules-based suggestions. *Effort: 2h*
- [X] **PolicyProfile** (profile_id, tenant_id, client_id, thresholds{posting, variance, capitalization, manual_jes, ocr_review}, revenue_policy, cutoff_rules, tickmark_map, deliverable_prefs, pricing_tier, doc_volume): Client configs, including tier and OCR review limits. *Effort: 3h*
- [X] **Document** (doc_id, tenant_id, client_id, period, type=’invoice|statement|receipt|payroll’, file_ref, hash, upload_date, status=’pending|processed|archived|review’, extracted_fields{vendor, amount, date, address, confidence}, review_status): Store documents with OCR outputs. *Effort: 3h*
- [X] **DocumentType** (type_id, name, fields[], required=’y|n’, validation_rules): Define document formats (e.g., invoice: vendor, amount, date, address). *Effort: 2h*
- [X] **User** (user_id, tenant_id, role=’admin|staff|client’, email, permissions, training_level=’junior|senior|manager’): Manage access and task routing. *Effort: 2h*
- [X] **Firm** (tenant_id, name, qbo_id, pricing_tier, doc_volume): Firm settings. *Effort: 2h*
- [X] **Client** (client_id, tenant_id, name, qbo_id, industry=’retail|pro_services|nonprofit’, policy_profile_id): Client configs. *Effort: 2h*
- [X] **Staff** (staff_id, tenant_id, user_id, role=’bookkeeper|manager’, training_level=’junior|senior’): Firm staff roles for task routing. *Effort: 2h*
- [X] **Engagement** (engagement_id, tenant_id, client_id, period, service_type=’bookkeeping|close|pbc_collection’, status, due_date, task_ids[]): Lightweight engagement for PBC and review tasks. *Effort: 3h, Dep: Client*
- [X] **Task** (task_id, engagement_id, client_id, type=’pbc_collection|ocr_review|tagging|je_approval’, assigned_staff_id, status, due_date, priority): Task for PBC or review. *Effort: 3h, Dep: Engagement, Staff*

### Services
- [X] **PolicyEngineService**: Apply layered rules; compute confidence (vendor prior 0.4, MCC 0.2, amount cadence 0.2, weekday 0.1, history 0.1); flag low-confidence (0.6-0.89) for review; persist corrections. *Effort: 6h, Dep: Rule, Correction, PolicyProfile*
- [X] **VendorNormalizationService**: Normalize (strip IDs `/\d{4,}$/`, dates `/\d{1,2}[\/\-]\d{1,2}/`, tokens [POS, ACH, WEB]); map to COA via MCC/NAICS; emit `vendor_canonical.csv`. *Effort: 6h, Dep: VendorCanonical*
- [X] **DataIngestionService**: Sync QBO (COA, txns, vendors, reports: TrialBalance, GLDetail); ingest bank CSVs; handle multi-currency, voided txns, locked books, bank feed lags. *Effort: 7h, Dep: VendorCanonical*
- [X] **CsvIngestionService**: Parse CSVs (regex-based column mapping); validate (missing fields, duplicates); link to `Document`. *Effort: 10h, Dep: Document, DocumentType*
- [X] **DocumentStorageService**: Store documents in S3 (or Postgres BLOBs for MVP); compute SHA-256 hashes; enforce audit trails. *Effort: 5h, Dep: Document*
- [X] **DocumentManagementService**: Categorize documents (OCR or manual); link to `Bill`, `BankTransaction`, or `PayrollBatch`; flag for review (confidence <0.9); archive post-close. *Effort: 6h, Dep: Document, DocumentType*
- [X] **DocumentReviewService**: Manage OCR/tagging review queue; batch by field (e.g., address), type (AP/AR), or client; persist corrections to `Document.extracted_fields`. *Effort: 8h, Dep: Document, DocumentType, Correction*
- [X] **TaskService**: Assign/route PBC collection and review tasks by `Staff.training_level` (junior=simple tagging, senior=complex tagging, manager=JE approval); track status. *Effort: 6h, Dep: Engagement, Task, Staff*
- [X] **PolicyProfileService**: Manage client policies (thresholds, COA maps, pricing tier, doc_volume, ocr_review limit); default: posting $250-$1000, variance 10%, cap $1000-$5000, manual_jes 5-10, ocr_review 10-50. *Effort: 3h, Dep: PolicyProfile*
- [X] **COASyncService**: Pull QBO COA; validate mappings in PolicyProfile; sync changes. *Effort: 3h, Dep: PolicyProfile*

### Routes
- [X] **/api/automation/rules** (GET, POST): Manage rules. *Effort: 2h, Dep: PolicyEngineService*
- [X] **/api/automation/vendors/normalize** (POST): Normalize vendor. *Effort: 2h, Dep: VendorNormalizationService*
- [X] **/api/automation/categorize** (POST): Categorize txns; return suggestions. *Effort: 2h, Dep: PolicyEngineService*
- [X] **/api/automation/corrections** (POST): Submit correction; update rules. *Effort: 2h, Dep: PolicyEngineService*
- [X] **/api/ingest/qbo** (POST): Trigger QBO sync (full/delta). *Effort: 2h, Dep: DataIngestionService, COASyncService*
- [X] **/api/csv/upload** (POST): Ingest CSV with auto-mapping. *Effort: 3h, Dep: CsvIngestionService*
- [X] **/api/csv/validate** (POST): Validate CSV; flag errors. *Effort: 2h, Dep: CsvIngestionService*
- [X] **/api/documents/upload** (POST): Upload documents (PDF, CSV, images). *Effort: 3h, Dep: DocumentStorageService*
- [X] **/api/documents/{id}** (GET, PATCH): View/edit document metadata and extracted fields. *Effort: 3h, Dep: DocumentManagementService, DocumentReviewService*
- [X] **/api/review/documents** (GET, POST): Manage review queue; batch by field/type/client. *Effort: 3h, Dep: DocumentReviewService*
- [X] **/api/tasks** (GET, POST, PATCH): Assign/track PBC and review tasks. *Effort: 3h, Dep: TaskService*

### Templates (React/Tailwind CSS)
- [X] **rule_editor.html**: View/edit rules; three-pane UX (left: rule list, center: form, right: preview). *Effort: 4h, Dep: /api/automation/rules*
- [X] **categorization_queue.html**: Review queue for mid-confidence txns (0.6-0.89); Assertion Chips; three-pane UX (left: lanes [Auto-Post, High $, New Vendor], center: txn details, right: actions [A accept, R recur, X exception]). *Effort: 5h, Dep: /api/automation/categorize*
- [X] **onboarding_queue.html**: Client onboarding (COA, thresholds, policy profile); three-pane UX (left: client list, center: PolicyProfile/COA, right: rule creation). *Effort: 4h, Dep: /api/automation/policies*
- [X] **csv_review.html**: Correct CSV errors (dropdowns for column remapping); three-pane UX (left: CSV list, center: errors, right: actions). *Effort: 5h, Dep: /api/csv/validate*
- [X] **document_manager.html**: Upload/tag/view documents; three-pane UX (left: doc list, center: preview, right: actions [tag, archive]). *Effort: 5h, Dep: /api/documents/upload*
- [X] **document_review.html**: Review OCR/tagging; batch by field (e.g., address), type (AP/AR), or client; Labelbox-like UI (left: doc list, center: preview with editable fields, right: actions [confirm, edit, flag]); integrates with `categorization_queue.html`. *Effort: 6h, Dep: /api/review/documents*
- [X] **task_dashboard.html**: View/assign PBC and review tasks; three-pane UX (left: task list [PBC Collection, OCR Review, Tagging], center: details [due date, staff], right: actions [assign, complete]); Fulcrum-style dragable cards. *Effort: 5h, Dep: /api/tasks*

### Seed Data
- [X] **SQL data**: Rules (100), vendors (200), corrections (10), suggestions (20), PolicyProfile (5 defaults), documents (50), DocumentType (5: invoice, statement, receipt, payroll, bank), engagements (10), tasks (20: PBC collection, OCR review). *Effort: 5h, Dep: Models*
- [X] **CSV templates**: `payroll_template.csv` (Date, Employee, GrossPay, Taxes, Deductions), `bank_template.csv` (Date, Description, Amount), `vendor_template.csv` (Vendor, InvoiceNo, Amount, Date), `invoice_template.csv` (Customer, InvoiceNo, Amount, DueDate). *Effort: 5h*

### Tests
- [X] **Pytest unit tests**: PolicyEngineService, VendorNormalizationService, DataIngestionService, CsvIngestionService, DocumentStorageService, DocumentManagementService, DocumentReviewService (batching), TaskService (routing). *Effort: 10h, Dep: Services*
- [X] **Pytest integration tests**: Routes; mock CSVs/QBO; golden dataset (retail, pro_services, nonprofit). *Effort: 8h, Dep: Routes*

### Documentation
- [X] **OpenAPI/Swagger**: Automation, CSV, document, review, task endpoints. *Effort: 4h, Dep: Routes*
- [X] **README**: Setup for rules, QBO sync, CSV/OCR imports, document storage, review queue, task routing. *Effort: 3h, Dep: None*

### KPIs
- % txns with canonical vendor, % auto-posted (≥0.9 confidence), override rate, false-merge rate (<1%), doc processing time, CSV error rate, OCR review completion time, task completion rate.

## Stage 1A: Accounts Payable (AP) Automation
*Goal*: Automate bill ingestion (OCR/CSV), categorization, payment scheduling, and statement reconciliation, with review queue integration. *Effort: ~45h, Dependencies: Stage 0*

### Models
- [ ] **Vendor** (vendor_id, tenant_id, client_id, canonical_name, qbo_id, w9_status, default_gl_account, terms, fingerprint_hash, canonical_id): Vendor master. *Effort: 2h, Dep: VendorCanonical*
- [X] **Bill** (bill_id, tenant_id, client_id, qbo_id, vendor_id, invoice_no, issue_date, due_date, total, lines[], attachment_refs[], status, rule_id, confidence, suggestion_id): Bill details. *Effort: 3h, Dep: Vendor, Rule, Suggestion, Document*
- [ ] **PaymentIntent** (intent_id, tenant_id, client_id, bill_ids[], provider, total_amount, funding_account, status, issued_at, cleared_at, fees): Payment orchestration. *Effort: 2h, Dep: Bill*
- [ ] **VendorStatement** (statement_id, tenant_id, client_id, vendor_id, period, file_ref, parsed_invoices[], mismatches[]): Statement reconciliation. *Effort: 3h, Dep: Vendor, Document*

### Services
- [X] **BillIngestionService**: Parse email/OCR/CSVs via Tesseract (simple) and Google Cloud Document AI (complex); categorize via PolicyEngineService (80%); store in `Document`; flag for review (confidence <0.9). *Effort: 8h, Dep: Bill, PolicyEngineService, DocumentManagementService, DocumentReviewService*
- [X] **APIngestionService**: Extract bills from QBO/Bill.com; link to `Document`. *Effort: 4h, Dep: Bill, VendorCanonical, Document*
- [ ] **APPaymentService**: Schedule payments via QBO/Bill.com; handle webhook updates (50-70%). *Effort: 4h, Dep: PaymentIntent*
- [ ] **VendorMasteringService**: Dedup via VendorNormalizationService; sync QBO; flag new vendors (confidence <0.6). *Effort: 4h, Dep: Vendor, VendorNormalizationService*
- [ ] **StatementReconciliationService**: Parse statements (CSV/OCR); compare QBO aging (60%); flag for review. *Effort: 5h, Dep: VendorStatement, DocumentManagementService, DocumentReviewService*
- [ ] **CorrectionService**: Convert cockpit corrections to Correction model; feed to PolicyEngineService and DocumentReviewService. *Effort: 4h, Dep: Correction*

### Routes
- [ ] **/api/ap/bills/upload** (POST): Ingest bill (CSV/OCR); flag for review. *Effort: 3h, Dep: BillIngestionService, DocumentReviewService*
- [ ] **/api/ap/bills/{id}** (GET, PATCH): Review/edit; submit correction. *Effort: 3h, Dep: Bill, CorrectionService*
- [ ] **/api/ap/bills/categorize** (POST): Categorize bills. *Effort: 2h, Dep: BillIngestionService*
- [ ] **/api/ap/payments** (POST): Trigger payment. *Effort: 3h, Dep: APPaymentService*
- [ ] **/api/ap/statements/reconcile** (POST): Reconcile statement; flag for review. *Effort: 3h, Dep: StatementReconciliationService, DocumentReviewService*
- [ ] **/api/ap/vendors/{id}** (GET, PATCH): Manage vendor. *Effort: 2h, Dep: VendorMasteringService*

### Templates (React/Tailwind CSS)
- [ ] **bill_review.html**: Three-pane UX (left: bill list, center: details [memo, vendor, suggestion, confidence, document preview], right: actions [A accept, R recur, X exception]); binder status widget; links to `document_review.html` for OCR fixes. *Effort: 4h, Dep: /api/ap/bills/{id}, /api/ap/bills/categorize*
- [ ] **payment_schedule.html**: Approve payments; three-pane UX (left: payment list, center: details, right: actions). *Effort: 3h, Dep: /api/ap/payments*
- [ ] **statement_recon.html**: Diff viewer; three-pane UX (left: statements, center: mismatches, right: actions); links to `document_review.html`. *Effort: 3h, Dep: /api/ap/statements/reconcile*

### Seed Data
- [ ] **SQL data**: Vendors, bills, payment intents, statements, linked documents (50). *Effort: 3h, Dep: Models*

### Tests
- [ ] **Pytest unit tests**: Services; include OCR/CSV parsing, review queue integration. *Effort: 6h, Dep: Services*
- [ ] **Pytest integration tests**: Routes; QBO/Bill.com mocks; golden dataset. *Effort: 5h, Dep: Routes*

### Documentation
- [ ] **OpenAPI/Swagger**: AP endpoints. *Effort: 2h, Dep: Routes*
- [ ] **README**: AP setup, QBO/Bill.com integration, OCR/CSV workflows, review queue. *Effort: 1h, Dep: None*

### KPIs
- % bills auto-categorized, median review time, OCR correction rate, correction propagation rate, QBO write success rate, doc processing time.

## Stage 1B: Accounts Receivable (AR) Automation
*Goal*: Automate invoice creation, collections, payments, adjustments via QBO and CSV, with review queue integration. *Effort: ~35h, Dependencies: Stage 0*

### Models
- [ ] **Customer** (customer_id, tenant_id, client_id, qbo_id, name, email, terms): Customer master. *Effort: 2h, Dep: Firm, Client*
- [ ] **Invoice** (invoice_id, tenant_id, client_id, qbo_id, customer_id, issue_date, due_date, total, lines[], status, attachment_refs[]): Invoice details. *Effort: 2h, Dep: Customer, Document*
- [ ] **Payment** (payment_id, tenant_id, client_id, qbo_id, invoice_ids[], amount, date, method): Payment application. *Effort: 2h, Dep: Invoice*
- [ ] **CreditMemo** (memo_id, tenant_id, client_id, qbo_id, invoice_id, amount, reason): Credit adjustments. *Effort: 2h, Dep: Invoice*

### Services
- [ ] **InvoiceService**: Create invoices from QBO/CSV; sync QBO (80%); flag for review (confidence <0.9). *Effort: 5h, Dep: Invoice, CsvIngestionService, DocumentReviewService*
- [ ] **CollectionsService**: Send AI reminders; track disputes (70%). *Effort: 4h, Dep: Invoice*
- [ ] **PaymentApplicationService**: Auto-match payments (80%). *Effort: 4h, Dep: Payment*
- [ ] **AdjustmentService**: Create memos (80%); flag for review. *Effort: 3h, Dep: CreditMemo, DocumentReviewService*

### Routes
- [ ] **/api/ar/invoices** (POST): Create invoice (QBO/CSV); flag for review. *Effort: 2h, Dep: InvoiceService, DocumentReviewService*
- [ ] **/api/ar/invoices/{id}** (GET, PATCH): Review/edit. *Effort: 2h, Dep: InvoiceService*
- [ ] **/api/ar/collections/remind** (POST): Trigger reminders. *Effort: 2h, Dep: CollectionsService*
- [ ] **/api/ar/payments/apply** (POST): Match payments. *Effort: 2h, Dep: PaymentApplicationService*
- [ ] **/api/ar/credits** (POST): Create memo; flag for review. *Effort: 2h, Dep: AdjustmentService*

### Templates (React/Tailwind CSS)
- [ ] **invoice_review.html**: Cockpit for validation; three-pane UX (left: invoice list, center: details, right: actions); links to `document_review.html`. *Effort: 3h, Dep: /api/ar/invoices/{id}*
- [ ] **collections_dashboard.html**: Overdue status; three-pane UX (left: overdue list, center: details, right: actions). *Effort: 3h, Dep: /api/ar/collections/remind*

### Seed Data
- [ ] **SQL data**: Customers, invoices, payments, memos, linked documents (20). *Effort: 2h, Dep: Models*

### Tests
- [ ] **Pytest unit tests**: Services; include CSV parsing, review queue. *Effort: 5h, Dep: Services*
- [ ] **Pytest integration tests**: Routes; QBO/CSV mocks. *Effort: 4h, Dep: Routes*

### Documentation
- [ ] **OpenAPI/Swagger**: AR endpoints. *Effort: 2h, Dep: Routes*
- [ ] **README**: AR setup, CSV workflows, review queue. *Effort: 1h, Dep: None*

### KPIs
- % invoices auto-applied, collection reminder response rate, OCR correction rate, doc processing time.

## Stage 1C: Bank & Credit Card Transactions
*Goal*: Automate feed matching, manual entries, transfers via QBO bank feeds and CSV, with review queue integration. *Effort: ~30h, Dependencies: Stage 0*

### Models
- [ ] **BankTransaction** (txn_id, tenant_id, client_id, external_id, amount, date, description, account_id, source, status, rule_id, confidence, suggestion_id): Transaction details. *Effort: 2h, Dep: Rule, Suggestion, Document*
- [ ] **Transfer** (transfer_id, tenant_id, client_id, qbo_id, from_account, to_account, amount, date, rule_id): Transfer records. *Effort: 2h, Dep: Rule*

### Services
- [ ] **BankFeedService**: Process CSVs via CsvIngestionService; use QBO bank feeds (Plaid-powered, 90% coverage); normalize descriptors (regex: `/[#*][0-9A-Z]{4,}/`, `/POS|ACH|WEB/`). *Effort: 5h, Dep: BankTransaction, CsvIngestionService*
- [ ] **MatchingService**: Categorize via PolicyEngineService (80%); handle transfers (amount ±$0.01, date ±3 days); flag new vendors; write drafts to QBO; flag for review (confidence <0.9). *Effort: 6h, Dep: BankTransaction, PolicyEngineService, DocumentReviewService*
- [ ] **TransferService**: Record transfers (80%). *Effort: 3h, Dep: Transfer*
- [ ] **CorrectionService**: Feed corrections to PolicyEngineService and DocumentReviewService; update QBO. *Effort: 3h, Dep: Correction*

### Routes
- [ ] **/api/bank/transactions/match** (POST): Match txns; submit corrections; write to QBO. *Effort: 2h, Dep: MatchingService, CorrectionService*
- [ ] **/api/bank/transactions/categorize** (POST): Categorize txns; draft to QBO; flag for review. *Effort: 2h, Dep: MatchingService, DocumentReviewService*
- [ ] **/api/bank/transfers** (POST): Record transfer; sync QBO. *Effort: 2h, Dep: TransferService*

### Templates (React/Tailwind CSS)
- [ ] **bank_matching.html**: Review queue for 0.6-0.89 confidence txns; three-pane UX (left: lanes [High $, New Vendor, Unreconciled], center: txn details [memo, vendor, suggestion, confidence, document preview], right: actions [A accept, R recur, X exception]); links to `document_review.html`; binder status widget. *Effort: 4h, Dep: /api/bank/transactions/categorize*

### Seed Data
- [ ] **SQL data**: Bank txns, transfers, linked documents (20); priors for retail/pro_services/nonprofit. *Effort: 2h, Dep: Models*

### Tests
- [ ] **Pytest unit tests**: Services; include QBO feeds, CSV parsing, regex normalization, review queue. *Effort: 5h, Dep: Services*
- [ ] **Pytest integration tests**: Routes; QBO/CSV mocks; golden dataset. *Effort: 4h, Dep: Routes*

### Documentation
- [ ] **OpenAPI/Swagger**: Bank endpoints. *Effort: 2h, Dep: Routes*
- [ ] **README**: QBO bank feed setup, CSV imports, review queue. *Effort: 1h, Dep: None*

### KPIs
- % txns auto-categorized, % auto-cleared, stale item reduction, QBO sync accuracy, OCR correction rate, doc processing time.

## Stage 1D: Payroll Reconciliation
*Goal*: Automate payroll JE posting and liability reconciliation via CSV/QBO Payroll, with review queue integration. *Effort: ~20h, Dependencies: Stage 0*

### Models
- [ ] **PayrollBatch** (batch_id, tenant_id, client_id, period, gross, net, taxes[], benefits[], attachment_refs[]): Payroll data. *Effort: 2h, Dep: Firm, Client, Document*
- [ ] **PayrollRemittance** (remittance_id, tenant_id, client_id, batch_id, type, amount, date, evidence_ref): Remittance tracking. *Effort: 2h, Dep: PayrollBatch, Document*

### Services
- [ ] **PayrollService**: Ingest payroll CSVs (e.g., ADP, Paychex, manual) or QBO Payroll; map to JEs (70%); flag for review. *Effort: 5h, Dep: PayrollBatch, CsvIngestionService, DocumentReviewService*
- [ ] **RemittanceService**: Track remittances (60%); link to `Document`; flag for review. *Effort: 4h, Dep: PayrollRemittance, DocumentManagementService, DocumentReviewService*

### Routes
- [ ] **/api/payroll/batches** (POST): Import batch (CSV/QBO); flag for review. *Effort: 2h, Dep: PayrollService, DocumentReviewService*
- [ ] **/api/payroll/remittances** (POST): Track remittance; flag for review. *Effort: 2h, Dep: RemittanceService, DocumentReviewService*

### Templates (React/Tailwind CSS)
- [ ] **payroll_review.html**: Cockpit for GL posting; three-pane UX (left: batch list, center: details [JE, document preview], right: actions); links to `document_review.html`. *Effort: 3h, Dep: /api/payroll/batches*

### Seed Data
- [ ] **SQL data**: Payroll batches, remittances, linked documents (10). *Effort: 2h, Dep: Models*

### Tests
- [ ] **Pytest unit tests**: Services; include CSV parsing, review queue. *Effort: 3h, Dep: Services*
- [ ] **Pytest integration tests**: Routes; QBO/CSV mocks. *Effort: 3h, Dep: Routes*

### Documentation
- [ ] **OpenAPI/Swagger**: Payroll endpoints. *Effort: 2h, Dep: Routes*
- [ ] **README**: CSV payroll setup, QBO Payroll integration, review queue. *Effort: 1h, Dep: None*

### KPIs
- % payroll JEs auto-posted, remittance accuracy, OCR correction rate, doc processing time.

## Stage 2: Pre-Close Review and Client Portal
*Goal*: Automate completeness checks, exceptions, PBC tracking, close readiness score, client PBC uploads, and task management. *Effort: ~45h, Dependencies: Stages 0, 1A, 1B, 1C, 1D*

### Models
- [ ] **PreCloseCheck** (check_id, tenant_id, client_id, period, type, status, evidence_refs[]): Completeness checks. *Effort: 2h, Dep: Document*
- [ ] **Exception** (exception_id, tenant_id, client_id, period, type, description, resolution): Exception tracking. *Effort: 2h*
- [ ] **PBCRequest** (request_id, tenant_id, client_id, period, item_type=’bank_stmt|payroll|invoice’, owner, due_date, status, reminders, task_id): PBC items linked to tasks. *Effort: 2h, Dep: Document, Task*
- [ ] **CloseChecklist** (checklist_id, tenant_id, client_id, period, items[], status): Close readiness tracking. *Effort: 2h*

### Services
- [ ] **PreCloseService**: Run checks (bank rec, AR/AP tie-outs, PBC completeness); flag exceptions (80%). *Effort: 5h, Dep: PreCloseCheck, Exception*
- [ ] **PBCTrackerService**: Track PBC items; block close on critical items; compute readiness score (% reconciled, exceptions, missing docs); assign tasks via TaskService. *Effort: 6h, Dep: PBCRequest, CloseChecklist, TaskService*
- [ ] **ClientCommsService**: Email/portal notifications for PBC requests; track responses. *Effort: 3h, Dep: PBCRequest*
- [ ] **ClientPortalService**: Handle client logins, PBC uploads (link to `Document`, `Task`), and close status views. *Effort: 6h, Dep: User, Client, PBCRequest, DocumentStorageService, TaskService*

### Routes
- [ ] **/api/preclose/checks** (POST): Run checks. *Effort: 2h, Dep: PreCloseService*
- [ ] **/api/preclose/exceptions/{id}** (GET, PATCH): Resolve exceptions. *Effort: 2h, Dep: PreCloseService*
- [ ] **/api/preclose/pbc** (GET, POST, PATCH): Manage PBC items; link to tasks. *Effort: 2h, Dep: PBCTrackerService*
- [ ] **/api/close/checklist** (GET, POST): Track close readiness. *Effort: 2h, Dep: PBCTrackerService*
- [ ] **/api/portal/login** (POST): Authenticate users. *Effort: 2h, Dep: ClientPortalService*
- [ ] **/api/portal/pbc/upload** (POST): Client PBC uploads; link to `Document`, `Task`. *Effort: 2h, Dep: ClientPortalService, DocumentStorageService, TaskService*
- [ ] **/api/portal/status** (GET): Show close progress and task status. *Effort: 2h, Dep: ClientPortalService, TaskService*

### Templates (React/Tailwind CSS)
- [ ] **preclose_dashboard.html**: Show checks, exceptions, PBC status, SLA alerts, task assignments; three-pane UX (left: lanes [PBC Missing, Exceptions], center: details, right: actions); binder status widget. *Effort: 4h, Dep: /api/preclose/checks, /api/preclose/pbc*
- [ ] **checklist_view.html**: Close readiness score and checklist status. *Effort: 3h, Dep: /api/close/checklist*
- [ ] **client_portal.html**: Client UI for PBC uploads, close status, task tracking; three-pane UX (left: tasks, center: docs, right: status); Fulcrum-style dragable cards. *Effort: 6h, Dep: /api/portal/pbc/upload, /api/portal/status*

### Seed Data
- [ ] **SQL data**: Checks, exceptions, PBC items, checklists (bank, payroll, invoice), portal users (10), tasks (10). *Effort: 3h, Dep: Models*

### Tests
- [ ] **Pytest unit tests**: Services; include portal auth, PBC uploads, task routing. *Effort: 6h, Dep: Services*
- [ ] **Pytest integration tests**: Routes; mock QBO/CSV; email mocks. *Effort: 5h, Dep: Routes*

### Documentation
- [ ] **OpenAPI/Swagger**: Pre-close, portal, task endpoints. *Effort: 2h, Dep: Routes*
- [ ] **README**: PBC setup, client portal, readiness score, task routing. *Effort: 1h, Dep: None*

### KPIs
- % PBC items on time, close delay days, exception resolution time, readiness score, client upload rate, task completion rate.

## Stage 3: Month-End Close
*Goal*: Automate reconciliations, adjustments, prepaids, cutoffs, approvals; write to QBO; integrate with review queue. *Effort: ~40h, Dependencies: Stages 0, 1A, 1B, 1C, 1D, 2*

### Models
- [ ] **Reconciliation** (recon_id, tenant_id, client_id, period, account_id, gl_end, stmt_end, difference, outstanding[], evidence_refs[], exception_id): Reconciliation data. *Effort: 3h, Dep: Exception, Document*
- [ ] **JournalEntry** (je_id, tenant_id, client_id, qbo_id, period, memo, lines[], evidence_refs[], rule_id, confidence): JE details. *Effort: 2h, Dep: Rule, Document*
- [ ] **Approval** (approval_id, tenant_id, client_id, period, type, status, approver, task_id): Approval tracking linked to tasks. *Effort: 2h, Dep: Staff, Task*
- [ ] **PrepaidSchedule** (schedule_id, tenant_id, client_id, vendor_id, start_date, end_date, amount, monthly_je, status=’draft|confirmed|active’): Prepaid amortization. *Effort: 2h, Dep: Vendor*
- [ ] **CutoffWorksheet** (worksheet_id, tenant_id, client_id, period, type=’payroll|utility|rent’, basis, je_id): Cutoff calculations. *Effort: 2h, Dep: JournalEntry*

### Services
- [ ] **ReconciliationService**: Compare GL vs. statements; auto-clear (amount ±$0.01, date ±3 days, 80%); flag stale items (>60 days). *Effort: 6h, Dep: Reconciliation, PolicyEngineService*
- [ ] **AdjustmentService**: Draft JEs via PolicyEngineService (60-75%); enforce guardrails (no cash/equity); flag manual JEs for Tier 3 upcharge and review; handle cutoffs (payroll: avg_daily_wages × days, utilities: last_bill/days × unbilled_days). *Effort: 6h, Dep: JournalEntry, PolicyEngineService, CutoffWorksheet, DocumentReviewService*
- [ ] **PrepaidService**: Detect prepaids (vendor in insurance/SaaS, regex: `/(From|Coverage).*?\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}/`); create schedules (default 12 months); monthly JEs (DR Expense/CR Prepaid); write to QBO. *Effort: 5h, Dep: PrepaidSchedule, PolicyEngineService*
- [ ] **ApprovalService**: Route approvals (60%) via TaskService; block on PBC missing. *Effort: 4h, Dep: Approval, TaskService*
- [ ] **TieOutService**: Compare AR/AP aging vs. GL; generate AP/AR snapshots; propose JEs for diffs (95% match). *Effort: 5h, Dep: JournalEntry*

### Routes
- [ ] **/api/close/reconciliations** (POST): Run recon; auto-clear; sync QBO. *Effort: 3h, Dep: ReconciliationService*
- [ ] **/api/close/adjustments** (POST): Post JE; write to QBO; flag for review. *Effort: 2h, Dep: AdjustmentService, DocumentReviewService*
- [ ] **/api/close/adjustments/categorize** (POST): Categorize JEs; draft to QBO; flag for review. *Effort: 2h, Dep: AdjustmentService, DocumentReviewService*
- [ ] **/api/close/prepaids/detect** (POST): Detect schedules; draft JEs; write to QBO. *Effort: 2h, Dep: PrepaidService*
- [ ] **/api/close/cutoffs/detect** (POST): Detect cutoffs; draft reversing JEs; write to QBO. *Effort: 2h, Dep: AdjustmentService*
- [ ] **/api/close/approvals** (POST): Submit/approve; link to tasks. *Effort: 2h, Dep: ApprovalService, TaskService*
- [ ] **/api/tieouts/ar|ap** (GET, POST): Run tie-outs; generate snapshots. *Effort: 2h, Dep: TieOutService*

### Templates (React/Tailwind CSS)
- [ ] **close_dashboard.html**: Show JE suggestions, prepaid schedules, cutoff worksheets, anomaly flags, AP/AR snapshots, task assignments; three-pane UX (left: lanes [Prepaids, Cutoffs], center: details, right: actions); binder status widget; links to `document_review.html`. *Effort: 4h, Dep: /api/close/adjustments/categorize, /api/close/prepaids/detect, /api/tieouts/ar|ap*

### Seed Data
- [ ] **SQL data**: Recons, JEs, approvals, prepaid schedules (insurance, SaaS), cutoff worksheets (payroll, utilities), AP/AR snapshots, linked documents (20), tasks (5). *Effort: 3h, Dep: Models*

### Tests
- [ ] **Pytest unit tests**: Services; include guardrails, cutoff/prepaid heuristics, QBO write, review queue. *Effort: 6h, Dep: Services*
- [ ] **Pytest integration tests**: Routes; QBO/CSV mocks; golden dataset. *Effort: 5h, Dep: Routes*

### Documentation
- [ ] **OpenAPI/Swagger**: Close endpoints. *Effort: 2h, Dep: Routes*
- [ ] **README**: Close guide, cutoff/prepaid setup, QBO sync, AP/AR snapshots, task routing. *Effort: 1h, Dep: None*

### KPIs
- % JEs auto-posted, % prepaids confirmed, % cutoffs reversed cleanly, stale item age, tie-out pass rate, QBO sync accuracy, OCR correction rate.

## Stage 4: Close Binder Assembly
*Goal*: Auto-generate binders with proofs, tie-outs, tickmarks, narrative, and commentary; integrate with review queue. *Effort: ~30h, Dependencies: Stages 0-3*

### Models
- [ ] **Binder** (binder_id, tenant_id, client_id, period, format=’excel|pdf’, tabs[], tickmarks[], status): Binder structure. *Effort: 2h, Dep: Document*
- [ ] **Tickmark** (tickmark_id, code=’✓|Δ|A|P|T|V’, description, object_id): Tickmark definitions. *Effort: 2h*
- [ ] **TieOut** (tieout_id, tenant_id, client_id, period, type=’ar|ap’, gl_balance, subledger_balance, diffs[], je_id): Tie-out data. *Effort: 2h, Dep: JournalEntry*

### Services
- [ ] **BinderService**: Generate Excel/PDF (tabs: Cover, Index, Tickmark Legend, Bank, AR, AP, Prepaids, JEs, Exceptions, Close Summary, AP/AR Snapshots); apply tickmarks (✓ reconciled, Δ JE, A accrual, P prepaid, T tie-out, V variance); link documents; flag for review. *Effort: 10h, Dep: Binder, JournalEntry, DocumentManagementService, DocumentReviewService*
- [ ] **TieOutService**: Moved to Stage 3 for dependency alignment. *Effort: 0h*

### Routes
- [ ] **/api/binder/compile** (POST): Generate binder; SHA-256 hash; flag for review. *Effort: 3h, Dep: BinderService, DocumentReviewService*
- [ ] **/api/binder/export** (GET): Export binder (Excel/PDF). *Effort: 3h, Dep: BinderService*

### Templates (React/Tailwind CSS)
- [ ] **binder_view.html**: Preview binder; tickmark legend; diff viewer; narrative display; three-pane UX (left: tabs, center: content, right: actions); binder status widget; links to `document_review.html`. *Effort: 4h, Dep: /api/binder/compile*

### Seed Data
- [ ] **SQL data**: Binders, tie-outs, tickmarks, linked documents (10); golden dataset (retail, pro_services, nonprofit). *Effort: 2h, Dep: Models*

### Tests
- [ ] **Pytest unit tests**: BinderService (tab order, tickmarks, document links, review queue). *Effort: 4h, Dep: Services*
- [ ] **Pytest integration tests**: Routes; mock QBO; golden dataset. *Effort: 3h, Dep: Routes*

### Documentation
- [ ] **OpenAPI/Swagger**: Binder endpoints. *Effort: 2h, Dep: Routes*
- [ ] **README**: Binder setup, tickmark mapping, document linking, review queue. *Effort: 1h, Dep: None*

### KPIs
- First-pass binder acceptance rate, tie-out pass rate, reviewer reformat requests, narrative completeness, doc linking accuracy, OCR correction rate.

## Stage 5: Best Practices for Scaling
*Goal*: Ensure scalability, observability, anti-drift, and advisory insights for Upstate pilot and beyond; include task routing validation. *Effort: ~40h, Dependencies: Stages 0-4*

### Models
- [ ] **WorkflowTemplate** (template_id, tenant_id, client_id, steps[], triggers): Workflow definitions for PBC and review tasks. *Effort: 2h*
- [ ] **Metric** (metric_id, tenant_id, client_id, period, name=’auto_post_rate|handle_time|error_rate|client_satisfaction|ar_creep|margin_compression|ocr_correction_rate|task_completion_rate’, value): KPI tracking. *Effort: 2h*

### Services
- [ ] **WorkflowService**: Orchestrate multi-firm tasks (PBC collection, OCR review); prioritize by materiality/due date; route by `Staff.training_level`. *Effort: 6h, Dep: WorkflowTemplate, TaskService*
- [ ] **ObservabilityService**: Track KPIs (auto-post rate, override rate, PBC delays, OCR correction rate, task completion rate, client satisfaction, AR creep, margin compression); flag drift (>5% suggestion change). *Effort: 8h, Dep: Metric*
- [ ] **BacktestService**: Run golden datasets (retail, pro_services, nonprofit, 3-12 months); regression-test rules and task routing. *Effort: 5h, Dep: PolicyEngineService, TaskService*

### Routes
- [ ] **/api/workflows/templates** (GET, POST): Manage templates. *Effort: 2h, Dep: WorkflowService*
- [ ] **/api/observability/metrics** (GET): Fetch KPIs. *Effort: 2h, Dep: ObservabilityService*
- [ ] **/api/backtest/run** (POST): Run golden dataset; compare outcomes. *Effort: 2h, Dep: BacktestService*

### Templates (React/Tailwind CSS)
- [ ] **workflow_dashboard.html**: Multi-firm queue; three-pane UX (left: lanes [PBC Missing, OCR Review, High $], center: task details, right: actions); KPI trends (AR creep, margin compression, task completion); binder status widget. *Effort: 5h, Dep: /api/observability/metrics, /api/tasks*

### Seed Data
- [ ] **SQL data**: Templates, metrics, tasks (10); golden dataset runner. *Effort: 2h, Dep: Models*

### Tests
- [ ] **Pytest unit tests**: Services; include drift detection, KPI calculations, task routing. *Effort: 5h, Dep: Services*
- [ ] **Pytest integration tests**: Routes; golden dataset validation. *Effort: 4h, Dep: Routes*

### Documentation
- [ ] **OpenAPI/Swagger**: Scaling endpoints. *Effort: 2h, Dep: Routes*
- [ ] **README**: Scaling guide, backtesting setup, KPI definitions, task routing. *Effort: 1h, Dep: None*

### KPIs
- Auto-post volume, drift rate, regression test pass rate, AR creep detection, margin compression alerts, OCR correction rate, task completion rate.

## Industry Packs
- **Retail**: Vendors (Square, Shopify); defaults: POS revenue, sales tax reconciliations; templates: `pos_transactions.csv`, `sales_tax.csv`.
- **Professional Services**: Vendors (Zoom, DocuSign); defaults: T&M accruals, unbilled revenue; templates: `client_invoices.csv`, `expenses.csv`.
- **Nonprofit**: Vendors (donor platforms); defaults: grant tracking, restricted funds; templates: `grants.csv`, `donations.csv`.

## Guardrails
- No auto-post to cash/equity; two-step balance sheet writes; locked periods with adjusting JEs.
- Shadow mode for new rules; change budget (<5% high-confidence flips).
- Feature flags per client; instant rollback.
- SHA-256 hashes for documents; mandatory JE-evidence links.
- Task routing by `Staff.training_level` (junior=simple, senior=complex, manager=approvals).

## Backlog (Stage 5 or Later)
- **Gusto Integration** (~12h): `PayrollService`, `RemittanceService`, `/api/payroll/batches`, `/api/payroll/remittances`, `payroll_review.html` for payroll processing.
- Bill.com Integration
- Google Document AI Integration
- Veryfi Integration
- **Plaid Integration** (~10h): `BankFeedService` standalone Plaid sync, `/api/bank/transactions/sync`.
- **NetSuite/SAP Integration** (~45h): Full ERP support for GL, AP, AR, close workflows.
- **Inventory Management** (~20h): `InventoryService`, `Item`, `InventoryAdjustment`, `/api/inventory/items`, `/api/inventory/adjustments`, `inventory_adjust.html`.
- **ML-Based Normalization** (~15h): NER (Hugging Face `bert-base-NER`) or clustering for vendor canonicalization.
- **Tax Integration** (~30h): Compute tax liabilities or file returns (e.g., 1120, 4562); Drake integration.
- **CRM Modules** (~20h): Integrate with Salesforce/HubSpot.
- **Mobile App** (~25h): Dedicated app for bookkeeper tasks.
- **Cloudfirms.io Features** (~100h): `Service`, `FixedAsset`, `TrialBalance`, `ComplianceCheck`, `Review`, `IntakeRequest`, `QBOConnection`, `ValidationEvent`, `Workpaper`, `WorkpaperAnnotation` for full practice management and tax prep.

## Parking Lot (Phase 3 or Beyond)
- **Variance Narrative Generation** (~10h): Auto-draft explanations for balance swings.
- **Advanced OCR/NLP for Invoices** (~15h): Extract service dates/terms beyond regex (Google Cloud Document AI custom models).
- **Sequence Models for Cadence** (~10h): Detect recurring patterns beyond heuristics.
- **Cloudfirms.io Advanced Features** (~50h): `SystemImprovement`, `AutomationReadiness`, `RoutingService` for ML-driven task routing and automation optimization.

## Effort Summary
- **Total**: ~290h (~6-7 months solo, 3-4 months with 1 SWE + 0.5 data SWE + 0.5 ops/bookkeeper).
- **MVP (Stages 0, 1A, 1B, 1C, 1E, 2)**: ~190h (3-4 months with 2-3 devs).
- **Team**: 1 SWE (backend, FastAPI), 0.5 data SWE (CSV/OCR, datasets), 0.5 ops/bookkeeper (QA, policies).
- **Pilot**: Q4 2025, 1-2 Upstate firms, 3-5 clients, validating CSV/OCR, review queue, PBC scheduling, D+5 closes, advisory deliverables.

## Strategy and Rationale
- **Document Processing**: `CsvIngestionService`, `DocumentStorageService`, `DocumentManagementService`, `DocumentReviewService`, Tesseract, and Google Cloud Document AI support 95% non-API clients, with a review queue for OCR/tagging (batched by field/type/client).
- **Engagement/Task Framework**: `Engagement`, `Task`, `TaskService` enable PBC collection and review task routing, inspired by **Cloudfirms.io** but scoped to MVP needs.
- **Client Portal**: `ClientPortalService` and `client_portal.html` integrate with `TaskService` for PBC uploads and task tracking, reducing firm workload.
- **Price Tiers**: Include OCR/tagging review effort in Tier 2 ($1000/mo, moderate review) and Tier 3 ($2000+/mo, high review), monetizing manual work.
- **Close Scope**: Focuses on bookkeeping, reconciliations, and binders; excludes payroll processing, taxes, and ERPs to align with single-partner firm needs.
- **Future-Proofing**: `Engagement` and `Task` models use foreign keys (`client_id`, `task_id`) to support scaling to practice management without spine rewrite.
- **Pilot**: Upstate focus validates CSV/OCR, review queue, and task routing, building trust for expansion.