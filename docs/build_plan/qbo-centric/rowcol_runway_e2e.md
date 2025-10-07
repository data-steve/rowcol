# RowCol Runway End-to-End Build Plan (v2.0 - Agent Ready)

This document provides a detailed, end-to-end build plan for the RowCol `runway/` product. It has been re-engineered to be **executable by an automated agent**, with highly granular, atomic tasks. It introduces a foundational **Phase 0** to align the codebase with the `ADVISOR_FIRST_ARCHITECTURE.md` before building product features.

**Core Principles for Agent Execution:**
- **Atomicity**: Each task is a single, verifiable action (e.g., create a file, define a class, add a field).
- **Explicitness**: File paths, model fields, and function signatures are specified exactly.
- [ ] **Idempotency**: Tasks are defined to be safely re-runnable where possible.
- **Dependency-Driven**: The plan follows a strict dependency graph from Phase 0 onwards.

---

## Table of Contents
- [Phase 0: Foundational Alignment](#phase-0-foundational-alignment)
  - [P0-1: Establish `advisor/` Layer](#p0-1-establish-advisor-layer)
  - [P0-2: Implement Multi-Tenancy & Scoping](#p0-2-implement-multi-tenancy--scoping)
  - [P0-3: Implement Feature Gating System](#p0-3-implement-feature-gating-system)
- [Phase 1: Core Cash Runway Ritual (MVP)](#phase-1-core-cash-runway-ritual-mvp)
  - [P1-1: Client List & Selection](#p1-1-client-list--selection)
  - [P1-2: Digest Tab (Runway Summary)](#p1-2-digest-tab-runway-summary)
  - [P1-3: Hygiene Tab (Data Quality)](#p1-3-hygiene-tab-data-quality)
  - [P1-4: Console Tab (AP/AR Decisions)](#p1-4-console-tab-ap-ar-decisions)
  - [P1-5: QBO Sync & Onboarding](#p1-5-qbo-sync--onboarding)
  - [P1-6: Compliance & Production Readiness](#p1-6-compliance--production-readiness)
- [Phase 2: Smart Features](#phase-2-smart-features)
- [Phase 3: Advisory Deliverables](#phase-3-advisory-deliverables)
- [Phase 4: Automation and Practice Scale](#phase-4-automation-and-practice-scale)

---

## Phase 0: Foundational Alignment
**Goal**: Retrofit the existing codebase to support the multi-product, advisor-first architecture. This phase is a prerequisite for all subsequent product development.

### P0-1: Establish `advisor/` Layer
**User Story**: "As a developer, I need a dedicated `advisor/` layer to house all cross-product advisor workflow logic, separating it from `domains/` and `runway/`."

- [ ] **P0-1.1**: Create directory `advisor/client_management/models/`.
- [ ] **P0-1.2**: Create file `advisor/client_management/models/advisor.py`.
- [ ] **P0-1.3**: In `advisor.py`, define the `Advisor` SQLAlchemy model with fields: `advisor_id` (String, primary_key), `email` (String, unique), `name` (String). Inherit from `Base` and `TimestampMixin`.
- [ ] **P0-1.4**: Create file `advisor/client_management/models/client.py`.
- [ ] **P0-1.5**: In `client.py`, define the `Client` model linking advisors to businesses: `id` (Integer, pk), `advisor_id` (String, FK to `advisors.advisor_id`), `business_id` (String, FK to `businesses.business_id`).
- [ ] **P0-1.6**: Create directory `advisor/client_management/services/`.
- [ ] **P0-1.7**: Create file `advisor/client_management/services/client_service.py`.
- [ ] **P0-1.8**: In `client_service.py`, implement `ClientService` with methods: `add_client_to_advisor`, `list_clients_for_advisor`, `remove_client_from_advisor`. These methods will operate on the `Client` model.

### P0-2: Implement Multi-Tenancy & Scoping
**User Story**: "As a developer, I need to refactor core services to be `advisor_id`-aware, ensuring all data access is securely scoped."

- [ ] **P0-2.1**: Modify `domains/core/services/base_service.py`. Rename `TenantAwareService` to `ScopedService`.
- [ ] **P0-2.2**: Refactor `ScopedService` to accept an `advisor_id` in its constructor.
- [ ] **P0-2.3**: Modify the query methods in `ScopedService` to join through the `Client` mapping table, ensuring all queries are filtered by the provided `advisor_id`.
- [ ] **P0-2.4**: Create a new Alembic migration script to rename the database table `firms` to `advisors` and `firm_id` to `advisor_id` as planned in `ADVISOR_FIRST_ARCHITECTURE.md`.
- [ ] **P0-2.5**: In `infra/auth/auth.py`, update JWT payload to include `advisor_id`. Create a dependency injector to provide the current `advisor_id` from the JWT to services.

### P0-3: Implement Feature Gating System
**User Story**: "As a developer, I need a feature gating system to control access to different product tiers (`basic_ritual_only`, `smart_features_enabled`)."

- [ ] **P0-3.1**: Modify `advisor/client_management/models/advisor.py`. Add fields to the `Advisor` model: `runway_tier` (String, default='basic'), `feature_flags` (JSONB, default={}).
- [ ] **P0-3.2**: Create directory `advisor/subscriptions/`.
- [ ] **P0-3.3**: Create file `advisor/subscriptions/feature_service.py`.
- [ ] **P0-3.4**: In `feature_service.py`, implement `FeatureService` with a method `can_use_feature(advisor: Advisor, feature_name: str) -> bool`. This service will check the advisor's `runway_tier` and `feature_flags`.
- [ ] **P0-3.5**: Define feature constants for `"basic_ritual_only"` and `"smart_features_enabled"` and map them to the appropriate tiers.
- [ ] **P0-3.6**: Create a FastAPI dependency that injects `FeatureService` and can be used as a route decorator to protect endpoints.

## Phase 1: Core Cash Runway Ritual (MVP)
**Goal**: Deliver simplified MVP ($50/client/month) for advisors, replacing spreadsheets with client list and 3-tab view (Digest, Hygiene, Console), scoped by advisor_id. Gate smart features with `basic_ritual_only` (per `2_SMART_FEATURES_REFERENCE.md`). Leverage `infra/qbo/` for QBO integration (per `COMPREHENSIVE_ARCHITECTURE.md`).  
**Timeline**: 4-6 weeks (~180h, per `0_BUILD_PLAN_PHASE1_RUNWAY_DETAILED.md`).  
**Success Criteria**:  
- Client list loads in <2s for 50 clients (per `README.md`, `RowCol_Cash_Runway_Ritual.md`).  
- Advisor completes weekly ritual in <30 min/client (per `0_BUILD_PLAN_PHASE1_RUNWAY_DETAILED.md`).  
- Runway calculation accuracy ≥95% vs. QBO (per `README.md`).  
- 100% test coverage on core flows, zero critical vulnerabilities (per `PRODUCTION_READINESS_CHECKLIST.md`).  
- Onboard new client in <5 min (per `0_BUILD_PLAN_PHASE1_RUNWAY_DETAILED.md`).  

### P1-1: Client List & Selection
**Type**: Execution-Ready  
**User Story**: "As an advisor, I want a client list with key metrics, so I can select clients for the ritual."
**Acceptance Criteria**:  
- [ ] Displays 20-50 clients (name, last_updated, runway status: red/yellow/green using RunwayCoverageBar).  
- [ ] Loads in <2s with pagination, WCAG AA compliant.  
- [ ] No financial advice language ("data shows" vs. "recommend").  
**Subtasks**:  
- [ ] P1-1.2.1: Create FastAPI route (`runway/routes/client_list.py`, GET /advisor/{advisor_id}/clients) (S, 4h)  
  **References**: `advisor/client_management/services/client_service.py`  
- [ ] P1-1.2.2: Build template (`runway/web/templates/client_list.html`, Tailwind CSS, shadcn/ui Table, RunwayCoverageBar for status) (M, 8h)  
  **References**: `build_plan_v5.md` UI playbook, `ui/PLAYBOOK.md`  
- [ ] P1-1.2.3: Add pagination and filtering (`runway/web/static/js/client_list.js`) (S, 4h)  
- [ ] P1-1.2.4: Optimize with PostgreSQL indexing on advisor_id (`infra/database/session.py`) and Redis caching (`infra/queue/job_storage.py`) (S, 4h)  
**Dependencies**: P1-1.1  
**Validation**: Integration test: List loads with scoping. Manual test: <2s for 50 clients, keyboard navigation, compliant language.  
**Effort**: M (20h)  

### P1-1.3: Digest Tab (Task ID: P1-1.3)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want a client’s cash runway summary to assess financial health.  
**Acceptance Criteria**:  
- [ ] Shows balance, runway weeks, pending bills/invoices using RunwayCoverageBar (5-50 weeks).  
- [ ] VarianceChip for delta vs. plan.  
- [ ] WCAG AA, List Mode, no financial advice language.  
**Subtasks**:  
- [ ] P1-1.3.1: Implement `DigestService` with advisor_id, client_id scoping (`runway/services/2_experiences/digest.py`, use `runway/services/0_data_orchestrators/digest_data_orchestrator.py`) (M, 8h)  
  **References**: `domains/core/services/runway_calculator.py`, `COMPREHENSIVE_ARCHITECTURE.md`  
- [ ] P1-1.3.2: Add `basic_ritual_only` to gate smart features (`runway/services/1_calculators/insight_calculator.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P1-1.3.3: Create FastAPI route (`runway/routes/digest.py`, GET /advisor/{advisor_id}/clients/{client_id}/digest) (S, 4h)  
- [ ] P1-1.3.4: Build template (`runway/web/templates/digest.html`, shadcn/ui Card, RunwayCoverageBar, VarianceChip, List Mode toggle) (M, 8h)  
  **References**: `build_plan_v5.md` UI playbook, `ui/PLAYBOOK.md`  
- [ ] P1-1.3.5: Add Storybook tests for accessibility (`tests/runway/test_ui.py`) (S, 4h)  
**Dependencies**: P1-1.1, `infra/qbo/smart_sync.py`  
**Validation**: Integration test: Metrics match QBO data. Manual test: <3s load, "data shows" language, keyboard navigation.  
**Effort**: L (28h)  

### P1-1.4: Hygiene Tab (Task ID: P1-1.4)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want to see data quality issues for a client, so I can prioritize fixes.  
**Acceptance Criteria**:  
- [ ] Shows hygiene score, top 3 issues via Flowband (sparse, 8-12 events).  
- [ ] WCAG AA, List Mode.  
- [ ] Handles datasets consistently.  
**Subtasks**:  
- [ ] P1-1.4.1: Implement `HygieneService` with advisor_id, client_id scoping (`runway/services/2_experiences/tray.py`, use `runway/services/0_data_orchestrators/hygiene_tray_data_orchestrator.py`) (M, 8h)  
  **References**: `COMPREHENSIVE_ARCHITECTURE.md`  
- [ ] P1-1.4.2: Add `basic_ritual_only` to gate smart prioritization (`runway/services/1_calculators/priority_calculator.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P1-1.4.3: Create FastAPI route (`runway/routes/tray.py`, GET /advisor/{advisor_id}/clients/{client_id}/tray) (S, 4h)  
- [ ] P1-1.4.4: Build template (`runway/web/templates/tray.html`, shadcn/ui Card, Flowband with Chart.js, List Mode toggle) (M, 8h)  
  **References**: `build_plan_v5.md` UI playbook, `ui/PLAYBOOK.md`  
- [ ] P1-1.4.5: Add Storybook tests for accessibility (`tests/runway/test_ui.py`) (S, 4h)  
**Dependencies**: P1-1.1, `infra/qbo/smart_sync.py`  
**Validation**: Unit test: Scores consistent with QBO. Manual test: Flowband shows issues, accessible.  
**Effort**: L (28h)  

### P1-1.5: Console Tab (Task ID: P1-1.5)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want batch AP/AR decisions for a client, so I can manage cash flow.  
**Acceptance Criteria**:  
- [ ] Checkbox lists for bills/invoices with "Pay now"/"Send reminder" buttons.  
- [ ] Batch actions complete in <2s for 50 items.  
- [ ] Syncs to QBO without errors.  
- [ ] VarianceChip for deltas, WCAG AA, List Mode.  
**Subtasks**:  
- [ ] P1-1.5.1: Implement `ConsoleService` with advisor_id, client_id scoping (`runway/services/2_experiences/console.py`, use `runway/services/0_data_orchestrators/decision_console_data_orchestrator.py`) (M, 8h)  
  **References**: `COMPREHENSIVE_ARCHITECTURE.md`  
- [ ] P1-1.5.2: Add `basic_ritual_only` to gate smart features (`runway/services/1_calculators/impact_calculator.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P1-1.5.3: Create FastAPI route (`runway/routes/console.py`, POST /advisor/{advisor_id}/clients/{client_id}/console) (S, 4h)  
- [ ] P1-1.5.4: Build template (`runway/web/templates/console.html`, shadcn/ui Table, VarianceChip, List Mode toggle) (M, 8h)  
  **References**: `build_plan_v5.md` UI playbook, `ui/PLAYBOOK.md`  
- [ ] P1-1.5.5: Add Storybook tests for accessibility (`tests/runway/test_ui.py`) (S, 4h)  
**Dependencies**: P1-1.1, `domains/ap/services/bill_service.py`, `domains/ar/services/invoice_service.py`  
**Validation**: Integration test: Actions sync to QBO. Manual test: <2s batch, accessible, "data shows" language.  
**Effort**: L (28h)  

### P1-1.6: QBO Sync Enhancements (Task ID: P1-1.6)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want reliable QBO sync for clients, so I can trust runway data.  
**Acceptance Criteria**:  
- [ ] Syncs bills, invoices, balances for 50 clients without rate limits.  
- [ ] Handles errors with retries, webhooks for real-time updates.  
- [ ] 95%+ delivery rate for syncs.  
**Subtasks**:  
- [ ] P1-1.6.1: Extend `SmartSyncService` with advisor_id, client_id scoping (`infra/qbo/smart_sync.py`) (M, 6h)  
  **References**: `COMPREHENSIVE_ARCHITECTURE.md`, `PRODUCTION_READINESS_CHECKLIST.md`  
- [ ] P1-1.6.2: Add retry logic for rate limits (`infra/qbo/sync_manager.py`) (S, 4h)  
- [ ] P1-1.6.3: Implement webhook handling (`infra/qbo/utils.py`, `domains/webhooks/routes.py`) (S, 4h)  
**Dependencies**: None  
**Validation**: Integration test: Sync 50 clients, handle rate limits. Manual test: Real-time updates via webhooks.  
**Effort**: M (14h)  

### P1-1.7: Audit Trail (Task ID: P1-1.7)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want to track decisions for compliance and review.  
**Acceptance Criteria**:  
- [ ] Logs bill approvals, payments, collections for SOC 2.  
- [ ] Accessible via API/UI.  
- [ ] No data corruption from logs.  
**Subtasks**:  
- [ ] P1-1.7.1: Implement `AuditService` (`domains/core/services/audit_log.py`) (M, 6h)  
  **References**: `PRODUCTION_READINESS_CHECKLIST.md`  
- [ ] P1-1.7.2: Add logging to `BillService`, `InvoiceService` (`domains/ap/services/bill_service.py`, `domains/ar/services/invoice_service.py`) (S, 4h)  
- [ ] P1-1.7.3: Create FastAPI route (`runway/routes/audit.py`, GET /advisor/{advisor_id}/clients/{client_id}/audit) (S, 4h)  
- [ ] P1-1.7.4: Build template (`runway/web/templates/audit.html`, shadcn/ui Table) (S, 4h)  
**Dependencies**: P1-1.1, P1-1.5  
**Validation**: Integration test: Actions logged. Manual test: UI shows trail, no corruption.  
**Effort**: M (18h)  

### P1-1.8: Email Alerts (Task ID: P1-1.8)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want weekly digest emails for clients, so I can stay informed.  
**Acceptance Criteria**:  
- [ ] Sends runway summary emails with >95% delivery rate.  
- [ ] Uses professional templates, SPF/DKIM for compliance.  
**Subtasks**:  
- [ ] P1-1.8.1: Implement `EmailService` (`infra/api/routes/sync.py`, SendGrid integration) (M, 6h)  
  **References**: `PRODUCTION_READINESS_CHECKLIST.md`  
- [ ] P1-1.8.2: Create digest template (`runway/web/templates/digest.html`) (S, 4h)  
- [ ] P1-1.8.3: Schedule job (`infra/jobs/job_scheduler.py`) (S, 4h)  
**Dependencies**: P1-1.3, `infra/qbo/smart_sync.py`  
**Validation**: Integration test: Emails sent to 50 advisors. Manual test: Delivery rate >95%, compliant templates.  
**Effort**: M (14h)  

### P1-1.9: Onboarding (Task ID: P1-1.9)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want to onboard clients with QBO auth, so I can start the ritual.  
**Acceptance Criteria**:  
- [ ] Onboards in <5 min, handles OAuth errors (e.g., 401, MFA).  
- [ ] Securely stores tokens in database.  
- [ ] No TestDrive/Runway Replay (deprecated).  
**Subtasks**:  
- [ ] P1-1.9.1: Implement `OnboardingService` (`advisor/onboarding/services/onboarding_service.py`, QBO auth flow) (M, 8h)  
  **References**: `infra/qbo/auth.py`, `PRODUCTION_READINESS_CHECKLIST.md`  
- [ ] P1-1.9.2: Add OAuth error handling (`infra/qbo/client.py`) (S, 4h)  
- [ ] P1-1.9.3: Create FastAPI route (`runway/routes/onboarding.py`, POST /advisor/{advisor_id}/onboarding) (S, 4h)  
- [ ] P1-1.9.4: Build wizard template (`runway/web/templates/onboarding.html`, shadcn/ui Form, tooltips) (M, 8h)  
  **References**: `ui/PLAYBOOK.md`  
- [ ] P1-1.9.5: Store tokens in database (`infra/database/session.py`) (S, 4h)  
**Dependencies**: P1-1.1, P1-1.6  
**Validation**: Integration test: Tokens stored, errors handled. Manual test: <5 min onboarding.  
**Effort**: L (28h)  

### P1-1.10: Testing Strategy (Task ID: P1-1.10)
**Type**: Execution-Ready  
**User Story**: As a developer, I want comprehensive tests for MVP reliability.  
**Acceptance Criteria**:  
- [ ] 80%+ coverage for `runway/`, `advisor/`.  
- [ ] Tests QBO rate limits, webhooks, runway accuracy (≥95% vs. QBO).  
- [ ] Accessibility tests (WCAG AA).  
**Subtasks**:  
- [ ] P1-1.10.1: Write unit tests for services (`tests/runway/test_digest.py`, `tests/advisor/test_client_service.py`) (M, 8h)  
  **References**: `0_BUILD_PLAN_PHASE1_RUNWAY_DETAILED.md`  
- [ ] P1-1.10.2: Write integration tests for QBO (`tests/infra/test_smart_sync.py`, rate limits, webhooks) (M, 8h)  
  **References**: `PRODUCTION_READINESS_CHECKLIST.md`  
- [ ] P1-1.10.3: Add accessibility tests (`tests/runway/test_ui.py`, Storybook for WCAG AA) (S, 4h)  
  **References**: `build_plan_v5.md` UI playbook  
- [ ] P1-1.10.4: Add coverage report (`tests/coverage.py`) (S, 4h)  
- [ ] P1-1.10.5: Validate runway accuracy (`tests/runway/test_runway_calculator.py`, compare vs. QBO) (S, 4h)  
**Dependencies**: P1-1.1–P1-1.9  
**Validation**: Run `pytest --cov=runway,advisor`; achieve 80%+ coverage. Manual test: Accessibility, error handling.  
**Effort**: L (28h)  

### P1-1.11: Productionalization (Task ID: P1-1.11)
**Type**: Execution-Ready  
**User Story**: As a developer, I want the MVP production-ready for advisors.  
**Acceptance Criteria**:  
- [ ] SOC 2/GDPR-compliant (audit logging, secrets).  
- [ ] 99.9% uptime, <2s responses for 50 clients.  
- [ ] No financial advice language.  
**Subtasks**:  
- [ ] P1-1.11.1: Implement audit logging (`domains/core/services/audit_log.py`, review state-mutating methods) (M, 8h)  
  **References**: `PRODUCTION_READINESS_CHECKLIST.md`  
- [ ] P1-1.11.2: Set up Datadog (`infra/monitoring/datadog.py`) (S, 4h)  
- [ ] P1-1.11.3: Rotate secrets, use AWS Secrets Manager (`infra/auth/auth.py`) (S, 4h)  
- [ ] P1-1.11.4: Configure Docker (`infra/docker/Dockerfile`, docker-compose) (S, 4h)  
- [ ] P1-1.11.5: Audit copy for compliance (`runway/web/templates/`, use "data shows") (S, 4h)  
  **References**: `build_plan_v5.md`  
- [ ] P1-1.11.6: Optimize DB indexing (`infra/database/session.py`) and Redis caching (`infra/queue/job_storage.py`) (S, 4h)  
**Dependencies**: P1-1.1–P1-1.10  
**Validation**: Security scan (OWASP/Snyk): No critical issues. Integration test: <2s responses. Manual test: Uptime, compliant language.  
**Effort**: L (28h)  

## Phase 2: Smart Features
**Goal**: Add Tier 2 smart controls ($150/client/month) for time-saving intelligence, per `1_BUILD_PLAN_PHASE2_SMART_TIER.md`, `2_SMART_FEATURES_REFERENCE.md`.  
**Timeline**: 3-4 months (~72h, parallel with Phase 1 testing).  
**Success Criteria**:  
- 60%+ Phase 1 users upgrade.  
- Advisors save 2-3h/client/week.  
- 70%+ collection response rate (per `2_SMART_FEATURES_REFERENCE.md`).  

### P2-2.1: Earmarking / Reserved Bill Pay (Task ID: P2-2.1)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want to earmark must-pay bills, so I can reserve funds and avoid cash crunches.  
**Acceptance Criteria**:  
- [ ] Earmarks bills, treats as "spent" in balance (available: $X, current: $Y, earmarked: $Z).  
- [ ] Runway uses available balance.  
- [ ] No financial advice language.  
**Subtasks**:  
- [ ] P2-2.1.1: Extend `Bill` model with earmark fields (`domains/ap/models/bill.py`) (S, 2h)  
  **References**: `1_BUILD_PLAN_PHASE2_SMART_TIER.md`  
- [ ] P2-2.1.2: Implement `RunwayReserveService` (`runway/services/0_data_orchestrators/reserve_runway.py`, enable `smart_features_enabled`) (M, 8h)  
- [ ] P2-2.1.3: Create FastAPI routes (`runway/routes/reserve_runway.py`, POST/DELETE /advisor/{advisor_id}/clients/{client_id}/reserve) (S, 2h)  
- [ ] P2-2.1.4: Update Digest UI (`runway/web/templates/digest.html`, show available balance) (S, 2h)  
**Dependencies**: P1-1.3, P1-1.6, `domains/core/services/runway_calculator.py`  
**Validation**: Integration test: Earmarks update runway. Manual test: UI shows balances, compliant language.  
**Effort**: M (14h)  

### P2-2.2: Runway Impact Calculator (Task ID: P2-2.2)
**Type**: Solutioning  
**User Story**: As an advisor, I want to see runway deltas from decisions, so I can optimize cash flow.  
**Acceptance Criteria**:  
- [ ] Shows deltas (e.g., "Delay to Oct 6 → +3 days") in green/red.  
- [ ] Latency <100ms.  
- [ ] No financial advice.  
**Subtasks**:  
- [ ] P2-2.2.1: Assess partial (`runway/services/1_calculators/impact_calculator.py`); document gaps (S, 2h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P2-2.2.2: Implement `ImpactCalculator` with advisor_id, client_id (`runway/services/1_calculators/impact_calculator.py`, enable `smart_features_enabled`) (S, 4h)  
- [ ] P2-2.2.3: Update Console UI (`runway/web/templates/console.html`, VarianceChip) (S, 2h)  
**Dependencies**: P1-1.5, P1-1.3  
**Validation**: Unit test: Deltas match calculations. Manual test: <100ms latency, UI shows deltas.  
**Effort**: S (8h)  

### P2-2.3: 3-Stage Collection Workflows (Task ID: P2-2.3)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want automated collections for overdue invoices, so I can improve cash inflows.  
**Acceptance Criteria**:  
- [ ] Sends reminder, follow-up, escalation emails with >95% delivery.  
- [ ] Tracks responses (>70% rate).  
- [ ] SPF/DKIM compliant.  
**Subtasks**:  
- [ ] P2-2.3.1: Implement `CollectionsService` (`runway/services/0_data_orchestrators/collections.py`, enable `smart_features_enabled`) (L, 10h)  
  **References**: `1_BUILD_PLAN_PHASE2_SMART_TIER.md`, `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P2-2.3.2: Create FastAPI route (`runway/routes/collections.py`, POST /advisor/{advisor_id}/clients/{client_id}/collections) (S, 3h)  
- [ ] P2-2.3.3: Update Console UI (`runway/web/templates/console.html`) (S, 2h)  
**Dependencies**: P1-1.5, P1-1.8, `domains/ar/services/invoice_service.py`  
**Validation**: Integration test: Emails sent, sync to QBO. Manual test: >95% delivery, response tracking.  
**Effort**: L (15h)  

### P2-2.4: Bulk Payment Matching (Task ID: P2-2.4)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want to match bulk payments to invoices, so I can reconcile accounts efficiently.  
**Acceptance Criteria**:  
- [ ] Suggests matches with >80% accuracy.  
- [ ] Manual override, no data corruption.  
**Subtasks**:  
- [ ] P2-2.4.1: Implement `PaymentMatchingService` (`runway/services/0_data_orchestrators/payment_matching.py`, enable `smart_features_enabled`) (L, 10h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P2-2.4.2: Create FastAPI route (`runway/routes/payments.py`, POST /advisor/{advisor_id}/clients/{client_id}/payment_matching) (S, 3h)  
- [ ] P2-2.4.3: Update Hygiene UI (`runway/web/templates/tray.html`) (S, 2h)  
**Dependencies**: P1-1.4, P1-1.6, `domains/ar/services/payment_matching.py`  
**Validation**: Integration test: Matches sync to QBO. Manual test: >80% accuracy, no corruption.  
**Effort**: L (15h)  

### P2-2.5: Vacation Mode Planning (Task ID: P2-2.5)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want to earmark bills for vacation periods, so I can ensure stability.  
**Acceptance Criteria**:  
- [ ] Auto-earmarks for date range, updates runway.  
- [ ] Latency <100ms for calculations.  
**Subtasks**:  
- [ ] P2-2.5.1: Extend `RunwayReserveService` for vacation mode (`runway/services/0_data_orchestrators/reserve_runway.py`) (M, 6h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P2-2.5.2: Create FastAPI route (`runway/routes/reserve_runway.py`, POST /advisor/{advisor_id}/clients/{client_id}/vacation_mode) (S, 2h)  
- [ ] P2-2.5.3: Update Digest UI (`runway/web/templates/digest.html`) (S, 2h)  
**Dependencies**: P2-2.1, P1-1.3  
**Validation**: Integration test: Earmarks applied, runway updated. Manual test: UI toggle, <100ms.  
**Effort**: M (10h)  

### P2-2.6: Smart Hygiene Prioritization (Task ID: P2-2.6)
**Type**: Solutioning  
**User Story**: As an advisor, I want to prioritize hygiene issues by runway impact, so I can focus on critical fixes.  
**Acceptance Criteria**:  
- [ ] Sorts issues by impact (e.g., "Fix 5 issues → +8 days").  
- [ ] Updates Flowband in Hygiene tab.  
**Subtasks**:  
- [ ] P2-2.6.1: Assess partial (`runway/services/1_calculators/priority_calculator.py`); document gaps (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P2-2.6.2: Implement `PriorityCalculator` (`runway/services/1_calculators/priority_calculator.py`, enable `smart_features_enabled`) (M, 6h)  
- [ ] P2-2.6.3: Update Hygiene UI (`runway/web/templates/tray.html`) (S, 2h)  
**Dependencies**: P1-1.4, P2-2.2  
**Validation**: Unit test: Prioritization matches impacts. Manual test: Flowband updates.  
**Effort**: M (12h)  

### P2-2.7: Variance Alerts (Task ID: P2-2.7)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want alerts for runway changes, so I can act proactively.  
**Acceptance Criteria**:  
- [ ] Sends alerts (e.g., "Runway dropped 8 days: 4 new bills") with >95% delivery.  
- [ ] Proactive notifications.  
**Subtasks**:  
- [ ] P2-2.7.1: Implement snapshot job (`infra/jobs/job_scheduler.py`) (S, 3h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P2-2.7.2: Implement `VarianceService` (`runway/services/1_calculators/insight_calculator.py`, enable `smart_features_enabled`) (S, 3h)  
- [ ] P2-2.7.3: Create email template (`infra/email/templates/variance_alert.html`) (S, 2h)  
**Dependencies**: P1-1.3, P1-1.8  
**Validation**: Integration test: Alerts for >5-day changes. Manual test: >95% delivery.  
**Effort**: S (8h)  

### P2-2.8: Testing and Compliance (Task ID: P2-2.8)
**Type**: Execution-Ready  
**User Story**: As a developer, I want tests for smart features, so I can ensure reliability.  
**Acceptance Criteria**:  
- [ ] 80%+ coverage for smart features.  
- [ ] Compliance with no financial advice.  
**Subtasks**:  
- [ ] P2-2.8.1: Write unit tests (`tests/runway/test_smart_features.py`) (M, 6h)  
- [ ] P2-2.8.2: Update compliance doc (`docs/runway/compliance.md`) (S, 4h)  
**Dependencies**: P2-2.1–P2-2.7  
**Validation**: Run `pytest --cov=runway`; 80%+ coverage. Manual review: Compliant language.  
**Effort**: M (10h)  

## Phase 3: Advisory Deliverables
**Goal**: Add Tier 3 features ($250/client/month) for forecasting and benchmarks, per `2_SMART_FEATURES_REFERENCE.md`.  
**Timeline**: 4-5 months (~63h).  
**Success Criteria**:  
- 90%+ advisors use benchmarks in meetings.  
- Forecasting accuracy >85% over 7 days.  
- 3+ scenario comparisons per client/month.  

### P3-3.1: Latest Safe Pay Date Calculation (Task ID: P3-3.1)
**Type**: Solutioning  
**User Story**: As an advisor, I want to calculate latest safe pay dates for bills, so I can advise on timing.  
**Acceptance Criteria**:  
- [ ] Calculates dates based on runway impact.  
- [ ] Updates Console UI.  
**Subtasks**:  
- [ ] P3-3.1.1: Assess requirements (`runway/services/1_calculators/safe_pay_date.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P3-3.1.2: Implement `SafePayDateCalculator` (`runway/services/1_calculators/safe_pay_date.py`) (M, 8h)  
- [ ] P3-3.1.3: Update Console UI (`runway/web/templates/console.html`) (S, 4h)  
**Dependencies**: P2-2.2, P1-1.5  
**Validation**: Unit test: Dates align with impacts. Manual test: UI updates.  
**Effort**: M (16h)  

### P3-3.2: Customer Payment Profiles (Task ID: P3-3.2)
**Type**: Solutioning  
**User Story**: As an advisor, I want customer payment profiles, so I can predict inflows.  
**Acceptance Criteria**:  
- [ ] Profiles based on history (e.g., "pays in 47 days").  
- [ ] Updates Digest UI.  
**Subtasks**:  
- [ ] P3-3.2.1: Assess partial (`runway/services/1_calculators/customer_profiles.py`) (S, 3h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P3-3.2.2: Implement `CustomerProfileService` (`runway/services/1_calculators/customer_profiles.py`) (M, 6h)  
- [ ] P3-3.2.3: Update Digest UI (`runway/web/templates/digest.html`) (S, 3h)  
**Dependencies**: P2-2.3  
**Validation**: Unit test: Profiles match history. Manual test: UI shows profiles.  
**Effort**: M (12h)  

### P3-3.3: Data Quality Scoring (Task ID: P3-3.3)
**Type**: Solutioning  
**User Story**: As an advisor, I want data quality scores for clients, so I can ensure accurate rituals.  
**Acceptance Criteria**:  
- [ ] Scores for each client (e.g., 85%+).  
- [ ] Updates Hygiene UI.  
**Subtasks**:  
- [ ] P3-3.3.1: Assess partial (`runway/services/1_calculators/data_quality_calculator.py`) (S, 3h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P3-3.3.2: Implement `DataQualityCalculator` (`runway/services/1_calculators/data_quality_calculator.py`) (M, 6h)  
- [ ] P3-3.3.3: Update Hygiene UI (`runway/web/templates/tray.html`) (S, 3h)  
**Dependencies**: P1-1.4  
**Validation**: Unit test: Scores reflect QBO issues. Manual test: UI shows scores.  
**Effort**: M (12h)  

### P3-3.4: Cash Flow Forecasting (Task ID: P3-3.4)
**Type**: Solutioning  
**User Story**: As an advisor, I want 2-4 week forecasts, so I can advise on future cash.  
**Acceptance Criteria**:  
- [ ] Forecasts with >85% accuracy over 7 days.  
- [ ] Updates Digest UI.  
**Subtasks**:  
- [ ] P3-3.4.1: Assess requirements (`runway/services/1_calculators/forecasting.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P3-3.4.2: Implement `ForecastingService` (`runway/services/1_calculators/forecasting.py`) (L, 12h)  
- [ ] P3-3.4.3: Update Digest UI (`runway/web/templates/digest.html`) (S, 4h)  
**Dependencies**: P2-2.2  
**Validation**: Unit test: Accuracy >85%. Manual test: UI shows forecasts.  
**Effort**: L (20h)  

### P3-3.5: Industry Benchmarking (Task ID: P3-3.5)
**Type**: Solutioning  
**User Story**: As an advisor, I want RMA benchmarks, so I can compare clients to industry standards.  
**Acceptance Criteria**:  
- [ ] Integrates RMA, shows comparisons.  
- [ ] Updates Digest UI.  
**Subtasks**:  
- [ ] P3-3.5.1: Assess RMA integration (`infra/api/coa_sync.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P3-3.5.2: Implement `BenchmarkingService` (`runway/services/1_calculators/benchmarking.py`) (L, 12h)  
- [ ] P3-3.5.3: Update Digest UI (`runway/web/templates/digest.html`) (S, 4h)  
**Dependencies**: P1-1.3  
**Validation**: Integration test: Benchmarks align with RMA. Manual test: UI shows comparisons.  
**Effort**: L (20h)  

### P3-3.6: Decision Guardrails (Task ID: P3-3.6)
**Type**: Solutioning  
**User Story**: As an advisor, I want guardrails to prevent risky decisions.  
**Acceptance Criteria**:  
- [ ] Blocks actions that drop runway below threshold.  
- [ ] Updates Console UI.  
**Subtasks**:  
- [ ] P3-3.6.1: Assess requirements (`runway/services/1_calculators/guardrails.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P3-3.6.2: Implement `GuardrailService` (`runway/services/1_calculators/guardrails.py`) (M, 8h)  
- [ ] P3-3.6.3: Update Console UI (`runway/web/templates/console.html`) (S, 4h)  
**Dependencies**: P2-2.2, P1-1.5  
**Validation**: Unit test: Blocks risky actions. Manual test: UI alerts.  
**Effort**: M (16h)  

### P3-3.7: What-If Scenario Planning (Task ID: P3-3.7)
**Type**: Solutioning  
**User Story**: As an advisor, I want to simulate scenarios, so I can test cash flow options.  
**Acceptance Criteria**:  
- [ ] Simulates multiple plans, shows deltas.  
- [ ] Updates Console UI.  
**Subtasks**:  
- [ ] P3-3.7.1: Assess requirements (`runway/services/1_calculators/scenario_planning.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P3-3.7.2: Implement `ScenarioPlanningService` (`runway/services/1_calculators/scenario_planning.py`) (L, 12h)  
- [ ] P3-3.7.3: Update Console UI (`runway/web/templates/console.html`) (S, 4h)  
**Dependencies**: P2-2.2, P3-3.4  
**Validation**: Unit test: Scenarios reflect changes. Manual test: UI shows deltas.  
**Effort**: L (20h)  

## Phase 4: Automation and Practice Scale
**Goal**: Add Tier 4 automation ($500-1050/client/month) for large practices, per `2_SMART_FEATURES_REFERENCE.md`, `ADVISOR_FIRST_ARCHITECTURE.md`.  
**Timeline**: 4-5 months (~47h).  
**Success Criteria**:  
- 95%+ automation success.  
- Advisors manage 2x more clients.  
- <2% churn.  

### P4-4.1: Budget-Based Automation Rules (Task ID: P4-4.1)
**Type**: Solutioning  
**User Story**: As an advisor, I want budget-based rules, so I can automate decisions.  
**Acceptance Criteria**:  
- [ ] Rules based on budgets, runway thresholds.  
- [ ] Updates Console UI.  
**Subtasks**:  
- [ ] P4-4.1.1: Assess requirements (`runway/services/0_data_orchestrators/automation_rules.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P4-4.1.2: Implement `AutomationRuleService` (`runway/services/0_data_orchestrators/automation_rules.py`) (L, 12h)  
- [ ] P4-4.1.3: Update Console UI (`runway/web/templates/console.html`) (S, 4h)  
**Dependencies**: P2-2.2, P3-3.6  
**Validation**: Integration test: Rules execute. Manual test: UI configures rules.  
**Effort**: L (20h)  

### P4-4.2: Conditional Scheduled Payments (Task ID: P4-4.2)
**Type**: Solutioning  
**User Story**: As an advisor, I want conditional payments, so I can schedule based on balance.  
**Acceptance Criteria**:  
- [ ] Schedules with conditions (balance > $X).  
- [ ] Updates Console UI.  
**Subtasks**:  
- [ ] P4-4.2.1: Assess partial (`runway/services/0_data_orchestrators/scheduled_payment_service.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P4-4.2.2: Implement `ConditionalPaymentService` (`runway/services/0_data_orchestrators/scheduled_payment_service.py`) (L, 12h)  
- [ ] P4-4.2.3: Update Console UI (`runway/web/templates/console.html`) (S, 4h)  
**Dependencies**: P2-2.1, P3-3.6  
**Validation**: Integration test: Conditions checked. Manual test: UI schedules.  
**Effort**: L (20h)  

### P4-4.3: Runway Protection Automation (Task ID: P4-4.3)
**Type**: Solutioning  
**User Story**: As an advisor, I want auto-delay of non-essential bills, so I can protect runway.  
**Acceptance Criteria**:  
- [ ] Auto-delays based on thresholds.  
- [ ] Updates Console UI.  
**Subtasks**:  
- [ ] P4-4.3.1: Assess requirements (`runway/services/0_data_orchestrators/runway_protection.py`) (S, 4h)  
  **References**: `2_SMART_FEATURES_REFERENCE.md`  
- [ ] P4-4.3.2: Implement `RunwayProtectionService` (`runway/services/0_data_orchestrators/runway_protection.py`) (M, 8h)  
- [ ] P4-4.3.3: Update Console UI (`runway/web/templates/console.html`) (S, 4h)  
**Dependencies**: P2-2.1, P3-3.6  
**Validation**: Integration test: No breaches. Manual test: UI shows delays.  
**Effort**: M (16h)  

### P4-4.4: Practice Management Tools (Task ID: P4-4.4)
**Type**: Solutioning  
**User Story**: As an advisor, I want multi-advisor tools, so I can scale my practice.  
**Acceptance Criteria**:  
- [ ] Dashboards, RBAC, white-label reports.  
- [ ] Supports multi-advisor firms.  
**Subtasks**:  
- [ ] P4-4.4.1: Create `Practice` model (`advisor/practice/models/practice.py`) (S, 4h)  
  **References**: `ADVISOR_FIRST_ARCHITECTURE.md`  
- [ ] P4-4.4.2: Implement `PracticeService` (`advisor/practice/services/practice_service.py`) (L, 12h)  
- [ ] P4-4.4.3: Update UI for dashboard (`runway/web/templates/practice.html`) (S, 4h)  
**Dependencies**: P1-1.1  
**Validation**: Integration test: RBAC restricts access. Manual test: White-label reports.  
**Effort**: L (20h)  

## Deferred Features
- Runway Reserve: Partial in `runway/services/0_data_orchestrators/reserve_runway.py`, gated by `smart_features_enabled`, reintegrated in P2-2.1.  
- Impact Calculator: Partial in `runway/services/1_calculators/impact_calculator.py`, gated, reintegrated in P2-2.2.  
- Smart Prioritization: Partial in `runway/services/1_calculators/priority_calculator.py`, gated, reintegrated in P2-2.6.  
- Variance Alerts: Partial in `runway/services/1_calculators/insight_calculator.py`, gated, reintegrated in P2-2.7.  
- TestDrive: Excluded, owner-focused (per `README.md`).  

---

**Total Estimated Effort**: Phase 1: 180h (4-6 weeks); Phase 2: 72h; Phase 3: 63h; Phase 4: 47h; Grand Total: 362h (~13 months).  
**Files Created/Modified**: ~100 files across `advisor/`, `runway/`, `infra/`, `domains/`.  
**Lines of Code**: ~15,000-20,000 (including tests).  

*Document Status: v2.0 - Last Updated: 2025-10-02*