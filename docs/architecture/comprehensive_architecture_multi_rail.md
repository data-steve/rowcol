# Comprehensive Architecture Overview for RowCol on Multi-rails

*Version 2.0 — October 6, 2025*

## Introduction
RowCol is a **Financial Control Plane** for CAS 2.0 firms managing 20–100 SMB clients ($1M–$5M revenue, 10–30 staff). It automates weekly cash runway rituals by orchestrating QuickBooks Online (QBO), Ramp, Plaid, and Stripe (CSV for A/R in MVP), enabling advisors to enforce liquidity guardrails (e.g., 14-day cash buffer) and deliver audit-proof outcomes. RowCol saves 30+ minutes/client/week through a multi-client console and hygiene tray, justifying $5k-$10k/month retainers.

**Advisor-First Context**: CAS firms are the primary ICP. Advisors manage client portfolios via a unified interface, approving payments and verifying outcomes. RowCol governs approvals and verification, while external rails (Ramp, QBO) handle execution and ledger updates. Individual business owners are not the target ICP.

**Core Value Proposition**: Unify siloed rails (QBO for ledger, Ramp for payment execution, Plaid for cash balances, Stripe CSV for A/R) into a multi-client console for advisor-led cash discipline, ensuring auditability and scalability.

**Nomenclature**:
- **Approve**: RowCol authorizes bill payments, applying guardrails based on Plaid cash balances.
- **Execute**: Ramp releases payments and syncs to QBO’s ledger.
- **Verify**: RowCol confirms execution (via Ramp webhooks, Plaid balances) and QBO sync.
- **Record**: QBO stores ledger data; RowCol logs audit notes for traceability.

## Architectural Principles
1. **Advisor-First Workflow** (ADR-007): Prioritize advisor-facing interfaces (multi-client console, hygiene tray) for portfolio management.
2. **Separation of Concerns** (ADR-001): Isolate rail integrations (QBO/Ramp/Plaid) from business logic and orchestration.
3. **Multi-Tenancy** (ADR-003): Advisor-centric isolation (`advisor_id → business_id`) for client data and operations.
4. **Orchestration Layer** (ADR-005): Centralize API coordination for QBO/Ramp/Plaid to handle fragility and rate limits.
5. **Multi-Client Governance** (ADR-008): Enable human-in-the-loop approvals across 20–100 clients.
6. **Multi-Rail Financial Control Plane** (ADR-010): Hub-and-spoke architecture with chain of custody verification loop across QBO (ledger hub), Ramp (A/P execution), Plaid (cash verification), and Stripe (A/R insights).

## High-Level Architecture
RowCol’s architecture is layered to separate user interaction, business logic, and external integrations:

