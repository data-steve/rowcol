# S13: Unified Multi-Rail Architecture Strategy

## **Task: Design Unified Multi-Rail Architecture - QBO-Honest Services + Domain Integration + Data Orchestrators**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** E03, E03_HUMBLE_QBO_SERVICES, S11, and S12 are all solving the same intertwined problem. We need one unified strategy that addresses QBO limitations, domain organization, sync integration, and data orchestrator patterns together.
- **Execution Status:** **Needs-Solutioning**

## **The Unified Problem**

**Current State**: We have 4 separate tasks trying to solve the same architectural problem:
- **E03_HUMBLE_QBO_SERVICES**: QBO can only do what QBO actually does
- **S12**: How to organize domains across multiple rails  
- **S11**: How domain services integrate with sync architecture
- **E03**: What data orchestrators use after the above is done

**The Reality**: These are all the same problem! We need:
1. **QBO-honest services** that only do what QBO supports
2. **Multi-rail domain organization** with _parked/ pattern
3. **Domain sync integration** that works with the new architecture
4. **Data orchestrators** that use the corrected services

## **Unified Architecture Strategy**

### **Phase 1: QBO-Honest Architecture (Current MVP)**

```
domains/
├── qbo/                           # QBO ledger rail (read-only sync)
│   └── services/
│       └── sync_service.py        # QBOSyncService - sync + transaction logs
├── ap/                            # A/P domain (QBO-honest business logic)
│   └── services/
│       └── bill_service.py        # CRUD + business logic only
├── ar/                            # A/R domain (QBO-honest business logic)  
│   └── services/
│       └── invoice_service.py     # CRUD + business logic only
└── bank/                          # Bank domain (QBO-honest business logic)
    └── services/
        └── balance_service.py     # CRUD + business logic only

_parked/                           # QBO-incompatible features
├── ap_execution/                  # A/P execution (future Ramp)
│   └── bill_payment_service.py
├── ar_execution/                  # A/R execution (future Stripe)
│   └── invoice_management_service.py
└── bank_verification/             # Bank verification (future Plaid)
    └── account_verification_service.py

runway/services/data_orchestrators/
├── hygiene_tray_data_orchestrator.py    # Uses domain services + QBOSyncService
├── decision_console_data_orchestrator.py # Uses domain services + QBOSyncService
└── digest_data_orchestrator.py          # Aggregates from other orchestrators
```

### **Phase 2: Multi-Rail Architecture (Future)**

```
domains/
├── qbo/                           # QBO ledger rail
├── ramp/                          # Ramp A/P execution rail
├── plaid/                         # Plaid verification rail
├── stripe/                        # Stripe A/R execution rail
├── ap/                            # A/P domain (orchestrates across rails)
├── ar/                            # A/R domain (orchestrates across rails)
└── bank/                          # Bank domain (orchestrates across rails)
```

## **Unified Service Patterns**

### **Pattern 1: QBO-Honest Domain Services**

```python
# domains/ap/services/bill_service.py
class BillService:
    """A/P domain service - QBO-honest business logic only."""
    
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        # Use QBOSyncService for sync operations
        self.qbo_sync = QBOSyncService(business_id, "", db)
    
    # BUSINESS LOGIC (QBO-compatible)
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
    
    # SYNC OPERATIONS (delegate to QBOSyncService)
    async def sync_bills_from_qbo(self) -> Dict[str, Any]:
        """Sync bills from QBO - delegate to QBOSyncService."""
        return await self.qbo_sync.get_bills()
    
    # NO EXECUTION METHODS - those go in _parked/ap_execution/
```

### **Pattern 2: Data Orchestrator Integration**

