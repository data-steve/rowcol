# S08: Experience Architecture Design

**Status**: [✅] Complete

**Priority**: P1 High

**Dependencies**
- **Depends on**: E02_FIX_DATA_ORCHESTRATOR_PATTERN (completed)
- **Blocks**: S07_ORCHESTRATOR_INTEGRATION_ANALYSIS

## **Problem Statement**

We need to align the architecture of `runway/core/`, `runway/core/data_orchestrators/`, and `runway/experiences/` based on clear product understanding of what each experience needs and how users interact with them.

## **Goal**

Create a comprehensive design doc that explains for each experience:
- What the experience needs
- What metrics/calculators it requires
- What data orchestrators should provide
- How users interact with each experience

## **Scope**

### **Experiences to Design**
1. **HygieneTray** - Live user-action experience
2. **DecisionConsole** - Live user-action experience  
3. **Digest** - Email snapshot experience
4. **TestDrive** - Email snapshot experience

### **Architecture Components to Align**
- `runway/core/` - Pure calculators vs mixed services
- `runway/core/data_orchestrators/` - Data pulling for each experience
- `runway/experiences/` - User-facing experience services

## **Product Understanding**

### **Live User-Action Experiences** (Tray, Console)
- **User Goal**: Actually clean up issues and make decisions
- **Data Need**: Raw data from orchestrators
- **User Actions**: Click, clean up, make decisions
- **Calculators**: Heads-up perspective and progress tracking
- **Architecture**: Experience → Calculator → Data Orchestrator → Domains

### **Email Snapshot Experiences** (Digest, TestDrive)
- **User Goal**: Understand situation overview, drive to action
- **Data Need**: Aggregated/calculated metrics from calculators
- **User Actions**: Click into tray/console to start working
- **Calculators**: Situation analysis and metrics
- **Architecture**: Experience → Calculator → Data Orchestrator → Domains

## **Experience Design Analysis**

### **1. HygieneTray Experience**

**User Goal**: Clean up data quality issues that prevent optimal runway analysis

**Current Implementation**: `TrayService` - Uses `HygieneTrayDataOrchestrator` + multiple calculators

**Data Needs**:
- Raw bills and invoices with data quality issues
- Tray item state (processing status, priorities)
- Real-time progress tracking

**Required Calculators**:
- **DataQualityAnalyzer** ✅ (Pure calculator - hygiene scoring)
- **PriorityCalculationService** ✅ (Pure calculator - priority scoring)
- **RunwayCalculationService** ✅ (Pure calculator - runway context)
- **BillImpactCalculator** ✅ (Stateless - bill impact analysis)
- **TrayItemImpactCalculator** ✅ (Stateless - tray item impact)

**Data Orchestrator**: `HygieneTrayDataOrchestrator` ✅
- Pulls bills, invoices, balances from QBO
- Manages tray state (item statuses, priorities, processing queue)
- Business_id scoped for multi-tenant safety

**User Actions**:
- View hygiene issues in priority order
- Click items to fix data quality problems
- Mark items as resolved
- Set priority order for processing

**Architecture Flow**:
```
HygieneTrayService → [DataQualityAnalyzer, PriorityCalculationService, RunwayCalculationService] → HygieneTrayDataOrchestrator → QBO/Domains
```

### **2. DecisionConsole Experience**

**User Goal**: Make context-laden financial decisions with prioritization

**Current Implementation**: `DecisionConsoleService` - Uses `DecisionConsoleDataOrchestrator` + `RunwayCalculationService`

**Data Needs**:
- Bills and invoices ready for decision-making
- Decision queue state
- Runway context for decision impact

**Required Calculators**:
- **RunwayCalculationService** ✅ (Pure calculator - runway context)
- **PriorityCalculationService** ✅ (Pure calculator - decision priorities)
- **DecisionImpactCalculator** ❌ (Missing - decision impact analysis)

**Data Orchestrator**: `DecisionConsoleDataOrchestrator` ✅
- Pulls bills, invoices, balances from QBO
- Manages decision queue state
- Business_id scoped for multi-tenant safety

**User Actions**:
- View bills and invoices in decision queue
- Make approve/reject decisions
- Add notes to decisions
- Process decision batch

**Architecture Flow**:
```
DecisionConsoleService → [RunwayCalculationService, PriorityCalculationService, DecisionImpactCalculator] → DecisionConsoleDataOrchestrator → QBO/Domains
```

