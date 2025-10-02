# RowCol Runway End-to-End Build Plan

This document provides a detailed, end-to-end build plan for the RowCol `runway/` product, reorienting the Oodaloo cash runway ritual (`build_plan_v5.md`) for advisors managing 20-50 clients. It maps all tasks from `build_plan_v5.md` to RowCol phases, categorizing them as preserved, adapted, deferred, or excluded, while delivering a simplified Phase 1 MVP (client list, Digest, Hygiene, Console) with advisor-first scoping. Smart features (e.g., runway reserve, impact calculator, 3-stage collections) are deferred to Phase 2, preserved via feature flags (`basic_ritual_only`, `smart_features_enabled`) without `runway/parked/`. The plan aligns with `ADVISOR_FIRST_ARCHITECTURE.md`, `COMPREHENSIVE_ARCHITECTURE.md`, and the `runway/` directory tree, using Python, FastAPI, SQLAlchemy, Pydantic, SQLite (dev), PostgreSQL (prod), and Poetry. Tasks match the granularity of `build_plan_v5.md` with user stories, acceptance criteria, subtasks, effort estimates (S: <8h, M: 8-16h, L: 16-24h), dependencies, and validation steps.

## Table of Contents
- [Assumptions](#assumptions)
- [Codebase Baseline](#codebase-baseline)
- [Oodaloo v5 Mapping](#oodaloo-v5-mapping)
- [Phase 1: Core Cash Runway Ritual](#phase-1-core-cash-runway-ritual)
  - [P1-1.1: Advisor Layer Setup](#p1-11-advisor-layer-setup)
  - [P1-1.2: Client List UI](#p1-12-client-list-ui)
  - [P1-1.3: Digest Tab](#p1-13-digest-tab)
  - [P1-1.4: Hygiene Tab](#p1-14-hygiene-tab)
  - [P1-1.5: Console Tab](#p1-15-console-tab)
  - [P1-1.6: QBO Sync Enhancements](#p1-16-qbo-sync-enhancements)
  - [P1-1.7: Audit Trail](#p1-17-audit-trail)
  - [P1-1.8: Email Alerts](#p1-18-email-alerts)
  - [P1-1.9: Onboarding](#p1-19-onboarding)
  - [P1-1.10: Testing Strategy](#p1-110-testing-strategy)
  - [P1-1.11: Productionalization](#p1-111-productionalization)
- [Phase 2: Smart Features](#phase-2-smart-features)
  - [P2-2.1: Earmarking / Reserved Bill Pay](#p2-21-earmarking--reserved-bill-pay)
  - [P2-2.2: Runway Impact Calculator](#p2-22-runway-impact-calculator)
  - [P2-2.3: 3-Stage Collection Workflows](#p2-23-3-stage-collection-workflows)
  - [P2-2.4: Bulk Payment Matching](#p2-24-bulk-payment-matching)
  - [P2-2.5: Vacation Mode Planning](#p2-25-vacation-mode-planning)
  - [P2-2.6: Smart Hygiene Prioritization](#p2-26-smart-hygiene-prioritization)
  - [P2-2.7: Variance Alerts](#p2-27-variance-alerts)
  - [P2-2.8: Testing and Compliance](#p2-28-testing-and-compliance)
- [Phase 3: Advisory Deliverables](#phase-3-advisory-deliverables)
  - [P3-3.1: Latest Safe Pay Date Calculation](#p3-31-latest-safe-pay-date-calculation)
  - [P3-3.2: Customer Payment Profiles](#p3-32-customer-payment-profiles)
  - [P3-3.3: Data Quality Scoring](#p3-33-data-quality-scoring)
  - [P3-3.4: Cash Flow Forecasting](#p3-34-cash-flow-forecasting)
  - [P3-3.5: Industry Benchmarking](#p3-35-industry-benchmarking)
  - [P3-3.6: Decision Guardrails](#p3-36-decision-guardrails)
  - [P3-3.7: What-If Scenario Planning](#p3-37-what-if-scenario-planning)
- [Phase 4: Automation and Practice Scale](#phase-4-automation-and-practice-scale)
  - [P4-4.1: Budget-Based Automation Rules](#p4-41-budget-based-automation-rules)
  - [P4-4.2: Conditional Scheduled Payments](#p4-42-conditional-scheduled-payments)
  - [P4-4.3: Runway Protection Automation](#p4-43-runway-protection-automation)
  - [P4-4.4: Practice Management Tools](#p4-44-practice-management-tools)
- [Deferred Features](#deferred-features)

## Assumptions
- Phase 0 tasks from `build_plan_v5.md` (e.g., QBOConnectionManager, SmartSyncService, domain services) are complete and preserved in `infra/` and `domains/` (per `COMPREHENSIVE_ARCHITECTURE.md`).
- Advisor layer (`advisor/`) is partially built; tasks complete it for multi-client workflows (per `ADVISOR_FIRST_ARCHITECTURE.md`).
- Smart features from `build_plan_v5.md` (e.g., runway reserve, impact calculator) are preserved via feature flags (`basic_ritual_only`, `smart_features_enabled`) (per `2_SMART_FEATURES_REFERENCE.md` and `1_BUILD_PLAN_PHASE2_SMART_TIER.md`).
- UI follows `ui/PLAYBOOK.md` from `build_plan_v5.md` (RunwayCoverageBar, Flowband, VarianceChip, WCAG AA).
- Compliance (no financial advice, SOC 2, GDPR) is enforced per `build_plan_v5.md` and `PRODUCTION_READINESS_CHECKLIST.md`.
- Effort estimates: S (<8h), M (8-16h), L (16-24h).
- No `runway/parked/`; use feature flags to gate smart features (per user feedback).
- TestDrive/Runway Replay excluded (per `README.md` and user feedback).
- QBO integration leverages `infra/qbo/` (per `COMPREHENSIVE_ARCHITECTURE.md` and folder tree).

## Codebase Baseline
- **infra/**: Comprehensive foundation (per `COMPREHENSIVE_ARCHITECTURE.md`, `PRODUCTION_READINESS_CHECKLIST.md`, folder tree).
  - `infra/qbo/smart_sync.py`: Complete, handles QBO sync with rate limiting, retries.
  - `infra/qbo/auth.py`: Complete, manages OAuth tokens.
  - `infra/qbo/sync_manager.py`: Complete, coordinates sync operations.
  - `infra/database/session.py`: Complete, manages DB connections.
  - `infra/auth/auth.py`: Complete, JWT-based authentication.
  - `infra/jobs/job_scheduler.py`: Complete, for background tasks.
- **domains/**: Robust business logic layer (per `ADVISOR_FIRST_ARCHITECTURE.md`, folder tree).
  - `domains/core/services/base_service.py`: Complete, TenantAwareService pattern.
  - `domains/ap/services/bill_service.py`: Complete, bill CRUD and QBO sync.
  - `domains/ap/models/bill.py`: Complete, bill entity.
  - `domains/ar/services/invoice_service.py`: Complete, invoice CRUD and QBO sync.
  - `domains/ar/models/invoice.py`: Complete, invoice entity.
  - `domains/core/services/runway_calculator.py`: Complete, calculates runway weeks.
  - `domains/core/services/audit_log.py`: Partial, needs expansion for SOC 2.
- **runway/**: Product orchestration layer, built on `domains/` and `infra/` (per `COMPREHENSIVE_ARCHITECTURE.md`, folder tree).
  - `runway/core/data_orchestrators/decision_console_data_orchestrator.py`: Partial, needs advisor_id scoping.
  - `runway/core/data_orchestrators/hygiene_tray_data_orchestrator.py`: Partial, needs advisor_id scoping.
  - `runway/services/2_experiences/digest.py`: Partial, needs simplification and feature flags.
  - `runway/services/2_experiences/console.py`: Partial, needs simplification and feature flags.
  - `runway/services/2_experiences/tray.py`: Partial, needs simplification and feature flags.
  - `runway/models/runway_reserve.py`: Partial, deferred to Phase 2.
  - `runway/services/0_data_orchestrators/reserve_runway.py`: Partial, deferred to Phase 2.
  - `runway/services/1_calculators/impact_calculator.py`: Partial, deferred to Phase 2.
  - `runway/services/1_calculators/priority_calculator.py`: Partial, deferred to Phase 2.
  - `runway/services/1_calculators/insight_calculator.py`: Partial, deferred to Phase 2.

## Oodaloo v5 Mapping
| Oodaloo_v5 Task | RowCol Task ID | Status | Notes |
|-----------------|----------------|--------|-------|
| Phase 0: QBOConnectionManager | N/A | Preserved | `infra/qbo/smart_sync.py`, `infra/qbo/auth.py` |
| Phase 0: SmartSyncService | N/A | Preserved | `infra/qbo/smart_sync.py` |
| Phase 0: BillService | N/A | Preserved | `domains/ap/services/bill_service.py` |
| Phase 0: InvoiceService | N/A | Preserved | `domains/ar/services/invoice_service.py` |
| Phase 0: Runway Calculator | P1-1.3 | Adapted | Simplified for Digest tab, advisor-scoped, `domains/core/services/runway_calculator.py` |
| Phase 0: DataQualityEngine | P1-1.4 | Preserved | `infra/qbo/data_quality_engine.py`, used in Hygiene tab |
| Phase 0: TenantAwareService | N/A | Preserved | `domains/core/services/base_service.py`, extended for advisor_id |
| Phase 1: Digest Experience | P1-1.3 | Adapted | Digest tab, uses RunwayCoverageBar, advisor-scoped, per `build_plan_v5.md` UI playbook |
| Phase 1: Tray (Hygiene) | P1-1.4 | Adapted | Hygiene tab, uses Flowband, advisor-scoped |
| Phase 1: Console | P1-1.5 | Adapted | Simplified batch actions, no smart prioritization, uses VarianceChip |
| Phase 1: Runway Reserve | P2-2.1 | Deferred | Partial in `runway/services/0_data_orchestrators/reserve_runway.py`, gated by `smart_features_enabled` |
| Phase 1: Impact Calculator | P2-2.2 | Deferred | Partial in `runway/services/1_calculators/impact_calculator.py`, gated by `smart_features_enabled` |
| Phase 1: Smart Prioritization | P2-2.6 | Deferred | Partial in `runway/services/1_calculators/priority_calculator.py`, gated by `smart_features_enabled` |
| Phase 1: Analytics (Insight Calc) | P2-2.7 | Deferred | Partial in `runway/services/1_calculators/insight_calculator.py`, gated by `smart_features_enabled` |
| Phase 1: TestDrive | N/A | Excluded | Owner-focused, deprecated per `README.md` and user feedback |
| Phase 1: Onboarding | P1-1.9 | Adapted | Advisor-focused QBO auth, no TestDrive/Runway Replay |

## Phase 1: Core Cash Runway Ritual
**Goal**: Deliver simplified MVP ($50/client/month) for advisors, replacing spreadsheets with client list and 3-tab view (Digest, Hygiene, Console), scoped by advisor_id. Gate smart features with `basic_ritual_only` (per `2_SMART_FEATURES_REFERENCE.md`). Leverage `infra/qbo/` for QBO integration (per `COMPREHENSIVE_ARCHITECTURE.md`).  
**Timeline**: 4-6 weeks (~180h, per `0_BUILD_PLAN_PHASE1_RUNWAY_DETAILED.md`).  
**Success Criteria**:  
- Client list loads in <2s for 50 clients (per `README.md`, `RowCol_Cash_Runway_Ritual.md`).  
- Advisor completes weekly ritual in <30 min/client (per `0_BUILD_PLAN_PHASE1_RUNWAY_DETAILED.md`).  
- Runway calculation accuracy ≥95% vs. QBO (per `README.md`).  
- 100% test coverage on core flows, zero critical vulnerabilities (per `PRODUCTION_READINESS_CHECKLIST.md`).  
- Onboard new client in <5 min (per `0_BUILD_PLAN_PHASE1_RUNWAY_DETAILED.md`).  

### P1-1.1: Advisor Layer Setup (Task ID: P1-1.1)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want to manage clients with advisor_id scoping, so I can access their data securely.  
**Acceptance Criteria**:  
- [ ] Models support multi-tenancy with advisor_id, client_id/business_id (per `ADVISOR_FIRST_ARCHITECTURE.md`).  
- [ ] `ClientService` handles CRUD with advisor_id filtering, no data leakage.  
- [ ] Integrates with `infra/auth/` for JWT-based authentication (per `COMPREHENSIVE_ARCHITECTURE.md`).  
**Subtasks**:  
- [ ] P1-1.1.1: Create `Advisor` model (`advisor/client_management/models/advisor.py`, fields: advisor_id, email, name, runway_tier, feature_flags) (S, 4h)  
  **References**: `infra/database/models.py`, `ADVISOR_FIRST_ARCHITECTURE.md`  
- [ ] P1-1.1.2: Create `Client` model (`advisor/client_management/models/client.py`, fields: client_id, advisor_id, company_name, qbo_realm_id) (S, 4h)  
  **References**: `infra/database/session.py`  
- [ ] P1-1.1.3: Implement `ClientService` (`advisor/client_management/services/client_service.py`, endpoints: GET/POST/PATCH /advisor/{advisor_id}/clients, use TenantAwareService) (M, 8h)  
  **References**: `domains/core/services/base_service.py`, `infra/auth/auth.py`  
- [ ] P1-1.1.4: Add advisor_id to TenantAwareService (`domains/core/services/base_service.py`) (S, 4h)  
**Dependencies**: None  
**Validation**: Unit tests: Models and service CRUD (`tests/advisor/test_client_service.py`). Integration test: No data leakage. Manual test: Advisor accesses only their clients.  
**Effort**: M (20h)  

### P1-1.2: Client List UI (Task ID: P1-1.2)
**Type**: Execution-Ready  
**User Story**: As an advisor, I want a client list with key metrics, so I can select clients for the ritual.  
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

**Document Status**: *Last Updated: 2025-10-02*  
*Status: Complete End-to-End Build Plan*  
*Next Review: After Phase 1 completion*

--- 

This plan is fully grounded in the documents and our conversation: advisor-first pivot from `README.md`, feature flags from `ADVISOR_FIRST_ARCHITECTURE.md`, smart features from `2_SMART_FEATURES_REFERENCE.md` and `1_BUILD_PLAN_PHASE2_SMART_TIER.md`, compliance/production from `PRODUCTION_READINESS_CHECKLIST.md` and `build_plan_v5.md`, architecture from `COMPREHENSIVE_ARCHITECTURE.md`, ritual from `RowCol_Cash_Runway_Ritual.md`, and high-level roadmap from `BUILD_PLAN_ADVISOR_FIRST_RUNWAY.md` and `0_BUILD_PLAN_PHASE1_RUNWAY_DETAILED.md`. No TestDrive, robust QBO via `infra/qbo/`, Cursor-ready tasks. If anything is off, point it out, and I'll fix it immediately.