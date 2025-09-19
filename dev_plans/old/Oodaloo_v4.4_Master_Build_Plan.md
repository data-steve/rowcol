# Oodaloo v4.4 Master Build Plan: Synthesized MVP & RowCol Roadmap

**Version**: 4.4  
**Date**: 2025-09-18  
**Synthesized From**: v4.3 Build Plan + Codebase Audit + Parked Functionality Audit
**Approach**: This build plan uses v4.3 as a base, preserving all history, and enriches it with synthesized findings from architectural reviews and audits. Each task now contains the necessary context to be self-contained.

## Overview
- **Goal**: Build a sellable runway MVP in 6-8 weeks (~240-300h solo) for service agencies ($1M–$5M, 10-30 staff), targeting QBO marketplace and CAS firm channels. Automate 70-80% of weekly cash runway decisions with QBO integration.
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

## Architecture Overview

### Domains/ Structure (QBO-Facing Primitives)
```
domains/
├── core/           # Business, User, Document models/services (simplified)
│                   # Key services: KPIService, DocumentReviewService, DocumentStorageService
├── integrations/   # External API coordination (NEW CENTRALIZED LAYER)
│   ├── smart_sync.py        # Unified integration coordinator (moved from core)
│   ├── identity_graph/      # Cross-platform deduplication (moved from root)
│   ├── qbo/                # QBO integration with centralized auth
│   └── plaid/              # Banking integration
├── ap/             # Bill, Vendor, Payment models/services  
├── ar/             # Invoice, Customer, Payment models/services
├── bank/           # BankTransaction, Transfer models/services
├── policy/         # Rule, Correction, Suggestion models/services
└── vendor_normalization/  # VendorCanonical models/services (cross-cutting)
```

**Synthesized Audit Findings & Recent Refactoring**:
- **SmartSyncService**: Moved to `domains/integrations/smart_sync.py` for better architectural clarity.
- **Identity Graph**: Moved to `domains/integrations/identity_graph/` as it's pure integration deduplication logic.
- **Centralized QBO Auth**: `QBOAuth` now handles all token refresh logic, eliminating duplication across services.
- **Document Services**: Simplified to AP-only scope - removed `DocumentManagementService` and `CsvIngestionService`.
- **Clean Integration Layer**: All external API coordination now centralized in `domains/integrations/`.

### Runway/ Structure (Product Orchestration)
```
runway/
├── digest/         # Weekly email generation and delivery
├── tray/           # Prep tray UI logic and workflows
├── console/        # Cash console dashboard and controls
├── onboarding/     # Business setup and QBO connection
└── routes/         # API orchestration layer
```

## Phase 0: Foundation & Core Ritual (60h, Weeks 1-2) - ✅ COMPLETED

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

## Phase 1: Smart AP & Payment Orchestration (164h, Weeks 3-5) - 🔄 MOSTLY COMPLETED

*Core AP infrastructure completed, but key "smart" features still need implementation to justify premium pricing.*

### Stage 1.1: AP Domain Services (74h)
- **[✅] Enhanced AP Models**: `Bill`, `Payment`, and `Vendor` models enhanced with enterprise-grade complexity.
- **[✅] AP Services**: Fresh implementation of `BillService`, `PaymentService`, `VendorService`, `SmartSyncService`, and `DocumentReviewService` with mocking.

### Stage 1.2: Runway Reserve System (30h)
- **[✅] Runway Reserve Logic**: `RunwayReserveService` implemented for earmarking funds, calculating balances, and auto-releasing reserves.
- **[ ] Enhanced Payment Timing Optimization** *Effort: 15h* - **MISSING FROM CURRENT IMPLEMENTATION**
  - **Context**: To achieve 'smart' payment orchestration, enhance decision support with timing insights. These features are **not yet implemented** and are needed to justify Smart AP as a $99/mo add-on.
  - **[ ] Implement 'Latest Safe Pay Date' calculation in `BillService`**: For each bill, calculate the last possible payment date without incurring late fees or vendor relationship damage, based on terms and due dates. *Effort: 6h*
  - **[ ] Add 'Runway Impact Suggestions' to payment scheduling**: When scheduling payments, show impact on runway (e.g., 'Paying now costs 4 days of runway; delaying to Latest Safe Pay Date protects those days'). *Effort: 5h*
  - **[ ] Integrate early payment discount detection**: Flag bills with discounts (e.g., '2/10 Net 30') and calculate ROI (e.g., 'Pay $10k by Tuesday to save $200'). *Effort: 4h*

