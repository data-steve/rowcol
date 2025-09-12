# Oodaloo v4.1 Build Plan and Task Backlog

## Overview
**Goal**: Deliver a cash flow management tool for agency owners (10–30 FTE, $1–$5M revenue) with a weekly “Friday Cash Runway” ritual (OODA loop: observe, orient, decide, act). Phases focus on usable features: Phase 0 (Proof-of-Concept), Phase 1 (Mature AP), Phase 2 (Mature AR/Smart Collections), Phase 3 (Runway Intelligence). Owner-only workflow, scalable for future multi-user support (e.g., RowCol vCFO/bookkeepers). Local development with SQLite for queues, scenario-based unit tests, and mocked QBO APIs. E2E testing post-tier completion.

**Tiers and Pricing**:
- Phase 0: Internal proof-of-concept (Q4 2025, ~100 hours).
- Phase 1: $99/mo, mature AP decision surface (Q1 2026, ~200 hours).
- Phase 2: $199/mo, mature AR/Smart Collections (Q3 2026, ~150 hours).
- Phase 3: $299/mo, Runway Intelligence with analytics/automation (Q1 2027, ~120 hours).

**Testing Strategy**:
- **Unit Tests**: Scenario-based with mocked QBO APIs (`static/qbo_mock_data.json`) for AP/AR/cash/hygiene scenarios (e.g., $5k rent due, $10k invoice >45d, $6k available balance).
- **Mocked APIs**: Simulate QBO `Bill`, `Invoice`, `Accounts` endpoints to test digest, Prep Tray, and actions.
- **Local HTML Preview**: Generate `digest.html` locally for email preview before SendGrid integration.
- **E2E Testing**: Post-tier “golden set” in CI/CD to validate QBO injection (e.g., simulate agency data in QBO sandbox).
- **Rationale**: Keeps development lightweight, delays costly E2E testing until tier completion, ensures robust unit tests for fast iteration.

**Scalability Principle**: Avoid hardcoding owner-only logic; use `user_id`, `role`, and `allowed_roles` in models to support future RowCol multi-user workflows (e.g., office manager, vCFO).

---

## Phase 0: Proof-of-Concept (Internal, Q4 2025, ~115 hours)
**Goal**: Validate core balance tracking, digest, Prep Tray, and audit logging with 5–10 design partners (QBO App Store, LinkedIn). Owner-only workflow, read-only QBO, deep-links. Target 70%+ digest open rate, 40–50% click-through, 80–90% AR/AP reconciliation, 50%+ overdue AR flagged.

