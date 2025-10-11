# Advisor Workflow Solutioning Tasks

This document contains the deeper solutioning tasks that require extensive product and workflow analysis before implementation.

## **Task 9: Solutioning - Advisor Workflow and Calculators**

- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Need to understand the actual advisor workflow before building experience services
- **Execution Status:** **Solutioning Required**

### **Task Checklist:**
- [ ] Document the real advisor workflow for weekly cash calls
- [ ] Define what "clean a hygiene issue" actually means
- [ ] Define what "approve payment scheduling" actually means
- [ ] Design calculator interfaces for runway impact, bulk operations, cash flow
- [ ] Design experience service interfaces that use calculators
- [ ] Create user stories for backstage advisor work
- [ ] Create user stories for frontstage weekly cash calls
- [ ] Document the WWW (Who/What/When) task capture workflow

### **Problem Statement**
We have gateway filtering methods but don't understand what advisors actually DO with the filtered data. Experience services need calculators to provide meaningful business logic, but we need to understand the advisor workflow first.

### **User Story**
"As an advisor preparing for a weekly cash call, I need to understand what RowCol helps me do with hygiene issues and payment decisions so that I can efficiently prepare for client meetings."

### **Solution Overview**
Deep solutioning on advisor workflow to understand:
- What does "clean a hygiene issue" actually mean?
- What calculators are needed for runway impact, bulk operations, cash flow?
- How do experience services use calculators to provide value?
- What's the backstage/frontstage advisor experience?

### **Key Questions to Answer:**
1. **Hygiene Issues**: What's the actual workflow for fixing data quality?
2. **Payment Decisions**: What calculations help advisors schedule payments?
3. **Collections**: What calculations help advisors prioritize collections?
4. **Client Deliverables**: What reports/explanations do advisors generate?
5. **WWW Tasks**: How do advisors capture and track accountability?

---

## **Task 10: Implement Calculators and Experience Services**

- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Implement the calculator and experience service design from Task 9
- **Execution Status:** **Pending Task 9**

### **Task Checklist:**
- [ ] Implement calculator interfaces (runway impact, bulk operations, cash flow)
- [ ] Implement experience services that use calculators
- [ ] Update wiring layer to include calculators
- [ ] Create basic UI endpoints for experience services
- [ ] All files can be imported without errors
- [ ] All services work with calculators and gateways

### **Problem Statement**
Implement the calculator and experience service design determined in Task 9.

### **User Story**
"As a developer, I need to implement calculators and experience services so that advisors can efficiently prepare for weekly cash calls."

### **Solution Overview**
Implement the calculator and experience service architecture designed in Task 9.

---

## **Task 11: Test Calculators and Experience Services**

- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Test the calculator and experience service implementation
- **Execution Status:** **Pending Task 10**

### **Task Checklist:**
- [ ] Create tests for calculator interfaces
- [ ] Create tests for experience services
- [ ] Create integration tests for calculator + gateway + experience service flow
- [ ] All tests can be run without errors
- [ ] All tests validate calculator logic
- [ ] All tests validate experience service functionality
- [ ] All tests pass

### **Problem Statement**
Test the calculator and experience service implementation from Task 10.

### **User Story**
"As a developer, I need to test calculators and experience services so that I can validate the advisor workflow implementation works correctly."

### **Solution Overview**
Create comprehensive tests for the calculator and experience service implementation.

---

## **Context and Background**

### **Why These Tasks Need Separate Solutioning**

These tasks require deep product understanding that goes beyond technical implementation:

1. **Advisor Workflow Understanding**: We need to understand what advisors actually do with hygiene issues and payment decisions
2. **Calculator Design**: We need to design business logic that provides real value to advisors
3. **Experience Service Architecture**: We need to understand how experience services use calculators to provide meaningful functionality

### **Current State**
- ✅ Domain gateways with filtering methods (`list_incomplete`, `list_payment_ready`, `list_collections_ready`)
- ✅ Wiring layer that creates services with gateways
- ❌ **Missing**: Understanding of what advisors actually do with filtered data
- ❌ **Missing**: Calculator interfaces for business logic
- ❌ **Missing**: Experience service interfaces that use calculators

### **Next Steps**
1. Complete Tasks 7-8 (finish current implementation and test it)
2. Begin Task 9 (deep solutioning on advisor workflow)
3. Use Task 9 insights to design calculators and experience services
4. Implement and test the new architecture

### **Dependencies**
- Tasks 7-8 must be completed first
- Task 9 requires extensive product research and user story development
- Tasks 10-11 depend on Task 9 completion

