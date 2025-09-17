# Oodaloo v4.3 Build Plan: Runway MVP & Mature Phases

**Checksum**: a1b2c3d4e5f6789abcdef0123456789fedcba

## Overview
- **Goal**: Build a sellable runway MVP in 6-8 weeks (~240-300h solo) for service agencies ($1M–$5M, 10-30 staff), targeting QBO marketplace and CAS firm channels. Automate 70-80% of weekly cash runway decisions with QBO integration for **Phase 0** (Core Ritual: Digest + Prep Tray + Runway Reserve), **Phase 1** (Smart AP: Bill Approval + Payment Orchestration), and **Phase 2** (Smart AR: Collections + Prioritization). Validate with 5-10 beta agencies ($99/mo) in Q4 2025. Mature phases add automation rules, analytics, and CAS multi-tenant features.
- **Scope**: Prioritize weekly cash ritual (digest email, prep tray, runway reserve earmarking, QBO sync). Use rigorous domains/ for QBO-facing primitives, runway/ for product orchestration. Build comprehensive API layer and behavior-driven testing from day one.
- **GTM Wedge**: Free "Weekly Runway Email" (digest preview) to hook agencies, upselling $99/mo core ritual, $99/mo Smart AP, $99/mo Smart AR add-ons.
- **Distribution Strategy**: QBO App Store targeting bookkeepers (5-15 clients each) as middle ground between individual owners and CAS firms. Bookkeepers become champions for runway advisory services, creating natural upgrade path to RowCol multi-tenant platform.
- **Tech Stack**: Python, FastAPI, SQLAlchemy (SQLite dev, Postgres prod), QBO API, SendGrid, Pydantic, Pytest, Redis (caching), Chart.js (analytics).
- **Design Principles**:
  - **Domains/Runway Architecture**: `domains/` contains QBO-facing primitives (reusable, rigorous), `runway/` contains product orchestration (digest, tray, console UI logic).
  - **Staged Development**: Mock external services (QBO, email, payments) in early phases, productionalize incrementally.
  - **Clean Mocking Architecture**: Mock data and logic must be external to core business functions via dependency injection. Services should work identically with mock or real providers.
  - **Junior/Mid-Level Maintainability**: Code should be readable and debuggable by junior/mid-level developers. Avoid clever tricks, prefer explicit over implicit, use clear naming and proper error handling.
  - **Behavior-Driven Testing**: User journey validation, email engagement tracking, QBO reconciliation accuracy from Phase 0.
  - **API-First**: Comprehensive REST API with OpenAPI docs, supporting both web UI and future mobile/integrations.
  - **Fresh Implementation**: Reference parked files for business logic, implement fresh using current Business-centric architecture.
  - **Production-Ready Path**: Clear progression from SQLite + mocks → Postgres + real APIs + Docker + CI/CD.
- **Validation Plan**: Q4 2025, 5-10 agencies (10-30 staff each), validating 70%+ digest engagement, 60%+ payment execution accuracy.
- **Pricing**: $99/mo core ritual, $99/mo Smart AP add-on, $99/mo Smart AR add-on, $199/mo automation bundle.
- **KPIs**: Digest open rate (70%+), payment execution rate (60%+), runway calculation accuracy (90%+), user engagement (weekly active usage 80%+).

## Architecture Overview

### Domains/ Structure (QBO-Facing Primitives)
```
domains/
├── core/           # Business, User, Document, Integration models/services
│                   # Key services: SmartSyncService, KPIService, DocumentReviewService
├── ap/             # Bill, Vendor, Payment models/services  
├── ar/             # Invoice, Customer, Payment models/services
├── bank/           # BankTransaction, Transfer models/services
├── policy/         # Rule, Correction, Suggestion models/services
└── vendor_normalization/  # VendorCanonical models/services
```

**Note**: Core services like `SmartSyncService` (QBO sync timing), `KPIService` (CAS analytics), and `DocumentReviewService` (bill processing) are essential infrastructure services that support multiple phases but may not be explicitly called out in each phase description.

