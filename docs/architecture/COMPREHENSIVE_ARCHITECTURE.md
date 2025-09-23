# Comprehensive Architecture Overview for Oodaloo

## Introduction
This document provides a detailed architectural overview of Oodaloo, a cash runway management tool built atop QuickBooks Online (QBO) for service agencies ($1M–$5M revenue, 10-30 staff). 

**Core Value Proposition**: Oodaloo is a "virtual Controller-in-a-box" that serves as the "single pane of glass" for business finances, transforming QBO data into actionable insights. It addresses the core problem that small business owners know their bank balance but not their cash runway or what actions to prioritize.

This document outlines the separation of concerns, data flow, integration patterns, and guiding principles that ensure scalability from MVP to RowCol (CAS firm multi-tenant platform).

## Definition of 'Smart' for Oodaloo
Oodaloo's features are designed to be 'smart' by reducing cognitive load and providing actionable insights at the moment of decision, rather than relying on complex AI or over-predictive models. We define 'smart' across three key tiers:
- **Connective Intelligence**: Linking Accounts Payable (AP), Accounts Receivable (AR), and cash runway in real-time to show the impact of decisions across domains, addressing the siloed nature of QBO's data. Examples: Credit memo runway impact, payment timing effects on cash flow.
- **Workflow Intelligence**: Transforming a passive ledger into an active decision-making ritual with guided, prioritized actions (e.g., Prep Tray workflows) to streamline weekly financial decisions.
- **Light-Touch Predictive Intelligence**: Offering simple, actionable heuristics (e.g., 'This customer pays in 47 days on average') instead of complex forecasts that create unnecessary noise for users.