### Week 1–2: Core Setup and QBO Integration (60 hours)
- [ ] **Setup Project Infrastructure (20h)**
  - [ ] Initialize FastAPI project with Poetry (`pyproject.toml`, `poetry.lock`).
  - [ ] Configure SQLite database (`database.py`) with tables: `firm`, `client`, `user`, `notification`, `tray_item`, `bill`, `invoice`, `bank_transaction`, `audit_log`.
    - **Fields** (`firm`): `id`, `name`, `qbo_tenant_id`, `created_at`, `updated_at`, `current_balance`, `reserved_balance`.
    - **Fields** (`client`): `id`, `firm_id`, `name`, `qbo_client_id`, `status`.
    - **Fields** (`user`): `id`, `firm_id`, `email`, `role` (default: `owner`), `qbo_access_token`, `qbo_refresh_token`.
    - **Fields** (`notification`): `id`, `firm_id`, `user_id`, `recipient_role`, `event_type` (digest/action), `content`, `sent_at` (disabled until Phase 3).
    - **Fields** (`tray_item`): `id`, `firm_id`, `type` (invoice/bill/bank), `qbo_id`, `status` (pending/resolved), `priority`, `due_date`, `allowed_roles` (default: `owner`).
    - **Fields** (`bill`, `invoice`): `id`, `firm_id`, `qbo_id`, `amount`, `due_date`, `status`, `aging_days`, `reserved_by_user_id` (default: owner).
    - **Fields** (`bank_transaction`): `id`, `firm_id`, `qbo_id`, `amount`, `date`, `status` (matched/unmatched).
    - **Fields** (`audit_log`): `id`, `firm_id`, `user_id`, `action_type` (approve_bill/send_drip/confirm_automation), `entity_type` (bill/invoice/tray_item), `entity_id`, `details` (JSON), `timestamp`.
  - [ ] Move RowCol-specific models to `_parked/`:
    - From `domains/core/models`: `business_entity.py`, `engagement.py`, `engagement_entities.py`, `job.py`, `service.py`, `task.py`, `document.py`, `document_type.py`, `staff.py`, `sync_cursor.py`, `transaction.py`, `integration.py` to `_parked/core/`.
    - From `domains/ap/models`: `coa_template.py`, `compliance.py`, `policy_rule_template.py`, `task_template.py`, `vendor_canonical.py`, `vendor_category.py`, `vendor_statement.py`, `vendor.py`, `payment.py`, `payment_intent.py` to `_parked/ap/`.
    - From `domains/ar/models`: `customer.py`, `credit_memo.py`, `payment.py` to `_parked/ar/`.
    - From `domains/bank/models`: `transfer.py` to `_parked/bank/`.
    - From `domains/policy/models`: `correction.py`, `policy_profile.py`, `suggestion.py` to `_parked/policy/`.
  - [ ] Update `domains/__init__.py` to import `firm.py`, `client.py`, `user.py`, `audit_log.py`, `bill.py`, `invoice.py`, `bank_transaction.py`, `webhook_event.py`, `rule.py`.
  - [ ] Write unit tests (`tests/test_database.py`) for schema validation and model migration.
  - **Dependencies**: None.
  - **Rationale**: Establishes lean models for Oodaloo, parks RowCol models, adds audit logging for traceability.
  - **KPIs**: 100% schema deployment, 100% model migration, 95%+ test coverage.

- [ ] **QBO Mocked Integration (25h)**
  - [ ] Create `domains/integrations/qbo_auth.py` for OAuth 2.0 flow (mocked for local dev).
  - [ ] Create `domains/integrations/qbo_integration.py` for mocked QBO API calls (GET `Bill`, `Invoice`, `Accounts`).
  - [ ] Add `domains/integrations/webhooks.py` for mocked QBO webhook handling.
  - [ ] Write unit tests (`tests/test_qbo_integration.py`) with mock data.
  - **Dependencies**: None.
  - **Rationale**: Simulates QBO sync for digest and tray.
  - **KPIs**: 100% mock API success, 95%+ test coverage.

- [ ] **Onboarding Qualifier (15h)**
  - [ ] Create `templates/onboarding.html` (React/Jinja2) with qualifier form (“Weekly cash review?”).
  - [ ] Add `domains/core/services/onboarding.py` to filter clients (20–30% drop-off).
  - [ ] Store data in `firm`, `user` tables; log onboarding in `audit_log`.
  - [ ] Write unit tests (`tests/test_onboarding.py`) for qualifier logic.
  - **Dependencies**: `audit_log` table.
  - **Rationale**: Filters unsuitable clients, logs onboarding actions.
  - **KPIs**: 90%+ onboarding completion, 20–30% drop-off.

### Week 3–4: Digest and Prep Tray (50 hours)
- [ ] **Friday Cash Runway Digest (25h)**
  - [ ] Create `runway/services/digest.py` to compute:
    - Cash Runway: `(current_balance - AP_due_14d) / weekly_burn`.
    - AR aging: Invoices >30/45d (`aging_days` from `invoice`).
    - AP due: Bills ≤14d (`due_date` from `bill`) with Must Pay (rent, payroll) / Can Delay (SaaS) tags (`policy` table).
    - Exceptions: Unmatched `bank_transaction`, high-priority `tray_item`.
  - [ ] Create `templates/digest.html` (Jinja2) for local HTML preview with QBO deep-links.
  - [ ] Add `runway/routes/digest.py` for local digest generation (no SendGrid yet).
  - [ ] Write unit tests (`tests/test_digest.py`) with `static/realistic_test_data.json` (e.g., $6k balance, $5k rent, $10k invoice).
  - **Dependencies**: `invoice.py`, `bill.py`, `bank_transaction.py` (create for data access).
  - **Rationale**: Delivers forward-looking cash flow snapshot for owner decisions.
  - **KPIs**: 70%+ digest preview accuracy, 40–50% deep-link coverage.

