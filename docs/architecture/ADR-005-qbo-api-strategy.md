# ADR-005: QBO API Strategy

**Date**: 2025-01-27  
**Status**: Accepted  
**Decision**: Use SmartSyncService as orchestration layer for QBO fragility while enabling immediate user actions.

## Context

QBO API has well-documented fragility that can disrupt the cash runway ritual:
- **Rate Limiting**: 500 requests/min per app, 100 requests/sec per realm
- **Intermittent Failures**: 503 Service Unavailable, network latency, maintenance windows
- **Duplicate Actions**: Retrying failed requests can create duplicate transactions
- **Lost Actions**: QBO's async processing can make actions appear to fail when they succeeded
- **Data Inconsistencies**: QBO data may not reflect real-time changes

**Note**: Current implementation is QBO-specific. Future multi-rail architecture will use rail-specific SmartSyncService variants rather than a generic service, as each integration rail has fundamentally different orchestration requirements.

## Decision

**SmartSyncService as Orchestration Layer**: Domain services handle business logic and CRUD operations, SmartSyncService provides orchestration (retry, dedup, rate limiting, caching), QBORawClient makes raw HTTP calls to QBO endpoints.

### Key Patterns
- **Orchestration Layer Pattern**: SmartSyncService coordinates all QBO interactions
- **Raw HTTP Client Pattern**: QBORawClient makes direct API calls, no business logic
- **Domain Service Pattern**: Business logic + CRUD operations, uses SmartSyncService for orchestration
- **Immediate Response Pattern**: User actions return instantly, background reconciliation ensures consistency

## Architecture Patterns

### Pattern 1: User Actions
```python
# Domain Service → SmartSyncService → Raw QBO HTTP Calls
@router.post("/bills/{bill_id}/pay")
async def pay_bill(bill_id: str, payment_data: PaymentRequest, business_id: str = Depends(get_business_id)):
    bill_service = BillService(db, business_id)
    payment = await bill_service.create_payment(bill_id, payment_data)
    return {"status": "paid", "payment_id": payment.id, "runway_impact": "+2 days"}

class BillService(TenantAwareService):
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.smart_sync = SmartSyncService(business_id, "", db)
    
    async def create_payment(self, bill_id: str, payment_data: PaymentRequest) -> Payment:
        # SmartSyncService handles orchestration (retry, dedup, rate limiting)
        qbo_result = await self.smart_sync.create_payment_immediate({
            "bill_id": bill_id,
            "amount": float(payment_data.amount),
            "payment_date": payment_data.payment_date.isoformat(),
            "payment_method": payment_data.payment_method
        })
        
        # Domain service handles business logic and data persistence
        payment = Payment(
            bill_id=bill_id,
            amount=payment_data.amount,
            payment_date=payment_data.payment_date,
            qbo_payment_id=qbo_result.get("id")
        )
        self.db.add(payment)
        self.db.commit()
        return payment
```

### Pattern 2: Background Syncs
```python
# Domain Service → SmartSyncService → Raw QBO HTTP Calls
class RunwayCalculator(TenantAwareService):
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.smart_sync = SmartSyncService(business_id, "", self.db)
    
    async def calculate_current_runway(self, qbo_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if qbo_data is None:
            qbo_data = await self._get_qbo_data_for_digest()
        
        runway_days = self._calculate_runway_days(qbo_data)
        daily_burn = await self._calculate_daily_burn_rate()
        
        return {
            "runway_days": runway_days,
            "daily_burn": daily_burn,
            "last_updated": datetime.utcnow()
        }
    
    async def _get_qbo_data_for_digest(self) -> Dict[str, Any]:
        # SmartSyncService handles caching, rate limiting, retry logic
        bills = await self.smart_sync.get_bills_by_due_days()
        invoices = await self.smart_sync.get_invoices_by_aging_days()
        company_info = await self.smart_sync.get_company_info()
        
        return {"bills": bills, "invoices": invoices, "company_info": company_info}
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
Domain Service → SmartSyncService → QBORawClient → QBO API
```

