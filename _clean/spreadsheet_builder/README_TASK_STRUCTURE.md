# RowCol MVP Task Structure

**Updated:** October 17, 2025  
**Structure:** Focused, modular task documents organized by phase

---

## **Document Organization**

We've separated the monolithic `ROWCOL_MVP_BUILD_PLAN.md` into focused, executable task documents to improve clarity and agent efficiency.

### **High-Level Overview**
- **`ROWCOL_MVP_BUILD_PLAN.md`** - Strategic overview, phases, success metrics (reference document)

### **Executable Tasks - Ready for Implementation**
- **`E0_PHASE_0_PORTING_AND_INTEGRATION.md`** - Foundation tasks (8 focused tasks, ~2 weeks)
- **`E1_PHASE_1_TEMPLATE_SYSTEM.md`** - Core features (5 focused tasks, ~3-4 weeks)

### **Solutioning Tasks - Analysis & Design Work**
- **`S0_NEEDS_SOLUTIONING.md`** - Design tasks requiring discovery (3 solutioning tasks, parallel with phases)

---

## **When to Use Each Document**

### **Start Here: `ROWCOL_MVP_BUILD_PLAN.md`**
- **When:** At the start of a new session or to understand overall strategy
- **Why:** High-level overview, phases, timeline, architecture context
- **Length:** ~80 lines (executive summary focused)
- **Time:** 5-10 minutes to read

### **Phase 0: `E0_PHASE_0_PORTING_AND_INTEGRATION.md`**
- **When:** Ready to start implementation (first two weeks)
- **Why:** Detailed tasks for porting models/services, updating imports, verification
- **Structure:** 8 executable tasks (E0.1 through E0.8)
- **Time:** ~15 minutes per task to execute
- **What:** Porting selective components from legacy code, setting up foundation

### **Phase 1: `E1_PHASE_1_TEMPLATE_SYSTEM.md`**
- **When:** Ready to build template system (weeks 3-6)
- **Why:** Detailed tasks for classification service, template renderer, API endpoints
- **Structure:** 5 executable tasks (E1.1 through E1.5)
- **Time:** ~30 minutes per task to execute
- **What:** Building the core template system using ported components

### **Design Work: `S0_NEEDS_SOLUTIONING.md`**
- **When:** Need to plan strategy or understand requirements better
- **Why:** Design tasks requiring discovery and analysis
- **Structure:** 3 solutioning tasks (S0.1, S0.2, S0.3)
- **Time:** 1-3 days per solutioning task (discovery + analysis + design)
- **What:** Multi-client pilot strategy, data quality metrics, learning loop design

---

## **Task Naming Convention**

### **Executable Tasks: `E[Phase]_[Name].md`**
- **E0** = Phase 0 tasks (Porting and Integration)
- **E1** = Phase 1 tasks (Template System)
- **E2** = Phase 2 tasks (Advanced Features) - planned for future
- Within each document: **E0.1**, **E0.2**, etc.

### **Solutioning Tasks: `S[Set]_[Name].md`**
- **S0** = First set of solutioning tasks
- Within document: **S0.1**, **S0.2**, etc.

---

## **Recommended Reading Order**

### **First Time (Understanding the Plan)**
1. `ROWCOL_MVP_BUILD_PLAN.md` (5-10 min)
   - Get strategic overview
   - Understand phases and timeline
2. `E0_PHASE_0_PORTING_AND_INTEGRATION.md` intro (10 min)
   - Understand foundation work
   - See task structure

### **Ready to Build (Phase 0)**
1. `E0_PHASE_0_PORTING_AND_INTEGRATION.md` full (30-45 min)
   - Read entire document for context
   - Understand all 8 tasks
2. Execute tasks in order: E0.1 → E0.2 → E0.3 → E0.4 → E0.5 → E0.6 → E0.7 → E0.8
3. Verify Phase 0 complete

### **Ready to Build (Phase 1)**
1. `E1_PHASE_1_TEMPLATE_SYSTEM.md` full (30-45 min)
   - Read entire document for context
   - Understand all 5 tasks
2. Execute tasks in order: E1.1 → E1.2 → E1.3 → E1.4 → E1.5
3. Verify Phase 1 complete

### **Need Strategy (Parallel or Planning)**
1. `S0_NEEDS_SOLUTIONING.md` full (20 min)
   - Understand what needs designing
   - Start with S0.1 (Multi-Client Pilot Strategy)

---

## **Critical Execution Order (Dependencies)**

### **Why Order Matters**
Some tasks have dependencies that must be respected to avoid blockers and ensure smooth execution.

### **Optimal Execution Sequence**
```
E0.1-E0.8 (Phase 0 porting) 
    ↓
S0.2 (Data Quality Metrics) - BLOCKER for E1.4
    ↓  
E1.1-E1.3 (Template system core)
    ↓
E1.4 (API endpoints) - now has data quality metrics
    ↓
S0.1 (Multi-client pilot strategy) - validate on new client
    ↓
E1.5 (Multi-client pilot validation) - now has strategy + metrics
    ↓
E2+ (Future phases with S0.3 learning loop)
```

### **Key Dependencies Explained**

**S0.2 (Data Quality Metrics) is a BLOCKER for E1.4:**
- E1.4 requires `/businesses/{business_id}/data-quality` endpoint
- This endpoint needs specific metrics (total_transactions, matched_transactions, data_quality_score, etc.)
- Without S0.2, we don't know what metrics to calculate or how to calculate them

