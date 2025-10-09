# S01: QBO Sandbox Testing Strategy

## Problem Statement
**CRITICAL TESTING GAP DISCOVERED**: Current testing approach relies heavily on mocks (337+ mock references) with 12+ test files skipping due to insufficient QBO sandbox data. This creates a false sense of security - we don't know if our code actually works with real QBO data. 

**Root Cause**: The existing sandbox framework is fragmented across multiple files without a unified strategy, AND the data orchestrator architecture is broken (discovered during S01 discovery), making it impossible to create proper test scenarios.

**Impact**: 
- Can't test real QBO integration because data orchestrators don't provide full entity coverage
- Calculators fail because they expect customers/vendors/accounts but orchestrators only provide bills/invoices/balances
- No purpose-specific filtering means we can't test hygiene vs decision-ready scenarios
- DigestDataOrchestrator duplication means we can't test proper aggregation patterns

## User Story
As a developer working on the QBO MVP, I need a unified testing strategy that eliminates mocks and provides real QBO sandbox data so that I can confidently validate that our runway calculations, payment processing, and data quality features actually work with real QuickBooks Online data.

## Solution Overview
Design and implement a comprehensive QBO sandbox testing strategy that:
1. **WAITS FOR S02 COMPLETION** - Data orchestrator architecture must be fixed first
2. **Aligns tests with corrected architecture** - Each runway experience has proper data orchestrator + calculators
3. **Defines test scenarios per experience** - What does each service actually need to test?
4. **Creates experience-specific test data** - Data that matches what each data orchestrator needs
5. **Eliminates mock violations** - Replace hardcoded mocks with real QBO API data
6. **Establishes testing patterns** - Consistent approach for all QBO integration tests

**Key Insight**: This is a chicken-egg problem - we need S02 to fix the data orchestrator architecture before we can create proper test scenarios. The current broken architecture makes it impossible to test real QBO integration.

## Solutioning Mindset (MANDATORY)
**Don't rush to solutions. Follow discovery → analysis → design → document process.**

This is a complex testing strategy problem that requires:
- **Deep discovery** of current testing infrastructure and data requirements
- **Careful analysis** of what each service actually needs to test
- **Thoughtful design** of unified testing patterns and sandbox data
- **Clear documentation** of executable implementation tasks

**Key Principle**: Validate every assumption against reality before designing solutions.

