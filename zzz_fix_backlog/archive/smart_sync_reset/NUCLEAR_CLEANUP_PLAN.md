# Nuclear Cleanup Plan - QBO Architecture Reset

*Generated from comprehensive analysis on 2025-01-27*  
*Status: 🚀 READY FOR EXECUTION*

## **The Problem**

Current QBO architecture is a complete mess:
- **3 duplicate QBO implementations** with circular dependencies
- **4000+ lines of mixed code** violating separation of concerns
- **Application won't start** due to import errors
- **Domain CRUD logic mixed with API calls** (violates ADR-001)

## **The Solution**

**Nuclear Option**: Delete everything QBO-related and rebuild cleanly.

**Target Architecture**:
```
Domain Service → SmartSyncService → Raw QBO HTTP Calls
```

Where:
- **Domain services** handle their own CRUD operations
- **SmartSyncService** provides resilience (retry, dedup, rate limiting, caching)
- **Raw QBO HTTP calls** are just HTTP requests to QBO endpoints

## **What to Delete (Complete Mess)**

```bash
# Delete all the circular dependency mess
rm -rf domains/qbo/client.py          # 2105 lines of mixed mess
rm -rf domains/qbo/data_service.py    # Redundant with SmartSyncService
rm -rf domains/qbo/service.py         # Redundant with SmartSyncService
rm -rf domains/integrations/qbo/      # Complete duplicate directory
rm -rf domains/qbo/interfaces.py      # Irrelevant
rm -rf domains/qbo/scenario_runner.py # Moving to sandbox service
rm -rf domains/qbo/create_sandbox_data.py # Moving to sandbox service
rm -rf domains/qbo/get_qbo_tokens.py  # Redundant
rm -rf domains/qbo/dev_tokens.json    # Development only
```

## **What to Keep (Actually Clean)**

```bash
# Keep these clean files:
# domains/qbo/auth.py - QBO authentication (move to infra/qbo/)
# domains/qbo/setup.py - QBO connection setup (move to infra/qbo/)
# domains/qbo/config.py - QBO configuration (move to infra/qbo/)
# domains/qbo/health.py - QBO health checks (move to infra/qbo/)
# domains/qbo/models.py - QBO domain models (keep in domains/qbo/)
```

## **What to Build (Clean Foundation)**

### **1. Raw QBO HTTP Client (`infra/qbo/client.py`)**
Just HTTP calls to QBO - no business logic:

```python
class QBORawClient:
    def __init__(self, business_id: str, realm_id: str):
        self.business_id = business_id
        self.realm_id = realm_id
        self.base_url = qbo_config.api_url
    
    async def get_bills_from_qbo(self, due_days: int = 30) -> Dict:
        """Raw HTTP call to QBO bills endpoint."""
        # Just HTTP call, no business logic
        
    async def create_payment_in_qbo(self, payment_data: Dict) -> Dict:
        """Raw HTTP call to QBO payment endpoint."""
        # Just HTTP call, no business logic
        
    async def get_invoices_from_qbo(self, aging_days: int = 30) -> Dict:
        """Raw HTTP call to QBO invoices endpoint."""
        # Just HTTP call, no business logic
```

### **2. Enhanced SmartSyncService (`infra/jobs/smart_sync.py`)**
Add QBO operation handling:

```python
class SmartSyncService:
    async def execute_qbo_call(self, operation: str, *args, **kwargs) -> Any:
        """Execute any QBO operation with resilience."""
        # 1. Check rate limits
        # 2. Check for duplicates
        # 3. Execute with retry
        # 4. Cache if needed
        # 5. Return result
        
        qbo_client = QBORawClient(self.business_id, realm_id)
        return await self._execute_with_retry(
            getattr(qbo_client, operation), *args, **kwargs
        )
```

### **3. Domain Services Handle Their Own CRUD**
```python
# domains/ap/services/bill_service.py
class BillService:
    def __init__(self, business_id: str):
        self.smart_sync = SmartSyncService(business_id)
    
    async def get_bills(self, due_days: int = 30) -> List[Bill]:
        """Get bills - domain handles its own CRUD."""
        qbo_data = await self.smart_sync.execute_qbo_call(
            "get_bills_from_qbo", due_days=due_days
        )
        # Transform QBO data to domain models
        return [Bill.from_qbo_data(item) for item in qbo_data]
    
    async def create_payment(self, bill_id: str, payment_data: Dict) -> Payment:
        """Create payment - domain handles its own CRUD."""
        qbo_result = await self.smart_sync.execute_qbo_call(
            "create_payment_in_qbo", payment_data=payment_data
        )
        # Transform and save to local DB
        return Payment.from_qbo_data(qbo_result)
```

## **Execution Steps**

### **Phase 1: Nuclear Cleanup (30 minutes)**
1. Delete all the circular dependency files
2. Fix immediate import errors by updating imports to use SmartSyncService directly

### **Phase 2: Build Clean Foundation (2 hours)**
1. Create `infra/qbo/client.py` with raw QBO HTTP calls only
2. Enhance `SmartSyncService` with `execute_qbo_call()` method
3. Update domain services to call SmartSyncService directly

### **Phase 3: Fix All Import Errors (1 hour)**
1. Update all imports from `domains.qbo.smart_sync` to `infra.jobs`
2. Remove all references to the deleted files
3. Test that application starts

## **Expected Results**

- **Clean architecture** following ADR-001
- **No circular dependencies**
- **SmartSyncService as central orchestration**
- **~1000 lines of clean code** (down from 4000+)
- **Application starts** without import errors
- **Domain services** handle their own business logic
- **Raw QBO client** just makes HTTP calls

---

*This nuclear plan will result in a clean, maintainable QBO architecture that follows ADR-001 principles.*
