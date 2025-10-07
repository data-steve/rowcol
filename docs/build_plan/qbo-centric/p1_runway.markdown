# RowCol Phase 1: Runway MVP - Detailed Build Plan

**Version**: 1.1  
**Date**: 2025-10-02  
**Target**: Productionizable Tier 1 MVP in 4-6 weeks (~180h)  
**Goal**: Spreadsheet replacement for advisors managing 20-50 clients

## ⚠️ **CRITICAL BUILD PLAN REALITY CHECK**

**This build plan is a starting point, not a finish line.**

### **What This Build Plan Actually Is:**
- High-level phases and tasks linked to master plan (`RowCol Runway End-to-End Build Plan`)
- Actionable, developer-level requirements with task IDs (e.g., P1-1.1)
- Grounded in existing codebase (`infra/`, `domains/`, `runway/`, `advisor/`)

### **What This Build Plan Is NOT:**
- ❌ A complete requirement doc—assumes discovery and gap analysis
- ❌ A final implementation guide—requires solutioning for complex tasks
- ❌ Fully accurate on estimates—based on assumptions

### **Required Healing Process:**
1. **Discovery Phase**: Validate codebase against assumptions
2. **Gap Analysis**: Identify missing details or misalignments
3. **Solutioning Phase**: Design solutions for complex problems
4. **Self-Healing Tasks**: Refine tasks during implementation
5. **Reality Grounding**: Base tasks on actual codebase

### **Core Demands**:
- Multi-tenancy with advisor-client scoping
- QBO integration (API fragility, rate limits, sync)
- Service boundaries (`domains/` vs `runway/`)
- Authentication with advisor-scoped access
- Data orchestration across systems

---

## Overview

Phase 1 delivers the core cash runway ritual for advisors, replacing spreadsheets with a client list and three-tab interface (Digest, Hygiene, Console), scoped by advisor_id. Smart features are gated with `basic_ritual_only`. Leverages `infra/qbo/` for QBO integration and follows `ui/PLAYBOOK.md` for UI standards.

### Success Criteria
- Client list loads in <2s for 50 clients
- Weekly ritual completed in <30 min/client (vs. 2+ hours in spreadsheets)
- Runway calculation accuracy ≥95% vs. QBO
- Zero critical/high security vulnerabilities
- Onboard new client in <5 min
- 80%+ test coverage on core flows

### Value Proposition
- **Tier 1** ($50/client/month): Spreadsheet replacement with visibility and basic decisions

### Phase 1 Features (Priority Order)
1. **Advisor Layer Setup** (P1-1.1, 20h) - Multi-tenancy foundation
2. **Client List UI** (P1-1.2, 20h) - Client selection dashboard
3. **Digest Tab** (P1-1.3, 28h) - Runway summary
4. **Hygiene Tab** (P1-1.4, 28h) - Data quality issues
5. **Console Tab** (P1-1.5, 28h) - Batch AP/AR decisions
6. **QBO Sync Enhancements** (P1-1.6, 14h) - Reliable data sync
7. **Audit Trail** (P1-1.7, 18h) - Compliance logging
8. **Email Alerts** (P1-1.8, 14h) - Weekly notifications
9. **Onboarding** (P1-1.9, 28h) - QBO client setup
10. **Testing Strategy** (P1-1.10, 28h) - Comprehensive tests
11. **Productionalization** (P1-1.11, 28h) - SOC 2/GDPR readiness

**Total Phase 1**: ~180 hours (4-6 weeks full-time)

---

## Feature 1: Client List UI (P1-1.2, 20h)

### Problem Statement
Advisors need a fast, accessible dashboard to select clients.

### User Story
"As an advisor, I want a client list with key metrics, so I can select clients for the ritual."

### Solution Overview
Build a paginated UI with RunwayCoverageBar, optimized for <2s load. Services first, unit tests, then routes/UI.

### Tasks

