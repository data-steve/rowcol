# RowCol Comprehensive Architecture

*Version 4.0 — Financial Control Plane for CAS 2.0 Firms*

## **Executive Summary**

RowCol is a **Financial Control Plane** for CAS 2.0 firms managing 20–100 SMB clients ($1M–$5M revenue, 10–30 staff). It automates weekly cash runway rituals by orchestrating QuickBooks Online (QBO), Ramp, Plaid, and Stripe through a hub-and-spoke architecture with Smart Sync patterns, enabling advisors to enforce liquidity guardrails and deliver audit-proof outcomes.

**Core Value Proposition**: Unify siloed rails into a multi-client console for advisor-led cash discipline, ensuring auditability and scalability through proper architectural patterns.

## **Product Strategy**

### **What is RowCol?**

RowCol productizes **cash discipline** as a **Financial Control Plane**, orchestrating the multi-rail stack that CAS 2.0 firms have already adopted. Unlike passive dashboards or single-client tools, it enables advisors to:

- **Govern**: Approve payments with liquidity guardrails (e.g., 14-day buffer)
- **Verify**: Confirm execution and sync outcomes across rails  
- **Prove**: Deliver branded digests to justify client retainers

**The Win**: Save 30+ minutes/client/week, govern 50%+ of bills via RowCol, eliminate spreadsheets by week 3, and strengthen client trust with proactive deliverables.

### **Why CAS 2.0 Needs a Control Plane**

CAS 2.0 firms face unique challenges in scaling strategic advisory:

- **Siloed Rails**: QBO (ledger), Ramp (A/P), Plaid (cash), and Stripe (A/R) require manual spreadsheet aggregation, unscalable past 20-30 clients
- **Time Drain**: Weekly "Friday cash checks" take 30–45 minutes/client, limiting advisory capacity
- **Cash Flow Risks**: 82% of SMB failures stem from cash flow issues; advisors must prevent payroll misses and crunches
- **Client Trust**: Advisors need branded deliverables to prove proactive governance and justify $5k-$10k/month retainers

**RowCol's Edge**: Unifies siloed rails into a multi-client Financial Control Plane using hub-and-spoke architecture, enabling scalable advisory with audit-proof outcomes.

### **Target Market Evolution**

| Attribute | Bookkeeping (Traditional) | CAS 1.0 (2010s) | CAS 2.0 (Modern) |
|-----------|---------------------------|-----------------|------------------|
| **Scope** | Data entry, reconciliations | Bookkeeping, bill pay, payroll | Bookkeeping, A/P, A/R, weekly advisory |
| **Tech Stack** | QBO, manual processes | QBO, Bill.com, Gusto | QBO, Ramp/Relay, Plaid, Stripe |
| **Workflow** | Client-specific, manual | Semi-standardized | Standardized, automated |
| **Touchpoints** | Month-end, year-end | Monthly reports | Weekly cash checks, monthly KPIs |
| **Value Proposition** | Compliance | Outsourced back office | Strategic advisory + operations |
| **Staff Roles** | Bookkeepers | Bookkeepers, clerks | Bookkeepers, controllers, advisors |

## **Architectural Principles**

### **1. Progressive Hub Architecture**

RowCol's hub model evolves as we add rails and prove the architecture:

#### **Phase 1: MVP (QBO-Centric Hub)**
- **QBO (Hub)**: Single source of truth for ledger data - where all truth ends up
- **RowCol (Orchestrator)**: Coordinates QBO operations and provides advisor interface
- **Future Rails**: Will be added as spokes to QBO hub

#### **Phase 2: Multi-Rail (RowCol as Operational Hub)**
- **RowCol (Operational Hub)**: Advisors' interface - orchestrates all financial operations
- **QBO (Ledger Hub)**: Source of record for GAAP-compliant data - the official ledger truth
- **Ramp (Execution Rail)**: Executes payments as directed by RowCol
- **Plaid (Verification Rail)**: Provides real-time verification data to RowCol
- **Stripe (Insights Rail)**: Provides A/R insights to RowCol

