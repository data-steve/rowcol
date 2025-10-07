# S03: SmartSyncService Architecture Fix

## Problem Statement
The SmartSyncService implementation has deviated from ADR-005 and created technical debt through inconsistent method signatures, duplicate functionality, and legacy compatibility code. **CRITICAL CONTEXT**: Previous tech debt work (commit 3c8993a) removed product-specific methods like `get_bills_for_digest()` and `get_invoices_for_digest()` to make SmartSyncService generic, but this created new problems: (1) duplicate `get_bills()` methods with different parameters (`due_days` vs `since_date`), (2) ADR-005 still references the removed methods, and (3) legacy compatibility code that shouldn't exist in a new system.

## User Story
As a developer working on the QBO MVP, I need SmartSyncService to provide clean, consistent orchestration methods that align with ADR-005 patterns so that domain services and data orchestrators can get the specific data they need without confusion or technical debt.

## Solution Overview
Fix the SmartSyncService architecture to:
1. **Eliminate duplicate methods** - Consolidate `get_bills()` variants into single, consistent interface
2. **Add purpose-specific orchestration** - Implement `get_bills_for_digest()`, `get_bills_with_issues()` as per ADR-005
3. **Remove legacy compatibility** - Delete deprecated methods that shouldn't exist in new system
4. **Align with ADR-005** - Ensure all methods follow the orchestration pattern correctly
5. **Document method sources** - Clarify which methods are from ADR-005 vs implementation artifacts

## Execution Status
- **Type**: Solutioning Task
- **Status**: Discovery Phase
- **Estimated Effort**: 6-8 hours
- **Priority**: P0 (blocking QBO MVP functionality)

## Discovery Commands
```bash
# Check for duplicate method signatures
grep -n "def get_bills" infra/qbo/smart_sync.py
grep -n "def get_invoices" infra/qbo/smart_sync.py

# Check for legacy compatibility methods
grep -n "LEGACY\|deprecated" infra/qbo/smart_sync.py

# Check ADR-005 method expectations vs implementation
grep -r "get_bills_for_digest\|get_bills_with_issues" docs/architecture/
grep -r "get_bills_for_digest\|get_bills_with_issues" infra/qbo/
```

## Discovery Results
- **Historical Context**: Commit 3c8993a removed product-specific methods (`get_bills_for_digest()`, `get_invoices_for_digest()`) to make SmartSyncService generic
- **Duplicate get_bills() methods**: Lines 144 (due_days) and 223 (since_date) with different signatures - **CREATED BY REFACTOR**
- **Duplicate get_invoices() methods**: Lines 153 (aging_days) and 232 (since_date) with different signatures - **CREATED BY REFACTOR**
- **Legacy compatibility section**: Lines 285-338 with deprecated methods
- **ADR-005 out of sync**: ADRs still reference removed methods (`get_bills_for_digest()`, `get_bills_with_issues()`)
- **Inconsistent parameter patterns**: Some methods use `due_days`, others use `since_date` - **LEFTOVER FROM REFACTOR**
- **Architecture mismatch**: ADRs expect purpose-specific methods, but SmartSyncService was made generic

## File Examples to Follow
- **ADR-005**: `docs/architecture/ADR-005-qbo-api-strategy.md`
- **Current SmartSyncService**: `infra/qbo/smart_sync.py`
- **QBORawClient**: `infra/qbo/client.py`

## Architecture Context
- **Current Phase**: QBO-only MVP (Phase 0.5)
- **Feature Gating**: QBO-only mode enabled, Ramp/Plaid/Stripe disabled
- **Payment Execution**: QBO sync-only (no execution), Ramp execution gated
- **Reserve Management**: Disabled in QBO-only mode
- **Multi-rail Architecture**: Ready for future phases

## Working Directory
- **Location**: `docs/build_plan/working/`
- **Archive**: `docs/build_plan/archive/`
- **Current Focus**: SmartSyncService architecture fixes

## Discovery Phase Tasks
1. **Analyze method duplication** (1h) - **COMPLETED**
   - [x] Found duplicate `get_bills()` methods with different signatures
   - [x] Found duplicate `get_invoices()` methods with different signatures
   - [x] Documented which methods are actually used by data orchestrators
   - [x] Identified which parameters are needed for different use cases

2. **Check ADR-005 compliance** (1h) - **PENDING**
   - [ ] Compare ADR-005 expected methods with current implementation
   - [ ] Identify missing purpose-specific orchestration methods
   - [ ] Document gaps between ADR and implementation

3. **Analyze legacy compatibility** (1h) - **PENDING**
   - [ ] Check if legacy methods are actually used anywhere
   - [ ] Identify which methods can be safely removed
   - [ ] Document migration path for any dependent code

4. **Design clean interface** (2h) - **PENDING**
   - [ ] Consolidate duplicate methods into single, consistent interface
   - [ ] Add missing ADR-005 orchestration methods
   - [ ] Remove unnecessary legacy compatibility code
   - [ ] Ensure all methods follow consistent parameter patterns

## Success Criteria
- **Single method signatures**: No duplicate `get_bills()` or `get_invoices()` methods
- **ADR-005 compliance**: All expected orchestration methods implemented
- **No legacy code**: Remove all deprecated compatibility methods
- **Consistent parameters**: All methods use consistent parameter naming and types
- **Clean interface**: SmartSyncService provides clear, purpose-specific orchestration

## Next Steps
1. Complete discovery phase tasks
2. Design clean SmartSyncService interface
3. Create implementation plan
4. Fix the architecture issues
5. Resume data orchestrator and QBO sandbox testing fixes

## Related Tasks
- **S01**: QBO Sandbox Testing Strategy (ON HOLD)
- **S02**: Data Orchestrator Architecture Fix (ON HOLD)
- **E01**: Consolidate duplicate SmartSyncService methods
- **E02**: Add missing ADR-005 orchestration methods
- **E03**: Remove legacy compatibility code
- **E04**: Update data orchestrators to use clean interface