#### Task P1-1.2.1: Implement ClientListService (M, 8h) - **Execution-Ready**
- **File**: `runway/services/2_experiences/client_list.py`
- [ ] Fetch clients with metrics (name, last_updated, runway_status).
- [ ] Inherit from `ScopedService` and use constructor-provided `advisor_id` for all queries.
**References**: `advisor/client_management/services/client_service.py`, `domains/core/services/runway_calculator.py`  
**Dependencies**: P0-1, P0-2  
**Validation**: Unit test: Returns scoped list (`tests/runway/unit/test_client_list.py`).  

#### Task P1-1.2.2: Create Client List Route (S, 4h) - **Execution-Ready**
- **File**: `runway/routes/client_list.py`, `runway/schemas/client_list.py`
- [ ] GET /advisor/{advisor_id}/clients, Pydantic schema.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`  
**Dependencies**: P1-1.2.1  
**Validation**: Unit test: Route returns valid JSON (`tests/runway/unit/test_routes.py`).  

#### Task P1-1.2.3: Build Client List Template (M, 8h) - **Execution-Ready**
- **File**: `runway/web/templates/client_list.html`
- [ ] shadcn/ui Table, RunwayCoverageBar (red/yellow/green), WCAG AA, List Mode toggle.
- [ ] Narrative copy: "Data shows X clients need attention."
**References**: `ui/PLAYBOOK.md`, `build_plan_v5.md`  
**Dependencies**: P1-1.2.2  
**Validation**: Manual test: Loads <2s, accessible, compliant language.  

#### Task P1-1.2.4: Optimize Performance (S, 4h) - **Execution-Ready**
- **File**: `infra/database/session.py`, `infra/queue/job_storage.py`
- [ ] Add PostgreSQL indexes on advisor_id, Redis caching.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-1.2.3  
**Validation**: Load test: <2s for 50 clients (`tests/integration/test_client_list.py`).  

---

## Feature 2: Digest Tab (P1-1.3, 28h)

### Problem Statement
Advisors need a concise runway summary to assess client health.

### User Story
"As an advisor, I want a client’s cash runway summary to assess financial health."

### Solution Overview
Build Digest tab with RunwayCoverageBar and VarianceChip, gated by `basic_ritual_only`. Services first, unit tests.

### Tasks

#### Task P1-2.1: Implement DigestService (M, 8h) - **Execution-Ready**
- **File**: `runway/services/2_experiences/digest.py`
- [ ] Inherit from `ScopedService`, accepting `advisor_id`. Methods should accept `client_id` (business_id) for specific client data.
- [ ] Use `runway_calculator.py`, Pydantic schema.
**References**: `runway/services/0_data_orchestrators/digest_data_orchestrator.py`, `domains/core/services/runway_calculator.py`  
**Dependencies**: P0-2, `infra/qbo/smart_sync.py`  
**Validation**: Unit test: Metrics match QBO (`tests/runway/unit/test_digest.py`).  

#### Task P1-2.2: Gate Smart Features (S, 4h) - **Execution-Ready**
- **File**: `runway/services/2_experiences/digest.py`
- [ ] Use the `FeatureService` (from P0-3) to check for the `basic_ritual_only` flag before calling `insight_calculator.py`.
**References**: `2_SMART_FEATURES_REFERENCE.md`  
**Dependencies**: P0-3, P1-2.1  
**Validation**: Unit test: Flag skips smart features (`tests/runway/unit/test_feature_flags.py`).  

#### Task P1-2.3: Create Digest Route (S, 4h) - **Execution-Ready**
- **File**: `runway/routes/digest.py`, `runway/schemas/digest.py`
- [ ] GET /advisor/clients/{client_id}/digest. The `advisor_id` will be derived from the JWT token.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`  
**Dependencies**: P1-2.2  
**Validation**: Unit test: Route returns valid JSON (`tests/runway/unit/test_routes.py`).  

