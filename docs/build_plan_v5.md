# Oodaloo v4.5 Restructured Build Plan: Logical MVP Flow

**Version**: 4.5  
**Date**: 2025-09-18  
**Restructured From**: v4.4 Master Build Plan  
**Key Changes**: 
- Removed unrealistic features requiring external data we don't have
- Reordered phases: Analytics → Budget Planning → Smart Automation
- Split major components into dedicated phases for better focus

## Oodaloo → RowCol Transition Architecture

**Key Principle**: `business` in Oodaloo = `client` in RowCol

**Oodaloo (Owner-Centric)**:
- Single business owner managing their QBO
- `business_id` as primary tenant identifier  
- Analytics about the business performance
- Simple user model (owner + bookkeeper)

**RowCol Transition Point**: When we add multi-client management capabilities
- Introduce `firm_id` as higher-level tenant
- `business` becomes `client` in firm context
- Add staff roles, engagement workflows, task management
- Analytics remain client-focused (not firm operational metrics)

**Preserved Concepts**:
- All business/client analytics and KPIs (same data, different context)
- Core AP/AR/Bank domain models (reusable across both products)
- QBO integration patterns (scale from 1:1 to 1:many)

**New RowCol Concepts**:
- `firm` → `client` relationship management
- Staff permissions and role-based access
- Engagement and task workflow management
- Firm-level operational dashboards (separate from client analytics)

### Long-term Considerations
- **QBO App Store Submission**: Requirements and review process timeline
- **CAS Firm Partnerships**: Identify target accounting firms for RowCol phase
- **Compliance Requirements**: SOC 2, data privacy, financial data handling

This plan provides the architectural rigor and detailed task breakdown needed for successful execution while maintaining clear separation between domains/ (QBO primitives) and runway/ (product orchestration).


## Overview
- **Goal**: Build a sellable runway MVP in 6-8 weeks (~300-350h solo) for service agencies ($1M–$5M, 10-30 staff), targeting QBO marketplace and CAS firm channels. Automate 70-80% of weekly cash runway decisions with QBO integration.
- **Scope**: **Cash runway management only** - not accrual accounting, revenue recognition, or month-end close workflows. Focus: "How much cash do I have today?" not "What's my GAAP-compliant revenue?"
- **Target Market**: Service agencies using **cash accounting** who need weekly runway decisions, not CAS firms doing complex bookkeeping.
- **Tech Stack**: Python, FastAPI, SQLAlchemy (SQLite dev, Postgres prod), QBO API, SendGrid, Pydantic, Pytest, Redis (caching), Chart.js (analytics).
- **Definition of 'Smart' for Oodaloo**: Our features are designed to be 'smart' by reducing cognitive load and providing actionable insights at the moment of decision, not through complex AI or over-predictive models. We define 'smart' across three tiers:
  - **Connective Intelligence**: Linking AP, AR, and cash runway in real-time to show cross-domain decision impacts, unlike QBO's siloed approach.
  - **Workflow Intelligence**: Transforming a passive ledger into an active decision-making ritual with guided, prioritized actions (e.g., Prep Tray workflows).
  - **Light-Touch Predictive Intelligence**: Offering simple, actionable heuristics (e.g., 'This customer pays in 47 days on average') instead of complex forecasts that create noise.
- **Architectural Foundation (Already Established)**:
  - ✅ **SmartSyncService**: Unified integration coordinator implemented in `domains/integrations/smart_sync.py` (moved from core)
  - ✅ **Centralized QBO Auth**: Token management centralized in `domains/integrations/qbo/qbo_auth.py` (eliminates service duplication)
  - ✅ **Identity Graph**: Cross-platform deduplication in `domains/integrations/identity_graph/` (prevents double-counting)
  - ✅ **TenantAwareService**: Business-centric isolation pattern implemented in `domains/core/services/base_service.py`  
  - ✅ **Models = Data Only Policy**: Business logic in services, not models (enforced system-wide)
  - ✅ **Clean Import Pattern**: Cascading imports via `__init__.py` files (main.py → runway → domains)



## Phase 0: Foundation & Core Ritual (78h, Weeks 1-2) - ✅ FULLY COMPLETED

### **🚨 CRITICAL ARCHITECTURAL ENHANCEMENT COMPLETED**
- **[✅] QBO Infrastructure Redesign** *Effort: 8h* - **COMPLETED**
  * **[✅] QBOConnectionManager**: Production-grade connection management with automatic token refresh, circuit breakers, and health monitoring
  * **[✅] QBOHealthMonitor**: Real-time health monitoring across all clients with alerts and automated recovery
  * **[✅] QBO Health API Routes**: Client-facing status pages, admin dashboards, and Prometheus metrics
  * **[✅] SmartSyncService Integration**: Updated to use resilient connection infrastructure
  * **Impact**: Transformed QBO from "scripts" to mission-critical infrastructure with world-class resilience

- **[✅] QBO API Validation Plan Implementation** *Effort: 25h* - **FULLY COMPLETED**
- **[✅] Core Runway Services Architecture** *Effort: 8h* - **COMPLETED**
  - **[✅] Move runway calculation and data quality services to proper location** (`runway/core/services/`)
  - **[✅] Fix architectural placement** (ADR-001 compliance: domains/ for QBO APIs, runway/ for product logic)
  - **[✅] Centralize all business rule thresholds** (`config/business_rules.py`)
  - **[✅] Remove duplicated logic from proof-of-value service**
- **[✅] CRITICAL: Foundation Integration Testing** *Effort: 20h* - **PHASE 1 GATE**
  - **RISK**: We've built extensive mocked functionality but haven't validated it works with real QBO data
  - **IMPACT**: Phase 1 Smart AP could fail if foundation assumptions are wrong
  - **SOLUTION**: End-to-end integration tests with real QBO API calls (no mocks)
  - **GATE CRITERIA**: All integration tests pass before Phase 1 Smart AP development begins
  * **[✅] Comprehensive QBO Test Suite**: Business scenario testing with 5 real-world company types (Marketing Agency, Construction, Professional Services, E-commerce, Consulting). Located in `domains/integrations/qbo/tests/`. *Effort: 15h* - **COMPLETED**
  * **[✅] Production QBO Infrastructure**: All QBO capabilities consolidated under `domains/integrations/qbo/` with proper architectural separation. *Effort: 5h* - **COMPLETED**
  * **[✅] QBO Integration Documentation**: Complete testing documentation, architectural guides, and troubleshooting procedures. *Effort: 3h* - **COMPLETED**
  * **[✅] Business Rules Documentation**: All hardcoded QBO analysis values moved to `config/business_rules.py` for maintainability. *Effort: 2h* - **COMPLETED**
  * **Impact**: QBO integration now has enterprise-grade testing, monitoring, and operational procedures

### Outstanding Foundation Issues - **RESOLVED**
- **[✅] Missing Core Domain Services** *Effort: 8h* - **COMPLETED**
  - **[✅] Remove Task-related tests** - Task model removed, not needed for Oodaloo *Effort: 1h*
  - **[✅] Fix automation routes** - No longer blocking, integration tests working *Effort: 3h*
  - **[✅] Implement missing Bank services** - `BankTransactionService` implemented *Effort: 4h*
- **[✅] Legacy Test Pattern Cleanup** *Effort: 6h* - **COMPLETED**
  - **[✅] Fix `firm_id`/`client_id` in Bank tests** - No instances found in tests *Effort: 2h*  
  - **[✅] Fix missing QBO integration imports** - Integration working properly *Effort: 4h*

*All Phase 0 components are implemented and tested. Database, auth, core services, and mock integrations are working.*

### Stage 0.1: Architecture Hardening (30h)
- **[✅] Database Structure**: Consolidated `db/` package with `Base`, `SessionLocal`, `get_db`, `create_db_and_tables`, `seed_database`.
- **[✅] Core Models**: `Business`, `User`, `Balance`, `Transaction`, `Document` models with proper relationships.
- **[✅] Testing Foundation**: Phase 0 targeted testing strategy, behavior validation framework.
- **[✅] Mocked QBO Integration**: `QBOIntegrationService` with comprehensive mock data for rapid development.

### Stage 0.2: Core API Foundation (30h)
- **[✅] API Structure**: Complete FastAPI application with comprehensive route organization.
- **[✅] Runway Services Foundation**: `DigestService`, `TrayService`, `OnboardingService` implemented with mock providers.
- **[✅] QBO Integration Test Framework**: Comprehensive QBO sandbox test scenarios with realistic agency data complete.
- **[✅] Architectural and Data Model Enhancements**: ADRs for `domains/` vs. `runway/` separation, `RunwayReserve` model, and background job runner are complete and implemented.
- **[✅] Onboarding Proof Moment** *Effort: 10h* - **COMPLETED**
  * **[✅] Runway Replay**: On first QBO connect, generate a retroactive 4-week runway digest using historical AR/AP data. *Effort: 6h* - **COMPLETED**
  * **[✅] Initial Hygiene Score**: Immediately surface hygiene issues (e.g., unmatched deposits, missing due dates) during connect. *Effort: 4h* - **COMPLETED**


