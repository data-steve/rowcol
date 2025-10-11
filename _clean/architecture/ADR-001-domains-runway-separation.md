# ADR-001: Domains vs Runway Architectural Separation

**Date**: 2025-09-17  
**Status**: Accepted  
**Decision**: Two-layer architecture with strict dependency rules for multi-product platform

## Context

Multi-product platform (Runway, RowCol) needs clear separation between business logic and product orchestration to prevent circular dependencies and enable code reuse.

## Decision

**Three-Layer Architecture** with strict dependency rules:

### **`domains/` - Core Business Primitives (Rail-Agnostic)**
**Pattern**: Domain-Driven Design + Gateway Pattern + Smart Sync Pattern
**Purpose**: Reusable, product-agnostic business logic with rail-agnostic interfaces

**Structure**:
```
domains/
├── core/           # User management, authentication, business profiles
├── ap/             # Accounts Payable (bills, vendors, payments)
├── ar/             # Accounts Receivable (invoices, collections)
├── bank/           # Bank accounts, transactions, reconciliation
└── qbo/            # QBO-specific implementations (infra gateway)
```

**Characteristics**: Single Responsibility, Rail-Agnostic, Product-Agnostic, Stateless, Testable

**Key Pattern**: Domain Gateways (interfaces) + Infra Gateways (implementations)

```python
# domains/ap/gateways.py (interface)
class BillsGateway(Protocol):
    def list(self, q: ListBillsQuery) -> List[Bill]: ...
    def schedule_payment(self, client_id: str, bill_id: str, amount: Decimal, pay_on: date) -> str: ...

# domains/ap/services/bill_payment.py
class BillPaymentService:
    def __init__(self, bills_gateway: BillsGateway):
        self.bills = bills_gateway
    
    def approve_payment(self, bill_id: str) -> PaymentApproval:
        """Core business logic for bill payment approval."""
        # Uses gateway interface - no direct rail dependencies
```

### **`infra/` - Infrastructure Implementations (Rail-Specific)**
**Pattern**: Gateway Implementation + Smart Sync Pattern + Transaction Logging
**Purpose**: Concrete implementations of domain gateways with rail-specific logic

**Structure**:
```
infra/
├── gateways/       # Infra gateway implementations (QBO, Ramp, Plaid, Stripe)
├── sync/           # Sync orchestrator, freshness checks, retry logic
├── db/             # Database session, transaction log, state mirror
└── rails/          # Rail-specific clients and mappers
    └── qbo/        # QBO client, auth, DTOs, mappers
```

**Key Pattern**: Smart Sync Pattern with Transaction Log + State Mirror

### **`runway/` - Product Orchestration (User-facing)**
**Pattern**: Orchestration Layer + Facade Pattern + State Management
**Purpose**: Runway-specific workflows that orchestrate multiple domain gateways

**Structure**:
```
runway/
├── routes/         # API endpoints (/runway/auth/, /runway/tray/, etc.)
├── services/       # Product-specific orchestration (TrayService, ConsoleService)
├── schemas/        # Runway-specific DTOs and API contracts
├── middleware/     # Authentication, CORS, logging, error handling
└── wiring/         # Composition root (dependency injection)
```

**Characteristics**: User-Centric, Orchestration, Product-Specific, Stateful, Integration

**Key Pattern**: Composition Root for dependency injection

```python
# runway/services/tray.py
class TrayService:
    def __init__(self, bills_gateway: BillsGateway, invoices_gateway: InvoicesGateway):
        self.bills = bills_gateway
        self.invoices = invoices_gateway
    
    def approve_tray_item(self, item_id: str) -> TrayActionResult:
        """Orchestrate multiple domain gateways for single user action."""
        # 1. Get bill via bills gateway (Smart Sync pattern)
        # 2. Schedule payment via bills gateway
        # 3. Update invoice via invoices gateway
        # 4. Return tray result (no direct rail dependencies)

# runway/wiring.py (composition root)
def create_tray_service(client_id: str) -> TrayService:
    bills_gateway = QBOBillsGateway(client_id)  # Infra implementation
    invoices_gateway = QBOInvoicesGateway(client_id)  # Infra implementation
    return TrayService(bills_gateway, invoices_gateway)
```

## Import Rules and Enforcement

### **Allowed Import Patterns**
✅ **Runway → Domains**: Runway can import domain gateway interfaces  
✅ **Runway → Infra**: Runway can import infra gateway implementations (via composition root)  
✅ **Domains → Domains**: Domains can import other domain interfaces (with care)  
✅ **Infra → Domains**: Infra can implement domain gateway interfaces  
✅ **All → Common**: All can import shared utilities

### **Forbidden Import Patterns**
❌ **Domains → Runway**: Domains cannot import runway-specific code  
❌ **Domains → Infra**: Domains cannot import infra implementations (use interfaces only)  
❌ **Circular Dependencies**: No circular imports between any modules

### **CI/CD Import Validation**
```bash
# Pre-commit hook to validate import rules
poetry run python scripts/validate_imports.py
```

**Validation Rules**: No imports from `runway/` within `domains/`, no circular dependencies, all imports resolve correctly

## Dependency Direction
`runway/ → domains/ → infra/` (no back edges, ever)

