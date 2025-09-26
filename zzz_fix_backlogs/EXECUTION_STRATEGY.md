# ZZZ Fix Backlogs - Execution Strategy

**Date**: 2025-01-27  
**Purpose**: Guide for executing the cleanup backlogs in the correct sequence

## Overview

The `zzz_fix_backlogs/` directory contains well-documented cleanup tasks that are **NOT** compatible with the `@agent/` system. These are markdown-based tasks designed for manual execution with clear patterns and verification steps.

## Key Changes Made

### 1. **Removed "Ready for Spec" Status**
- The `@spec` command was designed for net-new builds requiring detailed technical specifications
- These cleanup tasks already have sufficient detail: files to fix, patterns to implement, verification steps
- Tasks are now ready for direct execution

### 2. **Added Specific Test Verification**
- Each task now references specific pytest commands that should pass
- Examples:
  - `pytest tests/domains/unit/integrations/qbo/` - QBO integration tests
  - `pytest tests/integration/qbo/` - QBO API tests
  - `pytest tests/runway/unit/foundation/test_phase0_qbo.py` - QBO foundation tests

### 3. **Clarified Execution Strategy**
- **Sequential Execution**: Tasks must be run in order due to dependencies
- **No Parallel Execution**: Multiple tasks will collide if run simultaneously
- **Phase-Based**: Phase 1 → Phase 2 → Phase 3 (each phase builds on the previous)

## Execution Workflow

### For Each Task:
1. **Read the task completely** - understand files to fix, patterns to implement
2. **Follow the implementation pattern** - use the provided code examples
3. **Run verification commands** - ensure changes work correctly
4. **Test with pytest** - run the specified test commands
5. **Commit changes** - `git add . && git commit -m "Task: [name] - [summary]"`

### Phase Dependencies:
- **Phase 1**: Fix SmartSync Architecture (3 tasks, must be done in order)
- **Phase 2**: Consolidate Job Infrastructure (2 tasks, depends on Phase 1)
- **Phase 3**: Clean Up Remaining Issues (2 tasks, depends on Phase 2)

## Branch Readiness

The current branch is ready for execution:

### ✅ **Ready to Execute**
- All tasks have clear implementation patterns
- Specific test verification commands added
- Dependencies clearly documented
- ADR-005 references for architectural guidance

### ✅ **Self-Contained Tasks**
- Each task has sufficient detail for execution
- No need for additional specification generation
- Clear success criteria and verification steps

### ✅ **Sequential Design**
- Tasks build on each other logically
- Dependencies prevent parallel execution issues
- Phase-based organization for clear progression

## Usage Instructions

### Start Execution:
```bash
# Create branch for this cleanup phase
git checkout -b cleanup/smartsync-cleanup

# Execute tasks sequentially from Phase 1
# Follow each task's specific instructions
# Test and commit after each task

# When complete, merge back
git checkout main
git merge cleanup/smartsync-cleanup
git branch -d cleanup/smartsync-cleanup
```

### Task Execution Pattern:
1. Read task description and files to fix
2. Implement changes following the provided pattern
3. Run verification commands (grep, uvicorn, pytest)
4. Test manually if specified
5. Commit changes with descriptive message
6. Move to next task

## Notes

- **Not compatible with @agent/ system** - these are markdown-based, not YAML-based
- **Manual execution required** - no automated task runner
- **Well-documented** - each task has sufficient detail for independent execution
- **Test-driven verification** - specific pytest commands ensure correctness

The backlogs are ready for execution in any new thread or by any developer familiar with the codebase.