## Phase 1: Smart AP & Payment Orchestration (174h, Weeks 3-5) - 🔄 MOSTLY COMPLETED

*Core AP infrastructure completed, but key "smart" features still need implementation to justify premium pricing.*

### Stage 1.1: AP Domain Services (74h)
- **[✅] Enhanced AP Models**: `Bill`, `Payment`, and `Vendor` models enhanced with enterprise-grade complexity.
- **[✅] AP Services**: Fresh implementation of `BillService`, `PaymentService`, `VendorService`, `SmartSyncService`, and `DocumentReviewService` with mocking.
- **[✅] Missing AP Services & Test Fixes** *Effort: 8h* - **COMPLETED**
  - **[✅] Implement `StatementReconciliationService`** (`domains/ap/services/statement_reconciliation.py`) *Effort: 4h*  
  - **[✅] Fix legacy `firm_id`/`client_id` in AP tests** - Update to `business_id` pattern *Effort: 2h*
  - **[✅] Fix missing QBO integration imports** in AP tests (`domains.integrations.qbo`) *Effort: 2h*

### Stage 1.2: Runway Reserve System (30h)
- **[✅] Runway Reserve Logic**: `RunwayReserveService` implemented for earmarking funds, calculating balances, and auto-releasing reserves.
- **[ ] Configuration & Business Rules** *Effort: 4h* - **TECHNICAL DEBT**
  - **[ ] Move hardcoded payment priority thresholds** to config files (`domains/ap/services/bill_ingestion.py:144`)
  - **[ ] Move payment validation rules** to config (`domains/ap/services/payment.py:296`) 
  - **[ ] Move vendor risk assessment rules** to config (`domains/ap/services/vendor.py:74`)
  - **[ ] Move policy engine rules** to config (`domains/policy/services/policy_engine.py:213`)
- **[ ] Enhanced Payment Timing Optimization** *Effort: 11h* - **MISSING FROM CURRENT IMPLEMENTATION**
  - **Context**: To achieve 'smart' payment orchestration, enhance decision support with timing insights. These features are **not yet implemented** and are needed to justify Smart AP as a $99/mo add-on.
  - **[ ] Implement 'Latest Safe Pay Date' calculation in `BillService`**: For each bill, calculate the last possible payment date without incurring late fees or vendor relationship damage, based on terms and due dates. *Effort: 6h*
  - **[ ] Add 'Runway Impact Suggestions' to payment scheduling**: When scheduling payments, show impact on runway (e.g., 'Paying now costs 4 days of runway; delaying to Latest Safe Pay Date protects those days'). *Effort: 5h*

### Stage 1.21: Comprehensive QBO Sandbox Test Data Service (36h)

**Problem**: Multiple fragmented test data systems create inconsistent, incomplete test scenarios. Tests skip due to empty QBO sandbox, providers are scattered across codebase, and realistic business scenarios aren't properly represented in QBO format.

**Goal**: Create a unified, comprehensive QBO sandbox test data service that supports all test scenarios with realistic, industry-specific business data that works directly with QBO sandbox API.

#### **🔍 Current Test Data Audit** *Effort: 4h*
- **[ ] Inventory all existing test data sources** *Effort: 2h*
  - `runway/experiences/test_drive.py` (TestDriveService, TestDriveDemoDataService)
  - `runway/core/scenario_data.py` (BusinessScenarioProvider with 5 industry scenarios)
  - `domains/integrations/qbo/client.py` (_get_mock_response methods)
  - `domains/integrations/qbo/scenario_runner.py` (QBOScenarioTester)
  - `tests/conftest.py` (scattered fixture data)
  - Various provider mocks and demo data generators
- **[ ] Document test data gaps and inconsistencies** *Effort: 2h*
  - Identify which tests skip due to insufficient data
  - Map business logic requirements to data needs
  - Document QBO API response format requirements

#### **🏗️ Unified QBO Sandbox Data Architecture** *Effort: 12h*
- **[ ] Design centralized QBO test data service** *Effort: 4h*
  - **Location**: `domains/integrations/qbo/sandbox_data_service.py`
  - **Interface**: Consistent with existing `BusinessScenarioProvider` patterns
  - **Output**: Valid QBO API response format for all entity types
  - **Configurability**: Business size, industry, complexity levels
  
- **[ ] Enhanced business scenario data model** *Effort: 4h*
  - **Extend `BusinessScenario` dataclass** with QBO-specific fields:
    - `qbo_company_info`: Company metadata matching QBO CompanyInfo API
    - `qbo_chart_of_accounts`: Full chart of accounts with proper QBO structure
    - `qbo_tax_settings`: Tax rates, jurisdictions, compliance settings
    - `qbo_preferences`: QBO preferences that affect data structure
    - `data_quality_scenarios`: Intentional data quality issues for testing
  - **Add business complexity levels**:
    - `micro` (1-5 employees): 10-50 transactions/month
    - `small` (6-25 employees): 100-500 transactions/month  
    - `medium` (26-100 employees): 500-2000 transactions/month
  
- **[ ] QBO API response format compliance** *Effort: 4h*
  - **Bills**: Complete QBO Bill entity structure with all required fields
  - **Invoices**: Full Invoice entities with line items, taxes, payments
  - **Vendors/Customers**: Complete contact records with addresses, terms
  - **Accounts**: Chart of accounts with proper hierarchy and types
  - **Items**: Service/inventory items with pricing and tax settings
  - **Payments**: Payment records linking to bills/invoices

#### **🎯 Industry-Specific Scenario Enhancement** *Effort: 8h*
- **[ ] Marketing Agency (Enhanced)** *Effort: 2h*
  - **Seasonal cash flow**: Q4 surge, Q1 dip pattern
  - **High software costs**: 25+ SaaS subscriptions with varying terms
  - **Project-based billing**: Mix of retainer and milestone invoicing
  - **Data quality issues**: Duplicate vendors, missing due dates
  - **Cash position**: $75K operating + $25K payroll accounts
  
- **[ ] Construction Contractor (Enhanced)** *Effort: 2h*
  - **Equipment financing**: Large equipment purchases with payment plans
  - **Progress billing**: Percentage-of-completion invoicing
  - **Material costs**: Volatile material pricing and bulk purchases
  - **Subcontractor payments**: Complex 1099 tracking requirements
  - **Cash position**: $150K operating + $50K equipment reserve
  
- **[ ] Professional Services (Enhanced)** *Effort: 1h*
  - **Recurring revenue**: Monthly retainer stability
  - **Low inventory**: Service-based with minimal material costs
  - **Predictable expenses**: Office, software, professional development
  - **Cash position**: $45K operating, steady monthly flow
  
- **[ ] E-commerce Business (Enhanced)** *Effort: 2h*
  - **Inventory management**: Cost of goods sold, inventory valuation
  - **High transaction volume**: Hundreds of small transactions
  - **Payment processing**: Credit card fees, chargebacks, refunds
  - **Seasonal inventory**: Holiday buildup, post-season clearance
  - **Cash position**: $85K operating + $35K inventory financing
  
- **[ ] Consulting Firm (Enhanced)** *Effort: 1h*
  - **Project-based billing**: Time and materials tracking
  - **Travel expenses**: Complex expense reporting and reimbursement
  - **Contractor payments**: Mix of W2 and 1099 workforce
  - **Cash position**: $60K operating, project-dependent flow

#### **🔧 QBO Sandbox Data Population Service** *Effort: 8h*
- **[ ] Enhanced create_sandbox_data.py** *Effort: 4h*
  - **Scenario-based data creation**: Generate complete business scenarios in QBO
  - **Incremental data loading**: Add data without destroying existing records
  - **Data validation**: Ensure all created data passes QBO validation rules
  - **Rollback capability**: Clean slate functionality for test isolation
  - **Progress tracking**: Detailed logging of data creation process
  
- **[ ] QBO API batch operations** *Effort: 2h*
  - **Batch entity creation**: Use QBO batch API for efficient data loading
  - **Dependency management**: Handle entity relationships (vendor → bill)
  - **Error handling**: Graceful handling of QBO API limits and errors
  - **Rate limiting**: Respect QBO API rate limits during data creation
  
- **[ ] Test data validation and verification** *Effort: 2h*
  - **Data integrity checks**: Verify all relationships are properly created
  - **Financial balance validation**: Ensure accounting equation balances
  - **QBO sync verification**: Confirm data appears correctly in QBO UI
  - **Test scenario coverage**: Validate all test requirements are met

