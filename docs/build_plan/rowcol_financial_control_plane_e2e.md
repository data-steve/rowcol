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
- [Phase 1: Financial Control Plane MVP](#phase-1-financial-control-plane-mvp)
  - [P1-1: Multi-Rail Orchestration Layer](#p1-1-multi-rail-orchestration-layer)
  - [P1-2: Role-Based Interfaces](#p1-2-role-based-interfaces)
  - [P1-3: Client Deliverable System](#p1-3-client-deliverable-system)
  - [P1-4: Multi-Rail Integration](#p1-4-multi-rail-integration)
  - [P1-5: Production Readiness](#p1-5-production-readiness)
- [Phase 2: Proactive Planning Features](#phase-2-proactive-planning-features)
  - [P2-1: Cash Flow Projections](#p2-1-cash-flow-projections)
  - [P2-2: Early Collection Workflows](#p2-2-early-collection-workflows)
  - [P2-3: Proactive Bill Scheduling](#p2-3-proactive-bill-scheduling)
- [Phase 3+: Advanced Orchestration](#phase-3-advanced-orchestration)

---

## Phase 0: Foundational Alignment
**Goal**: Retrofit the existing codebase to support the multi-rail Financial Control Plane architecture. This phase is a prerequisite for all subsequent product development.

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

## Phase 1: Financial Control Plane MVP
**Goal**: Deliver the core Financial Control Plane MVP for CAS 2.0 firms, enabling multi-rail orchestration with role-based interfaces for bookkeepers, controllers, and advisors.
**Timeline**: 6-8 weeks (~120h).
**Success Criteria**:
- Multi-client console loads in <2s for 50 clients
- Role-based interfaces support bookkeeper → controller → advisor workflow chain
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

### P1-2: Role-Based Interfaces
**User Story**: "As a CAS 2.0 firm, I need role-specific interfaces for bookkeepers, controllers, and advisors to support our workflow chain."

#### P1-2.1: Bookkeeper Interface (Hygiene Tray)
**User Story**: "As a bookkeeper, I need a hygiene tray to identify and fix data quality issues across all rails."

**Integration Strategy**: Refactor existing `TrayService` and `HygieneTrayDataOrchestrator` into bookkeeper-specific interface.

- [ ] **P1-2.1.1**: Refactor `runway/services/2_experiences/tray.py` into `runway/services/experiences/bookkeeper_hygiene.py`.
- [ ] **P1-2.1.2**: In `bookkeeper_hygiene.py`, implement `BookkeeperHygieneService` with cross-rail data validation and issue prioritization.
- [ ] **P1-2.1.3**: Create file `runway/routes/bookkeeper.py`.
- [ ] **P1-2.1.4**: In `bookkeeper.py`, implement GET `/advisor/{advisor_id}/hygiene` endpoint for hygiene tray data.
- [ ] **P1-2.1.5**: Create template `runway/web/templates/bookkeeper_hygiene.html` with Flowband visualization for data quality issues.
- [ ] **P1-2.1.6**: Add bookkeeper interface tests in `tests/runway/test_bookkeeper.py`.

#### P1-2.2: Controller Interface (Decision Console)
**User Story**: "As a controller, I need a decision console to approve bills and execute payments with guardrails."

**Integration Strategy**: Refactor existing `DecisionConsoleService` and `DecisionConsoleDataOrchestrator` into controller-specific interface.

- [ ] **P1-2.2.1**: Refactor `runway/services/2_experiences/console.py` into `runway/services/experiences/controller_console.py`.
- [ ] **P1-2.2.2**: In `controller_console.py`, implement `ControllerConsoleService` with Ramp integration for bill approval and payment execution.
- [ ] **P1-2.2.3**: Create file `runway/routes/controller.py`.
- [ ] **P1-2.2.4**: In `controller.py`, implement POST `/advisor/{advisor_id}/clients/{client_id}/approve-bills` endpoint.
- [ ] **P1-2.2.5**: Create template `runway/web/templates/controller_console.html` with bill approval interface and guardrail enforcement.
- [ ] **P1-2.2.6**: Add controller interface tests in `tests/runway/test_controller.py`.

#### P1-2.3: Advisor Interface (Digest Tab + Client Deliverables)
**User Story**: "As an advisor, I need a digest tab and client deliverables to present strategic insights to clients."

**Integration Strategy**: Refactor existing `DigestService` and `DigestDataOrchestrator` into advisor-specific interface.

- [ ] **P1-2.3.1**: Refactor `runway/services/2_experiences/digest.py` into `runway/services/experiences/advisor_digest.py`.
- [ ] **P1-2.3.2**: In `advisor_digest.py`, implement `AdvisorDigestService` with QBO data aggregation and Plaid balance integration.
- [ ] **P1-2.3.3**: Create file `runway/routes/advisor.py`.
- [ ] **P1-2.3.4**: In `advisor.py`, implement GET `/advisor/{advisor_id}/clients/{client_id}/digest` endpoint.
- [ ] **P1-2.3.5**: Create template `runway/web/templates/advisor_digest.html` with runway summary and client insights.
- [ ] **P1-2.3.6**: Add advisor interface tests in `tests/runway/test_advisor.py`.

### P1-3: Client Deliverable System
**User Story**: "As an advisor, I need automated client deliverables to justify retainers and build trust."

- [ ] **P1-3.1**: Create file `runway/services/deliverables/client_report_generator.py`.
- [ ] **P1-3.2**: In `client_report_generator.py`, implement `ClientReportGenerator` for branded weekly summaries.
- [ ] **P1-3.3**: Create file `runway/services/deliverables/audit_trail_service.py`.
- [ ] **P1-3.4**: In `audit_trail_service.py`, implement `AuditTrailService` for SOC2-compliant logging and traceability.
- [ ] **P1-3.5**: Create file `runway/services/deliverables/email_service.py`.
- [ ] **P1-3.6**: In `email_service.py`, implement `EmailService` with SendGrid integration for client communications.
- [ ] **P1-3.7**: Create templates in `runway/web/templates/deliverables/` for branded client reports.
- [ ] **P1-3.8**: Create FastAPI routes in `runway/routes/deliverables.py` for deliverable generation.
- [ ] **P1-3.9**: Add deliverable system tests in `tests/runway/test_deliverables.py`.

### P1-4: Multi-Rail Integration
**User Story**: "As a developer, I need seamless integration with QBO, Ramp, and Plaid to support the Financial Control Plane."

#### P1-4.1: QBO Integration (Data Hub)
**User Story**: "As a developer, I need QBO to serve as the data hub for A/P and A/R state."

- [ ] **P1-4.1.1**: Enhance `infra/qbo/client.py` with multi-rail awareness and advisor scoping.
- [ ] **P1-4.1.2**: Update `infra/qbo/smart_sync.py` to support multi-rail data orchestration.
- [ ] **P1-4.1.3**: Create file `infra/qbo/multi_rail_sync.py`.
- [ ] **P1-4.1.4**: In `multi_rail_sync.py`, implement `QBODataHubService` for centralized data management.
- [ ] **P1-4.1.5**: Add QBO multi-rail tests in `tests/infra/test_qbo_multi_rail.py`.

#### P1-4.2: Ramp Integration (A/P Execution Rail)
**User Story**: "As a developer, I need Ramp to serve as the A/P execution rail for bill payments."

- [ ] **P1-4.2.1**: Complete `infra/ramp/client.py` with full API integration for bill approval and payment execution.
- [ ] **P1-4.2.2**: Create file `infra/ramp/webhook_handler.py`.
- [ ] **P1-4.2.3**: In `webhook_handler.py`, implement webhook processing for payment confirmations.
- [ ] **P1-4.2.4**: Create file `infra/ramp/sync_service.py`.
- [ ] **P1-4.2.5**: In `sync_service.py`, implement `RampSyncService` for QBO synchronization.
- [ ] **P1-4.2.6**: Add Ramp integration tests in `tests/infra/test_ramp_integration.py`.

#### P1-4.3: Plaid Integration (Verification Rail)
**User Story**: "As a developer, I need Plaid to serve as the verification rail for cash operations."

- [ ] **P1-4.3.1**: Enhance `infra/plaid/client.py` with multi-rail verification capabilities.
- [ ] **P1-4.3.2**: Create file `infra/plaid/verification_service.py`.
- [ ] **P1-4.3.3**: In `verification_service.py`, implement `PlaidVerificationService` for balance verification and guardrail enforcement.
- [ ] **P1-4.3.4**: Create file `infra/plaid/guardrail_service.py`.
- [ ] **P1-4.3.5**: In `guardrail_service.py`, implement `GuardrailService` for liquidity protection.
- [ ] **P1-4.3.6**: Add Plaid verification tests in `tests/infra/test_plaid_verification.py`.

#### P1-4.4: Stripe Integration (A/R Insights Rail)
**User Story**: "As a developer, I need Stripe to provide A/R insights for the Financial Control Plane."

- [ ] **P1-4.4.1**: Create file `infra/stripe/client.py`.
- [ ] **P1-4.4.2**: In `client.py`, implement `StripeClient` for A/R data ingestion (CSV-based for MVP).
- [ ] **P1-4.4.3**: Create file `infra/stripe/insights_service.py`.
- [ ] **P1-4.4.4**: In `insights_service.py`, implement `StripeInsightsService` for A/R analysis and reporting.
- [ ] **P1-4.4.5**: Add Stripe integration tests in `tests/infra/test_stripe_integration.py`.

### P1-5: Production Readiness
**User Story**: "As a developer, I need the Financial Control Plane to be production-ready with proper monitoring, security, and compliance."

- [ ] **P1-5.1**: Implement comprehensive audit logging in `domains/core/services/audit_log.py`.
- [ ] **P1-5.2**: Set up monitoring and alerting with Datadog integration in `infra/monitoring/datadog.py`.
- [ ] **P1-5.3**: Configure security measures including JWT rotation and AWS Secrets Manager in `infra/auth/auth.py`.
- [ ] **P1-5.4**: Set up Docker containerization in `infra/docker/Dockerfile` and `docker-compose.yml`.
- [ ] **P1-5.5**: Implement rate limiting and API protection in `infra/api/rate_limiting.py`.
- [ ] **P1-5.6**: Add comprehensive error handling and retry logic across all integrations.
- [ ] **P1-5.7**: Create production deployment scripts and documentation.
- [ ] **P1-5.8**: Implement automated testing pipeline with 100% coverage requirements.
- [ ] **P1-5.9**: Add performance optimization for multi-client operations.
- [ ] **P1-5.10**: Create SOC2 compliance documentation and audit trails.

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

**Total Estimated Effort**: Phase 0: 20h; Phase 1: 120h; Phase 2: 80h; Phase 3+: 60h; Grand Total: 280h (~7-8 weeks).
**Files Created/Modified**: ~150 files across `advisor/`, `runway/`, `infra/`, `domains/`, and new `multi_rail/` directory.
**Lines of Code**: ~20,000-25,000 (including tests and documentation).

*Document Status: v3.0 - Financial Control Plane Architecture with Integration Strategy*  
*Last Updated: 2025-01-03*