- [ ] **Prep Tray UI (20h)**
  - [ ] Create `templates/tray.html` (React/Jinja2) for gamified UI (“Clear 2 exceptions”).
  - [ ] Add `domains/tray/services/tray.py` for tray item prioritization (e.g., overdue invoices, unmatched transactions).
    - Logic: Sort by `priority`, `due_date`, filter by `allowed_roles=owner`.
  - [ ] Add `domains/tray/routes/tray.py` for tray item CRUD.
  - [ ] Write unit tests (`tests/test_tray.py`) for prioritization and rendering.
  - **Dependencies**: `tray.py` (create for owner-only logic).
  - **Rationale**: Gamified tray drives hygiene fixes, supports OODA loop.
  - **KPIs**: 80–90% reconciliation, 50%+ AR flagged.

- [ ] **Bank Feed Status Checks (5h)**
  - [ ] Create `domains/bank/services/feed_status.py` to monitor mocked bank feed sync.
    - Check unmatched `bank_transaction` entries.
  - [ ] Integrate status into digest and tray (`tray_item` with `type=bank`).
  - [ ] Write unit tests (`tests/test_feed_status.py`) with mock data.
  - **Dependencies**: `bank_transaction.py` (create for status checks).
  - **Rationale**: Ensures bank feed reliability for runway accuracy.
  - **KPIs**: 95%+ sync success.

---

## Phase 1: Smart AP ($99/mo, Q1 2026, ~210 hours)
**Goal**: Deliver full AP OODA loop (see, fix, decide, act) with in-app approvals, `BillPayment` drafting, earmarking, and simple payment execution. Include Risk-Free Trial Mode for design partners to test on sandbox or live QBO with $0.01 self-transactions and automatic cleanup. Target 80%+ approval rate, 60%+ payment rate, 80–90% reconciliation, 90%+ trial satisfaction.

### Week 5–7: AP Decision Surface (100 hours)
- [ ] **Enhanced Digest (30h)**
  - [ ] Update `runway/services/digest.py` to include:
    - AP due ≤14d with Must Pay/Can Delay tags (`policy` table).
    - Current/available balance (`firm.current_balance`, `firm.reserved_balance`).
    - AR >30/45d for context.
    - Drift alert: Compare Oodaloo’s `firm.current_balance` vs. QBO bank balance (via `qbo_integration.py` GET `/Accounts`). Flag >5% variance (e.g., “Sync drift: $300 variance—reconcile?”) with audit_log link.
  - [ ] Update `templates/digest.html` for local HTML preview with in-app action links (e.g., “Approve $5k rent”) and drift alert.
  - [ ] Write unit tests (`tests/test_digest.py`) with scenarios (e.g., $6k available, $5k rent due, 5% drift).
  - **Dependencies**: `bill.py`, `invoice.py`, `policy.py`, `audit_log` table.
  - **Rationale**: Forward-looking digest with drift alert drives trust in Runway Reserve.
  - **KPIs**: 70%+ preview accuracy, 40–50% link coverage, 90%+ drift alert accuracy.

