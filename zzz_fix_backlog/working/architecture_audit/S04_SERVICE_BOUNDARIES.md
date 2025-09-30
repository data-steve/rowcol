# S04_SERVICE_BOUNDARIES.md

**Status**: [ ] Discovery | [ ] Analysis | [ ] Design | [ ] Executable Tasks | [ ] Complete

**Dependencies**
- **Depends on**: S01_ARCHITECTURE_DISCOVERY_AUDIT.md
- **Blocks**: Service development clarity

**Thread Assignment**
- **Assigned to**: [Thread name/date]
- **Started**: [Date]
- **Completed**: [Date]

## **Read These Files First**

### **Architecture Context:**
- `docs/architecture/ADR-007-service-boundaries.md` - Service boundary definitions
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `domains/` and `runway/` service implementations

## **Problem Statement**

**Critical Issue**: Service boundaries may be unclear or incorrectly defined, leading to architectural confusion and maintenance problems.

**Specific Problems**:
1. **Service responsibilities** may overlap or be unclear
2. **Dependency direction** may violate architectural principles
3. **Domain vs Runway** separation may be inconsistent
4. **Service interfaces** may be poorly defined

**Business Impact**: 
- Development confusion: Developers don't know which service to use
- Maintenance problems: Changes require touching multiple services
- Architecture drift: Services grow beyond their intended scope

## **Discovery Phase**

### **1. Service Boundary Analysis**

**Discovery Commands**:
```bash
# Check service dependencies
grep -r "from.*runway" domains/ | head -10
grep -r "from.*domains" runway/ | head -10

# Check service class definitions
find domains/ -name "*service*.py" -exec echo "=== {} ===" \; -exec grep -A 5 "class.*Service" {} \;
find runway/ -name "*service*.py" -exec echo "=== {} ===" \; -exec grep -A 5 "class.*Service" {} \;

# Check for overlapping functionality
grep -r "def.*get.*data" domains/*/services/ | head -10
grep -r "def.*get.*data" runway/*/services/ | head -10
```

**Expected Outputs**:
- [ ] Map of service dependencies
- [ ] List of overlapping service functionality
- [ ] Analysis of domain vs runway separation

## **Analysis Phase**

### **1. Service Responsibility Clarity**

**Questions to Answer**:
- What should each service be responsible for?
- Where are the boundary violations?
- How should services interact?

## **Design Phase**

### **1. Clear Service Boundaries**

**Domain Services**:
- CRUD operations only
- Business logic for domain entities
- No product-specific logic

**Runway Services**:
- Product orchestration
- User experience logic
- Cross-domain coordination

## **Success Criteria**

- [ ] Clear service responsibilities defined
- [ ] Dependency direction enforced
- [ ] No overlapping functionality
- [ ] Service interfaces documented

## **Deliverables**

- [ ] Updated `docs/architecture/ADR-007-service-boundaries.md`
- [ ] `SERVICE_BOUNDARIES_GUIDELINES.md`
- [ ] Refactored service implementations
- [ ] Service interface documentation

## **Time Estimate**

- **Discovery**: 1 hour
- **Analysis**: 30 minutes
- **Design**: 1 hour
- **Total**: 2.5 hours

---

*This task clarifies service boundaries and prevents architectural confusion.*