### Runway/ Structure (Product Orchestration)
```
runway/
├── digest/         # Weekly email generation and delivery
├── tray/           # Prep tray UI logic and workflows
├── console/        # Cash console dashboard and controls
├── onboarding/     # Business setup and QBO connection
└── routes/         # API orchestration layer
```

### API Structure
```
runway/routes/      # Runway product APIs (user-facing)
├── auth.py         # Authentication and authorization (/runway/auth/)
├── businesses.py   # Business management (/runway/businesses/)
├── digest.py       # Weekly digest generation (/runway/digest/)
├── tray.py         # Prep tray items and actions (/runway/tray/)
├── console.py      # Cash console dashboard (/runway/console/)
├── analytics.py    # Reporting and insights (/runway/analytics/)
└── onboarding.py   # Business setup (existing)

domains/*/routes/   # Internal domain APIs (QBO-facing)
├── ap/routes/      # Internal AP operations (/domains/ap/*)
├── ar/routes/      # Internal AR operations (/domains/ar/*)
├── bank/routes/    # Internal bank operations (/domains/bank/*)
└── core/routes/    # Internal core operations (/domains/core/*)
```

## Phase 0: Foundation & Core Ritual (60h, Weeks 1-2)

*Goal*: Establish robust foundation with Business/User models, mocked QBO integration, email digest with mock provider, basic tray functionality, comprehensive testing framework. Focus on rapid development with mocked external services. *Effort: ~60h*

### Stage 0.1: Architecture Hardening (30h)
- **[✅] Database Structure**: Consolidated `db/` package with `Base`, `SessionLocal`, `get_db`, `create_db_and_tables`, `seed_database`.
- **[✅] Core Models**: `Business`, `User`, `Balance`, `Transaction`, `Document` models with proper relationships.
- **[✅] Testing Foundation**: Phase 0 targeted testing strategy, behavior validation framework.
- **[✅] Mocked QBO Integration**: `QBOIntegrationService` with comprehensive mock data for rapid development.

### Stage 0.2: Core API Foundation (30h)
- **[✅] API Structure**: Complete FastAPI application with comprehensive route organization.
  - [✅] `/runway/auth/` endpoints: login, logout, token refresh. *Effort: 4h*.
  - [✅] `/runway/businesses/` endpoints: create, read, update business profiles. *Effort: 4h*.
  - [✅] `/runway/users/` endpoints: user management and permissions. *Effort: 3h*.
  - [✅] Middleware: Authentication, CORS, request logging, error handling. *Effort: 5h*.
  - [✅] Enhance API tasks with auth/permission models, DTOs, and acceptance criteria for `/runway/auth/`, `/runway/businesses/`, `/runway/users/`. *Effort: 5h*.
- **[✅] Runway Services Foundation**:
  - [✅] `DigestService`: Weekly email generation with runway calculations. *Effort: 6h*.
  - [✅] Enhanced `DigestService` with mock email provider, beautiful HTML templates, and engagement tracking structure. *Effort: 5h*.
  - [✅] `TrayService`: Enhanced with priority scoring and mock QBO deep-links. *Effort: 4h*.
  - [✅] `OnboardingService`: QBO connection and business setup workflows with mock OAuth. *Effort: 4h*.
- **[✅] QBO Integration Test Framework** (Mock Development Foundation):
  - [✅] Build comprehensive QBO sandbox test scenarios with realistic agency data (bills, invoices, multiple accounts). *Effort: 8h*. **Status: Test framework and mock scenarios complete**
  
  > **Note**: Actual QBO validation moved to **Phase 4: Productionalization** where real sandbox testing occurs before production deployment.
