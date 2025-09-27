# RowCol Strategy, Requirements, and Build Plan

## Preamble
RowCol is a QBO-integrated tool for vCFO/bookkeeping firms (5–50 clients) serving agency clients ($1–$15M revenue, 10–50 FTE) without internal CFOs. It focuses on accrual accounting, delivering weekly cash runway rituals (leveraging Oodaloo’s `runway/services/digest.py`, `tray.py`) and Numeric-style monthly close checklists, with batch processing, RBAC, engagement management, and Fathom-style analytics (forecasting, KPIs). RowCol assumes QBO Agents handle 80–90% of transaction categorization, enabling focus on close management and strategic advice. It reuses Oodaloo’s `domains` layer (`ap`, `ar`, `bank`, `core`, `policy`, `webhooks`) and `_parked` files (e.g., `preclose.py`, `vendor_normalization.py`, `task.py`) to save 3–5 hours/client/week. Planned for Oodaloo’s Phase 3 (2027) or as a separate product.

## Product Vision
RowCol streamlines vCFO/bookkeeping workflows for accrual accounting, managing 5–50 agency clients with weekly runway digests, monthly close checklists, and analytics (e.g., cash flow forecasting, AR/AP aging, KPIs). It supports batch processing, RBAC (lead bookkeeper, staff, client, vCFO), engagement scoping, and PBC tracking, integrating with QBO (read/write, webhooks) for seamless operations.

## Target Persona
- **Primary**: vCFO/bookkeeping firms (5–50 clients, 2–10 staff) serving agencies ($1–$15M revenue, 10–50 FTE). Lead bookkeepers assign tasks, staff prep data, clients approve, vCFOs review and advise.
- **Secondary**: Agency owner clients, accessing dashboards for approvals and insights.
- **Needs**:
  - Weekly cash flow clarity (runway, AR, AP).
  - Monthly close rigor (reconciliations, JEs, financial statements).
  - Engagement management (onboarding, scoping, PBCs).
  - Analytics for strategic advice (forecasting, KPIs).

## Strategy
- **Focus**: Deliver accrual-accounting workflows for vCFO/bookkeeping firms, reusing Oodaloo’s runway ritual for weekly cash flow and adding firm-centric features (batch processing, RBAC, close checklists, analytics). Assume QBO Agents handle 80–90% of transaction categorization.
- **Distribution**: QBO App Store or direct sales to CAS firms.
- **Pricing**: $500–$1,500/mo (per-org + per-seat). Add-ons ($49–$99/mo) for advanced analytics, close automation, PBC tracking.
- **Extensibility**: Reuse Oodaloo’s `domains` and `_parked` files (e.g., `preclose.py`, `vendor_normalization.py`, `task.py`) for close, categorization, and engagement workflows.
- **Success Metrics**:
  - 3–5 hours/client/week saved.
  - 90%+ close checklist completion rate.
  - 80%+ analytics engagement (e.g., forecasting views).
  - 10–20 CAS firms as early adopters by 2027.

## Requirements

### Core Features (Phase 3 or Separate, $500–$1,500/mo, 2027)
- **Weekly Runway Ritual**:
  - Batch digest prep for 5–50 clients (Cash Runway, AR, AP, exceptions), reusing Oodaloo’s `runway/services/digest.py`, `tray.py`.
  - Multi-client dashboard (`runway/templates/dashboard.html`) with RBAC (lead bookkeeper, staff, client, vCFO).
  - Notifications: Emails/Slack for task assignments and client approvals.
- **Monthly Close Checklist**:
  - Numeric-style checklist (`runway/services/close_checklist.py`, reusing `_parked/close/services/preclose.py`):
    - Reconcile bank accounts, AR, AP, credit cards.
    - Post JEs for accruals (e.g., prepaid expenses, payroll, depreciation).
    - Generate Balance Sheet, P&L, Cash Flow.
    - Flag discrepancies (e.g., unmatched transactions, missing accounts).
  - UI: `runway/templates/close_checklist.html` (React/Jinja2).
  - Automation: Draft JEs using QBO Agents (80–90% accuracy for revenue/expenses).
- **Transaction Categorization**:
  - Batch categorization for unmatched transactions, reusing `_parked/ap/vendor_normalization.py`.
  - Leverage QBO Agents for account/customer suggestions.
  - UI: `runway/templates/categorization.html` (React/Jinja2).
- **Engagement Management**:
  - Client onboarding and scoping (`runway/services/engagement.py`, reusing `_parked/core/models/engagement.py`).
  - PBC tracking (`runway/services/pbc.py`, reusing `_parked/close/services/preclose.py`).
  - Task assignment for staff (`runway/services/task.py`, reusing `_parked/core/services/task.py`).
