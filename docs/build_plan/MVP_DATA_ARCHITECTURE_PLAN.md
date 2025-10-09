# MVP Data Architecture Build Plan

*Implementation plan for the missing middle layer solution*

## **The Problem We're Solving**

**Current State**: We're an empty shell around QBO with no local data, no sync jobs, and domain services that don't work. Everything is live API calls that won't scale for multi-client dashboards.

**The Opportunity**: Build the missing middle layer that bridges product requirements to code implementation with proper data mirroring, sync orchestration, and service boundaries.

## **The Solution: Three-Layer Architecture**

### **Layer 1: Data Mirroring (Local DB)**
**Purpose**: Fast multi-client queries, historical analysis, offline capabilities

**What We Mirror**:
- **Bills**: For runway calculations, hygiene analysis, decision making
- **Invoices**: For AR analysis, variance tracking, collection decisions  
- **Balances**: For cash position, trend analysis, guardrails

**Sync Strategy**:
- **Frequency**: Every 15 minutes via background jobs
- **Trigger**: Scheduled jobs + webhook notifications
- **Scope**: All clients in advisor portfolio
- **Storage**: PostgreSQL with proper indexing

### **Layer 2: Sync Orchestration (Background Jobs)**
**Purpose**: Keep local data fresh and handle QBO API fragility

**Components**:
- **SmartSyncService**: Rate limiting, retry logic, caching
- **Background Jobs**: Celery/APScheduler for scheduled syncs
- **Webhook Handlers**: Real-time updates for critical changes
- **Error Handling**: Retry with exponential backoff, dead letter queues

**Implementation**:
- Use existing `infra/jobs/` infrastructure
- SQLite for dev, PostgreSQL for prod
- Sync all clients in advisor portfolio

### **Layer 3: Service Boundaries (Fixed)**
**Purpose**: Clear separation of concerns and data access patterns

**Domain Services** (`domains/*/services/`):
- **Query**: Local DB for mirrored data
- **Call**: SmartSyncService for live data when needed
- **Methods**: `get_bills_with_issues()`, `get_bills_ready_for_decision()`
- **Scope**: Rail-agnostic business logic

**Data Orchestrators** (`runway/services/data_orchestrators/`):
- **Purpose**: Aggregate data from domain services for specific experiences
- **Data Source**: Domain services, not direct API calls
- **Filtering**: Purpose-specific (hygiene vs decisions vs reporting)
- **Aggregation**: Multi-client data coordination

**Runway Services** (`runway/services/experiences/`):
- **Purpose**: User experiences and workflows
- **Data Source**: Data orchestrators only
- **Scope**: MVP experiences (digest, hygiene tray, decision console)

## **Implementation Plan**

### **Phase 1: Build the Foundation (Week 1)**

#### **Day 1-2: Set Up Sync Infrastructure**
- **Task**: Configure existing `infra/jobs/` for QBO sync
- **Deliverable**: Background jobs syncing bills, invoices, balances every 15 minutes
- **Validation**: Jobs run successfully, data appears in local DB

#### **Day 3-4: Fix Domain Services**
- **Task**: Update domain services to query local DB + SmartSyncService
- **Deliverable**: `BillService`, `InvoiceService`, `BalanceService` working with local data
- **Validation**: Services return data from local DB, fall back to API when needed

#### **Day 5: Create Data Orchestrators**
- **Task**: Build purpose-specific data orchestrators
- **Deliverable**: `HygieneTrayDataOrchestrator`, `DecisionConsoleDataOrchestrator`, `DigestDataOrchestrator`
- **Validation**: Each orchestrator provides filtered data for its experience

### **Phase 2: Fix the Architecture (Week 2)**

#### **Day 1-2: Remove Execution Code**
- **Task**: Remove QBO execution assumptions from domain services
- **Deliverable**: Clean domain services focused on data access only
- **Validation**: No execution code in domain services

#### **Day 3-4: Fix Service Boundaries**
- **Task**: Ensure runway services use data orchestrators, not direct API calls
- **Deliverable**: Clean service boundaries with proper data flow
- **Validation**: All data flows through orchestrators

