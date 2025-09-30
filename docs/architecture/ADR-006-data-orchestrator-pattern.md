# ADR-006: Data Orchestrator Pattern

**Date**: 2025-01-27  
**Status**: Accepted  
**Decision**: Use data orchestrators in `runway/services/` to manage data pulling and state management for experience services

**Updated**: 2025-01-27  
**Status**: Updated  
**Decision**: Establish complete architecture pattern: Data Orchestrators → Calculators → Experiences with clear naming conventions and folder structure

## Context

Runway experience services need different entity combinations and time windows, but domains/ services are generic CRUD primitives. Need waypoint layer that's runway-aware but uses domains/ primitives.

**Problem**: Each experience needs different entity combinations, time windows, runtime patterns, and state management.

## Decision

**Complete Architecture Pattern**:
- **Location**: `runway/services/` with clear hierarchy
- **Pattern**: Data Orchestrators → Calculators → Experiences
- **Architecture**: `Frontend ↔ Experience Service ↔ Calculator ↔ Data Orchestrator ↔ Domains/`

### **Folder Structure**
```
runway/services/
├── 0_data_orchestrators/  # Data pulling + state management
├── 1_calculators/         # Pure business logic calculations  
└── 2_experiences/         # User-facing experience services
```

### **Naming Conventions**
- **Data Orchestrators**: `[Experience]DataOrchestrator` (e.g., `HygieneTrayDataOrchestrator`)
- **Calculators**: `[Domain][Function]Calculator` (e.g., `RunwayCalculator`, `PriorityCalculator`)
- **Experience Services**: `[Experience]Service` (e.g., `HygieneTrayService`)

## Architecture Pattern
```
Frontend (UI/UX)
    ↓
runway/services/2_experiences/ (user-facing experience services)
    ↓
runway/services/1_calculators/ (pure business logic calculations)
    ↓
runway/services/0_data_orchestrators/ (data pulling + state management)
    ↓
domains/ (CRUD primitives)
    ↓
SmartSyncService (QBO orchestration)
```

### **Data Flow**
1. **Frontend** makes API request to experience service
2. **Experience Service** orchestrates between calculators and data orchestrator
3. **Calculators** transform raw data into insights and metrics
4. **Data Orchestrator** pulls data from domains and manages state
5. **Domains** provide CRUD primitives for business entities
6. **SmartSyncService** handles QBO API integration

## Implementation Pattern

### **Data Orchestrator Structure**
```python
# runway/services/0_data_orchestrators/[experience]_data_orchestrator.py
class [Experience]DataOrchestrator:
    def __init__(self, db: Session):
        self.db = db  # No instance state - stateless service
    
    async def get_[experience]_data(self, business_id: str) -> Dict[str, Any]:
        # Pull all required data for experience
        # State management with proper business_id scoping
        # Return raw data + current state
    
    # Additional methods for state management as needed
    async def [experience_specific_method](self, business_id: str, ...) -> Dict[str, Any]:
        # Experience-specific functionality
        # ALL state operations must be scoped by business_id
```

### **Calculator Structure**
```python
# runway/services/1_calculators/[domain]_[function]_calculator.py
class [Domain][Function]Calculator:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
    
    def calculate_[function](self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Pure calculation logic
        # No state management
        # Returns calculated metrics/insights
```

### **Experience Service Structure**
```python
# runway/services/2_experiences/[experience].py
class [Experience]Service:
    def __init__(self, db: Session):
        self.db = db
        # Data orchestrator for data pulling
        self.data_orchestrator = [Experience]DataOrchestrator(db)
        # Calculators for business logic
        self.runway_calculator = RunwayCalculator(db, business_id)
        self.priority_calculator = PriorityCalculator(db, business_id)
    
    async def get_[experience]_data(self, business_id: str) -> Dict[str, Any]:
        # Get raw data from orchestrator
        raw_data = await self.data_orchestrator.get_[experience]_data(business_id)
        # Transform with calculators
        insights = self.runway_calculator.calculate_runway(raw_data)
        priorities = self.priority_calculator.calculate_priorities(raw_data)
        # Combine and return
        return self._combine_results(raw_data, insights, priorities)
```

### Multi-Tenancy Requirements
```python
# CRITICAL: All state management must be scoped by business_id
class [Experience]DataOrchestrator:
    async def _get_state(self, business_id: str) -> Dict[str, Any]:
        # State stored in database with business_id foreign key
        # NEVER store state in instance variables
        return await self.db.query(StateTable).filter(
            StateTable.business_id == business_id
        ).first()
    
    async def _store_state(self, business_id: str, state: Dict[str, Any]) -> None:
        # All state operations scoped to business_id
        # Ensures complete isolation between businesses
        state_record = StateTable(
            business_id=business_id,  # ← CRITICAL: Always scope by business_id
            state_data=state
        )
        self.db.add(state_record)
        self.db.commit()
```

### Experience Service Usage
```python
# runway/experiences/[experience].py
class [Experience]Service:
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = [Experience]DataOrchestrator()
    
    async def get_data(self, business_id: str) -> Dict[str, Any]:
        return await self.orchestrator.get_[experience]_data(business_id)
```

