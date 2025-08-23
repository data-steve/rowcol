# BookClose Backlog (Post-MVP)

**Overview**: Post-MVP features to extend BookClose beyond Tier 1 (Jobber/Stripe/QBO deposit reconciliation, Uncat expense categorization) and Tier 2 (job-costing) for additional CRMs, payment platforms, Tier 3 advisory features, and schema refactoring. Prioritized for Q1-Q3 2026 after MVP validation (1-2 beta clients, $99–$199/mo).

## Stage 4: Additional CRM & Payment Integrations
*Goal*: Add Housecall Pro, ServiceTitan, JobberPay, Square to support broader service pro market. *Effort: ~50h*
- **Housecall Pro (HCP)**:
  - **Need**: Sync invoices, payments, jobs to QBO for deposit reconciliation, expense categorization, job-costing.
  - **Solution**: Extend `DataIngestionService` for HCP REST API (`/invoices`, `/payments`, `/jobs`). Add `/webhooks/hcp` (`invoice.created`, `payment.created`). Map to `Integration`, `Transaction`, `Job`. Reuse `PolicyEngineService`, `job_cost_dashboard.py`. *Effort: 15h*.
  - **Priority**: High (100K+ users, service pro focus).
- **ServiceTitan (ST)**:
  - **Need**: Sync invoices, payments, timesheets to QBO for Tier 1–2 features.
  - **Solution**: Extend `DataIngestionService` for ST API (`/invoices`, `/payments`, `/timesheets`). Add `/webhooks/servicetitan`. Reuse schema, UI. *Effort: 15h*.
  - **Priority**: High (enterprise service pros, $5M–$10M revenue).
- **JobberPay**:
  - **Need**: Sync JobberPay charges, payouts to QBO for deposit reconciliation.
  - **Solution**: Extend `DataIngestionService` for JobberPay (subset of Jobber API). Add `/webhooks/jobberpay`. Reuse `PolicyEngineService`. *Effort: 10h*.
  - **Priority**: High (native to Jobber, seamless for users).
- **Square**:
  - **Need**: Sync POS payments, payouts to QBO for service pros.
  - **Solution**: Extend `DataIngestionService` for Square API (`/v2/payments`, `/v2/payouts`). Add `/webhooks/square` (`payment.created`). *Effort: 10h*.
  - **Priority**: High (3M+ merchants).
- **Tests**: Update `test_routes.py` for new integrations. Use sandbox data (50 clients, 10 jobs, 20 invoices, 5 payments). *Effort: 5h*.
- **Docs**: Update README for new platforms. *Effort: 2h*.
- **KPIs**: Auto-matched % (70-80%), override rate (<20%), platform adoption (2-3 clients/platform).

## Stage 5: Additional CRM Integrations
*Goal*: Add Salesforce, ServiceM8, Zoho CRM for broader CRM support. *Effort: ~55h*
- **Salesforce Field Service (SFS)**:
  - **Need**: Sync invoices, payments to QBO for service pros ($5M–$10M).
  - **Solution**: Extend `DataIngestionService` for SFS REST API (`/services/data/vXX.0/sobjects/Invoice__c`). Add `/webhooks/salesforce` (`Invoice__c.created`, `Payment__c.created`). Update `test_routes.py`. *Effort: 20h*.
  - **Priority**: Medium-High (100K+ users, QBO focus).
- **ServiceM8**:
  - **Need**: Sync invoices, payments, jobs for smaller service pros ($1M–$5M).
  - **Solution**: Extend `DataIngestionService` for ServiceM8 REST API (`/invoices`, `/payments`). Add `/webhooks/servicem8`. Reuse schema, UI. *Effort: 15h*.
  - **Priority**: Medium (50K+ users, complements Jobber).
- **Zoho CRM**:
  - **Need**: Sync invoices, payments for service pros with e-commerce.
  - **Solution**: Extend `DataIngestionService` for Zoho API (`/crm/v2/invoices`). Add `/webhooks/zoho`. Update `test_routes.py`. *Effort: 20h*.
  - **Priority**: Medium (150K+ users, broader CRM reach).
