# Updated Architecture Requirements Changes for Escher and BookClose

## Context and New Angle
The updated **BookClose Plan** (artifact_id="71fb2e5b-b639-4413-845b-6f2cc38c1c15") is a strong foundation but needs adjustments to align with targeting single-partner or double-partner SC accounting firms (1-5 staff, 10-50 clients, <200 txns/mo) in the Upstate, with a focus on document-heavy workflows (51% spreadsheets, 21% paper per SMB Group 2025). Key priorities include:
- Exploiting **OCR and CSV processing** as a competitive edge for non-API systems (95% of SC clients).
- Incorporating **paper-heavy requirements** into **price tiering**.
- Adding **document storage and management** to support audit-readiness.
- Enhancing **client portal** and data models (user, firm, client, staff, document, document_type).
- Clarifying **close management scope** (what we do vs. don’t do), limited by automation (60-75% for close, 80% for bookkeeping) and aligned with firm needs, with upcharges for manual work.
- Deprioritizing non-essential APIs (Gusto, Plaid, NetSuite, SAP) to Stage 5 or Backlog.
- Excluding payroll processing; focusing on **payroll reconciliation** via CSV/QBO Payroll.

## Confirmation on COASyncService
- **Retained**: `COASyncService` is critical for MVP (Stage 0, ~3h). It pulls client Chart of Accounts (COA) from QBO, validates mappings in `PolicyProfile`, and syncs changes, ensuring accurate transaction categorization and GL posting for 80% of SC clients using QBO. The service wasn’t dropped; it’s explicitly listed in Stage 0 (Services, Routes: `/api/ingest/qbo`). Its absence in some stages (e.g., 1A, 1C) is appropriate, as it’s a foundational service used across workflows.

## Changes to Architecture Requirements
Below are the specific changes needed to align the **BookClose Plan** with the new angle, preserving its integrity (e.g., tech stack, QBO focus, 137h MVP):

1. **Incorporate Paper-Heavy Requirements into Price Tiering**:
   - **Add**: Define pricing tiers based on document volume and complexity in **Escher Strategy** (artifact_id="443fa241-3dd6-4950-9748-6f224e1a498e") and **Firm One-Pager** (artifact_id="ff9bfab4-4e8c-4d71-8d4a-dac8c36de67c").
     - **Tier 1 ($500/mo)**: Low document volume (<50 docs/mo, e.g., QBO-native clients), 80% automation via QBO/Bill.com APIs.
     - **Tier 2 ($1000/mo)**: Medium volume (50-200 docs/mo, e.g., QuickBooks Desktop, CSV uploads), 60-75% automation with OCR/CSV.
     - **Tier 3 ($2000+/mo)**: High volume (>200 docs/mo, e.g., paper-heavy retail, manual payroll), 50-60% automation, upcharge for manual review (e.g., complex JEs, missing PBCs).
   - **Effort**: Update strategy docs (~2h), add pricing logic to `PolicyProfile` (client-specific thresholds for doc volume, ~1h).
   - **Impact**: Aligns pricing with document processing effort, appealing to single-partner firms with varied client needs.

2. **Add Document Storage and Management**:
   - **Add Models**:
     - **Document** (doc_id, tenant_id, client_id, period, type=’invoice|statement|receipt|payroll’, file_ref, hash, upload_date, status=’pending|processed|archived’): Store uploaded/scanned documents.
     - **DocumentType** (type_id, name, fields[], required=’y|n’, validation_rules): Define document formats (e.g., invoice: vendor, amount, date).
   - **Add Services**:
     - **DocumentStorageService**: Store documents in S3 (or Postgres BLOBs for MVP), compute SHA-256 hashes, enforce audit trails (Stage 0, ~5h).
     - **DocumentManagementService**: Categorize documents (via OCR or manual tagging), link to `Bill`, `BankTransaction`, or `PayrollBatch`, archive post-close (Stage 1A, ~5h).
   - **Add Routes**:
     - `/api/documents/upload` (POST): Upload documents (PDF, CSV, images).
     - `/api/documents/{id}` (GET, PATCH): View/edit document metadata.
   - **Add Template**:
     - `document_manager.html`: UI for uploading, tagging, and viewing documents; three-pane UX (left: doc list, center: preview, right: actions [tag, archive]).
   - **Effort**: ~15h (Stage 0: models/routes/storage, 7h; Stage 1A: management/template, 8h).
   - **Impact**: Ensures audit-ready storage (Evidence Locker), supports paper-heavy clients (21% paper, 51% spreadsheets).