**Key Insight**: In MVP, QBO is the hub because we're proving the Smart Sync pattern with a single rail. In the full vision, RowCol becomes the operational hub that orchestrates multiple rails while QBO remains the ledger hub for data lineage.

#### **Progressive Hub Evolution**

**MVP Phase (QBO-Centric)**:
```
         QBO (Hub)
           ↓
     [RowCol Orchestrator]
           ↓
    [Advisor Interface]
```

**Full Vision (RowCol as Operational Hub)**:
```
(Advisor Experience Hub)
        ROWCOL
           ↓
   [Control Plane orchestration]
           ↓
(Ledger Hub)
         QBO
           ↓
     [Rails: Ramp, Plaid, Stripe]
```

**Layer Responsibilities**:
- **MVP**: QBO is the hub; RowCol orchestrates QBO operations
- **Full Vision**: RowCol is the operational hub; QBO remains the ledger hub for reconciliation

### **2. Smart Sync Pattern (Core Infrastructure)**
The Smart Sync pattern solves current architectural rot by implementing proper data flow:

```
Runway → Domain Gateway (interface) → Infra Gateway (impl) → Sync Orchestrator decides Mirror vs Rail → Log INBOUND → Mirror upsert → return Mirror (STRICT)
Runway never sees rails/sync; Domains never instantiate sync.
```

**Key Components:**
- **Domain Gateways**: Rail-agnostic interfaces that define contracts
- **Infra Gateways**: Implement domain interfaces using sync orchestrator
- **Sync Orchestrator**: Implements smart switching between Mirror and Rail
- **Transaction Log**: Immutable audit trail for all data changes
- **State Mirror**: Fast local database for frequently accessed data

### **3. Dependency Direction (Non-Negotiable)**
```
runway/ → domains/ → infra/ (no back edges, ever)
```

### **4. Multi-Tenancy**
- **Advisor-Centric Isolation**: `advisor_id → business_id` for client data and operations
- **Tenant-Aware Services**: Enforce scoping at the application layer
- **Complete Isolation**: No shared state between businesses

### **5. Chain of Custody Verification Loop**
**Approve → Execute → Verify → Record** workflow ensures auditability:

1. **Approve (RowCol)**: Advisors approve bills with liquidity guardrails
2. **Execute (Ramp)**: Ramp releases payments and syncs to QBO
3. **Verify (RowCol)**: Confirm execution via webhooks and balance checks
4. **Record (QBO)**: Store ledger data; RowCol logs audit notes

## **System Architecture**

### **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                  ROWCOL SYSTEM ARCHITECTURE                 │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────── CLIENT LAYER ────────────────┐
│ Web UI (React) - Multi-client console, hygiene tray        │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                      API GATEWAY LAYER                      │
├─────────────────────────────────────────────────────────────┤
│ REST API (/api/v1/) - Advisor workflows, authentication    │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                     APPLICATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│ Runway Services (User experiences, workflows)              │
│ Domain Services (Business logic, Smart Sync integration)   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                     │
├─────────────────────────────────────────────────────────────┤
│ Smart Sync Orchestrator (DB/API switching logic)           │
│ Transaction Log Service (Immutable audit trails)           │
│ Rail Clients (QBO, Ramp, Plaid, Stripe integration)        │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                   EXTERNAL INTEGRATIONS (RAILS)            │
├─────────────────────────────────────────────────────────────┤
│ QBO (Ledger) | Ramp (AP) | Plaid (Balance) | Stripe (AR)   │
└─────────────────────────────────────────────────────────────┘
```

### **Service Architecture**

**Note**: Data Orchestrators are being deprecated as part of the Strangler-Fig recovery strategy. They will be replaced by proper domain gateways that follow the Smart Sync pattern.

#### **Domain Gateways (Rail-agnostic Contracts)**
```python
# domains/ap/gateways.py (contract)
from typing import Protocol, List, Literal
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

class Bill(BaseModel):
    id: str
    vendor_id: str | None = None
    due_date: date | None = None
    amount: Decimal
    status: Literal["OPEN","SCHEDULED","PAID"]

