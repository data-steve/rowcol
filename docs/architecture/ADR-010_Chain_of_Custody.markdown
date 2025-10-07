# ADR-010: Multi-Rail Financial Control Plane Architecture

**Date**: 2025-01-27  
**Status**: Draft  
**Decision**: Implement hub-and-spoke multi-rail architecture with chain of custody verification loop across RowCol (orchestration), QBO (ledger hub), Ramp (A/P execution), Plaid (cash verification), and Stripe (A/R insights) to enable Financial Control Plane for CAS 2.0 firms.

> **Code Alignment Note**: This ADR uses **suggestive code examples** that demonstrate the architectural pattern. The actual implementation should leverage existing `infra/jobs/` infrastructure (`SyncCache`, `SyncTimingManager`) and generalize `SmartSyncService` beyond QBO to handle Ramp and Plaid integrations.


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

## Context

**Strategic Pivot**: RowCol is pivoting from QBO-centric architecture to Financial Control Plane for CAS 2.0 firms, requiring orchestration across multiple external rails using a hub-and-spoke model.

**Market Reality**: CAS 2.0 firms have moved to Ramp for bill pay execution, making QBO-only approach obsolete. QBO API limitations (ledger-only, no execution capabilities) require multi-rail orchestration.

**Architecture Challenge**: Current `domains/` architecture is QBO-centric, with all domain services assuming single external system. This creates fundamental mismatch with Financial Control Plane requirements where multiple rails operate on same domain primitives.

**Solution**: Hub-and-spoke architecture where each rail has specific role, RowCol orchestrates verification loop, and chain of custody ensures auditability across rails.

## Decision

**Hub-and-Spoke Multi-Rail Architecture**: Implement Financial Control Plane using hub-and-spoke model where QBO serves as ledger hub, external rails handle specific operations, and RowCol orchestrates verification loop with chain of custody tracking.

### **Rail Responsibilities**
- **QBO (Hub)**: Single source of truth for ledger data (bills, invoices, payments, audit trail)
- **Ramp (Spoke)**: A/P execution (bill approval, payment processing, webhooks)
- **Plaid (Spoke)**: Cash verification (real-time balances, guardrails, cash truth)
- **Stripe (Spoke)**: A/R insights (invoice tracking, payment analysis, CSV processing)

### **Key Patterns**
- **Hub-and-Spoke Architecture**: Clear separation of concerns, each rail does one thing well
- **Verification Loop**: Orchestrates multi-rail operations with clear state transitions
- **Chain of Custody**: Tracks state ownership and transitions across rails
- **Event-Driven Reconciliation**: Uses webhooks and refresh-on-demand to minimize API calls

## Architecture Patterns

### Pattern 1: Verification Loop

**Implementation** (suggestive - should leverage existing infrastructure):
```python
# SUGGESTIVE: This pattern should be implemented using existing infra/jobs/ infrastructure
class VerificationLoopService:
    def __init__(self, business_id: str, db_session):
        self.business_id = business_id
        self.db_session = db_session
        
        # Use existing infrastructure
        from infra.jobs.job_storage import SyncCache
        from infra.jobs.sync_strategies import SyncTimingManager
        from infra.qbo.smart_sync import SmartSyncService  # TODO: generalize beyond QBO
        
        self.cache = SyncCache(business_id)
        self.timing_manager = SyncTimingManager(business_id)
        self.smart_sync = SmartSyncService(business_id, "", db_session)  # TODO: generalize

    async def approve_bill(self, advisor_id, bill_id, business_id):
        # Use existing Plaid integration (infra/plaid/consolidate.py)
        balance = await self._get_plaid_balance(business_id)
        if not self.apply_guardrails(balance, bill_id):
            raise ValueError("Guardrail violation")
        
        # Use generalized SmartSyncService for Ramp
        await self.smart_sync.execute_qbo_call("approve_bill_ramp", bill_id=bill_id)
        
        # Audit logging (implement using existing patterns)
        await self._log_audit(advisor_id, business_id, "approve", bill_id)

    async def verify_execution(self, webhook_data, business_id):
        bill_id = webhook_data["bill_id"]
        
        # Use existing cache infrastructure
        cached_balance = self.cache.get("plaid", f"balance_{business_id}")
        if not cached_balance:
            balance = await self._get_plaid_balance(business_id)
            self.cache.set("plaid", f"balance_{business_id}", balance, ttl_minutes=60)
        
        # Use existing QBO integration
        qbo_payment = await self.smart_sync.execute_qbo_call("get_bill_payment", bill_id=bill_id)
        
        if not self.verify_payment(webhook_data, balance, qbo_payment):
            await self.flag_hygiene_tray(business_id, bill_id)
        
        await self._log_audit(advisor_id, business_id, "verify", bill_id)
```

**Characteristics**:
- ✅ Clear state ownership (Ramp: execution, QBO: ledger, Plaid: cash, RowCol: approvals).
- ✅ Auditability via logged state transitions.

### Pattern 2: Event-Driven Reconciliation

