# ADR-001: Domains vs Runway Architectural Separation

**Date**: 2025-09-17  
**Status**: Accepted  
**Deciders**: Steve Simpson, Claude (AI Assistant)  
**Technical Story**: Phase 0.2 Core API Foundation  

## Context

Oodaloo requires a clear architectural separation between core business logic and product-specific orchestration. As we build toward a multi-product platform (Runway for cash management, future RowCol for multi-tenant CAS firms), we need a sustainable code organization that:

1. **Prevents circular dependencies** between domain logic and product features
2. **Enables code reuse** across multiple products (Runway, RowCol, future products)
3. **Maintains clear boundaries** for QBO-facing primitives vs user-facing workflows
4. **Supports junior/mid-level developer maintainability**
5. **Allows independent testing** of business logic vs product orchestration

## Decision

We will organize the codebase into two primary architectural layers:

### **`domains/` - Core Business Primitives (QBO-facing)**

**Purpose**: Reusable, product-agnostic business logic that directly interfaces with QBO and other external systems.

**Structure**:
```
domains/
├── core/           # User management, authentication, business profiles
├── ap/             # Accounts Payable (bills, vendors, payments)
├── ar/             # Accounts Receivable (invoices, collections)
├── bank/           # Bank accounts, transactions, reconciliation
└── integrations/   # QBO, payment processors, email providers
```

**Characteristics**:
- **Single Responsibility**: Each domain handles one business area
- **QBO-Centric**: Models and services mirror QBO data structures
- **Product-Agnostic**: No knowledge of Runway, RowCol, or other products
- **Stateless**: Pure business logic with minimal side effects
- **Testable**: Can be tested independently with mock data

**Example**:
```python
# domains/ap/services/bill_payment.py
class BillPaymentService:
    def approve_payment(self, bill_id: str) -> PaymentApproval:
        """Core business logic for bill payment approval."""
        # Pure business logic - no product-specific orchestration
```

### **`runway/` - Product Orchestration (User-facing)**

**Purpose**: Runway-specific workflows that orchestrate multiple domain services to deliver user value.

**Structure**:
```
runway/
├── routes/         # API endpoints (/runway/auth/, /runway/tray/, etc.)
├── services/       # Product-specific orchestration (DigestService, OnboardingService)
├── schemas/        # Runway-specific DTOs and API contracts
├── middleware/     # Authentication, CORS, logging, error handling
└── tray/           # Prep Tray feature (models, services, providers)
```

**Characteristics**:
- **User-Centric**: Designed around user workflows and value delivery
- **Orchestration**: Combines multiple domain services for complex workflows
- **Product-Specific**: Contains Runway business rules and UI logic
- **Stateful**: Manages user sessions, preferences, and workflow state
- **Integration**: Handles external APIs (email, notifications, analytics)

**Example**:
```python
# runway/services/tray.py
class TrayService:
    def __init__(self, ap_service: BillPaymentService, ar_service: InvoiceService):
        self.ap_service = ap_service
        self.ar_service = ar_service
    
    def approve_tray_item(self, item_id: str) -> TrayActionResult:
        """Orchestrate multiple domain services for single user action."""
        # 1. Approve payment (AP domain)
        # 2. Update invoice status (AR domain) 
        # 3. Recalculate runway (Core domain)
        # 4. Send notifications (Integration domain)
        # 5. Update tray state (Runway product)
```

## Import Rules and Enforcement

### **Allowed Import Patterns**:

✅ **Runway → Domains**: Runway can import and orchestrate domain services
```python
# runway/services/digest.py
from domains.core.services.balance_calculation import BalanceService
from domains.ap.services.bill_ingestion import BillService
```

✅ **Domain → Domain**: Domains can import other domains (with care)
```python
# domains/ap/services/vendor_payment.py  
from domains.bank.services.account_validation import AccountService
```

✅ **Both → Common**: Both can import shared utilities
```python
from common.exceptions import ValidationError
from config.business_rules import PaymentSettings
```

### **Forbidden Import Patterns**:

❌ **Domains → Runway**: Domains cannot import runway-specific code
```python
# domains/ap/services/bill_payment.py
from runway.services.digest import DigestService  # FORBIDDEN
```

❌ **Circular Dependencies**: No circular imports between any modules
```python
# domains/ap → domains/ar → domains/ap  # FORBIDDEN
```

### **CI/CD Import Validation**

We will implement automated import checks:

```bash
# Pre-commit hook to validate import rules
poetry run python scripts/validate_imports.py
```

**Validation Rules**:
1. No imports from `runway/` within `domains/`
2. No circular dependencies detected
3. All imports resolve correctly
4. External dependencies properly declared

## Benefits

### **1. Clear Separation of Concerns**
- **Domain services** focus on business logic correctness
- **Runway services** focus on user experience and workflow orchestration
- **Testing** can target each layer independently

### **2. Code Reusability**
- Domain services can be reused across Runway, RowCol, and future products
- Business logic changes propagate automatically to all products
- Shared domain models ensure data consistency

### **3. Scalable Development**
- **Junior developers** can work on domain services with clear boundaries
- **Senior developers** can focus on complex orchestration in runway services
- **Teams** can work independently on different domains

### **4. Future-Proof Architecture**
- Adding RowCol requires only new orchestration layer
- Domain services remain unchanged
- QBO integration points are centralized and reusable

## Consequences

### **Positive**:
- ✅ **Maintainability**: Clear boundaries reduce cognitive load
- ✅ **Testability**: Each layer can be tested in isolation  
- ✅ **Reusability**: Domain logic works across all products
- ✅ **Scalability**: Architecture supports multiple products and teams

### **Negative**:
- ⚠️ **Complexity**: More files and structure to understand initially
- ⚠️ **Overhead**: Some business logic requires coordination across services
- ⚠️ **Discipline**: Requires consistent adherence to import rules

### **Risks and Mitigations**:

**Risk**: Developers bypass architecture and create shortcuts  
**Mitigation**: Automated CI/CD import validation + code review guidelines

**Risk**: Over-engineering simple features  
**Mitigation**: Start with simple implementations, refactor when complexity justifies separation

**Risk**: Performance overhead from service orchestration  
**Mitigation**: Profile and optimize hot paths, consider caching strategies

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
├── routes/         # Internal API routes (if needed)
└── tests/          # Domain-specific tests
```

**Runway Structure**:
```
runway/
├── routes/         # User-facing API endpoints
├── services/       # Orchestration services
├── schemas/        # API DTOs and contracts
├── middleware/     # Cross-cutting concerns
└── tests/          # Integration and workflow tests
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
