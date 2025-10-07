# S02: Data Orchestrator Architecture Fix

## Problem Statement
The entire QBO integration architecture violates both ADR-005 and ADR-006 patterns. SmartSyncService lacks purpose-specific orchestration methods, domain services lack filtering methods, and data orchestrators bypass the intended patterns to pull raw generic data. This breaks the entire data flow, makes calculators fail, and creates a false sense of architecture compliance.

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
- **Status**: Discovery Phase
- **Estimated Effort**: 8-12 hours
- **Priority**: P0 (blocking QBO MVP functionality)

## Discovery Commands
```bash
# Check current orchestrator implementations
grep -r "get_bills\|get_invoices\|get_company_info" runway/services/0_data_orchestrators/
grep -r "customers\|vendors\|accounts" runway/services/1_calculators/
grep -r "qbo_data.get" runway/services/1_calculators/

# Check ADR-006 compliance
grep -r "SmartSyncService" runway/services/2_experiences/
grep -r "data_orchestrator" runway/services/2_experiences/
```

## Discovery Results
- **All orchestrators pull same data**: bills, invoices, company_info (balances)
- **Calculators expect full coverage**: customers, vendors, accounts in qbo_data parameter
- **No filtering by purpose**: HygieneTray should filter for issues, DecisionConsole for decision-ready
- **DigestDataOrchestrator is duplicative**: Should aggregate from other orchestrators
- **ADR-006 violation**: Experience services should use orchestrators, not direct SmartSyncService calls

## File Examples to Follow
- **ADR-006**: `docs/architecture/ADR-006-data-orchestrator-pattern.md`
- **Current Orchestrators**: `runway/services/0_data_orchestrators/`
- **Current Calculators**: `runway/services/1_calculators/`
- **Current Experiences**: `runway/services/2_experiences/`

## Architecture Context
- **Current Phase**: QBO-only MVP (Phase 0.5)
- **Feature Gating**: QBO-only mode enabled, Ramp/Plaid/Stripe disabled
- **Payment Execution**: QBO sync-only (no execution), Ramp execution gated
- **Reserve Management**: Disabled in QBO-only mode
- **Multi-rail Architecture**: Ready for future phases

## Working Directory
- **Location**: `docs/build_plan/working/`
- **Archive**: `docs/build_plan/archive/`
- **Current Focus**: Data orchestrator architecture fixes

## Discovery Phase Tasks
1. **Analyze ADR-006 compliance** (2h) - **IN PROGRESS**
   - [ ] Check if current implementation matches ADR-006 pattern
   - [ ] Identify specific violations and gaps
   - [ ] Document what should be vs what is

2. **Map calculator data requirements** (2h) - **PENDING**
   - [ ] Document exactly what each calculator needs from qbo_data
   - [ ] Identify missing entity coverage
   - [ ] Map data flow from orchestrators to calculators

3. **Design proper filtering strategy** (2h) - **PENDING**
   - [ ] Define what "hygiene issues" means for HygieneTray
   - [ ] Define what "decision-ready" means for DecisionConsole
   - [ ] Design filtering logic for each orchestrator

4. **Create implementation plan** (2h) - **PENDING**
   - [ ] Specific files to modify
   - [ ] Data flow changes required
   - [ ] Testing strategy for architecture fixes

## Success Criteria
- **ADR-006 compliance**: All experience services use orchestrators, no direct SmartSyncService calls
- **Proper filtering**: HygieneTray gets issues, DecisionConsole gets decision-ready items
- **Full entity coverage**: All orchestrators provide customers, vendors, accounts to calculators
- **No duplication**: Digest aggregates from HygieneTray + DecisionConsole
- **Working calculators**: All calculators get the data they need to function properly

## Next Steps
1. Complete discovery phase tasks
2. Design proper data orchestrator architecture
3. Create implementation plan
4. Fix the architecture issues
5. Resume QBO sandbox testing strategy

## Related Tasks
- **S01**: QBO Sandbox Testing Strategy (ON HOLD)
- **E01**: Fix HygieneTrayDataOrchestrator filtering
- **E02**: Fix DecisionConsoleDataOrchestrator filtering
- **E03**: Eliminate DigestDataOrchestrator duplication
- **E04**: Add full entity coverage to all orchestrators