## Benefits
1. **Single Source of Truth**: Data orchestrator manages both data and state
2. **Frontend Consistency**: Frontend can always get current state from orchestrator
3. **State Persistence**: State survives service restarts and multiple frontend instances
4. **Cleaner Experience Services**: Focus on business logic, not state management
5. **Better Testing**: Can test state management independently
6. **Scalability**: Multiple frontend instances can share state
7. **Multi-Tenant Safety**: All state scoped by business_id ensures complete isolation
8. **Stateless Services**: Services remain stateless for horizontal scaling
9. **ADR-001 Compliance**: Domains/ remain pure CRUD primitives
10. **Clear Separation**: Data orchestrators handle data, calculators handle logic, experiences handle UX
11. **Reusable Components**: Calculators can be shared across experiences
12. **Maintainable Architecture**: Clear boundaries between data, logic, and presentation layers

## **Examples**

### **Hygiene Tray (Simple)**
```python
# runway/services/0_data_orchestrators/hygiene_tray_data_orchestrator.py
class HygieneTrayDataOrchestrator:
    async def get_tray_data(self, business_id: str) -> Dict[str, Any]:
        # Pull raw data from domains
        bills = await self.ap_service.get_bills_with_issues(business_id)
        invoices = await self.ar_service.get_invoices_with_issues(business_id)
        return {"bills": bills, "invoices": invoices}

# runway/services/1_calculators/data_quality_calculator.py
class DataQualityCalculator:
    def calculate_hygiene_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Pure calculation logic
        return {"hygiene_score": 85, "issues": [...]}

# runway/services/2_experiences/tray.py
class HygieneTrayService:
    def __init__(self, db: Session):
        self.data_orchestrator = HygieneTrayDataOrchestrator(db)
        self.data_quality_calculator = DataQualityCalculator(db, business_id)
    
    async def get_tray_data(self, business_id: str) -> Dict[str, Any]:
        raw_data = await self.data_orchestrator.get_tray_data(business_id)
        hygiene_analysis = self.data_quality_calculator.calculate_hygiene_score(raw_data)
        return self._combine_results(raw_data, hygiene_analysis)
```

### **Decision Console (Stateful)**
```python
# runway/services/0_data_orchestrators/decision_console_data_orchestrator.py
class DecisionConsoleDataOrchestrator:
    def __init__(self, db: Session):
        self.db = db  # No instance state
    
    async def get_console_data(self, business_id: str) -> Dict[str, Any]:
        # Pull data + current decision queue (scoped by business_id)
        base_data = await self._pull_base_data(business_id)
        decision_queue = await self._get_decision_queue(business_id)  # ← Scoped by business_id
        return {**base_data, "decision_queue": decision_queue}
    
    async def add_decision(self, business_id: str, decision: Dict) -> Dict:
        await self._store_decision(business_id, decision)  # ← Scoped by business_id
        return await self.get_console_data(business_id)
    
    async def _get_decision_queue(self, business_id: str) -> List[Dict]:
        # State stored in database with business_id scoping
        business = self.db.query(Business).filter(Business.business_id == business_id).first()
        return business.metadata.get("decision_queue", [])
    
    async def _store_decision(self, business_id: str, decision: Dict) -> None:
        # All state operations scoped to business_id
        business = self.db.query(Business).filter(Business.business_id == business_id).first()
        if not business.metadata:
            business.metadata = {}
        business.metadata.setdefault("decision_queue", []).append(decision)
        self.db.commit()
```

## **Implications**

- **All experience services** will use orchestrator pattern
- **State management** centralized in orchestrators
- **Frontend** talks to experience services, which orchestrate calculators and orchestrators
- **Domains/ services** remain pure CRUD primitives
- **SmartSyncService** used only by orchestrators, not experiences
- **Calculators** provide pure business logic and can be shared across experiences
- **Clear separation** between data orchestration, business logic, and user experience

## **Migration Strategy**

1. **Phase 1**: Create orchestrators for each experience
2. **Phase 2**: Update experience services to use orchestrators + calculators
3. **Phase 3**: Remove direct SmartSyncService calls from experiences
4. **Phase 4**: Refactor existing calculators to pure calculation services
5. **Phase 5**: Create missing specific calculators for new functionality

## **Success Criteria**

- [ ] All experiences use their specific data orchestrator
- [ ] No direct SmartSyncService calls from experiences
- [ ] State management centralized in orchestrators
- [ ] Frontend can get consistent state from orchestrators
- [ ] Domain separation maintained (ADR-001 compliance)
- [ ] Calculators provide pure business logic and can be shared
- [ ] Clear separation between data orchestration, business logic, and user experience
- [ ] All components follow naming conventions: `[Domain][Function]Calculator`

## **Related ADRs**

- **ADR-001**: Domain separation principles
- **ADR-005**: QBO API strategy
- **ADR-003**: Multi-tenancy patterns

---

*This ADR establishes the data orchestrator pattern as the standard approach for runway experience services, providing a clean separation between data management and business logic while maintaining compliance with domain separation principles.*
