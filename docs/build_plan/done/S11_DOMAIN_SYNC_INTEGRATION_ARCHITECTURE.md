# S11: Domain Service Sync Integration Architecture

## **Task: Design Domain Service Integration with New Sync Architecture**
- **Status:** `[❌]` Superseded by S13
- **Priority:** P0 Critical
- **Justification:** With E02 SmartSync refactoring complete and E11 domain sync duplication fix in progress, we need to design how domain services integrate with the new `domains/qbo/services/sync_service.py` for transaction logs and mirror state. This affects data orchestrators (E03, S02) and requires clear integration patterns.
- **Execution Status:** **SUPERSEDED BY S13_UNIFIED_MULTI_RAIL_ARCHITECTURE**

## **Problem Statement**

**Current State**: We have completed major architectural changes:
- ✅ **E02**: SmartSync refactoring - `QBOSyncService` in `domains/qbo/services/sync_service.py`
- ✅ **S07**: Transaction log implementation - Mirror models + transaction logs
- 🔄 **E11**: Domain sync duplication fix - Removing sync methods from domain services
- 🔄 **E03**: Data orchestrators purpose-specific (in progress)
- 🔄 **S02**: Data orchestrator architecture fix (in progress)

**The Problem**: We need to design how domain services integrate with the new sync architecture:
- **Transaction Log Integration**: How do domain services work with transaction logs?
- **Mirror State Updates**: How do domain services update mirror models?
- **Sync Orchestration**: How do domain services trigger sync operations?
- **Data Orchestrator Integration**: How do orchestrators use both domain services and sync services?

**Why This Matters**:
- **E03/S02 Dependencies**: Data orchestrators need clear integration patterns
- **Transaction Log Compliance**: Domain services must work with audit trails
- **Mirror State Consistency**: Domain services must maintain data consistency
- **Multi-Rail Ready**: Pattern must work for QBO, Ramp, Plaid, Stripe

## **Architecture Context**

### **What We Have (Completed)**
- **`domains/qbo/services/sync_service.py`** - QBOSyncService with transaction log integration
- **Transaction Log Models** - Immutable audit trail models
- **Mirror Models** - Current state models with transaction log relationships
- **BaseSyncService** - Generic sync orchestration

### **What We're Building (In Progress)**
- **Domain Services** - Business logic only (no sync operations)
- **Data Orchestrators** - Purpose-specific data aggregation
- **Integration Patterns** - How services work together

### **What We Need to Design**
- **Domain Service Integration** - How domain services work with sync services
- **Transaction Log Patterns** - How domain services create audit trails
- **Mirror State Patterns** - How domain services maintain consistency
- **Orchestrator Integration** - How orchestrators use both service types

## **Integration Patterns Needed**

### **Pattern 1: Domain Service + Sync Service Integration**

```python
# Domain Service Pattern
class BillService:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        # Use QBOSyncService for sync operations
        self.qbo_sync = QBOSyncService(business_id, "", db)
    
    def get_payment_ready_bills(self) -> List[Bill]:
        """Business logic - query mirror models."""
        return self.db.query(Bill).filter(
            Bill.business_id == self.business_id,
            Bill.status == 'unpaid',
            Bill.amount > 0
        ).all()
    
    async def sync_bills_from_qbo(self) -> Dict[str, Any]:
        """Sync operation - delegate to QBOSyncService."""
        return await self.qbo_sync.get_bills()
```

### **Pattern 2: Transaction Log Integration**

```python
# Domain Service with Transaction Log Integration
class BillService:
    async def create_bill(self, bill_data: Dict[str, Any]) -> Bill:
        """Create bill with transaction log."""
        # Create mirror model
        bill = Bill(
            business_id=self.business_id,
            vendor_name=bill_data['vendor_name'],
            amount=bill_data['amount'],
            due_date=bill_data['due_date']
        )
        self.db.add(bill)
        self.db.commit()
        
        # Create transaction log entry
        await self.qbo_sync.transaction_log_service.log_bill_creation(
            bill=bill,
            bill_data=bill_data,
            source="user",
            created_by_user_id=bill_data.get('user_id')
        )
        
        return bill
```

### **Pattern 3: Data Orchestrator Integration**

