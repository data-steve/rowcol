# S06: Domain Object Mirroring Strategy

## **Task: Define Domain Object Mirroring Strategy**
- **Status:** `[✅]` Complete
- **Priority:** P0 Critical
- **Justification:** E01, E02, E03 all depend on understanding the mirroring strategy. We need to define the architectural pattern for how domain objects are mirrored locally, including transaction logs vs mirror models, before any execution tasks can proceed.
- **Execution Status:** **COMPLETE** - Implemented in S07 and E01

## Backstory and Context

### **The Problem We Discovered**
While working on E01 (Sync Infrastructure), we realized we were making ad-hoc recommendations for `ComplianceTransactionLog` and `BillMirror` models without understanding the broader mirroring strategy. This exposed a critical gap: **we haven't defined how domain objects are mirrored locally**.

### **Why This Matters**
- **E01, E02, E03 are blocked** - they all need to know what models to sync, query, and aggregate
- **Every domain object needs mirroring** - bills, invoices, vendors, customers, etc.
- **We need both patterns** - transaction logs (append-only audit trails) AND mirror models (current state for fast queries)
- **QBO is the ledger rail** - we need historical preservation beyond QBO's API limits
- **Compliance requirements** - ledger operations need audit trails

### **The Hypothesis We're Testing**
```python
# Transaction Log (append-only for audit)
class BillTransactionLog(Base, TenantMixin):
    # Immutable transaction log
    created_at = Column(DateTime, nullable=False)
    transaction_type = Column(String)  # created, updated, synced
    bill_data = Column(JSON)  # Full bill data at time of transaction
    
# Mirror Model (current state for queries)
class BillMirror(Base, TimestampMixin, TenantMixin):
    # Current state for fast queries
    qbo_id = Column(String, unique=True)
    vendor_name = Column(String)
    amount = Column(Numeric)
    # ... other fields
    
    # Sync tracking
    last_synced_at = Column(DateTime)
    sync_source = Column(String)
```

**Sync Service Pattern**:
- **Append to transaction log** (every change)
- **Update mirror model** (current state)

### **What We Need to Discover**
- Do existing domain models already follow this pattern?
- What's the relationship between transaction logs and mirror models?
- How should the sync service coordinate between them?
- Does this pattern work for all domain objects?
- How does this extend to future rails (Ramp, Plaid, Stripe)?

### **Expected vs Discovery**
**We expect to find:**
- Existing domain models that need mirroring
- Some audit log patterns already in place
- SmartSyncService that needs to be extended
- Database patterns that can be leveraged

**We might discover:**
- Existing mirroring patterns we didn't know about
- Different approaches that work better
- Constraints we didn't consider
- Opportunities to simplify the architecture

**The goal is to discover the reality, not just implement our hypothesis.**

## Problem Statement
We need to define the fundamental mirroring strategy for domain objects. Every domain object needs a mirror for fast queries, and we need transaction logs for audit trails. The current data architecture doesn't specify how this works, making E01, E02, E03 impossible to execute without architectural decisions.

## User Story
As a developer working on the QBO ledger rail MVP, I need a clear architectural pattern for mirroring domain objects so that I can implement sync infrastructure, domain services, and data orchestrators with consistent data access patterns.

## Solution Overview
Design a comprehensive mirroring strategy that defines how domain objects are mirrored locally, including the relationship between transaction logs (append-only audit trails) and mirror models (current state for queries), and how the sync service coordinates between them.

## CRITICAL: Read These Files First (MANDATORY)

### **Architecture Context (3 most relevant):**
- `docs/architecture/DATA_ARCHITECTURE_SPECIFICATION.md` - Foundational data architecture patterns
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `domains/core/models/base.py` - Existing model patterns

### **Product Context (2 most relevant):**
- `docs/build_plan/MVP_DATA_ARCHITECTURE_PLAN.md` - MVP implementation plan
- `docs/prds/prd0_mvp.md` - QBO ledger rail MVP requirements

### **Current Phase Context:**
- **Phase 0.5**: QBO ledger rail MVP (current focus)
- **Data Architecture**: Local mirroring + SmartSyncService for live data
- **Mirroring Need**: Every domain object needs mirroring for fast queries and audit trails

## Solutioning Mindset (MANDATORY)
**Don't rush to solutions. Follow discovery → analysis → design → document process.**

### **Discovery Phase Checklist (MANDATORY):**
- [ ] **All discovery commands run** - no shortcuts, no assumptions
- [ ] **All files read** - understand what actually exists
- [ ] **All analysis questions answered** - don't skip any
- [ ] **Assumptions validated** - test every assumption against reality
- [ ] **Current state documented** - write down what you found