#### **Day 5: Add Monitoring**
- **Task**: Add sync status monitoring and error handling
- **Deliverable**: Dashboard showing sync health, data freshness, error rates
- **Validation**: Can monitor sync performance and troubleshoot issues

### **Phase 3: MVP Validation (Week 3)**

#### **Day 1-2: End-to-End Testing**
- **Task**: Test full MVP workflow with real QBO data
- **Deliverable**: Working digest, hygiene tray, decision console
- **Validation**: All MVP features work with local data

#### **Day 3-4: Performance Optimization**
- **Task**: Optimize for multi-client dashboard performance
- **Deliverable**: Sub-3-second dashboard loads for 100 clients
- **Validation**: Performance meets requirements

#### **Day 5: Documentation and Cleanup**
- **Task**: Document architecture patterns and cleanup code
- **Deliverable**: Architecture docs, troubleshooting guides, clean codebase
- **Validation**: Team can maintain and extend the system

## **Data Flow Architecture**

### **Read Operations (Fast)**
```
User Request → Runway Service → Data Orchestrator → Domain Service → Local DB
```

### **Sync Operations (Background)**
```
Scheduled Job → SmartSyncService → QBO API → Local DB Update
```

### **Live Operations (Real-time)**
```
User Action → Runway Service → Domain Service → SmartSyncService → QBO API
```

## **Multi-Rail Considerations**

### **Current: QBO Ledger Rail MVP**
- **QBO**: Ledger rail for compliance and ledger operations
- **Sync**: Bills, invoices, balances from QBO
- **Storage**: Local PostgreSQL mirror with historical preservation
- **Operations**: Bill approvals, payment matching, hygiene fixes

### **Future: Multi-Rail Architecture**
- **QBO**: Compliance rail (ledger, hygiene, audit trail)
- **Ramp**: Execution rail (bill payment, payment processing)
- **Plaid**: Verification rail (bank balances, transaction matching)
- **Stripe**: Insights rail (AR insights, payment analysis)

### **Domain Service Evolution**
- **Current**: `domains/qbo/` for QBO-specific business logic
- **Future**: `domains/ramp/`, `domains/plaid/`, `domains/stripe/` for rail-specific logic
- **Shared**: `domains/core/` for rail-agnostic business logic

## **Code Organization Strategy**

### **Keep and Refactor**
- **Domain Models**: Keep all models, they're used by runway/
- **SmartSyncService**: Keep as infrastructure orchestration layer
- **Background Jobs**: Use existing `infra/jobs/` infrastructure
- **Calculators**: Keep as-is, they're stateless and correct

### **Park for Future Rails**
- **Payment Matching**: `domains/ar/services/payment_matching_unbundling.py` - sophisticated AR matching for Stripe
- **Vendor Normalization**: `domains/vendor_normalization/` - useful for Ramp vendor categorization
- **Policy Engine**: `runway/policy/services/policy_engine.py` - business rules for multi-rail

### **Delete/Refactor**
- **Execution Code**: Remove QBO execution assumptions from domain services
- **Unused Services**: Delete domain services that aren't used by runway/
- **Direct API Calls**: Remove runway services calling SmartSyncService directly

## **Success Criteria**

### **Performance**
- **Dashboard Load**: <3 seconds for 100 clients
- **Sync Frequency**: Every 15 minutes without rate limiting
- **Data Freshness**: 95% of data within 15 minutes of source

### **Reliability**
- **Uptime**: 99.9% availability
- **Error Recovery**: Graceful handling of QBO API failures
- **Data Integrity**: Zero data loss tolerance

### **Maintainability**
- **Clear Boundaries**: Domains query DB, runway uses orchestrators
- **Monitoring**: Real-time sync health and error tracking
- **Documentation**: Architecture patterns and troubleshooting guides

## **Architecture Quality Assessment**

### **✅ What We Got Right**

#### **Multi-Rail Architecture Foundation**
The separation we implemented is **architecturally sound**:
- `BaseSyncService` provides generic orchestration (rate limiting, retry, caching)
- `QBOSyncService` provides QBO-specific business logic
- This pattern will scale cleanly to `RampSyncService`, `PlaidSyncService`, `StripeSyncService`

#### **Transaction Log Integration**
The immutable audit trail approach is **excellent** for compliance needs:
- Complete change tracking for SOC2
- Multi-rail reconciliation support
- Immutable append-only logs prevent data tampering

