# E03: Create Purpose-Specific Data Orchestrators

## **Task: Build Purpose-Specific Data Orchestrators**
- **Status:** `[❌]` Superseded by S13
- **Priority:** P0 Critical
- **Justification:** Current data orchestrators pull the same generic QBO data without purpose-specific filtering. Need to create orchestrators that aggregate from domain services and provide filtered data for specific experiences.
- **Execution Status:** **SUPERSEDED BY S13_UNIFIED_MULTI_RAIL_ARCHITECTURE**
- **Dependencies:** S13: Unified Multi-Rail Architecture Strategy (consolidates E03, E03_HUMBLE_QBO_SERVICES, S11, S12)
- **Launch Doc:** Use `docs/build_plan/LAUNCH_EXECUTABLE_TASKS.md` for execution guidance

## CRITICAL: Read These Files First (MANDATORY)

### **Architecture Context (3 most relevant):**
- `docs/architecture/DATA_ARCHITECTURE_SPECIFICATION.md` - Foundational data architecture patterns
- `docs/architecture/ADR-006-data-orchestrator-pattern.md` - Data orchestrator patterns
- `docs/build_plan/working/S02_DATA_ORCHESTRATOR_ARCHITECTURE_FIX.md` - Data orchestrator issues and solutions

### **Product Context (1 most relevant):**
- `docs/build_plan/MVP_DATA_ARCHITECTURE_PLAN.md` - MVP implementation plan

### **Current Phase Context:**
- **Phase 0.5**: QBO-only MVP (current focus)
- **Data Architecture**: Local mirroring + SmartSyncService for live data
- **Orchestrator Pattern**: Aggregate from domain services, not direct API calls

## Problem Statement
Current data orchestrators pull the same raw data from SmartSyncService without purpose-specific filtering. We need to create orchestrators that aggregate from domain services and provide filtered data for specific experiences (hygiene vs decisions vs reporting).

## User Story
As a developer working on the QBO MVP, I need purpose-specific data orchestrators that aggregate from domain services and provide filtered data for specific experiences so that each experience gets the data it needs.

## Solution Overview
Create three purpose-specific data orchestrators: `HygieneTrayDataOrchestrator` (bills with issues), `DecisionConsoleDataOrchestrator` (bills ready for decision), and `DigestDataOrchestrator` (aggregates from the other two).

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
- **Discovery Required**: Need to find existing data orchestrators
- **Expected Pattern**: `runway/services/data_orchestrators/*.py` files
- **Expected Pattern**: Orchestrators calling SmartSyncService directly
- **Expected Pattern**: Missing purpose-specific filtering

## MANDATORY: Comprehensive Discovery Commands
```bash
# Find existing data orchestrators
find runway/ -name "*data_orchestrator*" -type f
find runway/ -name "*orchestrator*" -type f
grep -r "DataOrchestrator" runway/ --include="*.py"

# Find orchestrators calling SmartSyncService directly
grep -r "SmartSyncService" runway/services/data_orchestrators/ --include="*.py"
grep -r "smart_sync\." runway/services/data_orchestrators/ --include="*.py"
grep -r "get_bills\|get_invoices\|get_company_info" runway/services/data_orchestrators/ --include="*.py"

# Find purpose-specific filtering needs
grep -r "hygiene\|issues\|incomplete" runway/ --include="*.py"
grep -r "decision\|ready\|complete" runway/ --include="*.py"
grep -r "digest\|aggregate" runway/ --include="*.py"

# Check current orchestrator patterns
grep -r "def get_" runway/services/data_orchestrators/ --include="*.py"
grep -r "def _filter" runway/services/data_orchestrators/ --include="*.py"

# Test current state
uvicorn main:app --reload
pytest -k "test_data_orchestrator"
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
   - Update orchestrator methods AND all calls to those methods
   - Update data access patterns AND all references
   - Handle edge cases and multiple patterns in same file
   - Update related logic that depends on the changes

## Pattern to Implement
```python
# Purpose-specific data orchestrator pattern
from runway.services.data_orchestrators.base_data_orchestrator import BaseDataOrchestrator
from domains.ap.services.bill_ingestion import BillService
from domains.ar.services.invoice import InvoiceService
from domains.bank.services.balance_service import BalanceService

class HygieneTrayDataOrchestrator(BaseDataOrchestrator):
    """Data orchestrator for hygiene tray - bills and invoices with issues."""
    
    def __init__(self, db, business_id: str):
        super().__init__(db, business_id)
        self.bill_service = BillService(db, business_id)
        self.invoice_service = InvoiceService(db, business_id)
    
    async def get_hygiene_data(self) -> Dict[str, Any]:
        """Get bills and invoices with hygiene issues."""
        # Get bills with incomplete fields
        bills_with_issues = self.bill_service.get_bills_with_issues()
        
        # Get invoices with missing data
        invoices_with_issues = self.invoice_service.get_invoices_with_issues()
        
        return {
            "bills_with_issues": [
                {
                    "id": bill.bill_id,
                    "vendor_name": bill.vendor_name,
                    "amount": bill.amount,
                    "due_date": bill.due_date,
                    "issues": self._identify_bill_issues(bill)
                }
                for bill in bills_with_issues
            ],
            "invoices_with_issues": [
                {
                    "id": invoice.invoice_id,
                    "customer_name": invoice.customer_name,
                    "amount": invoice.amount,
                    "due_date": invoice.due_date,
                    "issues": self._identify_invoice_issues(invoice)
                }
                for invoice in invoices_with_issues
            ]
        }
    
    def _identify_bill_issues(self, bill) -> List[str]:
        """Identify specific issues with a bill."""
        issues = []
        if not bill.vendor_name:
            issues.append("Missing vendor name")
        if not bill.due_date:
            issues.append("Missing due date")
        if not bill.amount:
            issues.append("Missing amount")
        return issues

