# Solutioning Progress - Task 1.5: Consolidate Priority Logic and Clarify Domain Service Boundaries

*Status: 🔄 IN PROGRESS - Architectural Analysis Required*

## **Problem Statement**

The implementation of ADR-006 revealed massive architectural inconsistencies that must be addressed before Task 1 can be considered truly executable:

1. **Priority calculation logic scattered across 5+ services** with conflicting implementations
2. **Domain service duplication and overlap** creating confusion about responsibilities  
3. **RunwayCalculator scope creep** violating ADR-001 principles
4. **QBO data mapping inconsistency** between domains/ and runway/ naming conventions
5. **Missing integration** between experiences and runway/core services

## **Architecture Decisions Required**

### **1. Priority Calculation Consolidation**

**Decision**: Move ALL priority calculation logic to `runway/core/priority_calculation_service.py`

**Rationale**: 
- Single source of truth for all priority calculations
- Eliminates "rabbit droppings" of duplicate logic
- Centralizes business rules for consistency
- Maintains ADR-001 separation (domains/ = data, runway/ = business logic)

**Implementation**:
```python
# runway/core/priority_calculation_service.py
class PriorityCalculationService:
    def calculate_bill_priority_score(self, bill_data: Dict) -> float
    def calculate_invoice_priority_score(self, invoice_data: Dict) -> float
    def calculate_tray_item_priority(self, item_data: Dict) -> Dict
    def calculate_collection_priority_score(self, customer_data: Dict) -> float
```

**Remove from**:
- `domains/ap/services/bill_ingestion.py:297` - `calculate_bill_priority()`
- `domains/ar/services/customer.py:62` - `calculate_collection_priority_score()`
- `runway/core/payment_priority_calculator.py:38` - `calculate_bill_priority_score()`
- `runway/core/tray_priority_calculator.py:39` - `calculate_tray_item_priority()`

### **2. Domain Service Consolidation**

#### **AP Services Consolidation**
**Decision**: Merge `ap_ingestion.py` into `bill_ingestion.py` and rename to `bill_service.py`

**Rationale**:
- `ap_ingestion.py` is just a wrapper around `bill_ingestion.py`
- `bill_ingestion.py` already has comprehensive bill lifecycle management
- Single canonical service for all bill operations

**Implementation**:
- Keep `BillService` as the canonical AP service
- Remove `IngestionService` from `ap_ingestion.py`
- Update all imports to use `BillService`

#### **AR Services Consolidation**
**Decision**: Clarify boundaries between AR services

**Current Services**:
- `InvoiceService` - Basic invoice CRUD operations
- `CollectionsService` - Overdue invoice tracking and reminders
- `ARPlanService` - AR planning and forecasting
- `CustomerService` - Customer management and priority scoring
- `PaymentApplicationService` - Payment application to invoices
- `PaymentMatchingService` - Payment matching and reconciliation

**Proposed Boundaries**:
- **`InvoiceService`** - Invoice CRUD, basic queries
- **`CollectionsService`** - Overdue tracking, reminder sending, aging analysis
- **`CustomerService`** - Customer management, payment history, reliability scoring
- **`PaymentMatchingService`** - Payment application + matching (merge the two)
- **`ARPlanService`** - Move to `runway/core/` as it's product-specific

#### **Payment Services Consolidation**
**Decision**: Merge `PaymentApplicationService` into `PaymentMatchingService`

**Rationale**:
- Payment application and matching are closely related
- Reduces service complexity
- Single service for all payment-related operations

### **3. QBO Data Mapping Strategy**

**Decision**: Create consistent data mapping layer in `runway/core/data_mappers/`

**Problem**: QBO field names vs runway field names create confusion
- QBO: `TotalAmt`, `DueDate`, `VendorRef`
- Runway: `amount`, `due_date`, `vendor_name`

**Solution**: Create mapper services that handle QBO → Runway field mapping