#### **🧪 Test Integration and Fixture Enhancement** *Effort: 4h*
- **[ ] Unified test fixture system** *Effort: 2h*
  - **Replace scattered fixtures** with centralized scenario-based fixtures
  - **QBO business fixture**: Real QBO business with populated data
  - **Scenario fixtures**: Per-industry fixtures with complete data sets
  - **Data isolation**: Ensure tests don't interfere with each other
  
- **[ ] Test skip elimination** *Effort: 2h*
  - **Fix `test_qbo_data_retrieval_works`**: Ensure sufficient data for validation
  - **Fix reserve allocation tests**: Provide cash positions for allocation testing
  - **Data-dependent test support**: All tests have required data available
  - **Graceful degradation**: Fallback scenarios when sandbox is unavailable

#### **🚀 Success Criteria & Validation**
- **Zero test skips** due to insufficient QBO sandbox data
- **All 5 industry scenarios** fully represented in QBO sandbox format
- **Complete QBO entity coverage**: Bills, Invoices, Vendors, Customers, Accounts, Items
- **Realistic data quality issues** for testing data quality analyzer
- **Performance**: Full scenario creation in <2 minutes
- **Reliability**: 95%+ success rate for sandbox data population
- **Maintainability**: Clear documentation and extension patterns

#### **📋 Deliverables**
1. **`QBOSandboxDataService`**: Centralized service for QBO test data management
2. **Enhanced scenario data**: 5 complete industry scenarios with QBO format
3. **Improved `create_sandbox_data.py`**: Robust, scenario-based data population
4. **Unified test fixtures**: Consistent, reliable test data across all tests
5. **Documentation**: Complete guide for extending and maintaining test scenarios
6. **Validation suite**: Automated verification of test data completeness

**Impact**: Eliminates test data fragmentation, enables comprehensive QBO integration testing, and provides foundation for reliable CI/CD pipeline with real QBO API validation.

### Stage 1.3: Smart AP UI/UX (36h)
- **[✅] AP API Endpoints**: `/runway/ap/` endpoints for bills, payments, and vendors are complete.
- **[✅] Enhanced Tray Integration**: 'Must Pay' vs. 'Can Delay' categorization and runway impact visualization are complete.
- **[ ] Smart AP UI/UX Design & Implementation** *Effort: 36h* - **CRITICAL FOR ICP ADOPTION**
  - **Context**: For design-savvy ICP (ad agencies, marketing firms), the UI must feel genuinely "smart" and brand-forward, not like a basic accounting tool.
  - **[ ] Design Token Foundation & Component Setup** *Effort: 10h*
    - Implement design tokens in `tailwind.config.js` (navy/coral palette, shadows, motion)
    - Set up shadcn/ui + Radix components with class-variance-authority
    - Create Storybook foundation for primitive validation
    - Implement accessibility tokens (focus-ring, reduced-motion support)
  - **[ ] RunwayCoverageBar (Linear Time Indicator)** *Effort: 8h*
    - **REPLACE** circular runway gauge with horizontal coverage bar
    - Show "Covered until **Oct 6** — **14 days**" with payroll risk badge
    - Implement linear time visualization with colored segments
    - Add List Mode parity for accessibility
  - **[ ] PaymentTimeline (Per-Item Control)** *Effort: 12h*
    - Design micro-timeline slider for single AP items showing due date → latest safe date
    - Implement constrained movement with real-time runway delta preview
    - Handle tooltip: "Oct 6 (latest safe) → **+3 days** runway"
    - Integrate with Flowband action pills and tray detail views
  - **[ ] Runway Impact Visualization** *Effort: 6h*
    - Ensure every action shows explicit "+X days" runway delta
    - Implement narrative-first copy: "Delay $5k Rent to Oct 6 → **+3d**"
    - Create celebratory states: "Payroll safe 🎉", "Smart move!"

## Phase 2: Smart AR & Collections (130h, Weeks 6-7) - [IN PROGRESS]

*Goal*: Implement AR prioritization and automated collections with mock email delivery. **Cash focus only** - no revenue recognition or accrual accounting complexity.

### Stage 2.1: AR Domain Services (40h) - ✅ COMPLETED
- **[✅] Enhanced AR Models**: `Invoice`, `Customer`, `ARPayment` models enhanced; business logic correctly moved to services.
- **[✅] AR Services**: `CollectionsService`, `PaymentMatchingService`, `CustomerService` implemented.
- **[✅] Missing AR Services & Test Fixes** *Effort: 10h* - **COMPLETED**
  - **[✅] Implement `AdjustmentService`** (`domains/ar/services/adjustment.py`) - Smart credit memo creation with runway impact *Completed*
  - **[✅] Implement `InvoiceService`** (`domains/ar/services/invoice.py`) - Invoice creation and management *Completed*
  - **[✅] Implement `PaymentApplicationService`** (`domains/ar/services/payment_application.py`) - Payment allocation *Completed*
  - **[✅] Fix legacy `firm_id`/`client_id` in AR tests** - No instances found in current tests *Completed*
- **[ ] Authentication & User Context** *Effort: 6h* - **TECHNICAL DEBT**
  - **[ ] Implement user context in API calls** (`runway/reserves/routes/reserves.py` - created_by, updated_by, allocated_by fields)
  - **[ ] Add user context to bill approvals** (`runway/ap/routes/bills.py` - approved_by_user_id)
  - **[ ] Fix all "TODO: Get from auth context" comments** (7 instances across routes)
- **[ ] Database Tracking & Analytics** *Effort: 8h* - **TECHNICAL DEBT**
  - **[ ] Implement collection activity tracking** (`domains/ar/services/collections.py` - Track reminders, contact attempts)
  - **[ ] Add customer payment history scoring** (Customer payment reliability)
  - **[ ] Implement contact attempt tracking** (Collection actions database)

### Stage 2.2: Smart Collections System (29h)
- **[ ] Smart Credit Memo Management** *Effort: 4h* - **CORE SMART AR FEATURE**
  - **[✅] AdjustmentService**: Smart credit memo creation with runway impact (`domains/ar/services/adjustment.py`) *Completed*
  - **[ ] Overpayment Detection**: Automatically suggest credit memos for overpayments *Effort: 2h*
  - **[ ] Collections Integration**: Stop reminders when partial payment + credit memo created *Effort: 2h*
- **[ ] Collections Automation**:
  - **Context**: The `PARKED_FUNCTIONALITY_AUDIT` revealed that collection routes exist in `_parked/domains/ar/routes/collections.py` but the `CollectionsService` was not fully implemented. The parked routes also use the old `firm_id` which needs to be updated to `business_id`.
  - **[ ] 3-stage email sequences (30d gentle, 45d urgent, 60d final)**. *Effort: 10h*.
    - **Synthesized Plan**:
      - Implement the 3-stage email logic within the existing `domains/ar/services/collections.py`.
      - Create email templates in a new `runway/digest/templates/collections/` directory.
      - Use the existing `EmailService` pattern from the digest feature for delivery.
      - Mocking strategy should log emails to the console and a `logs/mock_collections.json` file for testing.
  - **[ ] Priority scoring: amount, age, customer history**. *Effort: 8h*.
    - **Synthesized Plan**:
      - Enhance the priority scoring algorithm in the `CollectionsService`.
      - Leverage the `CustomerService.get_payment_reliability()` method which is already implemented and provides customer risk scores.
      - The algorithm should combine invoice age, amount (e.g., >$5k boost), and the customer's payment reliability score.
      - Integrate 'Customer Payment Profiles' with simple heuristics (e.g., avg_days_to_pay, preferred contact method if available) to personalize scoring.
  - **[ ] Auto-pause on payment detection**. *Effort: 7h*.
    - **Synthesized Plan**:
      - Implement logic to automatically pause collection sequences.
      - This should hook into the `PaymentMatchingService`, which already detects and applies payments.
      - Add a status field to a `CollectionSequence` model to track its state (e.g., active, paused, completed).
      - Use the `SmartSyncService` to poll for new payments from QBO before sending a scheduled reminder.

### **🚨 CRITICAL: Replace Mocked AR Collections Service** *Effort: 6h* - **P0 CRITICAL FIX**
- **Problem**: `runway/core/ar_collections_service.py` contains mocked reminder functionality that just changes invoice status to "review" without actually sending emails or managing collection sequences.
- **Impact**: Tray service invoice reminder functionality is non-functional and misleading to users.
- **Solution**: Implement proper collections functionality as part of Smart Collections add-on module.
- **Tasks**:
  - **[ ] Implement real email sending** in `ARCollectionsService.send_reminder()` *Effort: 3h*
    - Replace mock status change with actual email delivery via `EmailService`
    - Create collection email templates (gentle, urgent, final notice)
    - Add collection activity tracking to database
  - **[ ] Add collection sequence management** *Effort: 2h*
    - Track which stage of collection sequence each invoice is in
    - Implement auto-pause when payment is detected
    - Add collection history and customer communication tracking
  - **[ ] Update tray service integration** *Effort: 1h*
    - Ensure tray service properly handles real collections responses
    - Add proper error handling for failed email delivery
    - Update success/failure messaging to reflect actual functionality