**S0.1 (Multi-Client Pilot Strategy) is needed for E1.5:**
- E1.5 success criteria requires "Data quality metrics > 80% across segments"
- S0.1 defines how to validate across different client types
- Mission First is all nonprofit - we need strategy for testing other client types

**S0.3 (Learning Loop) is correctly positioned post-MVP:**
- This is the "Spreadsheet with Macros" learning loop
- It's in Phase 3 of the Build Plan (Learning System Implementation)
- Not a blocker to core execution tasks
- Can be deferred until we have working template generation

---

## **Document Size & Scope**

### **Why We Split the Documents**

**Old Approach (Monolithic):**
- Single `ROWCOL_MVP_BUILD_PLAN.md`
- 1,300+ lines
- Mixed strategic + detailed execution
- Boilerplate + implementation code
- Hard for agents to manage context
- Risk of missing important details

**New Approach (Focused):**
- `ROWCOL_MVP_BUILD_PLAN.md` - 80 lines (strategy only)
- `E0_PHASE_0_PORTING_AND_INTEGRATION.md` - 600 lines (8 concrete tasks)
- `E1_PHASE_1_TEMPLATE_SYSTEM.md` - 700 lines (5 concrete tasks)
- `S0_NEEDS_SOLUTIONING.md` - 400 lines (3 design tasks)
- **Total:** Same information, much better organized

### **Benefits of This Structure**

✅ **Agent Efficiency:** Each doc fits in context window, reads completely  
✅ **Clarity:** Clear separation of strategy vs execution vs design  
✅ **Maintainability:** Update individual phase without breaking others  
✅ **Parallelization:** Multiple agents can work on different phases  
✅ **Reference:** Easy to find specific phase or task  
✅ **Boilerplate:** Minimal repetition across documents  

---

## **How Tasks Are Structured**

### **Each Executable Task Contains**
```
Task Name (E[Phase].[Number])
├── Status & Metadata (Priority, Duration, Dependencies)
├── Problem Statement
├── Solution Overview
├── Critical Assumption Validation
├── Discovery Commands (What to search for)
├── Porting/Implementation Process
├── Verification Commands (How to verify it works)
├── Definition of Done
└── Git Commit Instructions
```

### **Each Solutioning Task Contains**
```
Task Name (S[Set].[Number])
├── Status & Metadata (Priority, Phase)
├── Problem Statement
├── Solutioning Mindset (What needs to be figured out)
├── Discovery Phase Checklist
├── Analysis Phase Checklist
├── Design Phase Checklist
├── Documentation Phase Checklist
└── Completion Criteria
```

---

## **Progress Tracking**

### **Update Status as You Go**

In each document, update task status:
```markdown
**Status:** `[ ]` Not started  → `[🔄]` In progress  → `[✅]` Complete
```

### **Mark Completion**
```markdown
- [x] Task completed
- [ ] Task pending
```

### **Document Findings**
Each executable task has "Definition of Done" checklist:
- Mark items complete as you finish them
- Note any issues or edge cases discovered
- This becomes the basis for the next task

---

## **Switching Between Tasks**

### **Moving from Phase 0 → Phase 1**
1. Verify all Phase 0 success criteria met
2. Close Phase 0 document
3. Open `E1_PHASE_1_TEMPLATE_SYSTEM.md`
4. Read all 5 tasks to understand dependencies
5. Execute in order: E1.1 → E1.2 → E1.3 → E1.4 → E1.5

### **Starting Solutioning Work**
1. Open `S0_NEEDS_SOLUTIONING.md`
2. Read solutioning task fully
3. Follow discovery → analysis → design → documentation process
4. Create new executable task document when solution is complete

---

## **Key Resources**

### **Architecture Context (Read Once)**
- `_clean/architecture/comprehensive_architecture.md` - System architecture
- `_clean/architecture/ADR-005-qbo-api-strategy.md` - QBO strategy

### **Product Context (Read Once)**
- `_clean/mvp/mvp_comprehensive_prd.md` - MVP PRD

### **Recovery Context (Reference as Needed)**
- `_clean/strangled_fig/migration_manifest.md` - Strangled fig process
- `_clean/strangled_fig/stepped_plan.md` - Detailed roadmap

---

## **Best Practices**

### **When Starting a Task**
1. ✅ Read the entire section (5-10 min)
2. ✅ Run discovery commands
3. ✅ Read broader context in referenced files
4. ✅ Ask clarifying questions if unclear
5. ✅ Then execute

### **When Executing**
1. ✅ Do it in discrete chunks (1-2 hours)
2. ✅ Verify as you go
3. ✅ Update status in document
4. ✅ Test each change
5. ✅ Commit frequently

### **When Complete**
1. ✅ Mark Definition of Done items
2. ✅ Run verification commands
3. ✅ Commit final changes
4. ✅ Move to next task
5. ✅ Update this README if structure changes

---

## **Adding New Phases**

When you're ready for Phase 2, 3, etc.:

1. Create new document: `E2_PHASE_2_ADVANCED_FEATURES.md`
2. Follow same structure as E0/E1
3. Update `ROWCOL_MVP_BUILD_PLAN.md` Phase 2 section
4. Update this README with new document
5. Link to dependencies in new tasks

---

## **Questions?**

If something is unclear:
1. Check the solutioning tasks (`S0_NEEDS_SOLUTIONING.md`) for design work
2. Check the specific phase document for context
3. Refer back to `ROWCOL_MVP_BUILD_PLAN.md` for strategic overview
4. Read architecture documents for system design questions

**Remember:** The goal is to make each document as focused and useful as possible while maintaining comprehensive coverage of all work needed.