This definition guides all feature development, ensuring that 'smart' functionality directly supports agency owners in making informed, immediate decisions to manage their cash flow effectively.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Domain Architecture](#domain-architecture)
4. [Runway Architecture](#runway-architecture)
5. [Integration Architecture](#integration-architecture)
6. [Data Flow Architecture](#data-flow-architecture)
7. [Service Dependencies](#service-dependencies)
8. [API Architecture](#api-architecture)
9. [Background Jobs Architecture](#background-jobs-architecture)
10. [Security & Multi-Tenancy](#security--multi-tenancy)
11. [Implementation Phases](#implementation-phases)

---

## System Overview

Oodaloo is a cash runway management platform for service agencies ($1M–$5M, 10-30 staff) that automates 70-80% of weekly cash runway decisions through QBO integration.

### Core Value Proposition
- **Phase 0**: Core Ritual (Digest + Prep Tray + Runway Reserve)
- **Phase 1**: Smart AP (Bill Approval + Payment Orchestration) 
- **Phase 2**: Smart AR (Collections + Prioritization)
- **Phase 3**: Analytics & Automation
- **Future**: RowCol multi-tenant CAS firm platform

### Architectural Principles
1. **Domains/Runway Separation** (ADR-001): QBO primitives vs product orchestration
2. **Mock-First Development** (ADR-002): Build with mocks, productionalize incrementally
3. **Multi-Tenancy Strategy** (ADR-003): Business-centric tenant isolation
4. **Model Complexity Standards** (ADR-004): Enterprise-grade models with comprehensive documentation
5. **Service Method Delegation** (ADR-005): Business logic belongs in domain services, not orchestrators

---

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

---

## Domain Architecture

### Core Domain (`domains/core/`)
**Purpose**: Shared business entities and foundational services

```
domains/core/
├── models/                    # Foundational business entities
│   ├── base.py               # Base classes (TimestampMixin, TenantMixin)
│   ├── business.py           # Business entity (tenant root)
│   ├── user.py               # User management
│   ├── balance.py            # Financial balance snapshots
│   ├── transaction.py        # Financial transaction records
│   ├── document.py           # Document management
│   ├── audit_log.py          # SOC2 compliance logging
│   └── integration.py        # External integration tracking
├── services/                 # Core business services
│   ├── base_service.py       # TenantAwareService foundation
│   ├── document_review.py    # Document processing workflows (AP bills only)
│   ├── document_storage.py   # Document storage (AP bills only)
│   ├── kpi.py               # Analytics and KPI calculations
│   ├── user.py              # User management operations
│   └── audit_log.py         # Audit trail management
├── schemas/                  # API data transfer objects
└── routes/                   # Internal core API endpoints
```

**Key Responsibilities**:
- Multi-tenant business management
- User authentication and authorization  
- Document processing and review workflows (AP bills only)
- Analytics and KPI calculations
- Audit logging for compliance

### AP Domain (`domains/ap/`)
**Purpose**: Accounts Payable management and bill processing

```
domains/ap/
├── models/                   # AP business entities
│   ├── bill.py              # Bill records with approval workflow
│   ├── payment.py           # Payment execution and reconciliation
│   ├── vendor.py            # Vendor master data
│   └── vendor_statement.py  # Vendor statement reconciliation
├── services/                # AP business services
│   ├── bill_ingestion.py    # Bill processing (renamed to BillService)
│   ├── payment.py           # Payment orchestration (PaymentService)
│   ├── vendor.py            # Vendor management (VendorService)
│   └── statement_reconciliation.py # Statement matching
├── schemas/                 # AP API data transfer objects
├── routes/                  # Internal AP API endpoints
└── providers/               # AP-specific providers (mock/real)
```

**Key Responsibilities**:
- Bill ingestion and approval workflows
- Payment scheduling and execution
- Vendor master data management
- Statement reconciliation
- AP aging and reporting

### AR Domain (`domains/ar/`)
**Purpose**: Accounts Receivable management and collections

```
domains/ar/
├── models/                  # AR business entities
│   ├── invoice.py          # Invoice records
│   ├── customer.py         # Customer master data
│   ├── payment.py          # Customer payment tracking
│   └── credit_memo.py      # Credit memo management
├── services/               # AR business services
│   ├── collections.py      # Automated collection workflows
│   ├── adjustment.py       # Smart credit memo management
│   ├── payment_matching.py # Payment to invoice matching
│   └── customer.py         # Customer management
├── schemas/                # AR API data transfer objects
└── routes/                 # Internal AR API endpoints
```

### Bank Domain (`domains/bank/`)
**Purpose**: Bank account and transaction management

```
domains/bank/
├── models/                 # Banking entities
│   ├── bank_transaction.py # Bank transaction records
│   └── transfer.py         # Internal transfer tracking
├── services/               # Banking services
│   └── reconciliation.py   # Bank reconciliation
├── schemas/                # Banking API DTOs
└── routes/                 # Internal banking endpoints
```

### Integration Domain (`domains/integrations/`)
**Purpose**: External API integration coordination and cross-platform deduplication

```
domains/integrations/
├── smart_sync.py           # **UNIFIED INTEGRATION COORDINATOR**
├── identity_graph/         # Cross-platform deduplication system
│   ├── models.py          # Identity linking models
│   ├── services.py        # Identity consolidation logic
│   └── consolidate.py     # Cash ledger consolidation
├── qbo/                   # QuickBooks Online integration
│   ├── qbo_integration.py # Core QBO API client
│   └── qbo_auth.py        # Centralized QBO OAuth & token management
├── plaid/                 # Plaid banking integration
│   └── sync.py            # Plaid data synchronization
└── sendgrid/              # Email service integration (future)
```

**Key Principle**: 
- All external API coordination goes through `SmartSyncService`
- Identity graph prevents double-counting across platforms (bank, processors, ops)
- Centralized token management eliminates duplication across services

---

## Runway Architecture

### Purpose
Runway provides product orchestration and user-facing workflows that combine multiple domain primitives.

```
runway/
├── auth/                   # Authentication workflows
│   ├── routes/            # Auth API endpoints (/runway/auth/*)
│   ├── services/          # Auth orchestration services
│   └── schemas/           # Auth API schemas
├── businesses/            # Business management workflows
│   ├── routes/            # Business API (/runway/businesses/*)
│   ├── services/          # Business orchestration
│   └── schemas/           # Business API schemas
├── digest/                # Weekly digest generation
│   ├── routes/            # Digest API (/runway/digest/*)
│   ├── services/          # Digest orchestration + email
│   └── schemas/           # Digest API schemas
├── onboarding/            # Business setup workflows
│   ├── routes/            # Onboarding API (/runway/onboarding/*)
│   ├── services/          # Setup orchestration
│   └── schemas/           # Onboarding API schemas
├── jobs/                  # Background job processing
│   ├── job_runner.py      # Job execution engine
│   ├── providers.py       # Job storage (memory/Redis)
│   └── digest_jobs.py     # Digest scheduling
├── reserves/              # Runway reserve management
│   ├── services/          # Reserve calculation and allocation
│   └── models/            # Reserve tracking (future: move to domains/)
├── tray/                  # Prep tray workflows
│   ├── models/            # Tray item tracking
│   └── services/          # Tray orchestration
└── middleware/            # Request processing
    ├── auth.py            # Authentication middleware
    ├── tenant.py          # Multi-tenancy enforcement
    └── logging.py         # Request logging
```

### Key Architectural Rules

1. **No Direct External API Calls**: Runway services MUST use domains/ services only
2. **Orchestration Focus**: Combine multiple domain services for user workflows
3. **API Consistency**: All runway APIs follow `/runway/{feature}/` pattern
4. **Background Jobs**: Use job system for async workflows (digest, sync, etc.)

---

## Integration Architecture

### QBO Integration Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           QBO INTEGRATION ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              RUNWAY LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │DigestService│  │ BillService │  │OnboardingSvc│  │ JobRunner   │            │
│  │(digest data)│  │(bill sync)  │  │(QBO setup)  │  │(scheduled)  │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                │                   │
│         └────────────────┼────────────────┼────────────────┘                   │
│                          │                │                                    │
└─────────────────────────┼────────────────┼────────────────────────────────────┘
                          │                │
┌─────────────────────────┼────────────────┼────────────────────────────────────┐
│                      DOMAINS LAYER                                             │
├─────────────────────────┼────────────────┼────────────────────────────────────┤
│                         ▼                ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    SmartSyncService                                     │  │
│  │            **UNIFIED INTEGRATION COORDINATOR**                         │  │
│  │                                                                         │  │
│  │  ┌─ Rate Limiting ────────────────────────────────────────────────────┐ │  │
│  │  │ • Min intervals: 30min QBO, 15min others                          │ │  │
│  │  │ • Business hours: 4hr intervals                                   │ │  │
│  │  │ • Month-end: 2hr intervals                                        │ │  │
│  │  │ • Tax season: 1hr intervals                                       │ │  │
│  │  └────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                         │  │
│  │  ┌─ Sync Strategies ──────────────────────────────────────────────────┐ │  │
│  │  │ • ON_DEMAND: User waiting (digest generation)                     │ │  │
│  │  │ • SCHEDULED: Background sync (business hours aware)               │ │  │
│  │  │ • EVENT_TRIGGERED: User action triggered                          │ │  │
│  │  │ • BACKGROUND: Off-hours maintenance                               │ │  │
│  │  └────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                         │  │
│  │  ┌─ Cache Management ─────────────────────────────────────────────────┐ │  │
│  │  │ • Per-business sync tracking                                       │ │  │
│  │  │ • Result caching with timestamps                                   │ │  │
│  │  │ • User activity pattern tracking                                   │ │  │
│  │  └────────────────────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────┬───────────────────────────────────────────────┘  │
│                            │                                                  │
│  ┌─────────────────────────▼───────────────────────────────────────────────┐  │
│  │                domains/integrations/                                    │  │
│  │                                                                         │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                      │  │
│  │  │  QBOIntegration     │  │    QBOAuth          │                      │  │
│  │  │                     │  │                     │                      │  │
│  │  │ • get_bills()       │  │ • OAuth flow        │                      │  │
│  │  │ • get_invoices()    │  │ • Token refresh     │                      │  │
│  │  │ • get_vendors()     │  │ • Credentials mgmt  │                      │  │
│  │  │ • fetch_balances()  │  │                     │                      │  │
│  │  └─────────────────────┘  └─────────────────────┘                      │  │
│  └─────────────────────────┬───────────────────────────────────────────────┘  │
└─────────────────────────────┼──────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────────────────────────┐
│                         QUICKBOOKS ONLINE API                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  • Bills, Invoices, Vendors, Customers                                         │
│  • Chart of Accounts, Items, Classes                                           │
│  • Payments, Deposits, Transfers                                               │
│  • Company Information, Preferences                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### API Rate Limiting Strategy

| Period | QBO Interval | Plaid Interval | Strategy |
|--------|-------------|----------------|----------|
| Business Hours (9-5) | 4 hours | 2 hours | Normal operations |
| Month-End (28-31) | 2 hours | 1 hour | Increased frequency |
| Tax Season (Jan-Apr, Sep-Oct) | 1 hour | 30 min | High frequency |
| Off-Hours/Weekends | 8 hours | 4 hours | Maintenance only |
| User Active | Min 30min | Min 15min | Responsive to activity |

---

## Data Flow Architecture

### Weekly Digest Generation Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           WEEKLY DIGEST DATA FLOW                               │
└─────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   Monday    │
    │   9:00 AM   │ ← Scheduled Job (DigestJobScheduler)
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │ JobRunner   │ ← Background job execution
    │ executes    │
    │ digest job  │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │DigestService│ ← Runway orchestration service
    │.calculate_  │
    │ runway()    │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │SmartSyncSvc │ ← Centralized integration coordinator
    │.get_qbo_    │   • Checks rate limits
    │ data_for_   │   • Uses cached data if available
    │ digest()    │   • Applies ON_DEMAND strategy (high priority)
    └──────┬──────┘   • Handles token refresh automatically
           │
    ┌──────▼──────┐
    │domains/     │ ← Actual QBO API integration
    │integrations/│   • QBOIntegration.get_bills()
    │qbo/         │   • QBOIntegration.get_invoices()
    └──────┬──────┘   • QBOAuth.get_valid_token() (auto-refresh)
           │
    ┌──────▼──────┐
    │ QBO API     │ ← External QuickBooks Online
    │ Response    │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │SmartSyncSvc │ ← Cache results, update sync times
    │ caches &    │
    │ returns     │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │DigestService│ ← Calculate runway metrics
    │ processes   │   • Cash position
    │ QBO data    │   • AR aging
    └──────┬──────┘   • AP upcoming
           │          • Runway days remaining
    ┌──────▼──────┐
    │EmailService │ ← Send digest email
    │ sends HTML  │   • Beautiful template
    │ digest      │   • Engagement tracking
    └─────────────┘   • SendGrid delivery
```

### Bill Processing Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              BILL PROCESSING FLOW                               │
└─────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   User      │
    │ Uploads PDF │ ← Bill document upload
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │runway/ap/   │ ← Runway API endpoint
    │routes/bills │   POST /runway/ap/bills/upload
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │BillService  │ ← Enhanced bill_ingestion.py
    │.ingest_     │   • Tenant isolation
    │ document()  │   • Document processing
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │DocumentReview│ ← Document processing workflow
    │Service      │   • OCR extraction
    │             │   • Confidence scoring
    └──────┬──────┘   • Human review queue
           │
    ┌──────▼──────┐
    │ Bill Model  │ ← Create bill record
    │ Created     │   • Status: REVIEW
    │             │   • Vendor matching
    └──────┬──────┘   • Amount validation
           │
    ┌──────▼──────┐
    │ User        │ ← Review and approval
    │ Reviews &   │   • Runway API: PUT /runway/ap/bills/{id}/approve
    │ Approves    │   • Business rules validation
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │PaymentService│ ← Payment orchestration
    │.create_     │   • Payment scheduling
    │ payment()   │   • Approval workflows
    └──────┬──────┘   • Runway reserve allocation
           │
    ┌──────▼──────┐
    │SmartSyncSvc │ ← Sync payment to QBO
    │ schedules   │   • Smart timing
    │ QBO sync    │   • Rate limiting
    └──────┬──────┘   • Error handling
           │
    ┌──────▼──────┐
    │ QBO API     │ ← Create payment in QuickBooks
    │ Payment     │
    │ Created     │
    └─────────────┘
```

---

## Service Dependencies

### Core Service Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            SERVICE DEPENDENCY MAP                               │
└─────────────────────────────────────────────────────────────────────────────────┘

RUNWAY SERVICES (Product Orchestration)
├── DigestService
│   ├── → SmartSyncService (QBO data)
│   ├── → EmailService (delivery)
│   └── → Core Models (Business, Balance, User)
│
├── BillService (runway/ap/)
│   ├── → domains/ap/BillService (bill processing)
│   ├── → SmartSyncService (QBO sync)
│   ├── → DocumentReviewService (processing)
│   └── → PaymentService (orchestration)
│
├── PaymentService (runway/ap/)
│   ├── → domains/ap/PaymentService (execution)
│   ├── → SmartSyncService (QBO sync)
│   ├── → RunwayReserveService (allocation)
│   └── → VendorService (validation)
│
└── OnboardingService
    ├── → SmartSyncService (QBO setup)
    ├── → BusinessService (creation)
    └── → UserService (account setup)

INTEGRATION SERVICES (External API Coordination)
├── SmartSyncService ⭐ (UNIFIED INTEGRATION COORDINATOR)
│   ├── → domains/integrations/qbo/QBOIntegration
│   ├── → domains/integrations/plaid/PlaidSync
│   ├── → domains/integrations/identity_graph/ (deduplication)
│   ├── → Business Model (tenant context)
│   └── → Cache/Session management
│
├── domains/ap/BillService
│   ├── → Bill Model (data persistence)
│   ├── → Vendor Model (relationships)
│   ├── → DocumentReviewService (processing)
│   └── → Base TenantAwareService
│
├── domains/ap/PaymentService
│   ├── → Payment Model (data persistence)
│   ├── → Bill Model (relationships)
│   ├── → Vendor Model (validation)
│   └── → Base TenantAwareService
│
└── DocumentReviewService
    ├── → Document Model (data persistence)
    ├── → Bill Model (creation)
    └── → Base TenantAwareService

INTEGRATION SERVICES (External APIs)
├── domains/integrations/qbo/QBOIntegration
│   ├── → QBO API (external)
│   ├── → Business Model (tenant context)
│   └── → OAuth token management
│
└── domains/integrations/plaid/PlaidSync
    ├── → Plaid API (external)
    ├── → Business Model (tenant context)
    └── → Account linking
```

### Dependency Rules

1. **Runway → Domains**: ✅ Allowed (orchestration uses primitives)
2. **Domains → Runway**: ❌ Forbidden (primitives can't depend on orchestration)
3. **Domains → Domains**: ⚠️ Allowed with care (avoid circular dependencies)
4. **External APIs**: Must go through `domains/integrations/` only
5. **SmartSyncService**: Unified coordinator for all external integrations and cross-platform deduplication

---

## API Architecture

### API Endpoint Organization

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API ENDPOINT MAP                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

PUBLIC RUNWAY APIs (User-Facing Product Features)
├── /runway/auth/
│   ├── POST   /login
│   ├── POST   /logout
│   ├── POST   /refresh
│   └── GET    /me
│
├── /runway/businesses/
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{business_id}
│   ├── PUT    /{business_id}
│   └── DELETE /{business_id}
│
├── /runway/digest/
│   ├── GET    /
│   ├── POST   /generate
│   ├── GET    /history
│   └── POST   /schedule
│
├── /runway/onboarding/
│   ├── POST   /start
│   ├── GET    /status/{business_id}
│   ├── POST   /qbo/connect
│   └── POST   /complete
│
├── /runway/ap/
│   ├── GET    /bills/
│   ├── POST   /bills/upload
│   ├── PUT    /bills/{id}/approve
│   ├── POST   /bills/{id}/schedule-payment
│   ├── GET    /payments/
│   ├── POST   /payments/execute
│   └── GET    /vendors/
│
├── /runway/ar/
│   ├── GET    /invoices/
│   ├── GET    /collections/
│   ├── POST   /collections/send-reminder
│   └── GET    /customers/
│
└── /runway/analytics/
    ├── GET    /runway/
    ├── GET    /aging/
    ├── GET    /kpis/
    └── GET    /forecasts/

INTERNAL DOMAIN APIs (System Integration)
├── /domains/core/
│   ├── GET    /sync/status
│   ├── POST   /sync/trigger
│   ├── GET    /documents/review-queue
│   └── POST   /documents/{id}/review
│
├── /domains/ap/
│   ├── Internal bill processing endpoints
│   ├── Internal payment processing endpoints
│   └── Internal vendor management endpoints
│
└── /domains/ar/
    ├── Internal invoice processing endpoints
    ├── Internal collection processing endpoints
    └── Internal customer management endpoints

SYSTEM APIs (Health, Admin)
├── /health
├── /metrics
├── /docs (OpenAPI)
└── /admin/ (Future)
```

### API Authentication & Authorization

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          API SECURITY ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │    │    Auth     │    │   Tenant    │    │   Route     │
│  Request    │    │ Middleware  │    │ Middleware  │    │  Handler    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│1. JWT Token │    │2. Validate  │    │3. Extract   │    │4. Execute   │
│   Header    │───▶│   Token     │───▶│ business_id │───▶│   Business  │
│             │    │   Signature │    │   Context   │    │   Logic     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │                  │
                          ▼                  ▼
                   ┌─────────────┐    ┌─────────────┐
                   │   Return    │    │   Inject    │
                   │   401 if    │    │ business_id │
                   │   Invalid   │    │ into Request│
                   └─────────────┘    └─────────────┘

JWT Token Payload:
{
  "user_id": "uuid",
  "business_id": "uuid", 
  "email": "user@company.com",
  "permissions": ["read", "write", "admin"],
  "exp": timestamp,
  "iat": timestamp
}
```

---

## Background Jobs Architecture

### Job Processing System

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          BACKGROUND JOBS ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              JOB SCHEDULING                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Cron      │  │   User      │  │   Event     │  │   System    │            │
│  │ Scheduled   │  │ Triggered   │  │ Triggered   │  │ Triggered   │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                │                   │
│         └────────────────┼────────────────┼────────────────┘                   │
│                          │                │                                    │
└─────────────────────────┼────────────────┼────────────────────────────────────┘
                          │                │
┌─────────────────────────┼────────────────┼────────────────────────────────────┐
│                      JOB RUNNER SYSTEM                                         │
├─────────────────────────┼────────────────┼────────────────────────────────────┤
│                         ▼                ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    JobRunner                                            │  │
│  │                                                                         │  │
│  │  ┌─ Job Execution ────────────────────────────────────────────────────┐ │  │
│  │  │ • Function registry (register_function)                           │ │  │
│  │  │ • Async execution with error handling                             │ │  │
│  │  │ • Retry logic with exponential backoff                            │ │  │
│  │  │ • Status tracking (pending → running → completed/failed)          │ │  │
│  │  └────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                         │  │
│  │  ┌─ Idempotency ──────────────────────────────────────────────────────┐ │  │
│  │  │ • Idempotency keys prevent duplicate execution                     │ │  │
│  │  │ • Weekly digest: "weekly_digest_2025_38"                           │ │  │
│  │  │ • Business digest: "business_digest_{id}_2025_09_17"               │ │  │
│  │  └────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                         │  │
│  │  ┌─ Scheduling ───────────────────────────────────────────────────────┐ │  │
│  │  │ • Immediate execution                                               │ │  │
│  │  │ • Scheduled execution (future datetime)                            │ │  │
│  │  │ • Recurring jobs (via external cron)                               │ │  │
│  │  └────────────────────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────┬───────────────────────────────────────────────┘  │
│                            │                                                  │
│  ┌─────────────────────────▼───────────────────────────────────────────────┐  │
│  │                    Job Providers                                        │  │
│  │                                                                         │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                      │  │
│  │  │ InMemoryJobProvider │  │  RedisJobProvider   │                      │  │
│  │  │                     │  │                     │                      │  │
│  │  │ • Development use   │  │ • Production use    │                      │  │
│  │  │ • Simple dict       │  │ • Persistent queue  │                      │  │
│  │  │ • No persistence    │  │ • Distributed       │                      │  │
│  │  │ • Fast testing      │  │ • Scalable          │                      │  │
│  │  └─────────────────────┘  └─────────────────────┘                      │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘

JOB TYPES & SCHEDULES
├── Weekly Digest Jobs
│   ├── Schedule: Every Monday 9:00 AM
│   ├── Function: "send_all_digests" 
│   ├── Idempotency: "weekly_digest_{year}_{week}"
│   └── Retry: 2 attempts, 1 hour delay
│
├── Business Digest Jobs  
│   ├── Schedule: On-demand or per-business timing
│   ├── Function: "generate_business_digest"
│   ├── Idempotency: "business_digest_{id}_{date}"
│   └── Retry: 3 attempts, 30 min delay
│
├── QBO Sync Jobs
│   ├── Schedule: Smart intervals via SmartSyncService
│   ├── Function: "sync_qbo_data"
│   ├── Strategy: SCHEDULED background sync
│   └── Coordination: Through SmartSyncService rate limiting
│
└── Cleanup Jobs
    ├── Schedule: Daily after digest completion
    ├── Function: "cleanup_old_digest_jobs"
    ├── Purpose: Prevent job storage bloat
    └── Retention: 30 days of job history
```

### Job Function Registry

```python
# Job function registration pattern
class DigestJobScheduler:
    def _register_functions(self):
        self.job_runner.register_function("generate_business_digest", self._generate_business_digest)
        self.job_runner.register_function("send_all_digests", self._send_all_digests)
        self.job_runner.register_function("cleanup_old_digest_jobs", self._cleanup_old_jobs)
        
    async def _generate_business_digest(self, business_id: str) -> Dict[str, Any]:
        # Uses SmartSyncService for QBO data coordination
        # Calls DigestService for calculation and EmailService for delivery
        
    async def _send_all_digests(self) -> Dict[str, Any]:
        # Iterates through all active businesses
        # Schedules individual business digest jobs
        
    async def _cleanup_old_jobs(self) -> Dict[str, Any]:
        # Removes job records older than retention period
        # Prevents storage bloat
```

---

## Security & Multi-Tenancy

### Multi-Tenant Data Isolation

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MULTI-TENANCY ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────────┘

DATABASE LEVEL (Shared Database, Isolated Data)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          Business Table                                 │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │   │
│  │  │   Business A    │ │   Business B    │ │   Business C    │           │   │
│  │  │ business_id:    │ │ business_id:    │ │ business_id:    │           │   │
│  │  │ uuid-aaaa       │ │ uuid-bbbb       │ │ uuid-cccc       │           │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                       │                                         │
│                                       ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        Tenant-Isolated Tables                          │   │
│  │                                                                         │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                     Bills Table                                 │   │   │
│  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │   │   │
│  │  │  │ Bill 1      │ │ Bill 2      │ │ Bill 3      │             │   │   │
│  │  │  │business_id: │ │business_id: │ │business_id: │             │   │   │
│  │  │  │uuid-aaaa    │ │uuid-aaaa    │ │uuid-bbbb    │             │   │   │
│  │  │  └─────────────┘ └─────────────┘ └─────────────┘             │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                         │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                   Payments Table                                │   │   │
│  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │   │   │
│  │  │  │ Payment 1   │ │ Payment 2   │ │ Payment 3   │             │   │   │
│  │  │  │business_id: │ │business_id: │ │business_id: │             │   │   │
│  │  │  │uuid-aaaa    │ │uuid-bbbb    │ │uuid-cccc    │             │   │   │
│  │  │  └─────────────┘ └─────────────┘ └─────────────┘             │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘

APPLICATION LEVEL (TenantAwareService Pattern)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                     TenantAwareService                                  │   │
│  │                                                                         │   │
│  │  class TenantAwareService:                                              │   │
│  │      def __init__(self, db: Session, business_id: str):                 │   │
│  │          self.db = db                                                   │   │
│  │          self.business_id = business_id                                 │   │
│  │                                                                         │   │
│  │      def _base_query(self, model_class):                                │   │
│  │          """All queries automatically filtered by business_id"""       │   │
│  │          return self.db.query(model_class).filter(                     │   │
│  │              model_class.business_id == self.business_id                │   │
│  │          )                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                       │                                         │
│                                       ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    All Domain Services                                  │   │
│  │                                                                         │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │   │
│  │  │BillService  │ │PaymentSvc   │ │VendorSvc    │ │SmartSyncSvc │      │   │
│  │  │extends      │ │extends      │ │extends      │ │extends      │      │   │
│  │  │TenantAware  │ │TenantAware  │ │TenantAware  │ │TenantAware  │      │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘

REQUEST LEVEL (Middleware Enforcement)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      Request Flow                                       │   │
│  │                                                                         │   │
│  │  1. User Request → Auth Middleware                                      │   │
│  │     ├── Validate JWT token                                              │   │
│  │     ├── Extract business_id from token                                  │   │
│  │     └── Inject into request context                                     │   │
│  │                                                                         │   │
│  │  2. Request Context → Route Handler                                     │   │
│  │     ├── business_id available in request                                │   │
│  │     ├── Pass to service constructors                                    │   │
│  │     └── All data operations automatically tenant-isolated               │   │
│  │                                                                         │   │
│  │  3. Service Operations → Database                                       │   │
│  │     ├── _base_query() adds business_id filter                           │   │
│  │     ├── CREATE operations include business_id                           │   │
│  │     └── No cross-tenant data access possible                            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            SECURITY ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────────────┘

AUTHENTICATION (JWT-Based)
├── Token Generation
│   ├── User login → JWT token with business_id
│   ├── Token expiration: 24 hours
│   ├── Refresh token: 30 days
│   └── Secure cookie storage (HttpOnly, Secure, SameSite)
│
├── Token Validation
│   ├── Signature verification (RS256)
│   ├── Expiration checking
│   ├── Business context extraction
│   └── Rate limiting per user/business
│
└── Token Refresh
    ├── Automatic refresh before expiration
    ├── Refresh token rotation
    └── Invalid token cleanup

AUTHORIZATION (Business-Centric)
├── Business Ownership
│   ├── Users can only access their business data
│   ├── business_id embedded in JWT token
│   ├── All database queries filtered by business_id
│   └── No cross-business data access
│
├── Role-Based Access (Future)
│   ├── Owner: Full access
│   ├── Bookkeeper: AP/AR access
│   ├── Viewer: Read-only access
│   └── Admin: System management
│
└── API Permissions
    ├── /runway/ endpoints: Business owner access
    ├── /domains/ endpoints: Internal system only
    └── /admin/ endpoints: System admin only (future)

DATA PROTECTION
├── Encryption at Rest
│   ├── Database encryption (PostgreSQL TDE)
│   ├── File storage encryption (S3 server-side)
│   └── Backup encryption
│
├── Encryption in Transit
│   ├── TLS 1.3 for all API communications
│   ├── Certificate management (Let's Encrypt)
│   └── HSTS headers
│
├── PII Handling
│   ├── Minimal data collection
│   ├── Data retention policies
│   ├── GDPR compliance preparation
│   └── Audit trail for all data access
│
└── External Integration Security
    ├── OAuth 2.0 for QBO integration
    ├── API key management for SendGrid/Plaid
    ├── Token refresh automation
    └── Secure credential storage (env vars/vault)

AUDIT & COMPLIANCE
├── Audit Logging
│   ├── All data modifications logged
│   ├── User action tracking
│   ├── API access logging
│   └── SOC 2 compliance preparation
│
├── Error Handling
│   ├── No sensitive data in error messages
│   ├── Structured error logging
│   ├── Rate limiting on auth endpoints
│   └── DDoS protection (future)
│
└── Monitoring
    ├── Failed login attempt tracking
    ├── Unusual access pattern detection
    ├── Performance monitoring
    └── Security event alerting
```

---

## Implementation Phases

### Phase 0: Foundation ✅ (Completed)
- FastAPI application structure
- Database models and migrations
- Authentication and middleware
- Mock-first development patterns
- Core services and basic API endpoints
- Testing framework and documentation

### Phase 1: Smart AP & Payment Orchestration 🔄 (In Progress)

**Completed:**
- ✅ Enhanced AP Models (Bill, Payment, Vendor)
- ✅ AP Services (BillService, PaymentService, VendorService) 
- ✅ SmartSyncService (Unified QBO coordination)
- ✅ DocumentReviewService (Bill processing workflows)

**Remaining:**
- [ ] Runway Reserve System
- [ ] Smart AP API & UI
- [ ] Integration testing and validation

### Phase 2: Smart AR & Collections (In Progress)
- **[✅] Smart Credit Memo Management**: Intelligent overpayment detection and runway impact visualization
- AR domain services (collections, payment matching)
- Customer management and communication
- Automated reminder sequences
- Payment reconciliation workflows

### Phase 3: Analytics & Automation (Planned)
- KPIService integration with dashboard
- Forecasting algorithms
- Automation rule engine
- Chart.js visualizations

### Phase 4: Production Readiness (Planned)
- Real QBO/SendGrid/Plaid integration
- Cloud deployment (AWS/GCP/Azure)
- Performance optimization
- Security hardening
- CI/CD pipeline

---

## Architectural Validation Checklist

### ADR-001 Compliance ✅
- [x] SmartSyncService as single QBO coordinator
- [x] Runway services use domains/ primitives only
- [x] No direct external API calls from runway/
- [x] Clear domains/runway separation

### ADR-002 Compliance ✅
- [x] Mock providers for external services
- [x] Provider pattern implementation
- [x] Easy mock-to-real transition path

### ADR-003 Compliance ✅
- [x] TenantAwareService pattern
- [x] business_id tenant isolation
- [x] Middleware enforcement
- [x] JWT token business context

### ADR-004 Compliance ✅
- [x] Enterprise-grade model complexity
- [x] Comprehensive documentation
- [x] Business logic in services
- [x] Clear maintenance guidelines

### Code Quality Standards
- [ ] All services have comprehensive tests
- [ ] API endpoints have OpenAPI documentation
- [ ] Error handling follows patterns
- [ ] Logging is structured and consistent
- [ ] Performance benchmarks established

---

**Document Status**: Living document, updated with each architectural change  
**Next Review**: After Phase 1 completion  
**Stakeholders**: Principal Architect, Development Team, Product Owner