### **3. Digest Experience**

**User Goal**: Understand weekly situation overview and drive to action

**Current Implementation**: `DigestService` - Uses `DigestDataOrchestrator` + `RunwayCalculationService`

**Data Needs**:
- Aggregated metrics and summary data
- Historical trends and analysis
- Actionable insights and recommendations

**Required Calculators**:
- **RunwayCalculationService** ✅ (Pure calculator - runway analysis)
- **DataQualityAnalyzer** ✅ (Pure calculator - hygiene metrics)
- **TrendAnalysisCalculator** ❌ (Missing - historical trend analysis)
- **InsightGenerator** ❌ (Missing - insight generation)

**Data Orchestrator**: `DigestDataOrchestrator` ✅
- Pulls historical data with flexible configuration
- Manages digest state (progress, insights, recommendations)
- Supports A/B testing and experimentation

**User Actions**:
- View weekly situation summary
- Click into specific issues
- Navigate to tray/console for action

**Architecture Flow**:
```
DigestService → [RunwayCalculationService, DataQualityAnalyzer, TrendAnalysisCalculator, InsightGenerator] → DigestDataOrchestrator → QBO/Domains
```

### **4. TestDrive Experience**

**User Goal**: Preview Oodaloo value and drive to signup

**Current Implementation**: `TestDriveService` - Uses `DigestDataOrchestrator` with TestDrive config

**Data Needs**:
- Sample metrics and preview data
- Demo insights and value propositions
- A/B testing variants

**Required Calculators**:
- **RunwayCalculationService** ✅ (Pure calculator - runway preview)
- **DataQualityAnalyzer** ✅ (Pure calculator - hygiene preview)
- **ValuePropositionCalculator** ❌ (Missing - value prop generation)
- **DemoMetricsCalculator** ❌ (Missing - demo-specific metrics)

**Data Orchestrator**: `DigestDataOrchestrator` ✅ (Reused with TestDrive config)
- Pulls preview data with TestDrive configuration
- Supports A/B testing variants
- Manages demo state

**User Actions**:
- View preview of Oodaloo capabilities
- Click to signup
- Explore different A/B test variants

**Architecture Flow**:
```
TestDriveService → [RunwayCalculationService, DataQualityAnalyzer, ValuePropositionCalculator, DemoMetricsCalculator] → DigestDataOrchestrator → QBO/Domains
```

## **Calculator Architecture Design**

### **Pure Calculators** (Metrics Only) ✅

**Existing Pure Calculators**:
1. **DataQualityAnalyzer** ✅ - Hygiene scoring, data quality analysis
2. **RunwayCalculationService** ✅ - Runway calculations, scenario analysis
3. **PriorityCalculationService** ✅ - Priority scoring for all entity types
4. **BillImpactCalculator** ✅ - Bill-specific impact calculations (stateless)
5. **TrayItemImpactCalculator** ✅ - Tray item impact calculations (stateless)

**Missing Pure Calculators**:
6. **DecisionImpactCalculator** - Decision impact analysis
7. **TrendAnalysisCalculator** - Historical trend analysis
8. **InsightGenerator** - Insight and recommendation generation
9. **ValuePropositionCalculator** - Value prop generation for TestDrive
10. **DemoMetricsCalculator** - Demo-specific metrics

### **Mixed Services** (Need Separation) ❌

**Current Mixed Services**:
- **RunwayCalculationService** ✅ - Already separated (pure calculator)
- **PriorityCalculationService** ✅ - Already separated (pure calculator)

**No Mixed Services Found** - All current services are properly separated!

## **Data Orchestrator Architecture Design**

### **Data Orchestrators** (One per Experience) ✅

**Existing Orchestrators**:
1. **HygieneTrayDataOrchestrator** ✅ - Raw hygiene data + tray state
2. **DecisionConsoleDataOrchestrator** ✅ - Raw decision data + decision queue
3. **DigestDataOrchestrator** ✅ - Aggregated data + digest state (flexible config)

**Architecture Pattern**:
- All orchestrators are stateless (no instance variables)
- State stored in database with business_id scoping
- Pull data from QBO via SmartSyncService
- Transform data for specific experience needs
- Manage experience-specific state (queues, progress, etc.)

## **Experience Service Architecture Design**

### **Experience Services** ✅