### **Analysis Phase Checklist:**
- [ ] **Current state mapped** - understand how things work
- [ ] **Gaps identified** - what's missing or unclear
- [ ] **Patterns found** - look at similar solutions
- [ ] **Relationships understood** - how parts connect
- [ ] **Findings documented** - write down what you learned

### **Design Phase Checklist:**
- [ ] **Solution designed** - clear implementation approach
- [ ] **Dependencies mapped** - what needs to be done first
- [ ] **Patterns created** - reusable approaches
- [ ] **Verification planned** - how to test success
- [ ] **Solution documented** - complete approach written down

### **Documentation Phase Checklist:**
- [ ] **Executable tasks created** - hands-free implementation tasks
- [ ] **Specific patterns provided** - code examples and patterns
- [ ] **Verification steps defined** - specific commands to test
- [ ] **Dependencies mapped** - clear execution order
- [ ] **Task status updated** - marked as complete

### **Working Relationship Guidelines:**
- **Self-Sufficient Analysis**: Answer questions through discovery before asking for help
- **Validate Assumptions**: Test every assumption through discovery before asking questions
- **Don't Rush**: Follow the discovery → analysis → design → document process religiously
- **One Problem Per Doc**: Keep complexity contained in one solutioning document

## Code Pointers
- `domains/*/models/` - All existing domain models
- `domains/core/models/base.py` - Base model patterns
- `infra/qbo/smart_sync.py` - Existing sync service
- `domains/core/services/audit_log.py` - Existing audit log service

## MANDATORY: Discovery Commands
```bash
# Find all domain models
find domains/ -name "models" -type d
find domains/ -name "*.py" -path "*/models/*" -exec grep -l "class.*Model\|Base" {} \;

# Find existing mirroring patterns
grep -r "mirror\|sync\|cache" domains/ --include="*.py"
grep -r "created_at\|updated_at\|sync" domains/ --include="*.py"

# Find transaction log patterns
grep -r "audit\|log\|transaction" domains/ --include="*.py"
grep -r "append.*only\|immutable" domains/ --include="*.py"

# Check current model relationships
grep -r "ForeignKey\|relationship" domains/ --include="*.py"
grep -r "unique.*constraint\|index" domains/ --include="*.py"

# Test current state
uvicorn main:app --reload
pytest -k "test_model"
```

## Current Issues to Resolve
- **Missing Mirroring Strategy**: No clear pattern for how domain objects are mirrored
- **Transaction Log vs Mirror Model**: Unclear relationship between audit trails and current state
- **Sync Service Interface**: No defined interface for how sync service updates mirrors
- **Domain Object Coverage**: Don't know which domain objects need mirroring
- **Data Flow Pattern**: Unclear how external APIs → transaction logs → mirror models works

## Assumption Validation
- **Domain Models Exist**: Need to discover what domain models actually exist
- **Mirroring Patterns**: Need to understand current mirroring approaches
- **Audit Requirements**: Need to understand compliance audit trail requirements
- **Sync Service Capabilities**: Need to understand what SmartSyncService can do
- **Database Schema**: Need to understand current database patterns

## Required Analysis

### **Critical Questions to Answer**
1. **Do existing domain models already follow a mirroring pattern?** 
   - Are there already transaction logs and mirror models?
   - What patterns exist in the current codebase?

2. **What's the relationship between transaction logs and mirror models?**
   - Should they be separate tables or the same table?
   - How do they stay in sync?
   - What's the data flow pattern?

3. **How should the sync service coordinate between them?**
   - Does SmartSyncService already handle this?
   - What's the interface for updating mirrors?
   - How do we prevent data inconsistencies?

4. **Does this pattern work for all domain objects?**
   - Bills, invoices, vendors, customers, etc.
   - What's the general pattern that applies to all?
   - How do we handle different data types?

5. **How does this extend to future rails?**
   - Ramp, Plaid, Stripe integration
   - Multi-rail data reconciliation
   - Rail-specific vs rail-agnostic patterns

### **Discovery Focus Areas**
- **Domain Object Inventory**: What domain objects exist and what do they represent?
- **Mirroring Requirements**: What data needs to be mirrored for fast queries?
- **Audit Requirements**: What operations need transaction logs for compliance?
- **Sync Patterns**: How should external API data flow into local mirrors?
- **Model Relationships**: How should transaction logs relate to mirror models?

## Architecture Analysis
- **Data Architecture Fit**: How does this fit with DATA_ARCHITECTURE_SPECIFICATION.md?
- **Service Boundaries**: How does this fit with ADR-001 domain separation?
- **Multi-Tenancy**: How does this fit with ADR-003 multi-tenancy patterns?
- **QBO Integration**: How does this fit with QBO as ledger rail?
- **Future Rails**: How does this pattern extend to Ramp, Plaid, Stripe?

