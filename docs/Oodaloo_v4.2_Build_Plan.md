

# Oodaloo v4.2 Build Plan and Task Backlog

#### Overview
**Goal**: Build a modular cash flow management tool for agency owners (10–30 FTE, $1–$5M revenue) with a weekly “Friday Cash Runway” ritual (OODA loop: observe, orient, decide, act). The core module ($99/mo) delivers a digest email and Prep Tray decision surface, with add-on modules ($99/mo each) for Smart AP, Smart AR, Smart Budgets, and Smart Automation. An Analytics Pack ($99/mo) enhances insights. Designed for QBO integration, it empowers owners without bookkeepers, scalable for CAS firms via RowCol (multi-client rituals).

**Architecture**:
- **domains/**: Standardizes QBO-facing integrations (e.g., `domains/integrations/`, `domains/models/`).
- **runway/**: Houses product logic and orchestrations (e.g., `runway/services/`, `runway/templates/`).
- **Modularity**: Core module assumes minimal QBO cleanup; add-ons build incrementally (e.g., AP adds earmarking, AR adds drips).

**Pricing**:
- **Core Module ($99/mo)**: Digest email (basic reports) + Prep Tray (decision surface).
- **Add-Ons ($99/mo each)**: Smart AP (earmarking), Smart AR (drips), Smart Budgets (dynamic policies), Smart Automation (rules).
- **Analytics Pack ($99/mo)**: Charts/forecasts (available with any module).
- **Total**: $99–$594/mo, modular for ICP flexibility.

**Testing Strategy**:
- **Unit Tests**: Scenario-based with mocked QBO APIs (`static/qbo_mock_data.json`) for AP/AR/budget scenarios.
- **Integration Tests**: Real QBO sandbox post-Phase 1 for API reliability.
- **E2E Tests**: Golden set in CI/CD post-module, validating QBO injection.
- **Local Preview**: `runway/templates/` generates HTML for email/dashboard validation.

**Scalability**: Uses `user_id`, `role`, `allowed_roles` in models for future RowCol multi-user support (e.g., owner, bookkeeper, vCFO).



---

#### Phase 0: Proof-of-Concept (Internal, Q4 2025, ~120 hours)
**Goal**: Validate core digest email and Prep Tray with 5–10 design partners (QBO App Store, LinkedIn). Focus on owner-only workflow, read-only QBO, and deep-links. Target 70%+ digest open rate, 40–50% click-through, 80%+ data reconciliation.

##### Week 1–2: Core Setup and QBO Integration (65 hours)
- **[ ] Project Infrastructure (25h)**:
  - Initialize FastAPI with Poetry (`pyproject.toml`, `poetry.lock`).
  - Configure SQLite (`database.py`) with tables:
    - `firm`: `id`, `name`, `qbo_tenant_id`, `current_balance`, `reserved_balance`, `created_at`, `updated_at`.
    - `user`: `id`, `firm_id`, `email`, `role` (default: `owner`), `qbo_access_token`, `qbo_refresh_token`.
    - `notification`: `id`, `firm_id`, `user_id`, `recipient_role`, `event_type` (digest/action), `content`, `sent_at` (disabled until Phase 3).
    - `tray_item`: `id`, `firm_id`, `type` (invoice/bill/bank/budget), `qbo_id`, `status` (pending/resolved), `priority`, `due_date`, `allowed_roles` (default: `owner`).
    - `audit_log`: `id`, `firm_id`, `user_id`, `action_type` (approve_bill/send_drip/confirm_budget), `entity_type`, `entity_id`, `details` (JSON), `timestamp`.
  - Move RowCol models to `_parked/` (e.g., `business_entity.py` to `_parked/core/`).
  - Update `domains/__init__.py` for `firm.py`, `user.py`, `audit_log.py`.
  - Unit tests (`tests/test_database.py`) for schema (95%+ coverage).
  - **Dependencies**: None.
  - **Rationale**: Lean base for modularity, audit trail for trust.
  - **KPIs**: 100% schema deployment, 95%+ test coverage.

- **[ ] QBO Mocked Integration (30h)**:
  - `domains/integrations/qbo_auth.py`: OAuth 2.0 flow (mocked).
  - `domains/integrations/qbo_integration.py`: Mocked GET (`Bill`, `Invoice`, `Accounts`).
  - `domains/integrations/webhooks.py`: Mocked webhook handling.
  - Unit tests (`tests/test_qbo_integration.py`) with mock data (95%+ coverage).
  - **Dependencies**: None.
  - **Rationale**: Simulates QBO sync for core module.
  - **KPIs**: 100% mock API success.

- **[ ] Onboarding Qualifier (10h)**:
  - `runway/templates/onboarding.html` (React/Jinja2) with form (“Weekly cash review?”).
  - `runway/services/onboarding.py`: Filters clients (20–30% drop-off).
  - Store in `firm`, `user`; log onboarding in `audit_log`.
  - Unit tests (`tests/test_onboarding.py`) (90%+ coverage).
  - **Dependencies**: `audit_log`.
  - **Rationale**: Targets ICP, logs actions.
  - **KPIs**: 90%+ completion, 20–30% drop-off.

##### Week 3–4: Core Module (55 hours)
- **[ ] Digest Email (25h)**:
  - `runway/services/digest.py`: Computes cash runway (`(current_balance - AP_due_14d) / weekly_burn`), AR aging (>30/45d), AP due (≤14d), exceptions (unmatched `bank_transaction`).
  - `runway/templates/digest.html`: Local HTML preview with QBO deep-links.
  - `runway/routes/digest.py`: Local generation (no SendGrid yet).
  - Unit tests (`tests/test_digest.py`) with `static/realistic_test_data.json` (e.g., $6k balance, $5k rent).
  - **Dependencies**: `domains/models/bill.py`, `domains/models/invoice.py`, `domains/models/bank_transaction.py`.
  - **Rationale**: Baseline ritual snapshot.
  - **KPIs**: 70%+ accuracy, 40–50% deep-link coverage.

- **[ ] Prep Tray UI (25h)**:
  - `runway/templates/tray.html` (React/Jinja2) for hygiene fixes (“Clear 2 exceptions”).
  - `runway/services/tray.py`: Prioritizes `tray_item` by `due_date`, `priority` (owner-only).
  - `runway/routes/tray.py`: CRUD for tray items.
  - Unit tests (`tests/test_tray.py`) for prioritization (95%+ coverage).
  - **Dependencies**: `domains/models/tray_item.py`.
  - **Rationale**: Gamified decision surface.
  - **KPIs**: 80%+ reconciliation.

- **[ ] Bank Feed Status (5h)**:
  - `runway/services/feed_status.py`: Monitors unmatched `bank_transaction`.
  - Integrate into digest/tray.
  - Unit tests (`tests/test_feed_status.py`).
  - **Dependencies**: `domains/models/bank_transaction.py`.
  - **Rationale**: Ensures runway accuracy.
  - **KPIs**: 95%+ sync success.

---

#### Phase 1: Core Module + Smart AP (Q1 2026, ~220 hours)
**Goal**: Launch core module ($99/mo) with digest/Prep Tray, add Smart AP ($99/mo add-on) for earmarking/approvals. Include Risk-Free Trial Mode for design partners to test on sandbox or live QBO with $0.01 self-transactions and automatic cleanup. Target 80%+ approval rate, 60%+ payment rate, 80–90% reconciliation, 90%+ trial satisfaction.
##### Week 5–7: Smart AP Development (110 hours)
- **[ ] Enhanced Digest (30h)**:
  - `runway/services/digest.py`: Add AP due (≤14d, Must Pay/Can Delay tags), drift alert (5% variance vs. QBO balance).
  - `runway/templates/digest.html`: Action links (“Approve $5k rent”), drift alert.
  - Unit tests (`tests/test_digest.py`) with drift scenarios.
  - **Dependencies**: `domains/models/bill.py`, `domains/models/policy.py`.
  - **Rationale**: Proactive AP visibility.
  - **KPIs**: 70%+ accuracy, 90%+ drift alert.

- **[ ] Prep Tray with Runway Reserve (55h)**:
  - `runway/templates/tray.html`: Reserve meter (Chart.js), prompt (“Earmark $5k?”).
  - `runway/services/tray.py`: Approvals (`status=approved`, `reserved_by_user_id`), earmarking (`firm.reserved_balance += amount`).
  - `runway/services/ap.py`: Draft `BillPayment` (mocked QBO write).
  - `runway/templates/approval.html`: Approval UI.
  - Unit tests (`tests/test_tray.py`, `tests/test_ap.py`) with earmarking scenarios.
  - **Dependencies**: `domains/models/bill.py`, `domains/models/firm.py`.
  - **Rationale**: Proactive AP decisions.
  - **KPIs**: 80%+ approval rate, 90%+ earmarking trust.

- **[ ] In-App Payment Execution (25h)**:
  - `runway/services/ap.py`: Execute `BillPayment` (mocked POST).
  - `runway/templates/tray.html`: “Execute Payment” button.
  - Unit tests (`tests/test_ap.py`).
  - **Dependencies**: `domains/integrations/qbo_integration.py` (add write mocks).
  - **Rationale**: Completes OODA loop.
  - **KPIs**: 60%+ payment rate.

##### Week 8–10: QBO Integration and Trial Mode (110 hours)
- **[ ] Real QBO Integration (50h)**:
  - `domains/integrations/qbo_integration.py`: Live GET/POST (`Bill`, `BillPayment`).
  - `runway/services/preflight.py`: Validate QBO state (<5% drift).
  - Unit tests (`tests/test_qbo_integration.py`) with sandbox.
  - **Dependencies**: `domains/integrations/qbo_auth.py`.
  - **Rationale**: Production-ready sync.
  - **KPIs**: 100% API success, 95%+ coverage.

- **[ ] Risk-Free Trial Mode (20h)**:
  - `runway/services/trial_mode.py`: Sandbox ($0.01 self-invoice/bill, void), live ($0.01 test, delete).
  - `runway/templates/onboarding.html`: Toggle (“Sandbox Demo” vs. “Live Test”).
  - `runway/services/onboarding.py`: Offer trial with Runway Reserve.
  - Unit tests (`tests/test_trial_mode.py`) with $0.01 scenarios.
  - **Dependencies**: `domains/integrations/qbo_integration.py`, `audit_log`.
  - **Rationale**: Builds trust (90%+ satisfaction).
  - **KPIs**: 100% cleanup, 90%+ satisfaction.

- **[ ] Scenario Testing (40h)**:
  - `static/agency_test_scenarios.json`: AP scenarios (e.g., $6k balance, $5k rent).
  - Test digest, tray, approvals, payments locally.
  - Unit tests (`tests/test_scenarios.py`) (90%+ coverage).
  - **Dependencies**: All Phase 1 files.
  - **Rationale**: Validates functionality.
  - **KPIs**: 90%+ coverage, 0 critical bugs.

---

#### Phase 2: Smart AR and Smart Budgets (Q2 2026, ~180 hours)
**Goal**: Add Smart AR ($99/mo) for drips/prioritization, Smart Budgets ($99/mo) for dynamic policies. Target 60%+ payment rate, 80% budget adherence.

##### Week 11–13: Smart AR Development (90 hours)
- **[ ] AR Digest and Drips (40h)**:
  - `runway/services/digest.py`: Add drip status (e.g., “$10k, 30d reminder”).
  - `runway/services/ar.py`: 3-email drips (30/45/60d, >$5k/>45d).
  - `runway/templates/drip.html`: Preview with links.
  - `runway/routes/drip.py`: Scheduling.
  - Unit tests (`tests/test_ar.py`) with mock SendGrid.
  - **Dependencies**: `domains/models/invoice.py`.
  - **Rationale**: Boosts AR collections.
  - **KPIs**: 50%+ drip adoption, 60%+ payment rate.

- **[ ] Prep Tray with AR Prioritization (50h)**:
  - `runway/templates/tray.html`: AR hygiene, prioritization (>45d/$5k).
  - `runway/services/tray.py`: Prioritize `invoice` by `aging_days`, `amount`.
  - `runway/services/ar.py`: Send reminders (mocked).
  - Unit tests (`tests/test_tray.py`, `tests/test_ar.py`).
  - **Dependencies**: `domains/models/invoice.py`.
  - **Rationale**: Completes AR OODA.
  - **KPIs**: 80%+ prioritization.

- [ ] **Available Balance for AR (20h)**
  - [ ] Update `runway/services/digest.py` to estimate expected AR payments (e.g., “$5k likely in 7 days” based on historical `invoice` data).
  - [ ] Update `firm.reserved_balance` for AR expectations (e.g., reduce available balance until cleared).
  - [ ] Write unit tests (`tests/test_digest.py`) for balance calculations.
  - **Dependencies**: `firm.py`, `invoice.py`.
  - **Rationale**: Enhances runway accuracy with AR forecasts.
  - **KPIs**: 90%+ balance accuracy.

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


##### Week 14–15: Smart Budgets Development (90 hours)
- **[ ] Dynamic Budgeting Tool (50h)**:
  - `runway/services/budgets.py`: Apportioning checklist (e.g., $5k marketing, $3k rent), auto-adjusts via digest (AR inflows, AP outflows).
  - Fields: `id`, `firm_id`, `category`, `amount`, `allocated`, `variance`, `status` (active/over), `vacation_mode` (bool).
  - `runway/templates/budgets.html`: Visual meter, variance alerts, “Vacation readiness score” (e.g., “Safe with 3 weeks buffer”).
  - `runway/routes/budgets.py`: CRUD for budgets.
  - Unit tests (`tests/test_budgets.py`) with scenarios (e.g., $300 overage).
  - **Dependencies**: `domains/models/budget.py`, `domains/models/firm.py`.
  - **Rationale**: Robust budgeting beyond QBO’s static templates.
  - **KPIs**: 80%+ adherence, 90%+ score accuracy.

- **[ ] Budget Reporting (40h)**:
  - `runway/services/budgets.py`: Variance trends (Chart.js), historical analysis (e.g., “10% overspend last month”).
  - Integrate into `runway/templates/digest.html`.
  - Unit tests (`tests/test_budgets.py`).
  - **Dependencies**: `domains/models/budget.py`.
  - **Rationale**: Drives planning confidence.
  - **KPIs**: 80%+ engagement.

---

#### Phase 3: Smart Automation and Analytics Pack (Q3 2026, ~200 hours)
**Goal**: Add Smart Automation ($99/mo) for rules, Analytics Pack ($99/mo) for insights. Target 50%+ auto-mapped, 80%+ analytics use.

##### Week 16–18: Smart Automation (100 hours)
- **[ ] Dynamic Rules (50h)**:
  - `runway/services/automation.py`: Rules (e.g., “Pay $5k if runway >2 weeks”).
  - Fields: `id`, `firm_id`, `rule_type`, `conditions` (JSON), `actions` (JSON).
  - `runway/services/tray.py`: “Confirm All” for rules.
  - `runway/services/ap.py`: Auto-execute payments (update bill_ingestion.py), release reserves (`firm.reserved_balance -= amount`). 
  - Unit tests (`tests/test_automation.py`).
  - **Dependencies**: `domains/models/policy.py`.
  - **Rationale**: Automates decisions.
  - **KPIs**: 50%+ auto-mapped.

- **[ ] Collaboration Alerts (50h)**:
  - `runway/services/notification.py`: Alerts (e.g., “Confirm $5k”).
  - `runway/routes/notification.py`: CRUD.
  - Integrate SendGrid, log in `audit_log`.
  - Unit tests (`tests/test_notification.py`).
  - **Dependencies**: `domains/models/notification.py`.
  - **Rationale**: Light collaboration.
  - **KPIs**: 80%+ engagement.

##### Week 19–20: Analytics Pack (100 hours)
- **[ ] Aging Analytics (40h)**:
  - `runway/services/analytics.py`: 30/60/90d buckets (Chart.js).
  - `runway/templates/analytics.html`: Visualizations.
  - Unit tests (`tests/test_analytics.py`).
  - **Dependencies**: `domains/models/invoice.py`, `domains/models/bill.py`.
  - **Rationale**: Cash flow insights.
  - **KPIs**: 80%+ use.

- **[ ] Short-Term Cash Flow Forecasting (60h)**:
  - `runway/services/forecast.py`: 2–4 week predictions (e.g., “$5k in 7 days”).
  - `runway/templates/digest.html`, `runway/templates/tray.html`: Display.
  - Unit tests (`tests/test_forecast.py`).
  - **Dependencies**: `domains/models/invoice.py`.
  - **Rationale**: Planning tool.
  - **KPIs**: 90%+ accuracy.

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
---

#### Phase 4: RowCol Integration (Q1 2026, ~150 hours)
**Goal**: Launch RowCol for CAS firms (multi-client rituals). Target 10–20 firm adoptions.

- **[ ] Multi-Client Sync (100h)**:
  - `runway/services/rowcol.py`: Aggregate client runways.
  - `runway/templates/rowcol.html`: Dashboard.
  - Unit tests (`tests/test_rowcol.py`).
  - **Dependencies**: All modules.
  - **Rationale**: CAS anchor.
  - **KPIs**: 50+ client adoptions.

- **[ ] Validation (50h)**:
  - Test with 5 CAS firms.
  - **KPIs**: 90%+ satisfaction.

---

#### Technical Assessment
- **Scalability**: `allowed_roles` supports RowCol roles (vCFO, bookkeeper).

- **Security**: OAuth 2.0, SSL, audit logs.
- **Performance**: SQLite for dev, Lambda for prod (99%+ uptime).
- **Risks**: API limits mitigated with sandbox, scenario gaps with partner feedback.

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

#### Next Steps
- Beta: 5–10 agencies (Q4 2025).
- RowCol Pitch: CAS demo (October 2025).

This plan delivers a best-in-class, modular Oodaloo—download and validate locally!