#### Task P1-2.4: Build Digest Template (M, 8h) - **Execution-Ready**
- **File**: `runway/web/templates/digest.html`
- [ ] shadcn/ui Card, RunwayCoverageBar (5-50 weeks), VarianceChip, List Mode toggle.
- [ ] Narrative copy: "Data shows runway of X weeks."
**References**: `ui/PLAYBOOK.md`, `build_plan_v5.md`  
**Dependencies**: P1-2.3  
**Validation**: Manual test: Loads <3s, WCAG AA compliant.  

#### Task P1-2.5: Add Accessibility Tests (S, 4h) - **Execution-Ready**
- **File**: `tests/runway/unit/test_ui.py`
- [ ] Storybook tests for WCAG AA.
**References**: `build_plan_v5.md`  
**Dependencies**: P1-2.4  
**Validation**: Run Storybook; no accessibility issues.  

---

## Feature 3: Hygiene Tab (P1-1.4, 28h)

### Problem Statement
Advisors need to identify and prioritize data quality issues.

### User Story
"As an advisor, I want to see data quality issues for a client, so I can prioritize fixes."

### Solution Overview
Build Hygiene tab with Flowband for top issues, gated by `basic_ritual_only`. Services first, unit tests.

### Tasks

#### Task P1-3.1: Implement HygieneService (M, 8h) - **Execution-Ready**
- **File**: `runway/services/2_experiences/tray.py`
- [ ] Inherit from `ScopedService`. Methods should accept `client_id` for specific client data.
- [ ] Use `data_quality_engine.py`, Pydantic schema.
**References**: `runway/services/0_data_orchestrators/hygiene_tray_data_orchestrator.py`, `infra/qbo/data_quality_engine.py`  
**Dependencies**: P0-2, `infra/qbo/smart_sync.py`  
**Validation**: Unit test: Scores match QBO (`tests/runway/unit/test_hygiene.py`).  

#### Task P1-3.2: Gate Smart Features (S, 4h) - **Execution-Ready**
- **File**: `runway/services/2_experiences/tray.py`
- [ ] Use the `FeatureService` (from P0-3) to check for the `basic_ritual_only` flag before calling `priority_calculator.py`.
**References**: `2_SMART_FEATURES_REFERENCE.md`  
**Dependencies**: P0-3, P1-3.1  
**Validation**: Unit test: Flag skips smart features (`tests/runway/unit/test_feature_flags.py`).  