### Stage 1.3: Smart AP API & UI (45h)
- **[✅] AP API Endpoints**: `/runway/ap/` endpoints for bills, payments, and vendors are complete.
- **[✅] Enhanced Tray Integration**: 'Must Pay' vs. 'Can Delay' categorization and runway impact visualization are complete.
- **[ ] Smart AP UI/UX Design & Implementation** *Effort: 15h* - **CRITICAL FOR ICP ADOPTION**
  - **Context**: For design-savvy ICP (ad agencies, marketing firms), the UI must feel genuinely "smart" and brand-forward, not like a basic accounting tool.
  - **[ ] Payment Timing Intelligence Interface** *Effort: 6h*
    - Design visual timeline showing "Pay Now" vs "Latest Safe Pay Date" with runway impact
    - Create intuitive slider/calendar component for payment scheduling with real-time runway calculations
    - Implement smart color coding (green = safe, yellow = caution, red = risky) for payment timing decisions
  - **[ ] Discount Opportunity Highlights** *Effort: 4h*
    - Design attention-grabbing badges for early payment discounts (e.g., "Save $200 - Pay by Tuesday")
    - Create ROI calculator modal that feels like a financial advisor, not a spreadsheet
  - **[ ] Runway Impact Visualization** *Effort: 5h*
    - Design elegant runway meter showing "days protected/lost" for each payment decision
    - Create before/after preview: "Delaying this payment protects 4 days of runway"
    - Implement smooth animations that make the impact feel immediate and tangible

## Phase 2: Smart AR & Collections (115h, Weeks 6-7) - [IN PROGRESS]

*Goal*: Implement AR prioritization and automated collections with mock email delivery. **Cash focus only** - no revenue recognition or accrual accounting complexity.

### Stage 2.1: AR Domain Services (40h) - ✅ COMPLETED
- **[✅] Enhanced AR Models**: `Invoice`, `Customer`, `ARPayment` models enhanced; business logic correctly moved to services.
- **[✅] AR Services**: `CollectionsService`, `PaymentMatchingService`, `CustomerService` implemented.

### Stage 2.2: Smart Collections System (25h)
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
- **[ ] Smart AR UI/UX Design & Implementation** *Effort: 20h* - **CRITICAL FOR ICP ADOPTION**
  - **Context**: Collections interfaces are typically ugly and intimidating. For creative agencies, this needs to feel strategic and professional, not aggressive.
  - **[ ] Collection Playbook Interface** *Effort: 8h*
    - Design card-based layout showing customer payment profiles with visual indicators (reliable, slow, risky)
    - Create action-oriented buttons that feel strategic: "Gentle Nudge", "Priority Follow-up", "Final Notice"
    - Implement customer timeline showing payment history with smart insights (e.g., "Usually pays after 2nd reminder")
  - **[ ] Payment Matching Intelligence** *Effort: 6h*
    - Design confidence-scored matching interface with visual similarity indicators
    - Create drag-and-drop payment allocation with real-time invoice updates
    - Implement smart suggestions: "This $5,000 payment likely matches Invoice #1234 (95% confidence)"
  - **[ ] AR Aging Visualization** *Effort: 6h*
    - Design elegant aging buckets that feel like a dashboard, not a report
    - Create runway impact indicators: "Collecting these 3 invoices funds next month's payroll"
    - Implement priority heat maps showing which collections have highest runway impact

**Success Criteria**: AR aging calculated correctly, collection emails sent automatically (mocked), payments matched to invoices, 60%+ collection rate improvement in tests, 'Collection Playbook' increases user engagement by 50%+ in beta testing.

## Phase 2.5: Smart Budgets & Guardrails (75h, Week 7.5) - 🆕 RESTORED CRITICAL FEATURE

*Goal*: Implement budget-based guardrails and 'vacation mode' for essential vs discretionary spend categorization. **High-value $99/mo add-on** with 80% pain relief for planning. This was identified as a critical missing feature from the original ICP analysis.