### Stage 2.3: AR API & Integration (30h)
- **[✅] AR API Endpoints**: `/runway/ar/invoices/` and basic `/runway/ar/collections/` are complete.
- **[ ] `/runway/ar/collections/` - Manage reminder sequences**. *Effort: 5h*.
    - **Synthesized Plan**:
      - Un-park and refactor the routes from `_parked/domains/ar/routes/collections.py`.
      - Update routes to use `business_id` and the current `TenantAwareService` and auth middleware patterns.
      - Create API endpoints to allow users to start, stop, and view the status of collection sequences for a customer or invoice.
      - Implement 'Collection Playbook' UI in Prep Tray: Display prioritized actions (e.g., 'Chase Customer A with Urgent template now') based on payment profiles and runway impact.
- **[ ] `/runway/ar/payments/` - Payment matching and reconciliation**. *Effort: 5h*.
    - **Synthesized Plan**:
      - Create a new endpoint `POST /runway/ar/payments/match` for manual payment matching.
      - This endpoint will orchestrate the `PaymentMatchingService.match_payment_to_invoices()` method.
      - It should return match confidence scores to the UI and connect to the auto-pause collection logic.
- **[ ] Digest CC for Collaboration**
  * Add optional “CC Bookkeeper” field on business onboarding.
  * Weekly digest auto-sent to both owner + CC’d contact. *Effort: 4h*
  * No RBAC complexity — identical copy, role-agnostic.

- **[ ] Smart AR UI/UX Design & Implementation** *Effort: 43h* - **CRITICAL FOR ICP ADOPTION**
  - **Context**: Collections interfaces are typically ugly and intimidating. For creative agencies, this needs to feel strategic and professional, not aggressive.
  - **[ ] VarianceChip Integration** *Effort: 6h*
    - Implement variance tracking in AR context: "Expected AR: $25k, Actual: $19k → –3 days runway"
    - Add aggregation logic for multiple AR events: "–7 days today from 4 events"
    - Create one-click CTA routing to filtered collection tray
  - **[ ] CollectionPlaybookCard Component** *Effort: 10h*
    - Design card-based layout with customer payment profiles (reliable, slow, risky)
    - Implement action-oriented buttons: "Gentle Nudge", "Priority Follow-up", "Final Notice"
    - Show explicit runway impact: "Collecting this $8k invoice → **+5 days** runway"
    - Add ExplainHint components: "Usually pays after 2nd reminder"
  - **[ ] AgingBuckets Visualization** *Effort: 8h*
    - Design elegant aging buckets as actionable dashboard, not static report
    - Create runway impact indicators: "Collecting these 3 invoices funds next month's payroll"
    - Implement priority heat maps with clear runway deltas
  - **[ ] Payment Matching Intelligence** *Effort: 12h*
    - Design confidence-scored matching interface with visual similarity indicators
    - Create drag-and-drop payment allocation with real-time invoice updates
    - Implement smart suggestions: "This $5,000 payment likely matches Invoice #1234 (95% confidence)"
  - **[ ] Digest CC Field Implementation** *Effort: 4h*
    - Add optional bookkeeper email field in onboarding
    - Send identical digest to both owner + CC'd contact (no RBAC complexity)
    - Test collaboration lite approach for CAS distribution
  - **[ ] List Mode Parity** *Effort: 3h*
    - Ensure all AR visualizations have accessible list alternatives
    - Maintain identical actions between visual and list modes

## Phase 3: Smart Analytics & Insights (100h, Week 8)

*Goal*: Build actionable analytics foundation that enables informed budget planning and goal setting. Focus on insights from actual QBO data, not external benchmarks.*

### **🔍 DEDICATED DATA QUALITY & HYGIENE ENHANCEMENT SESSION** *Effort: 12h*

**Problem**: Current mock data and data quality thresholds are simplistic and don't reflect real-world business complexity across different business sizes and industries.

**Scope**: Comprehensive audit and enhancement of all data generation systems, quality scoring, and business scenario realism.

**Key Areas**:
- **🚨 CRITICAL: Eliminate All Mock Violations**: Replace all hardcoded mock values in KPI calculations with real data analysis (P0 Critical - violates "no more mocks" commitment)
- **Data Generator Consolidation**: Audit all mock data providers (`create_sandbox_data.py`, `scenario_runner.py`, `conftest.py` fixtures, QBO client mock data) and consolidate into unified, realistic data generation system
- **Business Size Awareness**: Enhance data generation to properly represent small (1-10 employees), medium (11-50 employees), and large (50+ employees) business scenarios with appropriate financial ratios and transaction volumes
- **Industry-Specific Patterns**: Create realistic data patterns for different industries (marketing agency, construction, professional services, e-commerce, consulting) with proper seasonal variations and cash flow characteristics
- **Data Quality Threshold Refinement**: Redesign scoring algorithms to be more nuanced and business-context aware, moving beyond simple percentage thresholds to multi-dimensional quality assessment
- **Real-World Validation**: Test data quality scoring against actual QBO sandbox data to ensure thresholds are realistic and actionable

**Deliverables**:
- Consolidated data generation architecture with clear separation of concerns
- Enhanced business scenario data that reflects real-world complexity
- Improved data quality scoring that provides meaningful insights
- Comprehensive test suite validating data quality across business sizes and industries

### Stage 3.1: Analytics Foundation (35h)
- **[ ] CRITICAL: Integration Tests** *Effort: 20h* - **BLOCKING PHASE 1 SMART AP**  
  - **[ ] Fix QBO sandbox integration test** (`tests/domains/unit/integrations/test_scenarios.py`) *Effort: 4h*
  - **[✅] Fix runway calculation in digest service** (AttributeError in integration test) *Effort: 4h*

### **🚨 P0 CRITICAL FIXES** *Effort: 8h* - **BLOCKING PRODUCTION**

**Problem**: Critical incomplete implementations that break core functionality and create security vulnerabilities.

**P0 Issues**:
- **Authentication Context Security Risk**: Hardcoded `"api_user"` in `runway/routes/bills.py` and `runway/routes/reserve_runway.py` instead of getting from auth context
- **Data Ingestion Service Broken**: `domains/core/services/data_ingestion.py` raises `NotImplementedError` 
- **Tray Experience Non-Functional**: `runway/experiences/tray.py` returns empty lists instead of real data

**Tasks**:
- **[ ] Fix Authentication Context** *Effort: 3h*
  - Replace hardcoded `"api_user"` with proper auth context retrieval
  - Update `runway/routes/bills.py` lines 172, 253
  - Update `runway/routes/reserve_runway.py` lines 66, 111, 164, 279
- **[ ] Fix Data Ingestion Service** *Effort: 2h*
  - Remove `NotImplementedError` from `domains/core/services/data_ingestion.py`
  - Implement basic QBO data ingestion using existing `QBOAPIProvider`
- **[ ] Fix Tray Data Provider** *Effort: 3h*
  - Implement real data retrieval in `runway/experiences/tray.py`
  - Connect to QBO data for bills, invoices, and runway items
  - Ensure tray experience shows actual business data

**Success Criteria**: All P0 issues resolved, no hardcoded auth, tray shows real data

### **🧪 REAL QBO API UNIT TESTS** *Effort: 6h* - **TESTING FOUNDATION**

**Problem**: Current tests rely heavily on mocks. Need real QBO API unit tests to validate actual integration behavior.

**Tasks**:
- **[ ] QBOAuthService Real API Tests** *Effort: 3h*
  - Test token refresh with real QBO sandbox
  - Test token expiration handling
  - Test OAuth flow with real authorization codes
  - Location: `tests/domains/unit/integrations/qbo/test_auth_real_api.py`
- **[ ] QBOAPIProvider Real API Tests** *Effort: 3h*
  - Test API calls with real QBO sandbox
  - Test rate limiting and retry logic
  - Test batch operations with real data
  - Test error handling with real API responses
  - Location: `tests/domains/unit/integrations/qbo/test_client_real_api.py`