#### Task P1-3.3: Create Hygiene Route (S, 4h) - **Execution-Ready**
- **File**: `runway/routes/tray.py`, `runway/schemas/tray.py`
- [ ] GET /advisor/clients/{client_id}/tray.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`  
**Dependencies**: P1-3.2  
**Validation**: Unit test: Route returns valid JSON (`tests/runway/unit/test_routes.py`).  

#### Task P1-3.4: Build Hygiene Template (M, 8h) - **Execution-Ready**
- **File**: `runway/web/templates/tray.html`
- [ ] shadcn/ui Card, Flowband (Chart.js, 8-12 events), List Mode toggle.
- [ ] Narrative copy: "Data shows top issues to fix."
**References**: `ui/PLAYBOOK.md`, `build_plan_v5.md`  
**Dependencies**: P1-3.3  
**Validation**: Manual test: Shows issues, WCAG AA compliant.  

#### Task P1-3.5: Add Accessibility Tests (S, 4h) - **Execution-Ready**
- **File**: `tests/runway/unit/test_ui.py`
- [ ] Storybook tests for WCAG AA.
**References**: `build_plan_v5.md`  
**Dependencies**: P1-3.4  
**Validation**: Run Storybook; no accessibility issues.  

---

## Feature 4: Console Tab (P1-1.5, 28h)

### Problem Statement
Advisors need efficient batch actions for AP/AR decisions.

### User Story
"As an advisor, I want batch AP/AR decisions for a client, so I can manage cash flow."

### Solution Overview
Build Console tab with checkbox actions, VarianceChip, gated by `basic_ritual_only`. Services first, unit tests.

### Tasks

#### Task P1-4.1: Implement ConsoleService (M, 8h) - **Execution-Ready**
- **File**: `runway/services/2_experiences/console.py`
- [ ] Inherit from `ScopedService` and ensure all actions are authorized for the given `advisor_id` and `client_id`.
- [ ] Use `bill_service.py`, `invoice_service.py`, Pydantic schema.
**References**: `runway/services/0_data_orchestrators/decision_console_data_orchestrator.py`, `domains/ap/services/bill_service.py`  
**Dependencies**: P0-2, `domains/ar/services/invoice_service.py`  
**Validation**: Unit test: Actions sync to QBO (`tests/runway/unit/test_console.py`).  

#### Task P1-4.2: Gate Smart Features (S, 4h) - **Execution-Ready**
- **File**: `runway/services/2_experiences/console.py`
- [ ] Use the `FeatureService` (from P0-3) to check for the `basic_ritual_only` flag before calling `impact_calculator.py`.
**References**: `2_SMART_FEATURES_REFERENCE.md`  
**Dependencies**: P0-3, P1-4.1  
**Validation**: Unit test: Flag skips smart features (`tests/runway/unit/test_feature_flags.py`).  

#### Task P1-4.3: Create Console Route (S, 4h) - **Execution-Ready**
- **File**: `runway/routes/console.py`, `runway/schemas/console.py`
- [ ] POST /advisor/clients/{client_id}/console.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`  
**Dependencies**: P1-4.2  
**Validation**: Unit test: Route processes actions (`tests/runway/unit/test_routes.py`).  

#### Task P1-4.4: Build Console Template (M, 8h) - **Execution-Ready**
- **File**: `runway/web/templates/console.html`
- [ ] shadcn/ui Table, VarianceChip, List Mode toggle, "Pay now"/"Send reminder" buttons.
- [ ] Narrative copy: "Data shows impact of actions."
**References**: `ui/PLAYBOOK.md`, `build_plan_v5.md`  
**Dependencies**: P1-4.3  
**Validation**: Manual test: Batch actions <2s, WCAG AA compliant.  

#### Task P1-4.5: Add Accessibility Tests (S, 4h) - **Execution-Ready**
- **File**: `tests/runway/unit/test_ui.py`
- [ ] Storybook tests for WCAG AA.
**References**: `build_plan_v5.md`  
**Dependencies**: P1-4.4  
**Validation**: Run Storybook; no accessibility issues.  

---

## Feature 5: QBO Sync Enhancements (P1-1.6, 14h)

### Problem Statement
Advisors need reliable QBO sync for accurate data.

### User Story
"As an advisor, I want reliable QBO sync for clients, so I can trust runway data."

### Solution Overview
Enhance `infra/qbo/` for advisor_id scoping, retries, and webhooks. Services first, unit tests.

### Tasks

#### Task P1-5.1: Extend SmartSyncService (M, 6h) - **Execution-Ready**
- **File**: `infra/qbo/smart_sync.py`
- [ ] Refactor sync methods to operate on a specific `client_id` (business_id). Authorization checks should happen at the service layer calling the sync.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`, `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P0-2  
**Validation**: Unit test: Sync respects scoping (`tests/infra/unit/test_smart_sync.py`).  

#### Task P1-5.2: Add Retry Logic (S, 4h) - **Execution-Ready**
- **File**: `infra/qbo/sync_manager.py`
- [ ] Handle rate limits, errors with exponential backoff.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-5.1  
**Validation**: Unit test: Retries succeed (`tests/infra/unit/test_sync_manager.py`).  