class ListBillsQuery(BaseModel):
    client_id: str
    status: Literal["OPEN","ALL"] = "OPEN"
    freshness_hint: Literal["CACHED_OK","STRICT"] = "CACHED_OK"

class BillsGateway(Protocol):
    def list(self, q: ListBillsQuery) -> List[Bill]: ...
    def schedule_payment(self, client_id: str, bill_id: str, amount: Decimal, pay_on: date) -> str: ...
```

#### **Infra Gateway (QBO Implementation)**
```python
# infra/gateways/ap_qbo_gateway.py (implements the domain interface)
class QBOBillsGateway(BillsGateway):
    def __init__(self, qbo_client: QBOClient, sync: SyncOrchestrator,
                 log: LogRepo, mirror: BillsMirrorRepo):
        self.qbo = qbo_client
        self.sync = sync
        self.log = log
        self.mirror = mirror

    def list(self, q: ListBillsQuery) -> list[Bill]:
        if self.sync.is_fresh("bills", q.client_id) and q.freshness_hint == "CACHED_OK":
            return self.mirror.list_open(q.client_id)

        raw, version = self.qbo.list_bills(company_id=q.client_id, status=q.status)
        self.log.append(direction="INBOUND", rail="qbo", operation="list_bills",
                        client_id=q.client_id, payload_json=json.dumps(raw), source_version=version)
        self.mirror.upsert_many(q.client_id, raw, source_version=version, synced_at=self.sync.now())
        return self.mirror.list_open(q.client_id)
```

#### **Runway Services (User Experience)**
```python
# runway/services/console.py (orchestrator)
class ConsoleService:
    def __init__(self, bills: BillsGateway, balances: BalancesGateway):
        self.bills = bills
        self.balances = balances

    def snapshot(self, client_id: str):
        bals = self.balances.get(BalancesQuery(client_id=client_id, freshness_hint="STRICT"))
        bills = self.bills.list(ListBillsQuery(client_id=client_id, freshness_hint="CACHED_OK"))
        # product calculators here...
        return {
            "bills": bills,
            "balances": bals,
            "runway_days": self.calculate_runway_days(bals, bills)
        }

class TrayService:
    def __init__(self, bills: BillsGateway, invoices: InvoicesGateway):
        self.bills = bills
        self.invoices = invoices
    
    def get_incomplete_bills(self, client_id: str):
        bills = self.bills.list(ListBillsQuery(client_id=client_id, status="OPEN"))
        
        # Runway-specific filtering for incomplete bills
        incomplete = [bill for bill in bills if bill.status == "OPEN"]
        return {
            "incomplete_bills": incomplete,
            "count": len(incomplete),
            "requires_attention": len([b for b in incomplete if b.days_overdue > 7])
        }
```

#### **Composition Root (Dependency Injection)**
```python
# runway/wiring.py (composition root)
def create_console_service(client_id: str) -> ConsoleService:
    # Bind Domain interfaces → Infra implementations
    bills_gateway = QBOBillsGateway(
        qbo_client=QBOClient(client_id),
        sync=SyncOrchestrator(client_id),
        log=LogRepo(),
        mirror=BillsMirrorRepo()
    )
    balances_gateway = QBOBalancesGateway(
        qbo_client=QBOClient(client_id),
        sync=SyncOrchestrator(client_id),
        log=LogRepo(),
        mirror=BalancesMirrorRepo()
    )
    
    return ConsoleService(bills_gateway, balances_gateway)