- [ ] **Prep Tray with Runway Reserve (55h)**
  - [ ] Update `templates/tray.html` for:
    - Hygiene fixes, approvals (e.g., “Pay $5k rent on 10/14”).
    - Runway Reserve UX: Visual “reserve meter” (Chart.js progress bar: “80% runway reserved—$1k free”) and prompt (“Earmark rent to protect 2 weeks runway?”).
    - Available balance display (e.g., “$1k left after $5k earmark”).
  - [ ] Update `domains/tray/services/tray.py` to:
    - Generate tray items for AP hygiene (e.g., missing due dates).
    - Support approvals (`status=approved`, `reserved_by_user_id=owner` in `bill`).
    - Earmark funds (`firm.reserved_balance += bill.amount`).
  - [ ] Create `ap/services/bill_ingestion.py` to draft `BillPayment` (mocked QBO write).
    - Fields: `bill_id`, `amount`, `pay_date`, `status=draft`.
  - [ ] Add `templates/approval.html` (React/Jinja2) for approval UI with Runway Reserve prompt (e.g., “Earmark $5k?”).
  - [ ] Write unit tests (`tests/test_tray.py`, `tests/test_bill_ingestion.py`) with scenarios (e.g., approve $5k rent, $1k left).
  - **Dependencies**: `bill.py`, `firm.py`.
  - **Rationale**: Runway Reserve makes AP decisions proactive, preventing overspending.
  - **KPIs**: 80%+ approval rate, 80–90% reconciliation, 90%+ user trust in earmarking.

- [ ] **In-App Payment Execution (15h)**
  - [ ] Update `ap/services/bill_ingestion.py` for simple `BillPayment` execution (mocked QBO write).
    - POST to mocked QBO `/BillPayment` for approved bills.
  - [ ] Update `templates/tray.html` with “Execute Payment” button.
  - [ ] Write unit tests (`tests/test_bill_ingestion.py`) for payment execution.
  - **Dependencies**: `qbo_integration.py` (add write mocks).
  - **Rationale**: Enables in-app actions, completing OODA loop.
  - **KPIs**: 60%+ payment rate.

### Week 8–10: QBO Integration, Testing, and Trial Mode (110 hours)
- [ ] **Real QBO Integration (50h)**
  - [ ] Update `domains/integrations/qbo_integration.py` for real QBO API calls (GET/POST `Bill`, `Accounts`, `BillPayment`).
    - Replace mocks with live endpoints (e.g., `/v3/company/<realmId>/BillPayment`).
  - [ ] Add `domains/core/services/preflight.py` for QBO state validation before writes (e.g., check balance drift <5%).
  - [ ] Write unit tests (`tests/test_qbo_integration.py`) with QBO sandbox data.
  - **Dependencies**: `qbo_auth.py`, `bill_ingestion.py`.
  - **Rationale**: Transitions to live QBO for production, supports drift alerts.
  - **KPIs**: 100% API success, 95%+ test coverage.

- [ ] **Risk-Free Trial Mode (10h)**
  - [ ] Create `domains/core/services/trial_mode.py` for sandbox/live self-tests:
    - **Sandbox**: Auto-create $0.01 self-invoice/bill in QBO sandbox (POST `/Invoice`, `/Bill`), run digest/Prep Tray with Runway Reserve, void via PUT `/Invoice/{id}` (status=Voided).
    - **Live**: Create $0.01 self-invoice/bill in partner’s QBO (customer/vendor = “Test Self”), run digest/Prep Tray with Runway Reserve, void/delete via API. Log in `audit_log`.
    - Toggle in `onboarding.html` (React/Jinja2): “Sandbox Demo” vs. “Live $0.01 Test.”
  - [ ] Update `domains/core/services/onboarding.py` to offer trial mode with Runway Reserve UX.
  - [ ] Write unit tests (`tests/test_trial_mode.py`) with mocked QBO ($0.01 scenarios).
  - **Dependencies**: `qbo_integration.py`, `audit_log` table, `onboarding.py`.
  - **Rationale**: Enables risk-free testing for design partners (sandbox + live), special in-app walkthru/demo of earmarking, boosting trust (90%+ satisfaction, 20%+ conversion).
  - **KPIs**: 100% test transaction cleanup, 90%+ partner satisfaction.

