# ADR-005: QBO API Strategy - SmartSyncService as Orchestration Layer

**Date**: 2025-01-27  
**Status**: Accepted  
**Decision**: Use SmartSyncService as the central orchestration layer for all QBO interactions, with domain services handling their own CRUD operations and QBORawClient making raw HTTP calls to QBO endpoints.

## Context

Oodaloo's core value proposition is the "weekly cash runway ritual" - a seamless, trustworthy experience where users can make immediate decisions (pay bills, send reminders) with real-time feedback. However, QuickBooks Online (QBO) API has well-documented fragility that can disrupt this experience:

- **Rate Limiting**: 500 requests/min per app, 100 requests/sec per realm
- **Intermittent Failures**: 503 Service Unavailable, network latency, maintenance windows
- **Duplicate Actions**: Retrying failed requests can create duplicate transactions
- **Lost Actions**: QBO's async processing can make actions appear to fail when they succeeded
- **Data Inconsistencies**: QBO data may not reflect real-time changes
- **Webhook Reliability**: Missed events, out-of-order delivery, duplicates

Without proper handling, these issues expose users to:
- Financial errors (duplicate payments, e.g., $10k overpayment)
- User-facing errors (429/503 during "Pay Bill" actions)
- Stale data (outdated runway numbers undermining trust)
- Performance issues (uncontrolled API calls hitting rate limits)

## Decision

**SmartSyncService as Orchestration Layer**: Use SmartSyncService as the central coordinator for all QBO interactions, with domain services handling their own business logic and CRUD operations, and QBORawClient making raw HTTP calls to QBO endpoints.

### Core Principle

The question isn't "SmartSyncService vs direct API calls" - it's "How do we use SmartSyncService to handle QBO's fragility while maintaining the UX of immediate user actions?"

**Answer**: SmartSyncService as the orchestration layer that handles retries, deduplication, rate limiting, and caching, while domain services handle their own business logic and QBORawClient makes raw HTTP calls to QBO endpoints.

## Architecture Patterns

### Pattern 1: User Actions (Domain Service → SmartSyncService → Raw QBO HTTP Calls)

For user actions like "Pay Bill" or "Send Reminder," domain services handle business logic and use SmartSyncService for orchestration.