**Success Criteria**: Real QBO API unit tests pass consistently, validate actual integration behavior

  - **[ ] Runway Reserve E2E Integration Test** (`tests/integration/test_runway_reserve_e2e.py`) *Effort: 8h* - **FOUNDATION VALIDATION**
    - Proves runway calculations work with real QBO data (not mocks)
    - Validates data quality issues actually affect business calculations  
    - Tests QBO connection reliability under load
    - **SUCCESS CRITERIA**: Foundation proven ready for Phase 1 Smart AP
  - **[ ] Smart AP E2E Integration Test** (`tests/integration/test_smart_ap_e2e.py`) *Effort: 8h* - **WORKFLOW VALIDATION**
    - Complete AP workflow: QBO bills → Processing → Payment Priority → Tray
    - Payment prioritization with real vendor data
    - Runway impact accuracy with AP decisions
    - **SUCCESS CRITERIA**: Smart AP features can be built with confidence
- **[ ] Core Analytics Services** *Effort: 33h* - **INCLUDES TECHNICAL DEBT**
  - **[ ] Replace Mock Data with QBO API** *Effort: 8h* - **TECHNICAL DEBT**
    - **[ ] QBO Cash flow data** (`runway/reserves/services/runway_reserve_service.py`) *Effort: 4h*
    - **[ ] Chart of Accounts sync** (`domains/core/services/coa_sync.py`) *Effort: 2h*
    - **[ ] QBO API integration** (`domains/core/providers/data_provider.py`) *Effort: 2h*
  - **[ ] `AnalyticsService`: Historical trends and patterns** *Effort: 10h*
    - AR/AP aging trends over time using actual business data
    - Cash flow patterns and seasonality detection
    - Vendor payment timing analysis and reliability scoring
  - **[ ] `ForecastingService`: Light-touch predictions** *Effort: 10h*
    - 2-4 week cash flow predictions using simple trend algorithms
    - Customer payment timing predictions based on history
    - Seasonal adjustment for cash flow forecasting
  - **[ ] `IndustryBenchmarkService`: Criterion-based benchmarking** *Effort: 5h*
    - **Data Integration**: Connect to RMA Annual Statement Studies API/data feeds
    - **NAICS Classification**: Auto-classify businesses using NAICS codes (541810, 541613, 541511, 541512)
    - **Key Ratios**: Current ratio, AR turnover, debt-to-worth, sales/working capital
    - **Size Segmentation**: $1-5M revenue brackets for accurate peer comparison
    - **Data Sources**: RMA, Sageworks, AICPA industry reports (licensed data feeds)
    - **Update Frequency**: Quarterly benchmark data refresh to maintain accuracy

### Stage 3.2: Analytics UI/UX (50h)
* Stage 3.21 [ ] Marketplace / Distribution Hooks**
  - [ ] **Payroll Confidence Badge**: Add a yes/no (or % confidence) “Next Payroll Ready?” indicator derived directly from runway days. Visible in app card and digest. *Effort: 6h*
  - [ ] **Runway Checkup Email**: Auto-trigger a single “trial proof” digest email on install (shows runway + hygiene from last 4 weeks). *Effort: 6h*

- **[ ] Smart Analytics Interface Design** *Effort: 65h* - **CRITICAL FOR ICP ADOPTION**
  - **Context**: Analytics dashboards are typically overwhelming with charts and numbers. For creative agencies, this needs to feel like strategic insights, not data dumps.
  - **[ ] Runway Flowband Implementation** *Effort: 15h*
    - Build signature visualization as centerpiece of Cash Console
    - Implement Chart.js streamplot with coral/green/red segments for AR/AP events
    - Add payroll markers with risk states and variance chip integration
    - Create drag-and-drop AP/AR events for "What If" scenarios
    - Ensure sparse display (top-N events, 8-12 max) with List Mode parity
  - **[ ] Executive Dashboard Design** *Effort: 20h*
    - Design story-driven dashboard answering "Where am I?", "What changed?", "What do I do now?"
    - Replace all circular gauges with RunwayCoverageBar linear indicators
    - Implement narrative-first microcopy throughout interface
    - Create actionable insight cards with explicit runway deltas
  - **[ ] Industry Criterion Benchmarking** *Effort: 15h*
    - **REALISTIC SCOPE**: Use established CPA industry benchmark sources (RMA, Sageworks, AICPA)
    - Integrate industry financial ratios for service agencies (NAICS 541810, 541613, 541511, 541512)
    - "Your AR turnover: 8.2x vs. Industry median: 6.5x for agencies $1-5M"  
    - "Your current ratio: 1.8 vs. Industry range: 1.2-2.1 for marketing services"
    - Include historical self-comparison: "Your improvement vs. your 6-month average"
    - **Data Sources**: RMA Annual Statement Studies, Sageworks Industry Data, AICPA benchmarks
  - **[ ] Lightweight "What If" Mode** *Effort: 15h*
    - Implement single overlay scenario planning (base vs one scenario only)
    - Create 2-3 controls max: delay bill, shift AR, toggle reserve
    - Show immediate delta feedback: "+3 days if rent delayed to Oct 6"
    - Extend ForecastingService for scenario objects (no multi-scenario sandboxing)

## Phase 4: Smart Budget Planning & Goals (106h, Week 9)

*Goal*: Build budget planning tools that leverage analytics insights to set realistic goals and create "what-if" scenarios for runway optimization.*
- **[ ] Variance Alerts Aggregation** *Effort: 4h*
    - Implement event-driven drift alerts that aggregate multiple transactions into one notification
    - Example: "Runway shortened by **7 days today** from 3 bills + 1 missed AR"
    - Prevents alert spam while maintaining "whenever it matters" intent


### Stage 4.1: Budget Planning Foundation (40h)
- **[ ] Budget Models & Services** *Effort: 25h*
  - **[ ] Budget Planning Service** *Effort: 15h*
    - Create budget categories based on actual spending patterns from analytics
    - Implement goal-setting workflows that reference historical performance
    - Build "what-if" scenario modeling for different budget allocations
  - **[ ] Goal Setting Engine** *Effort: 10h*
    - Create realistic goal suggestions based on analytics insights AND industry benchmarks
    - "Industry median AR turnover is 6.5x - your current 4.2x suggests 30% improvement opportunity"
    - "Your current ratio of 1.8 is healthy (industry range 1.2-2.1) - maintain this level"
    - Implement runway impact modeling for different budget scenarios
    - Build progress tracking against both self-set goals and industry standards

- **[ ] Budget Intelligence Logic** *Effort: 15h*
  - **[ ] Decision-Time Guardrails** *Effort: 8h*
    - Implement real-time budget checking during payment approvals
    - Create intelligent warnings based on runway impact and goals
    - Build override workflows that maintain goal tracking
  - **[ ] Vacation Mode Planning** *Effort: 7h*
    - Create essential vs. discretionary categorization based on historical data
    - Implement pre-approval workflows for vacation periods
    - Build return-from-vacation summary and review processes

### Stage 4.2: Budget Planning UI/UX (50h)
- **[ ] Smart Budget Interface Design** *Effort: 50h* - **CRITICAL FOR ICP ADOPTION**
  - **Context**: Budget tools are typically boring spreadsheet-like interfaces. For creative agencies, this needs to feel like a strategic planning tool, not accounting drudgery.
  - **[ ] PrepTrayList (Game Board Layout)** *Effort: 12h*
    - Implement three-lane design: Must Pay / Can Delay / Chasing
    - Each card shows runway delta preview with ExplainHint context
    - Use primary action verbs: Delay, Nudge, Approve (never generic "Update")
    - Ensure every move previews explicit runway impact
  - **[ ] Goal Setting Interface** *Effort: 20h*
    - Design goal-setting wizard that uses analytics insights as starting points
    - Create visual budget builders with drag-and-drop category allocation
    - Implement "what-if" scenario planning with real-time runway impact
    - Replace circular progress indicators with linear coverage bars
  - **[ ] Decision-Time Guardrails Interface** *Effort: 15h*
    - Design elegant warning modals that appear during payment approval
    - Create "traffic light" system for budget status with clear explanations
    - Implement smart suggestions based on goals and runway impact
    - Show explicit runway protection messaging
  - **[ ] Vacation Mode Planning Interface** *Effort: 3h*
    - Design vacation planning wizard that feels like a travel app
    - Create visual calendar showing pre-approved essentials vs. queued discretionary items
    - Implement "peace of mind" dashboard showing what's handled automatically

## Phase 5: Smart Automation Engine (75h, Week 10)

*Goal*: Build automation that executes proven budget plans and runway optimization strategies. Only automate what's been validated through analytics and budget planning.*

### Stage 5.1: Automation Foundation (35h)
- **[ ] Rule Engine Development** *Effort: 25h*
  - **[ ] Budget-Based Automation Rules** *Effort: 15h*
    - Create automation rules based on validated budget plans
    - Implement confidence scoring for automated decisions
    - Build dry-run mode for testing automation before activation
  - **[ ] Runway Protection Automation** *Effort: 10h*
    - Automate payment timing optimization based on runway goals
    - Create automatic vendor prioritization based on criticality scores
    - Implement cash flow protection rules