- [ ] **Scenario-Based Testing (30h)**
  - [ ] Update `static/agency_test_scenarios.json` for AP/hygiene scenarios (e.g., $6k balance, $5k rent due with Runway Reserve, $0.01 test bill).
  - [ ] Test digest, tray, approvals, payments, trial mode, and drift alerts locally with SQLite and mock APIs.
  - [ ] Generate `digest.html` previews for validation.
  - [ ] Write unit tests (`tests/test_scenarios.py`) for scenario coverage.
  - **Dependencies**: `digest.py`, `tray.py`, `bill_ingestion.py`, `trial_mode.py`.
  - **Rationale**: Ensures functionality matches agency needs, including trial mode,Runway Reserve and drift alerts.
  - **KPIs**: 90%+ scenario coverage, 0 critical bugs.

- [ ] **Design Partner Validation (20h)**
  - [ ] Onboard 5–10 design partners via `onboarding.html`, offering sandbox and live $0.01 self-tests.
  - [ ] Collect feedback on digest, tray, payment UX, and trial mode experience, Runway Reserve, and drift alerts..
  - [ ] Iterate on `digest.py`, `tray.py`, `bill_ingestion.py`, `trial_mode.py`.
  - **Dependencies**: All Phase 1 files.
  - **Rationale**: Validates product-market fit and trial mode trust, earmarking trust, and drift mitigation.
  - **KPIs**: 80%+ approval rate, 60%+ payment rate, 80–90% reconciliation, 90%+ trial satisfaction.

---

## Phase 2: Mature AR/Smart Collections ($199/mo, Q3 2026, ~150 hours)
**Goal**: Deliver full AR OODA loop with Smart Collections (drips, prioritization, in-app reminders). Maintain Phase 1 AP. Target 50%+ drip adoption, 60%+ payment rate post-reminder.

### Week 11–13: Smart Collections (90 hours)
- [ ] **AR Digest and Drip Campaigns (40h)**
  - [ ] Update `runway/services/digest.py` to include AR drip status (e.g., “$10k invoice, 30d reminder sent”), expected payments (e.g., “$5k likely in 7 days”).
  - [ ] Create `runway/services/drip.py` for 3-email sequence (30d gentle, 45d urgent, 60d final).
    - Trigger: AR >30d, prioritize >$5k or >45d.
  - [ ] Create `templates/drip.html` (Jinja2) for local HTML preview with in-app links.
  - [ ] Add `runway/routes/drip.py` for campaign scheduling.
  - [ ] Write unit tests (`tests/test_drip.py`) with mock SendGrid responses.
  - **Dependencies**: `invoice.py` (create for AR logic).
  - **Rationale**: Automates AR follow-ups, boosting payments.
  - **KPIs**: 50%+ drip adoption, 60%+ payment rate.

- [ ] **Prep Tray with AR Prioritization (30h)**
  - [ ] Update `templates/tray.html` for AR hygiene (e.g., unmatched deposits), prioritization (e.g., “Escalate $10k >45d”), and in-app reminders.
  - [ ] Update `domains/tray/services/tray.py` to prioritize invoices (`priority` field, filter by `aging_days`, `amount`).
  - [ ] Create `domains/ar/services/invoice.py` for reminder sends (mocked QBO write).
  - [ ] Write unit tests (`tests/test_tray.py`, `tests/test_invoice.py`) with scenarios (e.g., $10k invoice >45d).
  - **Dependencies**: `invoice.py`, `tray.py`.
  - **Rationale**: Enables in-app AR decisions, completing OODA loop.
  - **KPIs**: 80%+ prioritization rate, 80–90% reconciliation.

- [ ] **Available Balance for AR (20h)**
  - [ ] Update `runway/services/digest.py` to estimate expected AR payments (e.g., “$5k likely in 7 days” based on historical `invoice` data).
  - [ ] Update `firm.reserved_balance` for AR expectations (e.g., reduce available balance until cleared).
  - [ ] Write unit tests (`tests/test_digest.py`) for balance calculations.
  - **Dependencies**: `firm.py`, `invoice.py`.
  - **Rationale**: Enhances runway accuracy with AR forecasts.
  - **KPIs**: 90%+ balance accuracy.

