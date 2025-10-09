# Code Audit: Data Architecture Alignment

*Audit of existing codebase against Data Architecture Specification*

## **Executive Summary**

**Current State**: The codebase has **inconsistent data access patterns** that don't align with the defined data architecture. Services mix local database queries with direct API calls, creating the exact "missing middle layer" problem identified.

**Key Findings**:
- **Data Orchestrators**: Query APIs directly via SmartSyncService (correct pattern)
- **Domain Services**: Mix local DB queries with API calls (inconsistent pattern)
- **Runway Services**: Use data orchestrators correctly (good pattern)
- **Missing**: Clear data ownership boundaries and sync strategies

## **Detailed Findings**

### **✅ Correct Patterns (Align with Architecture)**

#### **1. Data Orchestrators (runway/services/data_orchestrators/)**
**Pattern**: Query APIs via SmartSyncService, no local storage
**Examples**:
- `DecisionConsoleDataOrchestrator`: Lines 52-56 query QBO via SmartSyncService
- `DigestDataOrchestrator`: Lines 171-173 query QBO via SmartSyncService

**Architecture Alignment**: ✅ **CORRECT** - Data orchestrators should query live APIs

#### **2. Runway Services (runway/services/experiences/)**
**Pattern**: Use data orchestrators for data access, no direct API calls
**Examples**:
- `TrayService`: Uses `HygieneTrayDataOrchestrator` for data
- `DigestService`: Uses `RunwayCalculator` with data from orchestrators
- `DecisionConsoleService`: Uses `DecisionConsoleDataOrchestrator`

**Architecture Alignment**: ✅ **CORRECT** - Runway services should use orchestrators

#### **3. Calculators (runway/services/calculators/)**
**Pattern**: Pure calculation logic, receive data as parameters
**Examples**:
- `RunwayCalculator`: Lines 34-46 receive data as parameters, no direct queries

**Architecture Alignment**: ✅ **CORRECT** - Calculators should be stateless

### **⚠️ Inconsistent Patterns (Need Alignment)**

#### **1. Domain Services (domains/*/services/)**
**Pattern**: Mix local database queries with API calls
**Examples**:

**BalanceService** (`domains/bank/services/balance_service.py`):
- Lines 33-35: Query local database for balances
- **Issue**: No sync mechanism to populate local data
- **Architecture Gap**: Missing data mirroring strategy

**InvoiceService** (`domains/ar/services/invoice.py`):
- Lines 136-177: Sync from QBO via SmartSyncService
- Lines 146-167: Store in local database
- **Issue**: Sync method exists but unclear when it's called
- **Architecture Gap**: Missing sync trigger strategy

**BusinessService** (`domains/core/services/business.py`):
- Lines 53-55: Query local database for business data
- **Issue**: Business data is RowCol-owned, not QBO-synced
- **Architecture Gap**: This is correct - business data should be local

#### **2. SmartSyncService Usage**
**Pattern**: Used directly by domain services instead of through orchestrators
**Examples**:
- `InvoiceService.sync_invoices()`: Direct SmartSyncService usage
- **Issue**: Domain services shouldn't call infrastructure directly
- **Architecture Gap**: Should go through data orchestrators

### **🚨 Critical Misalignments (Need Immediate Fix)**

#### **1. Missing Data Mirroring Strategy**
**Problem**: Domain services expect local data but no sync mechanism exists
**Examples**:
- `BalanceService.get_current_balances()`: Queries local DB but no sync method
- **Impact**: Local data will be empty or stale
- **Fix Required**: Implement sync strategies for mirrored data

#### **2. Inconsistent Service Boundaries**
**Problem**: Domain services call infrastructure directly
**Examples**:
- `InvoiceService.sync_invoices()`: Calls SmartSyncService directly
- **Impact**: Violates service boundary principles
- **Fix Required**: Move sync logic to data orchestrators

