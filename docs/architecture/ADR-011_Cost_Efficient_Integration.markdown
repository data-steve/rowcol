# ADR-011: Cost-Efficient Integration for Multi-Rail APIs

**Date**: 2025-10-06  
**Status**: Draft  
**Decision**: Optimize multi-rail API integrations (QBO, Ramp, Plaid, Stripe) using event-driven syncs, caching, and selective polling to minimize Plaid's per-account costs and QBO's rate limits while supporting 100-client portfolios.

> **Code Alignment Note**: This ADR uses **suggestive code examples** that demonstrate the architectural pattern. The actual implementation should leverage existing `infra/jobs/` infrastructure (`SyncCache`, `SyncTimingManager`) and generalize `SmartSyncService` beyond QBO to handle Ramp and Plaid integrations.

## Context
RowCol’s Financial Control Plane integrates QBO (ledger), Ramp (execution), Plaid (cash balances), and Stripe (CSV A/R) to automate cash discipline for CAS 2.0 firms. Plaid’s per-account fees ($0.50–$1.00/month per linked account) are the primary cost driver, while QBO’s 500/min rate limit and Ramp’s partnership-based limits require careful management to avoid throttling. Inefficient polling (e.g., frequent Plaid balance checks) or redundant API calls could inflate costs and degrade performance, impacting scalability for 20–100 client portfolios. The architecture must prioritize cost-efficient integration patterns to maintain high margins while ensuring reliability.

## Decision
Implement cost-efficient integration using event-driven syncs (Ramp webhooks, Plaid refresh-on-demand), aggressive caching (e.g., Redis for QBO/Plaid data), and selective polling to minimize API costs and respect rate limits. Internal services will optimize data retrieval and storage to reduce external API calls.

### Key Patterns
- **Event-Driven Syncs**: Use webhooks and on-demand refreshes to reduce polling.
- **Cached Data Access**: Cache QBO/Plaid data to minimize repeated API calls.

## Architecture Patterns

### Pattern 1: Event-Driven Syncs

**Implementation** (suggestive - should leverage existing infrastructure):
```python
# SUGGESTIVE: This pattern should use existing infra/jobs/ infrastructure
class IntegrationService:
    def __init__(self, business_id: str, db_session):
        self.business_id = business_id
        self.db_session = db_session
        
        # Use existing infrastructure
        from infra.jobs.job_storage import SyncCache, get_job_storage_provider
        from infra.jobs.sync_strategies import SyncTimingManager
        from infra.qbo.smart_sync import SmartSyncService  # TODO: generalize beyond QBO
        
        self.cache = SyncCache(business_id)
        self.job_storage = get_job_storage_provider(business_id)
        self.timing_manager = SyncTimingManager(business_id)
        self.smart_sync = SmartSyncService(business_id, "", db_session)

    async def handle_ramp_webhook(self, webhook_data):
        bill_id = webhook_data["bill_id"]
        business_id = webhook_data["business_id"]
        
        # Use existing deduplication via job storage
        idempotency_key = f"ramp_webhook:{bill_id}:{business_id}"
        existing_job = self.job_storage.get_job_by_idempotency_key(idempotency_key)
        if existing_job:
            return  # Idempotent
        
        # Store webhook as job for tracking
        job_data = {
            "id": f"ramp_webhook_{bill_id}_{business_id}",
            "idempotency_key": idempotency_key,
            "status": "processing",
            "webhook_data": webhook_data,
            "created_at": datetime.utcnow().isoformat()
        }
        self.job_storage.save_job(job_data)
        
        if webhook_data["status"] == "paid":
            await self.notify_verification_service(business_id, bill_id)

    async def refresh_plaid_balance(self, business_id, force=False):
        # Use existing cache infrastructure
        cache_key = f"plaid_balance_{business_id}"
        if not force and self.cache.is_valid("plaid"):
            cached_balance = self.cache.get("plaid", cache_key)
            if cached_balance:
                return cached_balance
        
        # Use existing Plaid integration (infra/plaid/consolidate.py)
        balance = await self._get_plaid_balance(business_id)
        self.cache.set("plaid", cache_key, balance, ttl_minutes=60)  # 1-hour TTL
        return balance
```

**Characteristics**:
- ✅ Minimizes Plaid API calls with refresh-on-demand.
- ✅ Handles Ramp webhooks idempotently to avoid redundant processing.

### Pattern 2: Cached Data Access

**Implementation** (suggestive - should leverage existing infrastructure):
```python
# SUGGESTIVE: This pattern should use existing infra/jobs/ infrastructure
class CacheService:
    def __init__(self, business_id: str):
        self.business_id = business_id
        
        # Use existing infrastructure
        from infra.jobs.job_storage import SyncCache
        from infra.jobs.sync_strategies import SyncTimingManager
        from infra.qbo.smart_sync import SmartSyncService  # TODO: generalize
        
        self.cache = SyncCache(business_id)
        self.timing_manager = SyncTimingManager(business_id)
        self.smart_sync = SmartSyncService(business_id, "", None)

    async def get_bill(self, bill_id):
        # Use existing cache infrastructure
        cache_key = f"qbo_bill_{bill_id}"
        cached = self.cache.get("qbo", cache_key)
        if cached:
            return cached
        
        # Use existing QBO integration
        bill = await self.smart_sync.execute_qbo_call("get_bill", bill_id=bill_id)
        self.cache.set("qbo", cache_key, bill, ttl_minutes=1440)  # 24-hour TTL
        return bill

    async def batch_get_bills(self, bill_ids):
        # Use existing cache infrastructure for batch operations
        cached_bills = {}
        to_fetch = []
        
        for bill_id in bill_ids:
            cache_key = f"qbo_bill_{bill_id}"
            cached = self.cache.get("qbo", cache_key)
            if cached:
                cached_bills[bill_id] = cached
            else:
                to_fetch.append(bill_id)
        
        if to_fetch:
            # Use existing QBO integration for batch fetch
            fetched = await self.smart_sync.execute_qbo_call("batch_get_bills", bill_ids=to_fetch)
            for bill_id, bill in fetched.items():
                cache_key = f"qbo_bill_{bill_id}"
                self.cache.set("qbo", cache_key, bill, ttl_minutes=1440)  # 24-hour TTL
                cached_bills[bill_id] = bill
        
        return cached_bills
```