#### Task P1-5.3: Implement Webhook Handling (S, 4h) - **Execution-Ready**
- **File**: `infra/qbo/utils.py`, `domains/webhooks/routes.py`
- [ ] Handle QBO webhooks for real-time updates.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-5.2  
**Validation**: Integration test: Webhooks trigger sync (`tests/integration/test_qbo_webhooks.py`).  

---

## Feature 6: Audit Trail (P1-1.7, 18h)

### Problem Statement
Advisors need logging for SOC 2 compliance and review.

### User Story
"As an advisor, I want to track decisions for compliance and review."

### Solution Overview
Expand `audit_log.py` for AP/AR actions, add UI. Services first, unit tests.

### Tasks

#### Task P1-6.1: Implement AuditService (M, 6h) - **Execution-Ready**
- **File**: `domains/core/services/audit_log.py`
- [ ] Ensure all log entries include `advisor_id` and the target `client_id` (business_id).
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P0-2  
**Validation**: Unit test: Logs capture actions (`tests/domains/unit/test_audit_log.py`).  

#### Task P1-6.2: Add Logging to Services (S, 4h) - **Execution-Ready**
- **File**: `domains/ap/services/bill_service.py`, `domains/ar/services/invoice_service.py`
- [ ] Hook audit logging into mutating methods.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`  
**Dependencies**: P1-6.1  
**Validation**: Unit test: Actions logged (`tests/domains/unit/test_bill_service.py`).  

#### Task P1-6.3: Create Audit Route (S, 4h) - **Execution-Ready**
- **File**: `runway/routes/audit.py`, `runway/schemas/audit.py`
- [ ] GET /advisor/clients/{client_id}/audit.
**References**: `build_plan_v5.md`  
**Dependencies**: P1-6.2  
**Validation**: Unit test: Route returns logs (`tests/runway/unit/test_routes.py`).  

#### Task P1-6.4: Build Audit Template (S, 4h) - **Execution-Ready**
- **File**: `runway/web/templates/audit.html`
- [ ] shadcn/ui Table for log display.
**References**: `ui/PLAYBOOK.md`  
**Dependencies**: P1-6.3  
**Validation**: Manual test: UI shows logs, WCAG AA compliant.  

---

## Feature 7: Email Alerts (P1-1.8, 14h)

### Problem Statement
Advisors need weekly notifications to stay informed.

### User Story
"As an advisor, I want weekly digest emails for clients, so I can stay informed."

### Solution Overview
Build email service with SendGrid for digests. Services first, unit tests.

### Tasks

#### Task P1-7.1: Implement EmailService (M, 6h) - **Execution-Ready**
- **File**: `infra/api/routes/sync.py`
- [ ] Integrate SendGrid, configure SPF/DKIM.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-2  
**Validation**: Unit test: Emails sent (`tests/infra/unit/test_email.py`).  

#### Task P1-7.2: Create Digest Email Template (S, 4h) - **Execution-Ready**
- **File**: `runway/web/templates/digest_email.html`
- [ ] Runway summary, compliant language ("Data shows...").
**References**: `build_plan_v5.md`  
**Dependencies**: P1-7.1  
**Validation**: Manual test: Template renders, compliant.  

#### Task P1-7.3: Schedule Email Job (S, 4h) - **Execution-Ready**
- **File**: `infra/jobs/job_scheduler.py`
- [ ] Schedule weekly digests for advisors.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`  
**Dependencies**: P1-7.2  
**Validation**: Integration test: Job sends emails (`tests/integration/test_email_jobs.py`).  

---

## Feature 8: Onboarding (P1-1.9, 28h)

### Problem Statement
Advisors need fast, secure QBO client onboarding.

### User Story
"As an advisor, I want to onboard clients with QBO auth, so I can start the ritual."

### Solution Overview
Build onboarding service with QBO auth, error handling, and UI. Services first, unit tests. No TestDrive.

### Tasks