### Stage 2.5.1: Budget Policy Engine (30h)
- **[ ] Budget Models & Schema** *Effort: 10h*
  - **Context**: Extend policy engine with budget fields and variance tracking per ICP pricing strategy.
  - **[ ] Create `Budget` model with categories (essential/discretionary), limits, periods**.
  - **[ ] Add budget variance fields to existing policy models in `domains/policy/`**.
  - **[ ] Create budget-specific schemas for API endpoints**.

- **[ ] Budget Service Logic** *Effort: 15h*
  - **Context**: Core budget enforcement and variance calculation for 'vacation mode' feature.
  - **[ ] Implement `BudgetService` with spend categorization logic**.
  - **[ ] Add variance calculation (actual vs budgeted spend)**.
  - **[ ] Create 'vacation mode' pre-approval workflows (essential bills only)**.
  - **[ ] Integrate with existing `PolicyEngineService` in `domains/policy/services/`**.
  - **[ ] Implement 'Decision-Time Guardrails' logic**: Warn during payment approvals if exceeding budget limits (e.g., 'This $500 payment exceeds Software budget by 25% and dips into Payroll reserve').

- **[ ] Budget Integration with Digest** *Effort: 5h*
  - **Context**: Show budget variance in weekly digest per high-engagement strategy.
  - **[ ] Add budget variance section to digest templates in `runway/digest/`**.
  - **[ ] Create budget alerts for overspend (>10% variance) in weekly emails**.

### Stage 2.5.2: Vacation Mode & Guardrails (20h)
- **[ ] Vacation Mode Planning** *Effort: 12h*
  - **Context**: Pre-plan essential payments, queue non-urgent ones - key ICP pain point relief.
  - **[ ] Create 'vacation mode' bill categorization (essential vs deferrable)**.
  - **[ ] Implement pre-approval workflows for vacation periods in `runway/ap/`**.
  - **[ ] Add vacation mode toggle to Prep Tray UI templates**.
  - **[ ] Ensure 'Vacation Mode' automates decisions**: Auto-schedule essentials (e.g., payroll, rent) and queue discretionary spend for post-vacation review.

- **[ ] Budget Guardrails** *Effort: 8h*
  - **Context**: Prevent overspend on discretionary categories - core value proposition.
  - **[ ] Add spend limits enforcement to payment approval flow**.
  - **[ ] Create budget alerts before payment execution in `PaymentService`**.
  - **[ ] Integrate guardrails with existing Runway Reserve system**.

### Stage 2.5.3: Smart Budget UI/UX Design (25h) - **CRITICAL FOR ICP ADOPTION**
- **[ ] Smart Budget Interface Design** *Effort: 25h*
  - **Context**: Budget tools are typically boring spreadsheet-like interfaces. For creative agencies, this needs to feel like a strategic planning tool, not accounting drudgery.
  - **[ ] Decision-Time Guardrails Interface** *Effort: 10h*
    - Design elegant warning modals that appear during payment approval with clear impact visualization
    - Create "traffic light" system for budget status (green = safe, yellow = approaching limit, red = over budget)
    - Implement smart suggestions: "This payment exceeds Software budget. Consider delaying until next month?"
    - Design override flow that feels intentional, not like breaking rules
  - **[ ] Vacation Mode Planning Interface** *Effort: 8h*
    - Design vacation planning wizard that feels like a travel app, not a financial tool
    - Create visual calendar showing pre-approved essentials vs. queued discretionary items
    - Implement "peace of mind" dashboard showing what's handled automatically
    - Design return-from-vacation summary with queued items ready for review
  - **[ ] Budget Variance Visualization** *Effort: 7h*
    - Design category-based budget cards with visual spending progress bars
    - Create trend indicators showing spending velocity: "On track to exceed Marketing budget by 15%"
    - Implement smart category suggestions based on spending patterns
    - Design budget reallocation interface with drag-and-drop between categories

**Success Criteria**: Budget variance tracking works, vacation mode pre-approves only essential bills, guardrails prevent discretionary overspend, 80%+ user satisfaction with 'take a vacation' confidence, 'Decision-Time Guardrails' reduce overspend incidents by 70%+ in testing, UI feels strategic and empowering (not restrictive) to design-focused ICP.

## Phase 3: Analytics & Automation (96h, Week 8)

*Goal*: Add forecasting, automation rules, comprehensive analytics dashboard. Build on Phase 1-2 data patterns with mocked data for rapid development. Focus on actionable insights for Analytics; evaluate Automation for MVP scope vs. RowCol roadmap.