```python
# runway/services/data_orchestrators/hygiene_tray_data_orchestrator.py
class HygieneTrayDataOrchestrator:
    """Data orchestrator for hygiene tray - bills with issues."""
    
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        # Use domain services for business logic
        self.bill_service = BillService(db, business_id)
        self.invoice_service = InvoiceService(db, business_id)
        # Use QBOSyncService for sync operations
        self.qbo_sync = QBOSyncService(business_id, "", db)
    
    async def get_hygiene_data(self) -> Dict[str, Any]:
        """Get bills and invoices with hygiene issues."""
        # Get business logic data from domain services
        payment_ready_bills = self.bill_service.get_payment_ready_bills()
        overdue_invoices = self.invoice_service.get_overdue_invoices()
        
        # Get sync data from QBOSyncService
        bills_data = await self.qbo_sync.get_bills()
        invoices_data = await self.qbo_sync.get_invoices()
        
        # Filter for hygiene issues
        bills_with_issues = self._identify_bill_issues(payment_ready_bills)
        invoices_with_issues = self._identify_invoice_issues(overdue_invoices)
        
        return {
            "bills_with_issues": bills_with_issues,
            "invoices_with_issues": invoices_with_issues,
            "sync_status": {
                "bills_last_sync": bills_data.get('last_sync'),
                "invoices_last_sync": invoices_data.get('last_sync')
            }
        }

# runway/services/data_orchestrators/decision_console_data_orchestrator.py
class DecisionConsoleDataOrchestrator:
    """Data orchestrator for decision console - bills ready for decision."""
    
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        # Use domain services for business logic
        self.bill_service = BillService(db, business_id)
        self.invoice_service = InvoiceService(db, business_id)
        # Use QBOSyncService for sync operations
        self.qbo_sync = QBOSyncService(business_id, "", db)
    
    async def get_decision_data(self) -> Dict[str, Any]:
        """Get bills and invoices ready for decision."""
        # Get business logic data from domain services
        bills_ready = self.bill_service.get_bills_ready_for_decision()
        invoices_ready = self.invoice_service.get_invoices_ready_for_decision()
        
        # Get sync data from QBOSyncService
        bills_data = await self.qbo_sync.get_bills()
        invoices_data = await self.qbo_sync.get_invoices()
        
        # Filter for decision-ready items
        bills_ready_for_decision = self._filter_decision_ready_bills(bills_ready)
        invoices_ready_for_decision = self._filter_decision_ready_invoices(invoices_ready)
        
        return {
            "bills_ready": bills_ready_for_decision,
            "invoices_ready": invoices_ready_for_decision,
            "sync_status": {
                "bills_last_sync": bills_data.get('last_sync'),
                "invoices_last_sync": invoices_data.get('last_sync')
            }
        }
```

### **Pattern 3: Digest Orchestrator vs Experience Service**

```python
# Option A: Digest as Data Orchestrator (aggregates from other orchestrators)
# runway/services/data_orchestrators/digest_data_orchestrator.py
class DigestDataOrchestrator:
    """Data orchestrator for digest - aggregates from hygiene and decision orchestrators."""
    
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        # Use other orchestrators for data
        self.hygiene_orchestrator = HygieneTrayDataOrchestrator(db, business_id)
        self.decision_orchestrator = DecisionConsoleDataOrchestrator(db, business_id)
        # Use balance service for current balances
        self.balance_service = BalanceService(db, business_id)
    
    async def get_digest_data(self) -> Dict[str, Any]:
        """Get aggregated digest data from other orchestrators."""
        # Get data from other orchestrators
        hygiene_data = await self.hygiene_orchestrator.get_hygiene_data()
        decision_data = await self.decision_orchestrator.get_decision_data()
        
        # Get current balances
        current_balances = self.balance_service.get_current_balances()
        
        return {
            "hygiene_summary": {
                "bills_with_issues_count": len(hygiene_data["bills_with_issues"]),
                "invoices_with_issues_count": len(hygiene_data["invoices_with_issues"])
            },
            "decision_summary": {
                "bills_ready_count": len(decision_data["bills_ready"]),
                "invoices_ready_count": len(decision_data["invoices_ready"])
            },
            "current_balances": current_balances,
            "hygiene_data": hygiene_data,
            "decision_data": decision_data
        }

# Option B: Digest as Experience Service (no orchestrator needed)
# runway/services/experiences/digest.py
class DigestService:
    """Digest experience service - aggregates from orchestrators."""
    
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        # Use orchestrators for data
        self.hygiene_orchestrator = HygieneTrayDataOrchestrator(db, business_id)
        self.decision_orchestrator = DecisionConsoleDataOrchestrator(db, business_id)
        self.balance_service = BalanceService(db, business_id)
    
    async def get_digest_experience(self) -> Dict[str, Any]:
        """Get digest experience data."""
        # Same implementation as DigestDataOrchestrator
        # but focused on user experience rather than raw data
        pass
```

