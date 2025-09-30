# RowCol Build Plan (Runway MVP and Close Add-On)

## Overview
RowCol is a QBO-integrated tool for vCFO/bookkeeping firms (5–50 clients) serving agencies ($1–$15M revenue, 10–50 FTE) without internal CFOs. RowCol Runway (MVP, $500–$1,500/mo) delivers batch weekly runway rituals and Smart Collections, launching Q4 2026 (~200 hours). RowCol Close (add-on, $99–$199/mo) adds Numeric-style monthly close checklists, deploying 2027 (~150 hours). QBO Payments handles payments, and QBO Agents manage 80–90% categorization. Codebase: ~70–80 files, reusing Oodaloo’s ~50–60 files and ~20–30 `_parked` files (e.g., `vendor_normalization.py`, `preclose.py`).

## Architecture
- **QBO Primitives Layer (`domains`)**: Reuse Oodaloo’s `ap`, `ar`, `bank`, `core`, `policy`, `webhooks`.
- **Orchestration Layer (`runway`)**: Firm-focused logic for batch runway, Smart Collections, close checklists.
- **Database**: Extend Oodaloo’s schema with `staff`, `role_assignment`, `close_checklist`, `engagement`, `pbc_request`.
- **Frontend**: React/Jinja2 for `dashboard.html`, `categorization.html`, `close_checklist.html`, `engagement.html`.

## RowCol Runway MVP (200 Hours, $500–$1,500/mo, Q4 2026)
### Objective
Deliver batch runway rituals and Smart Collections for 5–50 clients, with RBAC and basic analytics, reusing Oodaloo’s codebase.

### Task Breakdown
- **Week 1–3: Batch Runway and RBAC (80 hours)**:
  1. Extend `runway/services/digit.py` for batch prep (5–50 clients):
     - Metrics: Runway, AR (>30/45d), AP (due ≤14d), exceptions.
     - Role-aware: Lead bookkeeper (all clients), staff (assigned), client (own data).
  2. Create `runway/templates/dashboard.html` (React/Jinja2, multi-client filters: client, period, status).
  3. Extend `domains/core/models/user.py` for RBAC (roles: lead bookkeeper, staff, client, vCFO).
     - Schema: `domains/core/schemas/user.py` (add `RoleAssignment`).
     - Table: `role_assignment` (fields: `firm_id`, `user_id`, `client_id`, `permission_level`).
  4. Extend `runway/services/notification.py` for email alerts (e.g., task assignments).
  5. Tests: `runway/tests/test_batch_digest.py`, `test_rbac.py`.
- **Week 4–6: Batch Smart Collections (60 hours)**:
  1. Reuse `_parked/ar/services/collections.py`, `runway/services/drip.py` for batch drips:
     - 3-email sequence for 5–50 clients, triggered at due date or >30/45d.
     - Use QBO Payments “Pay Now” link.
  2. Extend `runway/models/drip_campaign.py`, `runway/templates/drip.html`.
  3. Add `runway/services/currency_check.py`:
    - Flag currency mismatches in Batch Runway Rituals (e.g., “$5,000 CAD deposit vs. $3,800 USD invoice”) by comparing `invoice.py` amounts with `bank_transaction.py` currency codes.
    - Surface alerts in `runway/templates/dashboard.html` for CAS firm review.
    - Test: `runway/tests/test_currency_check.py` with multi-currency mock data.
  4. Create `runway/services/automation.py`:
     - Prioritize invoices >$5k or top 10% of AR.
     - Pause drips on full/partial payments.
  5. Tests: `runway/tests/test_batch_drip.py`.
- **Week 7–8: Transaction Categorization (40 hours)**:
  1. Reuse `_parked/ap/vendor_normalization.py` for batch categorization.
  2. Extend `runway/services/tray.py` for 5–50 clients with QBO Agent suggestions.
  3. Create `runway/templates/categorization.html` (React/Jinja2).
  4. Tests: `runway/tests/test_batch_categorization.py`.
- **Week 9: Basic Analytics and Compliance (20 hours)**:
  1. Create `runway/services/analytics.py` for AR/AP aging (30/60/90d).
     - Reuse `_parked/core/services/kpi.py`.
  2. Create `runway/templates/analytics.html`, `runway/routes/analytics.py`.
  3. Enhance `domains/core/models/audit_log.py` for SOC 2-like logging.
  4. Add `runway/services/tax_flagging.py`:
    - Identify potential tax-related deposits (e.g., “$1,000 deposit with tax code”) in Batch Runway Rituals by analyzing `bank_transaction.py` for tax metadata (e.g., 1099, VAT).
    - Flag in `runway/templates/analytics.html` for CAS firm bookkeeper allocation.
    - Test: `runway/tests/test_tax_flagging.py` with tax mock data.
  5. Tests: `runway/tests/test_analytics.py`, `test_audit_log.py`.

### Success Metrics
- 3–5 hours/client/week saved.
- 80%+ drip campaign engagement.
- 10–20 CAS firms as early adopters.

## RowCol Close Add-On (150 Hours, $99–$199/mo, 2027)
### Objective
Add Numeric-style monthly close checklists, reusing `_parked/close/preclose.py` for reconciliations, JEs, and financial statements.

### Task Breakdown
- **Close Checklists (100 hours)**:
  1. Reuse `_parked/close/services/preclose.py` for:
     - Reconcile bank, AR, AP, credit cards.
     - Draft JEs for accruals (prepaid expenses, payroll).
     - Generate Balance Sheet, P&L, Cash Flow.
  2. Create `runway/services/close_checklist.py`, `runway/models/close_checklist.py` (fields: `firm_id`, `client_id`, `period`, `tasks`, `status`).
  3. Create `runway/templates/close_checklist.html`, `runway/routes/close_checklist.py`.
  4. Tests: `runway/tests/test_close_checklist.py`.
- **Engagement Management (50 hours)**:
  1. Reuse `_parked/core/models/engagement.py`, `_parked/core/services/engagement.py` for onboarding/scoping.
  2. Reuse `_parked/close/services/preclose.py` for PBC tracking (`runway/services/pbc.py`).
  3. Reuse `_parked/core/services/task.py` for staff assignments.
  4. Create `runway/templates/engagement.html`, `runway/routes/engagement.py`, `pbc.py`.
  5. Tests: `runway/tests/test_engagement.py`, `test_pbc.py`.

### Success Metrics
- 90%+ close checklist completion.
- 80%+ engagement adoption.

## Constraints
- **Budget**: ~350 hours total (Runway: 200, Close: 150), contractor support post-Oodaloo.
- **Timeline**: Runway (Q4 2026), Close (2027).
- **Codebase**: ~70–80 files, reusing Oodaloo and `_parked`.

## Risks and Mitigations
- **Risk**: ClientHub/Keeper copy runway ritual.
  - **Mitigation**: Launch RowCol Runway by Q4 2026, leveraging Oodaloo’s brand.
- **Risk**: QBO Agent limitations.
  - **Mitigation**: Manual categorization fallback in `tray.py`.