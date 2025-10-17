// *** SOLUTIONING GUARDRAIL: UNIVERSAL vs MISSION FIRST ***
// 
// Before solving any of these solutioning tasks, remember:
// 
// MISSION FIRST IS THE PROOF OF CONCEPT:
// - Provides the template structure (rows, formulas, layout)
// - Shows what output looks like for nonprofit + subscriptions
// - NOT the entire product definition
// 
// WE'RE SOLVING FOR UNIVERSAL:
// - How to detect inflows/outflows for ANY client type
// - How to detect recurrence/magnitude for ANY business model
// - How to bucket transactions to months for ANY payment pattern
// - How to store learning so each client improves over time
// 
// SOLUTIONING STRATEGY:
// When designing solutions, always ask:
// 
// ✅ "Does this work for nonprofit?"
// ✅ "Does this work for agency?"
// ✅ "Does this work for SaaS?"
// ✅ "Does this work for professional services?"
// 
// If answer is "no" or "with hardcoding", it's not the right solution.
// 
// MISSION FIRST SHOULD BE A TEST CASE:
// - S0.1 validates across nonprofit + agency + SaaS client types
// - S0.2 measures quality for diverse business models
// - S0.3 learns corrections from ANY client type
// 
// NOT a reason to hardcode or build bespoke logic.
// 
// *** The system scales or it doesn't. No middle ground. ***
//

# RowCol MVP - Tasks Needing Solutioning

**Status:** Analysis Phase  
**Focus:** Design and planning tasks requiring discovery and solution work  

---

## **CRITICAL: Context Files (MANDATORY)**

### **Architecture Context:**
- `_clean/architecture/comprehensive_architecture.md` - Overall architecture
- `_clean/mvp/recovery_build_plan.md` - Recovery strategy

### **Product Context:**
- `_clean/mvp/mvp_comprehensive_prd.md` - MVP PRD and market positioning

### **Executable Tasks Reference:**
- `_clean/spreadsheet_builder/E0_PHASE_0_PORTING_AND_INTEGRATION.md` - Phase 0 (foundation)
- `_clean/spreadsheet_builder/E1_PHASE_1_TEMPLATE_SYSTEM.md` - Phase 1 (core features)

---

## **S0.1: Multi-Client Pilot Strategy**

**Status:** `[ ]` Not started  
**Priority:** P1 High  
**Phase:** Planning (Pre-Phase 0)

### **Problem Statement**
Need to design and plan how to validate the template system across diverse CAS client types (nonprofit, agency, SaaS, etc.) to ensure:
1. Template adaptability across different GL structures
2. Vendor normalization works for different naming patterns
3. GL classification accuracy across industries
4. Data quality improvements transfer across segments
5. Market feedback for broader adoption

### **Solutioning Mindset**
This requires discovery of:
- What are the actual CAS market segments we should test?
- What data quality challenges are specific to each segment?
- How do GL structures differ across industries?
- What vendor patterns are unique to each segment?
- How do we measure success across segments?

### **Discovery Phase Checklist**

**Research Questions:**
- [ ] What are the primary CAS market segments (by firm type or client industry)?
- [ ] What are typical GL account structures for each segment?
- [ ] What are typical vendor naming patterns per segment?
- [ ] How do data quality issues differ across segments?
- [ ] What success metrics matter most to each segment?

**Discovery Commands:**
```bash
# Look for existing pilot documentation or market research
find . -name "*pilot*" -o -name "*segment*" -o -name "*market*" | grep -v node_modules

# Check for existing client data or test data
find . -path "*test*" -name "*data*" | head -10

# Look for existing business logic around segmentation
grep -r "nonprofit\|saas\|agency\|consulting" . --include="*.py" --include="*.md"

# Check product strategy for market insights
grep -r "segment\|market\|vertical" _clean/product/ --include="*.md"
```

**Files to Review:**
- `_clean/mvp/mvp_comprehensive_prd.md` - Market segmentation mentioned?
- `_clean/product/product_strategy.md` - CAS market strategy?
- `_clean/architecture/comprehensive_architecture.md` - Multi-tenant implications?

### **Analysis Phase Checklist**

**Current State Understanding:**
- [ ] What CAS market segments exist?
- [ ] What are the key differences between segments?
- [ ] Which segments should we target first?
- [ ] What data do we have access to for testing?