- **Analytics (Fathom-Style)**:
  - Cash flow forecasting (6–12 months, based on runway trends).
  - AR/AP aging reports (30/60/90d buckets).
  - KPIs (e.g., burn rate, profitability, liquidity ratios).
  - UI: `runway/templates/analytics.html` (React/Jinja2).
- **QBO Integration**:
  - Read/write API calls (`Invoice.Send`, `BillPayment`, `JournalEntry`) with batch endpoint optimization (120 requests/minute).
  - Webhooks for sync (`domains/webhooks/routes.py`).
- **Compliance**:
  - SOC 2-like audit logs (`domains/core/models/audit_log.py`).
  - RBAC for lead bookkeeper, staff, client, vCFO roles.

### Technical Requirements
- **Database**: Extend Oodaloo’s schema with:
  - `staff` (fields: `firm_id`, `user_id`, `role`).
  - `role_assignment` (fields: `firm_id`, `user_id`, `client_id`, `permission_level`).
  - `close_checklist` (fields: `firm_id`, `client_id`, `period`, `tasks`, `status`).
  - `engagement` (fields: `firm_id`, `client_id`, `scope`, `start_date`, `status`).
  - `pbc_request` (fields: `firm_id`, `client_id`, `period`, `item_type`, `status`, `task_id`).
  - Reuse `firm`, `client`, `bill`, `invoice`, `bank_transaction`.
- **RBAC**: Implement in `domains/core/services/user.py` (permissions: view, edit, approve, admin).
- **Testing**: Multi-client scenarios in `runway/tests/test_close_checklist.py`, `test_dashboard.py`, `test_engagement.py`.
- **Security**: Enhanced audit logs for SOC 2-like compliance, multi-tenancy (`firm_id`, `client_id`).

## Build Plan (~300 Hours, 2027)

### Objective
Build a vCFO/bookkeeping-focused product for weekly runway and monthly close rituals, with engagement management and analytics. Deploy in 2027 or as a separate product, reusing ~50–60 Oodaloo files and ~20–30 `_parked` files.

### Task Breakdown
#### Runway Ritual (80 hours)
- **Tasks**:
  1. Extend `runway/services/digest.py` for batch prep (5–50 clients):
     - Aggregate Cash Runway, AR (>30/45d), AP (due ≤14d), exceptions.
     - Role-aware: Lead bookkeeper sees all clients, staff sees assigned clients, clients see own data.
  2. Create `runway/templates/dashboard.html` (React/Jinja2) for multi-client views:
     - Filters: Client, period, status.
     - Metrics: Runway weeks, overdue AR, due AP.
  3. Extend `domains/core/models/user.py` for RBAC (roles: lead bookkeeper, staff, client, vCFO).
     - Schema: `domains/core/schemas/user.py` (add `RoleAssignment`).
  4. Extend `runway/services/notification.py` for Slack/email:
     - Task assignments (e.g., “Categorize transactions for Client X”).
     - Client approvals (e.g., “Approve JE for period”).
  5. Tests: `runway/tests/test_batch_digest.py`, `test_dashboard.py`, `test_rbac.py`.
- **Files Reused**: `digest.py`, `tray.py`, `user.py`, `notification.py`.

#### Monthly Close Checklist (100 hours)
- **Tasks**:
  1. Reuse `_parked/close/services/preclose.py` for checklist logic:
     - Reconcile bank accounts, AR, AP, credit cards (using `bank_transaction.py`, `bill.py`, `invoice.py`).
     - Draft JEs for accruals (e.g., prepaid expenses, payroll, depreciation) with QBO Agents.
     - Generate Balance Sheet, P&L, Cash Flow via QBO API (`JournalEntry`, `Report` endpoints).
  2. Create `runway/services/close_checklist.py`:
     - Tasks: Reconcile accounts, post JEs, review statements, flag discrepancies.
     - Status: `open`, `in_progress`, `completed`.
  3. Create `runway/models/close_checklist.py` (fields: `firm_id`, `client_id`, `period`, `tasks`, `status`).
     - Schema: `runway/schemas/close_checklist.py`.
  4. Create `runway/templates/close_checklist.html` (React/Jinja2, checklist UI).
  5. Create `runway/routes/close_checklist.py` (`/api/close_checklist`).
  6. Tests: `runway/tests/test_close_checklist.py`, `test_je_automation.py`.
- **Files Reused**: `_parked/close/services/preclose.py`, `bank_transaction.py`, `bill.py`, `invoice.py`.