```

**Composition Root** binds Domain interfaces → Infra implementations. This is the *only* place where Runway "knows" which gateway impls exist. CI and import guards prevent Runway from importing `infra.rails.*` or `infra.sync.*` directly.

## **Data Architecture**

### **Data Storage Patterns**

#### **Pattern 1: State Mirror (Local Database)**
**When to Use**: Data needed for frequent operations, calculations

**Data Types:**
- **Bills**: For runway calculations, decision making
- **Invoices**: For AR analysis, client reporting  
- **Vendors**: For normalization, categorization
- **Customers**: For client management, aging analysis

**Sync Strategy:**
- **Frequency**: Every 15 minutes via Sync Orchestrator
- **Trigger**: Scheduled jobs + webhook notifications
- **Smart Switching**: Sync Orchestrator decides Mirror vs Rail
- **Logging**: All Mirror updates logged as INBOUND transactions

#### **Pattern 2: Live Query (API)**
**When to Use**: Real-time data where accuracy is critical

**Data Types:**
- **Current Balances**: For real-time cash position
- **Connection Status**: For health monitoring
- **Live Transactions**: For immediate updates

**Query Strategy:**
- **Frequency**: On-demand via Infra Gateway
- **Caching**: Short TTL (5-15 minutes) for performance
- **Smart Switching**: Sync Orchestrator handles Mirror vs Rail decision
- **STRICT reads**: Write INBOUND log and upsert Mirror before returning

#### **Pattern 3: Transaction Log (Append-Only Audit Trail)**
**When to Use**: Financial data changes requiring immutable audit trails

**Data Types:**
- **Bill Changes**: Amount changes, status updates, approval decisions
- **Payment Events**: Execution, reconciliation, failure events
- **Sync Events**: All data synchronization activities

**Strategy:**
- **Append-Only**: Never update or delete transaction logs
- **Complete Snapshots**: Store full data state at time of change
- **Source Attribution**: Track which service initiated the change
- **INBOUND logs**: All Mirror updates from rails
- **OUTBOUND logs**: All write operations to rails

### **Data Flow Patterns**

#### **Read Operations (Smart Sync)**
```
User Request → Runway Service → Domain Gateway → Infra Gateway → Sync Orchestrator → Mirror/Rail → Log INBOUND → Mirror Update
```

#### **Write Operations (Transaction Logged)**
```
User Action → Runway Service → Domain Gateway → Infra Gateway → Log OUTBOUND → Rail API → Log OUTBOUND Result → Mirror Update
```

#### **Background Sync (Automated)**
```
Scheduled Job → Sync Orchestrator → Rail API → Log INBOUND → Mirror Update
```

#### **Multi-Client Operations**
```
User Request → Runway Service → Domain Gateway (per client) → Infra Gateway → Sync Orchestrator → Mirror/Rail
```

## **Multi-Rail Integration**

### **Rail Responsibilities**

- **QBO (Ledger Rail)**: Ledger data, hygiene validation, audit trail, AR collections via QBO Payments
- **Ramp (A/P Execution Rail)**: Bill payment, payment processing, vendor management
- **Plaid (Verification Rail)**: Bank balances, transaction matching, cash verification, ACH payments
- **Stripe (A/R Execution Rail)**: AR payment processing, customer management, payment insights

### **Cross-Rail Sync Strategy**

- **Data Consistency**: Each rail syncs to QBO as source of truth
- **Conflict Resolution**: QBO wins for ledger data, execution rails win for their domain
- **Audit Trail**: All changes tracked across rails with timestamps and sources
- **Error Handling**: Graceful degradation when rails are unavailable

### **Verification Loop Flow**

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

## **Core Product Components**

### **Multi-Client Console**
- Portfolio dashboard with red/yellow/green buffer status
- Client drill-down views for detailed cash analysis
- Batch operations across multiple clients

### **Decision Console**
- Bill approval interface with runway impact calculations
- Guardrail enforcement (14-day buffer, essential vs. discretionary)
- Batch approval workflows for efficiency

### **Client Digest System**
- Branded weekly summaries for client delivery
- Audit trails and variance reporting
- Strategic insights and recommendations
- Export capabilities for advisor records

### **Hygiene Tray**
- Cross-rail data validation and discrepancy detection
- Fundamental integration issues that require manual intervention
- One-click remediation for resolvable problems
- Data quality monitoring and alerts

## **Progressive Implementation Strategy**

### **Phase 1: QBO Ledger Rail MVP**
**Scope**: Bills, Invoices, Balances from QBO only
**Architecture**: Smart Sync pattern with transaction logs
**Services**: 
- `domains/ap/` - Bill business logic
- `domains/ar/` - Invoice business logic  
- `domains/bank/` - Balance business logic
- `infra/qbo/` - QBO client and sync orchestrator
- `runway/services/` - User experiences

### **Phase 2: Add Ramp Integration**
**Data Sources**: QBO (ledger) + Ramp (execution)
**Mirror Strategy**: Add Ramp bills and payment data
**Domain Services**: `domains/ramp/` for Ramp-specific business logic
**Infrastructure**: `infra/ramp/` with RampSmartSyncService
**Experiences**: Add bill approval and payment execution

### **Phase 3: Add Plaid Integration**
**Data Sources**: QBO + Ramp + Plaid (verification)
**Mirror Strategy**: Add Plaid bank data and transactions
**Domain Services**: `domains/plaid/` for Plaid-specific business logic
**Infrastructure**: `infra/plaid/` with PlaidSmartSyncService
**Experiences**: Add real-time balance verification

### **Phase 4: Add Stripe Integration**
**Data Sources**: QBO + Ramp + Plaid + Stripe (insights)
**Mirror Strategy**: Add Stripe AR data and payment insights
**Domain Services**: `domains/stripe/` for Stripe-specific business logic
**Infrastructure**: `infra/stripe/` with StripeSmartSyncService
**Experiences**: Add AR insights and payment analysis

## **Technical Requirements**

### **Performance**
- **Dashboard Load**: <3 seconds for portfolio view
- **Calculations**: <1 second for runway calculations
- **Sync Operations**: Complete within 15 minutes
- **API Responses**: <300ms for user actions

### **Reliability**
- **Uptime**: 99.9% availability
- **Data Loss**: Zero data loss tolerance
- **Error Recovery**: Graceful handling of API failures
- **Monitoring**: Real-time health monitoring

### **Security**
- **Authentication**: JWT with advisor_id context
- **Encryption**: At rest and in transit
- **Compliance**: SOC2 audit requirements
- **Audit Logs**: Complete change tracking

### **Scalability**
- **Multi-Client**: Support 100+ clients per advisor
- **Rate Limiting**: Respect external API limits
- **Caching**: Cross-rail data caching with appropriate TTL
- **Batch Operations**: Efficient bulk operations

## **Competitive Landscape**

| Tool | Multi-Client View | Cash Discipline | A/P Governance | A/R Insights | Client Deliverables |
|------|------------------|-----------------|----------------|--------------|-------------------|
| **QBO** | ❌ | Basic | Basic | Basic | ❌ |
| **Ramp/Relay** | ❌ | ❌ | ✅ (Execution) | ❌ | ❌ |
| **Float/Fathom** | ❌ | Basic | ❌ | ❌ | ✅ (Reports) |
| **Centime** | ❌ | ✅ (Single-company) | ✅ (Internal) | ✅ (Internal) | ❌ |
| **Mid-Market Suites** | ❌ | ✅ (Single-client) | ✅ (AP/AR) | ✅ | ❌ |
| **RowCol** | ✅ | ✅ (Multi-rail) | ✅ (Orchestration) | ✅ (Multi-rail) | ✅ (Digests, Audits) |

**RowCol's Advantage**: Unifies siloed rails into a multi-client Financial Control Plane using hub-and-spoke architecture, enabling scalable advisory with audit-proof outcomes.

## **Future Roadmap**

### **Stage B: Multi-Client Scale**
- Enhanced dashboard with search/filters
- Nightly hygiene scans for firm-wide reliability
- Idempotent webhooks and retries for robustness

### **Stage C: By-Demand Breadth**
- Stripe read-only A/R inflows
- Relay/QBO Bill Pay verification
- Gusto payroll date visibility

### **Platform Vision**
Building for CAS 2.0, leveraging trust and traction from weekly cash discipline product:
- Weekly automating bookkeeping (transaction categorization)
- Monthly closes
- Yearly tax prep integration

---

*This comprehensive architecture provides the foundation for implementing RowCol's Financial Control Plane with proper Smart Sync patterns, solving current architectural rot while enabling future multi-rail expansion.*