3. **Enhance Client Portal and Data Models**:
   - **Add Models**:
     - **User** (user_id, tenant_id, role=’admin|staff|client’, email, permissions): Manage firm staff and client access.
     - **Firm** (tenant_id, name, qbo_id, pricing_tier, doc_volume): Track firm-level settings.
     - **Client** (client_id, tenant_id, name, qbo_id, industry=’retail|pro_services|nonprofit’, policy_profile_id): Client-specific configs.
     - **Staff** (staff_id, tenant_id, user_id, role=’bookkeeper|manager’): Firm staff roles.
   - **Add Services**:
     - **ClientPortalService**: Handle client logins, PBC uploads, and notifications (Stage 2, ~5h).
   - **Add Routes**:
     - `/api/portal/login` (POST): Authenticate users.
     - `/api/portal/pbc/upload` (POST): Client PBC uploads (link to `Document`).
     - `/api/portal/status` (GET): Show close progress (readiness score, missing PBCs).
   - **Add Template**:
     - `client_portal.html`: Client-facing UI for PBC uploads, close status, and notifications; three-pane UX (left: tasks, center: docs, right: status).
   - **Effort**: ~15h (Stage 0: models, 5h; Stage 2: portal service/routes/template, 10h).
   - **Impact**: Enables client interaction (PBC uploads), supports firm/staff management, and aligns with single-partner firm needs (10-50 clients).

4. **Clarify Close Management Scope (What We Do vs. Don’t Do)**:
   - **What We Do**:
     - **Bookkeeping**: Categorize transactions (80% automation via QBO/Bill.com APIs, CSV uploads), reconcile bank/CC (90%), manage AP/AR (80%), and normalize vendors (Stage 0, 1A, 1C, 1B).
     - **Close Management**: Reconcile subledgers to GL (80%), draft JEs (60-75%), detect prepaids/cutoffs (70%), generate trial balances, produce audit-ready binders (BS, IS, JEs, tickmarks: ✓=reconciled, Δ=JE), and provide advisory insights (close readiness score, AP/AR snapshots, narratives) (Stages 2-4).
     - **Payroll Reconciliation**: Post payroll JEs and reconcile liabilities (Stage 1E, via CSV or QBO Payroll, 70% automation).
   - **What We Don’t Do**:
     - **Payroll Processing**: No wage calculations, tax filings, or benefits management (e.g., no Gusto for payroll runs).
     - **Tax Preparation**: No tax liability calculations or filings (e.g., Form 941, sales tax).
     - **Complex ERP Workflows**: No full NetSuite/SAP integrations (e.g., multi-entity consolidations, custom modules).
     - **Non-Standard JEs**: Complex accruals, intercompany transfers, or manual adjustments beyond automation limits require upcharge (Tier 3 pricing).
   - **Technical Limits**:
     - Automation capped at 60-75% for close tasks due to manual review needs (complex JEs, missing PBCs).
     - Non-API systems (95% of SC clients) rely on CSV uploads and OCR (Tesseract for simple, Google Cloud Document AI for complex).
     - Manual work (e.g., reviewing low-confidence txns, custom JEs) triggers Tier 3 upcharges ($2000+/mo).
   - **Alignment with Firm Needs**:
     - Single-partner firms need fast, audit-ready closes (D+5, <5 review notes) for retail, professional services, and nonprofit clients.
     - CSV/OCR workflows support their document-heavy reality (51% spreadsheets, 21% paper).
     - Advisory deliverables (AR creep, margin compression) add value, encouraging buy-in.
   - **Effort**: Update **Escher Strategy** and **Firm One-Pager** to clarify scope and upcharges (~2h). Add `PolicyProfile` fields for manual work thresholds (e.g., max_manual_jes, ~1h).
   - **Impact**: Sets clear expectations, aligns automation with firm budgets, and monetizes manual work.

