# 1_NEEDS_SOLVING_TASKS.md - Firm-First Development

**Status**: 🔍 NEEDS ANALYSIS  
**Context**: Tasks that require design/analysis before execution  
**Updated**: 2025-09-30

---

## **CRITICAL: Read These Files First**

### **Architecture Context (Required for All Tasks):**
- `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Complete system architecture
- `docs/BUILD_PLAN_FIRM_FIRST_V6.0.md` - Current build plan and phase context
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy
- `docs/architecture/ADR-003-multi-tenancy-strategy.md` - Multi-tenancy patterns
- `DEVELOPMENT_STANDARDS.md` - Development standards and anti-patterns

### **Task-Specific Context:**
- Review the specific task document for additional context files
- Understand the current phase and architectural constraints
- Familiarize yourself with the codebase structure and patterns

---

## **Context for All Tasks**

### **Strategic Pivot (2025-09-30)**
- **PRIMARY ICP**: CAS accounting firms (20-100 clients) 
- **SECONDARY ICP**: Individual business owners (Phase 7+)
- **PRIORITY**: Data completeness > Agentic features
- **PRICING**: $50/mo per client (CAS firms), $99/mo (future owners)
- **DISTRIBUTION**: Direct sales to CAS firms (primary), QBO App Store (Phase 7+)

### **Why We Pivoted**
Levi Morehouse (Aiwyn.ai President) validated the problem but identified the blocker:
- ✅ Problem is "10,000% right - real need"  
- ❌ BUT: "Owners won't do the work" (won't maintain data completeness)
- ✅ Solution: CAS firms can ensure data quality and enforce the ritual
- ✅ Pricing: $50/mo per client scales better than $99/mo per owner

### **Architecture Foundation**
- ✅ Multi-tenant ready (`business_id` scoping)
- ✅ Data orchestrator pattern implemented
- ✅ Service boundaries clarified (ADR-001 compliance)
- ✅ SmartSync patterns established
- ✅ Database fixtures created

### **Current State**
- **Phase 0-2**: Complete (foundation ready)
- **Phase 3**: Multi-tenant foundation (ready to start)
- **Phase 4**: Data completeness (bank feeds, missing bills)
- **Phase 5**: Multi-client dashboard
- **Phase 6**: CAS firm pilot features

---

## **Progress Tracking Instructions**

### **Task Status Tracking:**
- `[ ]` - Not started
- `[🔄]` - In progress (discovery phase)
- `[🔍]` - Analysis phase (after discovery complete)
- `[💡]` - Solution identified (ready to implement)
- `[✅]` - Solution documented (ready for executable phase)
- `[❌]` - Blocked/Need help

**IMPORTANT**: Always update the task status in the document as you work through tasks.

### **Cursor Todo Integration:**
1. **Create Cursor Todo** when starting analysis
2. **Update Todo Status** as analysis progresses
3. **Add Discovery Todos** for discovered issues
4. **Complete Todos** when analysis is done
5. **Clean Up Todos** when analysis is complete

---

## **🎯 ANALYSIS REQUIRED**

These tasks need design and analysis before they can be executed. They should be tackled after the execution-ready tasks are complete.

---

## **📋 SOLUTIONING TASKS**

### **Task S1: Design Comprehensive Testing Strategy**
- **Status**: `[ ]` Needs analysis
- **Priority**: P1 High
- **Effort**: 20h (analysis) + 40h (implementation)
- **Context**: After data architecture is complete
- **Focus**: Mock violations, integration tests, performance tests
- **Questions to Answer**:
  - How do we test multi-tenant data isolation?
  - What's the testing strategy for QBO integration?
  - How do we test performance with 50+ clients?
  - What's the mock strategy for external APIs?

### **Task S2: Design Console Payment Decision Workflow**
- **Status**: `[ ]` Needs analysis  
- **Priority**: P1 High
- **Effort**: 20h (analysis) + 30h (implementation)
- **Context**: Bill approval → staging → decision → finalization → execution
- **Focus**: Reserve allocation timing, batch processing, service boundaries
- **Questions to Answer**:
  - When should reserves be allocated vs. released?
  - How do we handle batch payment decisions?
  - What's the rollback strategy for failed payments?
  - How do we handle partial approvals?

### **Task S3: Design Real Sync Health Scoring**
- **Status**: `[ ]` Needs analysis
- **Priority**: P1 High
- **Effort**: 15h (analysis) + 25h (implementation)
- **Context**: Replace mock sync health scoring with real calculations
- **Focus**: QBO sync reliability, data freshness, error detection
- **Questions to Answer**:
  - What metrics indicate healthy QBO sync?
  - How do we detect and score sync failures?
  - What's the threshold for "unhealthy" sync?
  - How do we handle partial sync failures?

### **Task S4: Design Experiences Cleanup and Consolidation**
- **Status**: `[ ]` Needs analysis
- **Priority**: P2 Medium
- **Effort**: 10h (analysis) + 20h (implementation)
- **Context**: Consolidate duplicate experience services
- **Focus**: Service boundaries, code duplication, maintainability
- **Questions to Answer**:
  - Which experience services have overlapping functionality?
  - How do we consolidate without breaking existing patterns?
  - What's the right abstraction level for experience services?
  - How do we maintain backward compatibility?

### **Task S5: Design Infrastructure Phase 3 Consolidation**
- **Status**: `[ ]` Needs analysis
- **Priority**: P2 Medium
- **Effort**: 15h (analysis) + 30h (implementation)
- **Context**: Consolidate file processing, monitoring, and utils
- **Focus**: Infrastructure organization, service boundaries, reusability
- **Questions to Answer**:
  - How do we organize infrastructure services?
  - What's the right abstraction for file processing?
  - How do we standardize monitoring across services?
  - What utilities are truly reusable vs. domain-specific?

---

## **🔍 ANALYSIS FRAMEWORK**

For each solutioning task, provide:

### **1. Problem Analysis**
- What exactly needs to be solved?
- What are the current pain points?
- What are the constraints and requirements?

### **2. Solution Design**
- What's the proposed solution?
- How does it fit with existing architecture?
- What are the trade-offs?

### **3. Implementation Plan**
- What are the specific steps?
- What files need to be created/modified?
- What are the verification criteria?

### **4. Dependencies**
- What needs to be completed first?
- What external dependencies exist?
- What are the risks?

---

## **📊 PRIORITIZATION**

### **High Priority (Do First)**
1. **Task S1**: Testing Strategy - Critical for quality
2. **Task S2**: Payment Workflow - Core business logic
3. **Task S3**: Sync Health Scoring - Data reliability

### **Medium Priority (Do Later)**
4. **Task S4**: Experiences Cleanup - Code quality
5. **Task S5**: Infrastructure Consolidation - Organization

---

## **🚀 EXECUTION READINESS**

**These tasks are NOT ready for execution until:**
- [ ] Problem analysis is complete
- [ ] Solution design is documented
- [ ] Implementation plan is detailed
- [ ] Dependencies are mapped
- [ ] Verification criteria are defined

**After analysis, move to `EXECUTION_READY_TASKS.md`**

---

**Status**: Needs analysis before execution  
**Next Action**: Start with Task S1 (Testing Strategy) analysis  
**Updated**: 2025-09-30
