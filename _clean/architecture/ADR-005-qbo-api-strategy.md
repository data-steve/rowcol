# ADR-005: QBO API Strategy

**Date**: 2025-01-27  
**Status**: Accepted  
**Decision**: Use Sync Orchestrator with Smart Sync Pattern for QBO fragility while enabling immediate user actions.

## Context

QBO API has well-documented fragility that can disrupt the cash runway ritual:
- **Rate Limiting**: 500 requests/min per app, 100 requests/sec per realm
- **Intermittent Failures**: 503 Service Unavailable, network latency, maintenance windows
- **Duplicate Actions**: Retrying failed requests can create duplicate transactions
- **Lost Actions**: QBO's async processing can make actions appear to fail when they succeeded
- **Data Inconsistencies**: QBO data may not reflect real-time changes

**Architecture Alignment**: This ADR aligns with the Smart Sync Pattern from our comprehensive architecture - domain gateways use sync orchestrator for rail-specific coordination, with transaction logging and state mirror integration.

## Decision

**Sync Orchestrator with Smart Sync Pattern**: Domain gateways use sync orchestrator for rail coordination, with transaction logging and state mirror integration.

### Key Patterns
- **Domain Gateway Pattern**: Rail-agnostic interfaces in domains, rail-specific implementations in infra
- **Sync Orchestrator Pattern**: Centralized sync logic with freshness checks and retry logic
- **Transaction Log Pattern**: All data changes logged for audit trail and replayability
- **State Mirror Pattern**: Local mutable database for fast reads, synced from external APIs
- **Smart Sync Pattern**: DB freshness checks → API fallback → Log INBOUND → Mirror upsert

## Sync Orchestrator Interface (Concrete)

### Core Interface
```python
# infra/sync/orchestrator.py
class SyncOrchestrator:
    def read_refresh(
        self,
        entity: str,                    # "bills", "invoices", "balances"
        client_id: str,                 # advisor_id in MVP
        hint: Literal["CACHED_OK", "STRICT"],
        mirror_is_fresh: Callable[[str, str, dict], bool],  # (entity, client_id, policy) -> bool
        fetch_remote: Callable[[], tuple[list[dict], str | None]],  # returns (raw, source_version)
        upsert_mirror: Callable[[list[dict], str | None, datetime], None],
        read_from_mirror: Callable[[], list[Any]],
        on_hygiene: Callable[[str, str], None],  # (client_id, code) -> None
    ) -> list[Any]:
        # Policy-driven freshness check
        # STRICT or stale/expired → rail → INBOUND log → mirror upsert → return mirror
        # CACHED_OK + fresh → return mirror
        # Error → log failure + hygiene flag + return stale mirror

    def write_idempotent(
        self,
        operation: str,                 # "ap.post_bill_payment"
        client_id: str,                 # advisor_id in MVP
        idem_key: str,                  # stable key for deduplication
        call_remote: Callable[[], dict],
        optimistic_apply: Callable[[dict], None],
        on_hygiene: Callable[[str, str], None],
    ) -> dict:
        # OUTBOUND intent log → rail call → OUTBOUND result log → optimistic mirror apply
        # Error → log failure + hygiene flag + raise exception
```

### Entity Policy (Configuration)
```python
# core/freshness_policy.py
ENTITY_POLICY = {
    "bills":    {"soft_ttl_s": 300,  "hard_ttl_s": 3600},   # 5min soft, 1hr hard
    "invoices": {"soft_ttl_s": 900,  "hard_ttl_s": 3600},   # 15min soft, 1hr hard
    "balances": {"soft_ttl_s": 120,  "hard_ttl_s": 600},    # 2min soft, 10min hard
}
```

## Architecture Patterns

