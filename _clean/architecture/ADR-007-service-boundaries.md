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
- **Purpose**: CRUD primitives, rail-agnostic business logic, domain gateway interfaces
- **Dependencies**: Can depend on other domain services, domain gateway interfaces
- **Cannot depend on**: Runway/ services, infra/ implementations, product-specific logic
- **Examples**: `BillService`, `InvoiceService`, `PaymentService`, `BillsGateway` (interface)

#### **Infra/ Services**
- **Purpose**: Rail-specific implementations, sync orchestration, external API clients
- **Dependencies**: Can depend on domain gateway interfaces, external APIs
- **Cannot depend on**: Runway/ services, domain/ services (except interfaces)
- **Examples**: `QBOBillsGateway`, `SyncOrchestrator`, `QBOClient`, `TransactionLogService`

#### **Runway/ Services**
- **Purpose**: Product decisions, orchestration, runway calculations
- **Dependencies**: Can depend on domain gateway interfaces, infra gateway implementations
- **Cannot depend on**: Experience services (circular dependency)
- **Examples**: `TrayService`, `ConsoleService`, `RunwayCalculationService`

#### **Experience Services** (Deprecated)
- **Purpose**: User-facing experiences, data presentation
- **Status**: Being replaced by Runway/ services with domain gateway pattern
- **Migration**: Move orchestration logic to Runway/ services, use domain gateways
- **Examples**: `TrayService`, `ConsoleService` (now in Runway/)

### **Dependency Flow**
```
Runway Services → Domain Gateway Interfaces → Infra Gateway Implementations
```

**Key Pattern**: Domain gateways provide rail-agnostic interfaces; infra gateways implement them with rail-specific logic.

### **Anti-Patterns to Avoid**
1. **Domain services depending on runway services** (ADR-001 violation)
2. **Domain services depending on infra implementations** (use interfaces only)
3. **Circular dependencies** between any services
4. **Runway services depending on experience services**
5. **Data orchestrators** (replaced by domain gateway pattern)

## Examples

### **Correct Pattern**
```python
# Runway Service - orchestrates domain gateways
class TrayService:
    def __init__(self, bills_gateway: BillsGateway, invoices_gateway: InvoicesGateway):
        self.bills = bills_gateway
        self.invoices = invoices_gateway
    
    def approve_tray_item(self, item_id: str):
        # Uses domain gateway interfaces
        bill = self.bills.get(item_id)
        self.bills.schedule_payment(bill.id, bill.amount, bill.due_date)

# Domain Service - uses gateway interfaces
class BillService:
    def __init__(self, bills_gateway: BillsGateway):
        self.bills = bills_gateway
    
    def approve_payment(self, bill_id: str):
        # Uses gateway interface, no direct rail dependencies
        return self.bills.schedule_payment(bill_id, amount, due_date)

# Infra Gateway - implements domain interface
class QBOBillsGateway(BillsGateway):
    def __init__(self, qbo_client: QBOClient, sync: SyncOrchestrator):
        self.qbo = qbo_client
        self.sync = sync
    
    def schedule_payment(self, bill_id: str, amount: Decimal, due_date: date):
        # Rail-specific implementation
        return self.qbo.schedule_payment(bill_id, amount, due_date)
```

### **Incorrect Pattern (ADR-001 Violation)**
```python
# WRONG: Domain service depending on runway service
class BillService:
    def __init__(self, business_id: str):
        # This violates ADR-001
        self.runway_calculator = RunwayCalculationService(business_id)

# WRONG: Domain service depending on infra implementation
class BillService:
    def __init__(self, business_id: str):
        # This violates gateway pattern
        self.qbo_client = QBOClient(business_id)  # Should use BillsGateway interface

# WRONG: Data orchestrator pattern (deprecated)
class DataOrchestrator:
    def __init__(self):
        # This pattern is being replaced by domain gateways
        pass
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

## **Circular Dependencies Prevention**

### **Critical Dependency Rules**
**Circular dependencies** between services can cause import errors, testing problems, and architectural violations.

#### **Dependency Direction (Enforced)**
```
Infra Services → Domain Services → Runway Services → Experience Services
     ↑              ↑                ↑                  ↑
   (Base)        (CRUD)          (Logic)           (UI/UX)
```

#### **Forbidden Dependencies**
- **Runway → Domains**: ❌ Runway services cannot import from domains
- **Experience → Runway**: ❌ Experience services cannot import from runway (circular)
- **Cross-Domain**: ❌ Domain services cannot import from other domains

#### **Allowed Dependencies**
- **Domains → Infra**: ✅ Domain services can use infrastructure
- **Runway → Domains**: ✅ Runway services can use domain services
- **Experience → Both**: ✅ Experience services can use runway AND domain services

### **Import Pattern Enforcement**
```python
# ✅ CORRECT: Experience service using both runway and domain
from runway.services.calculators.runway_calculator import RunwayCalculator
from domains.ap.services.bill_service import BillService

class BillExperienceService:
    def __init__(self, db: Session, business_id: str):
        self.runway_calc = RunwayCalculator(db, business_id)
        self.bill_service = BillService(db, business_id)

# ❌ WRONG: Runway service importing from domains
from domains.ap.services.bill_service import BillService  # Circular dependency!

# ❌ WRONG: Cross-domain import
from domains.ar.services.invoice_service import InvoiceService  # Violates boundaries!
```

### **Testing Dependencies**
- **Unit Tests**: Mock all dependencies, test in isolation
- **Integration Tests**: Test service boundaries, not internal implementations
- **E2E Tests**: Test complete user workflows across all layers

## Related ADRs
- **ADR-001**: Domain separation principles (foundation)
- **ADR-005**: QBO API strategy (domain service patterns)
- **ADR-006**: Data orchestrator pattern (runway service patterns)

## Success Criteria
- **No ADR-001 violations** - domain services never depend on runway services
- **No circular dependencies** - clean dependency flow maintained
- **Clear service responsibilities** - each service has focused purpose
- **Maintainable architecture** - easy to understand and extend