```python
# runway/routes/abills.py
@router.post("/bills/{bill_id}/pay")
async def pay_bill(bill_id: str, payment_data: PaymentRequest, business_id: str = Depends(get_business_id)):
    # Domain service handles business logic
    bill_service = BillService(db, business_id)
    payment = await bill_service.create_payment(bill_id, payment_data)
    return {"status": "paid", "payment_id": payment.id, "runway_impact": "+2 days"}

# domains/ap/services/bill_ingestion.py
class BillService(TenantAwareService):
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.smart_sync = SmartSyncService(business_id, "", db)
    
    async def create_payment(self, bill_id: str, payment_data: PaymentRequest) -> Payment:
        """Create payment - domain handles its own CRUD."""
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

**Key Characteristics**:
- Domain services handle business logic and CRUD operations
- SmartSyncService handles orchestration (retry, dedup, rate limiting, caching)
- QBORawClient makes raw HTTP calls to QBO endpoints
- Immediate user feedback with background reconciliation
- Financial error prevention through deduplication

### Pattern 2: Background Syncs (Domain Service → SmartSyncService → Raw QBO HTTP Calls)

For background tasks like weekly digest generation, domain services use SmartSyncService to coordinate batch data fetches with caching and reconciliation.

```python
# runway/core/runway_calculator.py
class RunwayCalculator(TenantAwareService):
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.smart_sync = SmartSyncService(business_id, "", self.db)
    
    async def calculate_current_runway(self, qbo_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate current runway - domain handles its own business logic."""
        if qbo_data is None:
            qbo_data = await self._get_qbo_data_for_digest()
        
        # Domain service handles business logic and calculations
        runway_days = self._calculate_runway_days(qbo_data)
        daily_burn = await self._calculate_daily_burn_rate()
        
        return {
            "runway_days": runway_days,
            "daily_burn": daily_burn,
            "last_updated": datetime.utcnow()
        }
    
    async def _get_qbo_data_for_digest(self) -> Dict[str, Any]:
        """Get QBO data for digest - SmartSyncService handles orchestration."""
        # SmartSyncService handles caching, rate limiting, retry logic
        bills = await self.smart_sync.get_bills_for_digest()
        invoices = await self.smart_sync.get_invoices_for_digest()
        company_info = await self.smart_sync.get_company_info()
        
        return {
            "bills": bills,
            "invoices": invoices,
            "company_info": company_info
        }
```

**Key Characteristics**:
- Domain services handle business logic and calculations
- SmartSyncService manages timing, caching, rate limits, retry logic
- QBORawClient makes raw HTTP calls to QBO endpoints
- Cached results for instant access
- Periodic reconciliation for data consistency

### Pattern 3: Event-Triggered Reconciliation (Post-Action Syncs)

After user actions, trigger background syncs to ensure data consistency without delaying user response.

```python
# infra/jobs/smart_sync.py
class SmartSyncService:
    async def schedule_reconciliation(self, action_type: str, entity_id: str):
        """Queue background reconciliation for action."""
        job_id = f"reconcile:{action_type}:{entity_id}"
        await self.redis_job_queue.enqueue(
            job_id,
            self.reconcile_action,
            args=(action_type, entity_id)
        )
    
    async def reconcile_action(self, action_type: str, entity_id: str):
        """Verify action status with QBO."""
        qbo_client = QBOUserActionService(self.business_id)
        qbo_status = await qbo_client.get_status(action_type, entity_id)
        if qbo_status != await self.db.get_local_status(action_type, entity_id):
            await self.db.update_action_status(entity_id, qbo_status)
            await self.notify_drift(action_type, entity_id, "Status mismatch detected")
```

**Key Characteristics**:
- User gets immediate feedback
- Background reconciliation ensures accuracy
- Drift alerts maintain trust
- No interruption to user experience

## Service Architecture

### **Dependency Direction**
```
Domain Service → SmartSyncService → QBORawClient → QBO API
```

**Domain Services** handle business logic and CRUD operations, **SmartSyncService** provides orchestration, and **QBORawClient** makes raw HTTP calls. This pattern ensures:
- Single responsibility: Domain services handle business logic, SmartSyncService handles orchestration, QBORawClient handles HTTP calls
- Clean interfaces: Domain services only need to import SmartSyncService
- Reusability: SmartSyncService can be used by other integrations (Plaid, Stripe, etc.)
- Consistency: All QBO operations get the same orchestration behavior
- Testability: Each layer can be tested independently

### **Service Responsibilities**

#### SmartSyncService (infra/qbo/)
**Purpose**: Central orchestration layer for ALL QBO interactions
**Responsibilities**:
- Rate limit management and prioritization
- Retry logic with exponential backoff  
- Deduplication to prevent duplicate actions
- Caching and data consistency management
- User activity tracking for sync timing
- Background reconciliation scheduling
- Error handling and fallback strategies
- QBO-specific orchestration methods

**Interface**:
```python
class SmartSyncService:
    def __init__(self, business_id: str, realm_id: str, db_session=None)
    
    # QBO orchestration methods
    async def execute_qbo_call(self, operation: str, *args, **kwargs) -> Any
    async def get_bills_for_digest(self) -> List[Dict[str, Any]]
    async def get_invoices_for_digest(self) -> List[Dict[str, Any]]
    async def get_company_info(self) -> Dict[str, Any]
    async def create_payment_immediate(self, payment_data: Dict) -> Dict[str, Any]
    async def record_payment(self, payment_data: Dict) -> Dict[str, Any]
    
    # Caching methods
    def get_cache(self, platform: str, key: Optional[str] = None) -> Optional[Dict]
    def set_cache(self, platform: str, data: Dict, ttl_minutes: Optional[int] = None) -> None
    
    # Timing methods
    def should_sync(self, platform: str, strategy: SyncStrategy) -> bool
    def record_sync(self, platform: str, strategy: SyncStrategy, success: bool = True) -> None
```

#### QBORawClient (infra/qbo/)
**Purpose**: Raw HTTP client for QBO API calls
**Responsibilities**:
- Make raw HTTP calls to QBO endpoints
- Handle QBO-specific authentication
- Return raw QBO API responses
- No business logic, no orchestration, just HTTP calls

**Interface**:
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
**Purpose**: Handle business logic and CRUD operations
**Responsibilities**:
- Business logic and rules
- Data transformation and validation
- CRUD operations on domain models
- Use SmartSyncService for QBO orchestration
- Handle user workflows and business processes

**Interface**:
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

### **API Call Categorization**

#### **1. User Actions (Immediate Response <300ms)**
**Pattern**: `Route → Domain Service → SmartSyncService → QBORawClient → QBO API`
**Examples**: 
- Bill approval: `POST /bills/{bill_id}/approve`
- Payment execution: `POST /payments/{payment_id}/execute`
- Invoice reminders: `POST /invoices/{invoice_id}/send-reminder`

**Characteristics**:
- User-triggered actions requiring immediate feedback
- Financial operations that need deduplication
- Operations that affect cash runway calculations
- Domain services handle business logic and CRUD
- SmartSyncService handles retry, deduplication, rate limiting
- QBORawClient makes raw HTTP calls to QBO

#### **2. Data Fetching (For Calculations and Dashboards)**
**Pattern**: `Route/Experience → Domain Service → SmartSyncService → QBORawClient → QBO API`
**Examples**:
- Dashboard data: `GET /dashboard`, `GET /operational`
- Tray items: `TrayService.get_tray_items()`
- KPI calculations: `KPIService.get_cash_flow_kpis()`

**Characteristics**:
- Data needed for calculations, dashboards, analysis
- Can be cached for performance
- Domain services handle business logic and data transformation
- SmartSyncService handles caching, rate limiting, retry logic
- QBORawClient makes raw HTTP calls to QBO

#### **3. Bulk Operations (Background Processing)**
**Pattern**: `Background Job → Domain Service → SmartSyncService → QBORawClient → QBO API`
**Examples**:
- Digest generation: `POST /digest/send-all`
- Batch payments: `POST /payments/batch-execute`
- Analytics data collection

**Characteristics**:
- Background operations that can be queued
- Batch processing for efficiency
- Domain services handle business logic and data processing
- SmartSyncService handles timing, rate limiting, retry logic
- QBORawClient makes raw HTTP calls to QBO

#### **4. Health Checks (Direct API Calls)**
**Pattern**: `Route → Domain Service → QBORawClient → QBO API` (No SmartSyncService)
**Examples**:
- QBO connection status: `GET /qbo_setup/{business_id}/health`
- API availability checks

**Characteristics**:
- Direct API calls for health/status checks
- No orchestration needed
- Immediate response required
- Used for monitoring and diagnostics

## QBO Fragility Handling

### Rate Limiting (500/min, 100/sec)
- **Mechanism**: SyncTimingManager tracks API usage, prioritizing user actions
- **Implementation**: Check limits before proceeding, queue non-critical operations
- **UX Impact**: Users don't notice rate limits; actions complete instantly or queue transparently

### Transient Failures (e.g., 503)
- **Mechanism**: execute_with_retry uses exponential backoff (1s, 2s, 4s) for up to 3 attempts
- **Implementation**: Fallback to cached data for user actions; queue retries for syncs
- **UX Impact**: Users see instant results or graceful fallbacks

### Duplicate Actions
- **Mechanism**: IdentityGraph hashes action payloads to check for prior execution
- **Implementation**: Check before processing, prevent financial errors
- **UX Impact**: Prevents duplicate payments, maintains trust

### Lost Actions
- **Mechanism**: schedule_reconciliation verifies QBO status post-action
- **Implementation**: Background verification with local DB updates
- **UX Impact**: Ensures runway calculations reflect QBO reality

### Data Inconsistencies
- **Mechanism**: SyncCache stores recent data; periodic reconciliation and drift alerts
- **Implementation**: 240 min TTL for cached data; drift detection and notification
- **UX Impact**: Users see consistent data; drift alerts maintain trust

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

## Consequences

### Positive
- **Enterprise-grade reliability** for QBO integration
- **Immediate user experience** with <300ms response times
- **Financial error prevention** through deduplication
- **Data consistency** between QBO and local database
- **Scalable architecture** for RowCol multi-tenant platform
- **Trust maintenance** through drift alerts and freshness indicators

### Negative
- **Increased complexity** compared to simple API calls
- **Additional infrastructure** requirements (Redis, job queues)
- **Development overhead** for proper implementation
- **Testing complexity** for fragility scenarios

### Mitigation
- **Comprehensive testing** with QBO sandbox failure simulation
- **Clear documentation** and implementation patterns
- **Monitoring and alerting** for early issue detection
- **Gradual rollout** with beta testing validation

## Alternatives Considered

### Direct API Calls Only
- **Rejected**: Exposes users to QBO fragility, financial errors, poor UX
- **Reason**: Insufficient for production reliability requirements

### Webhook-First Approach
- **Rejected**: QBO webhooks are unreliable, add complexity, not suitable for MVP
- **Reason**: APIs with SmartSyncService provide sufficient reliability

### Microservices Architecture
- **Rejected**: Over-engineering for current scale, adds unnecessary complexity
- **Reason**: SmartSyncService provides adequate separation of concerns

## Implementation Timeline

### Phase 1: Core Infrastructure (20h)
- Create QBORawClient for raw HTTP calls
- Move SmartSyncService to infra/qbo/ with QBO orchestration
- Implement execute_qbo_call with retry, dedup, rate limiting

### Phase 2: Domain Service Updates (15h)
- Update domain services to use SmartSyncService
- Implement business logic and CRUD operations
- Add QBO orchestration calls

### Phase 3: Route Updates (10h)
- Update routes to use domain services
- Remove direct QBO client usage
- Implement reconciliation and drift alerts

### Phase 4: Testing and Validation (15h)
- Test with QBO sandbox failure simulation
- Validate retry and deduplication logic
- Verify UX trust metrics

**Total Effort**: ~60h over 4 weeks

## Success Metrics

- **Response Time**: <300ms for user actions
- **Reliability**: 99.9% success rate for critical operations
- **Data Consistency**: <5% drift between QBO and local database
- **User Trust**: 90%+ confidence in runway calculations
- **Error Prevention**: Zero duplicate payments or financial errors

## Circular Dependency Prevention

### Problem

During implementation, we encountered circular dependency issues where infrastructure modules (`infra/qbo/`) were importing domain models (`domains/core/models/`), creating import cycles that prevented the application from starting.

### Solution: Infrastructure Independence

**CRITICAL PRINCIPLE**: Infrastructure modules must NEVER directly import or query domain models from `domains/` packages.

#### 1. Data Transfer Objects (DTOs)

Use DTOs for data transfer between layers instead of direct domain model access:

```python
# infra/qbo/dtos.py
@dataclass
class QBOIntegrationDTO:
    business_id: str
    status: str
    platform: str = "qbo"
    access_token: Optional[str] = None
    # ... other fields
```

#### 2. Parameter-Based Data Access

Infrastructure services should accept data as parameters rather than querying it:

```python
# ❌ WRONG - Infrastructure querying domain models
async def get_business_health_details(self, business_id: str):
    business = self.db.query(Business).filter(Business.business_id == business_id).first()
    business_name = business.name if business else "Unknown"

# ✅ CORRECT - Infrastructure accepting data as parameters
async def get_business_health_details(self, business_id: str, business_name: str = None, integration_details: Dict[str, Any] = None):
    return {
        "business_id": business_id,
        "business_name": business_name or "Unknown",
        "integration_details": integration_details or {}
    }
```

#### 3. Lazy Initialization for Circular Dependencies

Use lazy initialization to break circular import chains when necessary:

```python
class SmartSyncService:
    def __init__(self, business_id: str, realm_id: str, db_session=None):
        self.qbo_client = None  # Lazy initialization
    
    def _get_qbo_client(self):
        """Lazy initialization to avoid circular imports."""
        if self.qbo_client is None:
            from .client import QBORawClient  # Imported here
            self.qbo_client = QBORawClient(self.business_id, self.realm_id, self.db_session)
        return self.qbo_client
```

### Architecture Flow

```
Domain Services → Query Domain Models → Pass Data to Infrastructure
     ↓
Infrastructure Services → Accept Data as Parameters → Process Data
     ↓
External APIs → Return Results → Domain Services Update Models
```

### Implementation Guidelines

1. **Infrastructure modules** (`infra/`) should only contain:
   - Raw HTTP clients
   - Orchestration services
   - Configuration
   - DTOs for data transfer

2. **Domain modules** (`domains/`) should contain:
   - Business models
   - Business logic services
   - Data persistence operations

3. **Data flow** should be:
   - Domain services query models and pass data to infrastructure
   - Infrastructure services accept data as parameters
   - Results flow back through domain services to update models

### Verification

To verify no circular dependencies exist:

```bash
# Check for domain imports in infrastructure
grep -r "from domains\." infra/
grep -r "import domains\." infra/

# Should return no results
```

## References

- [Oodaloo v4.5 Restructured Build Plan](../dev_plans/Oodaloo_v4.5_Restructured_Build_Plan.md)
- [ADR-001: Domains/Runway Separation](./ADR-001-domains-runway-separation.md)
- [Comprehensive Architecture](./COMPREHENSIVE_ARCHITECTURE.md)
- [QBO API Strategy Analysis](../../API_STRATEGY_ANALYSIS.md)
- [QBO Infrastructure README](../../infra/qbo/README.md)
- [Nuclear Cleanup Plan](../../zzz_fix_backlogs/smart_sync_reset/NUCLEAR_CLEANUP_PLAN.md)
- [Executable Nuclear Tasks](../../zzz_fix_backlogs/smart_sync_reset/0_EXECUTABLE_NUCLEAR_TASKS.md)