#### Transaction Categorization (50 hours)
- **Tasks**:
  1. Reuse `_parked/ap/vendor_normalization.py` for vendor standardization:
     - Batch categorize unmatched transactions (e.g., map to QBO accounts/customers).
     - Leverage QBO Agents for 80–90% accuracy.
  2. Extend `runway/services/tray.py` for batch categorization:
     - Support 5–50 clients, role-aware (staff categorizes, lead bookkeeper reviews).
  3. Create `runway/templates/categorization.html` (React/Jinja2, dropdowns for accounts/customers).
  4. Tests: `runway/tests/test_batch_categorization.py`.
- **Files Reused**: `_parked/ap/vendor_normalization.py`, `tray.py`.

#### Engagement Management (50 hours)
- **Tasks**:
  1. Reuse `_parked/core/models/engagement.py`, `_parked/core/services/engagement.py` for client onboarding and scoping:
     - Fields: `firm_id`, `client_id`, `scope` (e.g., bookkeeping, vCFO), `start_date`, `status`.
  2. Reuse `_parked/close/services/preclose.py` for PBC tracking:
     - Create `runway/services/pbc.py` for PBC requests (fields: `item_type`, `due_date`, `status`, `task_id`).
  3. Reuse `_parked/core/services/task.py` for task assignment:
     - Assign to staff (e.g., “Reconcile Client X’s AP”).
     - Link to PBCs and checklist tasks.
  4. Create `runway/templates/engagement.html` (React/Jinja2, onboarding/scoping UI).
  5. Create `runway/routes/engagement.py` (`/api/engagement`), `runway/routes/pbc.py` (`/api/pbc`).
  6. Tests: `runway/tests/test_engagement.py`, `test_pbc.py`.
- **Files Reused**: `_parked/core/models/engagement.py`, `_parked/core/services/engagement.py`, `_parked/core/services/task.py`, `_parked/close/services/preclose.py`.

#### Analytics (Fathom-Style, 50 hours)
- **Tasks**:
  1. Create `runway/services/analytics.py`:
     - Cash flow forecasting (6–12 months, based on runway trends).
     - AR/AP aging reports (30/60/90d buckets).
     - KPIs (burn rate, profitability, liquidity ratios), reusing `_parked/core/services/kpi.py`.
  2. Create `runway/templates/analytics.html` (React/Jinja2, charts via Chart.js).
  3. Create `runway/routes/analytics.py` (`/api/analytics`).
  4. Tests: `runway/tests/test_analytics.py`.
- **Files Reused**: `_parked/core/services/kpi.py`.

#### Compliance and Testing (20 hours)
- **Tasks**:
  1. Enhance `domains/core/models/audit_log.py` for SOC 2-like logging (e.g., log JE posts, approvals).
  2. Test multi-client scenarios with `realistic_test_data.json` (5–50 clients).
  3. Tests: `domains/core/tests/test_audit_log.py`, `runway/tests/test_multi_client.py`.
- **Files Reused**: `audit_log.py`.

### File Summary for Code Ingestion
| File | Domain | Current Functionality | RowCol Need | Action |
|------|--------|----------------------|-------------|-------|
| `preclose.py` | `_parked/close/services` | Pre-close checks, PBC tracking | Monthly close checklist, PBCs | Reuse: Move to `runway/services/close_checklist.py`, `pbc.py` |
| `vendor_normalization.py` | `_parked/ap/services` | Vendor standardization | Batch categorization | Reuse: Move to `runway/services/categorization.py` |
| `engagement.py` | `_parked/core/models` | Client engagement scoping | Engagement management | Reuse: Move to `runway/models/engagement.py` |
| `task.py` | `_parked/core/services` | Task assignment | Staff task management | Reuse: Move to `runway/services/task.py` |
| `kpi.py` | `_parked/core/services` | KPI computation | Analytics (forecasting, KPIs) | Reuse: Move to `runway/services/analytics.py` |
| `audit_log.py` | `core/models` | Audit logging | SOC 2-like compliance | Enhance: Add firm-centric logging |

## Constraints
- **Timeline**: Deploy in 2027 or as separate product.
- **Budget**: ~300 hours, leveraging Oodaloo’s ~50–60 files and ~20–30 `_parked` files.
- **Codebase**: ~70–80 files total, with minimal new development.
- **QBO API**: Read/write, handle 2025 throttling (120 requests/minute for Batch).

## Risks and Mitigations
- **Risk**: Overlap with Oodaloo’s runway features.
  - **Mitigation**: Differentiate with accrual accounting, batch workflows, and analytics. Reuse Oodaloo’s `digest.py`, `tray.py` for runway.
- **Risk**: CAS firms expect immediate launch.
  - **Mitigation**: Engage as Oodaloo design partners, validate with 10–20 firms for RowCol.
- **Risk**: QBO Agents underperform on categorization.
  - **Mitigation**: Fall back to manual categorization in `runway/services/tray.py`, with staff review.