### Week 14–15: Validation and SendGrid Integration (60 hours)
- [ ] **Real SendGrid Integration (20h)**
  - [ ] Update `runway/services/digest.py`, `runway/services/drip.py` to send via SendGrid API.
  - [ ] Test digest and drip delivery with design partners.
  - [ ] Write unit tests (`tests/test_sendgrid.py`) for email delivery.
  - **Dependencies**: `digest.py`, `drip.py`.
  - **Rationale**: Enables production email delivery.
  - **KPIs**: 99%+ email delivery success.

- [ ] **Scenario-Based Testing and Validation (40h)**
  - [ ] Extend `static/agency_test_scenarios.json` for AR scenarios (e.g., $10k invoice >45d, $5k expected in 7 days).
  - [ ] Test digest, tray, drips, and reminders locally with SQLite and mock APIs.
  - [ ] Validate with 5–10 design partners (feedback on drip tone, prioritization UX).
  - [ ] Iterate on `drip.py`, `tray.py`, `invoice.py`.
  - **Dependencies**: All Phase 2 files.
  - **Rationale**: Ensures AR functionality meets agency needs.
  - **KPIs**: 50%+ drip adoption, 60%+ payment rate, 80–90% reconciliation.

---

## Phase 3: Smart Cashflow Automation ($299/mo, Q2 2026, ~95 hours)
**Goal**: Deliver dynamic automation for AP/AR with pre-labeled rules, owner/bookkeeper notifications, and Runway Reserve release rules. Target 50%+ auto-mapped tasks, <20% runway risk, 80%+ notification engagement.

### Week 16–18: Automation and Collaboration (95 hours)
- [ ] **Dynamic Automation Rules with Reserve Release (40h)**
  - [ ] Create `runway/services/meta_policy.py` for dynamic rules (`policy` table).
    - Rules: e.g., “Pay $5k rent if runway >2 weeks,” “Release $3k reserve if AR clears early.”
    - Fields: `id`, `firm_id`, `rule_type` (pay/release), `conditions` (JSON, e.g., `{"runway_days": ">14"}`), `actions` (JSON, e.g., `{"reserve_amount": 5000}`).
  - [ ] Update `domains/tray/services/tray.py` for “Confirm All” button applying rules (e.g., auto-approve bills, release reserves).
  - [ ] Update `ap/services/bill_ingestion.py` to execute auto-approved payments and release reserves (`firm.reserved_balance -= amount`).
  - [ ] Add `templates/tray.html` for rule confirmation UX (e.g., “Release $3k reserve?”).
  - [ ] Write unit tests (`tests/test_meta_policy.py`) with scenarios (e.g., release $3k on $3k AR payment).
  - **Dependencies**: `policy.py`, `bill.py`, `firm.py`, `audit_log` table.
  - **Rationale**: Automates AP/AR decisions, releases reserves dynamically to prevent rigidity, drives PLG to $299/mo tier.
  - **KPIs**: 50%+ auto-mapped tasks, 95%+ reserve release accuracy.
- [ ] **AR/AP Aging Analytics (30h)**
  - [ ] Create `runway/services/aging_analytics.py` for 30/60/90d AR/AP buckets (Chart.js).
  - [ ] Add `templates/aging_analytics.html` (React/Jinja2) for visualizations.
  - [ ] Update `runway/services/digest.py` to include analytics summary.
  - [ ] Write unit tests (`tests/test_aging_analytics.py`) for data accuracy.
  - **Dependencies**: `invoice.py`, `bill.py`.
  - **Rationale**: Provides cash flow insights for decisions.
  - **KPIs**: 80%+ analytics engagement.

- [ ] **Short-Term Cash Flow Forecasting (20h)**
  - [ ] Create `runway/services/forecast.py` for 2–4 week forecasts (e.g., “$5k invoice likely in 7 days” based on `invoice` history).
  - [ ] Update `templates/digest.html`, `templates/tray.html` to show forecasts.
  - [ ] Write unit tests (`tests/test_forecast.py`) with scenarios.
  - **Dependencies**: `invoice.py`, `firm.py`.
  - **Rationale**: Enhances runway planning without vCFO complexity.
  - **KPIs**: 90%+ forecast accuracy.


