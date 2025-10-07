# Task Building Template - RowCol QBO MVP

*Streamlined template for creating executable and solutioning tasks with self-healing discovery*

## **Quick Start**

1. **Read Architecture Context** (below) - understand system patterns
2. **Navigate**: `cd ~/projects/rowcol`
3. **Activate**: `poetry shell` (one-time)
4. **Create Branch**: `git checkout -b feature/[task-name]`
5. **Start App**: `uvicorn main:app --reload` (keep running)
6. **Execute**: Follow the task-specific process

## **Architecture Context (Required for All Tasks)**

### **Core System Architecture:**
- `docs/architecture/comprehensive_architecture_multi_rail.md` - Complete system architecture
- `docs/build_plan/rowcol_financial_control_plane_e2e.md` - E2E build plan and phase context
- `docs/build_plan/QBO_MVP_ROADMAP.md` - QBO MVP focus and current phase
- `infra/config/feature_gates.py` - Feature gating system
- `infra/config/rail_configs.py` - Rail-specific configurations

### **Current Phase Context (QBO MVP Focus):**
- **Phase 0.5**: QBO-only MVP (current focus)
- **Feature Gating**: QBO-only mode enabled, Ramp/Plaid/Stripe disabled
- **Payment Execution**: QBO sync-only (no execution), Ramp execution gated
- **Reserve Management**: Disabled in QBO-only mode
- **Multi-rail Architecture**: Ready for future phases

### **Core System Patterns:**
- **Domain Services** (`domains/*/services/`): Business logic + CRUD operations
- **Runway Services** (`runway/`): Product orchestration and user experiences
- **Infrastructure Services** (`infra/`): Cross-cutting concerns (auth, database, external APIs)
- **Two-Layer Architecture**: `domains/` for business primitives, `runway/` for product features
- **Tenant Awareness**: All services filter by `business_id` for multi-tenancy

## **Task Categories**

### **Task Naming Convention**

**Executable Tasks**: `E01_[MEANINGFUL_NAME].md`
- **E** = Executable (ready for hands-free execution)
- **01** = Sequence number (E01, E02, E03...)
- **MEANINGFUL_NAME** = Key identifier (visible in Cursor @ attachment)

**Solutioning Tasks**: `S01_[MEANINGFUL_NAME].md`
- **S** = Solutioning (needs analysis and design)
- **01** = Sequence number (S01, S02, S03...)
- **MEANINGFUL_NAME** = Key identifier (visible in Cursor @ attachment)

### **Task Granularity Guidelines**

**Executable Tasks (E01_, E02_, E03_...)**:
- **Size**: 2-4 hours of focused work
- **Scope**: One service, one pattern, one feature
- **Dependencies**: Minimal external context needed
- **Ready for**: Hands-free execution with clear patterns

**Solutioning Tasks (S01_, S02_, S03_...)**:
- **Size**: One major architectural problem
- **Scope**: One complex system or integration
- **Dependencies**: Extensive discovery and analysis needed
- **Ready for**: Discovery → Analysis → Design → Documentation

**Decision Tree**:
1. **Can this be completed in 2-4 hours with clear patterns?** → Executable Task (E prefix)
2. **Does this need extensive discovery and analysis?** → Solutioning Task (S prefix)
3. **Is this too big for one task?** → Break into smaller tasks
4. **Is this too small to be meaningful?** → Combine with related tasks

## **Self-Healing Process (MANDATORY)**

### **The Core Problem:**
Build plans and task descriptions are idealized but codebase reality changes as we work. Static audits become stale quickly.

### **The Self-Healing Solution:**
Each task discovers its own reality, heals gaps dynamically, and updates documentation as it works.

### **Key Principles:**
- **Discovery First**: Always understand what actually exists before assuming
- **Gap Healing**: Fix discovered gaps as part of task execution
- **Documentation Updates**: Update build plans based on discovered reality
- **Iterative Refinement**: Each task improves the accuracy of subsequent tasks