```python
# Data Orchestrator Pattern
class DigestDataOrchestrator:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        # Use domain services for business logic
        self.bill_service = BillService(db, business_id)
        self.invoice_service = InvoiceService(db, business_id)
        # Use sync service for sync operations
        self.qbo_sync = QBOSyncService(business_id, "", db)
    
    async def get_digest_data(self) -> Dict[str, Any]:
        """Aggregate data from domain services and sync service."""
        # Get business logic data from domain services
        payment_ready_bills = self.bill_service.get_payment_ready_bills()
        overdue_invoices = self.invoice_service.get_overdue_invoices()
        
        # Get sync data from QBOSyncService
        bills_data = await self.qbo_sync.get_bills()
        invoices_data = await self.qbo_sync.get_invoices()
        
        return {
            "payment_ready_bills": payment_ready_bills,
            "overdue_invoices": overdue_invoices,
            "bills_data": bills_data,
            "invoices_data": invoices_data
        }
```

## **Key Design Decisions**

### **1. Service Responsibilities**
- **Domain Services**: Business logic + CRUD operations on mirror models
- **QBOSyncService**: Sync operations + transaction log integration
- **Data Orchestrators**: Aggregate from both domain services and sync services

### **2. Transaction Log Integration**
- **Domain Services**: Create transaction log entries for business operations
- **QBOSyncService**: Create transaction log entries for sync operations
- **TransactionLogService**: Centralized service for all transaction log operations

### **3. Mirror State Management**
- **Domain Services**: Update mirror models for business operations
- **QBOSyncService**: Update mirror models for sync operations
- **Atomic Updates**: Both mirror models and transaction logs updated together

### **4. Data Flow Patterns**
- **Business Operations**: Domain Service → Mirror Model + Transaction Log
- **Sync Operations**: QBOSyncService → Mirror Model + Transaction Log
- **Data Orchestration**: Orchestrator → Domain Services + QBOSyncService

## **Integration Requirements**

### **Domain Service Requirements**
- **No Direct Sync**: Domain services don't call QBO APIs directly
- **Transaction Log Integration**: All business operations create audit trails
- **Mirror State Updates**: All business operations update mirror models
- **Sync Delegation**: Sync operations delegate to QBOSyncService

### **Data Orchestrator Requirements**
- **Domain Service Integration**: Use domain services for business logic
- **Sync Service Integration**: Use QBOSyncService for sync operations
- **Purpose-Specific Filtering**: Filter data for specific experiences
- **Multi-Client Coordination**: Handle data for multiple clients

### **Transaction Log Requirements**
- **Immutable Audit Trails**: All changes create transaction log entries
- **Source Attribution**: Track whether changes came from user, QBO, or other rails
- **Complete Data Snapshots**: Store full data state at time of change
- **Multi-Rail Support**: Support QBO, Ramp, Plaid, Stripe sources

## **Implementation Tasks Needed**

### **E12: Domain Service Sync Integration**
- **Task**: Update domain services to integrate with QBOSyncService
- **Effort**: 1-2 days
- **Priority**: P0
- **Dependencies**: E11 (domain sync duplication fix)

### **E13: Transaction Log Integration**
- **Task**: Integrate transaction logs into domain service operations
- **Effort**: 1-2 days
- **Priority**: P0
- **Dependencies**: E12 (domain service sync integration)

### **E14: Data Orchestrator Integration**
- **Task**: Update data orchestrators to use both domain services and sync services
- **Effort**: 1-2 days
- **Priority**: P0
- **Dependencies**: E12, E13 (domain service and transaction log integration)

## **Verification Criteria**

### **Domain Service Integration**
- ✅ Domain services use QBOSyncService for sync operations
- ✅ Domain services create transaction log entries for business operations
- ✅ Domain services update mirror models for business operations
- ✅ No direct QBO API calls from domain services

### **Data Orchestrator Integration**
- ✅ Orchestrators use domain services for business logic
- ✅ Orchestrators use QBOSyncService for sync operations
- ✅ Purpose-specific filtering works correctly
- ✅ Multi-client data coordination works

### **Transaction Log Integration**
- ✅ All business operations create transaction log entries
- ✅ All sync operations create transaction log entries
- ✅ Source attribution works correctly
- ✅ Multi-rail support works

## **Dependencies**

### **Blocked By**
- **E11**: Domain sync duplication fix (in progress)
- **E03**: Data orchestrators purpose-specific (in progress)
- **S02**: Data orchestrator architecture fix (in progress)

### **Blocks**
- **E14**: Data orchestrator integration (needs this solution)
- **Future multi-rail implementation** (needs clear integration patterns)

## **Next Steps**

1. **Complete E11**: Finish domain sync duplication fix
2. **Design Integration Patterns**: Create detailed integration patterns
3. **Create Implementation Tasks**: E12, E13, E14
4. **Coordinate with E03/S02**: Ensure orchestrator integration works

---

*This solutioning task defines how domain services integrate with the new sync architecture, providing clear patterns for transaction logs, mirror state, and data orchestrator integration.*