```
┌─────────────────────────────────────────────────────────────┐
│                  ROWCOL SYSTEM ARCHITECTURE                 │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────── CLIENT LAYER ────────────────┐
│ Web UI (React)                                             │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                      API GATEWAY LAYER                      │
├─────────────────────────────────────────────────────────────┤
│ REST API (/api/v1/)                                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                     APPLICATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│ Advisor Workflow (Client Management, Notifications)        │
│ Runway Orchestration (Cash Discipline, Verification Loop)  │
│ Domains (AP, AR, Bank, Policy, Core)                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                     │
├─────────────────────────────────────────────────────────────┤
│ Integration Services (QBO, Ramp, Plaid, Stripe)            │
│ Core Services (Database, Authentication, Cache)            │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                   EXTERNAL INTEGRATIONS    (RAILS)          │
├─────────────────────────────────────────────────────────────┤
│ QBO (Ledger) | Ramp (AP) | Plaid (Balance) Stripe (AR)      │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities
1. **Client Layer**:
   - **Purpose**: Advisor-facing interface for multi-client cash management.
   - **Components**: React-based web UI with multi-client console (red/yellow/green status) and hygiene tray (data reliability flags).
2. **API Gateway Layer**:
   - **Purpose**: Expose RESTful endpoints for advisor workflows and system operations.
   - **Components**: FastAPI-based REST API (`/api/v1/`), handling authentication and request routing.
3. **Application Layer**:
   - **Advisor Workflow**: Manages client portfolios and notifications (e.g., Plaid token errors).
   - **Runway Orchestration**: Coordinates cash discipline via verification loop (approvals, verification).
   - **Domains**: Encapsulates accounting primitives (AP, AR, bank, policy).
4. **Infrastructure Layer**:
   - **Integration Services**: Connect to QBO, Ramp, Plaid, and Stripe (CSV).
   - **Core Services**: Handle database, authentication, and caching.
5. **External Integrations**:
   - **QBO**: Ledger for Bills and Invoices (BillPayments).
   - **Ramp**: Bill ingestion and payment execution.
   - **Plaid**: Real-time cash balances.
   - **Stripe**: A/R data (MVP).

## Multi-Rail Architecture: Hub-and-Spoke Model
RowCol operates as a **Financial Control Plane** using a hub-and-spoke architecture where each external rail has a specific, well-defined role:

- **QBO (Hub)**: Single source of truth for ledger data (bills, invoices, payments)
- **Ramp (Spoke)**: Execution layer for A/P operations (bill approval, payment processing)
- **Plaid (Spoke)**: Verification layer for cash operations (balance checks, guardrails)
- **Stripe (Spoke)**: Insights layer for A/R operations (invoice tracking, payment analysis)

This architecture ensures **clear separation of concerns** - each rail does one thing well, while RowCol orchestrates the verification loop across all rails.

## Chain of Custody: Verification Loop
The verification loop ensures auditability across multi-rail operations, with clear state ownership to minimize reconciliation overhead. RowCol orchestrates approvals and verification, while external rails execute and sync data.

**Intelligent Flow (OODA loop)**:
1. **Observe** (Data Orchestrator): Pull and stage raw data from QBO across client portfolio
2. **Orient** (Calculators): Analyze runway impact, prioritize decisions per client
3. **Decide** (Experience Service): Present staged decisions for approval across client portfolio
4. **Act** (Firm Staff): Approve batch → execute to QBO across multiple clients

**Steps**:
1. **Approve (RowCol)**:
   - **Description**: Advisors approve bills in the multi-client console, applying liquidity guardrails (e.g., 14-day buffer) based on Plaid cash balances.
   - **State Owner**: Ramp (bill pending → ready for release). RowCol (approval metadata, audit logs).
   - **Data Flow**: Reads Ramp bills and Plaid balances, authorizes via Ramp API, logs approval.
2. **Execute (Ramp)**:
   - **Description**: Ramp releases payments and syncs BillPayments to QBO.
   - **State Owner**: Ramp (payment execution), QBO (BillPayment in ledger).
   - **Data Flow**: Ramp processes payments, sends webhook to RowCol, syncs to QBO.
3. **Verify (RowCol)**:
   - **Description**: RowCol confirms payment execution (via Ramp webhook, Plaid balances) and QBO sync, flagging discrepancies in the hygiene tray.
   - **State Owner**: QBO (ledger truth), Plaid (cash truth).
   - **Data Flow**: Processes webhook, cross-checks Plaid balances and QBO BillPayments.
4. **Record (QBO, RowCol)**:
   - **Description**: QBO stores BillPayments (via Ramp). RowCol logs audit notes for traceability.
   - **State Owner**: QBO (ledger), RowCol (audit notes).
   - **Data Flow**: RowCol writes audit notes to QBO, updates hygiene tray.

**Hub-and-Spoke Architecture**:
```
                    ┌─────────────────────────────────────┐
                    │            ROWCOL HUB               │
                    │     (Financial Control Plane)      │
                    │  • Multi-client orchestration      │
                    │  • Workflow-specific coordination  │
                    │  • Cross-rail verification         │
                    └─────────────┬───────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┼─────────────────────────┐
        │                         │                         │                         |
        │  A/P Workflow           │  A/R Workflow           │  Cash Workflow          │
        │  ┌─────────┐ ┌─────────┐│ ┌─────────┐ ┌─────────┐│  ┌─────────┐ ┌─────────┐ |
        │  │   QBO   │ │  RAMP   ││ │   QBO   │ │ STRIPE  ││  │   QBO   │ │ PLAID   │ |
        │  │(Ledger) │ │(Execute)││ │(Ledger) │ │(A/R)    ││  │(Ledger) │ │(Cash)   │ |
        │  └─────────┘ └─────────┘│ └─────────┘ └─────────┘│  └─────────┘ └─────────┘ |
        │                         │                         |                         |
        └─────────────────────────┼─────────────────────────┼─────────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │         PLAID (Cash)                │
                    │    • Balance verification           │
                    │    • Guardrail enforcement          │
                    │    • Cross-workflow validation      │
                    └─────────────────────────────────────┘
```

**A/P Verification Loop Flow**:
```
┌───────────────────┐        ┌───────────────────┐        ┌───────────────────┐
│       RowCol      │        │       Ramp        │        │       QBO         │
│ (Approve, Verify) │        │    (Execute)      │        │     (Ledger)      │
└─────────┬─────────┘        └─────────┬─────────┘        └─────────┬─────────┘
          │                            │                            │
          │ 1. Read bills, balances    │                            │
          │ 2. Approve bills           │                            │
          │---------------------------->│ 3. Release payments        │
          │                            │---------------------------->│ 4. Sync BillPayments
          │                            │ 5. Webhook (bill.paid)     │
          │ 6. Verify (webhook, balances) <------------------------│
          │ 7. Write audit notes       │                            │
          │---------------------------->│                            │
          │                            │                            │ 8. Store ledger