### **Pattern 4: _parked/ Execution Services**

```python
# _parked/ap_execution/bill_payment_service.py
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
```

## **Unified Implementation Plan**

### **Step 1: Create QBO-Honest Domain Services**
- **Rename `bill_ingestion.py` → `bill.py`** - We're not ingesting, we're syncing from QBO
- **Remove execution methods** from existing domain services
- **Keep only QBO-compatible features** (CRUD, business logic, sync delegation)
- **Add QBOSyncService integration** for sync operations
- **Document QBO limitations** clearly

### **Step 2: Create _parked/ Structure**
- **Move execution methods** to `_parked/{ap_execution,ar_execution,bank_verification}/`
- **Preserve all functionality** for future rail implementation
- **Document future rail compatibility** for each service

### **Step 3: Humble Runway Services**
- **Remove QBO execution assumptions** from runway services
- **Update data orchestrators** to use QBO-honest domain services
- **Move execution logic** to _parked/ services
- **Focus on QBO sync-only** for tray and console needs
- **Digest aggregates** from tray and console orchestrators

**Runway Services That Need Humbling:**
- `runway/services/experiences/tray.py` - Remove payment execution methods
- `runway/routes/bills.py` - Remove payment execution routes
- `runway/routes/invoices.py` - Remove invoice creation routes
- `runway/routes/collections.py` - Remove collection execution methods
- `runway/services/data_orchestrators/` - Update to use QBO-honest services

### **Step 4: Update Data Orchestrators**
- **Use domain services** for business logic
- **Use QBOSyncService** for sync operations
- **Implement purpose-specific filtering** (hygiene vs decision-ready)
- **Aggregate from multiple sources** as needed

### **Step 5: Design Multi-Rail Integration**
- **Rail-specific services** in `domains/{qbo,ramp,plaid,stripe}/`
- **Domain services orchestrate** across rails
- **Unified interfaces** for multi-rail operations

## **Key Design Decisions**

### **1. Service Responsibilities**
- **Domain Services**: Business logic + CRUD + sync delegation
- **QBOSyncService**: Sync operations + transaction logs
- **Data Orchestrators**: Aggregate from domain services + sync services
- **_parked/ Services**: Execution capabilities for future rails

### **2. Digest Orchestrator Decision**
**Question**: Should digest be a data orchestrator or experience service?

**Option A: Digest as Data Orchestrator**
- ✅ **Aggregates from other orchestrators** (hygiene + decision)
- ✅ **Provides raw data** for multiple consumers
- ✅ **Reusable** across different experiences
- ❌ **Might be overkill** if only used by one experience

**Option B: Digest as Experience Service**
- ✅ **Focused on user experience** rather than raw data
- ✅ **Simpler architecture** - no separate orchestrator
- ✅ **Direct aggregation** from hygiene + decision orchestrators
- ❌ **Less reusable** if other services need digest data

**Recommendation**: **Option B - Digest as Experience Service**
- Digest is primarily a user experience, not a data source
- Other services can directly use hygiene + decision orchestrators
- Simpler architecture with fewer moving parts
- Experience services can aggregate from orchestrators as needed

### **3. QBO Limitations**
- **QBO Can Do**: Read-only sync, CRUD, business logic, reporting
- **QBO Cannot Do**: Payment execution, invoice creation, bank verification
- **Clear Boundaries**: Easy to see what's QBO-compatible vs advanced

### **4. Integration Patterns**
- **Domain Services**: Use QBOSyncService for sync operations
- **Data Orchestrators**: Use both domain services and QBOSyncService
- **Transaction Logs**: All operations create audit trails
- **Multi-Rail Ready**: Patterns work for QBO, Ramp, Plaid, Stripe

