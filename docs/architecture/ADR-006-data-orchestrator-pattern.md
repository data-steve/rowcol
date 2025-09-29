# ADR-006: Data Orchestrator Pattern for Experience Services

**Date**: 2025-01-27  
**Status**: Accepted  
**Decision**: Use data orchestrators in `runway/core/` to manage both data pulling and state management for experience services

## **Context**

The runway experience services (Hygiene Tray, Decision Console, Digest, Test Drive) need different combinations of data entities and time windows, but domains/ services are generic CRUD primitives. We need a waypoint layer that's runway-aware but still uses domains/ primitives.

**Problem**: Each experience needs:
- Different entity combinations (bills + invoices + balances)
- Different time windows (Digest=all data, TestDrive=4 weeks, Tray=immediate)
- Different runtime patterns (async batch vs on-demand)
- State management (Console decision queue, Digest batch processing)

**Previous Attempts**: `RunwayCalculator` tried to solve this but violated ADR-001 by doing data pulling instead of calculating.

## **Decision**

**Use Data Orchestrator Pattern**:
- **Location**: `runway/core/data_orchestrators/`
- **Pattern**: Service pattern with state management capabilities
- **State Management**: Orchestrator manages state, not experience services
- **Architecture**: `Frontend ↔ Experience Service ↔ Data Orchestrator ↔ Domains/`

## **Architecture Pattern**

```
runway/experiences/ (functionality + UX)
    ↓
runway/core/data_orchestrators/ (data + state management)
    ↓
runway/core/calculators/ (pure calculation services)
    ↓
domains/ (CRUD primitives)
    ↓
SmartSyncService (orchestration)
```

## **Implementation Pattern**

### **Data Orchestrator Structure**
```python
# runway/core/data_orchestrators/[experience]_data_orchestrator.py
class [Experience]DataOrchestrator:
    async def get_[experience]_data(self, business_id: str) -> Dict[str, Any]:
        # Pull all required data for experience
        # Return data + current state
    
    # Additional methods for state management as needed
    async def [experience_specific_method](self, business_id: str, ...) -> Dict[str, Any]:
        # Experience-specific functionality
```

### **Experience Service Usage**
```python
# runway/experiences/[experience].py
class [Experience]Service:
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = [Experience]DataOrchestrator()
    
    async def get_data(self, business_id: str) -> Dict[str, Any]:
        return await self.orchestrator.get_[experience]_data(business_id)
```

## **Benefits**

1. **Single Source of Truth**: Data orchestrator manages both data and state
2. **Frontend Consistency**: Frontend can always get current state from orchestrator
3. **State Persistence**: State survives service restarts and multiple frontend instances
4. **Cleaner Experience Services**: Focus on business logic, not state management
5. **Better Testing**: Can test state management independently
6. **Scalability**: Multiple frontend instances can share state
7. **ADR-001 Compliance**: Domains/ remain pure CRUD primitives

## **Examples**

### **Hygiene Tray (Simple)**
```python
class HygieneTrayDataOrchestrator:
    async def get_tray_data(self, business_id: str) -> Dict[str, Any]:
        bills = await self.ap_service.get_bills_with_issues(business_id)
        invoices = await self.ar_service.get_invoices_with_issues(business_id)
        return {"bills": bills, "invoices": invoices}
```

### **Decision Console (Stateful)**
```python
class DecisionConsoleDataOrchestrator:
    async def get_console_data(self, business_id: str) -> Dict[str, Any]:
        # Pull data + current decision queue
        base_data = await self._pull_base_data(business_id)
        decision_queue = await self._get_decision_queue(business_id)
        return {**base_data, "decision_queue": decision_queue}
    
    async def add_decision(self, business_id: str, decision: Dict) -> Dict:
        await self._store_decision(business_id, decision)
        return await self.get_console_data(business_id)
```

## **Implications**

- **All experience services** will use orchestrator pattern
- **State management** centralized in orchestrators
- **Frontend** talks to experience services, which talk to orchestrators
- **Domains/ services** remain pure CRUD primitives
- **SmartSyncService** used only by orchestrators, not experiences

## **Migration Strategy**

1. **Phase 1**: Create orchestrators for each experience
2. **Phase 2**: Update experience services to use orchestrators
3. **Phase 3**: Remove direct SmartSyncService calls from experiences
4. **Phase 4**: Refactor RunwayCalculator to pure calculation service

## **Success Criteria**

- [ ] All experiences use their specific data orchestrator
- [ ] No direct SmartSyncService calls from experiences
- [ ] State management centralized in orchestrators
- [ ] Frontend can get consistent state from orchestrators
- [ ] Domain separation maintained (ADR-001 compliance)

## **Related ADRs**

- **ADR-001**: Domain separation principles
- **ADR-005**: QBO API strategy
- **ADR-003**: Multi-tenancy patterns

---

*This ADR establishes the data orchestrator pattern as the standard approach for runway experience services, providing a clean separation between data management and business logic while maintaining compliance with domain separation principles.*
