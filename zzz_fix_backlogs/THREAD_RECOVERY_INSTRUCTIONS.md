# Thread Recovery Instructions - SmartSync Architecture Alignment

## **CRITICAL: Thread is Off Track - Immediate Action Required**

### **What Went Wrong**
The thread was following **outdated task instructions** that contradicted the current architecture. The executable tasks were written based on the OLD approach (moving utilities around) instead of the NEW approach (SmartSyncService as central orchestration layer).

### **Specific Problem**
- **Task 4** told the thread to import `SyncTimingManager` and `SyncCache` directly
- **This is WRONG** according to ADR-005 and the current architecture
- **Correct approach**: Use `SmartSyncService` as the single entry point for all sync operations

### **Evidence of Wrong Direction**
The thread implemented this pattern in multiple files:
```python
# WRONG - This is what the thread did in tray.py, runway_calculator.py, etc:
from infra.jobs.enums import SyncStrategy, SyncPriority
from infra.jobs.sync_strategies import SyncTimingManager
from infra.jobs.job_storage import SyncCache
self.timing_manager = SyncTimingManager(business_id)
self.cache = SyncCache(business_id, default_ttl_minutes=15)
```

**Files that were incorrectly modified:**
- `runway/experiences/tray.py`
- `runway/core/runway_calculator.py`
- `runway/experiences/digest.py`
- `runway/experiences/test_drive.py`
- `infra/queue/job_storage.py`
- `infra/scheduler/job_providers.py`
- `infra/scheduler/digest_jobs.py`

**The thread also started deleting directories prematurely** before completing the SmartSyncService replacement, which is the wrong order.

### **What Should Have Been Done**
```python
# CORRECT - This is what should be done:
from infra.jobs import SmartSyncService
self.smart_sync = SmartSyncService(business_id)
# Then use self.smart_sync.should_sync(), self.smart_sync.get_cache(), etc.
```

## **Immediate Recovery Steps**

### **Step 1: Stop Current Work**
- **STOP** working on the current task
- **DO NOT** continue with the current approach
- **READ** this entire recovery document first

### **Step 2: Revert ALL Wrong Changes**
```bash
# Check what files were modified during the erroneous Task 4 work
git status

# Revert ALL files that were changed with the wrong approach
git checkout HEAD -- runway/experiences/tray.py
git checkout HEAD -- infra/queue/job_storage.py
git checkout HEAD -- infra/scheduler/job_providers.py
git checkout HEAD -- infra/scheduler/digest_jobs.py
git checkout HEAD -- runway/core/runway_calculator.py
git checkout HEAD -- runway/experiences/digest.py
git checkout HEAD -- runway/experiences/test_drive.py

# Check if any other files were modified
git status

# Revert any remaining files that were changed
git checkout HEAD -- [any_other_modified_files]
```

### **Step 3: Reread Updated Tasks**
- **READ** `zzz_fix_backlogs/0_EXECUTABLE_TASKS.md` - it has been updated
- **FOCUS** on Task 4 - it now shows the correct SmartSyncService approach
- **UNDERSTAND** that all sync operations go through SmartSyncService

### **Step 4: Verify Architecture Understanding**
- **READ** `docs/architecture/ADR-005-qbo-api-strategy.md` - understand the central orchestration layer
- **UNDERSTAND** that SmartSyncService encapsulates all utilities
- **NEVER** import utilities directly - always use SmartSyncService

## **Updated Task 4 Instructions**

### **What Task 4 Actually Wants**
Task 4 has TWO parts that must be done in sequence:

#### **Part A: Replace Direct Utility Imports with SmartSyncService**
Replace direct utility imports with SmartSyncService usage in domains/ and runway/ files:

```python
# OLD (wrong):
from infra.jobs.sync_strategies import SyncTimingManager
from infra.jobs.job_storage import SyncCache
from infra.jobs.enums import SyncStrategy, SyncPriority

class SomeService:
    def __init__(self, business_id: str):
        self.timing_manager = SyncTimingManager(business_id)
        self.cache = SyncCache(business_id)

# NEW (correct):
from infra.jobs import SmartSyncService

class SomeService:
    def __init__(self, business_id: str):
        self.smart_sync = SmartSyncService(business_id)

    def some_method(self):
        # Use SmartSyncService methods instead of direct utilities
        if self.smart_sync.should_sync("qbo", SyncStrategy.SCHEDULED):
            data = self.smart_sync.get_cache("qbo")
            if not data:
                # Do sync work
                self.smart_sync.set_cache("qbo", result)
                self.smart_sync.record_user_activity("sync")
```

