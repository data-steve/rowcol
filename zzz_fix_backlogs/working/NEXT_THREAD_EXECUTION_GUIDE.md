# Next Thread Execution Guide

*Ready for immediate execution - 2025-01-27*

## **🎯 IMMEDIATE EXECUTION TASKS**

### **Task 1.3: TestDrive Data Orchestrator**
- **Status**: `[ ]` Ready for execution
- **Priority**: P1 High
- **Pattern**: Follows Task 1.2 pattern - TestDriveService uses TestDriveDataOrchestrator + RunwayCalculationService + PriorityCalculationService
- **Files**: 
  - Create: `runway/core/data_orchestrators/test_drive_data_orchestrator.py`
  - Update: `runway/experiences/test_drive.py`
- **Key Pattern**: Experience uses BOTH orchestrator AND calculation services directly

### **Task 1.4: Digest Data Orchestrator**
- **Status**: `[ ]` Ready for execution
- **Priority**: P1 High
- **Pattern**: Follows Task 1.2 pattern - DigestService uses DigestDataOrchestrator + RunwayCalculationService + PriorityCalculationService
- **Files**:
  - Create: `runway/core/data_orchestrators/digest_data_orchestrator.py`
  - Update: `runway/experiences/digest.py`, `infra/scheduler/digest_jobs.py`
- **Key Pattern**: Experience uses BOTH orchestrator AND calculation services directly

### **Task 2: QBOMapper Implementation**
- **Status**: `[ ]` Ready for execution
- **Priority**: P1 High
- **Pattern**: Centralized QBO field mapping service
- **Files**:
  - Create: `runway/core/data_mappers/qbo_mapper.py`
  - Update: Multiple files with QBO field access

## **📋 CRITICAL SUCCESS PATTERNS**

### **Experience Service Pattern (MANDATORY)**
Every experience service MUST follow this pattern:

```python
class ExperienceService:
    def __init__(self, db: Session, business_id: str):
        # Data orchestrator for data pulling + state management
        self.data_orchestrator = ExperienceDataOrchestrator(db, business_id)
        
        # Calculation services for business logic
        self.runway_calculator = RunwayCalculationService(db, business_id)
        self.priority_calculator = PriorityCalculationService(db, business_id)
        self.bill_impact_calculator = BillImpactCalculator()  # Stateless
        self.tray_item_impact_calculator = TrayItemImpactCalculator()  # Stateless
    
    async def get_experience_data(self, business_id: str):
        # 1. Get data from orchestrator
        qbo_data = await self.data_orchestrator.get_experience_data(business_id)
        
        # 2. Get runway context using calculation services
        runway_context = self.runway_calculator.calculate_current_runway(qbo_data)
        
        # 3. Calculate entity-specific impacts (stateless)
        bill_impacts = self.bill_impact_calculator.calculate_bill_runway_impact(bills, runway_context)
        tray_impacts = self.tray_item_impact_calculator.calculate_tray_item_runway_impact(items, runway_context)
        
        # 4. Calculate priorities
        priorities = self.priority_calculator.calculate_tray_item_priority(items)
        
        # 5. Combine results
        return self._combine_results(qbo_data, runway_context, bill_impacts, tray_impacts, priorities)
```

### **Key Principles**
1. **BOTH Pattern**: Experiences use BOTH orchestrators AND calculation services
2. **Stateless Calculators**: Entity impact calculators are stateless and receive runway context as parameters
3. **No Circular Dependencies**: RunwayCalculationService has no dependencies on other services
4. **ADR-001 Compliance**: Domains/ never depend on runway/ services

## **📁 REFERENCE FILES**

### **Architecture Context**
- `ARCHITECTURAL_FOUNDATION_SUMMARY.md` - Complete architectural decisions and patterns
- `001_EXECUTABLE_TASKS.md` - Updated with corrected Task 1.3 and 1.4
- `002_NEEDS_SOLVING_TASKS.md` - Remaining solutioning work

### **Implementation Examples**
- `runway/experiences/tray.py` - Example of correct pattern implementation
- `runway/experiences/console.py` - Example of correct pattern implementation
- `runway/core/data_orchestrators/hygiene_tray_data_orchestrator.py` - Example orchestrator
- `runway/core/data_orchestrators/decision_console_data_orchestrator.py` - Example orchestrator

## **🚀 EXECUTION ORDER**

1. **Start with Task 1.3** - TestDrive Data Orchestrator
   - Follows established pattern
   - Clear implementation examples
   - Straightforward execution

2. **Then Task 1.4** - Digest Data Orchestrator
   - Follows established pattern
   - Includes bulk processing
   - Clear implementation examples

3. **Then Task 2** - QBOMapper Implementation
   - Centralized field mapping
   - Multiple file updates
   - Straightforward execution

## **⚠️ CRITICAL WARNINGS**

1. **DO NOT** create `IntegratedCalculationService` - it conflicts with existing pattern
2. **DO NOT** create circular dependencies - entity calculators must be stateless
3. **DO NOT** bypass the orchestrator pattern - experiences must use both orchestrators AND calculators
4. **DO NOT** mix data pulling and business logic - orchestrators handle data, calculators handle logic

## **✅ VERIFICATION COMMANDS**

After each task completion:

```bash
# Check for correct pattern usage
grep -r "DataOrchestrator.*CalculationService" runway/experiences/
grep -r "RunwayCalculationService.*PriorityCalculationService" runway/experiences/

# Check for no old patterns
grep -r "RunwayCalculator" runway/experiences/
grep -r "IntegratedCalculationService" runway/

# Check server status
# Check uvicorn in Cursor terminal - should be running without errors
```

## **📊 SUCCESS METRICS**

- All experience services follow the established pattern
- No circular dependencies between services
- All QBO field access uses centralized mapper
- Server runs without errors
- All tests pass

**Ready for execution!** 🚀