### Week 19–20: Validation and Deployment (40 hours)
- [ ] **Scenario-Based Testing and QBO Injection (20h)**
  - [ ] Extend `static/agency_test_scenarios.json` for analytics/automation (e.g., $5k rent pre-labeled, $10k invoice escalated).
  - [ ] Inject test data into QBO sandbox to simulate agency scenarios.
  - [ ] Test digest, tray, analytics, and automation locally and with QBO.
  - [ ] Write unit tests (`tests/test_scenarios.py`) for E2E coverage.
  - **Dependencies**: All Phase 3 files.
  - **Rationale**: Validates production readiness.
  - **KPIs**: 90%+ scenario coverage, 0 critical bugs.

- [ ] **Design Partner Validation and Deployment (20h)**
  - [ ] Test analytics and automation with 5–10 design partners.
  - [ ] Deploy to local server with SQLite, prep for AWS Lambda.
  - [ ] Update `README.md`, `openapi.yaml` for endpoints.
  - **Dependencies**: All Phase 3 files.
  - **Rationale**: Ensures user adoption and production stability.
  - **KPIs**: 80%+ analytics engagement, 50%+ auto-mapped, 99%+ uptime.


- [ ] **Collaboration Notifications (35h)**
  - [ ] Create `runway/services/notification.py` for owner/bookkeeper alerts (e.g., “Confirm $5k payment,” “Reserve released”).
    - Fields: `id`, `firm_id`, `user_id`, `recipient_role`, `event_type` (payment/reserve_release), `content`, `sent_at`.
  - [ ] Create `runway/routes/notification.py` for CRUD (GET `/notifications`, POST `/notifications/acknowledge`).
  - [ ] Integrate SendGrid for delivery, log in `audit_log`.
  - [ ] Update `templates/tray.html` for notification display.
  - [ ] Write unit tests (`tests/test_notification.py`) for delivery/acknowledgment.
  - **Dependencies**: `notification` table, `audit_log` table.
  - **Rationale**: Enables light collaboration, syncs bookkeepers on reserves.
  - **KPIs**: 80%+ notification engagement, 99%+ delivery success.

- [ ] **Validation and Testing (20h)**
  - [ ] Update `static/agency_test_scenarios.json` for automation/reserve release scenarios (e.g., $6k balance, $5k rent, $3k AR clears).
  - [ ] Test rules, notifications, and reserve releases locally with SQLite and mock APIs.
  - [ ] Collect feedback from design partners on automation and collaboration.
  - **Dependencies**: All Phase 3 files.
  - **Rationale**: Ensures automation reliability and PLG appeal.
  - **KPIs**: <20% runway risk, 90%+ scenario coverage.
---

## Refactoring Notes
- **New Files**: Create `bill.py`, `invoice.py`, `policy.py`, `firm.py` for AP/AR/policy/balance logic.
- **Move `_parked/`**: Refactor `_parked/qbo/*` to `domains/integrations/` for QBO auth and APIs.
- **Scalability**: Use `user_id`, `role`, `allowed_roles` in `bill`, `invoice`, `tray_item`, `audit_log` tables. Keep `notification` table for future alerts (disabled for now).
- **Testing**: Mock QBO APIs in `qbo_integration.py` until Phase 1 real integration. Use `agency_test_scenarios.json` for realistic data.

## Risks and Mitigations
- **QBO API Limits**: Mock APIs locally; use QBO sandbox for Phase 1 testing to avoid rate limits.
- **Scenario Gaps**: Iterate `agency_test_scenarios.json` with design partner feedback to cover edge cases.
- **Scalability Overengineering**: Limit multi-user logic to `user_id`, `allowed_roles`; defer RBAC to RowCol.
- **Resource Constraints**: Prioritize unit tests, delay E2E until Phase 3 to stay within ~470-hour budget.