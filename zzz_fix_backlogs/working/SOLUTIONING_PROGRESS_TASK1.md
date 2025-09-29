# Solutioning Progress - Task 1: Calculator → Experience Data Flow

*Status: ✅ ANALYSIS COMPLETE - Ready for Architecture Decisions*

## **Problem Statement (Clarified)**

**Original Problem**: Calculator → Experience data flow is broken with runtime errors and domain separation violations.

**Root Cause Identified**: `RunwayCalculator` is a rogue attempt to replace `get_X_qbo_data_for_Y` pattern, but it's doing data pulling instead of calculating. It violates ADR-001 by pulling data instead of calculating with data.

**Core Architectural Challenge**: Each experience needs different entities, time windows, and runtime patterns, but domains/ services are generic CRUD primitives. We need a waypoint layer that's runway-aware but still uses domains/ primitives.

## **Architecture Decisions Made**

### **1. Experience Distinction Clarified**
- **Hygiene Tray**: Data quality fixes (independent actions, queue-based)
- **Decision Console**: Runway decisions (context-aware, batch approval)
- **Digest**: Weekly analysis (all data, async batch)
- **Test Drive**: PLG experience (4 weeks data, on-demand)

### **2. Data Orchestrator Pattern**
- **Problem**: Each experience needs different entity combinations and time windows
- **Solution**: Create experience-specific data orchestrators in `runway/core/`
- **Pattern**: `Experience → DataOrchestrator → Domains/ → SmartSyncService`

### **3. Two-Step Approval UX Validated**
- **Pattern**: Decide → Review → Final Approval
- **Research**: This is good UX for high-stakes financial decisions
- **Implementation**: Build approval queue, show cumulative impact, allow modifications

## **Proposed Architecture**

```
runway/experiences/ (functionality + UX)
    ↓
runway/core/data_orchestrators/ (experience-specific data pulling)
    ↓
runway/core/calculators/ (pure calculation services)
    ↓
domains/ (CRUD primitives)
    ↓
SmartSyncService (orchestration)
```

**Data Flow Examples**:
- `HygieneTrayService` → `HygieneTrayDataOrchestrator` → `ARService/APService` → `SmartSyncService`
- `DecisionConsoleService` → `DecisionConsoleDataOrchestrator` → `ARService/APService` → `SmartSyncService`
- `DigestService` → `DigestDataOrchestrator` → `ARService/APService` → `SmartSyncService`

## **Implementation Plan**

### **Phase 1: Create Data Orchestrators**
- Create `runway/core/data_orchestrators/` directory
- Implement `HygieneTrayDataOrchestrator`, `DecisionConsoleDataOrchestrator`, `DigestDataOrchestrator`, `TestDriveDataOrchestrator`
- Each orchestrator pulls required entities with experience-specific context

### **Phase 2: Refactor RunwayCalculator**
- Remove data pulling logic from `RunwayCalculator`
- Make it pure calculation service that takes orchestrated data
- Rename to `RunwayCalculationService` for clarity

### **Phase 3: Update Experience Services**
- Update experiences to use their specific orchestrator + calculator
- Remove direct SmartSyncService calls from experiences
- Implement proper error handling and fallbacks

### **Phase 4: Remove Mock Violations**
- Replace hardcoded returns with orchestrator calls
- Focus on getting code working, not systematic mock removal

## **Key Decisions Made**

1. **Orchestrator Granularity**: ✅ **One orchestrator per experience** - Start simple, optimize later
2. **Implementation Order**: ✅ **Tray → Console → TestDrive → Digest** - Start with simplest
3. **Orchestrator Pattern**: ✅ **Service pattern with state management** - Unified approach for all experiences
4. **State Management**: ✅ **Data Orchestrator manages state** - Single source of truth for data + state
5. **Batch Processing**: ✅ **Defer to later** - Implement orchestrator pattern first

## **Architecture Decisions Finalized**

### **Data Orchestrator Pattern**
- **Location**: `runway/core/data_orchestrators/`
- **Pattern**: Service pattern with state management capabilities
- **State Management**: Orchestrator manages state, not experience services
- **Benefits**: Frontend consistency, state persistence, cleaner experience services, better scalability

