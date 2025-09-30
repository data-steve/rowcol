# Comprehensive Architecture Overview for RowCol

## Introduction
**Multi-client cash flow console** for CAS firms managing 20-100 client businesses ($1M–$5M revenue, 10-30 staff) built atop QuickBooks Online (QBO). Domain-specific intelligent system that automates the weekly cash runway ritual across client portfolios through intelligent decision staging and human-in-the-loop approval.

**Firm-first context**: CAS firms as primary ICP, with individual business owners as future Phase 7+ consideration.

**Core Value Proposition**: Multi-client weekly cash call that compresses dozens of decisions across client portfolios into one intelligent approval, protecting client payroll and maximizing runway through automated orchestration.

**Agentic Architecture**: Built on the OODA loop (Observe, Orient, Decide, Act) - the same pattern as modern AI agents:
- **Sense**: Pull AR/AP/balance data from QBO
- **Think**: Calculate runway impact, prioritize decisions, simulate scenarios
- **Act**: Stage Must Pay/Can Delay, queue actions
- **Review**: Human approval → execute to QBO

## Architectural Principles
1. **Domains/Runway Separation** (ADR-001): QBO primitives vs product orchestration
2. **Multi-Tenancy Strategy** (ADR-003): Firm-first tenant isolation (firm_id → client_id)
3. **QBO API Strategy** (ADR-005): SmartSyncService as orchestration layer
4. **Data Orchestrator Pattern** (ADR-006): Agentic loop implementation (Sense → Think → Act → Review)
5. **Service Boundaries** (ADR-007): Clear dependency rules and responsibilities
6. **Agentic Architecture** (ADR-008): Human-in-the-loop AI for decision orchestration (PLANNED)

## Core Architectural Patterns

### **Agentic Loop Pattern (ADR-006: Data Orchestrator)**
**Purpose**: Implement the OODA loop (agentic pattern) through data orchestrators
**Pattern**: `Experience Service → Data Orchestrator (Sense) → Calculators (Think) → Experiences (Act) → Human Review`

**Agentic Flow**:
1. **Sense** (Data Orchestrator): Pull and stage raw data from QBO
2. **Think** (Calculators): Analyze runway impact, prioritize decisions
3. **Act** (Experience Service): Present staged decisions for approval
4. **Review** (Human): Approve batch → execute to QBO

```python
# Experience Service Integration Pattern
class TrayService:
    def __init__(self, db: Session, business_id: str):
        # Data orchestrator (runway service)
        self.data_orchestrator = HygieneTrayDataOrchestrator(db, business_id)
        
        # Calculation services (runway services)
        self.runway_calculator = RunwayCalculationService(db, business_id)
        self.priority_calculator = PriorityCalculationService(db, business_id)
        
        # Domain services (direct access)
        self.bill_service = BillService(business_id)
        self.invoice_service = InvoiceService(business_id)
```

### **Service Boundary Pattern (ADR-001 Compliance)**
**Purpose**: Clear separation between domain operations and runway decisions
**Pattern**: `Experience Services → Runway Services → Domain Services → Infra Services`

### **QBOMapper Pattern (Centralized Field Mapping)**
**Purpose**: Consistent QBO field access across codebase
**Pattern**: `QBOMapper.map_entity_data(qbo_data) → standardized_fields`

### **Task Complexity Curation Pattern**
**Purpose**: Separate executable tasks from solutioning tasks
**Pattern**: `Executable Tasks` (hands-free) vs `Solution Tasks` (analysis required)

### **Mock Elimination Pattern (No More Mocks)**
**Purpose**: Replace all mock data with real SmartSyncService calls
**Pattern**: `Mock Data → SmartSyncService → Real QBO Data`

### **Service Consolidation Pattern**
**Purpose**: Eliminate duplicate services and clarify responsibilities
**Pattern**: `Single Responsibility Principle` + `ADR-001 Compliance`

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           OODALOO SYSTEM ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Web UI (FastAPI Templates) │ Email Client (SendGrid) │ Mobile (Future)       │
└─────────────────┬───────────────────────┬─────────────────────────┬─────────────┘
                  │                       │                         │