- **[ ] Automation Execution Engine** *Effort: 10h*
  - Build safe execution environment with rollback capabilities
  - Create audit trails for all automated actions
  - Implement user notification and override systems

### Stage 5.2: Automation UI/UX (40h)
- **[ ] Automation Interface Design** *Effort: 40h*
  - **[ ] Rule Builder Interface** *Effort: 20h*
    - Design intuitive rule creation based on budget goals and analytics insights
    - Create visual rule testing with historical data simulation
    - Implement confidence indicators for rule effectiveness
  - **[ ] Automation Dashboard** *Effort: 20h*
    - Design automation status and performance monitoring
    - Create easy enable/disable controls with clear impact explanations
    - Implement automation audit log with clear action histories

## Phase 6: Production & Deployment (80h, Week 11-12)

*Goal*: Transform development MVP into production-ready application with real integrations, scalable infrastructure, and deployment pipeline.

### Stage 6.1: Production Database & Infrastructure (30h)
- **[ ] Confirm Audit Logging Coverage**:
  - [ ] Confirm we have the audit logging strategy we want. *Effort: 4h*.
  - [ ] Review all state mutating service methods to confirm they have correct audit logging. *Effort: 4h*.
- **[ ] Rotate all the keys **:
  - [ ] LLM has seen .env file so we need to get new secrets and figure out how to not let gen ai coders see it
  - [ ] get all refresh tokens to be stored in DB rather than local files now that we're moving to production persistent db access.
- **[ ] Database Migration**:
  - [ ] PostgreSQL setup and configuration. *Effort: 4h*.
  - [ ] Alembic migration system implementation. *Effort: 6h*.
  - [ ] Database connection pooling and optimization. *Effort: 4h*.
  - [ ] Backup and recovery strategy. *Effort: 3h*.
- **[ ] Infrastructure as Code**:
  - [ ] Docker containerization (Dockerfile + docker-compose). *Effort: 6h*.
  - [ ] Environment configuration management. *Effort: 4h*.
  - [ ] Health checks and monitoring setup. *Effort: 3h*.

### Stage 6.2: Real External Integrations (47h)
- **[ ] QBO Integration Validation** (Critical Product Validation):
  - [ ] Validate QBO API can support "single approval → multiple actions" workflow (bill approval + payment scheduling + AR reminders). *Effort: 6h*.
  - [ ] Test QBO webhook reliability and real-time sync accuracy for runway calculations. *Effort: 4h*.
  - [ ] Verify vendor normalization needs and data quality issues in real QBO data. *Effort: 4h*.
  - [ ] Load test QBO API rate limits and error handling under production volumes. *Effort: 4h*.
- **[ ] QBO Production Integration**:
  - [ ] Replace mocked QBOIntegrationService with real QBO API calls. *Effort: 8h*.
  - [ ] QBO OAuth flow implementation and token management. *Effort: 6h*.
  - [ ] Rate limiting, error handling, and retry logic. *Effort: 4h*.
  - [ ] QBO webhook handling for real-time updates. *Effort: 3h*.
- **[ ] Email Production Setup**:
  - [ ] SendGrid production account and domain verification. *Effort: 2h*.
  - [ ] AWS SES setup as fallback provider. *Effort: 2h*.

### Stage 6.3: CI/CD & Deployment Pipeline (25h)
- **[ ] CI/CD Implementation**:
  - [ ] GitHub Actions workflow for testing and deployment. *Effort: 8h*.
  - [ ] Automated testing pipeline with coverage reporting. *Effort: 6h*.
  - [ ] Security scanning and dependency updates. *Effort: 4h*.
- **[ ] Cloud Deployment**:
  - [ ] AWS/GCP/Azure deployment configuration. *Effort: 4h*.
  - [ ] Load balancer and SSL certificate setup. *Effort: 3h*.

### Stage 6.4: Production Monitoring & Security (20h)
- **[ ] Monitoring & Observability**:
  - [ ] Application Performance Monitoring (APM) integration. *Effort: 4h*.
  - [ ] Centralized logging with structured logs. *Effort: 4h*.
  - [ ] Error tracking and alerting system. *Effort: 4h*.
- **[ ] Security Hardening**:
  - [ ] Security headers and HTTPS enforcement. *Effort: 3h*.
  - [ ] API rate limiting and DDoS protection. *Effort: 3h*.
  - [ ] Secrets management and environment security. *Effort: 2h*.

### Stage 6.5: Performance & Scalability (10h)
- **[ ] Performance Optimization**:
  - [ ] Database query optimization and indexing. *Effort: 4h*.
  - [ ] API response caching with Redis. *Effort: 3h*.
  - [ ] Background job processing for digest sending. *Effort: 3h*.

### Stage 6.6: Productionalization Tasks (Lower Priority)
- **[ ] Monitoring & Observability Enhancement** *Effort: 8h* - **OPERATIONAL CONCERN**
  - [ ] Enhanced application performance monitoring (APM) integration
  - [ ] Centralized logging with structured logs and log aggregation
  - [ ] Error tracking and alerting system with escalation procedures
  - [ ] Health check endpoints for load balancer integration
  - [ ] Metrics dashboard for operational monitoring
- **[ ] Infrastructure Utilities & Tooling** *Effort: 6h* - **NICE TO HAVE**
  - [ ] Database migration utilities and rollback procedures
  - [ ] Backup and restore automation scripts
  - [ ] Environment configuration management tools
  - [ ] Development environment setup automation
  - [ ] Code quality and security scanning automation

**Success Criteria**: 
- Application runs in production with 99.9% uptime
- Real QBO data flows correctly with <2s API response times
- Email delivery rate >95% with proper tracking
- Automated deployments work reliably
- Comprehensive monitoring and alerting in place

## Phase 7+: RowCol Roadmap & Parked Functionality

*Goal*: Transform Oodaloo into a multi-tenant RowCol platform for CAS firms. This functionality is **out of scope** for the Runway MVP.

### **Phase 8: RowCol Compliance & Policy Engine**
- **Parked Functionality**: `_parked/domains/policy/` contains advanced rules for bookkeeping transaction compliance. This is a prerequisite for the "Close" product.

### **Phase 10: RowCol Close & Advanced Accounting**
- **Parked Functionality**:
  - **Revenue Recognition Engine**: 184-line GAAP-compliant implementation from `_parked/domains/ar/services/revenue_recognition.py`. This is for accrual accounting, not cash runway.
  - **PreClose System**: Complete month-end close workflows from `_parked/features/close/`.
  - **KPI Routes**: Existing routes in `_parked/domains/core/routes/kpi.py` that connect to active `KPIService` - unpark for Phase 3 Analytics.
  - **AR Collections Routes**: Partial implementation in `_parked/domains/ar/routes/collections.py` - integrate with Phase 2 Smart AR.
  
### **Phase 11: Multi-Tenant Architecture**
- **Parked Functionality**: Obsolete `Firm/Staff/Client/Engagement` models from `_parked/deprecated/`. These concepts will be re-introduced for RowCol's multi-tenant architecture.

### **Phase 12: Advanced CAS Features**
- **Parked Functionality**: `_parked/domains/ap/services/shared_expense_allocation.py` contains complex job costing logic for specialized contractors.
r each - **Task Management System**: The `Task` model and related services from `_parked/domains/core/models/task.py` are designed for the multi-tenant RowCol platform to manage staff assignments for client engagements. This will be re-introduced in the RowCol Close product.

---
*The remaining sections (Testing Strategy, API Documentation, etc.) from v4.3 are preserved below without changes.*

## Testing Strategy (Comprehensive - Updated for v4.5)

### Phase 0: Foundation Tests
```python
# tests/test_phase0_foundation.py
- test_database_creation_and_seeding()
- test_business_user_models_creation()  
- test_qbo_integration_service_init()
- test_basic_api_endpoints_respond()
- test_digest_service_runway_calculation()
- test_tray_service_item_management()
```

### Phase 1: Smart AP & Payment Orchestration Tests
```python
# tests/test_phase1_smart_ap.py
- test_bill_approval_workflow_end_to_end()
- test_payment_execution_qbo_sync()
- test_runway_reserve_calculation_accuracy()
- test_vendor_normalization_matching()
- test_payment_orchestration_error_handling()

# NEW: Enhanced Smart AP Features
- test_latest_safe_pay_date_calculation()
- test_runway_impact_suggestions_accuracy()
- test_payment_timing_optimization()
- test_payment_priority_intelligence_scoring()
- test_smart_ap_ui_components_render()
- test_payment_timing_interface_interactions()
```

