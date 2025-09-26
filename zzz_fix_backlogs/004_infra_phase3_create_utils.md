## **Infrastructure Phase 3: Create Utilities Backlog**

*Generated from infrastructure consolidation Phase 3 on 2025-01-27*

**Instructions:**
1. **Create Git Branch**: `git checkout -b cleanup/utilities`
2. Choose a task that is `Ready for Spec`.
3. Run the `@spec "<Task Title>"` command in Cursor.
4. Once the task is approved, switch to Auto mode and run `@build`.
5. After the task is complete, update the status here to `Done ✔️`.
6. **Commit Work**: `git add . && git commit -m "Task: [task-name] - [brief summary]"`
7. **When All Tasks Complete**: `git checkout main && git merge cleanup/utilities && git branch -d cleanup/utilities`

**Git Workflow:**
```bash
# Start this cleanup phase
git checkout -b cleanup/utilities

# Execute tasks in order, committing after each major change
git add .
git commit -m "Task: Audit utilities - Documented current architecture"

# When all tasks complete, merge back
git checkout main
git merge cleanup/utilities
git branch -d cleanup/utilities
```

**Rollback Plan:**
```bash
# If this phase fails, abandon it
git checkout main
git branch -D cleanup/utilities

# Or rollback specific changes
git checkout main
git reset --hard HEAD~1  # Go back one commit
```

**Context for All Tasks:**
- **Utilities**: Validation, serialization, crypto, and other generic utility functions
- **Current State**: Scattered across `infra/utils/`, `infra/api/base_client.py`, and other locations
- **Target**: Consolidated in `infra/utils/` with clear separation of concerns
- **ADR Reference**: See ADR-004 for model complexity standards and documentation requirements

**CRITICAL WARNINGS FROM PAINFUL LESSONS:**
- **NEVER** assume utility code is simple - it often has complex validation and serialization logic
- **ALWAYS** check for existing utility functions before creating new ones
- **ALWAYS** test utility functions with edge cases
- **NEVER** hardcode validation rules or serialization formats
- **ALWAYS** verify that crypto utilities are properly implemented and secure

---

## **Phase 1: Analyze Current Utility Code (P0 Critical)**

#### **Task: Audit Current Utility Code**
- **Status:** `Ready for Spec`
- **Justification:** Need to understand all utility code before consolidating to avoid breaking existing functionality.
- **Specific Files to Analyze:**
  - `infra/utils/` - Existing utility functions
  - `infra/api/base_client.py` - Retry logic and error handling
  - `infra/utils/error_handling.py` - Error handling utilities
  - `domains/` - Any utility functions in domain services
  - `runway/` - Any utility functions in runway code
- **Search Commands to Run:**
  - `grep -r "def.*validate\|def.*serialize\|def.*crypto\|def.*util" . --include="*.py"`
  - `grep -r "retry\|backoff\|error.*handling" . --include="*.py"`
  - `grep -r "json\|yaml\|xml\|csv" . --include="*.py"`
- **Required Analysis:**
  - Document all utility functions currently available
  - Identify all validation logic
  - Map all serialization formats
  - List all crypto utilities
- **Dependencies:** None
- **Verification:** 
  - Create comprehensive list of all utility functionality
  - Document current utility architecture
  - Identify any hardcoded validation rules or formats
- **Definition of Done:**
  - Complete inventory of all utility code
  - Clear understanding of current architecture
  - List of all utility types and functions
  - Documentation of validation and serialization logic
- **Next Action:** Ready for you to run `@spec "Audit Current Utility Code"`

---

#### **Task: Create infra/utils/ Directory Structure**
- **Status:** `Ready for Spec`
- **Justification:** Need proper directory structure for consolidated utility infrastructure.
- **Directory Structure to Create:**
  - `infra/utils/` - Main directory (already exists)
  - `infra/utils/validation.py` - Validation utilities
  - `infra/utils/serialization.py` - Serialization utilities
  - `infra/utils/crypto.py` - Crypto utilities
  - `infra/utils/retry.py` - Retry and backoff utilities
  - `infra/utils/error_handling.py` - Error handling utilities (already exists)
  - `infra/utils/__init__.py` - Package initialization
- **Dependencies:** `Audit Current Utility Code`
- **Verification:** 
  - Run `ls -la infra/utils/` - should show all directories and files
  - Run `python -c "import infra.utils"` - should import without errors
- **Definition of Done:**
  - All directory structure created
  - All files have proper docstrings
  - Package imports work correctly
- **Next Action:** Ready for you to run `@spec "Create infra/utils/ Directory Structure"`

---

## **Phase 2: Consolidate Validation Utilities (P1 High)**

#### **Task: Create Validation Utilities**
- **Status:** `Ready for Spec`
- **Justification:** Centralize validation logic for consistent validation across the application.
- **Target File:**
  - `infra/utils/validation.py` - Validation utilities
- **Required Features:**
  - Data type validation (string, number, email, etc.)
  - Business rule validation
  - File validation (type, size, content)
  - API request validation
  - Database constraint validation
- **Dependencies:** `Create infra/utils/ Directory Structure`
- **Verification:** 
  - Run `python -c "from infra.utils.validation import *"` - should import without errors
  - Test validation functions with various inputs
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - Validation utilities created with all required features
  - All validation types implemented
  - Validation functions tested and working
  - Error messages are clear and helpful
- **Next Action:** Ready for you to run `@spec "Create Validation Utilities"`

---

#### **Task: Create Serialization Utilities**
- **Status:** `Ready for Spec`
- **Justification:** Centralize serialization logic for consistent data handling across the application.
- **Target File:**
  - `infra/utils/serialization.py` - Serialization utilities
