# E11: Fix Domain Service Sync Duplication

## **Task: Remove Sync Methods from Domain Services - Use QBOSyncService Instead**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** We have duplication between `domains/qbo/services/sync_service.py` (QBOSyncService) and `domains/*/services/*` files that both do sync operations. This violates separation of concerns and creates architectural confusion. Domain services should do business logic, QBOSyncService should do sync operations.
- **Execution Status:** **Needs-Execution**

## **The Problem**

**Current State**: We have **two different sync patterns** that are conflicting:

1. **`domains/qbo/services/sync_service.py`** - QBOSyncService with sync methods like `sync_bill_with_log()`
2. **`domains/ap/services/bill_ingestion.py`** - BillService with `sync_bills_from_qbo()` method

**Issues**:
- ❌ **Duplication**: Same sync functionality in multiple places
- ❌ **Confusion**: Unclear which service to use for what
- ❌ **Violation of Separation of Concerns**: Domain services doing sync + business logic
- ❌ **Architectural Violation**: Domain services should not do sync operations

## **The Solution**

### **Clear Separation of Responsibilities**

#### **QBOSyncService** (`domains/qbo/services/sync_service.py`)
**Purpose**: QBO sync operations and API coordination
**Responsibilities**:
- ✅ QBO API calls (get_bills, get_invoices, etc.)
- ✅ Transaction log integration
- ✅ Mirror model updates
- ✅ Sync orchestration

#### **Domain Services** (`domains/*/services/*.py`)
**Purpose**: Domain-specific business logic and data queries
**Responsibilities**:
- ✅ Business logic and rules
- ✅ Data queries and filtering
- ✅ Domain-specific calculations
- ❌ **NO SYNC OPERATIONS** - Use QBOSyncService instead

## **Implementation Plan**

### **Step 1: Remove Sync Methods from Domain Services**

#### **domains/ap/services/bill_ingestion.py**
**Remove**:
- ❌ `sync_bills_from_qbo()` method (lines 189-209)
- ❌ `self.smart_sync = QBOSyncService()` instantiation
- ❌ All QBO API calls

**Keep**:
- ✅ `get_payment_ready_bills()` - Business logic
- ✅ `calculate_bill_priority()` - Business logic
- ✅ `get_bills_by_status()` - Data queries

#### **domains/ar/services/invoice.py**
**Remove**:
- ❌ `sync_invoices_from_qbo()` method
- ❌ `self.smart_sync = QBOSyncService()` instantiation
- ❌ All QBO API calls

**Keep**:
- ✅ `get_overdue_invoices()` - Business logic
- ✅ `get_invoices_by_aging_days()` - Business logic
- ✅ `calculate_aging_days()` - Business logic

### **Step 2: Domain Services Now Focus on Business Logic Only**

After removing sync methods, domain services now have clear responsibilities:

#### **domains/ap/services/bill_ingestion.py** (BillService)
**Business Logic Methods**:
- ✅ `get_payment_ready_bills()` - Business logic for payment readiness
- ✅ `get_bills_due_in_days()` - Business logic for due date filtering
- ✅ `get_overdue_bills()` - Business logic for overdue identification
- ✅ `process_bill()` - Business logic for bill processing
- ✅ `get_days_until_due()` - Business logic for due date calculations

#### **domains/ar/services/invoice.py** (InvoiceService)
**Business Logic Methods**:
- ✅ `get_overdue_invoices()` - Business logic for overdue identification
- ✅ `get_invoices_by_aging_days()` - Business logic for aging calculations
- ✅ `get_invoices_by_customer()` - Business logic for customer filtering
- ✅ `get_invoices_by_status()` - Business logic for status filtering

## **Files to Modify**

### **Files to Clean Up (Remove Sync Methods)**
1. **`domains/ap/services/bill_ingestion.py`**
   - Remove `sync_bills_from_qbo()` method
   - Remove `self.smart_sync` instantiation
   - Keep only business logic methods

2. **`domains/ar/services/invoice.py`**
   - Remove `sync_invoices_from_qbo()` method
   - Remove `self.smart_sync` instantiation
   - Keep only business logic methods

3. **`domains/bank/services/balance_service.py`**
   - Remove any sync methods
   - Remove `self.smart_sync` instantiation
   - Keep only business logic methods

### **Files Already Correct (No Changes Needed)**
1. **`runway/services/data_orchestrators/*.py`**
   - Already use QBOSyncService for sync operations
   - Already use domain services for business logic
   - Clear separation of concerns maintained

2. **`runway/services/experiences/*.py`**
   - Already use QBOSyncService for sync operations
   - Already use domain services for business logic

## **Architecture Benefits**

### **Clear Separation of Concerns**
- **QBOSyncService**: Sync orchestration and API coordination
- **Domain Services**: Business logic and data queries
- **Runway Services**: User experiences and workflows

### **No Duplication**
- **Single source of truth** for sync operations
- **Single source of truth** for business logic
- **Clear boundaries** between sync and business logic

### **Multi-Rail Ready**
- **QBOSyncService**: QBO-specific sync
- **Future RampSyncService**: Ramp-specific sync
- **Future PlaidSyncService**: Plaid-specific sync
- **Future StripeSyncService**: Stripe-specific sync

## **Verification**

### **No Sync Methods in Domain Services**
- ✅ `domains/ap/services/bill_ingestion.py` - No sync methods
- ✅ `domains/ar/services/invoice.py` - No sync methods
- ✅ `domains/bank/services/balance_service.py` - No sync methods

### **All Sync Operations in QBOSyncService**
- ✅ `domains/qbo/services/sync_service.py` - All sync operations
- ✅ Transaction log integration works
- ✅ Mirror model updates work

### **Runway Services Use Both**
- ✅ Use QBOSyncService for sync operations
- ✅ Use domain services for business logic
- ✅ Clear separation of concerns

## **Definition of Done**

- [ ] Remove all sync methods from domain services
- [ ] Remove QBOSyncService instantiation from domain services
- [ ] Update runway services to use both QBOSyncService and domain services
- [ ] All existing functionality still works
- [ ] Clear separation of concerns established
- [ ] Ready for multi-rail implementation

---

*This task eliminates duplication and establishes clear architectural boundaries between sync operations and business logic.*
