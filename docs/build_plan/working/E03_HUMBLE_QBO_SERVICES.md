# E03: Humble QBO Services

## **Task: Create Humble QBO Services - QBO Can Only Do What QBO Actually Does**
- **Status:** `[❌]` Superseded by S13
- **Priority:** P0 Critical
- **Justification:** Current domain services assume QBO can execute payments and create invoices, but QBO is only a ledger rail. We need to create humble QBO services that only do what QBO actually supports, and move execution capabilities to _parked/ for future Ramp/Stripe implementation.
- **Execution Status:** **SUPERSEDED BY S13_UNIFIED_MULTI_RAIL_ARCHITECTURE**

## **The Problem**

**Current State**: Domain services in `domains/{ap,ar,bank}/` assume QBO can do everything:
- `domains/ap/services/bill_ingestion.py` - Has payment execution methods
- `domains/ar/services/invoice.py` - Has invoice creation methods  
- `domains/bank/services/balance_service.py` - Has bank verification methods

**Reality**: QBO is only a ledger rail - it can sync data but can't execute payments, create invoices, or verify bank accounts.

**Solution**: Create humble QBO services that only do what QBO actually supports, and move execution capabilities to `_parked/` for future rail implementation.

## **What QBO Actually Supports**

### **✅ QBO Can Do (Keep in domains/qbo/)**
- **Read-only sync with light bookkeeping updates** from QBO API
- **Basic CRUD** on mirrored data
- **Query and filtering** of local data
- **Audit trail** and compliance tracking
- **Historical data** and reporting

### **❌ QBO Cannot Do (Move to _parked/)**
- **Bill payment execution** - Ramp will handle
- **Invoice creation/sending** - Stripe will handle
- **Bank account verification** - Plaid will handle
- **Payment processing** - Ramp/Stripe will handle
- **ACH payments** - Plaid will handle

## **Implementation Plan**

### **Step 1: Create Humble QBO Services**

#### **domains/qbo/services/bill_sync.py**
```python
class QBOBillSyncService:
    """QBO-specific bill sync service - read-only operations only."""
    
    def __init__(self, business_id: str, db_session):
        self.business_id = business_id
        self.db_session = db_session
        self.sync_service = QBOSyncService(business_id, "", db_session)
    
    async def sync_bills_from_qbo(self) -> List[Bill]:
        """Sync bills from QBO API to local mirror."""
        
    def get_bills_by_status(self, status: str) -> List[Bill]:
        """Query mirrored bills by status."""
        
    def get_bills_due_soon(self, days: int = 30) -> List[Bill]:
        """Query bills due within specified days."""
        
    def get_payment_ready_bills(self) -> List[Bill]:
        """Query bills ready for payment (but don't execute)."""
```

#### **domains/qbo/services/invoice_sync.py**
```python
class QBOInvoiceSyncService:
    """QBO-specific invoice sync service - read-only operations only."""
    
    def __init__(self, business_id: str, db_session):
        self.business_id = business_id
        self.db_session = db_session
        self.sync_service = QBOSyncService(business_id, "", db_session)
    
    async def sync_invoices_from_qbo(self) -> List[Invoice]:
        """Sync invoices from QBO API to local mirror."""
        
    def get_overdue_invoices(self, days: int = 0) -> List[Invoice]:
        """Query mirrored invoices that are overdue."""
        
    def get_invoices_by_aging_days(self, aging_days: int = 30) -> List[Invoice]:
        """Query invoices by aging days."""
```

#### **domains/qbo/services/balance_sync.py**
```python
class QBOBalanceSyncService:
    """QBO-specific balance sync service - read-only operations only."""
    
    def __init__(self, business_id: str, db_session):
        self.business_id = business_id
        self.db_session = db_session
        self.sync_service = QBOSyncService(business_id, "", db_session)
    
    async def sync_balances_from_qbo(self) -> List[Balance]:
        """Sync balances from QBO API to local mirror."""
        
    def get_current_balances(self) -> List[Balance]:
        """Query mirrored current balances."""
```

### **Step 2: Move Execution Code to _parked/**

#### **_parked/ap_execution/bill_payment_service.py**
```python
class BillPaymentService:
    """A/P execution service - will be implemented by Ramp."""
    
    async def approve_bill_for_payment(self, bill_id: str) -> PaymentIntent:
        """Approve bill for payment execution."""
        
    async def execute_payment(self, payment_intent_id: str) -> PaymentResult:
        """Execute payment through Ramp."""
        
    async def schedule_payment(self, bill_id: str, payment_date: datetime) -> ScheduledPayment:
        """Schedule payment for future execution."""
```

