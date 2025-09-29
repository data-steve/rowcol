# Solutioning Progress - Task 1.2: Design RunwayCalculator Service Architecture

*Status: 🔄 IN PROGRESS - Discovery Phase Complete, Analysis Phase Started*

## **Problem Statement**

RunwayCalculator has scope creep with mixed responsibilities violating ADR-001. Need to design proper service architecture that serves as foundation for priority scoring and other runway calculations. Current design mixes pure runway calculations with entity-specific calculations, making it unclear what belongs where.

## **Discovery Findings**

### **What Actually Exists:**

#### **RunwayCalculator Current Methods:**
1. **`calculate_current_runway(qbo_data)`** - Core runway calculation using cash position, burn rate, AR/AP
2. **`calculate_scenario_impact(scenario, qbo_data)`** - Compares baseline vs scenario runway
3. **`calculate_weekly_analysis(week_start, week_end, qbo_data)`** - Week-specific runway analysis
4. **`calculate_historical_runway(weeks_back, qbo_data)`** - Historical runway analysis for test drive
5. **`calculate_bill_runway_impact(bill_data)`** - Entity-specific: bill payment impact
6. **`calculate_tray_item_runway_impact(item_data)`** - Entity-specific: tray item impact
7. **`calculate_daily_burn_rate(qbo_data)`** - Utility: extract burn rate from data

#### **Priority Calculation Services:**
1. **`PriorityCalculationService`** - Centralized priority scoring (bills, invoices, collections, tray items)
2. **`PaymentPriorityCalculator`** - Bill payment priority (duplicate of PriorityCalculationService)
3. **`TrayPriorityCalculator`** - Tray item priority (duplicate of PriorityCalculationService)

#### **Experience Usage Patterns:**
- **Tray**: Uses `TrayPriorityCalculator` + `PaymentPriorityCalculator` + `RunwayCalculator` for impact
- **Console**: Uses `RunwayCalculator.calculate_current_runway()` for context
- **Digest**: Uses `RunwayCalculator.calculate_current_runway()` for weekly analysis
- **Test Drive**: Uses `RunwayCalculator.calculate_historical_runway()` for trend analysis

### **What the Task Assumed:**
- Clear separation between "scenario impact" vs "historical runway" vs "current runway"
- Entity-specific calculations properly organized
- Priority scoring integrated with runway calculations

### **Assumptions That Were Wrong:**
- **Method naming is inconsistent**: "scenario impact" vs "historical runway" vs "current runway" don't align well
- **Entity-specific calculations mixed in**: `calculate_bill_runway_impact()` and `calculate_tray_item_runway_impact()` are in RunwayCalculator
- **Priority services duplicated**: Three different priority calculation services exist
- **No clear foundation**: Each experience imports different combinations of services

### **Architecture Mismatches:**
1. **RunwayCalculator violates ADR-001**: Contains entity-specific calculations (bills, tray items)
2. **Priority calculation scattered**: Three different services doing similar work
3. **Inconsistent naming**: "scenario impact" vs "historical runway" vs "current runway" don't form coherent categories
4. **Mixed responsibilities**: Pure calculations mixed with entity-specific calculations

### **Task Scope Issues:**
- Need to understand what "scenario impact" vs "historical runway" vs "current runway" actually represent
- Need to determine proper boundaries between pure runway calculations and entity-specific calculations
- Need to integrate priority scoring with runway calculations properly
- **Need to clarify hygiene vs decision boundaries** - What blocks bills/invoices from being decision-ready?

## **Analysis Phase - Current Architecture Issues**

### **1. Method Categorization Analysis**

**After Reading Implementation, Methods Fall Into Clear Categories:**

#### **Pure Runway Calculations (Core Business Logic):**
- `calculate_current_runway(qbo_data)` - **Core runway calculation**: Cash + AR - AP / burn rate
- `calculate_scenario_impact(scenario, qbo_data)` - **Scenario analysis**: Compare baseline vs modified runway
- `calculate_historical_runway(weeks_back, qbo_data)` - **Historical analysis**: Runway trends over time
- `calculate_weekly_analysis(week_start, week_end, qbo_data)` - **Week-specific analysis**: Format runway for weekly context

#### **Entity-Specific Impact Calculations (Violate ADR-001):**
- `calculate_bill_runway_impact(bill_data)` - **Bill impact**: How paying a bill affects runway
- `calculate_tray_item_runway_impact(item_data)` - **Tray item impact**: How resolving tray item affects runway