### Pattern 1: User Actions (Smart Sync Pattern)
```python
# Runway Service → Domain Gateway → Infra Gateway → Sync Orchestrator
@router.get("/snapshot")
async def get_snapshot(advisor_id: str = Depends(get_advisor_id), business_id: str = Depends(get_business_id)):
    # Composition root creates service with proper gateways
    console_service = create_console_service(advisor_id, business_id)
    snapshot = await console_service.get_snapshot()
    return {"status": "success", "snapshot": snapshot, "runway_impact": "+2 days"}

# Domain Gateway Interface (Advisor-First Model)
class BillsGateway(Protocol):
    def list(self, q: ListBillsQuery) -> List[Bill]: ...
    # Note: Bill payment scheduling handled by Ramp rail (future), not QBO

# Infra Gateway Implementation (Concrete Sync Orchestrator Interface)
class QBOBillsGateway(BillsGateway):
    def __init__(self, qbo_client: QBOClient, sync: SyncOrchestrator, log: LogRepo, mirror: BillsMirrorRepo):
        self.qbo = qbo_client
        self.sync = sync
        self.log = log
        self.mirror = mirror

    def list(self, q: ListBillsQuery) -> List[Bill]:
        return self.sync.read_refresh(
            entity="bills",
            client_id=q.advisor_id,  # advisor_id is primary identifier
            hint=q.freshness_hint,
            mirror_is_fresh=lambda e, c, p: self.mirror.is_fresh(q.advisor_id, q.business_id, p),
            fetch_remote=lambda: self.qbo.list_bills(company_id=q.business_id, status=q.status),
            upsert_mirror=lambda raw, ver, ts: self.mirror.upsert_many(q.advisor_id, q.business_id, raw, ver, ts),
            read_from_mirror=lambda: self.mirror.list_open(q.advisor_id, q.business_id),
            on_hygiene=lambda c, code: self.log.flag_hygiene(c, code)
        )

    # Note: QBO BillsGateway only handles read operations
    # Bill payment scheduling will be handled by Ramp gateway (future rail)
    # QBO is the ledger hub - we read bills from QBO, but payments go through Ramp
```

### Pattern 2: Background Syncs (Smart Sync Pattern)
```python
# Runway Service → Domain Gateway → Infra Gateway → Sync Orchestrator
class ConsoleService:
    def __init__(self, bills_gateway: BillsGateway, balances_gateway: BalancesGateway):
        self.bills = bills_gateway
        self.balances = balances_gateway
    
    def snapshot(self, client_id: str):
        # Uses domain gateways with Smart Sync pattern
        bills = self.bills.list(ListBillsQuery(client_id=client_id, freshness_hint="CACHED_OK"))
        balances = self.balances.get(BalancesQuery(client_id=client_id, freshness_hint="STRICT"))
        
        return {
            "bills": bills,
            "balances": balances,
            "runway_days": self.calculate_runway_days(balances, bills)
        }

# Infra Gateway with Smart Sync
class QBOBillsGateway(BillsGateway):
    def list(self, q: ListBillsQuery) -> list[Bill]:
        # Smart Sync: Check freshness, decide DB vs API
        if self.sync.is_fresh("bills", q.client_id) and q.freshness_hint == "CACHED_OK":
            return self.mirror.list_open(q.client_id)
        
        # API fallback: Call QBO, log, update mirror
        raw, version = self.qbo.list_bills(company_id=q.client_id, status=q.status)
        self.log.append(direction="INBOUND", rail="qbo", operation="list_bills",
                        client_id=q.client_id, payload_json=json.dumps(raw), source_version=version)
        self.mirror.upsert_many(q.client_id, raw, source_version=version, synced_at=self.sync.now())
        return self.mirror.list_open(q.client_id)
```

### Pattern 3: Event-Triggered Reconciliation
```python
# Post-action syncs for data consistency
class SmartSyncService:
    async def schedule_reconciliation(self, action_type: str, entity_id: str):
        job_id = f"reconcile:{action_type}:{entity_id}"
        await self.redis_job_queue.enqueue(job_id, self.reconcile_action, args=(action_type, entity_id))
    
    async def reconcile_action(self, action_type: str, entity_id: str):
        qbo_client = QBOUserActionService(self.business_id)
        qbo_status = await qbo_client.get_status(action_type, entity_id)
        if qbo_status != await self.db.get_local_status(action_type, entity_id):
            await self.db.update_action_status(entity_id, qbo_status)
            await self.notify_drift(action_type, entity_id, "Status mismatch detected")
```

## Service Architecture

### Dependency Direction
```
Runway Service → Domain Gateway Interface → Infra Gateway Implementation → Sync Orchestrator → QBO API
```

### Service Responsibilities & Patterns