### Phase 2: Smart AR & Collections Tests
```python
# tests/test_phase2_smart_ar.py
- test_collections_email_sequence_delivery()
- test_ar_priority_scoring_algorithm()
- test_payment_matching_accuracy()
- test_collections_pause_on_payment()

# NEW: Enhanced Smart AR Features
- test_customer_payment_profile_creation()
- test_collection_playbook_prioritization()
- test_payment_matching_confidence_scoring()
- test_ar_aging_visualization_data()
- test_smart_ar_ui_components_render()
- test_collection_playbook_interface_workflows()
```

### Phase 3: Smart Analytics & Insights Tests
```python
# tests/test_phase3_analytics.py
- test_runway_forecasting_accuracy()
- test_analytics_dashboard_performance()
- test_chart_data_generation_speed()

# NEW: Industry Benchmarking & Analytics Features
- test_industry_benchmark_service_integration()
- test_naics_classification_accuracy()
- test_rma_data_feed_connection()
- test_financial_ratio_calculations()
- test_benchmark_comparison_accuracy()
- test_historical_trend_analysis()
- test_forecasting_confidence_bands()
- test_executive_dashboard_narrative_generation()
- test_criterion_benchmarking_ui_display()
```

### Phase 4: Smart Budget Planning & Goals Tests
```python
# tests/test_phase4_budget_planning.py
# NEW: Budget Planning & Goal Setting
- test_budget_category_creation_from_analytics()
- test_goal_setting_engine_suggestions()
- test_industry_benchmark_goal_recommendations()
- test_what_if_scenario_modeling()
- test_runway_impact_budget_calculations()
- test_decision_time_guardrails_logic()
- test_vacation_mode_bill_categorization()
- test_budget_planning_ui_workflows()
- test_goal_progress_tracking_accuracy()
- test_budget_variance_visualization()
```

### Phase 5: Smart Automation Engine Tests
```python
# tests/test_phase5_automation.py
# NEW: Automation & Rule Engine
- test_budget_based_automation_rules()
- test_rule_confidence_scoring()
- test_automation_dry_run_mode()
- test_runway_protection_automation()
- test_vendor_prioritization_automation()
- test_rule_execution_safety_checks()
- test_automation_rollback_capabilities()
- test_audit_trail_generation()
- test_rule_builder_interface_logic()
- test_automation_performance_monitoring()
```

### Phase 6: Production & Integration Tests
```python
# tests/test_phase6_production.py
- test_qbo_production_api_integration()
- test_real_time_webhook_processing()
- test_email_delivery_production_flow()
- test_database_migration_scripts()
- test_security_authentication_flow()
- test_rate_limiting_enforcement()
- test_error_handling_production_scenarios()
- test_monitoring_alert_triggers()
- test_backup_recovery_procedures()
```

### Behavior Validation Framework for "Smart" Features

#### Smart Feature Testing Approach
```python
# Enhanced testing for "smart" features that reduce cognitive load
class SmartFeatureTestMixin:
    def assert_reduces_cognitive_load(self, feature_output):
        """Test that smart features provide clear, actionable insights"""
        assert feature_output.has_clear_recommendation()
        assert feature_output.shows_impact_of_action()
        assert feature_output.provides_context()
        assert not feature_output.requires_mental_calculation()
    
    def assert_connective_intelligence(self, ap_action, ar_impact, runway_change):
        """Test cross-domain impact visibility"""
        assert ap_action.shows_ar_impact == ar_impact
        assert ap_action.shows_runway_change == runway_change
        assert ap_action.connects_domains()
    
    def assert_workflow_intelligence(self, workflow_step):
        """Test guided decision-making"""
        assert workflow_step.has_prioritized_actions()
        assert workflow_step.shows_next_steps()
        assert workflow_step.provides_context()
        assert workflow_step.feels_advisory_not_mechanical()
    
    def assert_light_touch_predictive(self, prediction):
        """Test predictions are simple and actionable"""
        assert prediction.is_understandable_without_explanation()
        assert prediction.includes_confidence_level()
        assert prediction.avoids_complex_forecasting()
```

#### Industry Benchmark Testing
```python
# Benchmark data validation for criterion-based comparisons
class BenchmarkTestSuite:
    def test_rma_data_integration(self):
        """Validate RMA Annual Statement Studies integration"""
        benchmark_service = IndustryBenchmarkService()
        ratios = benchmark_service.get_ratios_for_naics("541810", "$1-5M")
        assert ratios.current_ratio is not None
        assert ratios.ar_turnover is not None
        assert ratios.data_source == "RMA"
        assert ratios.last_updated_within_days(90)  # Quarterly updates
    
    def test_benchmark_accuracy_vs_mock_data(self):
        """Ensure benchmark comparisons are mathematically correct"""
        business_ratio = 8.2
        industry_median = 6.5
        comparison = benchmark_service.compare(business_ratio, industry_median)
        assert comparison.performance == "Above Average"
        assert comparison.improvement_opportunity == "26% better than median"
        assert comparison.provides_context()
    
    def test_naics_classification_accuracy(self):
        """Test automatic NAICS code assignment"""
        business_description = "Digital marketing agency specializing in social media"
        naics_code = benchmark_service.classify_business(business_description)
        assert naics_code in ["541810", "541613"]  # Advertising or Marketing Consulting
```

#### UI/UX Testing for Design-Savvy ICP
```python
# Design-focused ICP testing (agencies, marketing firms)
class ICPUITestSuite:
    def test_brand_forward_design_quality(self):
        """Test that UI meets design agency expectations"""
        dashboard = render_executive_dashboard()
        assert dashboard.has_visual_hierarchy()
        assert dashboard.uses_strategic_language()
        assert dashboard.avoids_accounting_jargon()
        assert dashboard.feels_professional_not_utilitarian()
    
    def test_smart_feels_intelligent(self):
        """Test that smart features feel genuinely smart"""
        payment_decision = render_payment_timing_interface()
        assert payment_decision.shows_clear_impact()
        assert payment_decision.provides_smart_suggestions()
        assert payment_decision.feels_advisory_not_mechanical()
        assert payment_decision.uses_smooth_animations()
    
    def test_analytics_narrative_quality(self):
        """Test story-driven dashboard approach"""
        narrative = generate_runway_story()
        assert narrative.reads_like_advisor_insights()
        assert narrative.prioritizes_actions()
        assert narrative.connects_data_to_decisions()
```

### Success Criteria by Phase

#### Phase 1: Smart AP Success Metrics
- 95%+ accuracy in Latest Safe Pay Date calculations
- Payment timing suggestions show measurable runway impact
- UI components load in <2 seconds with smooth animations
- 80%+ user satisfaction with payment intelligence features in beta testing

#### Phase 2: Smart AR Success Metrics  
- Collection playbook increases engagement by 50%+ over generic reminders
- Payment matching achieves 90%+ accuracy with confidence scoring
- Customer payment profiles predict timing within ±5 days
- AR aging visualization provides actionable runway insights

#### Phase 3: Analytics Success Metrics
- Industry benchmark integration connects to RMA/Sageworks successfully
- Financial ratio calculations match CPA-standard formulas within 0.1%
- Executive dashboard loads in <3 seconds with narrative generation
- Forecasting accuracy 90%+ over 2-week windows
- Benchmark comparisons feel credible to CPA-trained users

#### Phase 4: Budget Planning Success Metrics
- Goal suggestions based on benchmarks achieve 85%+ user acceptance
- What-if scenarios accurately model runway impact within 5%
- Decision-time guardrails prevent 70%+ overspend incidents
- Vacation mode pre-approves essentials with 95%+ accuracy
- Budget interface feels strategic, not restrictive

#### Phase 5: Automation Success Metrics
- Automation rules execute successfully 95%+ of time
- Dry-run mode prevents 100% of unintended actions
- Rule confidence scoring correlates with actual performance >80%
- Automation audit trails provide complete action history
- Users trust automation enough to enable it

#### Phase 6: Production Success Metrics
- Application runs with 99.9% uptime
- Real QBO integration processes data with <2s response times
- Email delivery rate >95% with proper tracking
- Security scanning shows zero critical vulnerabilities

### Mock Data Strategy for Smart Features

#### Industry Benchmark Mock Data
```python
# Realistic industry benchmark mock data based on RMA structure
MOCK_INDUSTRY_BENCHMARKS = {
    "541810": {  # Advertising Agencies
        "current_ratio": {"median": 1.4, "q1": 1.1, "q3": 2.0},
        "ar_turnover": {"median": 6.5, "q1": 4.2, "q3": 8.8},
        "debt_to_worth": {"median": 0.8, "q1": 0.3, "q3": 1.5},
        "sales_working_capital": {"median": 12.5, "q1": 8.2, "q3": 18.7}
    },
    "541613": {  # Marketing Consulting
        "current_ratio": {"median": 1.6, "q1": 1.2, "q3": 2.1},
        "ar_turnover": {"median": 7.2, "q1": 5.1, "q3": 9.4}
    }
}
```