## **Phase 1 Implementation Details**

### **File Renaming & Structure**
- **Rename**: `domains/ap/services/bill_ingestion.py` → `domains/ap/services/bill_service.py`
- **Reason**: We're not ingesting bills, we're syncing from QBO
- **Focus**: QBO sync-only for tray and console needs (with digest exposing those)

### **Runway Services That Need Humbling**
- `runway/services/experiences/tray.py` - Remove payment execution methods
- `runway/routes/bills.py` - Remove payment execution routes  
- `runway/routes/invoices.py` - Remove invoice creation routes
- `runway/routes/collections.py` - Remove collection execution methods
- `runway/services/data_orchestrators/` - Update to use QBO-honest services

### **Tests That Will Be Walloped**
- **QBO execution tests** - All testing payment/invoice creation (move to _parked/)
- **Feature gating tests** - No longer needed (everything is _parked/)
- **Mock-heavy tests** - Replace with real QBO sandbox data (S01)
- **Integration tests** - Update to test QBO sync-only functionality

**Test Strategy:**
- **Move execution tests** to `_parked/tests/` for future rail implementation
- **Keep sync tests** - Test QBO sync functionality
- **Update integration tests** - Focus on QBO sync-only
- **Trash mock-heavy tests** - Replace with real sandbox data

### **Import Havoc Assessment: SIGNIFICANT** 🔴
**Why significant havoc:**
1. **File rename** - `bill_ingestion` → `bill` affects 18 files
2. **Runway services** - Need to remove execution assumptions
3. **Method calls** - Some execution methods will be removed
4. **Route updates** - Payment/invoice creation routes need to be removed
5. **Tests walloped** - Most tests test QBO execution capabilities
6. **Mock cleanup** - Replace mocks with real QBO sandbox data

**Estimated effort**: 12-16 hours total
- Domain service updates: 2 hours
- Runway service humbling: 4-6 hours  
- Import updates: 2 hours
- Test cleanup: 4-6 hours
- Mock replacement: 2 hours

## **Implementation Tasks**

### **E18: Unified Multi-Rail Architecture Implementation**
- **Task**: Implement the unified architecture
- **Effort**: 12-16 hours
- **Priority**: P0
- **Scope**: 
  - Rename bill_ingestion → bill
  - Create QBO-honest domain services
  - Humble runway services (remove execution assumptions)
  - Create _parked/ structure
  - Move execution tests to _parked/
  - Clean up mock-heavy tests
  - Update data orchestrators
  - Design multi-rail integration patterns

## **Verification Criteria**

### **QBO-Honest Services**
- ✅ Domain services only do what QBO supports
- ✅ No execution methods in QBO-only services
- ✅ Clear documentation of QBO limitations
- ✅ Advanced features preserved in _parked/

### **Data Orchestrator Integration**
- ✅ Orchestrators use domain services for business logic
- ✅ Orchestrators use QBOSyncService for sync operations
- ✅ Purpose-specific filtering works correctly
- ✅ Multi-client data coordination works

### **Multi-Rail Architecture**
- ✅ Clear separation between ledger, execution, verification
- ✅ Rail-specific services in appropriate domains
- ✅ Domain services orchestrate across rails
- ✅ Unified interfaces for multi-rail operations

## **Dependencies**

### **Blocked By**
- **E11**: Domain sync duplication fix (in progress)

### **Blocks**
- **E03**: Data orchestrators purpose-specific (needs this unified strategy)
- **Future multi-rail implementation** (needs clear organization)

## **Next Steps**

1. **Complete E11**: Finish domain sync duplication fix
2. **Design Unified Architecture**: Create detailed implementation patterns
3. **Create E18**: Unified multi-rail architecture implementation
4. **Consolidate Tasks**: Merge E03, E03_HUMBLE_QBO_SERVICES, S11, S12 into E18

---

*This unified strategy addresses all four intertwined tasks as one cohesive architecture, providing clear patterns for QBO-honest services, multi-rail organization, domain integration, and data orchestrator patterns.*