5. **Refocus on Single/Double-Partner Firms**:
   - **Adjust Scope**: Target firms with 1-5 staff, 10-50 clients (<200 txns/mo, 1-2 entities). Focus on retail, professional services, and nonprofits, common in Upstate.
   - **Simplify Workflows**: Prioritize simple GLs (10-50 accounts), single-entity closes, and document-heavy clients (CSV uploads, scanned invoices).
   - **Pilot Strategy**: Q4 2025 pilot with 1-2 firms (3-5 clients), validating CSV/OCR workflows and D+5 closes.
   - **Effort**: Update **Escher Strategy** for Upstate focus (~1h). Adjust `PolicyProfile` for simpler COA mappings (~1h).
   - **Impact**: Builds trust with smaller firms, leverages relationship grace for iterative improvements.

6. **Elevate OCR and CSV Processing**:
   - **Add OCR**:
     - **Tesseract + OpenCV**: Basic OCR for simple invoices/receipts (vendor, amount, date) in Stage 1A (~5h).
     - **Google Cloud Document AI**: Advanced OCR for complex documents (multi-page invoices, tables) in Stage 1A (~10h).
   - **Enhance CSV**:
     - Update `DataIngestionService` to handle varied CSV formats (regex-based column mapping, e.g., “Amount” vs. “Total”) and validate data (missing fields, duplicates) (Stage 0, ~10h).
     - Add `CsvIngestionService` for robust CSV parsing across AP, AR, bank, and payroll (Stage 0, ~10h).
     - Create templates: `payroll_template.csv`, `bank_template.csv`, `vendor_template.csv`, `invoice_template.csv` for retail, professional services, nonprofits (~5h).
   - **Add Routes**:
     - `/api/csv/upload` (POST): Ingest CSV with auto-mapping.
     - `/api/csv/validate` (POST): Validate and flag errors.
   - **Add Template**:
     - `csv_review.html`: UI for CSV error correction (dropdowns for column remapping, ~5h).
   - **Effort**: ~45h (Stage 0: CSV services/routes/templates, 25h; Stage 1A: OCR, 15h; templates, 5h).
   - **Impact**: Supports 95% of non-API clients (QuickBooks Desktop, Sage, manual ledgers), positioning Escher as a document processing leader.

7. **Deprioritize Non-Essential APIs**:
   - **Gusto**: Move `PayrollService` and `RemittanceService` (Stage 1E) to **Backlog**. Replace with CSV-based payroll reconciliation (~5h, Stage 1E).
   - **Plaid**: Move `BankFeedService` Plaid integration (Stage 1C) to **Backlog**. Use QBO’s native bank feeds (Plaid-powered, 90% coverage) for MVP (~2h adjustment).
   - **NetSuite/SAP**: Move to **Backlog** for Stage 5. Support via CSV uploads for read-only GL data in MVP (~5h).
   - **Effort**: ~12h (adjust Stage 1E for CSV, 5h; adjust Stage 1C for QBO feeds, 2h; CSV for NetSuite/SAP, 5h).
   - **Impact**: Reduces MVP scope (~137h), focuses on QBO/Bill.com and CSV/OCR.

8. **Lower Automation Expectations**:
   - **Bookkeeping**: Keep 80% automation for transaction categorization and reconciliations (Stages 0, 1A, 1C).
   - **Close Management**: Adjust to 60-75% automation (Stages 2-3) due to manual review for complex JEs, missing PBCs. Update `PolicyEngineService` and `AdjustmentService` to flag low-confidence items (0.6-0.89) for review (~2h).
   - **Effort**: ~2h (update services for review flagging).
   - **Impact**: Aligns with technical limits and firm expectations, reducing over-automation risk.

9. **Regional Strategy**:
   - **Add**: Pilot plan for Upstate single/double-partner firms (1-2 firms, 3-5 clients, Q4 2025). Validate CSV/OCR workflows, D+5 closes, and advisory deliverables (AR creep, margin compression).
   - **Effort**: Add pilot plan to **Escher Strategy** (~2h).
   - **Impact**: Ensures early feedback from smaller firms, builds trust for expansion.