### Service Responsibilities & Patterns

#### SmartSyncService (infra/qbo/)
**Pattern**: Orchestration Layer + Circuit Breaker + Cache-Aside
**Responsibilities**: Rate limiting, retry logic, deduplication, caching, reconciliation
```python
class SmartSyncService:
    def __init__(self, business_id: str, realm_id: str, db_session=None)
    
    # QBO orchestration methods
    async def execute_qbo_call(self, operation: str, *args, **kwargs) -> Any
    async def get_bills_by_due_days(self, due_days: int = 30) -> Dict[str, Any]
    async def get_bills_by_date(self, since_date: datetime = None) -> Dict[str, Any]
    async def get_invoices_by_aging_days(self, aging_days: int = 30) -> Dict[str, Any]
    async def get_invoices_by_date(self, since_date: datetime = None) -> Dict[str, Any]
    async def get_customers(self) -> Dict[str, Any]
    async def get_vendors(self) -> Dict[str, Any]
    async def get_accounts(self) -> Dict[str, Any]
    async def get_company_info(self) -> Dict[str, Any]
    async def create_payment_immediate(self, payment_data: Dict) -> Dict[str, Any]
    async def sync_payment_record(self, payment_data: Dict) -> Dict[str, Any]
    
    # Backward compatibility methods
    async def get_bills(self) -> Dict[str, Any]
    async def get_invoices(self) -> Dict[str, Any]
    
    # Caching methods
    def get_cache(self, platform: str, key: Optional[str] = None) -> Optional[Dict]
    def set_cache(self, platform: str, data: Dict, ttl_minutes: Optional[int] = None) -> None
    
    # Timing methods
    def should_sync(self, platform: str, strategy: SyncStrategy) -> bool
    def record_sync(self, platform: str, strategy: SyncStrategy, success: bool = True) -> None
```

#### QBORawClient (infra/qbo/)
**Pattern**: Raw HTTP Client + Adapter
**Responsibilities**: Make raw HTTP calls, handle QBO authentication, return raw responses
```python
class QBORawClient:
    def __init__(self, business_id: str, realm_id: str, db_session=None)
    
    # Raw QBO API methods
    async def get_bills_from_qbo(self, due_days: int = 30) -> Dict[str, Any]
    async def get_invoices_from_qbo(self, aging_days: int = 30) -> Dict[str, Any]
    async def get_customers_from_qbo(self) -> Dict[str, Any]
    async def get_vendors_from_qbo(self) -> Dict[str, Any]
    async def get_accounts_from_qbo(self) -> Dict[str, Any]
    async def get_company_info_from_qbo(self) -> Dict[str, Any]
    async def create_payment_in_qbo(self, payment_data: Dict) -> Dict[str, Any]
    async def get_kpi_data(self) -> Dict[str, Any]
    async def get_aging_report(self) -> Dict[str, Any]
    async def get_payment_history(self, entity_type: str, entity_id: str) -> Dict[str, Any]
```

#### Domain Services (domains/*/services/)
**Pattern**: Domain Service + Repository + TenantAwareService
**Responsibilities**: Business logic, data transformation, CRUD operations, use SmartSyncService for orchestration
```python
class BillService(TenantAwareService):
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.smart_sync = SmartSyncService(business_id, "", db)
    
    # Business logic methods
    async def sync_bills_from_qbo(self, days_back: int = 90) -> List[Bill]
    async def create_payment(self, bill_id: str, payment_data: PaymentRequest) -> Payment
    async def get_bills_due_soon(self, days: int = 30) -> List[Bill]
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

## References

- [ADR-001: Domains/Runway Separation](./ADR-001-domains-runway-separation.md)
- [ADR-003: Multi-Tenancy Strategy](./ADR-003-multi-tenancy-strategy.md)
- [ADR-006: Data Orchestrator Pattern](./ADR-006-data-orchestrator-pattern.md)
- [ADR-007: Service Boundaries](./ADR-007-service-boundaries.md)