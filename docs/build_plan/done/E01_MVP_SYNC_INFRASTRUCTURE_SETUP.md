# E01: MVP Sync Infrastructure Setup

## **Task: Set Up QBO Sync Infrastructure**
- **Status:** `[✅]` Complete
- **Priority:** P0 Critical
- **Justification:** Foundation for all MVP data architecture - without sync infrastructure, we can't mirror data locally and will be stuck with live API calls that won't scale
- **Execution Status:** **COMPLETE** - Background sync jobs implemented and working
- **Dependencies:** S07: Sync and Transaction Log Implementation ✅ (completed)
- **Launch Doc:** Use `docs/build_plan/LAUNCH_EXECUTABLE_TASKS.md` for execution guidance

## CRITICAL: Read These Files First (MANDATORY)

### **Architecture Context (3 most relevant):**
- `docs/architecture/DATA_ARCHITECTURE_SPECIFICATION.md` - Foundational data architecture patterns
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy
- `infra/qbo/README.md` - QBO infrastructure module documentation

### **Product Context (2 most relevant):**
- `docs/build_plan/QBO_MVP_ROADMAP.md` - QBO MVP focus and current phase
- `docs/build_plan/MVP_DATA_ARCHITECTURE_PLAN.md` - MVP implementation plan

### **Current Phase Context:**
- **Phase 0.5**: QBO-only MVP (current focus)
- **Data Architecture**: Local mirroring + SmartSyncService for live data
- **Sync Strategy**: Background jobs every 15 minutes for bills, invoices, balances

## Problem Statement
We need to set up the sync infrastructure to mirror QBO ledger rail data locally. Currently, everything is live API calls that won't scale for multi-client dashboards. We need background jobs syncing bills, invoices, and balances every 15 minutes with historical preservation for compliance and long-term analysis.

## User Story
As a developer working on the QBO ledger rail MVP, I need background sync jobs running every 15 minutes to mirror QBO data locally with historical preservation so that multi-client dashboards can load fast and maintain compliance audit trails.

## Solution Overview
Configure existing `infra/jobs/` infrastructure for QBO sync, create background jobs for bills, invoices, and balances, and set up proper error handling and monitoring.

## CRITICAL: Assumption Validation Before Execution (MANDATORY)
**NEVER execute tasks without validating assumptions against reality.**

### Required Validation Steps:
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

### Discovery Documentation Template:
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving the wrong problems or have unclear scope]
```

### CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

## Initial Files to Fix
- **Discovery Required**: Need to find all existing job infrastructure
- **Expected Pattern**: `infra/jobs/` directory with job definitions
- **Expected Pattern**: Celery/APScheduler configuration
- **Expected Pattern**: Database models for bills, invoices, balances

## MANDATORY: Comprehensive Discovery Commands
```bash
# Find existing job infrastructure
find infra/ -name "*job*" -o -name "*scheduler*" -o -name "*celery*" -o -name "*apscheduler*"
grep -r "celery\|apscheduler\|scheduler" infra/ --include="*.py"
grep -r "background\|async\|task" infra/ --include="*.py"

# Find existing database models
find domains/ -name "models" -type d
find domains/ -name "*.py" -path "*/models/*" -exec grep -l "class.*Model\|Base" {} \;
grep -r "BillModel\|InvoiceModel\|BalanceModel" domains/ --include="*.py"

# Find existing sync patterns
grep -r "sync\|mirror\|cache" infra/ --include="*.py"
grep -r "get_bills\|get_invoices\|get_company_info" infra/ --include="*.py"

# Check current database configuration
grep -r "DATABASE_URL\|SQLALCHEMY" . --include="*.py"
grep -r "postgresql\|sqlite" . --include="*.py"