**Implementation**:
```python
# runway/core/data_mappers/qbo_mapper.py
class QBOMapper:
    def map_bill_data(self, qbo_bill: Dict) -> Dict:
        return {
            'amount': qbo_bill.get('TotalAmt', 0),
            'due_date': qbo_bill.get('DueDate'),
            'vendor_name': qbo_bill.get('VendorRef', {}).get('name'),
            'qbo_id': qbo_bill.get('Id'),
            # ... other mappings
        }
    
    def map_invoice_data(self, qbo_invoice: Dict) -> Dict:
        # Similar mapping for invoices
        pass
```

**Benefits**:
- Single place for QBO field mapping
- Consistent naming across runway services
- Easy to maintain when QBO API changes
- Clear separation between QBO data and runway data

### **4. RunwayCalculator Refactoring**

**Decision**: Split RunwayCalculator into focused services

**Current Issues**:
- Monolithic service doing too much
- Entity-specific calculations mixed with runway calculations
- Violates ADR-001 by doing domain-specific work

**Proposed Split**:
```python
# runway/core/runway_calculation_service.py - Pure runway calculations
class RunwayCalculationService:
    def calculate_current_runway(self, qbo_data: Dict) -> Dict
    def calculate_scenario_impact(self, scenario: Dict, qbo_data: Dict) -> Dict
    def calculate_historical_runway(self, qbo_data: Dict) -> List[Dict]

# runway/core/bill_impact_calculator.py - Bill-specific calculations  
class BillImpactCalculator:
    def calculate_bill_runway_impact(self, bill_data: Dict) -> Dict
    def calculate_payment_impact(self, payment_data: Dict) -> Dict

# runway/core/tray_impact_calculator.py - Tray-specific calculations
class TrayImpactCalculator:
    def calculate_tray_item_runway_impact(self, item_data: Dict) -> Dict
    def calculate_hygiene_impact(self, hygiene_data: Dict) -> Dict
```

### **5. Balance Service Relocation**

**Decision**: Move `domains/core/services/balance_service.py` to `domains/bank/services/balance_service.py`

**Rationale**:
- Balances are bank account data, not core business data
- Aligns with domain organization principles
- Reduces confusion about service location

## **Implementation Plan**

### **Phase 1: Priority Logic Consolidation**
1. Create `runway/core/priority_calculation_service.py`
2. Move all priority logic from domain services to this service
3. Update all services to use centralized priority logic
4. Remove duplicate priority methods from domain services

### **Phase 2: Domain Service Consolidation**
1. Merge `ap_ingestion.py` into `bill_ingestion.py`
2. Merge `PaymentApplicationService` into `PaymentMatchingService`
3. Move `ARPlanService` to `runway/core/`
4. Update all imports and references

### **Phase 3: QBO Data Mapping**
1. Create `runway/core/data_mappers/` directory
2. Implement `QBOMapper` for consistent field mapping
3. Update data orchestrators to use mappers
4. Ensure consistent naming across runway services

### **Phase 4: RunwayCalculator Refactoring**
1. Split RunwayCalculator into focused services
2. Move entity-specific calculations to appropriate calculators
3. Keep only pure runway calculations in RunwayCalculationService
4. Update all references to use new service structure

### **Phase 5: Balance Service Relocation**
1. Move balance service to `domains/bank/`
2. Update all imports and references
3. Ensure proper domain organization

## **Success Criteria**

- [ ] Single source of truth for all priority calculations
- [ ] Clear domain service boundaries with no duplication
- [ ] Consistent QBO data mapping across runway services
- [ ] RunwayCalculator split into focused services
- [ ] Proper ADR-001 and ADR-006 compliance
- [ ] All experiences using runway/core services correctly

## **Files to Update**

### **New Files**:
- `runway/core/priority_calculation_service.py`
- `runway/core/data_mappers/qbo_mapper.py`
- `runway/core/bill_impact_calculator.py`
- `runway/core/tray_impact_calculator.py`

