# Task Building Template

*Template for curating tasks by complexity into Executable, Needs Solving, and Blocked categories*

## **Overview**

This template documents the process for taking raw task backlogs and curating them into three categories based on complexity and readiness for execution.

## **Task Categories**

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
- Task details with:
  - Status, Priority, Justification
  - Specific Files to Fix
  - Search Commands to Run
  - Required Imports/Changes
  - Pattern to Implement (with code examples)
  - Dependencies
  - Verification Commands
  - Definition of Done
- **Progress Tracking Instructions** - Clear steps for updating task status as work progresses
- **Git Workflow Instructions** - Surgical commit steps for each task

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
- Task details with:
  - Status, Priority, Justification
  - Code Pointers
  - Current Issues to Resolve
  - Required Analysis
  - Dependencies
  - Verification
  - Definition of Done
  - Solution Required (what needs to be figured out)
- **Progress Tracking Instructions** - Clear steps for updating task status as analysis progresses

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

### **Step 2: Categorize by Complexity**
For each task, ask:
- **Is this fully solved?** → Executable
- **Does this need analysis work?** → Needs Solving
- **Is this blocked by other tasks?** → Blocked

### **Step 3: Preserve All Detail**
- **Lift and shift** - don't edit or simplify
- Preserve all critical warnings, search commands, verification steps
- Keep all implementation patterns and code examples
- Maintain all context and justification

### **Step 4: Create Curated Files**
1. Create `0_EXECUTABLE_TASKS.md` with fully-solved tasks
2. Create `1_NEEDS_SOLVING_TASKS.md` with analysis tasks
3. Create `2_BLOCKED_TASKS.md` with blocked tasks
4. Archive original files

### **Step 5: Clean Up**
- Remove "spec" and "agent" references
- Remove "Ready for Spec" status
- Update "Next Action" to point to next task
- Ensure consistent formatting

## **Quality Checklist**

### **Executable Tasks**
- [ ] Clear implementation patterns with code examples
- [ ] Specific files to fix with exact changes
- [ ] Complete verification steps
- [ ] No "figure out" language
- [ ] Ready for hands-free execution
- [ ] **Progress tracking instructions included**
- [ ] **Git workflow instructions included**

### **Needs Solving Tasks**
- [ ] Clear analysis requirements
- [ ] "Figure out" or "determine" language present
- [ ] Dependencies clearly identified
- [ ] Solution Required section explains what needs to be figured out
- [ ] **Progress tracking instructions included**

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
- **Specific Files to Fix:**
  - `file1.py` - [specific change needed]
  - `file2.py` - [specific change needed]
- **Search Commands to Run:**
  - `grep -r "pattern" path/`
- **Required Imports/Changes:**
  - Remove: `old_import`
  - Add: `new_import`
- **Pattern to Implement:**
  ```python
  # Code example here
  ```
- **Dependencies:** [List any dependencies]
- **Verification:** 
  - Run `command1` - should return X
  - Run `command2` - should return Y
- **Definition of Done:**
  - [Specific outcome 1]
  - [Specific outcome 2]
- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed
- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add [specific-files-modified]`
  - `git commit -m "feat: [task-description] - [brief-summary]"`
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
- **Current Issues to Resolve:**
  - [Issue 1]
  - [Issue 2]
- **Required Analysis:**
  - [What needs to be figured out]
- **Dependencies:** [List any dependencies]
- **Verification:** 
  - [How to verify the solution works]
- **Definition of Done:**
  - [What the solution should achieve]
- **Solution Required:** [What needs to be figured out]
- **Progress Tracking:**
  - Update status to `[🔄]` when starting analysis
  - Update status to `[💡]` when solution is identified
  - Update status to `[✅]` when solution is documented
  - Update status to `[❌]` if blocked or need help
```

## **File Naming Convention**

- `0_EXECUTABLE_TASKS.md` - Ready for execution
- `1_NEEDS_SOLVING_TASKS.md` - Need analysis work
- `2_BLOCKED_TASKS.md` - Blocked by dependencies
- `backlog/` - Original backlogs for future curation

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

## **Updates to This Template**

As we discover issues or improvements in the curation process, update this template to capture the learnings for future use.