### **Self-Healing Process:**

**Phase 1: Discovery & Reality Check (MANDATORY)**
1. **Read Task Description** - Understand what the build plan thinks needs to be done
2. **Discover Current Reality** - Find what actually exists in the codebase
3. **Identify Gaps** - Compare build plan assumptions vs. reality
4. **Heal Gaps** - Fix discovered issues as part of task execution
5. **Update Documentation** - Update build plan based on discovered reality

**Phase 2: Implementation**
1. **Implement the actual task** - Use discovered reality, not assumptions
2. **Heal discovered gaps** - Fix issues found during discovery
3. **Test thoroughly** - Verify everything works
4. **Update documentation** - Keep build plans accurate

### **Discovery Commands Pattern:**
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

### **Gap Healing Process:**
**When Gaps Are Discovered:**
1. **Document the Gap** - What build plan assumed vs. what exists
2. **Assess Impact** - Does this affect the task or future tasks?
3. **Heal Immediately** - Fix the gap as part of current task
4. **Update Build Plan** - Mark assumptions as corrected
5. **Propagate Changes** - Update related tasks that depend on this

### **0_EXECUTABLE_TASKS.md** - Ready for Hands-Free Execution
**Characteristics:**
- Clear implementation patterns with code examples
- Specific files to fix with exact changes needed
- Complete verification steps with pytest commands
- No "figure out" or "analyze" language
- Ready for execution by any developer familiar with the codebase

**Status Format:** `[ ]` Not started

**Required Sections:**
- Context for All Tasks
- Critical Warnings from Painful Lessons
- **CRITICAL: Recursive Discovery/Triage Pattern** - Built into every task
- **Progress Tracking Instructions** - Clear steps for updating task status as work progresses
- Task details with:
  - Status, Priority, Justification
  - **Initial Files to Fix** (starting point, not comprehensive)
  - **MANDATORY: Comprehensive Discovery Commands** (find ALL occurrences)
  - **MANDATORY: Recursive Triage Process** (understand context before changing)
  - **Pattern to Implement** (with code examples) - WHAT you're building
  - **Required Imports/Changes** (what needs to change) - HOW to implement
  - **Dependencies** (what this depends on) - WHAT you need
  - **MANDATORY: Comprehensive Cleanup Requirements** (handle all edge cases) - CLEANUP after implementation
  - Verification Commands
  - Definition of Done
- **Git Workflow Instructions** - Surgical commit steps for each task
- **Todo List Integration** - Cursor todo list management requirements

### **1_NEEDS_SOLVING_TASKS.md** - Needs Analysis and Solution Work
**Characteristics:**
- Analysis and discovery work required
- "Figure out" or "determine" language present
- Dependencies on other solution tasks
- Architectural decisions that need human input
- Cannot be executed without solution phase

**Status Format:** `[ ]` Not started