#### Sync Orchestrator (infra/sync/)
**Pattern**: Smart Sync + Transaction Log + State Mirror
**Responsibilities**: Freshness checks, retry logic, transaction logging, state mirror updates
```python
class SyncOrchestrator:
    def __init__(self, client_id: str, log_repo: LogRepo, mirror_repo: MirrorRepo):
        self.client_id = client_id
        self.log = log_repo
        self.mirror = mirror_repo
    
    # Smart Sync methods
    def is_fresh(self, entity_type: str, client_id: str) -> bool
    def now(self) -> datetime
    
    # Transaction logging
    def log_inbound(self, rail: str, operation: str, client_id: str, payload: dict, version: str) -> str
    def log_outbound(self, rail: str, operation: str, client_id: str, payload: dict) -> str
    
    # State mirror management
    def upsert_mirror(self, entity_type: str, client_id: str, data: list, version: str, synced_at: datetime) -> None
    def get_mirror(self, entity_type: str, client_id: str, filters: dict) -> list
```

#### QBO Client (infra/rails/qbo/)
**Pattern**: Raw HTTP Client + Adapter
**Responsibilities**: Make raw HTTP calls, handle QBO authentication, return raw responses
```python
class QBOClient:
    def __init__(self, client_id: str, realm_id: str)
    
    # Raw QBO API methods
    async def list_bills(self, company_id: str, status: str) -> tuple[list, str]  # (data, version)
    async def list_invoices(self, company_id: str, status: str) -> tuple[list, str]
    async def schedule_payment(self, bill_id: str, amount: Decimal, pay_on: date) -> dict
    async def get_company_info(self, company_id: str) -> dict
```

#### Domain Gateways (domains/*/gateways.py)
**Pattern**: Protocol Interface + Rail-Agnostic
**Responsibilities**: Define rail-agnostic business interfaces
```python
class BillsGateway(Protocol):
    def list(self, q: ListBillsQuery) -> List[Bill]: ...
    def schedule_payment(self, client_id: str, bill_id: str, amount: Decimal, pay_on: date) -> str: ...

class BalancesGateway(Protocol):
    def get(self, q: BalancesQuery) -> Balance: ...
```

#### Infra Gateways (infra/gateways/)
**Pattern**: Gateway Implementation + Rail-Specific
**Responsibilities**: Implement domain gateways with rail-specific logic and Smart Sync
```python
class QBOBillsGateway(BillsGateway):
    def __init__(self, qbo_client: QBOClient, sync: SyncOrchestrator, log: LogRepo, mirror: BillsMirrorRepo):
        self.qbo = qbo_client
        self.sync = sync
        self.log = log
        self.mirror = mirror
    
    def list(self, q: ListBillsQuery) -> List[Bill]:
        # Smart Sync pattern implementation
        if self.sync.is_fresh("bills", q.client_id) and q.freshness_hint == "CACHED_OK":
            return self.mirror.list_open(q.client_id)
        
        raw, version = self.qbo.list_bills(company_id=q.client_id, status=q.status)
        self.log.append(direction="INBOUND", rail="qbo", operation="list_bills",
                        client_id=q.client_id, payload_json=json.dumps(raw), source_version=version)
        self.mirror.upsert_many(q.client_id, raw, source_version=version, synced_at=self.sync.now())
        return self.mirror.list_open(q.client_id)
```

## QBO Fragility Handling

| Issue | Pattern | Mechanism | UX Impact |
|-------|---------|-----------|-----------|
| **Rate Limiting** (500/min, 100/sec) | **Token Bucket** | SyncTimingManager tracks usage, prioritizes user actions | Users don't notice; actions complete instantly or queue transparently |
| **Transient Failures** (503) | **Circuit Breaker + Retry** | execute_with_retry with exponential backoff (1s, 2s, 4s) | Users see instant results or graceful fallbacks |
| **Duplicate Actions** | **Idempotency Key** | IdentityGraph hashes action payloads to check prior execution | Prevents duplicate payments, maintains trust |
| **Lost Actions** | **Eventual Consistency** | schedule_reconciliation verifies QBO status post-action | Ensures runway calculations reflect QBO reality |
| **Data Inconsistencies** | **Cache-Aside + TTL** | SyncCache stores recent data; periodic reconciliation and drift alerts | Users see consistent data; drift alerts maintain trust |

## Implementation Guidelines

