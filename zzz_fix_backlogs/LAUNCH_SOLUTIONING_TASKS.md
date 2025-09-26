# Launch Solutioning Tasks - Reusable Recipe

*This file contains the standard instructions for tackling tasks that need analysis and solution work*

## **Quick Start**

1. **Create Branch**: `git checkout -b solution/[task-name]`
2. **Work One Task at a Time**: Focus on single task until fully solved
3. **Document Solution**: Create executable task list when solution is complete
4. **Archive When Done**: Move completed task file to `archive/` when solution is documented

## **Progress Tracking**

- `[ ]` - Not started
- `[🔄]` - In progress (analysis phase)
- `[💡]` - Solution identified (ready to implement)
- `[✅]` - Solution documented (ready for executable phase)
- `[❌]` - Blocked/Need help

**IMPORTANT**: Always update the task status in the document as you work through tasks. This allows tracking progress and identifying which solutions are complete.

## **Solutioning Pattern**

### **For Each Task:**
1. **Read the problem statement** - understand what needs to be figured out
2. **Analyze existing code** - understand current state and relationships
3. **Identify gaps** - what's missing or unclear
4. **Research patterns** - look at similar solutions in codebase
5. **Design solution** - create clear implementation plan
6. **Document solution** - create executable task list with specific patterns
7. **Validate solution** - ensure it can be executed hands-free
8. **Update status in document** - change `[ ]` to `[✅]` when solution is complete

### **Definition of Done for Solutioning:**
- **Clear problem statement** - what exactly needs to be solved
- **Specific files to modify** - exact files and changes needed
- **Implementation patterns** - code examples and patterns to follow
- **Verification steps** - specific commands to test success
- **No "figure out" language** - everything is specific and actionable
- **Dependencies mapped** - clear order of execution
- **Success criteria** - measurable outcomes

### **After Solution is Documented:**
1. **Create executable task list** - convert solution to hands-free tasks
2. **Archive solution work** - move to `archive/solutions/` directory
3. **Hand off to executable phase** - use LAUNCH_EXECUTABLE_TASKS.md

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
```

## **Solutioning Checklist**

- [ ] **Problem clearly defined** - no ambiguity about what needs to be solved
- [ ] **Current state analyzed** - understand existing code and relationships
- [ ] **Gaps identified** - what's missing or unclear
- [ ] **Solution designed** - clear implementation approach
- [ ] **Patterns documented** - specific code examples provided
- [ ] **Verification defined** - specific test commands provided
- [ ] **Dependencies mapped** - clear execution order
- [ ] **Success criteria defined** - measurable outcomes
- [ ] **No "figure out" language** - everything is specific and actionable

## **Blocking Analysis**

Before starting solutioning work, identify:
- **What executable tasks are blocked** by this solutioning work?
- **What's the minimum viable solution** to unblock those tasks?
- **What's the complete solution** for full functionality?
- **What can be done incrementally** vs what needs to be done all at once?

---

## **TASK LIST GOES HERE**

*Attach your specific solutioning task list to this file*

**⚠️ IMPORTANT: These tasks require analysis and solution work - do not attempt hands-free execution!**