**Required Sections:**
- Context for All Tasks
- **Progress Tracking Instructions** - Clear steps for updating task status as analysis progresses
- Task details with:
  - Status, Priority, Justification
  - **Code Pointers** (where to look)
  - **MANDATORY: Discovery Commands** (how to find all related code)
  - **Current Issues to Resolve** (what's broken)
  - **Assumption Validation** (what assumptions need to be tested)
  - **Required Analysis** (what needs to be figured out)
  - **Architecture Analysis** (how this fits with existing patterns)
  - **Solution Design Process** (step-by-step approach to solving)
  - **Dependencies** (what this depends on)
  - **Verification** (how to verify the solution works)
  - **Definition of Done** (what the solution should achieve)
  - **Solution Required** (what needs to be figured out)
- **Todo List Integration** - Cursor todo list management requirements

### **2_BLOCKED_TASKS.md** - Blocked by Solution Tasks
**Characteristics:**
- Ready for hands-free execution (same complexity as executable tasks)
- Blocked by solution tasks that need to be completed first
- Will become executable once dependencies are resolved

**Status Format:** `[ ]` Not started

**Required Sections:**
- Context for Blocked Tasks
- Blocking Analysis
- Resolution Path
- Summary

## **Curation Process**

### **Step 1: Read and Understand**
1. Read the original backlog completely
2. Understand the context and goals
3. Identify all tasks and their current state

### **Step 2: Add Required Context Documentation**
1. Add "Read These Files First" section to each task document
2. Include the 5 required architecture context files
3. Add task-specific context files as needed
4. Ensure all context files are accessible and relevant

### **Step 3: Categorize by Complexity**
For each task, ask:

#### **Executable Task Gatekeeping Questions:**
- **Is this fully solved?** (Clear implementation pattern exists)
- **Are ALL files identified?** (Not just initial files, but comprehensive discovery commands provided)
- **Is the recursive triage process defined?** (Understand context before changing)
- **Are cleanup requirements comprehensive?** (Handle all edge cases, not just basic changes)
- **Is there NO "figure out" language?** (Everything is specific and actionable)
- **Can any developer execute this?** (No additional context needed)

**If ANY answer is NO → Needs Solving**

#### **Needs Solving Task Gatekeeping Questions:**
- **Does this need analysis work?** (Discovery, understanding, design required)
- **Is there "figure out" or "determine" language?** (Indicates unknowns)
- **Are there architectural decisions needed?** (Requires human input)
- **Are dependencies unclear?** (Need to map relationships)
- **Does the solution need to be designed?** (Not just implemented)

**If ANY answer is YES → Needs Solving**

#### **Blocked Task Gatekeeping Questions:**
- **Is this ready for execution?** (Same complexity as executable tasks)
- **Is it blocked by solution tasks?** (Dependencies need to be resolved first)
- **Will it become executable once unblocked?** (No additional analysis needed)

**If ALL answers are YES → Blocked**

#### **Document Creation Gatekeeping Questions:**
When you discover a new issue during task curation, ask:

**For Solutioning Tasks:**
- **Is this a major architectural problem?** (Requires extensive discovery/analysis)
- **Does this intersect with multiple systems?** (Complex untangling needed)
- **Is this a standalone problem?** (Can be contained in one solutioning doc)
- **Does this need its own solutioning thread?** (Too complex to add to existing task)

**If YES to any → Create new solutioning task**

**For Executable Tasks:**
- **Is this a simple implementation issue?** (Can be added to existing task)
- **Is this a discovery finding?** (Add to task document, don't create new doc)
- **Is this a verification step?** (Add to task document)

**If YES to any → Add to existing executable task, NO new docs**

### **CRITICAL: Architectural Decision Promotion**

**When to Promote Working Docs to ADRs:**
- **Architectural decisions are stable** - no more changes expected
- **Patterns are proven** - have been implemented and tested
- **Hard won wisdom** - decisions that required significant iteration
- **Reusable patterns** - other developers need to follow these patterns
- **Verification commands exist** - can be automatically checked

**ADR Promotion Process:**
1. **Working doc contains stable architectural decision**
2. **Create ADR-XXX in `docs/architecture/`**
3. **Use ADR template** - status, decision, implementation, examples, verification
4. **Archive working doc** - move to `archive/` folder
5. **Update references** - point to new ADR location

**ADR Template:**
```markdown
# ADR-XXX: [Decision Title]

## Status
- **Date**: YYYY-MM-DD
- **Status**: Proposed/Accepted/Deprecated
- **Context**: [What problem this solves]

## Decision
[What was decided]

## Implementation
[How to implement this pattern]

## Examples
[Code examples showing the pattern]

## Verification
[How to verify this pattern is being followed]

## Related ADRs
- ADR-XXX: [Related decision]
```

### **CRITICAL: Assumption Validation Before Task Curation**

**NEVER curate tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

### **CRITICAL: Recursive Discovery/Triage Pattern**

**NEVER do blind search-and-replace!** This pattern prevents costly mistakes during task curation:

1. **Search for all occurrences** of patterns mentioned in the task
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine what it actually does vs what the task assumes:
   - What is this method's real purpose?
   - What are its dependencies and relationships?
   - What would break if we changed it?
   - Is this a false positive or actually relevant?
4. **Map the real system** - understand how things actually work vs how the task assumes they work
5. **Document assumptions vs reality** - write down what you found vs what the task assumed
6. **Plan based on reality** - design solutions based on what actually exists

**Example Discovery Pattern:**
```bash
# Step 1: Find all occurrences
grep -r "get_.*_for_digest" . --include="*.py"

# Step 2: For each file found, read the broader context
# - What is this method actually doing?
# - What are its real dependencies?
# - How is it being used in practice?
# - What would break if we changed it?

# Step 3: Map the real system
# - How do these pieces actually connect?
# - What are the real data flows?
# - What are the real dependencies?

# Step 4: Document reality vs assumptions
# - What did the task assume vs what actually exists?
# - What patterns are we seeing?
# - What needs to be designed vs what can be fixed?
```

### **Step 4: Preserve All Detail**
- **Lift and shift** - don't edit or simplify
- Preserve all critical warnings, search commands, verification steps
- Keep all implementation patterns and code examples
- Maintain all context and justification

### **Step 5: Create Curated Files**
1. Create `docs/build_plan/working/0_EXECUTABLE_TASKS.md` with fully-solved tasks
2. Create `docs/build_plan/working/1_NEEDS_SOLVING_TASKS.md` with analysis tasks
3. Create `docs/build_plan/working/2_BLOCKED_TASKS.md` with blocked tasks
4. Archive original files to `docs/build_plan/archive/`

### **Step 6: Clean Up**
- Remove "spec" and "agent" references
- Remove "Ready for Spec" status
- Update "Next Action" to point to next task
- Ensure consistent formatting

## **Quality Checklist**

### **All Task Types (MANDATORY)**
- [ ] **Assumption validation completed** - Task assumptions validated against actual codebase
- [ ] **Discovery documentation included** - What actually exists vs what task assumed documented
- [ ] **Architecture mismatches identified** - Current vs intended state gaps documented
- [ ] **Task scope validated** - Tasks solving the right problems, not wrong ones

### **Executable Tasks**
- [ ] Clear implementation patterns with code examples
- [ ] Specific files to fix with exact changes
- [ ] Complete verification steps
- [ ] No "figure out" language
- [ ] Ready for hands-free execution
- [ ] **Progress tracking instructions included**
- [ ] **Git workflow instructions included**
- [ ] **Todo list integration included**
- [ ] **Comprehensive cleanup requirements included**

### **Needs Solving Tasks**
- [ ] Clear analysis requirements
- [ ] "Figure out" or "determine" language present
- [ ] Dependencies clearly identified
- [ ] Solution Required section explains what needs to be figured out
- [ ] **Progress tracking instructions included**
- [ ] **Todo list integration included**
- [ ] **Scratch notes document requirement included**

### **Blocked Tasks**
- [ ] Ready for execution once unblocked
- [ ] Blocking dependencies clearly identified
- [ ] Resolution path outlined

## **Common Patterns**

### **Executable Task Pattern**
```markdown
#### **Task: [Task Name]**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical / P1 High / P2 Medium
- **Justification:** [Why this task is needed]

- **Initial Files to Fix:** (Starting point - NOT comprehensive)
  - `file1.py` - [specific change needed]
  - `file2.py` - [specific change needed]

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find ALL occurrences of the pattern
  grep -r "pattern" . --include="*.py"
  grep -r "related_pattern" . --include="*.py"
  grep -r "import.*pattern" . --include="*.py"
  find . -name "*.py" -exec grep -l "pattern" {} \;
  ```

- **MANDATORY: Recursive Triage Process:**
  1. **For each file found in discovery:**
     - Read the broader context around each occurrence
     - Understand what the method/service/route is doing
     - Determine if it needs simple replacement, contextual update, or complete overhaul
     - Identify all related imports, method calls, and dependencies
  2. **Map the real system:**
     - How do these pieces actually connect?
     - What are the real data flows?
     - What would break if you changed it?
  3. **Plan comprehensive updates:**
     - Update method names AND all calls to those methods
     - Update imports AND all references
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # Code example here - WHAT you're building
  ```

- **Required Imports/Changes:**
  - Remove: `old_import`
  - Add: `new_import`
  - Update: `method_name` → `new_method_name`

- **Dependencies:** [List any dependencies]

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references

- **Verification:** 
  - Run `grep -r "old_pattern" . --include="*.py"` - should return no results
  - Run `grep -r "new_pattern" . --include="*.py"` - should show new usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest` - should pass without import failures

- **Definition of Done:**
  - [Specific outcome 1]
  - [Specific outcome 2]
  - ALL occurrences found and updated (not just initial files)
  - No broken references or imports anywhere
  - Comprehensive cleanup completed

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add [specific-files-modified]`
  - `git commit -m "feat: [task-description] - [brief-summary]"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state

- **Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Remove Obsolete Files:** Delete any files that are no longer needed
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references
  - **Verification Cleanup:** Run cleanup verification commands
```

### **Needs Solving Task Pattern**
```markdown
#### **Task: [Task Name]**
- **Status:** `[ ]` Not started
- **Priority:** P1 High / P2 Medium
- **Justification:** [Why this task is needed]

- **Code Pointers:**
  - `file1.py` - [what to look at]
  - `file2.py` - [what to look at]

- **MANDATORY: Discovery Commands:**
  ```bash
  # Find all related code
  grep -r "related_pattern" . --include="*.py"
  grep -r "import.*related" . --include="*.py"
  find . -name "*.py" -exec grep -l "pattern" {} \;
  ```

- **Current Issues to Resolve:**
  - [Issue 1]
  - [Issue 2]

- **Assumption Validation:**
  - [What assumptions need to be tested against actual codebase]
  - [What might be different from what we think]

- **Required Analysis:**
  - [What needs to be figured out]
  - [What architectural decisions are needed]

- **Architecture Analysis:**
  - [How this fits with existing patterns]
  - [What ADRs apply to this problem]
  - [What services/patterns should be used]

- **Solution Design Process:**
  1. [Step 1: Discovery phase]
  2. [Step 2: Analysis phase]
  3. [Step 3: Design phase]
  4. [Step 4: Documentation phase]

- **Dependencies:** [List any dependencies]

- **Verification:** 
  - [How to verify the solution works]
  - [What tests need to be written]

- **Definition of Done:**
  - [What the solution should achieve]
  - [What documentation needs to be created]

- **Solution Required:** [What needs to be figured out]

- **Progress Tracking:**
  - Update status to `[🔄]` when starting analysis
  - Update status to `[💡]` when solution is identified
  - Update status to `[✅]` when solution is documented
  - Update status to `[❌]` if blocked or need help

- **Todo List Integration:**
  - Create Cursor todo for this task when starting analysis
  - Update todo status as analysis progresses
  - Mark todo complete when solution is documented
  - Add discovery todos for found issues
  - Remove obsolete todos when analysis is complete
  - Ensure todo list reflects current analysis state
```

## **File Naming Convention**

- `docs/build_plan/working/0_EXECUTABLE_TASKS.md` - Ready for execution
- `docs/build_plan/working/1_NEEDS_SOLVING_TASKS.md` - Need analysis work
- `docs/build_plan/working/2_BLOCKED_TASKS.md` - Blocked by dependencies
- `docs/build_plan/archive/` - Original backlogs for future curation

## **Git Workflow**

1. **Create branch:** `git checkout -b curate/[backlog-name]`
2. **Curate tasks:** Create the 3 curated files
3. **Clean up:** Remove spec/agent references
4. **Archive:** Move original files to archive/
5. **Commit:** `git add . && git commit -m "Curate [backlog-name] tasks by complexity"`
6. **Merge:** `git checkout main && git merge curate/[backlog-name]`

## **Success Metrics**

- **Executable Tasks:** Can be executed by any developer without additional context
- **Needs Solving Tasks:** Clear what analysis work is needed
- **Blocked Tasks:** Clear what dependencies need to be resolved
- **No Information Loss:** All detail preserved from original backlogs
- **Clean Formatting:** No spec/agent references, consistent status format
- **Git Workflow:** Clear surgical commit instructions for each task

## **Common Mistakes to Avoid**

- **Don't simplify** - preserve all detail from original
- **Don't edit tasks** - just curate by complexity
- **Don't remove warnings** - they're there for a reason
- **Don't change verification steps** - they're tested and working
- **Don't add new requirements** - just organize existing ones
- **Don't forget git workflow** - surgical commits are essential

## **Critical Lessons Learned**

### **Why Tasks Fail:**
1. **Assumption-Based Planning**: Tasks planned based on assumptions, not reality
2. **Incomplete Discovery**: Tasks list specific files but miss others found during execution
3. **Blind Search-and-Replace**: Changes made without understanding context
4. **Insufficient Cleanup**: Edge cases and dependencies not handled
5. **Missing File Operations**: Using `mv` instead of `cp` then `rm`
6. **No Todo Integration**: Progress not tracked in Cursor todo list
7. **Needless Questions**: Asking questions that can be answered through discovery or analysis

### **Success Patterns:**
1. **Assumption Validation**: Always validate task assumptions against actual codebase
2. **Comprehensive Discovery**: Find ALL occurrences, not just initial files
3. **Recursive Triage**: Understand context before making changes
4. **Comprehensive Cleanup**: Handle all edge cases and dependencies
5. **Proper File Operations**: Use `cp` then `rm` for moves
6. **Todo Integration**: Track progress and discovered edge cases
7. **Self-Sufficient Analysis**: Answer questions through discovery before asking for help

### **Template Requirements:**
- **Every task MUST have assumption validation completed before curation**
- **Every executable task MUST have comprehensive discovery commands**
- **Every executable task MUST have recursive triage process**
- **Every executable task MUST have comprehensive cleanup requirements**
- **Every executable task MUST have todo list integration**
- **Gatekeeping questions MUST be used to distinguish task types**

## **Working Relationship Guidelines**

### **Principal Architecture Role**
- **Technical Co-founder Support**: Provide principal architecture conviction, direction, and support
- **Solutioning Phase**: Drive technical architecture decisions and design solutions
- **Execution Phase**: Hand off "solutioned" problems to junior dev level implementation
- **Code Quality**: Ensure solutions are maintainable by junior-mid level engineers with AI support

### **Anti-Patterns to Avoid**
1. **Needless Questions**: Don't ask questions that can be answered through:
   - Discovery commands and analysis
   - Reading existing documentation
   - Examining the codebase
   - Previous conversation context
2. **Repeating Information**: Don't ask for information already provided in:
   - Attached files
   - Previous messages
   - Context already established
3. **Assumption-Based Questions**: Validate assumptions through discovery before asking questions

### **Effective Question Patterns**
- **Architecture Decisions**: "Do you agree with this approach, or do you see a better way?"
- **Priority Clarification**: "Should we fix the immediate runtime errors first, or design the full architecture?"
- **Scope Boundaries**: "Should we handle mock removal as part of this solution, or separately?"
- **Technical Conviction**: "What's your conviction on these architectural choices?"

### **Code Quality Standards**
- **Junior Developer Test**: Every piece of code should be understandable by a junior/mid-level developer within 30 seconds
- **AI Coder Support**: Code should be maintainable with AI assistance
- **Documentation**: In-line comments, preambles, docstrings, clear naming, clear patterns
- **Future Maintenance**: Code should be understandable weeks/months later by you, colleagues, or GPT-coders

## **Updates to This Template**

As we discover issues or improvements in the curation process, update this template to capture the learnings for future use.