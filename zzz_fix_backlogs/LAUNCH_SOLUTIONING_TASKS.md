# Launch Solutioning Tasks - Comprehensive Framework

*This file contains the complete solutioning methodology for tackling complex tasks that require analysis, discovery, and solution design*

## **CRITICAL: Read This Twice Before Starting**

This framework exists because solutioning is fundamentally different from execution. You will be given tasks that require discovery, analysis, and design work before they can be executed. **DO NOT RUSH TO SOLUTIONS.** Follow this process religiously to avoid the mistakes that have been made before.

## **Context for All Solutioning Tasks**

### **What is Solutioning?**
Solutioning is the process of taking complex, ambiguous problems and turning them into clear, executable tasks. Unlike execution tasks that are ready to implement, solutioning tasks require:

- **Discovery work** - understanding what actually exists vs what you assume
- **Analysis work** - identifying gaps, patterns, and relationships  
- **Design work** - creating solutions that fit the current system
- **Documentation work** - converting solutions into executable tasks

### **Why This Process Exists**
Complex software problems have dependencies, assumptions, and unknowns that must be discovered before solutions can be designed. Rushing to solutions without proper discovery leads to:
- Wrong assumptions about what exists
- Solutions that don't fit the current system
- Wasted effort on problems that don't exist
- Breaking things that were working

### **The Solutioning Mindset**
- **Be curious, not judgmental** - discover what exists before deciding what to fix
- **Validate assumptions** - test every assumption against reality
- **Trust the process** - don't skip steps or rush to solutions
- **Document everything** - write down what you find vs what you assumed
- **One task at a time** - focus deeply on each problem

## **The Solutioning Process**

### **Phase 0: Mandatory Discovery and Assumption Validation**

**BEFORE doing any analysis or design work, you MUST complete discovery:**

1. **Read the task completely** - understand what it's trying to solve
2. **Run ALL discovery commands** - don't skip any, even if they seem obvious
3. **Read ALL files listed in "Files to Read First"** - don't assume you know what's in them
4. **Answer ALL "Required Analysis" questions** - don't skip any questions
5. **Document what actually exists** - write down what you find vs what the task assumes
6. **Validate every assumption** - test if things actually exist before proceeding

**Discovery Commands (Run ALL of them):**
```bash
# Find all references to understand usage
grep -r "pattern" . --include="*.py"

# Understand file relationships  
find . -name "*.py" -exec grep -l "pattern" {} \;

# Check current imports
grep -r "import.*pattern" . --include="*.py"

# Test current state
uvicorn main:app --reload
pytest
```

**Discovery Documentation Template:**
```
## Discovery Findings for [Task Name]

### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Files That Need Updates:
- [List files that need changes based on discovery]

### Dependencies Discovered:
- [List dependencies that weren't obvious]
```

### **Phase 1: Analysis and Gap Identification**

**Only after discovery is complete:**

1. **Map current system state** - understand how things actually work
2. **Identify gaps** - what's missing or unclear
3. **Find patterns** - look at similar solutions in codebase
4. **Understand relationships** - how different parts connect
5. **Document findings** - write down what you learned

### **Phase 2: Solution Design**

**Only after analysis is complete:**

1. **Design solution** - create clear implementation plan
2. **Map dependencies** - understand what needs to be done first
3. **Create patterns** - design reusable approaches
4. **Plan verification** - how to test the solution works
5. **Document solution** - write down the complete approach

### **Phase 3: Solution Documentation**

**Only after design is complete:**

1. **Create executable task list** - convert solution to hands-free tasks
2. **Write specific patterns** - provide code examples and patterns
3. **Define verification steps** - specific commands to test success
4. **Map dependencies** - clear order of execution
5. **Update task status** - mark as complete

## **Progress Tracking**

- `[ ]` - Not started
- `[🔄]` - In progress (discovery phase)
- `[🔍]` - Analysis phase (after discovery complete)
- `[💡]` - Solution identified (ready to implement)
- `[✅]` - Solution documented (ready for executable phase)
- `[❌]` - Blocked/Need help

**IMPORTANT**: Always update the task status in the document as you work through tasks. This allows tracking progress and identifying which solutions are complete.

## **Solutioning Checklist**

### **Discovery Phase (MANDATORY):**
- [ ] **All discovery commands run** - no shortcuts, no assumptions
- [ ] **All files read** - understand what actually exists
- [ ] **All analysis questions answered** - don't skip any
- [ ] **Assumptions validated** - test every assumption against reality
- [ ] **Current state documented** - write down what you found

### **Analysis Phase:**
- [ ] **Current state mapped** - understand how things work
- [ ] **Gaps identified** - what's missing or unclear
- [ ] **Patterns found** - look at similar solutions
- [ ] **Relationships understood** - how parts connect
- [ ] **Findings documented** - write down what you learned

### **Design Phase:**
- [ ] **Solution designed** - clear implementation approach
- [ ] **Dependencies mapped** - what needs to be done first
- [ ] **Patterns created** - reusable approaches
- [ ] **Verification planned** - how to test success
- [ ] **Solution documented** - complete approach written down

### **Documentation Phase:**
- [ ] **Executable tasks created** - hands-free implementation tasks
- [ ] **Specific patterns provided** - code examples and patterns
- [ ] **Verification steps defined** - specific commands to test
- [ ] **Dependencies mapped** - clear execution order
- [ ] **Task status updated** - marked as complete

## **Common Analysis Commands**

```bash
# Find all references to understand usage
grep -r "pattern" . --include="*.py"

# Understand file relationships
find . -name "*.py" -exec grep -l "pattern" {} \;

# Check current imports
grep -r "import.*pattern" . --include="*.py"

# Test current state
uvicorn main:app --reload
pytest

# Check for specific patterns
grep -r "get_.*_for_digest" . --include="*.py"
grep -r "SmartSyncService" . --include="*.py"
grep -r "QBODataService" . --include="*.py"
```

## **Definition of Done for Solutioning**

- **Discovery complete** - all commands run, all files read, all assumptions validated
- **Analysis complete** - current state mapped, gaps identified, patterns found
- **Solution designed** - clear implementation approach with dependencies mapped
- **Documentation complete** - executable tasks created with specific patterns
- **No "figure out" language** - everything is specific and actionable
- **Verification defined** - specific commands to test success
- **Success criteria defined** - measurable outcomes

## **After Solution is Documented**

1. **Create executable task list** - convert solution to hands-free tasks
2. **Archive solution work** - move to `archive/solutions/` directory  
3. **Hand off to executable phase** - use LAUNCH_EXECUTABLE_TASKS.md

## **Critical Success Factors**

- **Trust the process** - don't rush to solutions, follow the phases
- **Validate assumptions** - test every assumption against reality
- **Document everything** - write down what you find vs what you assumed
- **One task at a time** - focus deeply on each problem
- **Be confident** - you need to not rush and trust the process

---

## **TASK LIST GOES HERE**

*Attach your specific solutioning task list to this file*

**⚠️ IMPORTANT: These tasks require analysis and solution work - do not attempt hands-free execution!**

**⚠️ CRITICAL: Follow the discovery → analysis → design → document process religiously!**