### **State Management Architecture**
```
Frontend ↔ Experience Service ↔ Data Orchestrator ↔ Domains/
         (business logic)      (data + state)      (CRUD)
```

**Rationale**: Data orchestrator becomes single source of truth for both data and state, making it easier for frontend and experience services to work together.

## **Success Criteria**

- [ ] All experiences use their specific data orchestrator
- [ ] No direct SmartSyncService calls from experiences
- [ ] RunwayCalculator is pure calculation service
- [ ] No runtime errors from broken method calls
- [ ] Domain separation maintained (ADR-001 compliance)
- [ ] Mock violations removed (quick fixes only)

## **Next Steps**

1. **Get architectural decisions** on pending questions
2. **Create executable tasks** for implementation
3. **Update other solutioning tasks** with implications
4. **Move to execution phase** once decisions are made

## **Implications for Other Tasks**

### **Task 2: Digest Data Architecture**
- Digest will use `DigestDataOrchestrator` pattern
- Bulk operations will be orchestrated batch processing
- No more `get_qbo_data_for_digest` pattern

### **Task 3: Testing Strategy**
- Test orchestrators with sandbox data
- Test calculators with orchestrated data
- Test experiences with orchestrator + calculator pattern

## **Files to Update**

- `runway/core/runway_calculator.py` - Refactor to pure calculation
- `runway/experiences/digest.py` - Use DigestDataOrchestrator
- `runway/experiences/tray.py` - Use HygieneTrayDataOrchestrator
- `runway/experiences/console.py` - Use DecisionConsoleDataOrchestrator
- `runway/experiences/test_drive.py` - Use TestDriveDataOrchestrator

## **Status: ⚠️ ARCHITECTURAL AUDIT REQUIRED**

**CRITICAL DISCOVERY**: Implementation of ADR-006 revealed massive architectural inconsistencies that must be addressed before Task 1 can be considered truly executable.

## **Major Issues Discovered**

### **1. Priority Calculation Logic Duplication (Rabbit Droppings)**
- **5+ different implementations** of priority calculation logic scattered across services
- **Bill priority**: 3 different implementations with different business rules
- **AR priority**: 2 different implementations with different scoring systems
- **No single source of truth** for priority calculations

### **2. RunwayCalculator Scope Creep**
- **Monolithic service** doing too much (entity-specific calculations, console logic, tray logic)
- **Violates ADR-001** by doing domain-specific work instead of pure runway calculations
- **Missing separation** between generic domain logic and product-specific runway logic

### **3. Domain Service Organization Confusion**
- **AP Services**: `ap_ingestion.py` vs `bill_ingestion.py` duplication
- **AR Services**: `ar_plan.py` vs `collections.py` vs `invoice.py` overlap
- **Payment Services**: `payment_application.py` vs `payment_matching.py` confusion
- **Balance Service**: Should be in `domains/bank` not `domains/core`

### **4. Missing Integration**
- **Tray experience** still has its own calculator priority functions
- **Experiences not dependent** on `runway/core` services
- **No clear separation** between domain services and runway services

## **Task 1.5 Required**

**Title**: Consolidate Priority Logic and Clarify Domain Service Boundaries

**Scope**: 
- Audit and consolidate all priority calculation logic
- Resolve domain service duplication and overlap  
- Refactor RunwayCalculator to pure calculation service
- Ensure proper ADR-001 and ADR-006 compliance

**Dependencies**: Must be completed before Task 1 can be considered truly executable

## **Status: ⚠️ REQUIRES TASK 1.5 COMPLETION**

Task 1 solutioning is complete, but execution requires Task 1.5 to address foundational architectural issues discovered during implementation.

## **ADR Recommendation**

This represents a significant architectural decision that should be documented as an ADR:

**ADR-006: Data Orchestrator Pattern for Experience Services**
- **Decision**: Use data orchestrators in `runway/core/` to manage both data pulling and state management
- **Rationale**: Provides single source of truth, enables frontend consistency, and maintains clean separation of concerns
- **Implications**: All experience services will use orchestrator pattern, state management centralized