#### **Utility Functions:**
- `calculate_daily_burn_rate(qbo_data)` - **Data extraction**: Extract burn rate from QBO data

**The Problem**: Entity-specific calculations (`bill_runway_impact`, `tray_item_runway_impact`) don't belong in RunwayCalculator - they violate ADR-001 by mixing domain-specific logic with pure runway calculations.

### **2. Priority Calculation Architecture Analysis**

**After Reading Implementation, Priority Services Have Different Purposes:**

#### **PriorityCalculationService (Centralized):**
- **Purpose**: Centralized priority scoring for all entities
- **Methods**: `calculate_bill_priority_score()`, `calculate_invoice_priority_score()`, `calculate_collection_priority_score()`, `calculate_tray_item_priority()`
- **Scope**: All priority calculations in one place

#### **PaymentPriorityCalculator (Specialized):**
- **Purpose**: Bill payment prioritization with runway integration
- **Methods**: `calculate_bill_priority_score()` (duplicate), `calculate_payment_decision_analysis()`, `generate_payment_scenarios()`
- **Scope**: Bill-specific priority with payment decision analysis

#### **TrayPriorityCalculator (Specialized):**
- **Purpose**: Tray item prioritization with runway integration
- **Methods**: `calculate_tray_item_priority()` (duplicate), `calculate_bill_tray_priority()`, `calculate_invoice_tray_priority()`
- **Scope**: Tray-specific priority with runway impact analysis

**The Problem**: 
1. **Method Duplication**: `calculate_bill_priority_score()` exists in both `PriorityCalculationService` and `PaymentPriorityCalculator`
2. **Method Duplication**: `calculate_tray_item_priority()` exists in both `PriorityCalculationService` and `TrayPriorityCalculator`
3. **Unclear Boundaries**: When to use centralized vs specialized services?
4. **Circular Dependencies**: `TrayPriorityCalculator` imports `PaymentPriorityCalculator` which imports `RunwayCalculator`

### **3. Experience Service Dependencies**

**Each Experience Imports Different Services:**
- **Tray**: `TrayPriorityCalculator` + `PaymentPriorityCalculator` + `RunwayCalculator`
- **Console**: `RunwayCalculator` only
- **Digest**: `RunwayCalculator` only  
- **Test Drive**: `RunwayCalculator` + `DataQualityAnalyzer`

**The Problem**: No consistent pattern for how experiences should get calculations.

## **Design Phase - Service Architecture Solution**

### **Key Questions Resolved**

1. **"scenario impact" vs "historical runway" vs "current runway" represent different time perspectives:**
   - **Current runway**: Right now, based on current data
   - **Scenario impact**: What if we changed something (future projection)
   - **Historical runway**: What was runway in the past (trend analysis)
   - **Solution**: These are all pure runway calculations and belong in the same service

2. **Entity-specific calculations should be separate calculators:**
   - Bills, invoices, collections, tray items each need their own impact calculators
   - They should be **stateless** and receive runway context as parameters (no circular dependencies)
   - **Solution**: Create separate entity impact calculators that receive runway context

3. **Priority scoring should be centralized:**
   - Current problem: Three services doing similar work (`TrayPriorityCalculator`, `PaymentPriorityCalculator`, `PriorityCalculationService`)
   - All have `calculate_bill_priority_score()` methods with slightly different logic
   - **Solution**: Use one centralized `PriorityCalculationService`

4. **Data Orchestrator Pattern Integration:**
   - **Experiences call both orchestrators AND calculation services directly** - not through an orchestration layer
   - Data orchestrators handle data pulling + state management
   - Calculation services handle business logic
   - **Solution**: Don't add `IntegratedCalculationService` - it conflicts with existing pattern

### **Proposed Service Architecture (CORRECTED)**

#### **1. RunwayCalculationService (Pure Runway Calculations)**
```python
class RunwayCalculationService:
    """Pure runway calculations - no entity-specific logic"""
    
    def calculate_current_runway(self, qbo_data: Dict) -> Dict
    def calculate_scenario_impact(self, scenario: Dict, qbo_data: Dict) -> Dict  
    def calculate_historical_runway(self, weeks_back: int, qbo_data: Dict) -> List[Dict]
    def calculate_weekly_analysis(self, week_start: datetime, week_end: datetime, qbo_data: Dict) -> Dict
    
    # Utility methods
    def calculate_daily_burn_rate(self, qbo_data: Dict) -> float
    def calculate_cash_position(self, qbo_data: Dict) -> float
    def calculate_ar_position(self, qbo_data: Dict) -> float
    def calculate_ap_position(self, qbo_data: Dict) -> float
```

