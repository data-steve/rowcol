# E01: Complete Nuclear Cleanup - Fix Broken Imports

## **Task: Complete Nuclear Cleanup - Fix Broken Imports**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** The nuclear cleanup was partially completed - messy files were deleted and clean foundation built, but import updates were never finished, leaving the application in a broken state
- **Execution Status:** **Execution-Ready**

## Problem Statement
The nuclear cleanup deleted the `domains/qbo/` directory (circular dependency mess) and created the clean `infra/qbo/` structure, but import updates were never completed. This leaves the application with broken imports that reference deleted files, preventing it from starting.

## User Story
As a developer working on the QBO MVP, I need the application to start without import errors so that I can continue development and testing of the QBO integration features.

## Solution Overview
Find and fix all broken imports that reference deleted `domains/qbo/` files by updating them to use the new `infra/qbo/` structure.

## Initial Files to Fix
- **Discovery Required**: Need to find all files with broken imports
- **Expected Pattern**: `from domains.qbo` → `from infra.qbo`
- **Expected Pattern**: `import domains.qbo` → `import infra.qbo`

## Discovery Commands
```bash
# Find broken imports
grep -r "from domains.qbo" . --include="*.py"
grep -r "import domains.qbo" . --include="*.py"
grep -r "domains/qbo" . --include="*.py"

# Check for references to deleted services
grep -r "QBODataService" . --include="*.py"
grep -r "QBOBulkScheduledService" . --include="*.py"

# Test application startup to find real import errors
poetry run python -c "import main; print('Import successful')"
```

## Discovery Results
- **No domains.qbo references found**: The nuclear cleanup was more complete than expected
- **Real import error discovered**: `ModuleNotFoundError: No module named 'common'`
- **Error location**: Multiple files importing from `common.exceptions`
- **Missing module**: `common.exceptions` should be `infra.config.exceptions`
- **Root cause**: The `common` module was renamed to `infra.config` but imports weren't updated
- **Files affected**: 20+ files need import updates from `common.exceptions` to `infra.config.exceptions`
- [x] **Additional issue discovered**: Numbered directory structure (`0_`, `1_`, `2_`) causes Python import syntax errors --- SOLVED BY USER

## Implementation Steps
1. [x] **Run discovery commands** to find all broken imports
2. [x] **Update imports** from `common.exceptions` to `infra.config.exceptions` (20+ files)
3. [x] **Update imports** from `domains.qbo.client` to `infra.qbo.client` (no references found)
4. [x] **Update imports** from `domains.qbo.smart_sync` to `infra.qbo.smart_sync` (no references found)
5. [x] **Remove any references** to deleted files (only comment reference remains)
6. [x] **Numbered directory structure** fixed by user

## Verification Steps
- [x] Run `grep -r "from domains.qbo" . --include="*.py"` - should return no results ✅
- [x] Run `grep -r "import domains.qbo" . --include="*.py"` - should return no results ✅
- [x] Run `grep -r "domains/qbo" . --include="*.py"` - should return no results ✅ (only comment reference remains)


## Success Criteria
- [x] **No broken imports**: All references to deleted `domains/qbo/` files are updated ✅
- [x] **Common.exceptions fixed**: All imports updated from `common.exceptions` to `infra.config.exceptions` ✅
- [x] **Numbered directories fixed**: All numbered directory imports resolved ✅
- [x] **Clean imports**: All imports use the new `infra/qbo/` structure ✅

## Git Workflow
```bash
# Create branch for this task
git checkout -b fix/nuclear-cleanup-imports

# After each major change, commit
git add .
git commit -m "E01: Fix broken imports from domains.qbo to infra.qbo"

# When complete, merge back
git checkout main
git merge fix/nuclear-cleanup-imports
git branch -d fix/nuclear-cleanup-imports
```

## Related Tasks
- **E02**: Complete Nuclear Cleanup - Remove References to Deleted Files
- **E03**: Complete Nuclear Cleanup - Test Application Startup
- **S03**: SmartSyncService Architecture Fix (parent solutioning task)
