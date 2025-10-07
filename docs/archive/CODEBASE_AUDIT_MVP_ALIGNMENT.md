# Codebase Audit: MVP Alignment Strategy

## **🎯 Objective**
Audit existing codebase to understand what's built, what works, and how to align it with QBO-only MVP strategy using feature gating.

## **📋 Audit Checklist**

### **Phase 1: Core Services Audit**
- [ ] **Digest Service** (`runway/services/2_experiences/digest.py`)
  - What exists: Email digest functionality
  - What works: QBO data integration
  - What needs gating: Multi-rail features
  - MVP readiness: ✅ Ready for QBO-only

- [ ] **Hygiene Tray Service** (`runway/services/2_experiences/tray.py`)
  - What exists: Bill quality issues, data hygiene
  - What works: QBO bill validation
  - What needs gating: Ramp bill hygiene
  - MVP readiness: ✅ Ready for QBO-only

- [ ] **Decision Console Service** (`runway/services/2_experiences/console.py`)
  - What exists: Bill approval workflow, decision making
  - What works: QBO bill approval logic
  - What needs gating: Ramp execution, multi-rail decisions
  - MVP readiness: ✅ Ready for QBO-only

- [ ] **Runway Calculator** (`runway/services/1_calculators/runway_calculator.py`)
  - What exists: Pure runway calculation logic
  - What works: Stateless, data-agnostic
  - What needs gating: Nothing (already QBO-agnostic)
  - MVP readiness: ✅ Ready for QBO-only

### **Phase 2: Data Orchestrators Audit**
- [ ] **Reserve Runway Service** (`runway/services/0_data_orchestrators/reserve_runway.py`)
  - What exists: Earmarking/reserve management
  - What works: QBO cash balance integration
  - What needs gating: Multi-rail reserve sources
  - MVP readiness: ✅ Ready for QBO-only

- [ ] **Scheduled Payment Service** (`runway/services/0_data_orchestrators/scheduled_payment_service.py`)
  - What exists: Payment scheduling with runway integration
  - What works: QBO scheduled payments
  - What needs gating: Ramp execution, multi-rail scheduling
  - MVP readiness: ✅ Ready for QBO-only

### **Phase 3: Domain Services Audit**
- [ ] **Payment Service** (`domains/ap/services/payment.py`)
  - What exists: Payment lifecycle, QBO sync
  - What works: QBO payment operations
  - What needs gating: Ramp execution, multi-rail payments
  - MVP readiness: ⚠️ Needs QBO execution audit

- [ ] **Vendor Normalization** (`domains/vendor_normalization/services.py`)
  - What exists: Vendor name canonicalization, COA mapping
  - What works: QBO vendor matching
  - What needs gating: Multi-rail vendor matching
  - MVP readiness: ✅ Ready for QBO-only

### **Phase 4: Infrastructure Audit**
- [ ] **Base API Client** (`infra/api/base_client.py`)
  - What exists: Common API patterns, rate limiting, retry logic
  - What works: QBO integration
  - What needs gating: Ramp, Plaid, Stripe integrations
  - MVP readiness: ✅ Ready for QBO-only

- [ ] **Job Storage** (`infra/jobs/job_storage.py`)
  - What exists: Unified job management, sync coordination
  - What works: QBO sync jobs
  - What needs gating: Multi-rail sync jobs
  - MVP readiness: ✅ Ready for QBO-only

- [ ] **Smart Sync** (`infra/qbo/smart_sync.py`)
  - What exists: QBO-specific sync orchestrator
  - What works: QBO sync with resilience
  - What needs gating: Multi-rail sync orchestration
  - MVP readiness: ✅ Ready for QBO-only

### **Phase 5: Configuration Audit**
- [ ] **Core Thresholds** (`infra/config/core_thresholds.py`)
  - What exists: Mixed product and API settings
  - What works: QBO thresholds
  - What needs gating: Rail-specific configurations
  - MVP readiness: ⚠️ Needs separation

- [ ] **QBO Config** (`infra/qbo/config.py`)
  - What exists: QBO-specific configuration
  - What works: QBO OAuth, URLs, webhooks
  - What needs gating: Nothing (already QBO-specific)
  - MVP readiness: ✅ Ready for QBO-only

## **🔍 Detailed Findings**

### **✅ High-Reuse Components (Ready for MVP)**
1. **Runway Calculator** (`runway/services/1_calculators/runway_calculator.py`)
   - **Status**: Pure calculation logic, stateless, data-agnostic
   - **MVP Ready**: ✅ No changes needed
   - **Key Features**: Current runway, scenario impact, historical analysis, weekly analysis
   - **Integration**: Already designed to receive data as parameters

