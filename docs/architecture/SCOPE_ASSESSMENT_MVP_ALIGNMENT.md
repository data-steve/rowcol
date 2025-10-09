# Scope Assessment: MVP Data Architecture Alignment

*Realistic assessment of changes needed to align codebase with data architecture for QBO-only MVP*

## **Executive Summary**

**Current State**: The codebase has **inconsistent data access patterns** that don't align with the defined data architecture. Services mix local database queries with direct API calls, creating the exact "missing middle layer" problem identified.

**Real Scope**: **3-4 weeks of focused work** to implement proper data patterns, fix service boundaries, and resolve data orchestrator filtering issues.

**Key Insight**: The architecture needs fundamental clarification on domains/ vs runway/ vs infra/ responsibilities, plus implementation of missing sync mechanisms and purpose-specific filtering.

**Critical Discovery**: Following S02/S04/S05 discovery process revealed that my initial assessment was wrong - DigestDataOrchestrator is duplicating data instead of aggregating, and data orchestrators lack purpose-specific filtering.

## **Detailed Scope Analysis**

### **✅ What's Already Correct (60% of Codebase)**

#### **1. Calculators (Perfect)**
- **Status**: ✅ **FULLY ALIGNED**
- **Examples**: `RunwayCalculator`, `PriorityCalculator`
- **Pattern**: Pure calculation logic, receive data as parameters
- **Effort**: **0 hours** - No changes needed

#### **2. SmartSyncService (Perfect)**
- **Status**: ✅ **FULLY ALIGNED**
- **Examples**: Rate limiting, retry logic, caching
- **Pattern**: Infrastructure orchestration layer
- **Effort**: **0 hours** - No changes needed

#### **3. Runway Services (Mostly Correct)**
- **Status**: ✅ **MOSTLY ALIGNED**
- **Examples**: `TrayService`, `DigestService`, `DecisionConsoleService`
- **Pattern**: Use data orchestrators for data access
- **Effort**: **5 hours** - Minor fixes needed

### **⚠️ What Needs Major Fixes (25% of Codebase)**

#### **1. Data Orchestrator Filtering Issues (S02)**
- **Files**: `DecisionConsoleDataOrchestrator`, `HygieneTrayDataOrchestrator`, `DigestDataOrchestrator`
- **Issue**: All orchestrators pull same raw data without purpose-specific filtering
- **Fix**: Implement purpose-specific filtering (hygiene issues vs decision-ready)
- **Effort**: **15 hours** - Major refactoring

#### **2. DigestDataOrchestrator Duplication (S02)**
- **Files**: `runway/services/data_orchestrators/digest_data_orchestrator.py`
- **Issue**: Duplicates raw data fetching instead of aggregating from other orchestrators
- **Fix**: Make it aggregate from HygieneTray + DecisionConsole
- **Effort**: **8 hours** - Architectural refactoring

#### **3. Missing Entity Coverage (S02)**
- **Files**: All data orchestrators
- **Issue**: Missing customers, vendors, accounts, balances for calculators
- **Fix**: Add full entity coverage to all orchestrators
- **Effort**: **10 hours** - Add missing data sources

#### **4. Missing Purpose-Specific Methods (S02)**
- **Files**: Domain services
- **Issue**: No `get_bills_with_issues()`, `get_bills_ready_for_decision()` methods
- **Fix**: Add purpose-specific filtering methods to domain services
- **Effort**: **12 hours** - Add domain service methods

### **🚨 What Needs Implementation (15% of Codebase)**

#### **1. Data Architecture Clarification (S04)**
- **Missing**: Clear domains/ vs runway/ vs infra/ responsibilities
- **Missing**: When to use local DB vs API calls
- **Missing**: Sync strategy for mirrored data
- **Effort**: **20 hours** - Architectural clarification

#### **2. Sync Orchestration (New Implementation)**
- **Missing**: Scheduled sync jobs for mirrored data
- **Missing**: Webhook triggers for real-time updates
- **Missing**: Sync status tracking
- **Effort**: **20 hours** - New infrastructure

#### **3. Data Mirroring Strategy (New Implementation)**
- **Missing**: Clear sync patterns for bills, invoices, balances
- **Missing**: Sync coordination between data types
- **Missing**: Data freshness validation
- **Effort**: **15 hours** - New patterns

## **Realistic Effort Estimates**

### **Phase 1: Critical Fixes (1 week, 30 hours)**

#### **Week 1: Fix Service Boundaries and Add Sync**
- **Day 1-2**: Fix service boundary violations (4 hours)
  - Move `InvoiceService.sync_invoices()` to data orchestrator
  - Update domain services to use orchestrators
  - Remove direct SmartSyncService dependencies

- **Day 3-4**: Implement sync orchestration (20 hours)
  - Create scheduled sync jobs
  - Add webhook handlers for real-time updates
  - Implement sync status tracking

- **Day 5**: Add missing sync methods (6 hours)
  - Add balance sync to data orchestrator
  - Implement sync coordination
  - Add error handling

### **Phase 2: Data Mirroring (1 week, 15 hours)**

#### **Week 2: Implement Data Mirroring Strategy**
- **Day 1-2**: Implement sync patterns (10 hours)
  - Add local mirroring for bills and invoices
  - Implement sync coordination
  - Add data freshness validation

