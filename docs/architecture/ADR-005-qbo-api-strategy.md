# ADR-005: QBO API Strategy - SmartSyncService as Orchestration Layer

**Date**: 2025-01-27  
**Status**: Accepted  
**Decision**: Use SmartSyncService as the central orchestration layer for all QBO interactions, handling fragility while enabling immediate user actions through direct API calls.

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

**SmartSyncService as Orchestration Layer**: Use SmartSyncService as the central coordinator for all QBO interactions, handling fragility while enabling immediate user actions through direct API calls.

### Core Principle

The question isn't "SmartSyncService vs direct API calls" - it's "How do we use SmartSyncService to handle QBO's fragility while maintaining the UX of immediate user actions?"

**Answer**: SmartSyncService as the orchestration layer that handles retries, deduplication, rate limiting, and caching, while still allowing direct API calls for user actions.

## Architecture Patterns

### Pattern 1: User Actions (Immediate, Direct API Calls with SmartSyncService Protection)

For user actions like "Pay Bill" or "Send Reminder," use direct QBO API calls wrapped in SmartSyncService's protective mechanisms.

```python
# runway/routes/ap.py
@router.post("/bills/{bill_id}/pay")
async def pay_bill(bill_id: str, payment_data: PaymentRequest, business_id: str = Depends(get_business_id)):
    smart_sync = SmartSyncService(business_id)
    
    # Check rate limits before proceeding
    if not smart_sync.should_sync("qbo", SyncStrategy.USER_ACTION):
        raise HTTPException(status_code=429, detail="Rate limit exceeded, try again shortly")
    
    # Deduplicate to prevent double payments
    if smart_sync.deduplicate_action("payment", bill_id, payment_data.dict()):
        return {"status": "already_processed", "payment_id": bill_id}
    
    # Execute direct QBO API call with retry logic
    qbo_client = QBOUserActionService(business_id)
    payment = await smart_sync.execute_with_retry(
        qbo_client.create_payment,
        payment_data,
        max_attempts=3,
        backoff_factor=2
    )
    
    # Update local DB and record activity
    await smart_sync.update_local_db("payment", bill_id, {"status": "paid", "payment_id": payment.id})
    smart_sync.record_user_activity("bill_payment")
    
    # Trigger background reconciliation
    await smart_sync.schedule_reconciliation("payment", bill_id)
    
    return {"status": "paid", "payment_id": payment.id, "runway_impact": "+2 days"}
```

**Key Characteristics**:
- Direct QBO API calls for immediacy (<300ms response)
- SmartSyncService handles retries, deduplication, rate limiting
- Immediate user feedback with background reconciliation
- Financial error prevention through deduplication

### Pattern 2: Background Syncs (Batch Operations with SmartSyncService)

For background tasks like weekly digest generation, use SmartSyncService to coordinate batch data fetches with caching and reconciliation.

```python
# runway/services/digest.py
async def generate_digest_background(business_id: str) -> DigestSchema:
    smart_sync = SmartSyncService(business_id)
    
    # Check if sync is needed
    if not smart_sync.should_sync("qbo", SyncStrategy.SCHEDULED):
        cached_data = smart_sync.get_cache("qbo")
        if cached_data:
            return DigestService.calculate_runway(cached_data)
    
    # Fetch fresh data with rate limit handling
    qbo_bulk = QBOBulkScheduledService(business_id)
    qbo_data = await smart_sync.execute_with_retry(
        qbo_bulk.get_qbo_data_for_digest,
        max_attempts=3,
        backoff_factor=2
    )
    
    # Cache results and update local DB
    smart_sync.set_cache("qbo", qbo_data, ttl_minutes=240)
    await smart_sync.update_local_db("digest", business_id, qbo_data)
    
    return DigestService.calculate_runway(qbo_data)
```

**Key Characteristics**:
- Batch data fetching for efficiency
- SmartSyncService manages timing, caching, rate limits
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
Service/Route → QBOClient → SmartSyncService → QBO API
```

**QBOClient** is the integration service that internally uses **SmartSyncService** for orchestration. This pattern ensures:
- Single responsibility: QBOClient handles QBO integration, SmartSyncService handles orchestration
- Clean interfaces: Services only need to import QBOClient
- Reusability: SmartSyncService can be used by other integrations (Plaid, Stripe, etc.)
- Consistency: All QBO operations get the same orchestration behavior
- Testability: QBO integration can be tested separately from orchestration logic

### **Service Responsibilities**

#### SmartSyncService (infra/jobs/)
**Purpose**: Central orchestration layer for ALL QBO interactions
**Responsibilities**:
- Rate limit management and prioritization
- Retry logic with exponential backoff  
- Deduplication to prevent duplicate actions
- Caching and data consistency management
- User activity tracking for sync timing
- Background reconciliation scheduling
- Error handling and fallback strategies

**Interface**:
```python
class SmartSyncService:
    def __init__(self, business_id: str)
    
    # Orchestration methods
    async def execute_qbo_operation(self, operation: str, *args, **kwargs) -> Any
    async def execute_qbo_batch_operation(self, operations: List[Dict]) -> Dict[str, Any]
    
    # Caching methods
    def get_cache(self, platform: str, key: Optional[str] = None) -> Optional[Dict]
    def set_cache(self, platform: str, data: Dict, ttl_minutes: Optional[int] = None) -> None
    
    # Timing methods
    def should_sync(self, platform: str, strategy: SyncStrategy) -> bool
    def record_sync(self, platform: str, strategy: SyncStrategy, success: bool = True) -> None