## Backlog and Parking Lot Updates
### Moved to Backlog (Out-of-Scope for MVP, Stage 5 or Later)
- **Gusto Integration** (Stage 1E, ~12h):
  - `PayrollService`, `RemittanceService`, `/api/payroll/batches`, `/api/payroll/remittances`, `payroll_review.html`.
  - **Reason**: Only 10-15% of SC clients use Gusto. CSV uploads and QBO Payroll cover 90% of payroll reconciliation needs.
- **Plaid Integration** (Stage 1C, ~10h):
  - `BankFeedService` Plaid-specific code, `/api/bank/transactions/sync`.
  - **Reason**: QBO’s native bank feeds (Plaid-powered) cover 90% of bank/CC reconciliation needs. Standalone Plaid is a nice-to-have for non-QBO banks.
- **NetSuite/SAP Integration** (Stage 5, ~45h):
  - Full ERP integrations for GL, AP, AR, and close workflows.
  - **Reason**: Only 10-15% of SC clients use NetSuite/SAP. CSV uploads suffice for MVP.
- **Inventory Management** (Stage 1D, ~20h):
  - `InventoryService`, `Item`, `InventoryAdjustment`, `/api/inventory/items`, `/api/inventory/adjustments`, `inventory_adjust.html`.
  - **Reason**: Limited relevance for single-partner firm clients (retail, professional services, nonprofits). CSV uploads can handle basic inventory adjustments.
- **ML-Based Normalization** (Parking Lot, moved to Backlog):
  - NER (Hugging Face `bert-base-NER`) or clustering for vendor canonicalization.
  - **Reason**: Rules-based `VendorNormalizationService` achieves 80% automation. ML requires ~50k labeled txns, deferred to post-MVP.

### Moved to Parking Lot (Phase 3 or Beyond)
- **Variance Narrative Generation** (Stage 4, ~10h):
  - Auto-draft explanations for balance swings (e.g., vendor mix, one-time charges).
  - **Reason**: Manual narratives suffice for MVP; ML-driven narratives need training data.
- **OCR/NLP for Invoices** (Stage 1A, ~15h):
  - Extract service dates/terms beyond regex (e.g., Google Cloud Document AI custom models).
  - **Reason**: Tesseract + Google Cloud Document AI covers 90% of invoice parsing needs.
- **Sequence Models for Cadence** (Stage 0, ~10h):
  - Detect recurring patterns beyond heuristics.
  - **Reason**: Heuristics in `PolicyEngineService` achieve 80% categorization; sequence models are overkill for MVP.
- **Tax Integration** (Backlog, unchanged):
  - Compute tax liabilities or file returns.
  - **Reason**: Out-of-scope for close management; firms handle taxes separately.
- **CRM Modules** (Backlog, unchanged):
  - Integrate with Salesforce/HubSpot.
  - **Reason**: Not needed for single-partner firm clients.
- **Mobile App** (Backlog, unchanged):
  - Dedicated app for bookkeeper tasks.
  - **Reason**: Web-based `client_portal.html` and `categorization_queue.html` suffice for MVP.

## Integrity Check
- **COASyncService**: Retained in Stage 0 (Services, Routes: `/api/ingest/qbo`) and used across stages (1A, 1C, 2-3) for COA mapping and QBO sync. No changes needed.
- **Plan Structure**: Preserves tech stack (Python, FastAPI, Postgres, React/Tailwind), QBO/Bill.com focus, and MVP scope (~137h, Stages 0, 1A, 1C, 2). Adjustments enhance CSV/OCR and add document storage/portal without disrupting workflow.
- **Dependencies**: New models (Document, DocumentType, User, Firm, Client, Staff) integrate with existing `PolicyProfile`, `Bill`, and `BankTransaction`. No conflicts with current routes/services.

## Next Steps
- **Share Updated Dev Plan**: Paste your manually synced plan (if further changes made), and I’ll update it to include OCR/CSV enhancements, document storage, client portal, price tiering, and scope clarifications.
- **Specify Action**: Reply with a focus, e.g., “Outline CsvIngestionService specs,” “Design document_manager.html,” or “Draft pilot survey for Upstate firms.”
- **Document Processing**: I can create CSV templates (`payroll_template.csv`) or OCR workflows (Tesseract/Google Cloud Document AI) if prioritized.
- **Close Scope**: I can update **Firm One-Pager** to clarify what Escher does/doesn’t do and highlight OCR/CSV strengths.