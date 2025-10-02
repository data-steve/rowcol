# Launch Self-Healing Tasks - RowCol Build Plan Execution

*This file provides the process for executing build plan tasks with dynamic gap discovery and healing*

## **Quick Start**

1. **Read Build Plan Context** (below) - understand Phase 1 requirements
2. **Navigate**: `cd ~/projects/rowcol`
3. **Activate**: `poetry shell` (one-time)
4. **Create Branch**: `git checkout -b feature/[task-name]`
5. **Start App**: `uvicorn main:app --reload` (keep running)
6. **Execute**: Follow the self-healing task process

## **Build Plan Context**

### **Phase 1 Goal**: Advisor-First Runway MVP
- **Target**: Productionizable Tier 1 MVP in 4 weeks (~120-180h)
- **Goal**: Spreadsheet replacement for advisors managing 20-50 clients
- **Success**: Advisor can see all clients' runway days in <2 seconds

### **⚠️ CRITICAL: Build Plan Reality Check**
- **Build plans are naively simplistic** - handwavy over massive complexity
- **Not real requirement docs** - too simplistic for actual implementation
- **Hopelessly underspecified** - missing critical details
- **Need massive healing** - like we did with v5 build plan on Oodaloo
- **Core demands are same as Oodaloo v5** - multi-tenancy, QBO integration, service boundaries

### **Key Architecture Changes Needed**:
- **Add `advisor_id` Model**: Create advisor entity (CAS professional) alongside existing business_id (client)
- **Create `advisor/` Layer**: New architectural layer for advisor-client interaction
- **Multi-Tenancy Update**: Support `advisor_id` → `business_id` (client) relationship
- **Feature Gating System**: Implement subscription tier-based feature flags
- **Console Payment Workflow**: Implement advisor-only payment decision workflow

### **What We Know Exists**:
- ✅ Multi-tenancy with `business_id` (clients) - needs `advisor_id` (advisors) added
- ✅ QBO integration with SmartSyncService
- ✅ Runway services architecture (data orchestrators, calculators, experiences)
- ✅ Domain services (AP, AR, Core) with proper patterns
- ✅ Many routes exist but need advisor-scoping

## **Self-Healing Process Philosophy**

### **The Core Problem**:
Build plans are idealized but codebase reality changes as we work. Static audits become stale quickly.

### **The Self-Healing Solution**:
Each task discovers its own reality, heals gaps dynamically, and updates documentation as it works.

### **Key Principles**:
- **Discovery First**: Always understand what actually exists before assuming
- **Gap Healing**: Fix discovered gaps as part of task execution
- **Documentation Updates**: Update build plans based on discovered reality
- **Iterative Refinement**: Each task improves the accuracy of subsequent tasks

## **Self-Healing Task Process**

### **Phase 1: Discovery & Reality Check (MANDATORY)**

**For Each Task, Before Any Implementation:**

1. **Read Task Description** - Understand what the build plan thinks needs to be done
2. **Discover Current Reality** - Find what actually exists in the codebase
3. **Identify Gaps** - Compare build plan assumptions vs. reality
4. **Heal Gaps** - Fix discovered issues as part of task execution
5. **Update Documentation** - Update build plan based on discovered reality

### **Discovery Commands Pattern**

```bash
# 1. Find all references to understand current patterns
grep -r "pattern_name" . --include="*.py"

# 2. Understand file relationships and dependencies
find . -name "*.py" -exec grep -l "pattern_name" {} \;

# 3. Check current imports and usage
grep -r "import.*pattern_name" . --include="*.py"

# 4. Test current state
uvicorn main:app --reload
pytest -k "test_pattern_name"

# 5. Check for specific patterns mentioned in build plan
grep -r "advisor_id" . --include="*.py"
grep -r "business_id" . --include="*.py"
grep -r "firm_id" . --include="*.py"
grep -r "client_id" . --include="*.py"
```

### **Gap Healing Process**

**When Gaps Are Discovered:**

1. **Document the Gap** - What build plan assumed vs. what exists
2. **Assess Impact** - Does this affect the task or future tasks?
3. **Heal Immediately** - Fix the gap as part of current task
4. **Update Build Plan** - Mark assumptions as corrected
5. **Propagate Changes** - Update related tasks that depend on this

### **Documentation Update Pattern**

**After Each Task:**

1. **Update Task Status** - Mark as complete with reality notes
2. **Update Build Plan** - Correct assumptions based on discoveries
3. **Update Dependencies** - Fix other tasks that depend on this work
4. **Archive Discovery** - Save discovery notes for future reference

