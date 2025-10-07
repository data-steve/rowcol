# RowCol Financial Control Plane End-to-End Build Plan (v3.0 - Multi-Rail Architecture)

*Complete build plan for the Financial Control Plane - Multi-rail orchestration platform for CAS 2.0 firms*

**Core Principles for Agent Execution:**
- **Atomicity**: Each task is a single, verifiable action (e.g., create a file, define a class, add a field).
- **Explicitness**: File paths, model fields, and function signatures are specified exactly.
- **Idempotency**: Tasks are defined to be safely re-runnable where possible.
- **Dependency-Driven**: The plan follows a strict dependency graph from Phase 0 onwards.

---

## Table of Contents
- [Phase 0: Foundational Alignment](#phase-0-foundational-alignment)
  - [P0-1: Establish `advisor/` Layer](#p0-1-establish-advisor-layer)
  - [P0-2: Implement Multi-Tenancy & Scoping](#p0-2-implement-multi-tenancy--scoping)
  - [P0-3: Implement Feature Gating System](#p0-3-implement-feature-gating-system)
  - [P0-4: Multi-Rail Infrastructure Foundation](#p0-4-multi-rail-infrastructure-foundation)
  - [P0-5: QBO API Capability Audit](#p0-5-qbo-api-capability-audit)
  - [P0-6: Domain/Runway Alignment](#p0-6-domainrunway-alignment)
  - [P0-7: Rail-Specific Configuration Consolidation](#p0-7-rail-specific-configuration-consolidation)
  - [P0-8: Multi-Rail Webhook Infrastructure](#p0-8-multi-rail-webhook-infrastructure)
  - [P0-9: Multi-Rail Sandbox Data Creation](#p0-9-multi-rail-sandbox-data-creation)
  - [P0-10: UI/UX Foundation](#p0-10-uiux-foundation)
  - [P0-11: Technical Debt Resolution](#p0-11-technical-debt-resolution)
  - [P0-12: Threshold Tuning & Policy Management](#p0-12-threshold-tuning--policy-management)
  - [P0-13: Ramp API Integration Reality Check](#p0-13-ramp-api-integration-reality-check)
  - [P0-14: Runway Services Ramp Reality Alignment](#p0-14-runway-services-ramp-reality-alignment)
  - [P0-15: Multi-Rail Identity Graph & Reconciliation](#p0-15-multi-rail-identity-graph--reconciliation)
  - [P0-16: Vendor Normalization Multi-Rail Integration](#p0-16-vendor-normalization-multi-rail-integration)
  - [P0-17: Multi-Rail Data Quality & Categorization](#p0-17-multi-rail-data-quality--categorization)
  - [P0-18: Multi-Rail Testing Strategy & Test Data](#p0-18-multi-rail-testing-strategy--test-data)
  - [P0-19: Console Payment Workflow with Ramp Execution](#p0-19-console-payment-workflow-with-ramp-execution)
- [Phase 1: Financial Control Plane MVP](#phase-1-financial-control-plane-mvp)
  - [P1-1: Multi-Rail Orchestration Layer](#p1-1-multi-rail-orchestration-layer)
  - [P1-2: Multi-Rail Integration](#p1-2-multi-rail-integration)
  - [P1-3: Production Readiness](#p1-3-production-readiness)
  - [P1-4: Role-Based Interfaces](#p1-4-role-based-interfaces)
  - [P1-5: Client Deliverable System](#p1-5-client-deliverable-system)
- [Phase 2: Proactive Planning Features](#phase-2-proactive-planning-features)
  - [P2-1: Cash Flow Projections](#p2-1-cash-flow-projections)
  - [P2-2: Early Collection Workflows](#p2-2-early-collection-workflows)
  - [P2-3: Proactive Bill Scheduling](#p2-3-proactive-bill-scheduling)
- [Phase 3+: Advanced Orchestration](#phase-3-advanced-orchestration)

---

## Phase 0: Foundational Alignment
**Goal**: Retrofit the existing codebase to support the multi-rail Financial Control Plane architecture. This phase is a prerequisite for all subsequent product development.

### Runway Surfaces Overview (Purpose and Success Metrics)
- Digest: Answer “Are we okay?” Success = no surprises; top 3 variances and buffer status are obvious; confidence is clear
- Hygiene Tray: Answer “Can I trust the numbers?” Success = readiness score meets threshold prior to approvals
- Decision Console: Answer “What should we do next?” Success = guardrails enforced; every action logged with Who/What/When (WWW)
- Forecast / Outlook: Answer “What’s coming?” Success = horizon coverage (2–13 weeks), freshness/confidence visible, actionable deltas (not heavy modeling)

### Advisor Modes (How advisors operate the ritual)
- Active (live cash call): Console is primary; Digest projected; WWW captured in-line
- Managed (as-needed): Console/Hygiene during week; weekly Digest summarizes variance and actions
- Silent (auto): Digest-only cadence; thresholds trigger alerts for intervention

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

### P0-4: Multi-Rail Infrastructure Foundation
**User Story**: "As a developer, I need multi-rail infrastructure to support hub-and-spoke architecture with QBO as data hub, Ramp as A/P execution rail, Plaid as verification rail, and Stripe as A/R insights rail."

- [ ] **P0-4.1**: Create directory `infra/ramp/`.
- [ ] **P0-4.2**: Create file `infra/ramp/client.py`.
- [ ] **P0-4.3**: In `client.py`, implement `RampClient` with OAuth 2.0 authentication, bill ingestion, approval, execution, and webhook handling methods.
- [ ] **P0-4.4**: Create file `infra/ramp/models.py`.
- [ ] **P0-4.5**: In `models.py`, define `RampBill`, `RampPayment`, and `RampWebhook` models for data persistence.
- [ ] **P0-4.6**: Enhance `infra/plaid/` for multi-rail usage by adding balance verification and guardrail enforcement methods.
- [ ] **P0-4.7**: Create file `infra/multi_rail/orchestrator.py`.
- [ ] **P0-4.8**: In `orchestrator.py`, implement `MultiRailOrchestrator` class with methods for workflow-specific rail coordination.
- [ ] **P0-4.9**: Create file `infra/multi_rail/validation.py`.
- [ ] **P0-4.10**: In `validation.py`, implement `CrossRailValidationService` for data consistency checking across rails.
- [ ] **P0-4.11**: Create file `infra/multi_rail/webhooks.py`.
- [ ] **P0-4.12**: In `webhooks.py`, implement webhook infrastructure for real-time event handling across all rails.
- [ ] **P0-4.13**: Generalize `SmartSyncService` to `MultiRailSmartSyncService` in `infra/qbo/smart_sync.py`.
- [ ] **P0-4.14**: Add rail-specific error handling and retry logic to `infra/multi_rail/error_handling.py`.

### P0-5: QBO API Capability Audit
**User Story**: "As a developer, I need to audit all QBO operations to remove faulty code that assumes QBO can execute when it only reads."

- [ ] **P0-5.1**: Audit all QBO write operations in `domains/` and `runway/` to identify faulty code.
- [ ] **P0-5.2**: Remove QBO payment execution code from `domains/ap/services/payment.py` (QBO can't execute).
- [ ] **P0-5.3**: Remove QBO bill approval code from `domains/ap/services/bill_ingestion.py` (QBO can't approve).
- [ ] **P0-5.4**: Remove QBO scheduling code from `runway/services/0_data_orchestrators/scheduled_payment_service.py` (QBO can't schedule).
- [ ] **P0-5.5**: Keep only QBO read operations (bills, invoices, balances) in `infra/qbo/smart_sync.py`.
- [ ] **P0-5.6**: Document actual QBO capabilities vs. assumptions in `docs/architecture/qbo_capabilities.md`.

### P0-6: Domain/Runway Alignment
**User Story**: "As a developer, I need to align existing code with ADR-001 domain/runway separation."

- [ ] **P0-6.1**: Move QBO scheduling from `runway/services/0_data_orchestrators/scheduled_payment_service.py` to `domains/ap/services/` (scheduling is primitive).
- [ ] **P0-6.2**: Keep earmarking in `runway/services/0_data_orchestrators/reserve_runway.py` (product feature).
- [ ] **P0-6.3**: Create domain primitives for QBO operations in `domains/ap/services/qbo_operations.py`.
- [ ] **P0-6.4**: Create runway orchestration for multi-rail coordination in `runway/services/orchestration/`.
- [ ] **P0-6.5**: Align reserve runway with domain primitives for proper integration.

### P0-7: Rail-Specific Configuration Consolidation
**User Story**: "As a developer, I need rail-specific configuration files to manage API settings, rate limits, and integration requirements for each rail."

**Integration Strategy**: Extract rail-specific settings from `core_thresholds.py` and create dedicated config files for each rail.

**Tasks**:
- [ ] **P0-7.1**: Create file `infra/config/rail_configs.py` with base `RailConfig` class and rail-specific settings.
- [ ] **P0-7.2**: In `rail_configs.py`, implement `QBOConfig`, `RampConfig`, `PlaidConfig`, `StripeConfig` classes.
- [ ] **P0-7.3**: Move QBO API settings from `core_thresholds.py` to `rail_configs.py` QBOConfig.
- [ ] **P0-7.4**: Define Ramp API settings (rate limits, endpoints, retry logic) in RampConfig.
- [ ] **P0-7.5**: Define Plaid API settings (rate limits, endpoints, retry logic) in PlaidConfig.
- [ ] **P0-7.6**: Define Stripe API settings (rate limits, endpoints, retry logic) in StripeConfig.
- [ ] **P0-7.7**: Update `base_client.py` to use rail-specific configs instead of hardcoded values.
- [ ] **P0-7.8**: Add rail configuration tests in `tests/infra/test_rail_configs.py`.

### P0-8: Multi-Rail Webhook Infrastructure
**User Story**: "As a developer, I need webhook handlers for each rail to process real-time updates and maintain data synchronization."

**Integration Strategy**: Create webhook handlers for Plaid, Stripe, and Ramp based on existing patterns.

**Tasks**:
- [ ] **P0-8.1**: Create file `infra/plaid/webhook.py` with Plaid webhook handler for transaction updates.
- [ ] **P0-8.2**: Create file `infra/stripe/webhook.py` with Stripe webhook handler for payment events.
- [ ] **P0-8.3**: Create file `infra/ramp/webhook.py` with Ramp webhook handler for A/P events.
- [ ] **P0-8.4**: Create file `domains/webhooks/models/webhook_event.py` for webhook event tracking.
- [ ] **P0-8.5**: Create file `infra/plaid/sync.py` with PlaidSyncService for data synchronization.
- [ ] **P0-8.6**: Create file `infra/stripe/sync.py` with StripeSyncService for A/R data sync.
- [ ] **P0-8.7**: Create file `infra/ramp/sync.py` with RampSyncService for A/P data sync.
- [ ] **P0-8.8**: Add webhook handler tests in `tests/infra/test_webhooks.py`.

### P0-9: Multi-Rail Sandbox Data Creation
**User Story**: "As a developer, I need realistic test data for all rails to support development and testing."

**Integration Strategy**: Create comprehensive sandbox data for QBO, Stripe, Plaid, and Ramp integrations.

**Tasks**:
- [ ] **P0-9.1**: Create file `scripts/create_multi_rail_sandbox_data.py` for comprehensive test data generation.
- [ ] **P0-9.2**: In sandbox script, implement QBO sandbox setup with 100 transactions, 50 vendors, 10 jobs.
- [ ] **P0-9.3**: In sandbox script, implement Stripe sandbox setup with 50 charges, 10 payouts.
- [ ] **P0-9.4**: In sandbox script, implement Plaid mock data setup with 100 bank transactions.
- [ ] **P0-9.5**: In sandbox script, implement Ramp mock data setup with 50 bills.
- [ ] **P0-9.6**: Add sandbox data creation tests in `tests/scripts/test_sandbox_data.py`.

### P0-10: UI/UX Foundation
**User Story**: "As a developer, I need a solid UI/UX foundation with design system, templates, and accessibility framework to support all role-based interfaces."

**Integration Strategy**: Build on existing template structure and establish modern UI patterns.

**Tasks**:
- [ ] **P0-10.1**: Set up design system with shadcn/ui components and Tailwind CSS configuration.
- [ ] **P0-10.2**: Create base template architecture in `runway/web/templates/base/` with consistent layout patterns.
- [ ] **P0-10.3**: Implement component library with reusable UI components (RunwayCoverageBar, VarianceChip, etc.).
- [ ] **P0-10.4**: Set up Chart.js integration for data visualization (runway charts, flowband displays).
- [ ] **P0-10.5**: Create accessibility framework with Storybook testing and WCAG compliance.
- [ ] **P0-10.6**: Implement responsive design patterns for desktop and mobile interfaces.
- [ ] **P0-10.7**: Create UI component tests in `tests/runway/test_ui.py` with accessibility validation.
- [ ] **P0-10.8**: Set up UI playbook documentation in `ui/PLAYBOOK.md` with design patterns and guidelines.

### P0-11: Technical Debt Resolution
**User Story**: "As a developer, I need to resolve existing technical debt before building new features to ensure a solid foundation."

**Integration Strategy**: Audit and fix existing codebase issues identified in technical debt backlog.

**Tasks**:
- [ ] **P0-11.1**: Audit existing codebase for architectural violations and deprecated patterns.
- [ ] **P0-11.2**: Fix performance bottlenecks and optimize database queries.
- [ ] **P0-11.3**: Resolve circular import issues and dependency conflicts.
- [ ] **P0-11.4**: Clean up deprecated code patterns and unused functionality.
- [ ] **P0-11.5**: Standardize error handling and logging patterns across services.
- [ ] **P0-11.6**: Update outdated dependencies and resolve security vulnerabilities.
- [ ] **P0-11.7**: Improve test coverage for critical paths and edge cases.
- [ ] **P0-11.8**: Document technical debt resolution in `docs/technical-debt/RESOLUTION_LOG.md`.

### P0-12: Threshold Tuning & Policy Management
**User Story**: "As a CAS 2.0 firm, I need intelligent threshold tuning and policy management to make automation effective, not just automated."

**Integration Strategy**: Build on existing config business rules and add industry benchmarking and dynamic tuning.

**Tasks**:
- [ ] **P0-12.1**: Create file `runway/services/policy/threshold_optimizer.py` for dynamic threshold tuning.
- [ ] **P0-12.2**: In `threshold_optimizer.py`, implement `ThresholdOptimizer` with industry benchmark integration.
- [ ] **P0-12.3**: Create file `runway/services/policy/industry_benchmarks.py` with CAS industry standards.
- [ ] **P0-12.4**: In `industry_benchmarks.py`, implement industry-standard thresholds for runway, payment limits, and risk scoring.
- [ ] **P0-12.5**: Create file `runway/services/policy/ab_testing_framework.py` for threshold effectiveness testing.
- [ ] **P0-12.6**: In `ab_testing_framework.py`, implement A/B testing for threshold optimization.
- [ ] **P0-12.7**: Create file `runway/services/policy/performance_monitor.py` for threshold effectiveness tracking.
- [ ] **P0-12.8**: In `performance_monitor.py`, implement monitoring of threshold performance and false positive/negative rates.
- [ ] **P0-12.9**: Create file `runway/routes/policy_management.py` for threshold configuration UI.
- [ ] **P0-12.10**: Add policy management tests in `tests/runway/test_policy_management.py`.

**Industry Benchmark Integration**:
- [ ] **P0-12.11**: Research and integrate CAS industry standards for runway thresholds (7/30/90 days).
- [ ] **P0-12.12**: Research and integrate payment approval thresholds ($1k auto, $5k review, $10k multi-approval).
- [ ] **P0-12.13**: Research and integrate risk scoring thresholds for customer/vendor assessment.
- [ ] **P0-12.14**: Create threshold recommendation engine based on business size, industry, and performance history.

### P0-13: Ramp API Integration Reality Check
**User Story**: "As a developer, I need to understand Ramp's actual API capabilities and build realistic integration, not assumptions."

**Integration Strategy**: Research Ramp API capabilities and build integration based on actual functionality.

**Tasks**:
- [ ] **P0-13.1**: Research Ramp API documentation for spending limits, approval workflows, and guardrail configuration.
- [ ] **P0-13.2**: Create file `infra/ramp/client.py` with actual Ramp API integration (not placeholder).
- [ ] **P0-13.3**: In `client.py`, implement `RampClient` with spending limit configuration and approval workflow management.
- [ ] **P0-13.4**: Create file `infra/ramp/guardrail_service.py` for Ramp guardrail configuration.
- [ ] **P0-13.5**: In `guardrail_service.py`, implement `RampGuardrailService` for setting spending limits and approval rules.
- [ ] **P0-13.6**: Create file `infra/ramp/approval_workflow.py` for Ramp approval workflow integration.
- [ ] **P0-13.7**: In `approval_workflow.py`, implement `RampApprovalWorkflow` for bill approval and payment execution.
- [ ] **P0-13.8**: Create file `infra/ramp/sync_service.py` for Ramp data synchronization with QBO.
- [ ] **P0-13.9**: In `sync_service.py`, implement `RampSyncService` for syncing bills, payments, and approvals.
- [ ] **P0-13.10**: Add Ramp integration tests in `tests/infra/test_ramp_integration.py`.

**Ramp API Capability Research**:
- [ ] **P0-13.11**: Document Ramp API spending limit configuration capabilities and limitations.
- [ ] **P0-13.12**: Document Ramp API approval workflow capabilities and integration points.
- [ ] **P0-13.13**: Document Ramp API payment execution capabilities and webhook events.
- [ ] **P0-13.14**: Create Ramp API integration guide in `docs/integrations/ramp_api_guide.md`.

### P0-14: Runway Services Ramp Reality Alignment
**User Story**: "As a developer, I need to align existing runway services with Ramp's actual capabilities, not QBO execution assumptions."

**Integration Strategy**: Refactor existing runway services to work with Ramp as the execution rail, not QBO.

**Tasks**:
- [ ] **P0-14.1**: Audit `runway/services/0_data_orchestrators/scheduled_payment_service.py` for QBO execution assumptions.
- [ ] **P0-14.2**: Refactor `ScheduledPaymentService` to use Ramp API for payment execution instead of QBO.
- [ ] **P0-14.3**: Audit `runway/services/0_data_orchestrators/reserve_runway.py` for QBO integration assumptions.
- [ ] **P0-14.4**: Refactor `RunwayReserveService` to work with Ramp guardrails and approval workflows.
- [ ] **P0-14.5**: Create file `runway/services/ramp_integration/ramp_execution_service.py` for Ramp payment execution.
- [ ] **P0-14.6**: In `ramp_execution_service.py`, implement `RampExecutionService` for bill payment execution via Ramp.
- [ ] **P0-14.7**: Create file `runway/services/ramp_integration/ramp_guardrail_service.py` for Ramp guardrail management.
- [ ] **P0-14.8**: In `ramp_guardrail_service.py`, implement `RampGuardrailService` for setting spending limits and approval rules.
- [ ] **P0-14.9**: Update `runway/services/2_experiences/console.py` to use Ramp execution instead of QBO.
- [ ] **P0-14.10**: Update `runway/services/2_experiences/tray.py` to work with Ramp approval workflows.
- [ ] **P0-14.11**: Add Ramp integration tests in `tests/runway/test_ramp_integration.py`.
- [ ] **P0-14.12**: Document Ramp integration changes in `docs/architecture/RAMP_INTEGRATION_ALIGNMENT.md`.

**Ramp Execution Reality Check**:
- [ ] **P0-14.13**: Research Ramp API for bill payment execution capabilities and limitations.
- [ ] **P0-14.14**: Research Ramp API for scheduled payment capabilities and recurring payment management.
- [ ] **P0-14.15**: Research Ramp API for reserve/earmarking capabilities and fund management.
- [ ] **P0-14.16**: Create migration guide from QBO execution to Ramp execution in `docs/migration/QBO_TO_RAMP_EXECUTION.md`.

### P0-15: Multi-Rail Identity Graph & Reconciliation
**User Story**: "As a developer, I need to extend the existing job storage and deduplication infrastructure to handle cross-rail transaction reconciliation and prevent double-counting."

**Integration Strategy**: Extend existing `infra/jobs/job_storage.py` deduplication utilities and `infra/qbo/smart_sync.py` patterns for multi-rail reconciliation.

**Tasks**:
- [ ] **P0-15.1**: Extend `infra/jobs/job_storage.py` with `TransactionIdentity` class for cross-rail transaction identity.
- [ ] **P0-15.2**: In `job_storage.py`, add `CrossRailDeduplicationService` using existing `sha256()` and idempotency patterns.
- [ ] **P0-15.3**: Create file `runway/services/reconciliation/multi_rail_reconciliation.py` for reconciliation orchestration.
- [ ] **P0-15.4**: In `multi_rail_reconciliation.py`, implement `MultiRailReconciliationService` using existing job storage patterns.
- [ ] **P0-15.5**: Extend `domains/vendor_normalization/services.py` with `MultiRailVendorMatcher` for cross-rail vendor matching.
- [ ] **P0-15.6**: In `vendor_normalization/services.py`, add `CrossRailVendorResolution` using existing canonicalization logic.
- [ ] **P0-15.7**: Create file `runway/services/reconciliation/transaction_consolidation.py` for cross-rail deduplication.
- [ ] **P0-15.8**: In `transaction_consolidation.py`, implement `TransactionConsolidationService` using existing deduplication utilities.
- [ ] **P0-15.9**: Create file `runway/routes/reconciliation.py` for reconciliation endpoints using existing job patterns.
- [ ] **P0-15.10**: Add reconciliation tests in `tests/runway/test_reconciliation.py` using existing test patterns.

**Multi-Rail Reconciliation Logic**:
- [ ] **P0-15.11**: Implement Plaid bank transactions → QBO bills reconciliation using existing vendor normalization.
- [ ] **P0-15.12**: Implement Ramp payments → Bank outflows reconciliation using existing deduplication patterns.
- [ ] **P0-15.13**: Implement Stripe invoices → QBO AR reconciliation using existing job storage idempotency.
- [ ] **P0-15.14**: Create reconciliation dashboard in `runway/web/templates/reconciliation_dashboard.html`.

### P0-16: Vendor Normalization Multi-Rail Integration
**User Story**: "As a developer, I need to extend the existing vendor normalization system to work with multi-rail data using the established patterns and infrastructure."

**Integration Strategy**: Extend existing `domains/vendor_normalization/` system to work with Plaid, Ramp, and Stripe data using existing job storage and deduplication patterns.

**Tasks**:
- [ ] **P0-16.1**: Audit existing `domains/vendor_normalization/` system and document current capabilities.
- [ ] **P0-16.2**: Extend `domains/vendor_normalization/services.py` with `MultiRailVendorMatcher` for cross-rail vendor matching.
- [ ] **P0-16.3**: In `services.py`, add `PlaidVendorMatcher` using existing vendor canonicalization and job storage patterns.
- [ ] **P0-16.4**: In `services.py`, add `RampVendorMatcher` for bill vendor identification using existing patterns.
- [ ] **P0-16.5**: In `services.py`, add `StripeCustomerMatcher` for invoice customer identification using existing patterns.
- [ ] **P0-16.6**: Extend existing `normalize_vendor()` method to support multi-rail vendor resolution.
- [ ] **P0-16.7**: Enhance existing COA mapping logic to work with multi-rail transaction categorization.
- [ ] **P0-16.8**: Extend existing USASpending.gov integration to support multi-rail vendor matching.
- [ ] **P0-16.9**: Add multi-rail vendor confidence scoring using existing confidence calculation patterns.
- [ ] **P0-16.10**: Add multi-rail vendor normalization tests in `tests/domains/test_vendor_normalization.py`.

**Vendor Normalization Enhancement**:
- [ ] **P0-16.11**: Integrate existing USASpending.gov data with multi-rail vendor matching using existing scripts.
- [ ] **P0-16.12**: Enhance existing vendor canonicalization to handle bank descriptors and payment descriptions.
- [ ] **P0-16.13**: Create vendor confidence scoring for multi-rail matches using existing confidence patterns.
- [ ] **P0-16.14**: Extend existing vendor normalization tests to cover multi-rail scenarios.

### P0-17: Multi-Rail Data Quality & Categorization
**User Story**: "As a developer, I need to extend the existing job storage and vendor normalization infrastructure to provide intelligent data quality and categorization across all rails."

**Integration Strategy**: Extend existing `infra/jobs/job_storage.py` deduplication and `domains/vendor_normalization/` categorization patterns for multi-rail data quality.

**Tasks**:
- [ ] **P0-17.1**: Extend `infra/jobs/job_storage.py` with `MultiRailCategorizer` for cross-rail categorization.
- [ ] **P0-17.2**: In `job_storage.py`, add `TransactionClassifier` using existing vendor normalization and job patterns.
- [ ] **P0-17.3**: Extend existing `domains/vendor_normalization/services.py` with `CrossRailDuplicateDetector` for duplicate detection.
- [ ] **P0-17.4**: In `vendor_normalization/services.py`, add `DataConsistencyChecker` using existing deduplication utilities.
- [ ] **P0-17.5**: Create file `runway/services/data_quality/multi_rail_quality_service.py` for data quality orchestration.
- [ ] **P0-17.6**: In `multi_rail_quality_service.py`, implement `MultiRailQualityService` using existing job storage patterns.
- [ ] **P0-17.7**: Extend existing `runway/services/2_experiences/tray.py` with multi-rail data quality checks.
- [ ] **P0-17.8**: In `tray.py`, add multi-rail categorization using existing vendor normalization patterns.
- [ ] **P0-17.9**: Create file `runway/routes/data_quality.py` for data quality management endpoints using existing patterns.
- [ ] **P0-17.10**: Add data quality tests in `tests/runway/test_data_quality.py` using existing test patterns.

**Data Quality Features**:
- [ ] **P0-17.11**: Implement transaction categorization using existing vendor normalization and MCC codes.
- [ ] **P0-17.12**: Implement duplicate detection across Plaid, QBO, Ramp, and Stripe using existing deduplication utilities.
- [ ] **P0-17.13**: Implement data consistency validation for cross-rail reconciliation using existing job storage patterns.
- [ ] **P0-17.14**: Create data quality dashboard in `runway/web/templates/data_quality_dashboard.html`.

### P0-18: Multi-Rail Testing Strategy & Test Data
**User Story**: "As a developer, I need comprehensive unit-first testing strategy with realistic multi-rail test data for Financial Control Plane reliability."

**Integration Strategy**: Build on existing test patterns with unit-first approach and multi-rail test data generation.

**Tasks**:
- [ ] **P0-18.1**: Design unit-first testing strategy (unit tests until stable, then integration)
- [ ] **P0-18.2**: Create multi-rail test data generation (QBO, Ramp, Plaid, Stripe scenarios)
- [ ] **P0-18.3**: Implement multi-tenant data isolation testing with realistic client data
- [ ] **P0-18.4**: Create QBO integration testing strategy with mock data
- [ ] **P0-18.5**: Implement performance testing for 100+ clients with multi-rail load
- [ ] **P0-18.6**: Design mock strategy for external APIs (Ramp, Plaid, Stripe)
- [ ] **P0-18.7**: Create realistic test scenarios (missing bills, payment failures, sync issues)
- [ ] **P0-18.8**: Implement cross-rail reconciliation testing with edge cases
- [ ] **P0-18.9**: Create CAS 2.0 multi-client test scenarios (50-100 clients)
- [ ] **P0-18.10**: Add test data validation for multi-rail consistency

**Multi-Rail Test Data Requirements**:
- [ ] **P0-18.11**: QBO test data: 100 transactions, 50 vendors, 10 jobs with realistic patterns
- [ ] **P0-18.12**: Ramp test data: 50 bills, 20 payments, approval workflows with edge cases
- [ ] **P0-18.13**: Plaid test data: 100 bank transactions with vendor matching scenarios
- [ ] **P0-18.14**: Stripe test data: 50 invoices, 20 payments, customer matching scenarios
- [ ] **P0-18.15**: Cross-rail reconciliation test data: matching and mismatching scenarios

### P0-19: Console Payment Workflow with Ramp Execution
**User Story**: "As a developer, I need to implement the console payment workflow using Ramp execution instead of QBO, with proper ADR-001 separation."

**Integration Strategy**: Build on existing payment services but replace QBO execution with Ramp execution and add missing orchestration layer.

**Tasks**:
- [ ] **P0-19.1**: Create `runway/services/orchestration/payment_orchestration_service.py` for decision-to-execution coordination
- [ ] **P0-19.2**: In `payment_orchestration_service.py`, implement `PaymentOrchestrationService` using existing payment services
- [ ] **P0-19.3**: Create `runway/services/experiences/bill_staging_service.py` for post-approval staging
- [ ] **P0-19.4**: In `bill_staging_service.py`, implement `BillStagingService` with immediate reserve allocation
- [ ] **P0-19.5**: Create `runway/services/experiences/decision_validation_service.py` for business rule validation
- [ ] **P0-19.6**: In `decision_validation_service.py`, implement `DecisionValidationService` for payment decisions
- [ ] **P0-19.7**: Update `runway/services/2_experiences/console.py` to use Ramp execution instead of QBO
- [ ] **P0-19.8**: Update `runway/services/0_data_orchestrators/decision_console_data_orchestrator.py` to actually execute payments
- [ ] **P0-19.9**: Create `runway/services/orchestration/batch_processing_service.py` for multiple decision processing
- [ ] **P0-19.10**: In `batch_processing_service.py`, implement `BatchProcessingService` for efficient decision processing

**Ramp Integration Requirements**:
- [ ] **P0-19.11**: Replace QBO payment execution with Ramp API calls in payment orchestration
- [ ] **P0-19.12**: Implement Ramp guardrail validation before payment execution
- [ ] **P0-19.13**: Add Ramp approval workflow integration for payment decisions
- [ ] **P0-19.14**: Implement error handling and rollback strategies for Ramp payment failures
- [ ] **P0-19.15**: Create Ramp payment status tracking and reconciliation

## Phase 1: Financial Control Plane MVP
**Goal**: Deliver the core Financial Control Plane MVP for CAS 2.0 firms, enabling multi-rail orchestration with role-based interfaces for bookkeepers, controllers, and advisors.
**Timeline**: 6-8 weeks (~120h).
**Success Criteria**:
- Multi-client console loads in <2s for 100 clients (CAS 2.0 requirement)
- Role-based interfaces support bookkeeper → controller → advisor workflow chain
- Data completeness scoring >90% accuracy for missing bill detection
- Firm-level analytics provide accurate aggregate metrics across all clients
- Multi-rail orchestration with 95%+ accuracy across QBO, Ramp, and Plaid
- Client deliverables generated automatically with branded reports
- 100% test coverage on core flows, zero critical vulnerabilities

### P1-1: Multi-Rail Orchestration Layer
**User Story**: "As a developer, I need a central orchestration layer that coordinates multi-rail operations for the Financial Control Plane."

**Integration Strategy**: Build on existing `BaseAPIClient` infrastructure and coordinate with existing `RunwayReserveService`.

- [ ] **P1-1.1**: Create file `runway/services/orchestration/multi_rail_service.py`.
- [ ] **P1-1.2**: In `multi_rail_service.py`, implement `MultiRailService` with methods for workflow-specific rail coordination.
- [ ] **P1-1.3**: Create file `runway/services/orchestration/verification_loop.py`.
- [ ] **P1-1.4**: In `verification_loop.py`, implement `VerificationLoopService` for chain of custody management across rails.
- [ ] **P1-1.5**: Create file `runway/services/orchestration/workflow_coordinator.py`.
- [ ] **P1-1.6**: In `workflow_coordinator.py`, implement `WorkflowCoordinator` for A/P, A/R, and cash workflow orchestration.
- [ ] **P1-1.7**: Create file `runway/services/orchestration/rail_health_monitor.py`.
- [ ] **P1-1.8**: In `rail_health_monitor.py`, implement `RailHealthMonitor` for monitoring integration health across all rails.
- [ ] **P1-1.9**: Integrate with existing `RunwayReserveService` for earmarking coordination.
- [ ] **P1-1.10**: Create FastAPI routes in `runway/routes/orchestration.py` for orchestration endpoints.
- [ ] **P1-1.11**: Add orchestration service tests in `tests/runway/test_orchestration.py`.

### P1-2: Multi-Rail Integration
**User Story**: "As a developer, I need seamless integration with QBO, Ramp, and Plaid to support the Financial Control Plane."

#### P1-2.1: QBO Integration (Data Hub)
**User Story**: "As a developer, I need QBO to serve as the data hub for A/P and A/R state."

- [ ] **P1-2.1.1**: Enhance `infra/qbo/client.py` with multi-rail awareness and advisor scoping.
- [ ] **P1-2.1.2**: Update `infra/qbo/smart_sync.py` to support multi-rail data orchestration.
- [ ] **P1-2.1.3**: Create file `infra/qbo/multi_rail_sync.py`.
- [ ] **P1-2.1.4**: In `multi_rail_sync.py`, implement `QBODataHubService` for centralized data management.
- [ ] **P1-2.1.5**: Add QBO multi-rail tests in `tests/infra/test_qbo_multi_rail.py`.

#### P1-2.2: Ramp Integration (A/P Execution Rail)
**User Story**: "As a developer, I need Ramp to serve as the A/P execution rail for bill payments."

- [ ] **P1-2.2.1**: Complete `infra/ramp/client.py` with full API integration for bill approval and payment execution.
- [ ] **P1-2.2.2**: Create file `infra/ramp/webhook_handler.py`.
- [ ] **P1-2.2.3**: In `webhook_handler.py`, implement webhook processing for payment confirmations.
- [ ] **P1-2.2.4**: Create file `infra/ramp/sync_service.py`.
- [ ] **P1-2.2.5**: In `sync_service.py`, implement `RampSyncService` for QBO synchronization.
- [ ] **P1-2.2.6**: Add Ramp integration tests in `tests/infra/test_ramp_integration.py`.

#### P1-2.3: Plaid Integration (Verification Rail)
**User Story**: "As a developer, I need Plaid to serve as the verification rail for cash operations."

- [ ] **P1-2.3.1**: Enhance `infra/plaid/client.py` with multi-rail verification capabilities.
- [ ] **P1-2.3.2**: Create file `infra/plaid/verification_service.py`.
- [ ] **P1-2.3.3**: In `verification_service.py`, implement `PlaidVerificationService` for balance verification and guardrail enforcement.
- [ ] **P1-2.3.4**: Create file `infra/plaid/guardrail_service.py`.
- [ ] **P1-2.3.5**: In `guardrail_service.py`, implement `GuardrailService` for liquidity protection.
- [ ] **P1-2.3.6**: Add Plaid verification tests in `tests/infra/test_plaid_verification.py`.

#### P1-2.4: Stripe Integration (A/R Insights Rail)
**User Story**: "As a developer, I need Stripe to provide A/R insights for the Financial Control Plane."

- [ ] **P1-2.4.1**: Create file `infra/stripe/client.py`.
- [ ] **P1-2.4.2**: In `client.py`, implement `StripeClient` for A/R data ingestion (CSV-based for MVP).
- [ ] **P1-2.4.3**: Create file `infra/stripe/insights_service.py`.
- [ ] **P1-2.4.4**: In `insights_service.py`, implement `StripeInsightsService` for A/R analysis and reporting.
- [ ] **P1-2.4.5**: Add Stripe integration tests in `tests/infra/test_stripe_integration.py`.

### P1-3: Production Readiness
**User Story**: "As a developer, I need the Financial Control Plane to be production-ready with proper monitoring, security, and compliance."

- [ ] **P1-3.1**: Implement comprehensive audit logging in `domains/core/services/audit_log.py`.
- [ ] **P1-3.2**: Set up monitoring and alerting with Datadog integration in `infra/monitoring/datadog.py`.
- [ ] **P1-3.3**: Configure security measures including JWT rotation and AWS Secrets Manager in `infra/auth/auth.py`.
- [ ] **P1-3.4**: Set up Docker containerization in `infra/docker/Dockerfile` and `docker-compose.yml`.
- [ ] **P1-3.5**: Implement rate limiting and API protection in `infra/api/rate_limiting.py`.
- [ ] **P1-3.6**: Add comprehensive error handling and retry logic across all integrations.
- [ ] **P1-3.7**: Create production deployment scripts and documentation.
- [ ] **P1-3.8**: Implement automated testing pipeline with 100% coverage requirements.
- [ ] **P1-3.9**: Add performance optimization for multi-client operations.
- [ ] **P1-3.10**: Create SOC2 compliance documentation and audit trails.

### P1-4: Role-Based Interfaces
**User Story**: "As a CAS 2.0 firm, I need role-specific interfaces for bookkeepers, controllers, and advisors to support our workflow chain."

#### P1-4.1: Bookkeeper Interface (Hygiene Tray)
**User Story**: "As a bookkeeper, I need a hygiene tray to identify and fix data quality issues across all rails."

**Integration Strategy**: Refactor existing `TrayService` and `HygieneTrayDataOrchestrator` into bookkeeper-specific interface.

- [ ] **P1-4.1.1**: Refactor `runway/services/2_experiences/tray.py` into `runway/services/experiences/bookkeeper_hygiene.py`.
- [ ] **P1-4.1.2**: In `bookkeeper_hygiene.py`, implement `BookkeeperHygieneService` with cross-rail data validation and issue prioritization.
- [ ] **P1-4.1.3**: Create file `runway/routes/bookkeeper.py`.
- [ ] **P1-4.1.4**: In `bookkeeper.py`, implement GET `/advisor/{advisor_id}/hygiene` endpoint for hygiene tray data.
- [ ] **P1-4.1.5**: Create template `runway/web/templates/bookkeeper_hygiene.html` with Flowband visualization for data quality issues.
- [ ] **P1-4.1.6**: Add bookkeeper interface tests in `tests/runway/test_bookkeeper.py`.

**Data Completeness Features (Critical for CAS 2.0)**:
- [ ] **P1-4.1.7**: Missing Bill Detection - Compare bank outflows to QBO bills, flag unexplained cash outflows. *Check: existing bank transaction matching logic*
- [ ] **P1-4.1.8**: Data Quality Scoring - Score completeness per client (0-100), track improvements over time. *Check: existing hygiene scoring*
- [ ] **P1-4.1.9**: CAS Firm Workflow - Easy interface for firms to enter missing bills identified by system. *Check: existing bill creation workflows*

Deliverable/UX Notes:
- Show "Pre-flight OK / Needs review" badge (readiness score), surfaced to Digest
- Display data freshness across Plaid/QBO/Ramp to build forecast confidence

#### P1-4.2: Controller Interface (Decision Console)
**User Story**: "As a controller, I need a decision console to approve bills and execute payments with guardrails."

**Integration Strategy**: Refactor existing `DecisionConsoleService` and `DecisionConsoleDataOrchestrator` into controller-specific interface.

- [ ] **P1-4.2.1**: Refactor `runway/services/2_experiences/console.py` into `runway/services/experiences/controller_console.py`.
- [ ] **P1-4.2.2**: In `controller_console.py`, implement `ControllerConsoleService` with Ramp integration for bill approval and payment execution.
- [ ] **P1-4.2.3**: Create file `runway/routes/controller.py`.
- [ ] **P1-4.2.4**: In `controller.py`, implement POST `/advisor/{advisor_id}/clients/{client_id}/approve-bills` endpoint.
- [ ] **P1-4.2.5**: Create template `runway/web/templates/controller_console.html` with bill approval interface and guardrail enforcement.
- [ ] **P1-4.2.6**: Add controller interface tests in `tests/runway/test_controller.py`.

**Execution & Audit Features (Critical for CAS 2.0)**:
- [ ] **P1-4.2.7**: Idempotency Keys - Every approval gets unique execution ID for verification. *Check: `domains/ap/services/payment.py` for existing execution tracking*
- [ ] **P1-4.2.8**: Immutable Audit Log - Who, when, what, snapshot inputs for every decision. *Check: existing audit logging in QBO integration*
- [ ] **P1-4.2.9**: Execution Verification - Webhook reconciliation to verify Ramp payments match bank postings. *Check: existing webhook handling*
- [ ] **P1-4.2.10**: Drift Detection - Flag variance between planned vs actual cash after execution. *Check: `runway/services/1_calculators/` for existing variance tracking*

Deliverable/UX Notes:
- Capture WWW (Who/What/When) on each approval/hold, store in audit trail
- Pipe WWW items into Digest "next steps" so clients see stewardship and ownership

#### P1-4.3: Advisor Interface (Digest Tab + Client Deliverables)
**User Story**: "As an advisor, I need a digest tab and client deliverables to present strategic insights to clients."

**Integration Strategy**: Refactor existing `DigestService` and `DigestDataOrchestrator` into advisor-specific interface.

- [ ] **P1-4.3.1**: Refactor `runway/services/2_experiences/digest.py` into `runway/services/experiences/advisor_digest.py`.
- [ ] **P1-4.3.2**: In `advisor_digest.py`, implement `AdvisorDigestService` with QBO data aggregation and Plaid balance integration.
- [ ] **P1-4.3.3**: Create file `runway/routes/advisor.py`.
- [ ] **P1-4.3.4**: In `advisor.py`, implement GET `/advisor/{advisor_id}/clients/{client_id}/digest` endpoint.
- [ ] **P1-4.3.5**: Create template `runway/web/templates/advisor_digest.html` with runway summary and client insights.
- [ ] **P1-4.3.6**: Add advisor interface tests in `tests/runway/test_advisor.py`.

**Multi-Client Dashboard Features (Critical for CAS 2.0)**:
- [ ] **P1-4.3.7**: Batch Runway View - List all clients with runway status, prioritize by risk (red/yellow/green). *Check: existing multi-client console logic*
- [ ] **P1-4.3.8**: Data Quality Score per Client - Show completeness score alongside runway status. *Check: existing hygiene scoring*
- [ ] **P1-4.3.9**: Firm-Level Analytics - Total clients at risk, average data completeness, total AP/AR due. *Check: existing aggregation logic*
- [ ] **P1-4.3.10**: Export & Reporting - Client list with runway status, weekly firm digest, PDF reports. *Check: existing export functionality*

Deliverable Design Principles:
- Short, branded, trust-building deliverables that show: state → variance → WWW next-actions
- Include "Pre-flight" badge and forecast confidence band; link to audit trail for proof

Meeting Cadence Mapping (auto-populated sections):
- Actuals (cash/buffer)
- AR (aging + friction)
- AP (pending + impact)
- 2–4 week outlook (operational horizon)
- 5–13 week outlook (strategic horizon)
- WWW (accountability loop)

### P1-5: Client Deliverable System
**User Story**: "As an advisor, I need automated client deliverables to justify retainers and build trust."

- [ ] **P1-5.1**: Create file `runway/services/deliverables/client_report_generator.py`.
- [ ] **P1-5.2**: In `client_report_generator.py`, implement `ClientReportGenerator` for branded weekly summaries.
- [ ] **P1-5.3**: Create file `runway/services/deliverables/audit_trail_service.py`.
- [ ] **P1-5.4**: In `audit_trail_service.py`, implement `AuditTrailService` for SOC2-compliant logging and traceability.
- [ ] **P1-5.5**: Create file `runway/services/deliverables/email_service.py`.
- [ ] **P1-5.6**: In `email_service.py`, implement `EmailService` with SendGrid integration for client communications.
- [ ] **P1-5.7**: Create templates in `runway/web/templates/deliverables/` for branded client reports.
- [ ] **P1-5.8**: Create FastAPI routes in `runway/routes/deliverables.py` for deliverable generation.
- [ ] **P1-5.9**: Add deliverable system tests in `tests/runway/test_deliverables.py`.

**White-Label Features (Critical for CAS 2.0)**:
- [ ] **P1-5.10**: Branding Options - Upload firm logo, customize primary color, custom domain (optional). *Check: existing branding infrastructure*
- [ ] **P1-5.11**: Client-Facing Reports - Weekly digest with firm branding, client portal with firm logo. *Check: existing report generation*
- [ ] **P1-5.12**: PDF Reports - Export with firm letterhead, professional presentation. *Check: existing PDF generation*


## Phase 2: Proactive Planning Features
**Goal**: Add proactive planning capabilities to transform the Financial Control Plane from reactive problem-solving to strategic anticipation.
**Timeline**: 4-5 weeks (~80h).
**Success Criteria**:
- 4/8/13 week cash flow projections with >85% accuracy
- Early collection workflows achieve >70% response rate
- Proactive bill scheduling reduces cash flow volatility by 40%
- Advisors save 2-3 hours per client per week

### P2-1: Cash Flow Projections
**User Story**: "As an advisor, I need 4/8/13 week cash flow projections to anticipate future cash needs and advise clients proactively."

- [ ] **P2-1.1**: Create file `runway/services/forecasting/cash_flow_projector.py`.
- [ ] **P2-1.2**: In `cash_flow_projector.py`, implement `CashFlowProjector` with 4/8/13 week projection algorithms.
- [ ] **P2-1.3**: Create file `runway/services/forecasting/accuracy_tracker.py`.
- [ ] **P2-1.4**: In `accuracy_tracker.py`, implement `AccuracyTracker` for projection validation and improvement.
- [ ] **P2-1.5**: Create file `runway/services/forecasting/scenario_planner.py`.
- [ ] **P2-1.6**: In `scenario_planner.py`, implement `ScenarioPlanner` for what-if analysis and contingency planning.
- [ ] **P2-1.7**: Create FastAPI routes in `runway/routes/forecasting.py` for projection endpoints.
- [ ] **P2-1.8**: Create templates in `runway/web/templates/forecasting/` for projection visualization.
- [ ] **P2-1.9**: Add forecasting tests in `tests/runway/test_forecasting.py`.

Forecast Experience Brief (scope & integration, not a new module):
- Horizon control: 2–4 week operational + 5–13 week strategic
- Inputs: AR schedules, AP runs, payroll cycles, known fixed events
- Actions: delay/accelerate toggles; simple what‑if on key drivers
- Outputs: updated runway buffer, variance vs prior forecast, “top 3 surprises”
- Refresh cadence: nightly auto-refresh; manual on demand
- Trust metric: forecast freshness indicator + confidence band based on data latency
- Integration: push summarized forecast deltas into Digest; feed buffer impact to Decision Console

### P2-2: Early Collection Workflows
**User Story**: "As a controller, I need automated early collection workflows to accelerate A/R and improve cash flow."

- [ ] **P2-2.1**: Create file `runway/services/collections/early_collection_service.py`.
- [ ] **P2-2.2**: In `early_collection_service.py`, implement `EarlyCollectionService` with automated reminder sequences.
- [ ] **P2-2.3**: Create file `runway/services/collections/payment_acceleration.py`.
- [ ] **P2-2.4**: In `payment_acceleration.py`, implement `PaymentAccelerationService` for A/R optimization.
- [ ] **P2-2.5**: Create file `runway/services/collections/customer_communication.py`.
- [ ] **P2-2.6**: In `customer_communication.py`, implement `CustomerCommunicationService` for professional client outreach.
- [ ] **P2-2.7**: Create FastAPI routes in `runway/routes/collections.py` for collection workflows.
- [ ] **P2-2.8**: Create email templates in `runway/web/templates/collections/` for automated communications.
- [ ] **P2-2.9**: Add collection workflow tests in `tests/runway/test_collections.py`.

### P2-3: Proactive Bill Scheduling
**User Story**: "As a controller, I need proactive bill scheduling to optimize cash flow timing and reduce volatility."

- [ ] **P2-3.1**: Create file `runway/services/scheduling/bill_scheduler.py`.
- [ ] **P2-3.2**: In `bill_scheduler.py`, implement `BillScheduler` for optimal payment timing based on cash availability.
- [ ] **P2-3.3**: Create file `runway/services/scheduling/cash_optimizer.py`.
- [ ] **P2-3.4**: In `cash_optimizer.py`, implement `CashOptimizer` for liquidity management and buffer maintenance.
- [ ] **P2-3.5**: Create file `runway/services/scheduling/priority_engine.py`.
- [ ] **P2-3.6**: In `priority_engine.py`, implement `PriorityEngine` for bill prioritization based on strategic importance.
- [ ] **P2-3.7**: Create FastAPI routes in `runway/routes/scheduling.py` for scheduling endpoints.
- [ ] **P2-3.8**: Create templates in `runway/web/templates/scheduling/` for scheduling interface.
- [ ] **P2-3.9**: Add scheduling tests in `tests/runway/test_scheduling.py`.

## Phase 3+: Advanced Orchestration
**Goal**: Add advanced orchestration capabilities for enterprise-scale Financial Control Plane operations.
**Timeline**: 6-8 weeks (~60h).
**Success Criteria**:
- Support for 100+ client portfolios with <2s response times
- Advanced automation rules with 95%+ success rate
- Multi-advisor firm support with role-based access control
- Enterprise-grade security and compliance

### P3-1: Enterprise Scale Operations
**User Story**: "As an enterprise CAS 2.0 firm, I need to scale the Financial Control Plane to support 100+ clients with multiple advisors."

- [ ] **P3-1.1**: Implement horizontal scaling architecture with load balancing.
- [ ] **P3-1.2**: Add advanced caching strategies for multi-client operations.
- [ ] **P3-1.3**: Create enterprise dashboard for firm-wide oversight.
- [ ] **P3-1.4**: Implement advanced role-based access control (RBAC).
- [ ] **P3-1.5**: Add white-label customization for client deliverables.

### P3-2: Advanced Automation
**User Story**: "As a controller, I need advanced automation rules to handle complex cash flow scenarios automatically."

- [ ] **P3-2.1**: Create advanced rule engine for complex automation scenarios.
- [ ] **P3-2.2**: Implement machine learning for pattern recognition and optimization.
- [ ] **P3-2.3**: Add conditional logic for dynamic decision making.
- [ ] **P3-2.4**: Create automation audit trails and rollback capabilities.

### P3-3: Integration Ecosystem
**User Story**: "As a developer, I need to expand the integration ecosystem to support additional financial tools and services."

- [ ] **P3-3.1**: Add support for additional payment rails (Relay, Bill.com).
- [ ] **P3-3.2**: Implement advanced A/R integrations (Stripe API, payment portals).
- [ ] **P3-3.3**: Create webhook ecosystem for third-party integrations.
- [ ] **P3-3.4**: Add API marketplace for custom integrations.

---

## **Integration Strategy Summary**

### **What We Can Reuse** (60% of functionality)
- ✅ **Core Calculation Services**: `RunwayCalculator`, `ImpactCalculator`, `PriorityCalculator`, `InsightCalculator`, `DataQualityCalculator`
- ✅ **Reserve Management**: `RunwayReserveService` for earmarking (runway layer)
- ✅ **Experience Services**: `DigestService`, `TrayService`, `DecisionConsoleService` (refactor for roles)
- ✅ **Data Orchestrators**: `DigestDataOrchestrator`, `HygieneTrayDataOrchestrator`, `DecisionConsoleDataOrchestrator`
- ✅ **Domain Services**: AP, AR, Bank, Core domains (enhance for multi-rail)
- ✅ **QBO Integration**: `SmartSyncService` and `infra/qbo/` (enhance for multi-rail)

### **What We Need to Build** (40% of functionality)
- ❌ **Multi-Rail Infrastructure**: Ramp, Stripe, Multi-Rail Orchestrator
- ❌ **Role-Based Interfaces**: Bookkeeper/Controller/Advisor specific services
- ❌ **Verification Loop**: Chain of custody verification across rails
- ❌ **Client Deliverable System**: Branded reports and audit trails
- ❌ **Advisor Scoping**: `advisor_id` scoping throughout system

### **What We Need to Remove** (Faulty Code)
- ❌ **QBO Execution Operations**: Payment execution, bill approval, scheduling (QBO can't do these)
- ❌ **Faulty Assumptions**: Code that assumes QBO can execute when it only reads
- ❌ **Misaligned Architecture**: Code that violates ADR-001 domain/runway separation

### **Integration Approach**
1. **Leverage Existing Architecture**: Build on solid foundation of data orchestrators and calculation services
2. **Extend Don't Replace**: Add multi-rail capabilities to existing services
3. **Role-Based Refactoring**: Transform existing interfaces into role-specific experiences
4. **Incremental Enhancement**: Build new capabilities alongside existing functionality
5. **Clean Up Faulty Code**: Remove operations that QBO doesn't support

---

**Total Estimated Effort**: Phase 0: 280h; Phase 1: 120h; Phase 2: 80h; Phase 3+: 60h; Grand Total: 540h (~13-14 weeks).
**Files Created/Modified**: ~150 files across `advisor/`, `runway/`, `infra/`, `domains/`, and new `multi_rail/` directory.
**Lines of Code**: ~20,000-25,000 (including tests and documentation).

*Document Status: v3.0 - Financial Control Plane Architecture with Integration Strategy*  
*Last Updated: 2025-01-03*
