# E18: Unified Multi-Rail Architecture Implementation

## **Task: Implement QBO-Honest Architecture with _parked/ Pattern**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** Current domain and runway services assume QBO can execute payments and create invoices, but QBO is only a ledger rail. We need to create QBO-honest services and move execution capabilities to _parked/ for future Ramp/Stripe implementation.
- **Execution Status:** **Execution-Ready**
- **Launch Doc:** Use `docs/build_plan/LAUNCH_EXECUTABLE_TASKS.md` for execution guidance

## **CRITICAL: Read These Files First (MANDATORY)**

### **Architecture Context (3 most relevant):**
- `docs/architecture/DATA_ARCHITECTURE_SPECIFICATION.md` - Foundational data architecture patterns
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy

### **Product Context (1 most relevant):**
- `docs/build_plan/QBO_MVP_ROADMAP.md` - QBO MVP focus and current phase

### **Current Phase Context:**
- **Phase 0.5**: QBO-only MVP (current focus)
- **Feature Gating**: QBO-only mode enabled, Ramp/Plaid/Stripe disabled
- **Payment Execution**: QBO sync-only (no execution), Ramp execution gated
- **Data Architecture**: Local mirroring + QBOSyncService for live data

### **Task-Specific Context (3 most relevant):**
- `domains/ap/services/bill_ingestion.py` - Current over-extended AP service
- `domains/ar/services/invoice.py` - Already QBO-honest AR service
- `runway/services/experiences/tray.py` - Runway service with execution assumptions

## **Problem Statement**

**Current State**: Domain and runway services assume QBO can do everything:
- `domains/ap/services/bill_ingestion.py` - Has payment execution methods
- `runway/services/experiences/tray.py` - Assumes payment execution
- `runway/routes/bills.py` - Has payment execution routes
- Most tests test QBO execution capabilities

**Reality**: QBO is only a ledger rail - it can sync data but can't execute payments, create invoices, or verify bank accounts.

**Solution**: Create QBO-honest services and move execution capabilities to `_parked/` for future rail implementation.

## **User Story**
"As a developer working on the QBO MVP, I need QBO-honest services that only do what QBO actually supports, with execution capabilities moved to _parked/ for future Ramp/Stripe implementation, so that the system is honest about QBO's limitations and ready for multi-rail architecture."