#### Task P1-8.1: Implement OnboardingService (M, 8h) - **Execution-Ready**
- **File**: `advisor/onboarding/services/onboarding_service.py`
- [ ] Handle QBO OAuth flow, store tokens on the `Business` model, and create a `Client` mapping to the current advisor.
**References**: `infra/qbo/auth.py`, `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P0-1, P0-2  
**Validation**: Unit test: Auth completes (`tests/advisor/unit/test_onboarding.py`).  

#### Task P1-8.2: Add OAuth Error Handling (S, 4h) - **Execution-Ready**
- **File**: `infra/qbo/client.py`
- [ ] Handle 401, MFA errors with user feedback.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-8.1  
**Validation**: Unit test: Errors handled (`tests/infra/unit/test_qbo_auth.py`).  

#### Task P1-8.3: Create Onboarding Route (S, 4h) - **Execution-Ready**
- **File**: `runway/routes/onboarding.py`, `runway/schemas/onboarding.py`
- [ ] POST /advisor/onboarding.
**References**: `build_plan_v5.md`  
**Dependencies**: P1-8.2  
**Validation**: Unit test: Route processes auth (`tests/runway/unit/test_routes.py`).  

#### Task P1-8.4: Build Onboarding Wizard Template (M, 8h) - **Execution-Ready**
- **File**: `runway/web/templates/onboarding.html`
- [ ] shadcn/ui Form, tooltips, WCAG AA.
**References**: `ui/PLAYBOOK.md`  
**Dependencies**: P1-8.3  
**Validation**: Manual test: Onboarding <5 min, accessible.  

#### Task P1-8.5: Secure Token Storage (S, 4h) - **Execution-Ready**
- **File**: `infra/database/session.py`
- [ ] Store QBO tokens securely in database.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-8.4  
**Validation**: Integration test: Tokens stored securely (`tests/integration/test_onboarding.py`).  

---

## Feature 9: Testing Strategy (P1-1.10, 28h)

### Problem Statement
Developers need comprehensive tests for reliability.

### User Story
"As a developer, I want comprehensive tests for MVP reliability."

### Solution Overview
Achieve 80%+ coverage with unit and selective integration tests, unified sandbox data.

### Tasks

#### Task P1-9.1: Build Unified Sandbox Data (M, 8h) - **Execution-Ready**
- **File**: `tests/conftest.py`, `tests/create_sandbox_data.py`
- [ ] Generate realistic QBO data for 50 clients.
**References**: `build_plan_v5.md`, `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P0-1, P1-1 to P1-8  
**Validation**: Run sandbox; generates consistent data.  

#### Task P1-9.2: Write Unit Tests for Services (M, 8h) - **Execution-Ready**
- **File**: `tests/runway/unit/test_digest.py`, `tests/advisor/unit/test_client_service.py`
- [ ] Test DigestService, ClientService with sandbox data.
**References**: `0_BUILD_PLAN_PHASE1_RUNWAY_DETAILED.md`  
**Dependencies**: P1-9.1  
**Validation**: Run pytest; 80%+ coverage (`tests/coverage.py`).  

#### Task P1-9.3: Write Integration Tests (S, 4h) - **Execution-Ready**
- **File**: `tests/integration/test_qbo_integration.py`
- [ ] Test QBO sync, onboarding (no mocks).
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-9.2  
**Validation**: Integration test: Syncs match QBO data.  

#### Task P1-9.4: Add Accessibility Tests (S, 4h) - **Execution-Ready**
- **File**: `tests/runway/unit/test_ui.py`
- [ ] Storybook tests for WCAG AA.
**References**: `build_plan_v5.md`  
**Dependencies**: P1-9.3  
**Validation**: Run Storybook; no accessibility issues.  

#### Task P1-9.5: Validate Runway Accuracy (S, 4h) - **Execution-Ready**
- **File**: `tests/runway/unit/test_runway_calculator.py`
- [ ] Ensure ≥95% accuracy vs. QBO.
**References**: `README.md`  
**Dependencies**: P1-9.4  
**Validation**: Unit test: Accuracy meets threshold.  