┌─────────┴─────────┐
│      Plaid        │
│     (Cash)        │
└───────────────────┘
```

**A/R Processing Flow** (Future):
```
┌───────────────────┐        ┌───────────────────┐
│       RowCol      │        │       QBO         │
│ (Process, Match)  │        │     (Ledger)      │
└─────────┬─────────┘        └─────────┬─────────┘
          │                            │
          │ 1. Read invoices           │
          │ 2. Process payments        │
          │---------------------------->│ 3. Update invoice status
          │ 4. Match payments          │
          │ 5. Write audit notes       │
          │---------------------------->│
┌─────────┴─────────┐
│     Stripe        │
│   (CSV A/R)       │
└───────────────────┘
```

**Reconciliation**:
- **Plaid-to-Bank**: Optional, as Plaid is the cash truth. If needed, RowCol reconciles Plaid balances to QBO bank transactions, flagging mismatches in the hygiene tray.
- **Vendor Normalization**: RowCol maintains a vendor identity graph to align Ramp and QBO vendors, ensuring consistent bill matching across rails.

## System Components

### **Multi-Client Console**
- Portfolio dashboard with client status indicators
- Batch operations and drill-down capabilities
- Advisor workflow management

### **Decision Console**
- Bill approval interface with guardrail enforcement
- Runway impact calculations and batch operations
- Integration with Ramp for payment execution

### **Client Digest System**
- Automated weekly summary generation
- Branded client deliverables and audit trails
- Strategic insights and variance reporting

### **Hygiene Tray**
- Cross-rail data validation and discrepancy detection
- Fundamental integration issues requiring manual intervention
- One-click remediation for resolvable problems

### **Error Handling Architecture**
- Graceful degradation for API failures
- Retry logic and fallback mechanisms
- Caching for offline resilience
- Transparent error recovery without user intervention

## API Architecture
### External API (`/api/v1/`)
The REST API serves advisor workflows, exposed via FastAPI:
- **Endpoints**:
  - `/advisor/clients`: Multi-client console (list, status).
  - `/advisor/clients/{id}`: Client drill-down (details, approvals).
  - `/advisor/notifications`: Hygiene alerts (e.g., Plaid token errors).
  - `/runway/console`: Approval interface for bill actions.
  - `/runway/tray`: Hygiene tray for data reliability issues.
  - `/core/auth`: JWT authentication.
  - `/core/health`: System health check.
- **Access**: Secured by JWT with `advisor_id` context.

### Internal Service Boundaries
Domains and integrations are accessed internally by the runway orchestration layer, not exposed externally:
- **Core Domain**: Business and user management, audit logging.
- **AP Domain**: Bill and vendor processing, payment verification.
- **AR Domain**: Invoice and customer processing (CSV-based).
- **Bank Domain**: Cash balance integration (Plaid).
- **Policy Domain**: Liquidity guardrails and rules engine.
- **Vendor Normalization**: Vendor identity graph for Ramp/QBO alignment.
- **Integration Services**: QBO (ledger), Ramp (AP execution), Plaid (balances), Stripe (AR).

**Interaction**:
- Runway orchestration calls internal domain services (e.g., AP for bills, policy for guardrails).
- Domain services interact with integration services (e.g., QBO for Bills, Plaid for balances).
- No direct external API access to domains or integrations.

## Non-Functional Requirements
1. **Multi-Tenancy**:
   - **Requirement**: Isolate data and operations by `advisor_id` and `business_id`.
   - **Mechanism**: Tenant-aware services enforce scoping at the application layer.
   - **Future**: Support multi-advisor firms with role-based access (e.g., senior_accountant).
2. **Security**:
   - **Requirement**: JWT authentication, encryption at rest/transit, SOC2-compliant audit logging.
   - **Mechanism**: Audit logs capture all approval/verification actions, linked to `advisor_id`.
3. **Scalability**:
   - **Requirement**: Support 100-client portfolios with low latency.
   - **Mechanism**: Caching (e.g., Redis) for QBO/Plaid data, batch API calls to handle rate limits (e.g., QBO 500/min).
4. **Reliability**:
   - **Requirement**: Handle API fragility (e.g., Plaid token errors, Ramp webhook drops).
   - **Mechanism**: Retry logic, idempotent webhook processing, user notifications for errors.

## API Validation
- **QBO**: Supports Bills, BillPayments, and Attachables for ledger and audit notes. OAuth 2.0, 500/min rate limit. Proven by Puzzle/Digits.
- **Ramp**: Supports bill ingestion, approval, execution, and webhooks. OAuth 2.0, sandbox-tested (Ironclad).
- **Plaid**: Provides real-time balances for guardrails/verification. 99.9% SLA, used by Digits/Brex.
- **Stripe**: CSV-based A/R processing (MVP). Low-risk, validated by Digits.

*Document Status*: Living document, for principal architect review.  
*Stakeholders*: Principal Architect, Development Team, Product Owner.