- **Required Features:**
  - JSON serialization/deserialization
  - YAML serialization/deserialization
  - XML serialization/deserialization
  - CSV serialization/deserialization
  - Custom object serialization
- **Dependencies:** `Create Validation Utilities`
- **Verification:** 
  - Run `python -c "from infra.utils.serialization import *"` - should import without errors
  - Test serialization functions with various data types
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - Serialization utilities created with all required features
  - All serialization formats implemented
  - Serialization functions tested and working
  - Error handling for invalid data
- **Next Action:** Ready for you to run `@spec "Create Serialization Utilities"`

---

## **Phase 3: Create Crypto and Retry Utilities (P1 High)**

#### **Task: Create Crypto Utilities**
- **Status:** `Ready for Spec`
- **Justification:** Centralize crypto functionality for secure data handling.
- **Target File:**
  - `infra/utils/crypto.py` - Crypto utilities
- **Required Features:**
  - Hashing (SHA-256, MD5, etc.)
  - Encryption/decryption (AES, RSA, etc.)
  - Digital signatures
  - Password hashing (bcrypt, scrypt, etc.)
  - Random number generation
- **Dependencies:** `Create Serialization Utilities`
- **Verification:** 
  - Run `python -c "from infra.utils.crypto import *"` - should import without errors
  - Test crypto functions with various inputs
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - Crypto utilities created with all required features
  - All crypto functions implemented
  - Crypto functions tested and working
  - Security best practices followed
- **Next Action:** Ready for you to run `@spec "Create Crypto Utilities"`

---

#### **Task: Consolidate Retry and Backoff Utilities**
- **Status:** `Ready for Spec`
- **Justification:** Centralize retry logic that's currently scattered across the codebase.
- **Target File:**
  - `infra/utils/retry.py` - Retry and backoff utilities
- **Required Features:**
  - Exponential backoff
  - Linear backoff
  - Custom retry strategies
  - Retry decorators
  - Circuit breaker pattern
- **Dependencies:** `Create Crypto Utilities`
- **Verification:** 
  - Run `python -c "from infra.utils.retry import *"` - should import without errors
  - Test retry functions with various scenarios
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - Retry utilities created with all required features
  - All retry strategies implemented
  - Retry functions tested and working
  - Circuit breaker pattern working
- **Next Action:** Ready for you to run `@spec "Consolidate Retry and Backoff Utilities"`

---

## **Phase 4: Update Error Handling (P1 High)**

#### **Task: Enhance Error Handling Utilities**
- **Status:** `Ready for Spec`
- **Justification:** Enhance existing error handling utilities with additional functionality.
- **Target File:**
  - `infra/utils/error_handling.py` - Enhanced error handling utilities
- **Required Features:**
  - Custom exception classes
  - Error logging and tracking
  - Error response formatting
  - Error recovery strategies
  - Error monitoring integration
- **Dependencies:** `Consolidate Retry and Backoff Utilities`
- **Verification:** 
  - Run `python -c "from infra.utils.error_handling import *"` - should import without errors
  - Test error handling functions
  - Run `uvicorn main:app --reload` - should start without errors
- **Definition of Done:**
  - Error handling utilities enhanced
  - All error handling features implemented
  - Error handling functions tested and working
  - Error monitoring integration working
- **Next Action:** Ready for you to run `@spec "Enhance Error Handling Utilities"`

---

## **Phase 5: Integrate and Test (P2 Medium)**

#### **Task: Update All Utility Imports**
- **Status:** `Ready for Spec`
- **Justification:** Update all imports throughout codebase to use new infra/utils/ structure.
- **Search Commands to Run:**
  - `grep -r "from infra\.utils\|import.*infra\.utils" . --include="*.py"`
- **Dependencies:** `Enhance Error Handling Utilities`
- **Verification:** 
  - Run `grep -r "infra.utils" . --include="*.py"` - should show new imports
  - Run `uvicorn main:app --reload` - should start without errors
  - Run `pytest` - should pass without failures
- **Definition of Done:**
  - All imports updated to use infra/utils/
  - Application starts without errors
  - All tests pass
- **Next Action:** Ready for you to run `@spec "Update All Utility Imports"`

---

#### **Task: Test Utilities End-to-End**
- **Status:** `Ready for Spec`
- **Justification:** Verify that all utility functionality works correctly after consolidation.
- **Test Scenarios:**
  - Validation utilities with various data types
  - Serialization utilities with various formats
  - Crypto utilities with various inputs
  - Retry utilities with various scenarios
  - Error handling utilities
- **Dependencies:** `Update All Utility Imports`
- **Verification:** 
  - Test each utility type manually
  - Test utility functions with edge cases
  - Test error handling
  - Run `pytest` - should pass without failures
- **Definition of Done:**
  - All utility types work correctly
  - All utility functions tested
  - Error handling working correctly
  - All tests pass
- **Next Action:** Ready for you to run `@spec "Test Utilities End-to-End"`

---

**Summary:**
- **Total Tasks:** 8
- **P0 Critical:** 1 task
- **P1 High:** 5 tasks
- **P2 Medium:** 2 tasks
- **Ready for Spec:** 8 tasks

**Quick Reference Commands:**
```bash
# Check for utility code
grep -r "def.*validate\|def.*serialize\|def.*crypto\|def.*util" . --include="*.py"

# Check for retry logic
grep -r "retry\|backoff\|error.*handling" . --include="*.py"

# Test utilities
python -c "from infra.utils import *"

# Test application startup
uvicorn main:app --reload
```

This backlog captures all the utility consolidation work with paranoid-level detail to avoid the painful lessons learned from the SmartSync refactoring.