## Execution Status
- **Type**: Solutioning Task
- **Status**: ON HOLD - Critical Architecture Issues Discovered
- **Estimated Effort**: 12-16 hours (down from build_plan_v5's 36h overkill)
- **Priority**: P0 (blocking QBO MVP confidence)
- **Hold Reason**: Discovery revealed critical data orchestrator architecture gaps that must be fixed first

## Discovery Commands
```bash
# Current test data audit
grep -r "sandbox" tests/ --include="*.py"  # Found 10+ sandbox references
grep -r "mock" tests/ --include="*.py" | wc -l  # 337+ mock references
find tests/ -name "*.py" -exec grep -l "skip" {} \;  # 12+ files with skips

# What services need what data
grep -r "get_.*_for_digest" runway/services/ --include="*.py"  # Found in onboarding.py
grep -r "get_.*_for_tray" runway/services/ --include="*.py"  # No direct references
grep -r "get_.*_for_console" runway/services/ --include="*.py"  # No direct references

# Current QBO integration reality
grep -r "QBO" tests/ --include="*.py" | wc -l  # 380+ QBO references
ls tests/sandbox/  # 6 files: create_sandbox_data.py, scenario_data.py, scenario_runner.py, etc.
```

## Discovery Results
**DISCOVERED DURING S01 DISCOVERY PHASE**:

### **Current Testing State:**
- **Mock Violations**: 337+ mock references across test files
- **Test Skips**: 12+ files skip due to insufficient data
- **QBO References**: 380+ QBO references in tests (heavy integration)
- **Sandbox Files**: 6 existing sandbox files but fragmented approach

### **Current Architecture (BROKEN):**
- **DigestService**: Uses `DigestDataOrchestrator` + `RunwayCalculator` + `InsightCalculator`
- **TrayService**: Uses `HygieneTrayDataOrchestrator` + `RunwayCalculator` + `PriorityCalculator` + `ImpactCalculator`
- **ConsoleService**: Uses `DecisionConsoleDataOrchestrator` + `RunwayCalculator` + `ImpactCalculator` + `InsightCalculator`

### **CRITICAL ARCHITECTURE GAPS DISCOVERED:**
- **Data Orchestrator Problem**: All orchestrators pull same raw data instead of filtering by purpose (hygiene vs decision-ready)
- **Missing Entity Coverage**: Data orchestrators only pull bills/invoices/balances, but calculators expect customers/vendors/accounts
- **DigestDataOrchestrator Duplication**: Pulls same raw data instead of aggregating from HygieneTray + DecisionConsole
- **Import Path Violations**: Orchestrators in `runway/core/data_orchestrators/` but experiences import from `runway/services/data_orchestrators/`
- **ADR-006 Violations**: Experience services should use orchestrators, not direct SmartSyncService calls

### **Testing Impact:**
- **Can't test real QBO integration** because data orchestrators don't provide full entity coverage
- **Calculators fail** because they expect customers/vendors/accounts but orchestrators don't provide them
- **No purpose-specific filtering** means we can't test hygiene vs decision-ready scenarios
- **DigestDataOrchestrator duplication** means we can't test proper aggregation patterns
- **Full QBO Entity Coverage Needed**: bills, invoices, customers, vendors, accounts, company info (balances)
- **Data Quality Testing**: Need realistic data quality issues for testing hygiene features
- **Priority Testing**: Need vendor/customer names for priority scoring algorithms

## File Examples to Follow
- **Existing Sandbox**: `tests/sandbox/create_sandbox_data.py`, `scenario_data.py`, `scenario_runner.py`
- **QBO Integration**: `infra/qbo/smart_sync.py`, `infra/qbo/client.py` (✅ COMPLETED in S03)
- **Service Data Needs**: `runway/services/2_experiences/digest.py`, `tray.py`, `console.py`
- **Broken Orchestrators**: `runway/core/data_orchestrators/` (imports broken, need S02 fix)
- **Expected Orchestrators**: `runway/services/data_orchestrators/` (where experiences expect them)
- **Reference Architecture**: `docs/archive/build_plan_v5.md` (Stage 1.21 - 36h comprehensive approach)

## Architecture Context
- **Current Phase**: QBO-only MVP (Phase 0.5)
- **Feature Gating**: QBO-only mode enabled, Ramp/Plaid/Stripe disabled
- **Payment Execution**: QBO sync-only (no execution), Ramp execution gated
- **Reserve Management**: Disabled in QBO-only mode
- **Multi-rail Architecture**: Ready for future phases

### **S03 Completion Impact (✅ COMPLETED)**
SmartSyncService now provides clean high-level API:
- `get_bills()`, `get_invoices()`, `get_customers()`, `get_vendors()`, `get_accounts()`, `get_company_info()`
- Each method handles retry, caching, activity recording, deduplication internally
- Rail-specific design documented for future multi-rail support
- **Ready for S02**: Data orchestrators can now use clean SmartSyncService API

### **S02 Dependency (IN PROGRESS)**
S01 **CANNOT PROCEED** until S02 fixes data orchestrator architecture:
- Fix import paths (orchestrator locations)
- Implement purpose-specific filtering in each orchestrator
- Add missing entity coverage to all orchestrators
- Make DigestDataOrchestrator aggregative instead of duplicative
- Fix ADR-006 compliance in experience services

## Working Directory
- **Location**: `docs/build_plan/working/`
- **Archive**: `docs/build_plan/archive/`
- **Current Focus**: QBO MVP testing foundation

## Discovery Phase Checklist (MANDATORY)
- [x] **All discovery commands run** - no shortcuts, no assumptions
- [x] **All files read** - understand what actually exists
- [x] **All analysis questions answered** - don't skip any
- [x] **Assumptions validated** - test every assumption against reality
- [x] **Current state documented** - write down what you found

## Analysis Phase Checklist
- [x] **Current state mapped** - understand how things work
- [x] **Gaps identified** - what's missing or unclear
- [x] **Patterns found** - look at similar solutions
- [x] **Relationships understood** - how parts connect
- [x] **Findings documented** - write down what you learned

## Design Phase Checklist
- [ ] **Solution designed** - clear implementation approach
- [ ] **Dependencies mapped** - what needs to be done first
- [ ] **Patterns created** - reusable approaches
- [ ] **Verification planned** - how to test success
- [ ] **Solution documented** - complete approach written down

## Documentation Phase Checklist
- [ ] **Executable tasks created** - hands-free implementation tasks
- [ ] **Specific patterns provided** - code examples and patterns
- [ ] **Verification steps defined** - specific commands to test
- [ ] **Dependencies mapped** - clear execution order
- [ ] **Task status updated** - marked as complete

## Discovery Phase Tasks
1. **Audit existing test data sources** (2h) - **COMPLETED**
   - [x] Found 6 sandbox files but fragmented approach
   - [x] Identified 337+ mock references across tests
   - [x] Found 12+ files with skip conditions
   - [x] Documented QBO API response format requirements

2. **Analyze service data requirements** (2h) - **COMPLETED**
   - [x] DigestService: Uses `DigestDataOrchestrator` + `RunwayCalculator` + `InsightCalculator`
   - [x] TrayService: Uses `HygieneTrayDataOrchestrator` + `RunwayCalculator` + `PriorityCalculator` + `ImpactCalculator`
   - [x] ConsoleService: Uses `DecisionConsoleDataOrchestrator` + `RunwayCalculator` + `ImpactCalculator` + `InsightCalculator`
   - [x] **DigestDataOrchestrator QBO needs**: `get_bills()`, `get_invoices()`, `get_company_info()` (balances)
   - [x] **HygieneTrayDataOrchestrator QBO needs**: `get_bills()`, `get_invoices()`, `get_company_info()` (balances)
   - [x] **DecisionConsoleDataOrchestrator QBO needs**: `get_bills()`, `get_invoices()`, `get_company_info()` (balances)
   - [x] **BUT calculators need more**: `get_customers()`, `get_vendors()`, `get_accounts()` for data quality analysis
   - [x] **DataQualityCalculator needs**: customers, vendors, accounts for consistency checks and completeness analysis
   - [x] **PriorityCalculator needs**: vendor_name, customer_name for priority scoring
   - [x] **Test scenarios defined**: Need full QBO entity coverage: bills, invoices, customers, vendors, accounts, company info

3. **CRITICAL ARCHITECTURE GAPS DISCOVERED** (2h) - **COMPLETED**
   - [x] **Data Orchestrator Problem**: All orchestrators pull same raw data instead of filtering by purpose
   - [x] **Missing Entity Coverage**: Data orchestrators only pull bills/invoices/balances, but calculators expect customers/vendors/accounts
   - [x] **DigestDataOrchestrator Duplication**: Pulls same raw data instead of aggregating from HygieneTray + DecisionConsole
   - [x] **Import Path Violations**: Orchestrators in `runway/core/data_orchestrators/` but experiences import from `runway/services/data_orchestrators/`
   - [x] **ADR-006 Violations**: Experience services should use orchestrators, not direct SmartSyncService calls
   - [x] **Testing Impact**: Can't test real QBO integration because data orchestrators don't provide full entity coverage

4. **WAIT FOR S02 COMPLETION** (0h) - **PENDING**
   - [ ] **S02 must fix data orchestrator architecture first**
   - [ ] **S02 must implement purpose-specific filtering in each orchestrator**
   - [ ] **S02 must add missing entity coverage to all orchestrators**
   - [ ] **S02 must make DigestDataOrchestrator aggregative instead of duplicative**
   - [ ] **S02 must fix ADR-006 compliance in experience services**

5. **Design unified testing strategy** (4h) - **PENDING (AFTER S02)**
   - [ ] **Centralized QBO sandbox data service** with full entity coverage
   - [ ] **3 business scenarios** with realistic data quality issues
   - [ ] **Purpose-specific test data** for hygiene vs decision-ready scenarios
   - [ ] **Integration testing patterns** for real QBO API calls

6. **Create implementation plan** (4h) - **PENDING (AFTER S02)**
   - [ ] Specific files to modify
   - [ ] Data generation approach
   - [ ] Integration testing patterns
   - [ ] Success criteria

## Success Criteria
- **Zero test skips** due to insufficient QBO sandbox data
- **All 3 business scenarios** fully represented in QBO sandbox format
- **Complete QBO entity coverage**: Bills, Invoices, Customers, Vendors, Accounts, Company Info (balances)
- **Realistic data quality issues** for testing hygiene features (missing due dates, orphaned references, etc.)
- **Vendor/Customer data** for priority scoring algorithms
- **Account data** for chart of accounts validation
- **Performance**: Full scenario creation in <2 minutes
- **Maintainability**: Clear documentation and extension patterns

## Next Steps
1. **WAIT FOR S02 COMPLETION** - Data orchestrator architecture must be fixed first
2. **Resume discovery phase tasks** - Design unified testing architecture after S02
3. **Create implementation plan** - Specific execution tasks for testing strategy
4. **Break down into executable tasks** - Implementation tasks for sandbox testing
5. **Begin implementation** - Only after S02 provides working data orchestrators

## Key Questions to Answer After S02
1. **Testing Strategy**: How should we test purpose-specific filtering (hygiene vs decision-ready)?
2. **Sandbox Data**: What specific data quality issues should we simulate for testing?
3. **Integration Patterns**: How should we test real QBO API calls vs mocked responses?
4. **Scenario Coverage**: What business scenarios best represent our target customers?
5. **Performance Testing**: How should we test QBO API rate limiting and retry logic?

## Working Relationship Guidelines
- **Self-Sufficient Analysis**: Answer questions through discovery before asking for help
- **Validate Assumptions**: Test every assumption through discovery before asking questions
- **Don't Rush**: Follow the discovery → analysis → design → document process religiously
- **One Problem Per Doc**: Keep complexity contained in one solutioning document

## Related Tasks
- **S02**: Data Orchestrator Architecture Fix (IN PROGRESS - S01 dependency)
- **S03**: SmartSyncService Architecture Fix (✅ COMPLETED - provides clean API foundation)
- **Future E01**: Implement QBO Sandbox Data Service (after S02)
- **Future E02**: Create Business Scenario Test Data (after S02)
- **Future E03**: Implement Integration Testing Patterns (after S02)