**Characteristics**:
- ✅ Reduces QBO API calls with Redis caching.
- ✅ Supports batch operations to stay within rate limits.

## Implementation Guidelines

### When to Use This Pattern:
- When integrating with cost-sensitive APIs (e.g., Plaid) or rate-limited APIs (e.g., QBO).
- When scaling to 100 clients with frequent data syncs (e.g., weekly cash runway rituals).

### Code Organization:
```
# SUGGESTIVE: Should leverage existing infrastructure
runway/services/
├── integration_service.py          # Event-driven syncs (NEW)
└── cache_service.py                # Cached data access (NEW)

# EXISTING INFRASTRUCTURE TO LEVERAGE:
infra/jobs/
├── job_storage.py                 # ✅ EXISTS - SyncCache, JobStorageProvider
├── sync_strategies.py             # ✅ EXISTS - SyncTimingManager
└── enums.py                       # ✅ EXISTS - SyncStrategy, SyncPriority

infra/qbo/
├── smart_sync.py                  # ✅ EXISTS - SmartSyncService (TODO: generalize)
└── client.py                      # ✅ EXISTS - QBO API client

infra/plaid/
└── consolidate.py                 # ✅ EXISTS - Plaid balance client

# TODO: Implement Ramp integration
infra/ramp/
└── adapter.py                     # TODO: Ramp webhook client
```

### Required Patterns:
```python
# SUGGESTIVE: This pattern should leverage existing SmartSyncService
class BaseIntegrationClient:
    def __init__(self, business_id: str, platform: str):
        self.business_id = business_id
        self.platform = platform
        
        # Use existing infrastructure
        from infra.jobs.job_storage import SyncCache
        from infra.jobs.sync_strategies import SyncTimingManager
        from infra.qbo.smart_sync import SmartSyncService  # TODO: generalize
        
        self.cache = SyncCache(business_id)
        self.timing_manager = SyncTimingManager(business_id)
        self.smart_sync = SmartSyncService(business_id, "", None)
    
    async def call_api(self, endpoint, method, data=None):
        # Use existing SmartSyncService orchestration
        return await self.smart_sync.execute_qbo_call(
            f"{self.platform}_{endpoint}",
            method=method,
            data=data
        )
```

## Benefits

### Positive Outcomes
✅ **Cost Efficiency**: Reduces Plaid API calls, keeping per-account costs low (~$1–$3/client/month).  
✅ **Scalability**: Manages QBO’s 500/min rate limit with batching and caching.

### Business Value
- Maintains high margins by minimizing API costs for 100-client portfolios.
- Enhances advisor trust with reliable, low-latency data syncs.

## Consequences

**Positive**: Lower operational costs and improved performance.  
**Negative**: Cache management adds complexity to state consistency.

**Risks & Mitigations**:
- **Risk**: Cache staleness leads to outdated balances.  
  **Mitigation**: Use short TTLs (e.g., 1 hour for Plaid balances) and force refresh on advisor action.
- **Risk**: Webhook delays disrupt verification.  
  **Mitigation**: Fallback to periodic QBO checks with cached data.

## Success Metrics
- **Plaid API Calls**: <1 balance call/client/week on average.
- **QBO Rate Limit Usage**: <50% of 500/min limit during peak load.

## Implementation Notes

### **Existing Infrastructure to Leverage**
- ✅ `infra/jobs/job_storage.py` - SyncCache, JobStorageProvider for caching and deduplication
- ✅ `infra/jobs/sync_strategies.py` - SyncTimingManager for intelligent sync timing
- ✅ `infra/jobs/enums.py` - SyncStrategy, SyncPriority enums
- ✅ `infra/qbo/smart_sync.py` - SmartSyncService (needs generalization beyond QBO)
- ✅ `infra/plaid/consolidate.py` - Plaid integration

### **TODO: Generalize SmartSyncService**
The existing `SmartSyncService` is QBO-specific but should be generalized to handle:
- Ramp webhook processing
- Plaid balance fetching with cost optimization
- Stripe CSV processing
- Multi-rail rate limiting and caching

### **TODO: Implement Missing Components**
- `infra/ramp/adapter.py` - Ramp webhook client
- `runway/services/integration_service.py` - Event-driven sync orchestration
- `runway/services/cache_service.py` - Cached data access patterns

## Related ADRs
- **ADR-005**: Orchestration Layer (centralizes API coordination for cost efficiency).
- **ADR-010**: Chain of Custody (leverages event-driven syncs for verification).

**Last Updated**: 2025-10-06  
**Next Review**: 2026-01-06