#### **Part B: Clean Up infra/ Directory Structure**
After Part A is complete, clean up the infra/ directory so that `infra/jobs/` is the single source of truth and old directories are removed:

- **Files to Update in Part A:**
  - `runway/experiences/tray.py` - Replace direct utility imports with SmartSyncService
  - `runway/core/runway_calculator.py` - Replace direct utility imports with SmartSyncService
  - `runway/experiences/digest.py` - Replace direct utility imports with SmartSyncService
  - `runway/experiences/test_drive.py` - Replace direct utility imports with SmartSyncService

- **Files to Update in Part B:**
  - `infra/queue/job_storage.py` - Update imports to use infra/jobs/ structure
  - `infra/scheduler/job_providers.py` - Update imports to use infra/jobs/ structure
  - `infra/scheduler/digest_jobs.py` - Update imports to use infra/jobs/ structure

- **Directories to Delete in Part B:**
  - `infra/cache/` (entire directory)
  - `infra/queue/` (entire directory)
  - `infra/scheduler/` (entire directory)
  - `infra/utils/sync_strategies.py` (moved to `infra/jobs/sync_strategies.py`)

### **Critical: Two-Step Process**
1. **First**: Replace direct utility imports with SmartSyncService in domains/ and runway/ files
2. **Then**: Clean up infra/ directory structure and remove old directories
3. **Never**: Do both at the same time - this creates confusion and errors

### **Verification Commands**
```bash
# Check for direct utility imports (should return no results)
grep -r "from infra\.jobs\.(sync_strategies|job_storage|enums)" . --include="*.py"
grep -r "SyncTimingManager\|SyncCache" . --include="*.py"

# Check for SmartSyncService usage (should show new imports)
grep -r "SmartSyncService" . --include="*.py"

# Test application startup
uvicorn main:app --reload
```

## **New Safeguard: Architecture Alignment Check**

### **Before Starting Any Task**
1. **READ** the task description completely
2. **CHECK** if the task aligns with ADR-005 architecture
3. **VERIFY** that the task promotes SmartSyncService as central orchestration layer
4. **STOP** if the task seems to contradict the overall architecture direction

### **Red Flags to Watch For**
- Tasks that ask you to import utilities directly (`SyncTimingManager`, `SyncCache`)
- Tasks that bypass SmartSyncService
- Tasks that don't mention SmartSyncService as the central layer
- Tasks that seem to contradict ADR-005

### **When to Stop and Ask for Help**
- If a task seems to contradict the overall architecture
- If you're unsure about the correct approach
- If the task instructions seem outdated or wrong
- If you see red flags in the task description

## **Key Architecture Principles to Remember**

1. **SmartSyncService is the central orchestration layer** for ALL QBO interactions
2. **NEVER import utilities directly** - always use SmartSyncService
3. **SmartSyncService encapsulates** sync timing, caching, user activity tracking, rate limiting, retry logic, and deduplication
4. **All sync operations** should go through SmartSyncService methods
5. **User actions** = direct QBO API calls wrapped in SmartSyncService
6. **Background syncs** = SmartSyncService + QBOBulkScheduledService

## **Recovery Checklist**

- [ ] Stop current work immediately
- [ ] Revert wrong changes made so far
- [ ] Reread updated Task 4 instructions
- [ ] Read ADR-005 to understand architecture
- [ ] Implement Task 4 with SmartSyncService approach
- [ ] Verify no direct utility imports remain
- [ ] Test application startup
- [ ] Continue with remaining tasks using correct architecture

## **Questions to Ask Yourself**

1. **Does this task promote SmartSyncService as the central orchestration layer?**
2. **Am I importing utilities directly instead of using SmartSyncService?**
3. **Does this approach align with ADR-005?**
4. **Am I following the pattern shown in the task examples?**

If the answer to any of these is "no" or "I'm not sure", **STOP** and ask for clarification.

---

**Remember**: The goal is to have SmartSyncService as the single entry point for all sync operations. Don't bypass it by importing utilities directly.