- **Tests**: Update `test_routes.py` for new integrations. *Effort: 5h*.
- **Docs**: Update README for new platforms. *Effort: 2h*.
- **KPIs**: Auto-matched % (70-80%), override rate (<20%), platform adoption (2-3 clients/platform).

## Stage 6: Month-End Close
*Goal*: Automate reconciliations, adjustments, prepaids, cutoffs. *Effort: ~40h*
- **Models**: `Reconciliation`, `JournalEntry`, `Approval`, `PrepaidSchedule`, `CutoffWorksheet`. *Effort: 5h*.
- **Services**:
  - `ReconciliationService`: Automate bank, AR, AP reconciliations. *Effort: 10h*.
  - `AdjustmentService`: Generate JEs for corrections (`build_qbo_deposit_payload`, `build_qbo_fee_expense_payload`). *Effort: 8h*.
  - `PrepaidService`: Generate monthly recognition schedules (`make_deferred_schedule`). *Effort: 5h*.
  - `ApprovalService`: Route JEs for approval. *Effort: 5h*.
- **Routes**: `/api/close/reconciliations`, `/api/close/adjustments`, `/api/close/prepaids/detect`, `/api/close/cutoffs/detect`. *Effort: 5h*.
- **Templates**: `close_dashboard.py` (Streamlit): Reconciliation status, JE previews. *Effort: 5h*.
- **Tests**: Pytest for services, routes. *Effort: 5h*.
- **Docs**: Update README for close workflows. *Effort: 2h*.
- **KPIs**: % JEs auto-posted (70-80%), % prepaids confirmed (90%).

## Stage 7: Close Binder Assembly
*Goal*: Generate binders with proofs, tie-outs, tickmarks. *Effort: ~30h*
- **Models**: `Binder`, `Tickmark`, `TieOut`. *Effort: 3h*.
- **Services**: `BinderService`: Compile binders (Cover, Index, Tickmark Legend, Bank, AR, AP, Prepaids, JEs, Exceptions). *Effort: 10h*.
- **Routes**: `/api/binder/compile`, `/api/binder/export`. *Effort: 3h*.
- **Templates**: `binder_view.py` (Streamlit): Binder preview, export button. *Effort: 5h*.
- **Tests**: Pytest for BinderService. *Effort: 5h*.
- **Docs**: Update README for binders. *Effort: 2h*.
- **KPIs**: Binder acceptance rate (90%), tie-out pass rate (95%).

## Stage 8: Tier 3 Advisory Features
*Goal*: Add deferred revenue schedules, cash flow forecasting for advisory value. *Effort: ~30h*
- **Deferred Revenue Schedule**:
  - **Need**: Recognize prepaid revenue over time (e.g., 12 months).
  - **Solution**: Use `make_deferred_schedule` for monthly JEs (Deferred Revenue → Revenue). Store in `Transaction`. Add `/api/deferred/schedule` (POST). *Effort: 15h*.
  - **Priority**: Low (niche, advisory-focused).
  - **KPIs**: Schedule accuracy (100%), generation time (<5s).
- **Cash Flow Forecasting**:
  - **Need**: Simple inflow/outflow projections.
  - **Solution**: Build `CashFlowService` using `Transaction` data (inflows: deposits; outflows: expenses, payroll). Add `/api/cashflow/forecast` (GET). Update `job_cost_dashboard.py`. *Effort: 15h*.
  - **Priority**: Low (retention tool).
  - **KPIs**: Forecast accuracy (80%+), client engagement (10-20%).
- **Tests**: Pytest for services, routes. *Effort: 5h*.
- **Docs**: Update README for advisory features. *Effort: 2h*.

