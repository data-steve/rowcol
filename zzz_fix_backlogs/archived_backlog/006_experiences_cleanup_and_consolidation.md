# Backlog Task: Experiences Cleanup and Consolidation

## **Task Overview**
- **ID**: `006_experiences_cleanup_and_consolidation`
- **Priority**: P1 HIGH
- **Estimated Time**: 6-8 hours
- **Status**: `[ ]` Not started
- **Category**: Architecture Cleanup

## **Problem Statement**
The `runway/experiences/` directory has multiple architectural issues that need comprehensive cleanup:

1. **Mixed Concerns**: Data providers and business logic mixed in same files
2. **Dead Code**: Mock/test data providers that should be moved to sandbox data service
3. **Inconsistent Imports**: Some files use old `domains.qbo.smart_sync` imports
4. **Duplicate Versions**: Multiple versions of similar functionality in same files
5. **Antipatterns**: Factory functions and data providers in business logic files

## **Evidence of Problems**

### **tray.py (Already Partially Fixed)**
- **Git Reference**: Changes made in current session
- **Issues Found**:
  - Had TrayDataProvider classes mixed with TrayService
  - Factory function `get_tray_data_provider()` in business logic file
  - Mock data provider logic that should be in sandbox service
- **Changes Made**:
  - Removed TrayDataProvider classes (moved to `qbo_sandbox_data_examples.md`)
  - Simplified TrayService to use SmartSyncService directly
  - Cleaned up imports and constructor

### **onboarding.py (Needs Investigation)**
- **Issues Found**:
  - Uses old import: `from domains.qbo.smart_sync import SmartSyncService`
  - Should use: `from infra.jobs import SmartSyncService`
  - May have similar data provider patterns

### **digest.py (Needs Investigation)**
- **Issues Found**:
  - Commented out email service imports
  - May have mock data provider patterns
  - Needs to use SmartSyncService for QBO data

### **test_drive.py (Needs Investigation)**
- **Issues Found**:
  - Large file (700+ lines) - may have mixed concerns
  - May have demo/mock data providers mixed with business logic
  - Needs to use SmartSyncService for QBO data

## **Required Analysis**

### **Step 1: Audit All Experience Files**
```bash
# Check for old SmartSync imports
grep -r "from domains.qbo.smart_sync" runway/experiences/

# Check for data provider patterns
grep -r "class.*DataProvider\|class.*Provider" runway/experiences/

# Check for factory functions
grep -r "def get_.*_provider\|def get_.*_data" runway/experiences/

# Check for mock/test/demo patterns
grep -r "Mock\|Test\|Demo" runway/experiences/

# Check file sizes (large files may have mixed concerns)
find runway/experiences/ -name "*.py" -exec wc -l {} \;
```

### **Step 2: Identify Specific Issues Per File**
For each experience file, identify:
- [ ] Old SmartSync imports that need updating
- [ ] Data provider classes that should be moved to sandbox service
- [ ] Factory functions that don't belong in business logic
- [ ] Mock/test data that should be in sandbox service
- [ ] Mixed concerns (data providers + business logic)
- [ ] Dead code or commented out functionality

### **Step 3: Categorize Issues**
- **Import Issues**: Old `domains.qbo.smart_sync` → `infra.jobs`
- **Data Provider Issues**: Move to sandbox data service
- **Mixed Concerns**: Separate data providers from business logic
- **Dead Code**: Remove unused mock/test functionality
- **Architecture Issues**: Ensure proper separation of concerns

## **Proposed Solution**

### **Phase 1: Import Updates**
- Update all experience files to use `from infra.jobs import SmartSyncService`
- Remove old `from domains.qbo.smart_sync import SmartSyncService` imports
- Ensure consistent import patterns across all experience files

### **Phase 2: Data Provider Extraction**
- Move all data provider classes to `qbo_sandbox_data_examples.md`
- Remove factory functions from business logic files
- Ensure experiences use SmartSyncService directly for QBO data

### **Phase 3: Mixed Concerns Cleanup**
- Separate data providers from business logic
- Ensure each experience file has single responsibility
- Remove duplicate versions of functionality

### **Phase 4: Dead Code Removal**
- Remove commented out functionality
- Remove unused mock/test data
- Clean up imports and dependencies

## **Files to Investigate and Fix**
- `runway/experiences/tray.py` - ✅ Partially fixed, needs verification
- `runway/experiences/onboarding.py` - Needs import updates
- `runway/experiences/digest.py` - Needs investigation
- `runway/experiences/test_drive.py` - Needs investigation
- `runway/experiences/console.py` - Needs investigation (if exists)

## **Dependencies**
- None - this is a cleanup task that can be done independently

## **Verification**
- [ ] All experience files use `from infra.jobs import SmartSyncService`
- [ ] No old `domains.qbo.smart_sync` imports remain
- [ ] No data provider classes in business logic files
- [ ] No factory functions in business logic files
- [ ] All mock/test data moved to sandbox data examples
- [ ] Each experience file has single responsibility
- [ ] No dead code or commented out functionality
- [ ] All tests pass after cleanup

## **Definition of Done**
- All experience files have clean, single responsibility
- Data providers moved to sandbox data service
- Consistent import patterns across all files
- No mixed concerns or antipatterns
- All functionality works with SmartSyncService
- Clean, maintainable code structure

## **Rollback Plan**
```bash
# Revert all changes if needed
git checkout HEAD~1 -- runway/experiences/
git checkout HEAD~1 -- qbo_sandbox_data_examples.md
```

## **Context**
This cleanup is essential for maintaining clean architecture in the experiences layer. The current state has antipatterns that make the code hard to maintain and understand. This task will establish proper separation of concerns and ensure all experiences follow consistent patterns.

## **Related Files**
- `qbo_sandbox_data_examples.md` - Where data providers should be moved
- `infra/jobs/smart_sync.py` - Central orchestration layer for QBO interactions
- `docs/architecture/ADR-005-qbo-api-strategy.md` - Architecture guidance