## File Examples to Follow
- `domains/core/models/base.py` - Example of base model patterns
- `domains/core/services/audit_log.py` - Example of audit log service
- `infra/qbo/smart_sync.py` - Example of sync service
- `domains/ap/models/bill.py` - Example of domain model

## Solution Design Process
1. **Discovery Phase**: Map all existing domain models and mirroring patterns
2. **Analysis Phase**: Understand requirements for mirroring and audit trails
3. **Design Phase**: Create the general mirroring pattern for all domain objects
4. **Documentation Phase**: Create executable tasks for implementation

## Dependencies
- **S07**: Sync and Transaction Log Implementation (needed to validate and implement the pattern)
- **E01**: MVP Sync Infrastructure Setup (blocked pending this solution)
- **E03**: MVP Data Orchestrators Purpose Specific (blocked pending this solution)

## Verification
- **Pattern Validation**: Does the mirroring pattern work for all domain objects?
- **Sync Service Integration**: Does the pattern work with SmartSyncService?
- **Audit Trail Compliance**: Does the pattern support compliance requirements?
- **Performance Testing**: Does the pattern support fast multi-client queries?
- **Multi-Rail Extension**: Does the pattern extend to future rails?

## Definition of Done
- **Mirroring Pattern Defined**: Clear architectural pattern for domain object mirroring
- **Transaction Log Pattern**: Clear pattern for append-only audit trails
- **Sync Service Interface**: Clear interface for how sync service updates mirrors
- **Model Relationships**: Clear relationships between transaction logs and mirror models
- **Executable Tasks Created**: E01, E02, E03 updated with proper dependencies
- **Architecture Documentation**: Pattern documented in DATA_ARCHITECTURE_SPECIFICATION.md

## Solution Complete

### **Mirroring Strategy: Mirror Model + Transaction Log Pattern**

**Current State**: Domain models (`Bill`, `Vendor`, `Payment`) ARE the mirror models with QBO sync fields
**Solution**: Add transaction log models alongside existing mirror models

### **Pattern Implementation**

```python
# Mirror Model (current state for queries) - EXISTING
class Bill(Base, TimestampMixin, TenantMixin):
    # ... existing fields with QBO sync fields ...
    transaction_logs = relationship("BillTransactionLog", back_populates="bill")

# Transaction Log (append-only for audit) - NEW
class BillTransactionLog(Base, TenantMixin):
    transaction_id = Column(String(36), primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.bill_id"))
    transaction_type = Column(String(50))  # created, updated, synced, deleted
    source = Column(String(50))  # qbo, ramp, plaid, stripe, user
    bill_data = Column(JSON)  # Complete data snapshot
    changes = Column(JSON)  # What changed
    created_at = Column(DateTime, nullable=False)
```

### **Sync Service Pattern**

```python
class SmartSyncService:
    async def sync_bill(self, qbo_bill_data: Dict[str, Any]) -> Bill:
        # 1. Update mirror model (existing logic)
        bill = self._update_bill_mirror(qbo_bill_data)
        
        # 2. Append to transaction log (NEW)
        await self._append_bill_transaction_log(
            bill=bill,
            transaction_type="synced",
            source="qbo",
            bill_data=qbo_bill_data
        )
        
        return bill
```

### **Why Transaction Logs Are Required**

1. **SOC2 Compliance**: Immutable financial audit trails
2. **Multi-Rail Reconciliation**: Cross-rail data verification
3. **Chain of Custody**: Approve → Execute → Verify → Record workflow
4. **Financial Integrity**: Zero data loss tolerance
5. **Regulatory Compliance**: Financial services requirements

### **Multi-Rail Extension**

- **QBO**: `qbo_*_id` fields → `ramp_*_id`, `plaid_*_id`, `stripe_*_id` fields
- **SmartSyncService** → `RampSmartSyncService`, `PlaidSmartSyncService`, `StripeSmartSyncService`
- **Transaction Logs**: Each rail appends to same transaction log models

### **Updated DATA_ARCHITECTURE_SPECIFICATION.md**

Added system-wide data requirements including:
- Multi-rail reconciliation data
- Compliance and audit data  
- Performance and scale data
- Transaction log patterns
- Cross-rail entity mapping

## Progress Tracking
- Update status to `[🔄]` when starting analysis
- Update status to `[💡]` when solution is identified
- Update status to `[✅]` when solution is documented
- Update status to `[❌]` if blocked or need help

## Todo List Integration
- Create Cursor todo for this task when starting analysis
- Update todo status as analysis progresses
- Mark todo complete when solution is documented
- Add discovery todos for found issues
- Remove obsolete todos when analysis is complete
- Ensure todo list reflects current analysis state