#### Budget Planning Mock Scenarios
```python
# Goal setting scenarios based on industry benchmarks
MOCK_BUDGET_SCENARIOS = {
    "conservative": {
        "ar_improvement_target": 10,  # 10% improvement
        "expense_reduction_target": 5,
        "runway_buffer_days": 45
    },
    "aggressive": {
        "ar_improvement_target": 25,  # Reach industry median
        "expense_reduction_target": 15,
        "runway_buffer_days": 30
    },
    "industry_standard": {
        "ar_improvement_target": 15,  # Gradual improvement
        "expense_reduction_target": 8,
        "runway_buffer_days": 60
    }
}
```

#### Smart Feature Mock Responses
```python
# Mock responses that demonstrate "smart" behavior
MOCK_SMART_RESPONSES = {
    "payment_timing": {
        "recommendation": "Delay this $5,000 payment by 8 days to protect 3 days of runway",
        "confidence": 0.92,
        "reasoning": "Based on vendor payment history and current cash flow"
    },
    "collection_playbook": {
        "priority_action": "Send 'Priority Follow-up' to Customer A",
        "reasoning": "Usually pays after 2nd reminder, $8,000 invoice would fund payroll",
        "confidence": 0.87
    }
}
```

This comprehensive testing strategy ensures that our "smart" features actually deliver on their promise of reducing cognitive load and providing actionable insights at the moment of decision, while meeting the high design and usability standards expected by our creative agency ICP.

## API Documentation (OpenAPI/Swagger)

### Authentication
```yaml
/runway/auth/login:
  post:
    summary: User login
    requestBody:
      schema:
        type: object
        properties:
          email: string
          password: string
    responses:
      200:
        schema:
          type: object
          properties:
            access_token: string
            user: UserSchema
```

### Core Business Operations
```yaml
/runway/businesses/{business_id}/digest:
  get:
    summary: Generate weekly runway digest
    responses:
      200:
        schema:
          type: object
          properties:
            runway_days: number
            cash_balance: number
            ar_overdue: number
            ap_due_soon: number
            tray_items: array

/runway/businesses/{business_id}/tray:
  get:
    summary: Get prep tray items
    responses:
      200:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/TrayItem'
  
  post:
    summary: Take action on tray item
    requestBody:
      schema:
        type: object
        properties:
          action: string  # confirm, delay, split
          tray_item_id: integer
          metadata: object
```

### AP Operations
```yaml
/domains/ap/bills:
  get:
    summary: List bills with filtering
    parameters:
      - name: status
        schema:
          type: string
          enum: [pending, approved, scheduled, paid]
      - name: due_within_days
        schema:
          type: integer
    responses:
      200:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/Bill'

  patch:
    summary: Approve or schedule bill payment
    requestBody:
      schema:
        type: object
        properties:
          bill_ids: array
          action: string  # approve, schedule, delay
          payment_date: string
          runway_reserve: boolean
```

### AR Operations
```yaml
/domains/ar/invoices:
  get:
    summary: List invoices with aging
    parameters:
      - name: aging_bucket
        schema:
          type: string
          enum: [current, 30d, 60d, 90d]
      - name: priority
        schema:
          type: string
          enum: [high, medium, low]
    responses:
      200:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/Invoice'

/domains/ar/collections:
  post:
    summary: Trigger collection sequence
    requestBody:
      schema:
        type: object
        properties:
          invoice_ids: array
          sequence_type: string  # gentle, urgent, final
          custom_message: string
```

## Parked Files Strategy

### High-Value References (Review & Extract Logic)
- **`_parked/domains/ap/services/statement_reconciliation.py`**: Payment matching algorithms
- **`_parked/domains/ar/services/collections.py`**: Collection sequence logic
- **`_parked/domains/policy/services/`**: Rule engine patterns
- **`_parked/domains/vendor_normalization/`**: Already successfully integrated

### Implementation Approach
1. **Review Phase** (5-10h per domain): Extract business logic, algorithms, data patterns
2. **Fresh Implementation** (20-30h per domain): Build using current Business model and db/ structure  
3. **Integration Testing** (10-15h per domain): Validate with Phase 0 testing foundation
4. **Total per domain**: 35-55h (vs. 60-80h debugging old relationships)

### Files to Skip Entirely
- **`_parked/core/models/`**: Obsolete Client/Firm architecture

## Critical Architectural Decisions Needed

### Audit Logging Strategy (Phase 3-4)
**Current State**: Partial audit_log.py and _decorators.py exist but need design decisions

**Key Questions**:
- **Entity Types**: Currently designed for Firm/User/Asset RBAC. Oodaloo needs Business/User/Transaction entities
- **Cause ID**: Correlation system for cascading service calls (e.g., "payment_batch_123" traces through multiple services)
- **RBAC Integration**: Do we need role-based permissions or simple business-owner-only access?
- **Audit Scope**: Financial transactions only vs. all business operations

**Proposed Approach**:
```yaml
Phase 3: Basic Financial Audit Logging
  - Transaction-level audit trails (payments, bills, adjustments)
  - Simple cause_id correlation for payment batches
  - Business-owner-only access (no RBAC complexity)
  
Phase 4+: Enhanced Audit System  
  - User role permissions (if multi-user needed)
  - Advanced correlation patterns
  - Compliance reporting features
```

**Effort**: 15-20h design + implementation

### API Versioning Strategy
**Current State**: Mixed `/api/v1/` and `/api/` prefixes

**Decision Needed**: Standardize on consistent versioning approach
- Option A: `/api/v1/` for all routes (future-proof)
- Option B: `/api/` for simplicity (current mixed state)

**Recommendation**: Standardize on `/api/v1/` (5h effort)

### API Exposure Strategy
**Current State**: `domains/` routes were previously exposed in `main.py`

**Decision Made**: Only `runway/` routes should be exposed to the frontend
- **[✅] Removed `domains/` routes from public API** in `main.py` to ensure only `runway/` endpoints are accessible.
- **[✅] Evaluated necessity of `domains/` routes**: Determined that `domains/` can be a pure service layer without HTTP endpoints, with all interactions orchestrated through `runway/`.

**Effort**: Completed

## UI/UX Playbook Integration

### Design System Implementation
All UI development must follow the consolidated **UI/UX Playbook** (`ui/PLAYBOOK.md`):

#### Core Design Principles
Every UI element must answer three questions in order:
1. **Where am I?** (state) → concise, linear time indicator
2. **What changed?** (delta) → variance vs plan/last week  
3. **What do I do now?** (one primary action) → explicit runway delta from the action

#### Component Standards
- **RunwayCoverageBar**: REPLACES all circular runway gauges with linear time visualization
- **Runway Flowband**: Signature visualization (sparse, top-N events, List Mode parity)
- **VarianceChip**: Aggregated variance tracking with one-click CTA routing
- **PaymentTimeline**: Per-item control with constrained slider and runway delta preview
- **PrepTrayList**: Game board layout (Must Pay / Can Delay / Chasing)
- **All components**: Must show explicit "+X days" runway delta for actions

#### Development Guardrails
- **Design Tokens**: Use only defined tokens (--brand, --bg, --fg, etc.) - ban raw hexes
- **Copy Standards**: Narrative-first ("Do X → +Y days"), celebratory states ("Payroll safe 🎉")
- **Accessibility**: WCAG AA compliance, List Mode parity, keyboard navigation
- **Performance**: Flowband renders <300ms, ≤25 event pills
- **Storybook**: Required for all primitives with a11y validation

#### Success Metrics Integration
- **Desirability**: ≥70% pilots mention Flowband positively
- **Usefulness**: ≥30% AP/AR actions from Flowband, ≥50% variance chip clicks
- **Quality**: Error-free keyboard traversal, <1 alert/day average (aggregation)

## **🚨 Critical Legal & Compliance Requirements**

### **Financial Advice Liability - CRITICAL**
- **NEVER use language that could be construed as financial advice**
- We are **NOT financial advisors** - we provide tools and insights only
- **Approved Language**: "data shows", "common strategies", "insights to consider", "tools to help you decide"
- **PROHIBITED Language**: "recommendations", "advice", "we suggest", "you should", "we recommend"
- All UI copy, API responses, and documentation must be reviewed for compliance
- Users make all financial decisions - we only provide information and analysis tools
- **Legal Risk**: Significant liability exposure if we appear to give financial advice

### **Implementation Requirements**
- [ ] **Audit all existing copy** for prohibited financial advice language
- [ ] **Update API response schemas** to use compliant terminology
- [ ] **Review UI components** for advice-like language
- [ ] **Create copy review checklist** for all new features
- [ ] **Legal review process** for customer-facing content

---

## Validation & Success Metrics