### User Action Flow
1. User clicks action (e.g., "Pay Bill")
2. Route calls domain service
3. Domain service calls SmartSyncService for orchestration
4. SmartSyncService calls QBORawClient for HTTP call
5. QBORawClient makes raw HTTP call to QBO
6. Domain service handles business logic and updates local database
7. Return immediate response
8. Schedule background reconciliation

### Background Sync Flow
1. Domain service calls SmartSyncService for orchestration
2. SmartSyncService checks timing rules and cache validity
3. Use cached data if available
4. If needed, SmartSyncService calls QBORawClient for HTTP call
5. QBORawClient makes raw HTTP call to QBO
6. SmartSyncService caches results with appropriate TTL
7. Domain service processes data and updates local database

### Error Handling Strategy
- **User Actions**: Fail fast with cached fallback, show retry options
- **Background Syncs**: Queue retries, use cached data, notify of issues
- **Critical Failures**: Alert users, maintain audit trail, enable manual intervention

## Success Metrics
- **Response Time**: <300ms for user actions
- **Reliability**: 99.9% success rate for critical operations
- **Data Consistency**: <5% drift between QBO and local database
- **User Trust**: 90%+ confidence in runway calculations
- **Error Prevention**: Zero duplicate payments or financial errors

## Circular Dependency Prevention

**CRITICAL PRINCIPLE**: Infrastructure modules must NEVER directly import or query domain models from `domains/` packages.

### Anti-Patterns & Solutions