### Stage 3.1: Analytics Foundation (36h)
- **[ ] Analytics Models & Services**:
  - **Context**: The `CODEBASE_AUDIT` confirmed that `KPIService` exists in `domains/core/services/kpi.py` and is active, but its routes in `_parked/domains/core/routes/kpi.py` are disconnected.
  - **[ ] `AnalyticsService`: AR/AP aging trends, basic profit analysis, runway forecasting with mock historical data**. *Effort: 10h*.
      - **Synthesized Plan**: Create a new `AnalyticsService` that builds upon the existing `KPIService` to provide higher-level insights like aging trends.
      - **Enhanced Focus**: Ensure analytics are actionable (e.g., 'AR aging trend shows 30% risk of shortfall in 2 weeks; prioritize Customer A').
  - **[ ] `ForecastingService`: 2-4 week cash flow predictions using trend algorithms**. *Effort: 10h*.
      - **Synthesized Plan**: Implement a new service using simple linear regression on historical cash flow data from AP/AR services.
      - **Enhanced Focus**: Keep predictions light-touch and actionable (e.g., '$5k invoice likely in 7 days based on history') avoiding complex meta-level forecasting.
  - **[✅] `KPIService`: CAS firm metrics**. *Effort: 6h*. **COMPLETED: Service is active**.
      - **Synthesized Plan**: The next step is to un-park its routes (see Stage 3.3).
  - **[ ] Chart.js integration for visual dashboards with sample data**. *Effort: 10h*.
      - **Synthesized Plan**: The analytics API endpoints already return data. This task involves integrating Chart.js into the existing HTML templates in `templates/` to visualize that data.
      - **Enhanced Focus**: Include criterion-based benchmarking (e.g., 'Your AR aging vs. industry average for agencies $1-5M') and cohort-based benchmarking (e.g., 'Your runway vs. peers with similar AR lag') in visualizations for actionable context.

### Stage 3.2: Automation Rules Engine (20h) - 🆕 SCOPED FOR MVP REVIEW
- **[ ] Automation Framework**:
  - **Context**: Automation can enhance the MVP by reducing manual tasks (e.g., pre-labeled rules for payments), but risks scope creep into enterprise features. Evaluate for MVP vs. RowCol roadmap.
  - **[ ] `AutomationRuleService`: Pre-labeled payment and collection rules with mock execution**. *Effort: 10h*.
      - **Synthesized Plan**: Implement basic rules (e.g., 'Pay rent if runway >2 weeks') to automate repetitive decisions in Prep Tray.
      - **MVP Justification**: Include in MVP as it ties to 'Vacation Mode' and budget guardrails, reducing cognitive load by 50%+ for common tasks.
  - **[ ] Rule execution engine with confidence scoring and dry-run mode**. *Effort: 10h*.
      - **Synthesized Plan**: Build engine to execute rules with confidence scores (e.g., '90% sure this payment matches rule') and dry-run for user validation.
      - **MVP Justification**: Include in MVP to ensure trust in automation; dry-run mode aligns with owner-centric control.

### Stage 3.3: Analytics API (10h)
- **[✅] Analytics Endpoints**: `/runway/analytics/kpis/*` endpoints are implemented.
  - **Synthesized Plan for Integration**:
    - **Un-park and integrate KPI routes**: Move routes from `_parked/domains/core/routes/kpi.py` to `runway/analytics/routes/`. Update them to use the current auth middleware and `business_id` pattern, connecting them to the existing `KPIService`.
    - **Enhanced Focus**: Ensure endpoints support benchmarking data (criterion-based and cohort-based) for dashboard visualizations.

### Stage 3.4: Smart Analytics UI/UX Design (30h) - **CRITICAL FOR ICP ADOPTION**
- **[ ] Smart Analytics Interface Design** *Effort: 30h*
  - **Context**: Analytics dashboards are typically overwhelming with charts and numbers. For creative agencies, this needs to feel like strategic insights, not data dumps.
  - **[ ] Executive Dashboard Design** *Effort: 12h*
    - Design story-driven dashboard that reads like a narrative: "Your runway story this week..."
    - Create visual hierarchy emphasizing insights over raw data
    - Implement smart contextual explanations: "AR aging is 15% worse than agencies your size"
    - Design actionable insight cards: "Focus here first" with clear next steps
  - **[ ] Benchmarking Visualization** *Effort: 8h*
    - Design criterion-based comparison interface showing "You vs. Industry Average"
    - Create cohort comparison views: "You vs. Similar Agencies" with visual positioning
    - Implement trend comparison: "Your improvement vs. peer trajectory"
    - Design confidence indicators for benchmark reliability
  - **[ ] Forecasting Interface** *Effort: 10h*
    - Design scenario planning interface with visual runway projections
    - Create "What if?" sliders for different collection/payment scenarios
    - Implement confidence bands around predictions with clear explanations
    - Design alert system for forecast changes: "Your 2-week outlook improved by 3 days"

