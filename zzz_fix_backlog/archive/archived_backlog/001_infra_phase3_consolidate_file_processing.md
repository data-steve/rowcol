## **Infrastructure Phase 3: Consolidate File Processing Backlog**

*Generated from infrastructure consolidation Phase 3 on 2025-01-27*

**Instructions:**
1. **Create Git Branch**: `git checkout -b cleanup/file-processing`
2. **Execute Tasks Sequentially**: Work through tasks in order (they have dependencies)
3. **For Each Task**: Follow the specific implementation patterns and verification steps
4. **Test After Each Task**: Run the specified verification commands
5. **Commit After Each Task**: `git add . && git commit -m "Task: [task-name] - [brief summary]"`
6. **When All Tasks Complete**: `git checkout main && git merge cleanup/file-processing && git branch -d cleanup/file-processing`

**Git Workflow:**
```bash
# Start this cleanup phase
git checkout -b cleanup/file-processing

# Execute tasks in order, committing after each major change
git add .
git commit -m "Task: Audit file processing - Documented current architecture"

# When all tasks complete, merge back
git checkout main
git merge cleanup/file-processing
git branch -d cleanup/file-processing
```

**Rollback Plan:**
```bash
# If this phase fails, abandon it
git checkout main
git branch -D cleanup/file-processing

# Or rollback specific changes
git checkout main
git reset --hard HEAD~1  # Go back one commit
```

**Context for All Tasks:**
- **File Processing**: Document storage, validation, upload handling, and file management utilities
- **Current State**: Scattered across `domains/core/services/document_storage.py`, `runway/routes/bills.py`, and other locations
- **Target**: Consolidated in `infra/files/` with clear separation of concerns
- **ADR Reference**: See ADR-004 for model complexity standards and documentation requirements

**CRITICAL WARNINGS FROM PAINFUL LESSONS:**
- **NEVER** move files without checking ALL import references first
- **ALWAYS** test file upload functionality after moving document storage
- **ALWAYS** check for hardcoded paths that might break after consolidation
- **NEVER** assume file processing is simple - it often has complex validation logic
- **ALWAYS** verify that file storage backends (local, S3, etc.) still work after changes

---

## **Phase 1: Analyze Current File Processing (P0 Critical)**

#### **Task: Audit Current File Processing Code**
- **Status:** `[ ]` Not started
- **Justification:** Need to understand all file processing code before consolidating to avoid breaking existing functionality.
- **Specific Files to Analyze:**
  - `domains/core/services/document_storage.py` - Main document storage service
  - `runway/routes/bills.py` - File upload handling for bills
  - `runway/routes/vendors.py` - File upload handling for vendors
  - `runway/routes/invoices.py` - File upload handling for invoices
  - Any other files with file upload/processing logic
- **Search Commands to Run:**
  - `grep -r "file.*upload\|upload.*file\|document.*storage" . --include="*.py"`
  - `grep -r "FileStorage\|DocumentStorage\|file_storage" . --include="*.py"`
  - `grep -r "\.pdf\|\.jpg\|\.png\|\.csv\|\.xlsx" . --include="*.py"`
- **Required Analysis:**
  - Document all file types currently supported
  - Identify all file storage backends (local, S3, etc.)
  - Map all file validation logic
  - List all file processing utilities
- **Dependencies:** None
- **Verification:** 
  - Create comprehensive list of all file processing functionality
  - Document current file storage architecture
  - Identify any hardcoded paths or configurations
- **Definition of Done:**
  - Complete inventory of all file processing code
  - Clear understanding of current architecture
  - List of all file types and storage backends
  - Documentation of validation logic
- **Next Action:** Execute Task 1: Audit Current File Processing Code

---

#### **Task: Create infra/files/ Directory Structure**
- **Status:** `[ ]` Not started
- **Justification:** Need proper directory structure for consolidated file processing infrastructure.
- **Directory Structure to Create:**
  - `infra/files/` - Main directory
  - `infra/files/document_processing.py` - Document storage and processing
  - `infra/files/file_validation.py` - File validation utilities
  - `infra/files/upload_handlers.py` - File upload handling
  - `infra/files/storage_providers.py` - Storage backend providers
  - `infra/files/__init__.py` - Package initialization
- **Dependencies:** `Audit Current File Processing Code`
- **Verification:** 
  - Run `ls -la infra/files/` - should show all directories and files
  - Run `python -c "import infra.files"` - should import without errors
- **Definition of Done:**
  - All directory structure created
  - All files have proper docstrings
  - Package imports work correctly
- **Next Action:** Execute Task 2: Create infra/files/ Directory Structure

---

## **Phase 2: Consolidate File Processing (P1 High)**

#### **Task: Move Document Storage to infra/files/**
- **Status:** `[ ]` Not started
- **Justification:** Centralize document storage functionality in infrastructure layer.
- **Specific Files to Move:**
  - `domains/core/services/document_storage.py` → `infra/files/document_processing.py`
- **Required Changes:**
  - Move all classes and functions to new location
  - Update class names to be more generic (remove domain-specific naming)
  - Add comprehensive docstrings per ADR-004
  - Update imports throughout codebase
- **Search Commands to Run:**
  - `grep -r "from domains.core.services.document_storage" . --include="*.py"`
  - `grep -r "import.*document_storage" . --include="*.py"`
- **Dependencies:** `Create infra/files/ Directory Structure`
- **Verification:** 
  - Run `grep -r "domains.core.services.document_storage" . --include="*.py"` - should return no results
  - Run `grep -r "infra.files.document_processing" . --include="*.py"` - should show new imports
  - Run `uvicorn main:app --reload` - should start without import errors