**Implementation** (suggestive - should leverage existing infrastructure):
```python
# SUGGESTIVE: This pattern should use existing infra/jobs/ infrastructure
class WebhookHandler:
    def __init__(self, business_id: str, db_session):
        self.business_id = business_id
        self.db_session = db_session
        
        # Use existing infrastructure
        from infra.jobs.job_storage import SyncCache, get_job_storage_provider
        from infra.jobs.sync_strategies import SyncTimingManager
        from infra.qbo.smart_sync import SmartSyncService  # TODO: generalize
        
        self.cache = SyncCache(business_id)
        self.job_storage = get_job_storage_provider(business_id)
        self.timing_manager = SyncTimingManager(business_id)
        self.smart_sync = SmartSyncService(business_id, "", db_session)

    async def handle_webhook(self, webhook_data):
        bill_id = webhook_data["bill_id"]
        business_id = webhook_data["business_id"]
        
        # Use existing deduplication via job storage
        idempotency_key = f"webhook:{bill_id}:{business_id}"
        existing_job = self.job_storage.get_job_by_idempotency_key(idempotency_key)
        if existing_job:
            return  # Idempotent
        
        # Store webhook as job for tracking
        job_data = {
            "id": f"webhook_{bill_id}_{business_id}",
            "idempotency_key": idempotency_key,
            "status": "processing",
            "webhook_data": webhook_data,
            "created_at": datetime.utcnow().isoformat()
        }
        self.job_storage.save_job(job_data)
        
        # Use existing cache for balance
        balance = await self._get_cached_plaid_balance(business_id)
        
        # Use existing QBO integration
        qbo_payment = await self.smart_sync.execute_qbo_call("get_bill_payment", bill_id=bill_id)
        
        if webhook_data["status"] == "paid" and qbo_payment and balance.get("is_valid"):
            await self.mark_verified(business_id, bill_id)
        else:
            await self.flag_hygiene_tray(business_id, bill_id)
```

**Characteristics**:
- ✅ Minimizes API calls using Ramp webhooks and Plaid refresh-on-demand.
- ✅ Idempotent webhook processing to prevent duplicate actions.

## Implementation Guidelines

### When to Use This Pattern:
- When orchestrating multi-rail operations (QBO, Ramp, Plaid) for bill payments.
- When ensuring auditability for advisor-led cash discipline across 20–100 clients.

### Code Organization:
```
# SUGGESTIVE: Should leverage existing infrastructure
runway/services/
├── verification_loop.py          # Verification loop orchestration (NEW)
└── webhook_handler.py            # Event-driven reconciliation (NEW)

# EXISTING INFRASTRUCTURE TO LEVERAGE:
infra/jobs/
├── job_storage.py               # ✅ EXISTS - SyncCache, JobStorageProvider
├── sync_strategies.py           # ✅ EXISTS - SyncTimingManager
└── enums.py                     # ✅ EXISTS - SyncStrategy, SyncPriority

infra/qbo/
└── smart_sync.py                # ✅ EXISTS - SmartSyncService (TODO: generalize)

infra/plaid/
└── consolidate.py               # ✅ EXISTS - Plaid integration

domains/core/
└── audit_log.py                 # TODO: Implement audit logging
```

### Required Patterns:
```python
class AuditLogService:
    async def log(self, advisor_id, business_id, action, bill_id):
        # Store audit record with advisor_id, business_id, action
        pass
```

## Benefits

### Positive Outcomes
✅ **Auditability**: Every state transition (approval, verification) is logged for SOC2 compliance.  
✅ **Reliability**: Webhook-driven reconciliation reduces state conflicts across rails.

### Business Value
- Enables advisor trust by ensuring traceable, error-free cash discipline workflows.
- Supports scalability to 100 clients with minimal reconciliation overhead.

## Consequences

**Positive**: Clear state ownership simplifies debugging and auditing.  
**Negative**: Webhook dependency increases reliance on Ramp’s 99.9% SLA.

**Risks & Mitigations**:
- **Risk**: Ramp webhook drops miss payment events.  
  **Mitigation**: Implement retry queues and periodic QBO checks.
- **Risk**: Plaid token errors disrupt balance verification.  
  **Mitigation**: Notify advisors via hygiene tray, offer manual fallback.

## Success Metrics
- **Reconciliation Accuracy**: 99% of payments verified without discrepancies.
- **Webhook Latency**: 95% of Ramp webhooks processed within 1 second.

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
- Plaid balance fetching
- Stripe CSV processing
- Multi-rail orchestration

### **TODO: Implement Missing Components**
- `domains/core/audit_log.py` - Audit logging service
- `infra/ramp/adapter.py` - Ramp webhook client
- `runway/services/verification_loop.py` - Verification orchestration
- `runway/services/webhook_handler.py` - Event-driven reconciliation

## Related ADRs
- **ADR-001**: Separation of Concerns (isolates rail integrations from orchestration).
- **ADR-005**: Orchestration Layer (centralizes API coordination for verification loop).
- **ADR-011**: Cost-Efficient Integration (leverages caching and event-driven patterns).

**Last Updated**: 2025-10-06  
**Next Review**: 2026-01-06