---

## Feature 10: Productionalization (P1-1.11, 28h)

### Problem Statement
MVP needs to be production-ready for advisors.

### User Story
"As a developer, I want the MVP production-ready for advisors."

### Solution Overview
Implement SOC 2/GDPR compliance, monitoring, and performance optimizations. Services first, unit tests.

### Tasks

#### Task P1-10.1: Implement Audit Logging (M, 8h) - **Execution-Ready**
- **File**: `domains/core/services/audit_log.py`
- [ ] Log all state-mutating actions (bill approvals, etc.).
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-6  
**Validation**: Integration test: Logs capture changes (`tests/domains/integration/test_audit_log.py`).  

#### Task P1-10.2: Set Up Monitoring (S, 4h) - **Execution-Ready**
- **File**: `infra/monitoring/datadog.py`
- [ ] Configure Datadog for APM, health checks.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-10.1  
**Validation**: Manual test: Alerts on errors.  

#### Task P1-10.3: Rotate Secrets (S, 4h) - **Execution-Ready**
- **File**: `infra/auth/auth.py`
- [ ] Use AWS Secrets Manager for JWT keys, QBO tokens.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-8  
**Validation**: Manual test: Secrets loaded securely.  

#### Task P1-10.4: Configure Docker and DB (S, 4h) - **Execution-Ready**
- **File**: `infra/docker/Dockerfile`, `infra/database/session.py`
- [ ] Dockerize app, set up PostgreSQL with Alembic migrations.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-10.3  
**Validation**: Integration test: Deployment succeeds (`tests/integration/test_deployment.py`).  

#### Task P1-10.5: Audit Compliance Copy (S, 4h) - **Execution-Ready**
- **File**: `runway/web/templates/*`
- [ ] Ensure no financial advice ("data shows" vs. "recommend").
**References**: `build_plan_v5.md`  
**Dependencies**: P1-10.4  
**Validation**: Manual review: Templates compliant.  

#### Task P1-10.6: Optimize Performance (S, 4h) - **Execution-Ready**
- **File**: `infra/database/session.py`, `infra/queue/job_storage.py`
- [ ] Add connection pooling, Redis caching for queries.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P1-10.5  
**Validation**: Load test: Dashboard <2s (`tests/integration/test_performance.py`).  

---

## Success Metrics

### Must-Have Metrics (Launch Blockers)
- ✅ Client list loads in <2s for 50 clients
- ✅ Runway calculation accuracy: ≥95% vs. QBO
- ✅ Zero security vulnerabilities (critical/high)
- ✅ 80%+ test coverage on core flows
- ✅ Onboard new client in <5 min

### Nice-to-Have Metrics (Monitor Post-Launch)
- 🎯 Weekly ritual time: <30 min/client
- 🎯 80%+ advisor weekly return rate
- 🎯 <1% error rate on QBO API calls
- 🎯 Average API response time <500ms

---

## Dependencies & Risks

### Dependencies
- **External**: QBO API read access, SendGrid for emails
- **Internal**: `infra/qbo/` complete, `advisor/` partially built

### Risks & Mitigations
- **Risk**: QBO rate limits disrupt sync
  - **Mitigation**: Retries, webhooks, caching (P1-5.3)
- **Risk**: UI inaccessible
  - **Mitigation**: Storybook tests, WCAG AA (P1-2.5, P1-3.5, P1-4.5)
- **Risk**: Data leakage between advisors
  - **Mitigation**: `advisor_id` scoping via `ScopedService`, RBAC (Phase 0)

---

**Total Estimated Effort**: 180 hours (4-6 weeks full-time)

**Files Created/Modified**: ~80 files across `advisor/`, `runway/`, `infra/`, `domains/`, `tests/`

**Lines of Code**: ~15,000 (including tests)

**Next Steps**: Build Phase 2 offline while Phase 1 is user-tested.