- **Definition of Done:**
  - Document storage moved to infra/files/
  - All imports updated throughout codebase
  - Application starts without errors
  - All tests pass
- **Next Action:** Execute Task 3: Move Document Storage to infra/files/

---

#### **Task: Consolidate File Upload Handlers**
- **Status:** `[ ]` Not started
- **Justification:** Centralize file upload handling logic that's currently scattered across route files.
- **Specific Files to Consolidate:**
  - `runway/routes/bills.py` - Extract file upload logic
  - `runway/routes/vendors.py` - Extract file upload logic
  - `runway/routes/invoices.py` - Extract file upload logic
- **Target File:**
  - `infra/files/upload_handlers.py` - Consolidated upload handlers
- **Required Changes:**
  - Extract common file upload patterns
  - Create generic upload handler classes
  - Update route files to use consolidated handlers
  - Add proper error handling and validation
- **Dependencies:** `Move Document Storage to infra/files/`
- **Verification:** 
  - Run `grep -r "file.*upload\|upload.*file" runway/routes/` - should show updated usage
  - Test file upload functionality in each route
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - File upload logic consolidated in infra/files/
  - Route files use consolidated handlers
  - File upload functionality works correctly
  - Error handling is consistent across all routes
- **Next Action:** Execute Task 4: Consolidate File Upload Handlers

---

#### **Task: Create File Validation Utilities**
- **Status:** `[ ]` Not started
- **Justification:** Centralize file validation logic for consistent validation across all file types.
- **Target File:**
  - `infra/files/file_validation.py` - File validation utilities
- **Required Validation Types:**
  - File type validation (PDF, images, CSV, Excel)
  - File size validation
  - File content validation
  - Security validation (malware scanning, etc.)
- **Dependencies:** `Consolidate File Upload Handlers`
- **Verification:** 
  - Run `python -c "from infra.files.file_validation import *"` - should import without errors
  - Test validation with various file types
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - File validation utilities created
  - All file types properly validated
  - Validation integrated with upload handlers
  - Security validation implemented
- **Next Action:** Execute Task 5: Create File Validation Utilities

---

## **Phase 3: Create Storage Providers (P1 High)**

#### **Task: Create Storage Provider Abstraction**
- **Status:** `[ ]` Not started
- **Justification:** Abstract storage backends to support multiple storage providers (local, S3, etc.).
- **Target File:**
  - `infra/files/storage_providers.py` - Storage provider abstraction
- **Required Providers:**
  - Local file storage
  - AWS S3 storage
  - Abstract base class for new providers
- **Dependencies:** `Create File Validation Utilities`
- **Verification:** 
  - Run `python -c "from infra.files.storage_providers import *"` - should import without errors
  - Test each storage provider
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - Storage provider abstraction created
  - Local and S3 providers implemented
  - Abstract base class for extensibility
  - All providers tested and working
- **Next Action:** Execute Task 6: Create Storage Provider Abstraction

---

## **Phase 4: Update All Imports and Test (P2 Medium)**

#### **Task: Update All File Processing Imports**
- **Status:** `[ ]` Not started
- **Justification:** Update all imports throughout codebase to use new infra/files/ structure.
- **Search Commands to Run:**
  - `grep -r "domains.core.services.document_storage" . --include="*.py"`
  - `grep -r "file.*upload\|upload.*file" . --include="*.py"`
- **Dependencies:** `Create Storage Provider Abstraction`
- **Verification:** 
  - Run `grep -r "domains.core.services.document_storage" . --include="*.py"` - should return no results
  - Run `grep -r "infra.files" . --include="*.py"` - should show new imports
  - Run `uvicorn main:app --reload` - should start without errors
  - Run `pytest` - should pass without failures
- **Definition of Done:**
  - All imports updated to use infra/files/
  - No references to old document storage location
  - Application starts without errors
  - All tests pass
- **Next Action:** Execute Task 7: Update All File Processing Imports

---

#### **Task: Test File Processing End-to-End**
- **Status:** `[ ]` Not started
- **Justification:** Verify that all file processing functionality works correctly after consolidation.
- **Test Scenarios:**
  - File upload for bills
  - File upload for vendors
  - File upload for invoices
  - File validation for different types
  - Storage provider switching
- **Dependencies:** `Update All File Processing Imports`
- **Verification:** 
  - Test each file upload endpoint manually
  - Test file validation with various file types
  - Test storage provider functionality
  - Run `pytest` - should pass without failures
- **Definition of Done:**
  - All file upload functionality works correctly
  - File validation works for all supported types
  - Storage providers work correctly
  - All tests pass
- **Next Action:** Execute Task 8: Test File Processing End-to-End

---

**Summary:**
- **Total Tasks:** 7
- **P0 Critical:** 1 task
- **P1 High:** 5 tasks
- **P2 Medium:** 1 task
- **Total Tasks:** 8 tasks

**Quick Reference Commands:**
```bash
# Check for file processing code
grep -r "file.*upload\|upload.*file\|document.*storage" . --include="*.py"

# Check for document storage imports
grep -r "domains.core.services.document_storage" . --include="*.py"

# Test file processing
python -c "from infra.files import *"

# Test application startup
uvicorn main:app --reload
```

This backlog captures all the file processing consolidation work with paranoid-level detail to avoid the painful lessons learned from the SmartSync refactoring.