**Success Criteria**: Runway forecasting accuracy 90%+ over 2-week window with actionable outputs, automation rules execute successfully 95%+ of time for MVP use cases, analytics dashboard loads in <3 seconds, chart rendering performance <1 second, benchmarking features increase user insight engagement by 70%+ in beta testing, analytics feel strategic and actionable (not overwhelming) to design-focused ICP.

**Note on Automation Scope**: Automation is retained in MVP due to its alignment with 'Vacation Mode' and budget guardrails, focusing on owner-centric repetitive tasks. Advanced automation (e.g., complex multi-step workflows, firm-level rules) will be deferred to RowCol phases (Phase 6+).

## Phase 6: Production & Deployment (80h, Week 11-12)

*Goal*: Transform development MVP into production-ready application with real integrations, scalable infrastructure, and deployment pipeline.

### Stage 4.1: Production Database & Infrastructure (30h)
- **[ ] Database Migration**:
  - [ ] PostgreSQL setup and configuration. *Effort: 4h*.
  - [ ] Alembic migration system implementation. *Effort: 6h*.
  - [ ] Database connection pooling and optimization. *Effort: 4h*.
  - [ ] Backup and recovery strategy. *Effort: 3h*.
- **[ ] Infrastructure as Code**:
  - [ ] Docker containerization (Dockerfile + docker-compose). *Effort: 6h*.
  - [ ] Environment configuration management. *Effort: 4h*.
  - [ ] Health checks and monitoring setup. *Effort: 3h*.

### Stage 4.2: Real External Integrations (47h)
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

### Stage 4.3: CI/CD & Deployment Pipeline (25h)
- **[ ] CI/CD Implementation**:
  - [ ] GitHub Actions workflow for testing and deployment. *Effort: 8h*.
  - [ ] Automated testing pipeline with coverage reporting. *Effort: 6h*.
  - [ ] Security scanning and dependency updates. *Effort: 4h*.
- **[ ] Cloud Deployment**:
  - [ ] AWS/GCP/Azure deployment configuration. *Effort: 4h*.
  - [ ] Load balancer and SSL certificate setup. *Effort: 3h*.

### Stage 4.4: Production Monitoring & Security (20h)
- **[ ] Monitoring & Observability**:
  - [ ] Application Performance Monitoring (APM) integration. *Effort: 4h*.
  - [ ] Centralized logging with structured logs. *Effort: 4h*.
  - [ ] Error tracking and alerting system. *Effort: 4h*.
- **[ ] Security Hardening**:
  - [ ] Security headers and HTTPS enforcement. *Effort: 3h*.
  - [ ] API rate limiting and DDoS protection. *Effort: 3h*.
  - [ ] Secrets management and environment security. *Effort: 2h*.

### Stage 4.5: Performance & Scalability (10h)
- **[ ] Performance Optimization**:
  - [ ] Database query optimization and indexing. *Effort: 4h*.
  - [ ] API response caching with Redis. *Effort: 3h*.
  - [ ] Background job processing for digest sending. *Effort: 3h*.

**Success Criteria**: 
- Application runs in production with 99.9% uptime
- Real QBO data flows correctly with <2s API response times
- Email delivery rate >95% with proper tracking
- Automated deployments work reliably
- Comprehensive monitoring and alerting in place

## Phase 5+: RowCol Roadmap & Parked Functionality

*Goal*: Transform Oodaloo into a multi-tenant RowCol platform for CAS firms. This functionality is **out of scope** for the Runway MVP.

### **Phase 6: RowCol Compliance & Policy Engine**
- **Parked Functionality**: `_parked/domains/policy/` contains advanced rules for bookkeeping transaction compliance. This is a prerequisite for the "Close" product.