#### **3. Missing Sync Triggers**
**Problem**: No clear strategy for when to sync data
**Examples**:
- Sync methods exist but no scheduled jobs or webhook triggers
- **Impact**: Data will become stale
- **Fix Required**: Implement sync scheduling and triggers

## **Data Flow Analysis**

### **Current Data Flows**

#### **Pattern 1: Data Orchestrator Flow (CORRECT)**
```
User Request → Runway Service → Data Orchestrator → SmartSyncService → QBO API
```
**Status**: ✅ Aligns with architecture
**Examples**: DecisionConsoleDataOrchestrator, DigestDataOrchestrator

#### **Pattern 2: Domain Service Direct Flow (INCORRECT)**
```
User Request → Domain Service → SmartSyncService → QBO API
```
**Status**: ❌ Violates service boundaries
**Examples**: InvoiceService.sync_invoices()

#### **Pattern 3: Local Database Flow (INCOMPLETE)**
```
User Request → Domain Service → Local Database
```
**Status**: ⚠️ Missing sync mechanism
**Examples**: BalanceService.get_current_balances()

### **Required Data Flows (Per Architecture)**

#### **Pattern 1: Live Query Flow**
```
User Request → Runway Service → Data Orchestrator → SmartSyncService → QBO API
```
**Status**: ✅ Already implemented correctly

#### **Pattern 2: Mirrored Data Flow**
```
Scheduled Job → Data Orchestrator → SmartSyncService → QBO API → Local Database
User Request → Runway Service → Domain Service → Local Database
```
**Status**: ❌ Missing sync mechanism

#### **Pattern 3: Hybrid Flow**
```
User Request → Runway Service → Data Orchestrator → SmartSyncService → QBO API (live)
Scheduled Job → Data Orchestrator → SmartSyncService → QBO API → Local Database (mirror)
```
**Status**: ❌ Not implemented

## **Gap Analysis**

### **Missing Components**

#### **1. Sync Orchestration**
- **Missing**: Scheduled sync jobs for mirrored data
- **Missing**: Webhook triggers for real-time updates
- **Missing**: Sync status tracking and error handling

#### **2. Data Ownership Clarity**
- **Unclear**: Which data should be mirrored vs queried live
- **Unclear**: When to use each pattern
- **Unclear**: How to handle data conflicts

#### **3. Service Boundary Enforcement**
- **Missing**: Clear guidelines for service responsibilities
- **Missing**: Enforcement of no direct infrastructure calls from domain services
- **Missing**: Data orchestrator patterns for all data access

### **Inconsistent Implementations**

#### **1. Balance Data**
- **Current**: Domain service queries local DB
- **Missing**: Sync mechanism to populate local data
- **Architecture**: Should be mirrored data with sync

#### **2. Invoice Data**
- **Current**: Domain service has sync method but unclear usage
- **Missing**: Clear sync strategy and triggers
- **Architecture**: Should be mirrored data with sync

#### **3. Bill Data**
- **Current**: Data orchestrators query live APIs
- **Missing**: Local mirroring for performance
- **Architecture**: Should be hybrid (mirror + live query)

## **Alignment Recommendations**

### **Immediate Fixes (High Priority)**

#### **1. Implement Data Mirroring Strategy**
- **Action**: Create sync jobs for mirrored data (bills, invoices, balances)
- **Pattern**: Scheduled jobs → Data Orchestrator → SmartSyncService → Local DB
- **Timeline**: 1-2 weeks

#### **2. Fix Service Boundaries**
- **Action**: Move all SmartSyncService calls to data orchestrators
- **Pattern**: Domain services → Data Orchestrators → SmartSyncService
- **Timeline**: 1 week

#### **3. Implement Sync Triggers**
- **Action**: Create scheduled jobs and webhook handlers
- **Pattern**: Cron jobs + webhook endpoints → Data Orchestrators
- **Timeline**: 1 week

