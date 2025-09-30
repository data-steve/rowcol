# ADR-007: Service Boundaries and Dependencies

## Status
- **Date**: 2025-01-27
- **Status**: Accepted
- **Context**: Need clear service boundaries to prevent circular dependencies and maintain clean architecture

## Decision
Establish clear service boundaries with strict dependency rules to prevent architectural violations and maintain clean separation of concerns.

## Implementation

### **Service Boundary Rules**

#### **Domains/ Services**
- **Purpose**: CRUD primitives, QBO sync, basic business logic
- **Dependencies**: Can depend on other domain services, infra services, external APIs
- **Cannot depend on**: Runway/ services, experience services, product-specific logic
- **Examples**: `BillService`, `InvoiceService`, `PaymentService`, `SmartSyncService`

#### **Runway/ Services**
- **Purpose**: Product decisions, orchestration, runway calculations
- **Dependencies**: Can depend on domain services, infra services
- **Cannot depend on**: Experience services (circular dependency)
- **Examples**: `RunwayCalculationService`, `PriorityCalculationService`, `DataOrchestrator`

#### **Experience Services**
- **Purpose**: User-facing experiences, data presentation
- **Dependencies**: Can depend on runway/ services AND domain services directly
- **Pattern**: Use BOTH data orchestrators AND calculation services
- **Examples**: `TrayService`, `ConsoleService`, `DigestService`, `TestDriveService`

### **Dependency Flow**
```
Experience Services → Runway Services → Domain Services → Infra Services
```

### **Anti-Patterns to Avoid**
1. **Domain services depending on runway services** (ADR-001 violation)
2. **Circular dependencies** between any services
3. **Experience services depending on other experience services**
4. **Runway services depending on experience services**

## Examples

### **Correct Pattern**
```python
# Experience Service - can depend on both runway and domain
class TrayService:
    def __init__(self, db: Session, business_id: str):
        # Data orchestrator (runway service)
        self.data_orchestrator = HygieneTrayDataOrchestrator(db, business_id)
        
        # Calculation services (runway services)
        self.runway_calculator = RunwayCalculationService(db, business_id)
        self.priority_calculator = PriorityCalculationService(db, business_id)
        
        # Domain services (direct access)
        self.bill_service = BillService(business_id)
        self.invoice_service = InvoiceService(business_id)

# Runway Service - can depend on domain services
class RunwayCalculationService:
    def __init__(self, db: Session, business_id: str):
        # Domain services only
        self.bill_service = BillService(business_id)
        self.invoice_service = InvoiceService(business_id)

# Domain Service - cannot depend on runway services
class BillService:
    def __init__(self, business_id: str):
        # Infra services only
        self.smart_sync = SmartSyncService(business_id)
        self.qbo_client = QBOClient(business_id)
```

### **Incorrect Pattern (ADR-001 Violation)**
```python
# WRONG: Domain service depending on runway service
class BillService:
    def __init__(self, business_id: str):
        # This violates ADR-001
        self.runway_calculator = RunwayCalculationService(business_id)
```

## Verification

### **Dependency Check Commands**
```bash
# Check for ADR-001 violations (domain services depending on runway)
grep -r "from runway\." domains/ --include="*.py"
grep -r "import.*runway" domains/ --include="*.py"

# Check for circular dependencies
grep -r "from.*experiences" runway/ --include="*.py"
grep -r "import.*experiences" runway/ --include="*.py"

# Check for experience service dependencies
grep -r "from.*experiences" runway/experiences/ --include="*.py"
```

### **Verification Steps**
1. **Run dependency checks** - no ADR-001 violations
2. **Check import statements** - no circular dependencies
3. **Verify service boundaries** - each service has clear responsibilities
4. **Test service instantiation** - no dependency injection issues

## Related ADRs
- **ADR-001**: Domain separation principles (foundation)
- **ADR-005**: QBO API strategy (domain service patterns)
- **ADR-006**: Data orchestrator pattern (runway service patterns)

## Success Criteria
- **No ADR-001 violations** - domain services never depend on runway services
- **No circular dependencies** - clean dependency flow maintained
- **Clear service responsibilities** - each service has focused purpose
- **Maintainable architecture** - easy to understand and extend