- **[ ] Architectural and Data Model Enhancements**:
  - [✅] Architectural Decision Record (ADR) for `domains/` vs. `runway/` separation and CI import rule checks. *Effort: 3h*.
  - [✅] Define `RunwayReserve` data model, math logic (reserved vs. available), and migration strategy. *Effort: 5h*.
  - [✅] Select and implement background job runner (e.g., RQ) for digest scheduling with idempotency and retries. *Effort: 5h*.
  - [✅] Document QBO config contract (`.env` requirements, dry-run defaults) and safety gates. *Effort: 3h*.

**Success Criteria**: `uvicorn main:app --reload` starts cleanly, basic API endpoints respond, core models persist correctly.

## Phase 1: Smart AP & Payment Orchestration (134h, Weeks 3-5)

*Goal*: Implement bill approval workflows, runway reserve earmarking, payment orchestration with mocked QBO sync. Reference parked AP files for business logic, implement fresh with mock payment execution. *Effort: ~134h*

### Stage 1.1: AP Domain Services (74h)
- **[✅] Enhanced AP Models**: 
  - [✅] Review `_parked/domains/ap/` for business logic patterns. *Effort: 10h*.
  - [✅] `Bill` model enhancements: approval status, payment scheduling, QBO sync fields. *Effort: 8h*.
  - [✅] `Payment` model: payment intents, execution tracking, reconciliation status. *Effort: 8h*.
  - [✅] `Vendor` model: payment terms, preferred payment methods, canonical mapping. *Effort: 6h*.
- **[✅] AP Services** (Fresh Implementation with Mocking):
  - [✅] `BillService`: Bill ingestion, approval workflows, payment scheduling with mock data. *Effort: 12h*.
  - [✅] `PaymentService`: Mock payment execution, simulated QBO sync, reconciliation logic. *Effort: 10h*.
  - [✅] `VendorService`: Enhanced vendor matching and canonicalization with sample data. *Effort: 6h*.
  - [✅] `SmartSyncService`: **UNIFIED QBO COORDINATION** - Single point for all QBO access, intelligent sync timing, rate limiting, context-aware intervals. Eliminates ADR-001 violations. *Effort: 8h*.
  - [✅] `DocumentReviewService`: Document processing workflows for bill ingestion and approval. *Effort: 6h*.

### Stage 1.2: Runway Reserve System (30h)
- **[ ] Runway Reserve Logic**:
  - [ ] `RunwayReserveService`: Earmarking funds for scheduled payments. *Effort: 10h*.
  - [ ] Balance calculation with reserved vs. available funds. *Effort: 8h*.
  - [ ] Reserve auto-release on payment execution or AR collection. *Effort: 6h*.
  - [ ] Visual runway meter and reserve indicators. *Effort: 6h*.

### Stage 1.3: Smart AP API & UI (30h)
- **[ ] AP API Endpoints**:
  - [ ] `/runway/ap/bills/` - List, approve, schedule bills (orchestrates domains/ap). *Effort: 8h*.
  - [ ] `/runway/ap/payments/` - Execute payments, track status (orchestrates domains/ap). *Effort: 8h*.
  - [ ] `/runway/ap/vendors/` - Vendor management and normalization (orchestrates domains/ap). *Effort: 6h*.
- **[ ] Enhanced Tray Integration**:
  - [ ] Must Pay vs. Can Delay bill categorization. *Effort: 4h*.
  - [ ] Runway impact visualization for payment decisions. *Effort: 4h*.

**Success Criteria**: Bills can be approved and scheduled, mock payments execute successfully, runway reserves update correctly, payment workflows demonstrate 60%+ success rate with mock data.

## Phase 2: Smart AR & Collections (80h, Weeks 6-7)

*Goal*: Implement AR prioritization, automated collections with mock email delivery, payment matching algorithms. Reference parked AR files, implement fresh with mock customer data and collection scenarios. *Effort: ~80h*