class DecisionConsoleDataOrchestrator(BaseDataOrchestrator):
    """Data orchestrator for decision console - bills and invoices ready for decision."""
    
    def __init__(self, db, business_id: str):
        super().__init__(db, business_id)
        self.bill_service = BillService(db, business_id)
        self.invoice_service = InvoiceService(db, business_id)
    
    async def get_decision_data(self) -> Dict[str, Any]:
        """Get bills and invoices ready for decision."""
        # Get bills ready for decision
        bills_ready = self.bill_service.get_bills_ready_for_decision()
        
        # Get invoices ready for collection
        invoices_ready = self.invoice_service.get_invoices_ready_for_decision()
        
        return {
            "bills_ready": [
                {
                    "id": bill.bill_id,
                    "vendor_name": bill.vendor_name,
                    "amount": bill.amount,
                    "due_date": bill.due_date,
                    "priority": self._calculate_bill_priority(bill)
                }
                for bill in bills_ready
            ],
            "invoices_ready": [
                {
                    "id": invoice.invoice_id,
                    "customer_name": invoice.customer_name,
                    "amount": invoice.amount,
                    "due_date": invoice.due_date,
                    "priority": self._calculate_invoice_priority(invoice)
                }
                for invoice in invoices_ready
            ]
        }

class DigestDataOrchestrator(BaseDataOrchestrator):
    """Data orchestrator for digest - aggregates from hygiene and decision orchestrators."""
    
    def __init__(self, db, business_id: str):
        super().__init__(db, business_id)
        self.hygiene_orchestrator = HygieneTrayDataOrchestrator(db, business_id)
        self.decision_orchestrator = DecisionConsoleDataOrchestrator(db, business_id)
        self.balance_service = BalanceService(db, business_id)
    
    async def get_digest_data(self) -> Dict[str, Any]:
        """Get aggregated digest data from hygiene and decision orchestrators."""
        # Get hygiene data
        hygiene_data = await self.hygiene_orchestrator.get_hygiene_data()
        
        # Get decision data
        decision_data = await self.decision_orchestrator.get_decision_data()
        
        # Get current balances (live data)
        balances = await self.balance_service.get_current_balances()
        
        return {
            "hygiene_summary": {
                "bills_with_issues_count": len(hygiene_data["bills_with_issues"]),
                "invoices_with_issues_count": len(hygiene_data["invoices_with_issues"])
            },
            "decision_summary": {
                "bills_ready_count": len(decision_data["bills_ready"]),
                "invoices_ready_count": len(decision_data["invoices_ready"])
            },
            "current_balances": balances,
            "hygiene_data": hygiene_data,
            "decision_data": decision_data
        }
```

## File Examples to Follow
- `runway/services/data_orchestrators/digest_data_orchestrator.py` - Example of current orchestrator
- `domains/ap/services/bill_ingestion.py` - Example of domain service
- `domains/ar/services/invoice.py` - Example of domain service
- `domains/bank/services/balance_service.py` - Example of balance service

## Required Imports/Changes
- Add: `from domains.ap.services.bill_ingestion import BillService`
- Add: `from domains.ar.services.invoice import InvoiceService`
- Add: `from domains.bank.services.balance_service import BalanceService`
- Update: Orchestrators to aggregate from domain services
- Add: Purpose-specific filtering methods
- Remove: Direct SmartSyncService calls

## Dependencies
- Domain services for data access
- Base data orchestrator class
- Purpose-specific filtering logic
- Multi-client data coordination

## MANDATORY: Comprehensive Cleanup Requirements
- **File Operations:** Use `cp` then `rm` for moves, never just `mv`
- **Import Cleanup:** Remove ALL old imports, add ALL new imports
- **Reference Cleanup:** Update ALL references to renamed methods/classes
- **Dependency Cleanup:** Update ALL dependent code
- **Test Cleanup:** Update ALL test files that reference changed code
- **Documentation Cleanup:** Update ALL documentation references

## Verification
- Run `uvicorn main:app --reload` - should start without errors
- Run `pytest -k "test_data_orchestrator"` - should pass orchestrator tests
- Check that orchestrators aggregate from domain services
- Check that purpose-specific filtering works
- Verify digest orchestrator aggregates from other two

## Definition of Done
- Three purpose-specific data orchestrators created
- Orchestrators aggregate from domain services, not SmartSyncService
- Purpose-specific filtering implemented
- Digest orchestrator aggregates from hygiene and decision orchestrators
- All discovery findings addressed

## Progress Tracking
- Update status to `[🔄]` when starting work
- Update status to `[✅]` when task is complete
- Update status to `[❌]` if blocked or failed

## Git Commit
- After completing verification, commit the specific files modified:
- `git add [specific-files-modified]`
- `git commit -m "feat: E03 - Create purpose-specific data orchestrators"`

## Todo List Integration
- Create Cursor todo for this task when starting
- Update todo status as work progresses
- Mark todo complete when task is done
- Add cleanup todos for discovered edge cases
- Remove obsolete todos when files are deleted
- Ensure todo list reflects current system state

## Related Tasks
- **E01**: MVP Sync Infrastructure Setup (dependency)
- **E02**: Fix Domain Services for Local Data Access (dependency)
- **S02**: Data Orchestrator Architecture Fix (parent solutioning task)