| Anti-Pattern | Solution | Pattern |
|--------------|----------|---------|
| **Infrastructure querying domain models** | **Parameter-based data access** | Domain services pass data as parameters |
| **Direct domain model imports in infra/** | **DTOs for data transfer** | Use DTOs instead of domain models |
| **Circular import chains** | **Lazy initialization** | Import dependencies at runtime |

### Architecture Flow
```
Domain Services → Query Models → Pass Data → Infrastructure Services → External APIs
     ↑                                                                        ↓
Domain Services ← Update Models ← Process Results ← Infrastructure Services ←
```

### Implementation Rules
1. **Infrastructure modules** (`infra/`): Raw HTTP clients, orchestration services, DTOs only
2. **Domain modules** (`domains/`): Business models, business logic services, data persistence
3. **Data flow**: Domain services query models → pass data to infrastructure → process results → update models

### Verification
```bash
# Check for domain imports in infrastructure (should return no results)
grep -r "from domains\." infra/
grep -r "import domains\." infra/
```

## Multi-Rail Architecture

This ADR establishes the pattern for QBO-specific orchestration. For multi-rail support, each integration rail will have its own SmartSyncService variant:

### Rail-Specific Orchestration Design

**Decision**: Each integration rail (QBO, Ramp, Plaid, Stripe) will have its own SmartSyncService variant rather than a generic service.

**Rationale**: Different APIs have fundamentally different orchestration requirements:

| Rail | Rate Limiting | Retry Logic | Caching | Activity Tracking |
|------|---------------|-------------|---------|-------------------|
| **QBO** | 500 req/min, 100 req/sec | Exponential backoff | 240min TTL | User action patterns |
| **Ramp** | Different limits | Ramp-specific errors | Card-specific patterns | Ramp user activity |
| **Plaid** | Plaid limits | Webhook-based | Account-specific | Plaid sync patterns |
| **Stripe** | Stripe limits | Stripe error handling | Payment-specific | Stripe activity |

### Implementation Pattern

```python
# Each rail has its own orchestration service
class SmartSyncService:           # QBO-specific
class RampSmartSyncService:       # Ramp-specific  
class PlaidSmartSyncService:      # Plaid-specific
class StripeSmartSyncService:     # Stripe-specific

# Domain services use the appropriate rail service
await qbo_smart_sync.get_bills()      # QBO orchestration
await ramp_smart_sync.get_cards()     # Ramp orchestration
await plaid_smart_sync.get_accounts() # Plaid orchestration
await stripe_smart_sync.get_payments() # Stripe orchestration
```

### Benefits

1. **Rail-Specific Optimization**: Each service optimized for its API characteristics
2. **Independent Evolution**: Rails can evolve independently without affecting others
3. **Clear Separation**: Each rail's orchestration logic is self-contained
4. **Consistent Interface**: All rails provide similar high-level methods to domain services

## Smart Sync Pattern Specification

*The correct architecture pattern that connects domain gateways, infra gateways, sync orchestrator, transaction logs, and state mirror tables*

### **The Smart Sync Pattern (Correct Implementation)**

#### **What Should Happen**
```
Runway Service → Domain Gateway (interface) → Infra Gateway (impl) → Sync Orchestrator → Rail API
                                                      ↓
                                              Transaction Log ← Mirror DB
```

#### **The Smart Switching Logic**
1. **Runway Service** calls domain gateway interface (e.g., `BillsGateway.list()`)
2. **Infra Gateway** checks if local data is fresh enough via Sync Orchestrator
3. **If fresh**: Return data from State Mirror (fast)
4. **If stale**: Call Rail API, log INBOUND transaction, update State Mirror, return fresh data
5. **Transaction Log**: Record all data changes for audit trail and replayability

### **Current Broken Implementation (What We're Fixing)**

#### **Current Reality**
```
BillService.get_bills_due_in_days() → Direct DB Query (bypasses sync service)
QBOSyncService.get_bills_by_due_days() → Direct API Call (no smart switching)
DataOrchestrator → Direct QBOSyncService calls (wrong pattern)
```

#### **The Disconnect**
- **Domain services** do their own database queries (bypass sync)
- **QBOSyncService** just does raw API calls (no smart switching)
- **Data orchestrators** call sync service directly (wrong layer)
- **No connection** between domain services and sync orchestrator
- **Transaction logs** not integrated with the switching logic

### **Key Architectural Principles**

#### **1. Domain Gateways (Interfaces)**
- **Location**: `domains/*/gateways.py`
- **Purpose**: Rail-agnostic business interfaces
- **Dependencies**: None (pure interfaces)
- **Examples**: `BillsGateway`, `BalancesGateway`, `InvoicesGateway`

#### **2. Infra Gateways (Implementations)**
- **Location**: `infra/gateways/`
- **Purpose**: Rail-specific implementations of domain gateways
- **Dependencies**: Sync Orchestrator, Rail Clients, Transaction Log, State Mirror
- **Examples**: `QBOBillsGateway`, `RampBillsGateway`, `PlaidBalancesGateway`

#### **3. Sync Orchestrator (Centralized Logic)**
- **Location**: `infra/sync/orchestrator.py`
- **Purpose**: Centralized sync logic, freshness checks, transaction logging
- **Dependencies**: Transaction Log, State Mirror
- **Examples**: `SyncOrchestrator`

#### **4. Runway Services (Orchestration)**
- **Location**: `runway/services/`
- **Purpose**: Product-specific orchestration using domain gateways
- **Dependencies**: Domain Gateway interfaces only
- **Examples**: `TrayService`, `ConsoleService`

#### **5. Composition Root (Dependency Injection)**
- **Location**: `runway/wiring.py`
- **Purpose**: Single place where domain interfaces are bound to infra implementations
- **Dependencies**: All infra implementations
- **Examples**: `create_tray_service()`, `create_console_service()`

### **The Real Fix Needed**

1. **Create Domain Gateways** - Define rail-agnostic interfaces in domains
2. **Create Infra Gateways** - Implement domain gateways with Smart Sync pattern
3. **Create Sync Orchestrator** - Centralized sync logic with transaction logging
4. **Update Runway Services** - Use domain gateways instead of direct calls
5. **Create Composition Root** - Single place for dependency injection
6. **Deprecate Data Orchestrators** - Replace with domain gateway pattern

### **Success Criteria**

- [ ] Domain gateways provide rail-agnostic interfaces
- [ ] Infra gateways implement Smart Sync pattern
- [ ] Sync orchestrator centralizes all sync logic
- [ ] Transaction log captures all data changes
- [ ] State mirror provides fast local reads
- [ ] Runway services use domain gateways only
- [ ] Composition root handles all dependency injection
- [ ] No direct rail calls from runway services
- [ ] No direct sync calls from domain services

## References

- [ADR-001: Domains/Runway Separation](./ADR-001-domains-runway-separation.md)
- [ADR-003: Multi-Tenancy Strategy](./ADR-003-multi-tenancy-strategy.md)
- [ADR-007: Service Boundaries](./ADR-007-service-boundaries.md)
- [ADR-010: Multi-Rail Financial Control Plane](./ADR-010-multi-rail-financial-control-plane.md)