2. **Base API Client** (`infra/api/base_client.py`)
   - **Status**: Comprehensive foundation for all API integrations
   - **MVP Ready**: ✅ Solid foundation for QBO-only MVP
   - **Key Features**: Rate limiting, retry logic, error handling, caching, circuit breaker
   - **Platform Support**: QBO, Plaid, Stripe, Zapier (already defined)

3. **Vendor Normalization** (`domains/vendor_normalization/services.py`)
   - **Status**: Sophisticated vendor matching and COA mapping system
   - **MVP Ready**: ✅ QBO vendor matching works
   - **Key Features**: Vendor canonicalization, COA mapping, USASpending.gov integration
   - **Integration**: Ready for multi-rail extension

### **⚠️ Medium-Reuse Components (Need Gating)**
1. **Digest Service** (`runway/services/2_experiences/digest.py`)
   - **Status**: Email digest with runway calculations
   - **MVP Ready**: ⚠️ Needs gating for multi-rail features
   - **Key Features**: Runway calculation, email generation, batch processing
   - **Gating Needed**: Multi-rail data sources, client-facing vs advisor-facing

2. **Hygiene Tray** (`runway/services/2_experiences/tray.py`)
   - **Status**: Bill quality issues and data hygiene
   - **MVP Ready**: ⚠️ Needs gating for Ramp hygiene
   - **Key Features**: Priority scoring, impact calculation, action processing
   - **Gating Needed**: Ramp bill hygiene, multi-rail data sources

3. **Decision Console** (`runway/services/2_experiences/console.py`)
   - **Status**: Bill approval workflow and decision making
   - **MVP Ready**: ⚠️ Needs gating for Ramp execution
   - **Key Features**: Decision queue, impact analysis, decision finalization
   - **Gating Needed**: Ramp execution, multi-rail decision orchestration

4. **Reserve Runway** (`runway/services/0_data_orchestrators/reserve_runway.py`)
   - **Status**: Earmarking and reserve management
   - **MVP Ready**: ⚠️ Needs gating for multi-rail sources
   - **Key Features**: Reserve creation, funding, allocation, utilization
   - **Gating Needed**: Multi-rail reserve sources, Ramp integration

5. **Scheduled Payment** (`runway/services/0_data_orchestrators/scheduled_payment_service.py`)
   - **Status**: Payment scheduling with runway integration
   - **MVP Ready**: ⚠️ Needs gating for Ramp execution
   - **Key Features**: Reserve allocation, QBO scheduled payments, optimal timing
   - **Gating Needed**: Ramp execution, multi-rail scheduling