#### **_parked/ar_execution/invoice_management_service.py**
```python
class InvoiceManagementService:
    """A/R execution service - will be implemented by Stripe."""
    
    async def create_invoice(self, customer_id: str, items: List[InvoiceItem]) -> Invoice:
        """Create invoice for customer."""
        
    async def send_invoice(self, invoice_id: str) -> SendResult:
        """Send invoice to customer."""
        
    async def process_payment(self, invoice_id: str, payment_method: str) -> PaymentResult:
        """Process payment for invoice."""
```

#### **_parked/bank_verification/account_verification_service.py**
```python
class AccountVerificationService:
    """Bank verification service - will be implemented by Plaid."""
    
    async def verify_bank_account(self, account_id: str) -> VerificationResult:
        """Verify bank account with Plaid."""
        
    async def match_transactions(self, account_id: str) -> List[MatchedTransaction]:
        """Match transactions for reconciliation."""
```

### **Step 3: Update Runway Services**

#### **runway/services/data_orchestrators/digest_data_orchestrator.py**
```python
# Change from:
from domains.ap.services.bill_ingestion import BillService

# To:
from domains.qbo.services.bill_sync import QBOBillSyncService
from _parked.ap_execution.bill_payment_service import BillPaymentService

class DigestDataOrchestrator:
    def __init__(self, db: Session):
        self.bill_sync = QBOBillSyncService("", "", db)
        self.bill_payment = BillPaymentService()  # For future Ramp integration
```

### **Step 4: Update Domain Models**

#### **domains/qbo/models/bill.py**
```python
class QBOBill(Base, TimestampMixin, TenantMixin):
    """QBO-specific bill model - read-only sync data."""
    __tablename__ = "qbo_bills"
    
    # QBO Integration Fields
    qbo_bill_id = Column(String(255), nullable=False, index=True)
    qbo_sync_token = Column(String(50), nullable=True)
    qbo_last_sync = Column(DateTime, nullable=True)
    
    # Bill Data (from QBO)
    bill_number = Column(String(100), nullable=True)
    amount_cents = Column(Integer, nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="unpaid")
    
    # No execution fields - those go in Ramp models
```

## **File Migration Plan**

### **Files to Create**
- `domains/qbo/services/bill_sync.py`
- `domains/qbo/services/invoice_sync.py`
- `domains/qbo/services/balance_sync.py`
- `_parked/ap_execution/bill_payment_service.py`
- `_parked/ar_execution/invoice_management_service.py`
- `_parked/bank_verification/account_verification_service.py`

### **Files to Update**
- `runway/services/data_orchestrators/digest_data_orchestrator.py`
- `runway/services/data_orchestrators/decision_console_data_orchestrator.py`
- `runway/services/data_orchestrators/hygiene_tray_data_orchestrator.py`
- `runway/services/data_orchestrators/test_drive_data_orchestrator.py`

### **Files to Move to _parked/**
- `domains/ap/services/bill_ingestion.py` → `_parked/ap_execution/bill_ingestion_service.py`
- `domains/ar/services/invoice.py` → `_parked/ar_execution/invoice_service.py`
- `domains/bank/services/balance_service.py` → `_parked/bank_verification/balance_service.py`

## **Verification**

### **QBO Services Work**
- ✅ QBO services only do read-only operations
- ✅ No execution methods in QBO services
- ✅ All sync operations work correctly
- ✅ Data queries return expected results

### **Execution Code Parked**
- ✅ Execution methods moved to _parked/
- ✅ Clear separation between sync and execution
- ✅ Parked services ready for future rail implementation
- ✅ No execution assumptions in QBO services

### **Runway Services Updated**
- ✅ Runway services use humble QBO services
- ✅ Execution capabilities available in _parked/
- ✅ All existing functionality still works
- ✅ Clear migration path to multi-rail

## **Definition of Done**

- [ ] Humble QBO services created in `domains/qbo/services/`
- [ ] Execution code moved to `_parked/{ap_execution,ar_execution,bank_verification}/`
- [ ] Runway services updated to use humble QBO services
- [ ] All existing functionality still works
- [ ] Clear separation between sync and execution
- [ ] Ready for future rail implementation

## **Next Steps**

1. **Start with bill services** - Create `QBOBillSyncService`
2. **Move execution code** - Move payment methods to `_parked/ap_execution/`
3. **Update runway services** - Use humble QBO services
4. **Test functionality** - Ensure everything still works
5. **Repeat for AR and bank** - Apply same pattern to invoices and balances

---

*This task creates the foundation for multi-rail architecture by properly separating QBO's ledger capabilities from execution capabilities that will be handled by future rails.*