### **Files to Modify**:
- `domains/ap/services/bill_ingestion.py` - Remove priority logic
- `domains/ar/services/customer.py` - Remove priority logic
- `runway/core/runway_calculator.py` - Split into focused services
- `runway/core/payment_priority_calculator.py` - Remove, use centralized service
- `runway/core/tray_priority_calculator.py` - Remove, use centralized service

### **Files to Remove**:
- `domains/ap/services/ap_ingestion.py` - Merge into bill_ingestion.py
- `domains/ar/services/payment_application.py` - Merge into payment_matching.py
- `domains/ar/services/ar_plan.py` - Move to runway/core/

## **Dependencies**

- Must be completed before Task 1 can be considered truly executable
- Requires understanding of all business rules and service responsibilities
- May require updates to existing tests and API endpoints

## **Status: 🔄 PARTIALLY COMPLETED - READY FOR NEXT THREAD**

### **✅ COMPLETED (Phase 2 - Domain Service Consolidation)**
1. **AP Services Consolidated**: 
   - ✅ Deleted `domains/ap/services/ap_ingestion.py`
   - ✅ Updated `domains/ap/routes/ingest.py` to use `BillService` directly
   - ✅ Updated `domains/ap/services/__init__.py` to remove `IngestionService`

2. **AR Services Consolidated**:
   - ✅ Merged `PaymentApplicationService` into `PaymentMatchingService`
   - ✅ Deleted `domains/ar/services/payment_application.py`
   - ✅ Updated `domains/ar/services/__init__.py` and `domains/ar/routes/payments.py`
   - ✅ Moved `ARPlanService` to `runway/core/ar_plan_service.py`
   - ✅ Deleted `domains/ar/services/ar_plan.py`

3. **Balance Service Relocated**:
   - ✅ Moved `domains/core/services/balance_service.py` to `domains/bank/services/balance_service.py`
   - ✅ Deleted original file and updated references

4. **Import Errors Fixed**:
   - ✅ Fixed `ModuleNotFoundError` for deleted `PaymentApplicationService`
   - ✅ Server now starts successfully

5. **Data Orchestrator Pattern Implemented**:
   - ✅ Created `runway/core/data_orchestrators/` directory
   - ✅ Implemented `HygieneTrayDataOrchestrator` and `DecisionConsoleDataOrchestrator`
   - ✅ Updated Tray and Console experiences to use orchestrators
   - ✅ Refactored `RunwayCalculator` to pure calculation service

### **🔄 REMAINING WORK (Next Thread)**
1. **Priority Logic Consolidation** - **NEEDS SOLUTIONING** - Requires analysis and design
2. **QBO Data Mapping Strategy** - **NEEDS SOLUTIONING** - Requires analysis and design
3. **RunwayCalculator Refactoring** - **NEEDS SOLUTIONING** - Requires analysis and design (Task 1.2)

## **SOLUTIONING WORK REQUIRED**

### **Critical Issue Identified**
The previous analysis was premature and created executable tasks without proper solutioning work. The RunwayCalculator refactoring is the **foundation** that needs to be designed first, as it will determine how priority scoring and other calculations should be organized.

### **Next Steps for Next Thread**

1. **Start with Task 1.2** - Design RunwayCalculator Service Architecture (foundation task)
2. **Complete Priority Logic Solutioning** - After understanding the service architecture
3. **Complete QBO Data Mapping Solutioning** - After understanding data flow patterns
4. **Create executable tasks** only after solutioning is complete
5. **Validate** that all experiences work correctly with new architecture

### **Key Insight**
RunwayCalculator refactoring is the architectural foundation that will determine:
- How priority scoring integrates with runway calculations
- How entity-specific calculations (bills, invoices, collections) should be organized
- What the proper service boundaries should be
- How different calculation types (scenario, historical, current) should work together

This must be designed first before any other consolidation work can be properly planned.

## **Thread Handoff Notes**

- **Server Status**: ✅ Working (import errors fixed)
- **Completed**: Domain service consolidation (AP, AR, Balance)
- **Next Priority**: Priority logic consolidation (solutioning phase)
- **Key Files**: All domain service consolidation complete, ready for priority logic design