- **Day 3**: Add monitoring and alerting (5 hours)
  - Sync status monitoring
  - Data quality alerts
  - Performance metrics

### **Phase 3: Testing and Validation (3-5 days, 10 hours)**

#### **Week 3: Validate and Test**
- **Day 1-2**: Integration testing (5 hours)
  - Test sync mechanisms
  - Validate data freshness
  - Performance testing

- **Day 3**: Documentation and cleanup (5 hours)
  - Update architecture docs
  - Create troubleshooting guides
  - Code cleanup

## **Total Effort: 95 hours (3-4 weeks)**

### **Breakdown by Priority**

#### **Critical (Must Have for MVP)**
- **Service Boundary Fixes**: 4 hours
- **Sync Orchestration**: 20 hours
- **Missing Sync Methods**: 6 hours
- **Total Critical**: 30 hours (1 week)

#### **Important (Should Have for MVP)**
- **Data Mirroring Strategy**: 15 hours
- **Monitoring and Alerting**: 5 hours
- **Total Important**: 20 hours (1 week)

#### **Nice to Have (Can Defer)**
- **Performance Optimization**: 5 hours
- **Advanced Monitoring**: 5 hours
- **Total Nice to Have**: 10 hours (can defer)

## **Risk Assessment**

### **Low Risk (High Confidence)**
- **Service Boundary Fixes**: Simple refactoring, well-understood patterns
- **Sync Orchestration**: Standard infrastructure patterns
- **Missing Sync Methods**: Additive changes, no breaking changes

### **Medium Risk (Medium Confidence)**
- **Data Mirroring Strategy**: New patterns, need careful testing
- **Sync Coordination**: Complex interactions between data types

### **Mitigation Strategies**
- **Start with Critical Fixes**: Get MVP working first
- **Incremental Implementation**: Add one sync pattern at a time
- **Comprehensive Testing**: Test each pattern thoroughly
- **Rollback Plan**: Keep old patterns until new ones are validated

## **MVP Readiness Assessment**

### **Current MVP Readiness: 60%**

#### **What Works Now**
- ✅ Data orchestrators query QBO correctly
- ✅ Runway services use orchestrators correctly
- ✅ Calculators work with provided data
- ✅ SmartSyncService handles API orchestration

#### **What's Missing for MVP**
- ❌ No sync mechanism for local data
- ❌ Service boundary violations
- ❌ No data mirroring strategy
- ❌ No sync status monitoring

### **After Phase 1: 85% MVP Ready**
- ✅ Service boundaries fixed
- ✅ Sync orchestration implemented
- ✅ Missing sync methods added
- ⚠️ Data mirroring strategy partially implemented

### **After Phase 2: 95% MVP Ready**
- ✅ All data patterns implemented
- ✅ Sync monitoring in place
- ✅ Data freshness validated
- ✅ Performance optimized

## **Implementation Strategy**

### **Approach: Incremental Implementation**
1. **Fix Critical Issues First**: Get basic functionality working
2. **Add Sync Mechanisms**: Implement data mirroring
3. **Add Monitoring**: Ensure reliability
4. **Optimize Performance**: Fine-tune for production

### **Success Criteria**
- **MVP Functionality**: All MVP features work with QBO data
- **Data Freshness**: 95% of data within 15 minutes of source
- **Performance**: <3 second dashboard load times
- **Reliability**: 99.9% successful sync operations

## **Resource Requirements**

### **Development Team**
- **Principal Architect**: 20 hours (architecture and design)
- **Senior Developer**: 25 hours (implementation)
- **Junior Developer**: 10 hours (testing and documentation)

### **Timeline**
- **Week 1**: Critical fixes (30 hours)
- **Week 2**: Data mirroring (20 hours)
- **Week 3**: Testing and validation (10 hours)
- **Total**: 3 weeks, 60 hours

## **Dependencies**

### **External Dependencies**
- **QBO API Access**: Required for testing
- **Database Access**: Required for sync implementation
- **Monitoring Tools**: Required for sync status tracking

### **Internal Dependencies**
- **SmartSyncService**: Already implemented
- **Data Orchestrators**: Already implemented
- **Runway Services**: Already implemented

## **Next Steps**

### **Immediate Actions (This Week)**
1. **Review and Approve**: Stakeholder review of this assessment
2. **Create Implementation Tasks**: Break down into executable tasks
3. **Set Up Development Environment**: Ensure QBO API access
4. **Begin Phase 1**: Start with service boundary fixes

### **Week 1 Goals**
- Fix all service boundary violations
- Implement basic sync orchestration
- Add missing sync methods
- Validate MVP functionality

### **Week 2 Goals**
- Implement data mirroring strategy
- Add sync monitoring and alerting
- Performance testing and optimization
- Documentation updates

### **Week 3 Goals**
- Comprehensive testing
- Production readiness validation
- Documentation completion
- Handoff to development team

## **Conclusion**

**The scope is manageable**: 55 hours over 2-3 weeks to align the codebase with the data architecture.

**Most code is correct**: 80% of the codebase already follows the right patterns.

**Focus on missing pieces**: Implement sync mechanisms and fix service boundaries.

**MVP is achievable**: With focused effort, the QBO-only MVP can be delivered in 2-3 weeks.

---

*This assessment provides a realistic roadmap for aligning the codebase with the data architecture patterns needed for the QBO-only MVP.*
