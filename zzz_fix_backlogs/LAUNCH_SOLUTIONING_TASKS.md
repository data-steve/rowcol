# Launch Solutioning Tasks - Context & Mindset

*This file provides the context and mindset needed for solutioning tasks. The actual solutioning work is defined in the individual task documents.*

## **Quick Start**
1. **Read Architecture Context** (below) - understand system patterns
2. **Navigate**: `cd ~/projects/oodaloo`
3. **Activate**: `poetry shell` (one-time)
4. **Create Branch**: `git checkout -b solutioning/[task-name]`
5. **Start App**: `uvicorn main:app --reload` (keep running)
6. **Execute**: Follow the specific solutioning task document

## **Architecture Context**

### **Core System Patterns:**
- **Domain Services** (`domains/*/services/`): Business logic + CRUD operations
- **Runway Services** (`runway/`): Product orchestration and user experiences
- **Infrastructure Services** (`infra/`): Cross-cutting concerns (auth, database, external APIs)
- **Two-Layer Architecture**: `domains/` for business primitives, `runway/` for product features

### **Key Principles:**
- **Service Boundaries**: Clear separation between domain operations and product orchestration
- **Single Responsibility**: Each service has one clear purpose
- **Dependency Direction**: Runway depends on domains, not vice versa
- **Tenant Awareness**: All services filter by `business_id` for multi-tenancy

## **What This Launch Doc Provides**

### **What Solutioning Task Docs Already Have:**
- Discovery commands to find all related code
- Analysis questions that need to be answered
- Architecture decisions that need to be made
- Progress tracking and status updates

### **What This Launch Doc Adds:**
- **System context** to understand the architecture
- **Solutioning mindset** for approaching complex problems
- **Document creation guidelines** for when to create new docs
- **Success criteria** for knowing when you're done

## **Solutioning Mindset**

### **The Core Problem:**
Solutioning tasks are complex and ambiguous. They require discovery, analysis, and design before they can be executed. **Don't rush to solutions.**

### **The Solutioning Approach:**
1. **Discover what actually exists** - don't assume task descriptions are accurate
2. **Analyze gaps and patterns** - understand what's missing or unclear
3. **Design solutions that fit** - create approaches that work with the current system
4. **Document executable tasks** - convert solutions to hands-free implementation tasks

### **Key Principles:**
- **Validate assumptions** - test every assumption against reality
- **One problem per solutioning doc** - keep complexity contained
- **Document everything** - write down what you find vs what you assumed
- **Focus deeply** - don't try to solve multiple problems at once

## **Document Creation Guidelines**

### **When to Create New Docs:**
- Try to work as much as you can in the solution doc where you started. We're currently doing one solution-oriented task per doc for this reason. 
- **All discovery, analysis, and untangling stays in that doc**
- If a truly complex problem disentangles into a separate requirement set, it may make sense to pull that off and put in a separate solutioning task for later. 
- Otherwise when tasks get disentangled to the point the become truly "hands free" executable, they should be added to the executable task list following that task-types template pattern... or if its trulier compact enough to quickly implement, just do it then if it doesn't take thread too far off base from the solutioning task focus.

### **When NOT to Create New Docs:**
- **During execution phase** - executable tasks should be hands-free
- **For simple questions** - use the existing solutioning doc
- **For minor clarifications** - add to existing progress doc

## **Success Criteria**

### **You're Done When:**
- **Discovery complete** - all commands run, all files read, all assumptions validated
- **Analysis complete** - current state mapped, gaps identified, patterns found
- **Solution designed** - clear implementation approach with dependencies mapped
- **Documentation complete** - executable tasks created with specific patterns
- **No "figure out" language** - everything is specific and actionable
- **Verification defined** - specific commands to test success

---

## **TASK LIST GOES HERE**

*Attach your specific solutioning task list to this file*

**⚠️ IMPORTANT: These tasks require analysis and solution work - do not attempt hands-free execution!**
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