### **Phase 7: RowCol Close & Advanced Accounting**
- **Parked Functionality**:
  - **Revenue Recognition Engine**: 184-line GAAP-compliant implementation from `_parked/domains/ar/services/revenue_recognition.py`. This is for accrual accounting, not cash runway.
  - **PreClose System**: Complete month-end close workflows from `_parked/features/close/`.
  
### **Phase 8: Multi-Tenant Architecture**
- **Parked Functionality**: Obsolete `Firm/Staff/Client/Engagement` models from `_parked/deprecated/`. These concepts will be re-introduced for RowCol's multi-tenant architecture.

### **Phase 9: Advanced CAS Features**
- **Parked Functionality**: `_parked/domains/ap/services/shared_expense_allocation.py` contains complex job costing logic for specialized contractors.

---
*The remaining sections (Testing Strategy, API Documentation, etc.) from v4.3 are preserved below without changes.*

## Testing Strategy (Comprehensive)

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

### Phase 1: Behavior Validation Tests
```python
# tests/test_phase1_smart_ap.py
- test_bill_approval_workflow_end_to_end()
- test_payment_execution_qbo_sync()
- test_runway_reserve_calculation_accuracy()
- test_vendor_normalization_matching()
- test_payment_orchestration_error_handling()
```

### Phase 2: Collections & AR Tests
```python
# tests/test_phase2_smart_ar.py
- test_collections_email_sequence_delivery()
- test_ar_priority_scoring_algorithm()
- test_payment_matching_accuracy()
- test_collections_pause_on_payment()
```

### Phase 3: Analytics & Automation Tests
```python
# tests/test_phase3_analytics.py
- test_runway_forecasting_accuracy()
- test_automation_rules_execution()
- test_analytics_dashboard_performance()
- test_chart_data_generation_speed()
```

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
- **Most `_parked/tests/`**: Wrong fixtures and relationships  
- **`_parked/domains/webhooks/`**: Phase 4+ feature

## Validation & Success Metrics

### Phase 0 Success Criteria
- ✅ `uvicorn main:app --reload` starts without errors
- ✅ Core API endpoints respond correctly
- ✅ Business and User models persist correctly
- ✅ Basic digest and tray functionality works
- ✅ QBO integration service initializes (mocked)

### Phase 1 Success Criteria
- 60%+ bill payment execution rate
- Runway reserve calculations accurate within 2%
- Payment-to-QBO sync successful 95%+ of time
- Must Pay vs Can Delay categorization 80%+ accurate

### Phase 2 Success Criteria
- Collection email delivery rate 95%+
- AR payment matching accuracy 90%+
- Collection sequence engagement 40%+ open rate
- Payment-to-invoice matching 85%+ automatic

### Phase 3 Success Criteria
- Runway forecasting accuracy 90%+ over 2-week window
- Automation rules execute successfully 95%+ of time
- Analytics dashboard loads in <3 seconds
- Chart rendering performance <1 second

### Overall MVP Success Criteria
- 5-10 beta agencies onboarded successfully
- Weekly digest engagement 70%+ open rate
- Overall user weekly active usage 80%+
- Customer satisfaction score 8/10+
- Technical uptime 99.5%+

## Development vs Production Strategy

### Mock-First Development Approach

**Philosophy**: Build and validate business logic with mocked external dependencies, then swap in real integrations during productionalization.

### Configuration-Driven Service Selection

**Environment Variables**:
```bash
# Development (Phases 0-3)
ENVIRONMENT=development
USE_MOCK_EMAIL=true
USE_MOCK_QBO=true
USE_MOCK_PAYMENTS=true
DATABASE_URL=sqlite:///oodaloo.db

# Production (Phase 4+)
ENVIRONMENT=production
USE_MOCK_EMAIL=false
USE_MOCK_QBO=false
USE_MOCK_PAYMENTS=false
DATABASE_URL=postgresql://user:pass@host:5432/oodaloo
SENDGRID_API_KEY=real_key
QBO_CLIENT_ID=real_client_id
QBO_CLIENT_SECRET=real_secret
AWS_ACCESS_KEY_ID=real_key
AWS_SECRET_ACCESS_KEY=real_secret
```

### Service Abstraction Benefits

