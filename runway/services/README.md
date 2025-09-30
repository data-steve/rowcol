# Runway Services Architecture

This directory contains all runway-specific services organized by architectural layer and responsibility.

## **Architecture Overview**

The runway services follow a clear hierarchy that separates concerns and enables reusability:

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

## **Folder Structure**

### **0_data_orchestrators/** - Data Pulling + State Management
- **Purpose**: Pull raw data from domains and manage experience-specific state
- **Responsibilities**: 
  - Data aggregation from multiple domains
  - State management (queues, progress, etc.)
  - Multi-tenant safety with business_id scoping
- **Examples**: `HygieneTrayDataOrchestrator`, `DecisionConsoleDataOrchestrator`

### **1_calculators/** - Pure Business Logic Calculations
- **Purpose**: Transform raw data into insights and metrics
- **Responsibilities**:
  - Pure calculation logic (no state management)
  - Business rule implementation
  - Metric generation and analysis
- **Examples**: `RunwayCalculator`, `PriorityCalculator`, `DataQualityCalculator`

### **2_experiences/** - User-Facing Experience Services
- **Purpose**: Orchestrate between calculators and data orchestrators for user experiences
- **Responsibilities**:
  - User-facing business logic
  - API response formatting
  - Experience orchestration
- **Examples**: `HygieneTrayService`, `DecisionConsoleService`, `DigestService`

## **Naming Conventions**

### **Data Orchestrators**
- Pattern: `[Experience]DataOrchestrator`
- Examples: `HygieneTrayDataOrchestrator`, `DecisionConsoleDataOrchestrator`
- Purpose: Pull data and manage state for specific experiences

### **Calculators**
- Pattern: `[Domain][Function]Calculator`
- Examples: `RunwayCalculator`, `PriorityCalculator`, `DataQualityCalculator`
- Purpose: Pure business logic calculations

### **Experience Services**
- Pattern: `[Experience]Service`
- Examples: `HygieneTrayService`, `DecisionConsoleService`
- Purpose: User-facing experience orchestration

## **Data Flow**

1. **Frontend** makes API request to experience service
2. **Experience Service** orchestrates between calculators and data orchestrator
3. **Calculators** transform raw data into insights and metrics
4. **Data Orchestrator** pulls data from domains and manages state
5. **Domains** provide CRUD primitives for business entities
6. **SmartSyncService** handles QBO API integration

## **Key Principles**

### **Separation of Concerns**
- **Data Orchestrators**: Handle data pulling and state management
- **Calculators**: Handle pure business logic calculations
- **Experience Services**: Handle user-facing orchestration

### **Multi-Tenancy**
- All state operations must be scoped by business_id
- No shared state between businesses
- Complete isolation at the data layer

### **Reusability**
- Calculators can be shared across experiences
- Data orchestrators are experience-specific
- Experience services orchestrate between components

### **Stateless Services**
- All services remain stateless for horizontal scaling
- State is managed in the database with business_id scoping
- No instance variables that persist across requests

## **Implementation Guidelines**

### **Data Orchestrators**
```python
class [Experience]DataOrchestrator:
    def __init__(self, db: Session):
        self.db = db  # No instance state - stateless service
    
    async def get_[experience]_data(self, business_id: str) -> Dict[str, Any]:
        # Pull all required data for experience
        # State management with proper business_id scoping
        # Return raw data + current state
```

### **Calculators**
```python
class [Domain][Function]Calculator:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
    
    def calculate_[function](self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Pure calculation logic
        # No state management
        # Returns calculated metrics/insights
```

### **Experience Services**
```python
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

## **Related Documentation**

- **ADR-006**: Data Orchestrator Pattern
- **ADR-001**: Domain separation principles
- **ADR-005**: QBO API strategy
- **ADR-003**: Multi-tenancy patterns

---

*This architecture provides clear separation of concerns, enables reusability, and maintains compliance with domain separation principles.*