#### **2. Entity Impact Calculators (Stateless, No Circular Dependencies)**
```python
class BillImpactCalculator:
    """Bill-specific runway impact calculations - STATELESS"""
    
    def calculate_bill_runway_impact(self, bill_data: Dict, runway_context: Dict) -> Dict
    def calculate_payment_impact(self, payment_data: Dict, runway_context: Dict) -> Dict

class TrayItemImpactCalculator:
    """Tray item-specific runway impact calculations - STATELESS
    
    Tray Items = Bills and invoices with **blocking data quality issues** that prevent them from being ready for decision-making:
    
    **AP Hygiene Issues (Bills):**
    - Missing due dates on bills → Can't schedule payment timing
    - Missing vendor information → Can't process payment
    - Missing line item details → Can't verify bill accuracy
    - Malformed data from QBO sync → Can't process bill
    
    **AR Hygiene Issues (Invoices):**
    - Incomplete customer data → Can't send invoice
    - Missing line item details → Can't send invoice
    - Unmatched AR payments → Can't identify truly overdue invoices (prevents false overdue calls)
    - Malformed data from QBO sync → Can't process invoice
    
    **Purpose**: Calculate runway impact of fixing these blocking issues before decision-making
    """
    
    def calculate_tray_item_runway_impact(self, item_data: Dict, runway_context: Dict) -> Dict
```

#### **3. PriorityCalculationService (Centralized Priority Scoring)**
```python
class PriorityCalculationService:
    """Centralized priority scoring for all entities - replaces duplicates"""
    
    def calculate_bill_priority_score(self, bill_data: Dict) -> float
    def calculate_invoice_priority_score(self, invoice_data: Dict) -> float
    def calculate_collection_priority_score(self, customer_data: Dict) -> float
    def calculate_tray_item_priority(self, item_data: Dict) -> Dict
```

#### **4. Data Orchestrators (Already Exist - Don't Change)**
```python
# Already implemented - keep as is
class HygieneTrayDataOrchestrator:
    async def get_tray_data(self, business_id: str) -> Dict[str, Any]

class DecisionConsoleDataOrchestrator:
    async def get_console_data(self, business_id: str) -> Dict[str, Any]
```

### **Integration Patterns (CORRECTED)**

#### **Experience Services Use Both Orchestrators AND Calculation Services:**
```python
# Tray Experience - CORRECT pattern
class TrayService:
    def __init__(self, db: Session, business_id: str):
        # Data orchestrator handles data pulling + state
        self.data_orchestrator = HygieneTrayDataOrchestrator(db, business_id)
        
        # Calculation services handle business logic
        self.runway_calculator = RunwayCalculationService(db, business_id)
        self.priority_calculator = PriorityCalculationService(db, business_id)
        self.bill_impact_calculator = BillImpactCalculator()
        self.tray_item_impact_calculator = TrayItemImpactCalculator()
    
    def get_tray_items(self, business_id: str) -> List[Dict]:
        # Get data from orchestrator
        qbo_data = await self.data_orchestrator.get_tray_data(business_id)
        
        # Get runway context
        runway_context = self.runway_calculator.calculate_current_runway(qbo_data)
        
        # Calculate entity-specific impacts (stateless)
        bill_impacts = self.bill_impact_calculator.calculate_bill_runway_impact(bills, runway_context)
        tray_impacts = self.tray_item_impact_calculator.calculate_tray_item_runway_impact(items, runway_context)
        
        # Calculate priorities
        priorities = self.priority_calculator.calculate_tray_item_priority(items)
        
        return self._combine_results(qbo_data, runway_context, bill_impacts, tray_impacts, priorities)
```

#### **Entity Impact Calculators Are Stateless (No Circular Dependencies):**
```python
class BillImpactCalculator:
    """Stateless - receives runway context as parameter"""
    
    def calculate_bill_runway_impact(self, bill_data: Dict, runway_context: Dict) -> Dict:
        # Use provided runway context (no service dependencies)
        amount = bill_data.get('amount', 0)
        daily_burn = runway_context.get('burn_rate', {}).get('daily_burn', 1)
        impact_days = amount / daily_burn if daily_burn > 0 else 0
        
        return {
            'impact_days': impact_days,
            'runway_after_payment': runway_context['base_runway_days'] - impact_days,
            'risk_level': self._determine_risk_level(impact_days)
        }
```

### **Benefits of This Architecture**