## **Task Execution Pattern**

### **For Each Build Plan Task:**

1. **Discovery Phase** (15-30 min)
   - Run discovery commands
   - Read existing code
   - Understand current patterns
   - Document assumptions vs. reality

2. **Gap Analysis Phase** (10-15 min)
   - Identify what needs to be built vs. what exists
   - Find architectural mismatches
   - Plan gap healing approach

3. **Implementation Phase** (varies)
   - Implement the actual task
   - Heal discovered gaps
   - Update related code
   - Test thoroughly

4. **Documentation Phase** (5-10 min)
   - Update build plan with reality
   - Mark task as complete
   - Update dependent tasks
   - Archive discovery notes

## **Common Gap Patterns**

### **Architecture Mismatches**
- Build plan assumes `advisor_id` but code uses `business_id`
- Build plan assumes certain service patterns that don't exist
- Build plan assumes certain file structures that are different

### **Implementation Gaps**
- Build plan assumes features exist that don't
- Build plan assumes certain APIs that aren't implemented
- Build plan assumes certain data models that are different

### **Dependency Gaps**
- Build plan assumes certain services exist that don't
- Build plan assumes certain patterns that aren't implemented
- Build plan assumes certain integrations that aren't ready

## **Success Criteria**

### **Task Complete When**:
- ✅ **Discovery complete** - All assumptions validated against reality
- ✅ **Gaps healed** - All discovered gaps fixed
- ✅ **Implementation complete** - Task functionality working
- ✅ **Documentation updated** - Build plan reflects reality
- ✅ **Dependencies updated** - Related tasks updated based on discoveries

### **Build Plan Complete When**:
- ✅ **All tasks executed** - Phase 1 MVP working
- ✅ **All gaps healed** - Architecture matches build plan
- ✅ **Documentation accurate** - Build plan reflects actual implementation
- ✅ **No stale assumptions** - All tasks based on reality

## **Working Relationship Guidelines**

### **Self-Healing Phase Role**
- **Principal Architecture**: Drive technical architecture decisions and gap healing
- **Technical Co-founder Support**: Provide conviction, direction, and support for architectural choices
- **Self-Sufficient Analysis**: Answer questions through discovery before asking for help
- **Gap Healing**: Fix discovered gaps as part of task execution

### **Anti-Patterns to Avoid**
1. **Assumption-Based Implementation**: Don't implement without discovering reality
2. **Gap Ignoring**: Don't skip healing discovered gaps
3. **Documentation Staleness**: Don't leave build plans with incorrect assumptions
4. **Dependency Neglect**: Don't forget to update dependent tasks

### **Effective Patterns**
- **Discovery-Driven Development**: Always discover before implementing
- **Gap Healing Integration**: Fix gaps as part of task execution
- **Documentation Living**: Keep build plans updated with reality
- **Dependency Awareness**: Update related tasks based on discoveries

## **Example Self-Healing Task**

### **Task**: "Create Client List View - Backend"

**Discovery Phase**:
```bash
# Find current client-related code
grep -r "client" . --include="*.py" | head -20
grep -r "advisor" . --include="*.py" | head -20
grep -r "business_id" . --include="*.py" | head -20

# Check existing runway services
ls runway/services/
ls runway/routes/
```

**Gap Analysis**:
- Build plan assumes `advisor_id` (advisor) + `business_id` (client) relationship exists
- Build plan assumes advisor model exists but may not
- Build plan assumes client list aggregation across advisor's clients
- Build plan assumes certain service patterns that may not exist

**Gap Healing**:
- Add `advisor_id` model and relationship to existing `business_id` (clients)
- Create advisor-client relationship management
- Implement client list aggregation across advisor's portfolio
- Implement service patterns as needed

**Implementation**:
- Implement actual client list functionality
- Heal discovered gaps
- Test thoroughly

**Documentation Update**:
- Update build plan with reality
- Mark task as complete
- Update dependent tasks

## **Critical Success Factors**

- **Trust the Process** - Discovery → Gap Analysis → Healing → Implementation → Documentation
- **Heal Gaps Immediately** - Don't defer gap healing to later
- **Update Documentation** - Keep build plans accurate
- **One Task at a Time** - Focus deeply on each task
- **Be Confident** - You have the tools to discover and heal gaps

---

## **TASK LIST GOES HERE**

*Attach your specific self-healing task list to this file*

**⚠️ IMPORTANT: These tasks use self-healing process - discover reality, heal gaps, implement, document!**

**⚠️ CRITICAL: Follow the discovery → gap analysis → healing → implementation → documentation process religiously!**