1. **Rapid Development**: No external API setup required for Phases 0-3
2. **Predictable Testing**: Mock data ensures consistent test results
3. **Cost Control**: No API usage charges during development
4. **Offline Development**: Work without internet connectivity
5. **Easy Productionalization**: Simple environment variable changes

### Clean Mocking Architecture Standards

**Core Principle**: Business logic functions must be completely agnostic to whether they're using mock or real data providers.

**Implementation Pattern**:
```python
# ✅ GOOD: Clean dependency injection
class TrayService:
    def __init__(self, db: Session, data_provider: TrayDataProvider = None):
        self.data_provider = data_provider or get_tray_data_provider()
    
    def calculate_runway_impact(self, item):
        return self.data_provider.get_runway_impact(item.type)

# ❌ BAD: Mock data embedded in business logic
class TrayService:
    def calculate_runway_impact(self, item):
        if item.type == "overdue_bill":
            return {"cash_impact": -1500}  # Hard-coded mock data
```

**Provider Pattern Requirements**:
1. **Abstract Base Class**: Define interface contract
2. **Mock Provider**: External class with realistic test data
3. **Production Provider**: Real integration implementation
4. **Factory Function**: Environment-based provider selection
5. **Environment Variables**: `USE_MOCK_*=true/false` controls

**Mock Data Strategy**:

**Mock Email Provider**:
- Logs emails to console and `logs/mock_emails_*.json`
- Tracks engagement metrics for testing
- Simulates delivery success/failure scenarios
- **Location**: `runway/services/email/mock_provider.py`

**Mock QBO Integration**:
- Returns realistic bill/invoice/balance data
- Simulates API rate limiting and errors
- Supports different business scenarios (healthy, cash-strapped, etc.)
- **Location**: `domains/integrations/qbo/mock_provider.py`

**Mock Tray Data**:
- Priority weights, runway impacts, action results
- Realistic business scenarios and edge cases
- **Location**: `runway/tray/providers/mock_data_provider.py`

**Mock Payment Processing**:
- Simulates payment success/failure rates
- Mock bank account verification
- Realistic processing delays and confirmations
- **Location**: `domains/ap/providers/mock_payment_provider.py`

**Benefits of Clean Mocking**:
- Services work identically with mock/real providers
- Easy to swap providers via environment variables
- Mock data can be shared across tests
- No risk of "fooling ourselves" with embedded test data
- Production code has zero mock contamination

## Coding Standards for Maintainability

### Core Principle: "Junior Developer Test"
Every piece of code should be understandable and debuggable by a junior/mid-level developer within 30 seconds.

### Database Transaction Patterns

**✅ GOOD: Transaction Context Managers**
```python
from contextlib import contextmanager

@contextmanager
def db_transaction(db: Session):
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise

# Usage
def create_business_and_user(business_data, user_data):
    with db_transaction(db):
        business = Business(**business_data)
        db.add(business)
        db.flush()  # Get ID without committing
        
        user_data["business_id"] = business.business_id
        user = User(**user_data)
        db.add(user)
        # Both saved together or both fail
```

**❌ BAD: Manual Commits**
```python
def create_business_and_user(business_data, user_data):
    business = Business(**business_data)
    db.add(business)
    db.commit()  # Danger: partial state if user creation fails
    
    user = User(**user_data)
    db.add(user)
    db.commit()
```

### Exception Handling Patterns

**✅ GOOD: Specific Exceptions with Context**
```python
def send_digest_email(business_id: str):
    try:
        business = get_business(business_id)
        digest_data = calculate_runway(business)
        email_result = send_email(digest_data)
        return email_result
    except BusinessNotFoundError as e:
        logger.error(f"Business {business_id} not found for digest: {e}")
        raise HTTPException(status_code=404, detail="Business not found")
    except EmailDeliveryError as e:
        logger.error(f"Email delivery failed for business {business_id}: {e}")
        raise HTTPException(status_code=500, detail="Email delivery failed")
    except Exception as e:
        logger.error(f"Unexpected error in digest generation for {business_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

**❌ BAD: Bare Exception Handling**
```python
def send_digest_email(business_id: str):
    try:
        # Complex logic here
        return result
    except Exception:
        pass  # Silent failure - impossible to debug