### **🚨 Needs Audit (QBO Execution Assumptions)**
1. **Payment Service** (`domains/ap/services/payment.py`)
   - **Status**: Comprehensive payment lifecycle management
   - **MVP Ready**: ⚠️ **CRITICAL** - Assumes QBO execution capabilities
   - **Key Features**: Payment execution, status tracking, reconciliation, QBO sync
   - **Issues**: Lines 104-133 assume QBO can execute payments (it can't!)
   - **Action Required**: Audit and remove QBO execution assumptions

2. **Core Thresholds** (`infra/config/core_thresholds.py`)
   - **Status**: Mixed product and API settings
   - **MVP Ready**: ⚠️ Needs separation
   - **Key Features**: Runway thresholds, tray priorities, QBO settings
   - **Issues**: QBO API settings mixed with product thresholds
   - **Action Required**: Extract QBO settings to rail-specific config

### **🔧 Infrastructure Components (Ready for Extension)**
1. **QBO Config** (`infra/qbo/config.py`)
   - **Status**: QBO-specific configuration
   - **MVP Ready**: ✅ Already QBO-specific
   - **Key Features**: OAuth URLs, API URLs, webhook endpoints
   - **Integration**: Ready for rail-specific configuration consolidation

2. **Job Storage** (`infra/jobs/job_storage.py`)
   - **Status**: Unified job management system
   - **MVP Ready**: ✅ Ready for multi-rail extension
   - **Key Features**: Sync coordination, deduplication, storage
   - **Integration**: Ready for multi-rail sync jobs

3. **Smart Sync** (`infra/qbo/smart_sync.py`)
   - **Status**: QBO-specific sync orchestrator
   - **MVP Ready**: ✅ QBO sync works
   - **Key Features**: Rate limiting, retry logic, caching, deduplication
   - **Integration**: Ready for multi-rail sync orchestration

## **🎯 MVP Alignment Strategy**

### **Phase 0.5: QBO-Only MVP (4-6 weeks)**
**Goal**: Use existing code with QBO-only gating

**Implementation**:
1. **Feature Gating**: Use existing `can_use_feature()` system
2. **Test Gating**: Gate multi-rail tests with feature flags
3. **Service Gating**: Gate multi-rail functionality in services
4. **UI Gating**: Show/hide multi-rail features in UI

**Code Changes**:
- Add feature flags for `ENABLE_RAMP_INTEGRATION`, `ENABLE_PLAID_INTEGRATION`, `ENABLE_STRIPE_INTEGRATION`
- Gate multi-rail functionality in existing services
- Create QBO-only golden dataset for testing
- Gate tests based on feature flags

### **Phase 1: Add Ramp (4-6 weeks)**
**Goal**: Extend existing code to include Ramp

**Implementation**:
1. **Enable Ramp**: Un-gate Ramp functionality
2. **Extend Services**: Add Ramp-specific logic to existing services
3. **Extend Tests**: Add Ramp integration tests
4. **Extend UI**: Show Ramp-specific features

## **📊 Effort Estimates**

### **Phase 0.5: QBO-Only MVP (4-6 weeks)**
- **Critical QBO Execution Audit**: 15h (audit and remove QBO execution assumptions)
- **Feature Gating Implementation**: 25h (add flags, gate services, gate tests)
- **Rail-Specific Config Separation**: 10h (extract QBO settings from core_thresholds.py)
- **QBO-Only Golden Dataset**: 20h (create realistic test data for all services)
- **UI Simplification**: 30h (combine digest + hygiene + console into dashboard)
- **Test Gating Strategy**: 15h (strategic test gating, not blanket silencing)
- **Total**: 115h (3-4 weeks)

### **Phase 1: Add Ramp (4-6 weeks)**
- **Ramp API Client**: 25h (build Ramp API client using BaseAPIClient)
- **Ramp Integration**: 30h (extend services to include Ramp functionality)
- **Ramp Golden Dataset**: 15h (add Ramp test data to existing dataset)
- **Ramp Tests**: 20h (integration and E2E tests for Ramp features)
- **Ramp UI**: 20h (show Ramp features in existing interfaces)
- **Total**: 110h (3-4 weeks)

### **Phase 2: Add Plaid + Stripe (4-6 weeks)**
- **Plaid Integration**: 30h (build Plaid API client, extend services)
- **Stripe Integration**: 25h (build Stripe API client, extend services)
- **Multi-Rail Golden Dataset**: 20h (comprehensive test data across all rails)
- **Multi-Rail Tests**: 25h (integration and E2E tests for all rails)
- **Multi-Rail UI**: 25h (show multi-rail features in interfaces)
- **Total**: 125h (3-4 weeks)

## **🚀 Next Steps**

1. **Start with Core Services Audit** - understand what exists
2. **Identify Gating Points** - where to add feature flags
3. **Create QBO-Only Golden Dataset** - realistic test data
4. **Implement Feature Gating** - gate multi-rail functionality
5. **Test MVP Functionality** - ensure QBO-only works
6. **Plan Ramp Integration** - prepare for Phase 1

## **💡 Key Insights**

### **🎯 What You Have Built (Solid Foundation)**
- **Runway Calculator**: Pure, stateless, data-agnostic - perfect for MVP
- **Base API Client**: Comprehensive foundation for all integrations - ready to extend
- **Vendor Normalization**: Sophisticated system - ready for multi-rail
- **Core Services**: Digest, Hygiene, Console - need gating but solid logic
- **Infrastructure**: Job storage, smart sync, QBO config - ready for extension

### **⚠️ Critical Issues to Address**
- **QBO Execution Assumptions**: Payment service assumes QBO can execute payments (it can't!)
- **Mixed Configurations**: QBO API settings buried in core_thresholds.py
- **Test Strategy**: Need principled gating, not blanket silencing

### **🚀 Strategic Approach**
- **Phase 0.5**: QBO-only MVP using existing code with gating (115h)
- **Phase 1**: Add Ramp by extending existing services (110h)
- **Phase 2**: Add Plaid + Stripe using same patterns (125h)
- **Total**: 350h (9-12 weeks) vs 540h (13-14 weeks) for full build

### **💪 Why This Works**
- **Preserves Investment**: 80% of existing code is reusable
- **Enables Learning**: QBO-only MVP lets you learn before expanding
- **Maintains Quality**: Principled gating vs random patching
- **Sets Up Success**: Each phase builds on the previous one

This approach gives you a working QBO-only MVP in 3-4 weeks while preserving your investment and setting up clean expansion to multi-rail.