**Existing Services**:
1. **TrayService** ✅ - Uses orchestrator + calculators for live experience
2. **DecisionConsoleService** ✅ - Uses orchestrator + calculators for live experience
3. **DigestService** ✅ - Uses orchestrator + calculators for email experience
4. **TestDriveService** ✅ - Uses orchestrator + calculators for preview experience

**Architecture Pattern**:
- Each service uses one data orchestrator
- Each service uses multiple calculators for business logic
- Services remain stateless (no instance variables)
- Services orchestrate between orchestrators and calculators
- Services handle user-facing logic and API responses

## **Missing Components Analysis**

### **Missing Calculators** (Need to Create)

1. **DecisionImpactCalculator**
   - Purpose: Calculate impact of approve/reject decisions on runway
   - Input: Decision data + runway context
   - Output: Impact analysis (runway days gained/lost)

2. **TrendAnalysisCalculator**
   - Purpose: Analyze historical trends for digest
   - Input: Historical QBO data
   - Output: Trend metrics and patterns

3. **InsightGenerator**
   - Purpose: Generate insights and recommendations
   - Input: Analysis results from other calculators
   - Output: Actionable insights and recommendations

4. **ValuePropositionCalculator**
   - Purpose: Generate value props for TestDrive
   - Input: Demo data + analysis results
   - Output: Value proposition statements

5. **DemoMetricsCalculator**
   - Purpose: Calculate demo-specific metrics
   - Input: Demo data
   - Output: Demo metrics and KPIs

### **Missing Experience Services** (Need to Create)

**None** - All experience services exist and are properly implemented!

## **Architecture Alignment Plan**

### **Phase 1: Create Missing Calculators** (High Priority)

1. **DecisionImpactCalculator** - For DecisionConsole
2. **TrendAnalysisCalculator** - For Digest
3. **InsightGenerator** - For Digest
4. **ValuePropositionCalculator** - For TestDrive
5. **DemoMetricsCalculator** - For TestDrive

### **Phase 2: Update Experience Services** (Medium Priority)

1. **DecisionConsoleService** - Add DecisionImpactCalculator
2. **DigestService** - Add TrendAnalysisCalculator + InsightGenerator
3. **TestDriveService** - Add ValuePropositionCalculator + DemoMetricsCalculator

### **Phase 3: Integration Testing** (Low Priority)

1. Test all experience services with new calculators
2. Validate data flow from orchestrators to calculators to experiences
3. Ensure proper error handling and fallbacks

## **Implementation Roadmap**

### **Immediate Actions** (Next 1-2 days)
1. Create missing calculators in `runway/core/`
2. Update experience services to use new calculators
3. Test integration points

### **Short Term** (Next 1 week)
1. Complete S07 integration analysis
2. Run E03 validation tests
3. Fix any integration issues found

### **Medium Term** (Next 2 weeks)
1. Implement missing experience services if needed
2. Update routes to use new architecture
3. Update tests to cover new components

## **Success Criteria**

- [ ] All experience needs clearly defined
- [ ] Calculator architecture aligned with experience needs
- [ ] Data orchestrator architecture aligned with experience needs
- [ ] Missing components identified and prioritized
- [ ] Implementation plan ready for execution
- [ ] All stakeholders understand the design

## **Key Insights**

### **What's Working Well** ✅
1. **Data Orchestrators** - Properly implemented with state management
2. **Core Calculators** - Most pure calculators already exist
3. **Experience Services** - All services exist and follow correct pattern
4. **Architecture Pattern** - Correct flow: Experience → Calculator → Orchestrator → Domains

### **What Needs Work** ❌
1. **Missing Calculators** - 5 calculators need to be created
2. **Calculator Integration** - Experience services need to use new calculators
3. **Testing** - Need to validate all integration points

### **Architecture Quality** ✅
- **Separation of Concerns** - Clear boundaries between orchestrators, calculators, and experiences
- **Multi-tenancy** - Proper business_id scoping throughout
- **Stateless Services** - All services follow stateless pattern
- **Flexible Configuration** - DigestDataOrchestrator supports multiple use cases

## **Next Steps**

1. **Complete S07** - Integration analysis to map current state against this design
2. **Run E03** - Validate that current implementations work with existing integration points
3. **Create Missing Calculators** - Implement the 5 missing calculators
4. **Update Experience Services** - Integrate new calculators into experience services
5. **Test End-to-End** - Ensure all experiences work correctly with new architecture

---

*This design provides the foundation for implementing the correct architecture pattern with clear separation of concerns and proper calculator integration.*