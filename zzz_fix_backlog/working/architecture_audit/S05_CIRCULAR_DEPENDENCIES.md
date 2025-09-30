# S05_CIRCULAR_DEPENDENCIES.md

**Status**: [ ] Discovery | [ ] Analysis | [ ] Design | [ ] Executable Tasks | [ ] Complete

**Dependencies**
- **Depends on**: S01_ARCHITECTURE_DISCOVERY_AUDIT.md
- **Blocks**: Clean architecture, maintainability

**Thread Assignment**
- **Assigned to**: [Thread name/date]
- **Started**: [Date]
- **Completed**: [Date]

## **Read These Files First**

### **Architecture Context:**
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- Service import patterns across domains/ and runway/

## **Problem Statement**

**Critical Issue**: Circular dependencies between services can cause import errors, testing problems, and architectural violations.

**Specific Problems**:
1. **Runway importing from domains** may create circular dependencies
2. **Domain services importing from runway** violates separation
3. **Cross-domain imports** may create dependency cycles
4. **Import order issues** can break the application

**Business Impact**: 
- Development blockers: Import errors prevent development
- Testing problems: Circular dependencies break test isolation
- Architecture violations: Violates clean architecture principles

## **Discovery Phase**

### **1. Circular Dependency Detection**

**Discovery Commands**:
```bash
# Check for runway importing from domains (should be OK)
grep -r "from.*domains" runway/ | head -10

# Check for domains importing from runway (should NOT happen)
grep -r "from.*runway" domains/ | head -10

# Check for cross-domain imports
grep -r "from.*domains\." domains/ | head -10

# Check import patterns
find . -name "*.py" -exec grep -l "import.*domains\|import.*runway" {} \; | head -10
```

**Expected Outputs**:
- [ ] Map of all service imports
- [ ] Identification of circular dependencies
- [ ] List of architectural violations

## **Analysis Phase**

### **1. Dependency Analysis**

**Questions to Answer**:
- Which imports are causing circular dependencies?
- What's the correct dependency direction?
- How can we break the cycles?

## **Design Phase**

### **1. Dependency Resolution**

**Correct Dependency Direction**:
- Runway → Domains (OK)
- Domains → Runway (NOT OK)
- Domains → Domains (minimal, through interfaces)

### **2. Interface Extraction**

**Strategy**:
- Extract shared interfaces
- Use dependency injection
- Create service facades

## **Success Criteria**

- [ ] No circular dependencies
- [ ] Correct dependency direction enforced
- [ ] Clean import structure
- [ ] All tests pass

## **Deliverables**

- [ ] `DEPENDENCY_ANALYSIS.md` - Map of all dependencies
- [ ] Refactored service imports
- [ ] Interface extraction where needed
- [ ] Dependency injection setup

## **Time Estimate**

- **Discovery**: 1 hour
- **Analysis**: 30 minutes
- **Design**: 1 hour
- **Total**: 2.5 hours

---

*This task eliminates circular dependencies and enforces clean architecture.*
