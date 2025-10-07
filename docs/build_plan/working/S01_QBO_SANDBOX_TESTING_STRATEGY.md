# S01: QBO Sandbox Testing Strategy

## Problem Statement
Current testing approach relies heavily on mocks (337+ mock references) with 12+ test files skipping due to insufficient QBO sandbox data. This creates a false sense of security - we don't know if our code actually works with real QBO data. The existing sandbox framework is fragmented across multiple files without a unified strategy for realistic, scenario-relevant test data.

## User Story
As a developer working on the QBO MVP, I need a unified testing strategy that eliminates mocks and provides real QBO sandbox data so that I can confidently validate that our runway calculations, payment processing, and data quality features actually work with real QuickBooks Online data.

## Solution Overview
Design and implement a comprehensive QBO sandbox testing strategy that:
1. **Aligns tests with current architecture** - Each runway experience has its own data orchestrator + calculators
2. **Defines test scenarios per experience** - What does each service actually need to test?
3. **Creates experience-specific test data** - Data that matches what each data orchestrator needs
4. **Eliminates mock violations** - Replace hardcoded mocks with real QBO API data
5. **Establishes testing patterns** - Consistent approach for all QBO integration tests

**Key Insight**: This is a chicken-egg problem - we need to understand what each experience actually needs to test before we can design the sandbox data strategy.

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
- **Mock Violations**: 337+ mock references across test files
- **Test Skips**: 12+ files skip due to insufficient data
- **QBO References**: 380+ QBO references in tests (heavy integration)
- **Sandbox Files**: 6 existing sandbox files but fragmented approach
- **Current Architecture**: Each runway experience has its own data orchestrator pattern:
  - **DigestService**: Uses `DigestDataOrchestrator` + `RunwayCalculator` + `InsightCalculator`
  - **TrayService**: Uses `HygieneTrayDataOrchestrator` + `RunwayCalculator` + `PriorityCalculator` + `ImpactCalculator`
  - **ConsoleService**: Uses `DecisionConsoleDataOrchestrator` + `RunwayCalculator` + `ImpactCalculator` + `InsightCalculator`
- **Chicken-Egg Problem**: Tests need to align with current architecture, but we need to understand what each service actually needs to test
- **CRITICAL ARCHITECTURE GAP**: Data orchestrators only pull bills/invoices/balances, but calculators expect customers/vendors/accounts
- **Data Orchestrator Problem**: All orchestrators pull same raw data instead of filtering by purpose (hygiene vs decision-ready)
- **Calculator Data Mismatch**: Calculators expect full QBO entity coverage but orchestrators don't provide it
- **Full QBO Entity Coverage Needed**: bills, invoices, customers, vendors, accounts, company info (balances)
- **Data Quality Testing**: Need realistic data quality issues for testing hygiene features
- **Priority Testing**: Need vendor/customer names for priority scoring algorithms

## File Examples to Follow
- **Existing Sandbox**: `tests/sandbox/create_sandbox_data.py`, `scenario_data.py`, `scenario_runner.py`
- **QBO Integration**: `infra/qbo/smart_sync.py`, `infra/qbo/client.py`
- **Service Data Needs**: `runway/services/2_experiences/digest.py`, `tray.py`, `console.py`
- **Reference Architecture**: `docs/archive/build_plan_v5.md` (Stage 1.21 - 36h comprehensive approach)

## Architecture Context
- **Current Phase**: QBO-only MVP (Phase 0.5)
- **Feature Gating**: QBO-only mode enabled, Ramp/Plaid/Stripe disabled
- **Payment Execution**: QBO sync-only (no execution), Ramp execution gated
- **Reserve Management**: Disabled in QBO-only mode
- **Multi-rail Architecture**: Ready for future phases

## Working Directory
- **Location**: `docs/build_plan/working/`
- **Archive**: `docs/build_plan/archive/`
- **Current Focus**: QBO MVP testing foundation

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

3. **Design unified testing strategy** (4h) - **IN PROGRESS**
   - [x] **Digest Orchestrator**: Duplicative - should aggregate from HygieneTray + DecisionConsole data
   - [x] **Calculator Data Needs**: General purpose qbo_data with all entities (bills, invoices, customers, vendors, accounts)
   - [x] **Company Info vs Balances**: Separate concerns - company info from QBO, balances from Plaid (future)
   - [x] **Chart of Accounts**: Skip for MVP - not used in current calculations
   - [ ] **Architecture Fix**: Data orchestrators need to provide full entity coverage to calculators
   - [ ] **Centralized QBO sandbox data service** with full entity coverage
   - [ ] **3 business scenarios** with realistic data quality issues

4. **Create implementation plan** (4h) - **PENDING**
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
1. Complete discovery phase tasks
2. Design unified testing architecture
3. Create implementation plan
4. Break down into executable tasks
5. Begin implementation

## Related Tasks
- **S02**: QBO API Integration Validation
- **S03**: Data Quality Testing Framework
- **E01**: Implement QBO Sandbox Data Service
- **E02**: Create Business Scenario Test Data
