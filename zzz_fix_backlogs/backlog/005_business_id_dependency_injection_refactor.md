# Backlog Task: Refactor Business ID Dependency Injection Pattern

## **Task Overview**
- **ID**: `005_business_id_dependency_injection_refactor`
- **Priority**: P1 HIGH
- **Estimated Time**: 4-6 hours
- **Status**: `[ ]` Not started
- **Category**: Architecture Refactoring

## **Problem Statement**
The current `get_services()` pattern creates over-engineered dependency injection containers that:
1. **Over-engineer** - create services just to extract `business_id` from them
2. **Fragile** - if any service fails to initialize, you lose access to `business_id`
3. **Inconsistent** - different routes need different services, so the pattern doesn't scale
4. **Hidden dependencies** - code breaks if services fail to initialize, even when you don't need their functionality

## **Current Anti-Pattern**
```python
def get_services(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    """Get all required services with business context."""
    return {
        "bill_service": BillService(db, business_id),
        "payment_service": PaymentService(db, business_id),
        "sync_timing": SyncTimingManager(business_id),
        "smart_sync": SmartSyncService(business_id),
        "reserve_service": RunwayReserveService(db, business_id)
    }

# Then later in routes:
business_id = services["smart_sync"].business_id  # Anti-pattern!
```

## **Proposed Solution**
Replace service containers with direct, explicit dependency injection:

```python
@router.post("/bills/{bill_id}/pay")
async def pay_bill(
    bill_id: str,
    payment_data: PaymentRequest,
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)  # Direct access
):
    # Create only the services you actually need
    bill_service = BillService(db, business_id)
    smart_sync = SmartSyncService(business_id)
    
    # Use them directly
    result = await bill_service.pay_bill(bill_id, payment_data)
    smart_sync.record_user_activity("bill_payment")
    return result
```

## **Benefits**
1. **Explicit dependencies** - you can see exactly what each route needs
2. **Resilient** - if one service fails, others still work
3. **Testable** - easy to mock individual services
4. **Scalable** - different routes can have different service needs
5. **Clear** - no hidden data extraction from service containers

## **Files to Refactor**
- `runway/routes/bills.py` - Remove `get_services()`, add direct `business_id` dependency
- `runway/routes/vendors.py` - Same pattern
- `runway/routes/invoices.py` - Same pattern
- `runway/routes/collections.py` - Same pattern
- `runway/routes/kpis.py` - Same pattern
- `runway/routes/payments.py` - Same pattern

## **Implementation Steps**
1. **Audit current usage** - Find all `get_services()` calls and `services["service_name"].business_id` patterns
2. **Refactor route functions** - Replace service container with direct `business_id` dependency
3. **Remove `get_services()`** - Delete the over-engineered dependency injection function
4. **Update service constructors** - Ensure all services accept `business_id` directly
5. **Test each route** - Verify functionality works with direct dependencies

## **Verification**
- [ ] All routes use direct `business_id` dependency instead of service containers
- [ ] No more `services["service_name"].business_id` patterns
- [ ] `get_services()` function removed
- [ ] All routes still work correctly
- [ ] Code is more explicit and resilient

## **Definition of Done**
- All route functions use direct `business_id = Depends(get_current_business_id)`
- No service containers used for data extraction
- Services created only when actually needed
- Code is more explicit, resilient, and testable
- All tests pass

## **Rollback Plan**
```bash
git checkout HEAD~1 -- runway/routes/
git checkout HEAD~1 -- runway/routes/bills.py
git checkout HEAD~1 -- runway/routes/vendors.py
git checkout HEAD~1 -- runway/routes/invoices.py
git checkout HEAD~1 -- runway/routes/collections.py
git checkout HEAD~1 -- runway/routes/kpis.py
git checkout HEAD~1 -- runway/routes/payments.py
```

## **Context**
This refactoring aligns with the principle that **services should be used for functionality, not as data containers**. The current pattern creates unnecessary coupling and makes the code more fragile than it needs to be.