**Key Principle**: Domain gateways provide rail-agnostic interfaces; infra gateways implement them with rail-specific logic.

## Benefits
- **Clear Separation of Concerns**: Domain gateways (interfaces) vs Infra gateways (implementations) vs Runway services (orchestration)
- **Code Reusability**: Domain gateways work across Runway, RowCol, future products
- **Rail Agnostic**: Domain logic independent of specific rails (QBO, Ramp, Plaid, Stripe)
- **Scalable Development**: Junior devs (domains) vs Senior devs (orchestration)
- **Future-Proof Architecture**: Adding new rails requires only new infra gateway implementations

## Consequences
**Positive**: Maintainability, Testability, Reusability, Scalability  
**Negative**: Complexity, Overhead, Discipline required

**Risks & Mitigations**:
- **Architecture bypass**: Automated CI/CD validation + code review
- **Over-engineering**: Start simple, refactor when complexity justifies separation
- **Performance overhead**: Profile hot paths, consider caching strategies

## Implementation Guidelines

### **When to Create a New Domain**:
- Represents a distinct business area (AP, AR, Bank, etc.)
- Has clear QBO API boundaries
- Can be tested independently
- Will be reused across multiple products

### **When to Add to Runway**:
- User-facing workflow or API endpoint
- Orchestrates multiple domain services
- Contains product-specific business rules
- Manages user state or preferences

### **Code Organization Patterns**:

**Domain Structure**:
```
domains/ap/
├── models/         # SQLAlchemy models
├── services/       # Business logic services
├── schemas/        # Pydantic schemas for data validation
└── routes/         # Internal API routes (if needed)
```

**Runway Structure**:
```
runway/
├── routes/         # User-facing API endpoints
├── services/       # Orchestration services
├── schemas/        # API DTOs and contracts
└── middleware/     # Cross-cutting concerns
```

**Test Structure**:
```
tests/
├── domains/        # Domain-specific tests
├── runway/         # Integration and workflow tests
└── infra/          # Infrastructure tests
```

## Monitoring and Success Metrics

### **Architecture Health Metrics**:
- **Import Violations**: 0 forbidden imports in CI/CD
- **Circular Dependencies**: 0 detected circular imports
- **Test Coverage**: >90% for both domains and runway services
- **Code Reuse**: Domain services used by multiple products

### **Developer Experience Metrics**:
- **Onboarding Time**: New developers productive within 2 days
- **Feature Development**: Clear guidance on where to add new features
- **Bug Resolution**: Issues can be isolated to specific architectural layers

## Future Considerations

### **RowCol Integration**:
When we add RowCol (multi-tenant CAS firm product), the architecture will support it naturally:

```
rowcol/
├── routes/         # RowCol-specific API endpoints
├── services/       # Multi-tenant orchestration
├── schemas/        # RowCol DTOs
└── middleware/     # Tenant isolation, RBAC
```

**Domain services remain unchanged** - RowCol simply orchestrates them differently.

### **Microservices Evolution**:
If we eventually move to microservices, this architecture provides natural service boundaries:
- **Core Domain Service**: User management, business profiles
- **AP Domain Service**: Bills, vendors, payments
- **AR Domain Service**: Invoices, collections  
- **Runway Product Service**: User workflows and orchestration
- **RowCol Product Service**: Multi-tenant workflows

## References

- **Domain-Driven Design**: Evans, Eric. "Domain-Driven Design: Tackling Complexity in the Heart of Software"
- **Clean Architecture**: Martin, Robert. "Clean Architecture: A Craftsman's Guide to Software Structure and Design"
- **Oodaloo Build Plan v4.3**: `/dev_plans/Oodaloo_v4.3_Build_Plan.md`
- **Phase 0 Testing Strategy**: `/docs/PHASE0_TESTING_STRATEGY.md`

## Addendum: QBO Integration Architecture Fix (2025-09-17)

### Issue Identified
During Phase 1 development, a **critical ADR-001 violation** was discovered:
- Multiple services were making direct QBO API calls
- `DigestService` (runway/) was calling `QBOIntegrationService` directly (now fixed to use SmartSyncService)
- `SmartSyncService` (domains/) was duplicating QBO logic
- No unified coordination of QBO rate limiting and sync timing

### Solution Implemented
**Unified QBO Architecture** through `SmartSyncService`:

```
RUNWAY LAYER (Product Orchestration)
├── DigestService ──┐
├── JobRunner ──────┼──► SmartSyncService ──► domains/integrations/qbo/
├── BillService ────┘    (Single QBO Coordinator)
└── Other Services

DOMAINS LAYER (QBO Primitives)
├── SmartSyncService (QBO Coordinator)
└── domains/integrations/qbo/ (Actual QBO API)
```

**Key Changes:**
1. `SmartSyncService` became single point for all QBO coordination
2. `DigestService` now uses `smart_sync.get_qbo_data_for_digest()`
3. Removed direct QBO calls from runway/ services
4. Unified rate limiting and sync timing across all QBO interactions

**Result**: Full ADR-001 compliance with proper domains/runway separation.

---

**Last Updated**: 2025-09-17  
**Next Review**: Phase 1 completion (when we add AP orchestration workflows)