**Gap Analysis:**
- [ ] Do we have test data for each segment?
- [ ] Do we have COA templates for each segment?
- [ ] Do we have vendor normalization rules for each segment?
- [ ] What's missing or unclear?

### **Design Phase Checklist**

**Pilot Design:**
- [ ] Select 2-3 primary market segments to pilot
- [ ] Define success metrics for each segment
- [ ] Design test data setup for each segment
- [ ] Plan feedback collection process
- [ ] Design iteration cycle based on feedback

**Rollout Strategy:**
- [ ] Phased rollout plan (segment-by-segment)
- [ ] Feedback incorporation process
- [ ] Measurement and adjustment strategy
- [ ] Success criteria per segment

### **Documentation Phase Checklist**

**Deliver:**
- [ ] Pilot strategy document with:
  - Chosen market segments and rationale
  - Success metrics per segment
  - Test data requirements
  - Timeline and dependencies
- [ ] Market segment profiles:
  - Typical GL structures
  - Vendor patterns
  - Data quality challenges
  - Success criteria
- [ ] Feedback collection process
- [ ] Create E1.5 executable task (Multi-Client Pilot Validation)

### **Solution Required**
Design a multi-segment pilot strategy that validates:
1. Template adaptability across industries
2. GL classification effectiveness
3. Vendor normalization robustness
4. Market fit across CAS segments
5. Data quality improvement mechanisms

### **Next Task:** E1.5 - Multi-Client Pilot Validation (uses this strategy)

---

## **S0.2: Data Quality Metrics Framework**

**Status:** `[ ]` Not started  
**Priority:** P1 High  
**Phase:** Planning (Concurrent with Phases 0-1)

### **Problem Statement**
Need to design and implement comprehensive data quality metrics that:
1. Measure transaction classification accuracy
2. Track vendor normalization effectiveness
3. Monitor GL mapping quality
4. Identify data quality issues by type
5. Guide continuous improvement

### **Solutioning Mindset**
This requires understanding:
- What makes good vs bad data quality in cash flow context?
- How do we measure each dimension?
- What are the acceptance thresholds?
- How do we identify and categorize data quality issues?
- What improvement levers exist?

### **Discovery Phase Checklist**

**Research Questions:**
- [ ] What data quality dimensions matter most? (coverage, accuracy, timeliness, completeness)
- [ ] How are these measured in existing systems?
- [ ] What are industry-standard thresholds?
- [ ] What data quality issues have we seen?
- [ ] How do quality issues correlate with transaction types?

**Discovery Commands:**
```bash
# Look for existing data quality metrics
grep -r "quality\|accuracy\|coverage\|confidence" . --include="*.py" --include="*.md" | head -20

# Check existing transaction models for quality fields
grep -r "confidence\|status\|quality" domains/core/models/ --include="*.py"

# Look for existing validation logic
grep -r "validate\|check\|verify" domains/ --include="*.py" | head -20

# Check console service for metrics
grep -r "class ConsoleService\|def.*metric" _clean/mvp/runway/services/ --include="*.py"
```

**Files to Review:**
- `domains/core/models/transaction.py` - What quality fields exist?
- `_clean/mvp/domains/core/models/transaction.py` - Ported version?
- `_clean/mvp/runway/services/console_service.py` - Existing metrics?

### **Analysis Phase Checklist**

**Current State Understanding:**
- [ ] What quality metrics are already tracked?
- [ ] What fields in models support quality measurement?
- [ ] What gaps exist in current tracking?
- [ ] What data quality issues are we seeing?

**Gap Analysis:**
- [ ] Are there quality issues not being tracked?
- [ ] Are there metrics not being calculated?
- [ ] Are thresholds defined?
- [ ] Is feedback mechanism in place?

### **Design Phase Checklist**

**Metrics Framework:**
- [ ] Define quality dimensions (coverage, accuracy, timeliness, completeness)
- [ ] Define metrics for each dimension
- [ ] Define measurement methods
- [ ] Define acceptance thresholds
- [ ] Define improvement mechanisms

**Quality Monitoring:**
- [ ] Real-time quality dashboard
- [ ] Quality alerts/notifications
- [ ] Issue categorization system
- [ ] Root cause analysis framework

### **Documentation Phase Checklist**

**Deliver:**
- [ ] Data quality metrics framework document with:
  - Quality dimensions and definitions
  - Metrics and measurement methods
  - Acceptance thresholds
  - Improvement mechanisms