### **Medium Priority Fixes**

#### **1. Clarify Data Ownership**
- **Action**: Document which data is mirrored vs queried live
- **Pattern**: Update architecture docs with clear guidelines
- **Timeline**: 3-5 days

#### **2. Implement Hybrid Patterns**
- **Action**: Add local mirroring for frequently accessed data
- **Pattern**: Mirror for calculations, query live for real-time updates
- **Timeline**: 2-3 weeks

#### **3. Add Sync Monitoring**
- **Action**: Implement sync status tracking and error handling
- **Pattern**: Sync status dashboard and alerting
- **Timeline**: 1-2 weeks

### **Low Priority Improvements**

#### **1. Performance Optimization**
- **Action**: Optimize sync frequency and caching strategies
- **Pattern**: Tune sync intervals based on data usage patterns
- **Timeline**: Ongoing

#### **2. Data Quality Monitoring**
- **Action**: Add data freshness and consistency checks
- **Pattern**: Automated data quality alerts
- **Timeline**: 2-3 weeks

## **Implementation Plan**

### **Phase 1: Fix Critical Misalignments (2-3 weeks)**
1. **Implement Data Mirroring** (1 week)
   - Create sync jobs for bills, invoices, balances
   - Implement sync status tracking
   - Add error handling and retry logic

2. **Fix Service Boundaries** (1 week)
   - Move SmartSyncService calls to data orchestrators
   - Update domain services to use orchestrators
   - Remove direct infrastructure dependencies

3. **Implement Sync Triggers** (1 week)
   - Create scheduled sync jobs
   - Add webhook handlers for real-time updates
   - Implement sync coordination

### **Phase 2: Implement Missing Patterns (2-3 weeks)**
1. **Hybrid Data Patterns** (1 week)
   - Add local mirroring for bills and invoices
   - Implement live query for real-time data
   - Add data freshness validation

2. **Data Ownership Clarity** (1 week)
   - Document data ownership boundaries
   - Create implementation guidelines
   - Add validation checks

3. **Monitoring and Alerting** (1 week)
   - Add sync status monitoring
   - Implement data quality alerts
   - Create sync performance metrics

### **Phase 3: Optimization and Polish (1-2 weeks)**
1. **Performance Tuning** (1 week)
   - Optimize sync frequency
   - Tune caching strategies
   - Add performance monitoring

2. **Documentation and Training** (1 week)
   - Update architecture documentation
   - Create implementation guides
   - Add troubleshooting documentation

## **Success Metrics**

### **Technical Metrics**
- **Data Freshness**: 95% of mirrored data within 15 minutes of source
- **Sync Reliability**: 99.9% successful sync operations
- **Performance**: <3 second dashboard load times
- **Error Rate**: <1% sync failures

### **Architecture Metrics**
- **Service Boundaries**: 100% of services follow defined patterns
- **Data Ownership**: Clear ownership for 100% of data types
- **Sync Coverage**: All mirrored data has sync mechanisms
- **Monitoring**: 100% of sync operations monitored

## **Risk Assessment**

### **High Risk**
- **Data Loss**: Sync failures could result in stale data
- **Performance**: Sync operations could impact system performance
- **Complexity**: Multiple sync patterns could increase maintenance burden

### **Mitigation Strategies**
- **Data Loss**: Implement comprehensive error handling and retry logic
- **Performance**: Use background jobs and optimize sync frequency
- **Complexity**: Clear documentation and monitoring for all patterns

## **Next Steps**

1. **Review and Approve**: Stakeholder review of this audit and recommendations
2. **Prioritize Fixes**: Decide which fixes to implement first
3. **Create Implementation Tasks**: Break down fixes into executable tasks
4. **Begin Implementation**: Start with highest priority fixes
5. **Monitor Progress**: Track implementation against success metrics

---

*This audit provides the foundation for aligning the codebase with the defined data architecture patterns.*