```

#### QBOClient (domains/qbo/)
**Purpose**: QBO integration service that internally uses SmartSyncService for orchestration
**Responsibilities**:
- Provide clean interface for all QBO operations
- Internally use SmartSyncService for orchestration (retry, deduplication, rate limiting, caching)
- Handle QBO-specific data transformations
- Return standardized data structures
- Categorize API calls by type (User Actions, Data Fetching, Bulk Operations, Health Checks)
- Configure SmartSyncService behavior based on API call type

**Interface**:
```python
class QBOClient:
    def __init__(self, business_id: str, realm_id: str, db: Session)
    
    # Data fetching methods
    async def get_bills(self, due_days: int = 30) -> List[Dict[str, Any]]
    async def get_invoices(self, aging_days: int = 30) -> List[Dict[str, Any]]
    async def get_customers(self) -> List[Dict[str, Any]]
    async def get_vendors(self) -> List[Dict[str, Any]]
    async def get_accounts(self) -> List[Dict[str, Any]]
    async def get_company_info(self) -> Dict[str, Any]
    
    # User action methods
    async def create_payment(self, payment_data: Dict) -> Dict[str, Any]
    async def send_reminder(self, invoice_id: str, reminder_data: Dict) -> Dict[str, Any]
    async def approve_bill(self, bill_id: str) -> Dict[str, Any]
    
    # Batch operations
    async def get_all_data_batch(self) -> Dict[str, Any]
    async def execute_batch_operations(self, operations: List[Dict]) -> Dict[str, Any]
    
    # Health check methods
    async def health_check(self) -> Dict[str, Any]
    async def get_status(self) -> Dict[str, Any]
```

### **API Call Categorization**

#### **1. User Actions (Immediate Response <300ms)**
**Pattern**: `Route → QBOClient.user_action_method() → SmartSyncService.execute_qbo_operation() → QBO API`
**Examples**: 
- Bill approval: `POST /bills/{bill_id}/approve`
- Payment execution: `POST /payments/{payment_id}/execute`
- Invoice reminders: `POST /invoices/{invoice_id}/send-reminder`

**Characteristics**:
- User-triggered actions requiring immediate feedback
- Financial operations that need deduplication
- Operations that affect cash runway calculations
- QBOClient internally uses SmartSyncService with high priority and deduplication
- SmartSyncService handles retry, deduplication, rate limiting

#### **2. Data Fetching (For Calculations and Dashboards)**
**Pattern**: `Route/Experience → QBOClient.get_data_method() → SmartSyncService.execute_qbo_operation() → QBO API`
**Examples**:
- Dashboard data: `GET /dashboard`, `GET /operational`
- Tray items: `TrayService.get_tray_items()`
- KPI calculations: `KPIService.get_cash_flow_kpis()`

**Characteristics**:
- Data needed for calculations, dashboards, analysis
- Can be cached for performance
- QBOClient internally uses SmartSyncService with caching enabled
- SmartSyncService handles caching, rate limiting

#### **3. Bulk Operations (Background Processing)**
**Pattern**: `Background Job → QBOClient.batch_method() → SmartSyncService.execute_qbo_batch_operation() → QBO API`
**Examples**:
- Digest generation: `POST /digest/send-all`
- Batch payments: `POST /payments/batch-execute`
- Analytics data collection

**Characteristics**:
- Background operations that can be queued
- Batch processing for efficiency
- QBOClient internally uses SmartSyncService with low priority
- SmartSyncService handles timing, rate limiting, retry logic

#### **4. Health Checks (Direct API Calls)**
**Pattern**: `Route → QBOClient.health_check()` (No SmartSyncService)
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
2. Check rate limits and deduplication
3. Execute direct QBO API call with retry logic
4. Update local database
5. Record user activity
6. Return immediate response
7. Schedule background reconciliation

### Background Sync Flow
1. Check timing rules and cache validity
2. Use cached data if available
3. Fetch fresh data if needed with rate limiting
4. Cache results with appropriate TTL
5. Update local database
6. Process data for consumption

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

### Phase 1: Core SmartSyncService Enhancement (20h)
- Enhance execute_with_retry for user actions and background syncs
- Integrate SyncTimingManager for rate limit tracking
- Add deduplicate_action for all user actions

### Phase 2: Route Updates (15h)
- Update runway routes to use QBOUserActionService wrapped in SmartSyncService
- Implement reconciliation and drift alerts
- Add UI feedback for failed actions

### Phase 3: Testing and Validation (15h)
- Test with QBO sandbox failure simulation
- Validate retry and deduplication logic
- Verify UX trust metrics

**Total Effort**: ~50h over 4 weeks

## Success Metrics

- **Response Time**: <300ms for user actions
- **Reliability**: 99.9% success rate for critical operations
- **Data Consistency**: <5% drift between QBO and local database
- **User Trust**: 90%+ confidence in runway calculations
- **Error Prevention**: Zero duplicate payments or financial errors

## References

- [Oodaloo v4.5 Restructured Build Plan](../dev_plans/Oodaloo_v4.5_Restructured_Build_Plan.md)
- [ADR-001: Domains/Runway Separation](./ADR-001-domains-runway-separation.md)
- [Comprehensive Architecture](./COMPREHENSIVE_ARCHITECTURE.md)
- [QBO API Strategy Analysis](../../API_STRATEGY_ANALYSIS.md)