- [ ] Metrics dashboard design
- [ ] Quality monitoring system design
- [ ] Integration plan with E1.4 API endpoints

### **Solution Required**
Design a comprehensive data quality metrics framework that:
1. Measures transaction classification accuracy
2. Tracks vendor normalization effectiveness
3. Monitors GL mapping quality
4. Enables continuous improvement
5. Integrates with API endpoints

### **Next Task:** E1.4 - Create API Endpoints for Template Generation (needs these metrics)

---

## **S0.3: Learning Loop Integration (Fast Follow)**

**Status:** `[ ]` Not started  
**Priority:** P2 Medium  
**Phase:** Post-MVP (Fast Follow)

### **Problem Statement**
Template system should improve over time using:
1. User corrections to suggested GL classifications
2. Vendor normalization refinement
3. Policy engine rule learning
4. Confidence score calibration

Need to design how corrections/suggestions flow through the system.

### **Solutioning Mindset**
This requires understanding:
- How do corrections currently flow (if at all)?
- How does policy engine learn from corrections?
- How does vendor normalization improve?
- What feedback mechanisms exist?
- How do we avoid regressing on quality?

### **Discovery Phase Checklist**

**Research Questions:**
- [ ] How do Suggestion and Correction models work?
- [ ] What feedback mechanisms exist in PolicyEngine?
- [ ] How does VendorNormalization currently improve?
- [ ] What learning mechanisms are available?
- [ ] What safety measures prevent regressions?

**Discovery Commands:**
```bash
# Check policy engine for learning logic
grep -r "correction\|suggestion\|learn\|feedback" _parked/policy/ --include="*.py"

# Check correction/suggestion models
grep -r "class Correction\|class Suggestion" . --include="*.py"

# Check vendor normalization for improvement mechanisms
grep -r "improve\|confidence\|calibrate" _parked/vendor_normalization/ --include="*.py"

# Look for existing feedback systems
grep -r "feedback\|correct\|suggest" domains/ap/services/ --include="*.py"
```

### **Analysis Phase Checklist**

**Current State Understanding:**
- [ ] What learning capabilities exist?
- [ ] What feedback mechanisms are in place?
- [ ] What's the current flow for corrections?
- [ ] What gaps exist in learning loop?

**Opportunity Analysis:**
- [ ] Where would learning provide most value?
- [ ] What are low-hanging fruit improvements?
- [ ] What requires more investment?
- [ ] What risks exist?

### **Design Phase Checklist**

**Learning Loop Design:**
- [ ] Correction collection mechanism
- [ ] Feedback processing system
- [ ] Policy engine rule refinement
- [ ] Vendor normalization improvement
- [ ] Confidence score calibration

**Safety Mechanisms:**
- [ ] Regression detection
- [ ] Quality gates
- [ ] Rollback procedures
- [ ] Audit trail

### **Solution Required**
Design a learning loop that:
1. Collects user corrections safely
2. Improves policy engine rules over time
3. Refines vendor normalization
4. Calibrates confidence scores
5. Prevents regressions

### **Next Task:** E2+ (Future phases - this is post-MVP enhancement)

---

## **Planning Next Steps**

### **Recommended Solutioning Order:**

1. **S0.1: Multi-Client Pilot Strategy** (1-2 days)
   - Determines which segments to test
   - Informs E1.5 execution
   - Guides market validation approach

2. **S0.2: Data Quality Metrics Framework** (2-3 days)
   - Informs E1.4 API endpoint design
   - Guides implementation approach
   - Enables measurement during piloting

3. **S0.3: Learning Loop Integration** (Design only, post-MVP)
   - Can proceed in parallel after Phase 0
   - Not needed for MVP execution
   - Should be designed before Phase 2

### **Completion Criteria:**

Each solutioning task should produce:
- [ ] Problem analysis document
- [ ] Current state assessment
- [ ] Solution design document
- [ ] Implementation roadmap
- [ ] Executable task(s) for next phase

---

## **How to Use These Solutioning Tasks**

1. **Start with discovery** - Run all discovery commands and read referenced files
2. **Document findings** - Write down what you learn and what's unclear
3. **Analyze gaps** - Compare current state to needed capabilities
4. **Design solution** - Create design documents with specific approaches
5. **Create executable tasks** - Convert design into step-by-step implementation tasks
6. **Update this document** - Mark tasks complete and link to new executable tasks

This process ensures we make well-informed decisions rather than guessing, and produces clear executable work for the next phase.