## Stage 9: Schema Refactor
*Goal*: Optimize `Integration`, `Transaction`, `Job` for complex CRMs (e.g., Salesforce) and inventory platforms. *Effort: ~10h*
- **Need**: Handle platform-specific fields (e.g., Salesforce `Invoice__c`).
- **Solution**: Normalize fields, add mapping layer in `DataIngestionService`. Update DB schema, tests. *Effort: 10h*.
- **Priority**: Medium (post-MVP, after validating 3-5 CRMs).
- **KPIs**: Schema migration time (<5h), test pass rate (95%).

## Stage 10: Inventory Platform Integrations
*Goal*: Add Katana, Fishbowl for e-commerce/manufacturing service pros. *Effort: ~45h*
- **Katana**:
  - **Need**: Sync sales orders, purchase orders to QBO.
  - **Solution**: Extend `DataIngestionService` for Katana API (`/sales_orders`, `/purchase_orders`). Add `/webhooks/katana`. Reuse `PolicyEngineService`, `job_cost_dashboard.py`. *Effort: 20h*.
  - **Priority**: Low (high Synder overlap).
- **Fishbowl**:
  - **Need**: Sync sales orders, purchase orders for manufacturing-heavy service pros.
  - **Solution**: Extend `DataIngestionService` for Fishbowl API (`/sales_orders`, `/purchase_orders`). Add `/webhooks/fishbowl`. *Effort: 25h*.
  - **Priority**: Low (complex, Synder overlap).
- **Tests**: Update `test_routes.py`. *Effort: 5h*.
- **Docs**: Update README for inventory platforms. *Effort: 2h*.
- **KPIs**: Auto-matched % (70-80%), platform adoption (1-2 clients).

## Additional Features
- **Gusto Integration** (~12h): `PayrollService`, `/api/payroll/batches`, `/api/payroll/remittances`, `payroll_review.html` for payroll processing.
- **Bill.com Integration** (~10h): `BillService`, `/api/bills/sync` for AP automation.
- **Google Document AI** (~10h): Advanced OCR for receipts/invoices.
- **Veryfi Integration** (~10h): Receipt processing with AI.
- **Plaid Integration** (~10h): `BankFeedService`, `/api/bank/transactions/sync` for bank feed sync.
- **NetSuite/SAP Integration** (~45h): ERP support for GL, AP, AR, close workflows.
- **Inventory Management** (~20h): `InventoryService`, `Item`, `InventoryAdjustment`, `/api/inventory/items`, `/api/inventory/adjustments`, `inventory_adjust.html`.
- **ML-Based Normalization** (~15h): NER (Hugging Face `bert-base-NER`) or clustering for vendor canonicalization.
- **Tax Integration** (~30h): Compute tax liabilities (e.g., 1120, 4562); Drake integration.
- **CRM Modules** (~20h): Salesforce/HubSpot for client management.
- **Mobile App** (~25h): Bookkeeper task management app.
- **Variance Narrative Generation** (~10h): Auto-draft explanations for balance swings.
- **Advanced OCR/NLP for Invoices** (~15h): Extract service dates/terms (Google Cloud Document AI).

## Validation Plan
- **Timeline**: Q1-Q3 2026, post-MVP (1-2 beta clients).
- **Steps**:
  1. Add Housecall Pro, ServiceTitan, JobberPay, Square (Q1 2026, ~50h).
  2. Test with 3-5 SC clients (5-10 jobs each, $99–$199/mo). *Effort: 20h*.
  3. Add Salesforce, ServiceM8, Zoho CRM (Q2 2026, ~55h).
  4. Refactor schema for scalability (Q2 2026, ~10h).
  5. Implement month-end close, binder assembly (Q2 2026, ~70h).
  6. Add Tier 3 advisory features (Q3 2026, ~30h).
  7. Evaluate Katana/Fishbowl based on beta feedback (Q3 2026, ~45h).
- **KPIs**: Auto-matched % (70-80%), override rate (<20%), client retention (80%+), platform adoption (2-3 clients/platform).