```

### Configuration and Constants

**✅ GOOD: Named Constants with Business Context**
```python
# config/business_rules.py
class RunwayThresholds:
    CRITICAL_DAYS = 7      # Less than 1 week = critical
    WARNING_DAYS = 30      # Less than 1 month = warning
    HEALTHY_DAYS = 90      # More than 3 months = healthy

class TrayPriorities:
    URGENT_SCORE = 80      # Requires immediate attention
    MEDIUM_SCORE = 60      # Should be handled today
    LOW_SCORE = 40         # Can wait until tomorrow

# Usage
if runway_days < RunwayThresholds.CRITICAL_DAYS:
    alert_level = "critical"
```

**❌ BAD: Magic Numbers**
```python
if runway_days < 7:  # Why 7? What does this mean?
    alert_level = "critical"

if priority_score > 80:  # Why 80? Who decided this?
    mark_urgent()
```

### Service Layer Patterns

**✅ GOOD: Clear Dependencies and Error Boundaries**
```python
class DigestService:
    def __init__(self, db: Session, email_provider: EmailProvider, 
                 runway_calculator: RunwayCalculator):
        self.db = db
        self.email_provider = email_provider
        self.runway_calculator = runway_calculator
    
    def generate_weekly_digest(self, business_id: str) -> DigestResult:
        """Generate weekly runway digest for a business.
        
        Args:
            business_id: UUID of the business
            
        Returns:
            DigestResult with email status and runway data
            
        Raises:
            BusinessNotFoundError: If business doesn't exist
            RunwayCalculationError: If runway calculation fails
            EmailDeliveryError: If email sending fails
        """
        business = self._get_business_or_raise(business_id)
        runway_data = self.runway_calculator.calculate(business)
        email_result = self.email_provider.send_digest(runway_data)
        return DigestResult(runway_data=runway_data, email_result=email_result)
```

**❌ BAD: Unclear Dependencies and No Documentation**
```python
class DigestService:
    def generate_digest(self, biz_id):  # What type? What does it return?
        # Complex logic with no explanation
        pass
```

### Why These Standards Matter

1. **Onboarding Speed**: New developers productive in days, not weeks
2. **Debugging Efficiency**: Find and fix bugs in minutes, not hours  
3. **Change Velocity**: Business requirement changes don't require rewrites
4. **Code Reviews**: Reviewers can focus on business logic, not deciphering code
5. **Technical Debt**: Prevents accumulation of "clever" code that becomes unmaintainable

## Risk Mitigation

### Technical Risks
- **QBO API Rate Limits**: Implement caching, batch operations, graceful degradation
- **Email Delivery Issues**: Multiple provider backup (SendGrid + Amazon SES)
- **Database Performance**: Query optimization, indexing strategy, connection pooling
- **Integration Complexity**: Comprehensive error handling, retry logic, audit trails

### Product Risks  
- **User Adoption**: Free digest preview, gradual feature introduction, customer success outreach
- **Feature Complexity**: Start simple, add complexity based on user feedback
- **Competitive Response**: Focus on unique runway ritual, build switching costs through data

### Business Risks
- **Market Validation**: Beta program with real agencies, measure engagement metrics
- **Pricing Sensitivity**: Modular pricing, clear ROI demonstration, free tier
- **Sales Channel**: QBO marketplace + direct CAS firm outreach

## Next Steps & Immediate Actions

### Phase 0 Completion (Current Focus)
1. **Enhanced TrayService**: Priority scoring, mock QBO deep-links, action confirmations
2. **OnboardingService**: Business setup with mock QBO OAuth workflow
3. **Background Job Runner**: Select and implement job scheduler for digest delivery
4. **ADR Documentation**: Architectural decision record for domains/runway separation

### Phase 1 Preparation (Next 2 Weeks)
1. **AP Domain Review**: Analyze parked AP files for business logic patterns
2. **Runway Reserve Design**: Define data model and math logic for fund earmarking
3. **Mock Payment System**: Design payment execution simulation framework
4. **Testing Strategy**: Implement behavior-driven testing for AP workflows

### Phase 4 Planning (Production Readiness)
1. **Cloud Provider Selection**: Choose AWS/GCP/Azure based on startup credits and needs
2. **Domain & SSL Setup**: Secure domain name and certificate management
3. **Monitoring Strategy**: Select APM tool (DataDog, New Relic, or open source)
4. **Backup & Recovery**: Design database backup and disaster recovery plan

### Oodaloo → RowCol Transition Architecture

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
