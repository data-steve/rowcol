# S12: Multi-Rail Domain Organization

## **Task: Design Multi-Rail Domain Organization Architecture**
- **Status:** `[❌]` Superseded by S13
- **Priority:** P0 Critical
- **Justification:** Current domain services assume QBO can do everything (execution + ledger), but QBO is only a ledger rail. We need to design how domains, infra, and runway services will be organized across QBO, Ramp, Plaid, and Stripe rails, including the _parked/ pattern for QBO-incompatible features.
- **Execution Status:** **SUPERSEDED BY S13_UNIFIED_MULTI_RAIL_ARCHITECTURE**

## **Problem Statement**

**Current State**: We have domain services in `domains/{ap,ar,bank}/` that assume QBO can do everything (execution + ledger), but QBO is only a ledger rail.

**The Problem**: We need to design multi-rail domain organization:
- **Humble QBO Services**: Keep only what QBO actually supports (ledger rail)
- **Move Execution to _parked/**: QBO-incompatible features for future Ramp/Stripe
- **Design Multi-Rail Structure**: Clear separation across QBO, Ramp, Plaid, Stripe
- **Plan Migration Path**: From QBO-only to multi-rail architecture

**Why This Matters**:
- **QBO Strategy Compliance**: QBO is read-only ledger, not execution rail
- **Multi-Rail Architecture**: System must support multiple rails
- **Feature Preservation**: Advanced features aren't lost, just parked
- **Clear Boundaries**: Easy to see what's QBO-compatible vs advanced

## **Rail Responsibilities & Capabilities**

### **QBO (Ledger Rail) - What It Actually Does**
**Capabilities**:
- ✅ Read-only sync (bills, invoices, vendors, customers, accounts)
- ✅ Basic CRUD on mirrored data
- ✅ Audit trail and compliance tracking
- ✅ Historical data and reporting

**Limitations**:
- ❌ No bill payment execution
- ❌ No invoice creation/sending
- ❌ No bank account management
- ❌ No payment processing

### **Ramp (A/P Execution Rail) - Future Implementation**
**Capabilities**:
- ✅ Bill payment execution
- ✅ Vendor management and onboarding
- ✅ Payment method management
- ✅ A/P workflow automation

### **Plaid (Verification Rail) - Future Implementation**  
**Capabilities**:
- ✅ Bank account verification
- ✅ Real-time balance checking
- ✅ Transaction matching and reconciliation
- ✅ ACH payment processing

### **Stripe (A/R Execution Rail) - Future Implementation**
**Capabilities**:
- ✅ Invoice creation and sending
- ✅ Payment collection and processing
- ✅ Customer management
- ✅ A/R workflow automation

## **Multi-Rail Domain Architecture**

### **Phase 1: QBO-Only MVP (Current)**
```
domains/
├── qbo/                    # QBO-specific business logic
│   └── services/
│       └── sync_service.py # QBOSyncService
├── ap/                     # A/P domain (QBO-honest)
│   └── services/
│       └── bill_service.py # Basic CRUD, no execution
├── ar/                     # A/R domain (QBO-honest)
│   └── services/
│       └── invoice_service.py # Basic CRUD, no execution
└── bank/                   # Bank domain (QBO-honest)
    └── services/
        └── balance_service.py # Basic CRUD, no execution

_parked/                    # QBO-incompatible features
├── domains/
│   ├── ap/
│   │   └── services/
│   │       └── bill_execution.py # Payment execution (Ramp)
│   ├── ar/
│   │   └── services/
│   │       └── invoice_execution.py # Invoice creation (Stripe)
│   └── bank/
│       └── services/
│           └── bank_management.py # Bank account management (Plaid)
└── runway/
    └── services/
        └── policy/         # Policy engine (moved from domains/)
```

### **Phase 2: Multi-Rail Architecture (Future)**
```
domains/
├── qbo/                    # QBO ledger rail
│   └── services/
│       └── sync_service.py
├── ramp/                   # Ramp A/P execution rail
│   └── services/
│       └── payment_service.py
├── plaid/                  # Plaid verification rail
│   └── services/
│       └── verification_service.py
├── stripe/                 # Stripe A/R execution rail
│   └── services/
│       └── invoice_service.py
├── ap/                     # A/P domain (rail-agnostic)
│   └── services/
│       └── bill_service.py # Orchestrates across rails
├── ar/                     # A/R domain (rail-agnostic)
│   └── services/
│       └── invoice_service.py # Orchestrates across rails
└── bank/                   # Bank domain (rail-agnostic)
    └── services/
        └── balance_service.py # Orchestrates across rails
```

## **Implementation Strategy**

### **Step 1: Humble QBO Services (Phase 1)**
- **Remove execution methods** from domain services
- **Keep only QBO-compatible features** (CRUD, sync, reporting)
- **Move advanced features** to `_parked/` directory
- **Update service boundaries** to be QBO-honest

### **Step 2: Create _parked/ Structure**
- **Copy advanced versions** to `_parked/domains/`
- **Move policy engine** to `_parked/runway/services/`
- **Document limitations** and future rail compatibility
- **Preserve all functionality** for future implementation

### **Step 3: Design Multi-Rail Integration**
- **Rail-specific services** in `domains/{qbo,ramp,plaid,stripe}/`
- **Domain services** orchestrate across rails
- **Clear separation** between ledger, execution, verification rails
- **Unified interfaces** for multi-rail operations

## **Key Design Decisions**

### **1. _parked/ Pattern**
- **Centralized parking** for QBO-incompatible features
- **Preserved functionality** for future rail implementation
- **Clear documentation** of limitations and future plans
- **Easy migration** to appropriate rail-specific services

### **2. Rail-Specific Services**
- **QBO**: Ledger operations and sync
- **Ramp**: A/P execution and payment processing
- **Plaid**: Bank verification and reconciliation
- **Stripe**: A/R execution and invoice processing

### **3. Domain Service Orchestration**
- **Rail-agnostic interfaces** for business logic
- **Rail-specific delegation** for execution operations
- **Unified data models** across all rails
- **Consistent transaction logging** across rails

## **Migration Path**

### **Phase 1: QBO-Only MVP**
1. **Humble existing services** - Remove QBO-incompatible features
2. **Create _parked/ structure** - Move advanced features
3. **Update service boundaries** - Clear QBO vs execution separation
4. **Document limitations** - What QBO can/can't do

### **Phase 2: Add Ramp (A/P Execution)**
1. **Create RampSyncService** - Ramp-specific sync operations
2. **Move A/P execution** from _parked/ to domains/ramp/
3. **Update A/P domain services** - Orchestrate QBO + Ramp
4. **Implement payment workflows** - Ramp execution + QBO ledger

### **Phase 3: Add Plaid (Verification)**
1. **Create PlaidSyncService** - Plaid-specific sync operations
2. **Move bank verification** from _parked/ to domains/plaid/
3. **Update bank domain services** - Orchestrate QBO + Plaid
4. **Implement reconciliation** - Plaid verification + QBO ledger

### **Phase 4: Add Stripe (A/R Execution)**
1. **Create StripeSyncService** - Stripe-specific sync operations
2. **Move A/R execution** from _parked/ to domains/stripe/
3. **Update A/R domain services** - Orchestrate QBO + Stripe
4. **Implement invoice workflows** - Stripe execution + QBO ledger

## **Implementation Tasks Needed**

### **E15: Humble QBO Services**
- **Task**: Remove QBO-incompatible features from domain services
- **Effort**: 1-2 days
- **Priority**: P0
- **Dependencies**: E11 (domain sync duplication fix)

### **E16: Create _parked/ Structure**
- **Task**: Move advanced features to _parked/ directory
- **Effort**: 1-2 days
- **Priority**: P0
- **Dependencies**: E15 (humble QBO services)

### **E17: Design Multi-Rail Integration**
- **Task**: Design rail-specific services and domain orchestration
- **Effort**: 2-3 days
- **Priority**: P1
- **Dependencies**: E15, E16 (humble services and _parked/ structure)

## **Verification Criteria**

### **QBO-Honest Services**
- ✅ Domain services only do what QBO supports
- ✅ No execution methods in QBO-only services
- ✅ Clear documentation of QBO limitations
- ✅ Advanced features preserved in _parked/

### **Multi-Rail Architecture**
- ✅ Rail-specific services in appropriate domains
- ✅ Domain services orchestrate across rails
- ✅ Clear separation between ledger, execution, verification
- ✅ Unified interfaces for multi-rail operations

### **Migration Path**
- ✅ Clear progression from QBO-only to multi-rail
- ✅ Preserved functionality for future implementation
- ✅ Easy migration of _parked/ features to appropriate rails
- ✅ Consistent patterns across all rails

## **Dependencies**

### **Blocked By**
- **E11**: Domain sync duplication fix (in progress)
- **S11**: Domain sync integration architecture (in progress)

### **Blocks**
- **E15**: Humble QBO services (needs this solution)
- **E16**: Create _parked/ structure (needs this solution)
- **Future multi-rail implementation** (needs clear organization)

## **Next Steps**

1. **Complete E11**: Finish domain sync duplication fix
2. **Complete S11**: Finish domain sync integration architecture
3. **Design Multi-Rail Organization**: Create detailed organization patterns
4. **Create Implementation Tasks**: E15, E16, E17

---

*This solutioning task defines the multi-rail domain organization architecture, including the _parked/ pattern for QBO-incompatible features and the migration path to multi-rail support.*
