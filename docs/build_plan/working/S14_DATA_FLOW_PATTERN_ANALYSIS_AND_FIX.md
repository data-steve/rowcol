# S14: Data Flow Pattern Analysis and Fix

## **Task: Analyze and Fix Data Flow Pattern Violations in Domain Services**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** Current domain services may be violating the documented data flow patterns. We need to analyze which operations should use Pattern 1 (local DB), Pattern 2 (infrastructure services), or Pattern 3 (background sync), and fix any violations before proceeding with E18.
- **Execution Status:** **Needs-Solutioning**

## **CRITICAL: Read These Files First (MANDATORY)**

### **Architecture Context (3 most relevant):**
- `docs/architecture/DATA_ARCHITECTURE_SPECIFICATION.md` - Foundational data architecture patterns
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy

### **Current Phase Context:**
- **Phase 0.5**: QBO-only MVP (current focus)
- **Feature Gating**: QBO-only mode enabled, Ramp/Plaid/Stripe disabled
- **Data Architecture**: Local mirroring + QBOSyncService for live data

### **Task-Specific Context (3 most relevant):**
- `domains/ap/services/bill.py` - Current AP service with QBOSyncService calls
- `domains/ap/services/payment.py` - Current payment service with QBOSyncService calls
- `domains/ar/services/collections.py` - Current AR service with QBOSyncService calls

## **Problem Statement**

**Current State**: Domain services are calling QBOSyncService, but it's unclear whether they're using the correct data flow patterns for each operation.

**The Confusion**: 
- Domain services ARE supposed to call infrastructure services (Pattern 2)
- But they should also query local DB for business logic (Pattern 1)
- Background jobs should handle sync operations (Pattern 3)

**The Real Question**: Are domain services using the RIGHT pattern for each operation?

## **User Story**
"As a developer working on the QBO MVP, I need to understand which operations should use local database queries vs infrastructure service calls vs background sync, so that the system follows the documented data flow patterns correctly."

## **The Data Flow Patterns (From DATA_ARCHITECTURE_SPECIFICATION.md)**

### **Pattern 1: Read Operations (Fast)**
```
User Request → Runway Service → Domain Service → Local DB (mirrored data)
```
**When to use**: Business logic queries, calculations, reporting
**Example**: "Get all unpaid bills" - we already have this data locally

### **Pattern 2: Real-time Operations**
```
User Request → Runway Service → Domain Service → Infrastructure Service → Live API
```
**When to use**: Need fresh data from external systems
**Example**: "Get current QBO balance" - need live data from QBO

### **Pattern 3: Background Sync**
```
Scheduled Job → Infrastructure Service → External API → Local DB Update
```
**When to use**: Keep local database updated with external data
**Example**: Every 15 minutes, sync bills from QBO to our database

## **Service Responsibilities (From DATA_ARCHITECTURE_SPECIFICATION.md)**

### **Domain Services** (`domains/*/services/`)
- **Pattern 1**: Query local database for business logic (fast)
- **Pattern 2**: Call infrastructure services for live data when needed
- **Never**: Query external APIs directly (use infrastructure services)

### **Infrastructure Services** (`infra/*/` or `domains/qbo/services/`)
- **Handle external APIs**: Talk to QBO, Ramp, etc.
- **Rate limiting**: Don't overwhelm external systems
- **Error handling**: Retry failed requests
- **Data transformation**: Convert external data to our format

## **Current State Analysis**

### **Files to Analyze**
1. `domains/ap/services/bill.py` - Has `self.smart_sync.get_bills()` calls
2. `domains/ap/services/payment.py` - Has `self.smart_sync.record_payment()` calls
3. `domains/ar/services/collections.py` - Has `self.smart_sync.get_invoices()` calls

### **Questions to Answer**
1. **Which operations need fresh data** (Pattern 2) vs **cached data** (Pattern 1)?
2. **Are domain services calling infrastructure services at the right times**?
3. **Is background sync working** to keep local DB updated (Pattern 3)?
4. **Are there any operations that should be Pattern 1 but are using Pattern 2**?

## **Solution Design**

### **Step 1: Analyze Current Usage Patterns**
- **Audit each domain service** to understand what operations they perform
- **Categorize each operation** as Pattern 1, 2, or 3
- **Identify violations** where wrong pattern is used

### **Step 2: Define Correct Patterns for Each Operation**
- **Business logic queries** → Pattern 1 (local DB)
- **Fresh data needs** → Pattern 2 (infrastructure services)
- **Sync operations** → Pattern 3 (background jobs)

### **Step 3: Fix Pattern Violations**
- **Move Pattern 1 operations** to query local DB
- **Keep Pattern 2 operations** calling infrastructure services
- **Ensure Pattern 3 operations** are handled by background jobs

### **Step 4: Improve Architecture Documentation**
- **Make data flow patterns clearer** in DATA_ARCHITECTURE_SPECIFICATION.md
- **Add examples** of when to use each pattern
- **Document service responsibilities** more clearly

## **Architecture Doc Improvement Needed**

### **Current (Confusing)**
```
Domain Services (domains/*/services/):
- Query: Local database for mirrored data
- Call: Infrastructure services for live data
```

### **Better (Clearer)**
```
Domain Services (domains/*/services/):
- Pattern 1: Query local database for business logic (fast)
- Pattern 2: Call infrastructure services for live data when needed
- Never: Query external APIs directly (use infrastructure services)
```

## **Success Criteria**

### **Pattern Compliance**
- ✅ All domain services use correct pattern for each operation
- ✅ Business logic queries use local DB (Pattern 1)
- ✅ Fresh data needs use infrastructure services (Pattern 2)
- ✅ Sync operations use background jobs (Pattern 3)

### **Architecture Clarity**
- ✅ Data flow patterns clearly documented
- ✅ Service responsibilities clearly defined
- ✅ Examples show when to use each pattern

### **Code Quality**
- ✅ No pattern violations in domain services
- ✅ Clear separation between Pattern 1, 2, 3 operations
- ✅ Proper error handling for each pattern

## **Dependencies**
- S13: Unified Multi-Rail Architecture (needs this analysis first)
- E18: Unified Multi-Rail Architecture Implementation (blocked until this is complete)

## **Next Steps**
1. **Analyze current usage patterns** in domain services
2. **Categorize operations** by correct pattern
3. **Identify violations** and fix them
4. **Improve architecture documentation**
5. **Create execution tasks** for any fixes needed

## **Progress Tracking**
- Update status to `[🔄]` when starting work
- Update status to `[✅]` when solution is documented
- Update status to `[❌]` if blocked or need help
