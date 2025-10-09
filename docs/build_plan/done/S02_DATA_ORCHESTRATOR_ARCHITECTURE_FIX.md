# S02: Data Orchestrator Architecture Fix

## Problem Statement
**CRITICAL ARCHITECTURE GAP DISCOVERED**: The entire QBO integration architecture violates both ADR-005 and ADR-006 patterns. While we thought the data orchestrator pattern was implemented correctly, discovery revealed that all orchestrators pull the same generic QBO data without purpose-specific filtering, making calculators fail and creating a false sense of architecture compliance.

**Root Cause**: Data orchestrators were implemented as simple data fetchers rather than purpose-specific filters, and DigestDataOrchestrator duplicates functionality instead of aggregating from other orchestrators.

**Impact**: 
- Calculators expect full entity coverage (customers, vendors, accounts) but get only bills/invoices/balances
- No filtering by purpose (hygiene issues vs decision-ready items)
- DigestDataOrchestrator is duplicative instead of aggregative
- Experience services have broken imports due to orchestrator location mismatch

## User Story
As a developer working on the QBO MVP, I need the data orchestrator pattern to work correctly so that each experience gets the data it needs (hygiene issues vs decision-ready items) and calculators get the full entity coverage they require for proper analysis.

## Solution Overview
Fix the entire QBO integration architecture to:
1. **Implement ADR-005 SmartSyncService orchestration** - Add purpose-specific methods like `get_bills_for_digest()`, `get_bills_with_issues()`
2. **Implement ADR-006 domain service filtering** - Add methods like `get_bills_with_issues()` to domain services
3. **Fix data orchestrator patterns** - Use domain services instead of direct SmartSyncService calls
4. **Provide full entity coverage** - All orchestrators must provide customers, vendors, accounts to calculators
5. **Eliminate DigestDataOrchestrator duplication** - Digest should aggregate from HygieneTray + DecisionConsole

## Execution Status
- **Type**: Solutioning Task
- **Status**: ✅ **ARCHITECTURE RESOLVED** - Implementation tasks created
- **Estimated Effort**: 0 hours (architecture complete, implementation tasks created)
- **Priority**: P0 (blocking QBO MVP functionality)

## Architecture Resolution
**✅ RESOLVED**: The DATA_ARCHITECTURE_SPECIFICATION.md and MVP_DATA_ARCHITECTURE_PLAN.md provide the complete architectural solution:

### **Data Orchestrator Pattern (Fixed)**
- **Purpose**: Aggregate data from domain services for specific experiences
- **Data Source**: Domain services, not direct SmartSyncService calls
- **Filtering**: Purpose-specific (hygiene vs decisions vs reporting)
- **Aggregation**: Multi-client data coordination

### **Service Boundaries (Fixed)**
- **Domain Services**: Query local DB + SmartSyncService for live data
- **Data Orchestrators**: Aggregate from domain services
- **Runway Services**: Use data orchestrators only

### **Progressive Implementation**
- **Phase 1**: QBO-only MVP with proper data orchestrator patterns
- **Phase 2+**: Add Ramp, Plaid, Stripe with rail-specific orchestrators

## Implementation Tasks Created

**✅ IMPLEMENTATION TASKS CREATED**: The MVP data architecture implementation has been broken down into executable tasks:

### **E01: MVP Sync Infrastructure Setup**
- **Task**: Set up QBO sync infrastructure with background jobs
- **Effort**: 1-2 days
- **Priority**: P0
- **Dependencies**: None (foundation task)

### **E02: Fix Domain Services for Local Data Access**
- **Task**: Update domain services to query local DB + SmartSyncService
- **Effort**: 1-2 days
- **Priority**: P0
- **Dependencies**: E01 (needs sync infrastructure)

### **E03: Create Purpose-Specific Data Orchestrators**
- **Task**: Build purpose-specific data orchestrators that aggregate from domain services
- **Effort**: 1-2 days
- **Priority**: P0
- **Dependencies**: E01, E02 (needs sync infrastructure and domain services)

### **Additional Tasks Needed**
- **E04**: Fix Service Boundaries (update runway services to use orchestrators)
- **E05**: Add Full Entity Coverage (ensure all orchestrators provide complete data)
- **E06**: Fix Import Paths (move orchestrators to correct location)

## Success Criteria
- **ADR-006 compliance**: All experience services use orchestrators, no direct SmartSyncService calls
- **Proper filtering**: HygieneTray gets issues, DecisionConsole gets decision-ready items
- **Full entity coverage**: All orchestrators provide customers, vendors, accounts to calculators
- **No duplication**: Digest aggregates from HygieneTray + DecisionConsole
- **Working calculators**: All calculators get the data they need to function properly

## Next Steps
1. **Start Implementation**: Begin with E01 (fix import paths)
2. **Follow Architecture**: Use DATA_ARCHITECTURE_SPECIFICATION.md as guide
3. **Test Incrementally**: Validate each fix with QBO sandbox
4. **Complete MVP**: Finish all implementation tasks

## Related Tasks
- **S01**: QBO Sandbox Testing Strategy (ON HOLD - waiting for S02 completion)
- **S03**: SmartSyncService Architecture Fix (✅ COMPLETED)
- **S04**: Data Ownership Strategy (✅ RESOLVED by architecture docs)
- **S05**: MVP Product-to-Code Alignment (✅ RESOLVED by architecture docs)

---

*The architecture is now fully defined. Implementation tasks remain to fix the code to match the architecture.*