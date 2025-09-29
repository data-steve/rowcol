# Launch Solutioning Tasks - Comprehensive Framework

*This file contains the complete solutioning methodology for tackling complex tasks that require analysis, discovery, and solution design*

## **CRITICAL: Read This Twice Before Starting**

This framework exists because solutioning is fundamentally different from execution. You will be given tasks that require discovery, analysis, and design work before they can be executed. **DO NOT RUSH TO SOLUTIONS.** Follow this process religiously to avoid the mistakes that have been made before.

## **CRITICAL: Read These Files First**

Before starting any solutioning tasks, you MUST read these files to understand the system:

### **Architecture Context:**
- `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Complete system architecture
- `docs/build_plan_v5.md` - Current build plan and phase context
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy
- `docs/architecture/ADR-003-multi-tenancy-strategy.md` - Multi-tenancy patterns
- `DEVELOPMENT_STANDARDS.md` - Development standards and anti-patterns

### **Solutioning Context:**
- Review the specific solutioning task document for additional context
- Understand the current phase and architectural constraints
- Familiarize yourself with the codebase structure and patterns

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

#### **CRITICAL: Assumption Validation Framework**

**NEVER start solutioning without validating assumptions against reality.**

**Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

**Discovery Documentation Template:**
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

**Validation Process:**
1. **From a basic grep, search recursively outward** in that file until you understand what that code was intended to help with
2. **Then you will understand what the fix actually needs to be** beyond simplistic search and replace
3. **With that understanding you can compare it** to your understanding of broader task and ADRs, building plan etc
4. **Document mismatches** between task assumptions and code reality
5. **Plan solutions based on reality** not assumptions

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

**CRITICAL: Recursive Discovery/Triage Pattern**

**NEVER do blind search-and-replace!** This pattern prevents costly mistakes during discovery:

1. **Search for all occurrences** of the pattern you need to understand
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine what it actually does vs what you assumed:
   - What is this method's real purpose?
   - What are its dependencies and relationships?
   - What would break if you changed it?
   - Is this a false positive or actually relevant?
4. **Map the real system** - understand how things actually work vs how you assumed they work
5. **Document assumptions vs reality** - write down what you found vs what you assumed
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
# - What did we assume vs what actually exists?
# - What patterns are we seeing?
# - What needs to be designed vs what can be fixed?
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

## **Todo List Management (MANDATORY)**

### **For Each Task:**
1. **Create Cursor Todo:** When starting analysis, create a todo in Cursor
2. **Update Todo Status:** As analysis progresses, update todo status
3. **Add Discovery Todos:** For discovered issues, add discovery todos
4. **Complete Todos:** Mark todos complete when analysis is done
5. **Clean Up Todos:** Remove obsolete todos when analysis is complete

### **Todo Status Mapping:**
- `[ ]` Not started → Todo: "Not Started"
- `[🔄]` In progress → Todo: "In Progress"
- `[🔍]` Analysis phase → Todo: "Analysis"
- `[💡]` Solution identified → Todo: "Solution Ready"
- `[✅]` Solution documented → Todo: "Complete"
- `[❌]` Blocked/Need help → Todo: "Blocked"

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

## **Working Relationship Guidelines**

### **Solutioning Phase Role**
- **Principal Architecture**: Drive technical architecture decisions and design solutions
- **Technical Co-founder Support**: Provide conviction, direction, and support for architectural choices
- **Self-Sufficient Analysis**: Answer questions through discovery before asking for help
- **Solution Design**: Create clear, executable solutions for junior dev implementation

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