### Stage 2.1: AR Domain Services (40h)
- **[ ] Enhanced AR Models**:
  - [ ] Review `_parked/domains/ar/` for collections logic patterns. *Effort: 8h*.
  - [ ] `Invoice` model: aging buckets, collection priority, payment matching. *Effort: 6h*.
  - [ ] `Customer` model: payment history, collection preferences, risk scoring. *Effort: 6h*.
  - [ ] `ARPayment` model: payment matching, deposit reconciliation. *Effort: 6h*.
- **[ ] AR Services** (Fresh Implementation):
  - [ ] `CollectionsService`: Automated reminder sequences, priority scoring. *Effort: 8h*.
  - [ ] `PaymentMatchingService`: Deposit to invoice reconciliation. *Effort: 6h*.

### Stage 2.2: Smart Collections System (25h)
- **[ ] Collections Automation**:
  - [ ] 3-stage email sequences (30d gentle, 45d urgent, 60d final). *Effort: 10h*.
  - [ ] Priority scoring: amount, age, customer history. *Effort: 8h*.
  - [ ] Auto-pause on payment detection. *Effort: 7h*.

### Stage 2.3: AR API & Integration (15h)
- **[ ] AR API Endpoints**:
  - [ ] `/runway/ar/invoices/` - List, prioritize, track aging (orchestrates domains/ar). *Effort: 5h*.
  - [ ] `/runway/ar/collections/` - Manage reminder sequences (orchestrates domains/ar). *Effort: 5h*.
  - [ ] `/runway/ar/payments/` - Payment matching and reconciliation (orchestrates domains/ar). *Effort: 5h*.

**Success Criteria**: AR aging calculated correctly, collection emails sent automatically, payments matched to invoices, 60%+ collection rate improvement.

## Phase 3: Analytics & Automation (66h, Week 8)

*Goal*: Add forecasting, automation rules, comprehensive analytics dashboard. Build on Phase 1-2 data patterns with mocked data for rapid development. *Effort: ~66h*

### Stage 3.1: Analytics Foundation (36h)
- **[ ] Analytics Models & Services**:
  - [ ] `AnalyticsService`: AR/AP aging trends, basic profit analysis, runway forecasting with mock historical data. *Effort: 10h*.
  - [ ] `ForecastingService`: 2-4 week cash flow predictions using trend algorithms. *Effort: 10h*.
  - [ ] `KPIService`: CAS firm metrics (auto-posting %, override rates, task completion, processing times). *Effort: 6h*.
  - [ ] Chart.js integration for visual dashboards with sample data. *Effort: 10h*.

### Stage 3.2: Automation Rules Engine (20h)
- **[ ] Automation Framework**:
  - [ ] `AutomationRuleService`: Pre-labeled payment and collection rules with mock execution. *Effort: 10h*.
  - [ ] Rule execution engine with confidence scoring and dry-run mode. *Effort: 10h*.

### Stage 3.3: Analytics API (10h)
- **[ ] Analytics Endpoints**:
  - [ ] `/runway/analytics/runway/` - Runway trends and forecasts with mock data. *Effort: 5h*.
  - [ ] `/runway/analytics/aging/` - AR/AP aging analytics with sample datasets. *Effort: 5h*.

**Success Criteria**: Analytics dashboard loads quickly with mock data, forecast algorithms work correctly, automation rules execute in dry-run mode.

## Phase 4: Productionalization & Deployment (80h, Week 9-10)

*Goal*: Transform development MVP into production-ready application with real integrations, scalable infrastructure, and deployment pipeline. *Effort: ~80h*

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

### Integration & Performance Tests
```python
# tests/test_integration.py
- test_qbo_api_rate_limiting()
- test_email_delivery_tracking()
- test_database_performance_100_bills()
- test_concurrent_user_workflows()
- test_error_recovery_scenarios()
- test_qbo_contract_stubs()  # Contract tests for QBO client stubs (record/replay for sandbox)
- test_openapi_schema_snapshots()  # OpenAPI schema snapshot tests in CI
- test_performance_budgets_100_bills()  # Performance budgets for 100+ bills processing path
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