# Test current state
uvicorn main:app --reload
pytest -k "test_job\|test_sync"
```

## MANDATORY: Recursive Triage Process
1. **For each file found in discovery:**
   - Read the broader context around each occurrence
   - Understand what the method/service/route is doing
   - Determine if it needs simple replacement, contextual update, or complete overhaul
   - Identify all related imports, method calls, and dependencies
2. **Map the real system:**
   - How do these pieces actually connect?
   - What are the real data flows?
   - What would break if you changed it?
3. **Plan comprehensive updates:**
   - Update job definitions AND all calls to those jobs
   - Update database models AND all references
   - Handle edge cases and multiple patterns in same file
   - Update related logic that depends on the changes

## Pattern to Implement
```python
# Background job for syncing QBO data
from celery import Celery
from infra.qbo.smart_sync import SmartSyncService
from domains.ap.models.bill import BillModel
from domains.ar.models.invoice import InvoiceModel
from domains.bank.models.balance import BalanceModel

app = Celery('rowcol')

@app.task
def sync_qbo_data(business_id: str):
    """Sync QBO data for a specific business."""
    smart_sync = SmartSyncService(business_id, "", db)
    
    # Sync bills
    bills_data = await smart_sync.get_bills()
    for bill_data in bills_data.get("bills", []):
        # Update or create bill in local DB
        pass
    
    # Sync invoices
    invoices_data = await smart_sync.get_invoices()
    for invoice_data in invoices_data.get("invoices", []):
        # Update or create invoice in local DB
        pass
    
    # Sync balances
    company_info = await smart_sync.get_company_info()
    for balance_data in company_info.get("balances", []):
        # Update or create balance in local DB
        pass

# Scheduled job configuration
from celery.schedules import crontab

app.conf.beat_schedule = {
    'sync-qbo-data': {
        'task': 'sync_qbo_data',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}
```

## File Examples to Follow
- `infra/qbo/smart_sync.py` - Example of SmartSyncService usage
- `domains/ap/models/bill.py` - Example of database model
- `domains/ar/models/invoice.py` - Example of database model
- `domains/bank/models/balance.py` - Example of database model

## Required Imports/Changes
- Add: `from celery import Celery`
- Add: `from celery.schedules import crontab`
- Add: `from infra.qbo.smart_sync import SmartSyncService`
- Update: Database models to support sync timestamps
- Add: Error handling and retry logic

## Dependencies
- Celery or APScheduler for background jobs
- Database models for bills, invoices, balances
- SmartSyncService for QBO API calls
- Database connection for local storage

## MANDATORY: Comprehensive Cleanup Requirements
- **File Operations:** Use `cp` then `rm` for moves, never just `mv`
- **Import Cleanup:** Remove ALL old imports, add ALL new imports
- **Reference Cleanup:** Update ALL references to renamed methods/classes
- **Dependency Cleanup:** Update ALL dependent code
- **Test Cleanup:** Update ALL test files that reference changed code
- **Documentation Cleanup:** Update ALL documentation references

## Verification
- Run `uvicorn main:app --reload` - should start without errors
- Run `celery -A main.celery worker --loglevel=info` - should start worker
- Run `celery -A main.celery beat --loglevel=info` - should start scheduler
- Run `pytest -k "test_sync"` - should pass sync tests
- Check database for synced data after 15 minutes

## Definition of Done
- Background jobs configured and running
- Bills, invoices, balances syncing every 15 minutes
- Error handling and retry logic implemented
- Database models updated with sync timestamps
- Monitoring and logging in place
- All discovery findings addressed

## Progress Tracking
- Update status to `[🔄]` when starting work
- Update status to `[✅]` when task is complete
- Update status to `[❌]` if blocked or failed

## Git Commit
- After completing verification, commit the specific files modified:
- `git add [specific-files-modified]`
- `git commit -m "feat: E01 - Set up QBO sync infrastructure"`

## Todo List Integration
- Create Cursor todo for this task when starting
- Update todo status as work progresses
- Mark todo complete when task is done
- Add cleanup todos for discovered edge cases
- Remove obsolete todos when files are deleted
- Ensure todo list reflects current system state

## Related Tasks
- **E02**: Fix Domain Services for Local Data Access
- **E03**: Create Purpose-Specific Data Orchestrators
- **S02**: Data Orchestrator Architecture Fix (parent solutioning task)