## **Solution Overview**
1. **Rename `bill_ingestion.py` → `bill.py`** - We're not ingesting, we're syncing from QBO
2. **Create QBO-honest domain services** - Remove execution methods, keep only QBO-compatible features
3. **Humble runway services** - Remove QBO execution assumptions
4. **Move execution code to _parked/** - Preserve functionality for future rails
5. **Update all imports and references** - Comprehensive cleanup
6. **Clean up tests** - Move execution tests to _parked/, keep sync tests

## **CRITICAL: Assumption Validation Before Execution (MANDATORY)**

### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

### **Discovery Documentation Template:**
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
- [List where tasks may be solving wrong problems or have unclear scope]
```

## **MANDATORY: Comprehensive Discovery Commands**

```bash
# Find all bill_ingestion references
grep -r "bill_ingestion" . --include="*.py"
grep -r "from domains\.ap\.services\.bill_ingestion" . --include="*.py"
grep -r "import.*bill_ingestion" . --include="*.py"

# Find all execution method calls
grep -r "execute_payment\|create_invoice\|send_invoice" . --include="*.py"
grep -r "approve_bill\|schedule_payment" . --include="*.py"

# Find runway services with execution assumptions
grep -r "payment.*execution\|invoice.*creation" runway/ --include="*.py"
grep -r "BillService\|InvoiceService" runway/ --include="*.py"

# Find test files that test execution
find tests/ -name "*.py" -exec grep -l "execute_payment\|create_invoice" {} \;
find tests/ -name "*.py" -exec grep -l "approve_bill\|schedule_payment" {} \;

# Check current _parked/ structure
ls -la _parked/
find _parked/ -name "*.py" -type f

# Test current state
uvicorn main:app --reload
pytest -k "test_bill" --collect-only
```

## **MANDATORY: Recursive Triage Process**

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
   - Rename bill_ingestion → bill AND all calls to those methods
   - Remove execution methods AND all references
   - Update imports AND all dependent code
   - Handle edge cases and multiple patterns in same file
   - Update related logic that depends on the changes

## **Pattern to Implement**

### **Step 1: Create QBO-Honest Bill Service**
```python
# domains/ap/services/bill.py (RENAME from bill_ingestion.py)
class BillService:
    """QBO-honest AP bill service - sync from QBO, CRUD + business logic only."""
    
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        self.qbo_sync = QBOSyncService(business_id, "", db)
    
    # KEEP: Basic CRUD and business logic
    def get_bill_by_qbo_id(self, qbo_id: str) -> Bill:
        """Get bill by QBO ID."""
        return self.db.query(Bill).filter(
            Bill.business_id == self.business_id,
            Bill.qbo_bill_id == qbo_id
        ).first()
    
    def get_payment_ready_bills(self) -> List[Bill]:
        """Query bills ready for payment (but don't execute)."""
        return self.db.query(Bill).filter(
            Bill.business_id == self.business_id,
            Bill.status == 'unpaid',
            Bill.amount > 0,
            Bill.due_date.isnot(None)
        ).all()
    
    def get_bills_by_vendor(self, vendor_name: str) -> List[Bill]:
        """Query bills by vendor."""
        return self.db.query(Bill).filter(
            Bill.business_id == self.business_id,
            Bill.vendor_name == vendor_name
        ).all()
    
    # KEEP: Sync delegation (we're syncing from QBO, not ingesting)
    async def sync_bills_from_qbo(self) -> Dict[str, Any]:
        """Sync bills from QBO - delegate to QBOSyncService."""
        return await self.qbo_sync.get_bills()
    
    # REMOVE: Payment execution methods (move to _parked/)
    # REMOVE: Bill ingestion methods (we're not uploading bills)
```

### **Step 2: Create _parked/ Execution Services**
```python
# _parked/ap_execution/bill_payment_service.py (NEW)
class BillPaymentService:
    """A/P execution service - will be implemented by Ramp."""
    
    async def approve_bill_for_payment(self, bill_id: str) -> PaymentIntent:
        """Approve bill for payment execution."""
        # Future Ramp integration
        pass
    
    async def execute_payment(self, payment_intent_id: str) -> PaymentResult:
        """Execute payment through Ramp."""
        # Future Ramp integration
        pass
    
    async def schedule_payment(self, bill_id: str, payment_date: datetime) -> ScheduledPayment:
        """Schedule payment for future execution."""
        # Future Ramp integration
        pass

# _parked/ar_execution/invoice_management_service.py (NEW)
class InvoiceManagementService:
    """A/R execution service - will be implemented by Stripe."""
    
    async def create_invoice(self, customer_id: str, items: List[InvoiceItem]) -> Invoice:
        """Create invoice for customer."""
        # Future Stripe integration
        pass
    
    async def send_invoice(self, invoice_id: str) -> SendResult:
        """Send invoice to customer."""
        # Future Stripe integration
        pass
```

### **Step 3: Humble Runway Services**
```python
# runway/services/experiences/tray.py (UPDATE)
class TrayService:
    """Hygiene tray service - QBO-honest, no execution assumptions."""
    
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        # Use QBO-honest services
        self.bill_service = BillService(db, business_id)
        self.invoice_service = InvoiceService(db, business_id)
    
    # REMOVE: Payment execution methods
    # REMOVE: Invoice creation methods
    # KEEP: Data querying and display methods
    # KEEP: Sync status methods
```

## **File Examples to Follow**
- `domains/ar/services/invoice.py` - Already QBO-honest AR service
- `domains/bank/services/balance_service.py` - Already QBO-honest bank service
- `_parked/domains/ar/services/invoice_with_policy.py` - Example of _parked/ structure

## **Required Imports/Changes**
- **Rename**: `domains/ap/services/bill_ingestion.py` → `domains/ap/services/bill.py`
- **Update**: All imports from `bill_ingestion` to `bill`
- **Remove**: Execution methods from domain services
- **Move**: Execution methods to `_parked/{ap_execution,ar_execution,bank_verification}/`
- **Update**: Runway services to use QBO-honest domain services
- **Update**: All test files to use new imports and remove execution tests

## **Dependencies**
- E11: Domain sync duplication fix (in progress)
- S01: QBO sandbox testing strategy (for test cleanup)

## **MANDATORY: Comprehensive Cleanup Requirements**

### **File Operations:**
- **Rename**: `bill_ingestion.py` → `bill.py` using `cp` then `rm`
- **Create**: `_parked/{ap_execution,ar_execution,bank_verification}/` directories
- **Move**: Execution methods to appropriate _parked/ services
- **Update**: All 18+ import references

### **Import Cleanup:**
- **Remove**: ALL old `bill_ingestion` imports
- **Add**: ALL new `bill` imports
- **Update**: ALL references to renamed methods/classes
- **Update**: ALL dependent code

### **Test Cleanup:**
- **Move**: Execution tests to `_parked/tests/`
- **Update**: Sync tests to use new imports
- **Remove**: Mock-heavy tests (replace with real sandbox data)
- **Update**: Integration tests to focus on QBO sync-only

### **Runway Service Cleanup:**
- **Remove**: Payment execution methods from runway services
- **Remove**: Invoice creation methods from runway services
- **Update**: Data orchestrators to use QBO-honest services
- **Update**: Routes to remove execution endpoints

## **Verification**

### **QBO-Honest Services:**
- ✅ Domain services only do what QBO supports
- ✅ No execution methods in QBO-only services
- ✅ Clear documentation of QBO limitations
- ✅ Advanced features preserved in _parked/

### **Import Updates:**
- ✅ Run `grep -r "bill_ingestion" . --include="*.py"` - should return no results
- ✅ Run `grep -r "from domains\.ap\.services\.bill" . --include="*.py"` - should show new usage
- ✅ Run `grep -r "execute_payment\|create_invoice" . --include="*.py"` - should only show _parked/ references

### **Test Cleanup:**
- ✅ Run `pytest -k "test_bill"` - should pass with new imports
- ✅ Run `pytest -k "test_payment_execution"` - should only run _parked/ tests
- ✅ Run `uvicorn main:app --reload` - should start without errors

### **Runway Service Humbling:**
- ✅ Runway services don't assume QBO execution
- ✅ Data orchestrators use QBO-honest services
- ✅ Routes don't expose execution endpoints

## **Definition of Done**

- [ ] `bill_ingestion.py` renamed to `bill.py`
- [ ] All 18+ import references updated
- [ ] Execution methods moved to _parked/ services
- [ ] Runway services humbled (no execution assumptions)
- [ ] Tests cleaned up (execution tests moved to _parked/)
- [ ] All imports working correctly
- [ ] No broken references or imports anywhere
- [ ] Comprehensive cleanup completed
- [ ] QBO-honest architecture implemented
- [ ] Ready for multi-rail future

## **Progress Tracking**

- Update status to `[🔄]` when starting work
- Update status to `[✅]` when task is complete
- Update status to `[❌]` if blocked or failed

## **Git Commit**

After completing verification, commit the specific files modified:
- `git add [specific-files-modified]`
- `git commit -m "feat: E18 - Implement QBO-honest architecture with _parked/ pattern"`

## **Todo List Integration**

- Create Cursor todo for this task when starting
- Update todo status as work progresses
- Mark todo complete when task is done
- Add cleanup todos for discovered edge cases
- Remove obsolete todos when files are deleted
- Ensure todo list reflects current system state


## **Critical Lessons Learned**

### **Why This Task is Execution-Ready:**
1. **Clear Implementation Pattern** - QBO-honest services with _parked/ pattern
2. **Specific Files Identified** - 18+ files need import updates
3. **Comprehensive Discovery Commands** - Find all occurrences
4. **Recursive Triage Process** - Understand context before changing
5. **Comprehensive Cleanup Requirements** - Handle all edge cases
6. **No "Figure Out" Language** - Everything is specific and actionable

### **Success Patterns:**
1. **Assumption Validation** - Always validate task assumptions against actual codebase
2. **Comprehensive Discovery** - Find ALL occurrences, not just initial files
3. **Recursive Triage** - Understand context before making changes
4. **Comprehensive Cleanup** - Handle all edge cases and dependencies
5. **Proper File Operations** - Use `cp` then `rm` for moves
6. **Todo Integration** - Track progress and discovered edge cases