┌─────────────────▼───────────────────────▼─────────────────────────▼─────────────┐
│                              API GATEWAY LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│              FastAPI Application (main.py)                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐     │
│  │   Runway Routes     │  │   Domain Routes     │  │    Core Routes      │     │
│  │   /runway/*         │  │   /domains/*        │  │    /auth, /health   │     │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘     │
└─────────────────┬───────────────────────┬─────────────────────────┬─────────────┘
                  │                       │                         │
┌─────────────────▼───────────────────────▼─────────────────────────▼─────────────┐
│                           APPLICATION LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        RUNWAY/ (Product Orchestration)                  │   │
│  │                                                                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │   Auth      │  │  Businesses │  │   Digest    │  │ Onboarding  │    │   │
│  │  │ - Routes    │  │ - Routes    │  │ - Routes    │  │ - Routes    │    │   │
│  │  │ - Services  │  │ - Services  │  │ - Services  │  │ - Services  │    │   │
│  │  │ - Schemas   │  │ - Schemas   │  │ - Schemas   │  │ - Schemas   │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  │                                                                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │    Tray     │  │   Reserve   │  │    Jobs     │  │ Middleware  │    │   │
│  │  │ - Models    │  │ - Services  │  │ - Runner    │  │ - Auth      │    │   │
│  │  │ - Services  │  │ - Models    │  │ - Providers │  │ - Logging   │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                       │
│                                         ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        DOMAINS/ (QBO Primitives)                        │   │
│  │                                                                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │    Core     │  │     AP      │  │     AR      │  │    Bank     │    │   │
│  │  │ - Models    │  │ - Models    │  │ - Models    │  │ - Models    │    │   │
│  │  │ - Services  │  │ - Services  │  │ - Services  │  │ - Services  │    │   │
│  │  │ - Schemas   │  │ - Schemas   │  │ - Schemas   │  │ - Schemas   │    │   │
│  │  │ - Routes    │  │ - Routes    │  │ - Routes    │  │ - Routes    │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  │                                                                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │   │
│  │  │   Policy    │  │ Vendor Norm │  │Integration  │                     │   │
│  │  │ - Models    │  │ - Models    │  │ - QBO       │                     │   │
│  │  │ - Services  │  │ - Services  │  │ - Plaid     │                     │   │
│  │  │ - Rules     │  │ - Canonical │  │ - Auth      │                     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────┬─────────────────────────┬─────────────┘
                  │                       │                         │
┌─────────────────▼───────────────────────▼─────────────────────────▼─────────────┐
│                            DATA LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐     │
│  │   SQLite (Dev)      │  │   PostgreSQL (Prod) │  │   Redis (Jobs/Cache)│     │
│  │ - Business Data     │  │ - Business Data     │  │ - Job Queue         │     │
│  │ - Transaction Data  │  │ - Transaction Data  │  │ - Session Cache     │     │
│  │ - Audit Logs        │  │ - Audit Logs        │  │ - Sync Cache        │     │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘     │
└─────────────────┬───────────────────────┬─────────────────────────┬─────────────┘
                  │                       │                         │
┌─────────────────▼───────────────────────▼─────────────────────────▼─────────────┐
│                         EXTERNAL INTEGRATIONS                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐     │
│  │   QuickBooks API    │  │    SendGrid API     │  │    Plaid API        │     │
│  │ - Bills/Invoices    │  │ - Email Delivery    │  │ - Bank Accounts     │     │
│  │ - Vendors/Customers │  │ - Template Engine   │  │ - Transactions      │     │
│  │ - Chart of Accounts │  │ - Engagement Track  │  │ - Balance Data      │     │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Domain Architecture

### Core Domain (`domains/core/`)
**Purpose**: Shared business entities and foundational services
- Multi-tenant business management
- User authentication and authorization  
- Document processing and review workflows (AP bills only)
- Analytics and KPI calculations
- Audit logging for compliance

### AP Domain (`domains/ap/`)
**Purpose**: Accounts Payable management and bill processing
- Bill ingestion and approval workflows
- Payment scheduling and execution
- Vendor master data management
- Statement reconciliation
- AP aging and reporting

### AR Domain (`domains/ar/`)
**Purpose**: Accounts Receivable management and collections
- Invoice management and tracking
- Customer master data management
- Collections and reminder workflows
- Payment matching and reconciliation
- AR aging and reporting

### Bank Domain (`domains/bank/`)
**Purpose**: Bank account and transaction management
- Bank transaction records
- Internal transfer tracking
- Bank reconciliation

## Runway Architecture

### Purpose
Runway provides product orchestration and user-facing workflows that combine multiple domain primitives.

### Key Architectural Rules

1. **No Direct External API Calls**: Runway services MUST use domains/ services only
2. **Orchestration Focus**: Combine multiple domain services for user workflows
3. **API Consistency**: All runway APIs follow `/runway/{feature}/` pattern
4. **Background Jobs**: Use job system for async workflows (digest, sync, etc.)

## Service Dependencies

### **Dependency Flow**
```
Experience Services → Runway Services → Domain Services → Infra Services
```

### **Service Boundary Rules**

#### **Domains/ Services**
- **Purpose**: CRUD primitives, QBO sync, basic business logic
- **Dependencies**: Can depend on other domain services, infra services, external APIs
- **Cannot depend on**: Runway/ services, experience services, product-specific logic

#### **Runway/ Services**
- **Purpose**: Product decisions, orchestration, runway calculations
- **Dependencies**: Can depend on domain services, infra services
- **Cannot depend on**: Experience services (circular dependency)

#### **Experience Services**
- **Purpose**: User-facing experiences, data presentation
- **Dependencies**: Can depend on runway/ services AND domain services directly
- **Pattern**: Use BOTH data orchestrators AND calculation services

### **Anti-Patterns to Avoid**
1. **Domain services depending on runway services** (ADR-001 violation)
2. **Circular dependencies** between any services
3. **Experience services depending on other experience services**
4. **Runway services depending on experience services**

## QBO Integration Architecture

### **SmartSyncService as Orchestration Layer**

SmartSyncService handles QBO's fragility while enabling immediate user actions through three patterns:

1. **User Actions**: Direct API calls with SmartSyncService protection
2. **Background Syncs**: Batch operations with SmartSyncService coordination
3. **Event-Triggered Reconciliation**: Post-action syncs for data consistency

### **API Rate Limiting Strategy**

| Period | QBO Interval | Plaid Interval | Strategy |
|--------|-------------|----------------|----------|
| Business Hours (9-5) | 4 hours | 2 hours | Normal operations |
| Month-End (28-31) | 2 hours | 1 hour | Increased frequency |
| Tax Season (Jan-Apr, Sep-Oct) | 1 hour | 30 min | High frequency |
| Off-Hours/Weekends | 8 hours | 4 hours | Maintenance only |
| User Active | Min 30min | Min 15min | Responsive to activity |

## Data Flow Architecture

### **Weekly Digest Generation Flow**
```
Monday 9:00 AM → JobRunner → DigestService → SmartSyncService → QBO API → Cache → Email
```

### **Bill Processing Flow**
```
User Upload → BillService → DocumentReview → Bill Model → User Approval → PaymentService → QBO Sync
```

## API Architecture

### **API Endpoint Organization**

#### **Public Runway APIs (User-Facing Product Features)**
- `/runway/auth/` - Authentication
- `/runway/businesses/` - Business management
- `/runway/digest/` - Weekly digest generation
- `/runway/onboarding/` - Business setup workflows
- `/runway/ap/` - Accounts Payable operations
- `/runway/ar/` - Accounts Receivable operations
- `/runway/analytics/` - Analytics and reporting

#### **Internal Domain APIs (System Integration)**
- `/domains/core/` - Core system operations
- `/domains/ap/` - Internal AP processing
- `/domains/ar/` - Internal AR processing

#### **System APIs (Health, Admin)**
- `/health` - Health checks
- `/metrics` - System metrics
- `/docs` - OpenAPI documentation

## Security & Multi-Tenancy

### **Multi-Tenant Data Isolation**
- **Database Level**: Shared database with business_id isolation
- **Application Level**: TenantAwareService pattern with automatic filtering
- **Request Level**: JWT token with business_id context

### **Security Architecture**
- **Authentication**: JWT-based with business context
- **Authorization**: Business-centric access control
- **Data Protection**: Encryption at rest and in transit
- **Audit & Compliance**: Comprehensive logging for SOC2 compliance

## Implementation Phases

### **Phase 0: Foundation ✅ (Completed)**
- FastAPI application structure
- Database models and migrations
- Authentication and middleware
- Mock-first development patterns
- Core services and basic API endpoints

### **Phase 1: Smart AP & Payment Orchestration 🔄 (In Progress)**
- Enhanced AP Models (Bill, Payment, Vendor)
- AP Services (BillService, PaymentService, VendorService) 
- SmartSyncService (Unified QBO coordination)
- DocumentReviewService (Bill processing workflows)

### **Phase 2: Smart AR & Collections (In Progress)**
- AR domain services (collections, payment matching)
- Customer management and communication
- Automated reminder sequences
- Payment reconciliation workflows

### **Phase 3: Analytics & Automation (Planned)**
- KPIService integration with dashboard
- Forecasting algorithms
- Automation rule engine
- Chart.js visualizations

### **Phase 4: Production Readiness (Planned)**
- Real QBO/SendGrid/Plaid integration
- Cloud deployment (AWS/GCP/Azure)
- Performance optimization
- Security hardening
- CI/CD pipeline

## Architectural Validation Checklist

### **ADR Compliance ✅**
- [x] ADR-001: Domains/runway separation
- [x] ADR-003: Multi-tenancy strategy
- [x] ADR-005: QBO API strategy
- [x] ADR-007: Service boundaries

### **Code Quality Standards**
- [ ] All services have comprehensive tests
- [ ] API endpoints have OpenAPI documentation
- [ ] Error handling follows patterns
- [ ] Logging is structured and consistent
- [ ] Performance benchmarks established

---

**Document Status**: Living document, updated with each architectural change  
**Next Review**: After Phase 1 completion  
**Stakeholders**: Principal Architect, Development Team, Product Owner
