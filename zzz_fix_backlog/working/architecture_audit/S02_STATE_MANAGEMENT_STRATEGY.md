# S02_STATE_MANAGEMENT_STRATEGY.md

**Status**: [✅] Discovery | [✅] Analysis | [✅] Design | [✅] Executable Tasks | [✅] Complete

**Dependencies**
- **Depends on**: S01_ARCHITECTURE_DISCOVERY_AUDIT.md
- **Blocks**: All data orchestrator development

**Thread Assignment**
- **Assigned to**: Architecture Discovery Thread
- **Started**: 2025-01-27
- **Completed**: 2025-01-27

**Note**: Converted to E02_FIX_DATA_ORCHESTRATOR_PATTERN.md executable task. This solutioning task is complete.

## **Read These Files First**

### **Architecture Context:**
- `docs/architecture/ADR-006-data-orchestrator-pattern.md` - Current data orchestrator pattern
- `runway/core/data_orchestrators/decision_console_data_orchestrator.py` - Stateful orchestrator example
- `runway/core/data_orchestrators/hygiene_tray_data_orchestrator.py` - Stateless orchestrator example

## **Problem Statement**

**Critical Issue**: ADR-006 is correct about state management, but we need to verify proper business_id scoping for multi-tenant safety.

**Specific Problems**:
1. **ADR-006** correctly claims data orchestrators should manage state
2. **DecisionConsoleDataOrchestrator** stores decision queue state in database correctly
3. **Multi-tenant isolation** needs to be verified and documented
4. **Multi-tenant safety** requires proper business_id scoping in state management

**Business Impact**: 
- Security risk: Poor multi-tenant isolation could leak data between businesses
- Architecture violation: State not properly scoped by business_id
- Development blocker: Prevents building other orchestrators correctly

## **Discovery Phase**

### **1. Analyze Current State Management**

**Discovery Commands**:
```bash
# Check for stateful patterns in orchestrators
grep -r "self\.[a-z]" runway/core/data_orchestrators/ | grep -v "def " | head -10

# Check for database state storage
grep -r "metadata\|queue\|state" runway/core/data_orchestrators/ | head -10

# Check ADR-006 state management claims
grep -r "state" docs/architecture/ADR-006-data-orchestrator-pattern.md
```

**Expected Outputs**:
- [ ] List of stateful patterns in current orchestrators
- [ ] Identification of database state storage
- [ ] Analysis of ADR-006 state management claims

## **Analysis Phase**

### **1. State Management Strategy**

**Questions to Answer**:
- What state should be managed where?
- How should decision queues work without backend state?
- What's the correct pattern for data orchestrators?

**State Management Strategy**:
- **Frontend State**: UI state, form data, temporary selections
- **Database State**: Persistent business data (decisions, queues) - scoped by business_id
- **Service State**: Stateless services that read/write database state with business_id scoping

## **Design Phase**

### **1. Corrected ADR-006**

**Updated Pattern**:
- Data orchestrators are **stateless data transformers**
- No state management in services
- State lives in frontend (UI) or database (persistent)

### **2. Orchestrator Refactoring**

**DecisionConsoleDataOrchestrator Changes**:
- Remove decision queue state management
- Move decision queue to database model
- Make orchestrator stateless data transformer only

**New Pattern for All Orchestrators**:
```python
class DataOrchestrator:
    def __init__(self, db: Session):
        self.db = db  # No instance state
    
    async def get_data(self, business_id: str) -> Dict[str, Any]:
        # Pull data, transform for frontend
        # NO state management
        return transformed_data
```

## **Success Criteria**

- [ ] ADR-006 updated to stateless pattern
- [ ] DecisionConsoleDataOrchestrator made stateless
- [ ] All orchestrators follow stateless pattern
- [ ] State management strategy documented

## **Deliverables**

- [ ] Updated `docs/architecture/ADR-006-data-orchestrator-pattern.md`
- [ ] Refactored `runway/core/data_orchestrators/decision_console_data_orchestrator.py`
- [ ] `STATE_MANAGEMENT_STRATEGY.md` - Clear guidelines for where state lives
- [ ] Updated orchestrator pattern documentation

## **Time Estimate**

- **Discovery**: 30 minutes
- **Analysis**: 30 minutes  
- **Design**: 1 hour
- **Total**: 2 hours

---

*This task fixes the core state management architectural violation that blocks proper multi-tenant SaaS development.*