1. **Clear Separation of Concerns**: Pure runway calculations separate from entity-specific logic
2. **No Circular Dependencies**: RunwayCalculationService has no dependencies on other services
3. **Single Source of Truth**: One priority calculation service, one runway calculation service
4. **Easy to Test**: Each service can be tested independently
5. **Easy to Extend**: New entity types can get their own impact calculators
6. **ADR-001 Compliance**: Domain-specific logic separated from pure business logic

## **Implementation Plan (CORRECTED)**

### **Phase 1: Create New Service Structure**
1. **Rename `RunwayCalculator` to `RunwayCalculationService`** - Already refactored to pure calculations
2. **Create `BillImpactCalculator`** - Move bill-specific calculations from `RunwayCalculator` (stateless)
3. **Create `TrayItemImpactCalculator`** - Move tray item calculations from `RunwayCalculator` (stateless)
4. **Keep existing Data Orchestrators** - Don't change `HygieneTrayDataOrchestrator` and `DecisionConsoleDataOrchestrator`

### **Phase 2: Consolidate Priority Services**
1. **Keep `PriorityCalculationService`** - As centralized priority scoring
2. **Remove `PaymentPriorityCalculator`** - Merge into `PriorityCalculationService`
3. **Remove `TrayPriorityCalculator`** - Merge into `PriorityCalculationService`
4. **Update all references** - Use centralized priority service

### **Phase 3: Update Experience Services**
1. **Update `TrayService`** - Use both data orchestrator AND calculation services directly
2. **Update `ConsoleService`** - Use both data orchestrator AND calculation services directly
3. **Update `DigestService`** - Use both data orchestrator AND calculation services directly
4. **Update `TestDriveService`** - Use both data orchestrator AND calculation services directly

### **Phase 4: Remove Old Services**
1. **Remove `PaymentPriorityCalculator`** - Merged into `PriorityCalculationService`
2. **Remove `TrayPriorityCalculator`** - Merged into `PriorityCalculationService`
3. **Update all imports** - Use new service structure

## **Success Criteria**

- [ ] Clear separation between pure runway calculations and entity-specific calculations
- [ ] Single source of truth for priority calculations
- [ ] No circular dependencies between services
- [ ] All experiences use consistent calculation patterns
- [ ] ADR-001 compliance maintained
- [ ] Easy to test and extend

## **Files to Create**

### **New Services:**
- `runway/core/bill_impact_calculator.py` - Bill-specific impact calculations (stateless)
- `runway/core/tray_item_impact_calculator.py` - Tray item impact calculations (stateless)
  - **Tray Items**: Bills and invoices with **blocking data quality issues** that prevent them from being ready for decision-making
  - **Purpose**: Calculate runway impact of fixing data quality issues before decision-making

### **Files to Modify:**
- `runway/core/runway_calculator.py` - Rename to `runway_calculation_service.py` (already refactored)
- `runway/experiences/tray.py` - Use both data orchestrator AND calculation services directly
- `runway/experiences/console.py` - Use both data orchestrator AND calculation services directly
- `runway/experiences/digest.py` - Use both data orchestrator AND calculation services directly
- `runway/experiences/test_drive.py` - Use both data orchestrator AND calculation services directly

### **Files to Remove:**
- `runway/core/payment_priority_calculator.py` - Merged into PriorityCalculationService
- `runway/core/tray_priority_calculator.py` - Merged into PriorityCalculationService

## **Status: ✅ SOLUTIONING COMPLETE - READY FOR EXECUTION**

### **Solution Summary:**
- **Architecture**: Corrected to work with existing Data Orchestrator Pattern
- **Services**: Simple, focused services with clear responsibilities
- **Integration**: Experiences use both orchestrators AND calculation services directly
- **Dependencies**: No circular dependencies - entity calculators are stateless
- **Priority Logic**: Centralized in single `PriorityCalculationService`

### **Key Corrections Made:**
1. ✅ **Removed `IntegratedCalculationService`** - conflicts with existing pattern
2. ✅ **Fixed circular dependencies** - entity calculators are stateless
3. ✅ **Corrected integration pattern** - experiences call both orchestrators and calculators
4. ✅ **Simplified architecture** - work with existing patterns, don't replace them
5. ✅ **Consolidated priority logic** - single source of truth
6. ✅ **Clarified hygiene vs decision boundaries** - Hygiene = blocking issues that prevent bills/invoices from being decision-ready

### **Ready for Execution Tasks:**
The solutioning is complete and the architecture is correct. Execution tasks can now be created based on this comprehensive service architecture design.