#### **Mirror Model Strategy**
The local mirroring approach is **smart** for our use case:
- Fast multi-client operations (100+ clients per advisor)
- Offline capability for calculations
- Reduces API calls to external systems

### **🚀 Strategic Improvements Needed**

#### **Data Consistency & Atomicity**
**Current Gap**: Mirror model updates and transaction logs aren't atomic
**Solution**: Wrap sync operations in database transactions
```python
async def sync_bill_with_log(self, bill, qbo_bill_data, ...):
    async with self.db_session.begin():  # Atomic transaction
        # Update mirror model
        self._update_bill_mirror(bill, mapped_data)
        # Create transaction log
        transaction_log = await self.transaction_log_service.log_bill_sync(...)
        # Both succeed or both fail
```

#### **Multi-Rail Reconciliation Strategy**
**Missing Piece**: How to handle conflicts when QBO says $1000 but Ramp says $999?
**Solution**: Add reconciliation service for cross-rail conflicts
```python
class MultiRailReconciliationService:
    async def reconcile_bill_data(self, bill_id: str):
        qbo_data = await self.qbo_sync.get_bill(bill_id)
        ramp_data = await self.ramp_sync.get_bill(bill_id)
        
        if qbo_data['amount'] != ramp_data['amount']:
            # Log conflict, flag for human review
            await self.flag_data_conflict(bill_id, qbo_data, ramp_data)
```

#### **Sync Timing & Dependencies**
**Current Gap**: No coordination between rails. What if Ramp payment affects QBO balance?
**Solution**: Event-driven sync with dependency tracking
```python
class SyncOrchestrator:
    async def handle_payment_executed(self, payment_event):
        # 1. Update Ramp data
        await self.ramp_sync.update_payment(payment_event)
        # 2. Trigger QBO sync (payment affects QBO balance)
        await self.qbo_sync.sync_affected_bills(payment_event.bill_ids)
        # 3. Update runway calculations
        await self.runway_calculator.recalculate(payment_event.business_id)
```

### **📊 Architecture Maturity Grades**

#### **For Current Phase (QBO-only MVP)**
**Grade: A-**
- Solid foundation that won't need major refactoring
- Transaction logs provide compliance coverage
- Mirror models enable fast operations

#### **For Multi-Rail Future**
**Grade: B+**
- Architecture will scale, but needs:
  - Cross-rail reconciliation logic
  - Event-driven sync coordination
  - Conflict resolution strategies

#### **For Enterprise Scale (100+ clients)**
**Grade: B**
- Mirror models will need optimization (caching, indexing)
- Transaction logs will need archival strategy
- Sync orchestration will need queue management

### **🔧 Implementation Roadmap**

#### **Phase 1.5: Data Consistency (Immediate)**
1. **Add atomic transactions** to all sync methods
2. **Implement sync status tracking** (pending, synced, failed)
3. **Add data validation** before mirror updates
4. **Create sync health monitoring** dashboard

#### **Phase 2.5: Multi-Rail Preparation (Before Ramp)**
1. **Design reconciliation service** for cross-rail conflicts
2. **Add event-driven sync triggers** (webhook → sync cascade)
3. **Implement sync dependency tracking** (Ramp payment → QBO sync)
4. **Create conflict resolution workflows**

#### **Phase 3.5: Scale Optimization (100+ clients)**
1. **Add sync queue management** (Redis/Celery)
2. **Implement data archival** for transaction logs
3. **Add performance monitoring** for sync operations
4. **Create data freshness alerts**

## **Next Steps**

1. **Start Phase 1**: Set up sync infrastructure with existing `infra/jobs/`
2. **Configure Database**: Set up PostgreSQL for local mirroring
3. **Build Sync Jobs**: Create background jobs for bills, invoices, balances
4. **Test with QBO Sandbox**: Validate sync patterns work
5. **Implement Phase 1.5**: Add atomic transactions and sync monitoring
6. **Iterate and Optimize**: Build, test, and refine the architecture

---

*This plan provides the concrete foundation for building the missing middle layer that bridges product requirements to code implementation, with clear guidance for multi-rail scaling and enterprise readiness.*
