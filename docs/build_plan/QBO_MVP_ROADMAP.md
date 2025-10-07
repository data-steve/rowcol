# QBO MVP Roadmap

## **🎯 Current Status: QBO MVP Foundation Complete**

**Note:** This is the QBO-only MVP roadmap (2-3 weeks). For the full multi-rail platform plan, see `rowcol_financial_control_plane_e2e.md`.

**What's Done:**
- ✅ QBO execution assumptions fixed
- ✅ Feature gating system implemented
- ✅ Technical debt protected for future phases
- ✅ All core services gated properly

**What's Next: QBO MVP Delivery**

---

## **📋 Next Steps (In Order)**

### **Step 1: QBO MVP Dashboard (2-3 weeks)**
**Goal**: Get a working QBO-only product in users' hands

**Tasks:**
1. **Create QBO-only test scenarios** (1 week)
   - Use existing sandbox framework
   - Create 3-5 realistic business profiles
   - Generate QBO data for all services

2. **Build unified dashboard** (1-2 weeks)
   - Combine digest + hygiene + console into single page
   - Show QBO data only (feature gated)
   - Mobile-friendly for advisor use

3. **Fix Business ID dependency injection** (2-3 days)
   - Replace get_services() pattern with direct business_id injection
   - Update all route files to use new pattern
   - Clean up over-engineered dependency containers

4. **Test with real QBO data** (3-5 days)
   - Connect to actual QBO sandbox
   - Validate all services work
   - Fix any remaining issues

**Deliverable**: Working QBO-only MVP that advisors can use

---

### **Step 2: Ramp Integration (3-4 weeks)**
**Goal**: Add Ramp payment execution and reserve management

**Tasks:**
1. **Ramp API integration** (1 week)
   - Build Ramp API client
   - Test with Ramp sandbox

2. **Enable Ramp features** (1-2 weeks)
   - Un-gate Ramp functionality
   - Implement payment execution
   - Implement reserve management

3. **Resolve technical debt** (1 week)
   - Fix scheduled payment + reserve integration
   - Redesign reserve management architecture
   - Implement proper payment execution strategy

**Deliverable**: Multi-rail platform with QBO + Ramp

---

### **Step 3: Multi-Rail Optimization (3-4 weeks)**
**Goal**: Add Plaid + Stripe, optimize for scale

**Tasks:**
1. **Add Plaid + Stripe** (2 weeks)
   - Build API clients
   - Integrate with existing services

2. **Optimize architecture** (1-2 weeks)
   - Consolidate data orchestrators
   - Refactor service boundaries
   - Implement dynamic configuration

**Deliverable**: Full multi-rail platform

---

## **🗂️ Document Cleanup**

**Keep:**
- `MASTER_ROADMAP.md` - This document (single source of truth)
- `rowcol_financial_control_plane_e2e.md` - Detailed technical specs

**Archive:**
- `CODEBASE_AUDIT_MVP_ALIGNMENT.md` - Superseded by implementation
- `QBO_MVP_IMPLEMENTATION_HANDOFF.md` - Superseded by implementation
- `TECHNICAL_DEBT_PHASE_STRATEGY.md` - Superseded by implementation
- `PHASE_1_TECHNICAL_DEBT_BACKLOG.md` - Superseded by implementation

---

## **🎯 Current Focus: QBO MVP Dashboard**

**Next 3 tasks:**
1. Create QBO-only test scenarios
2. Build unified dashboard
3. Test with real QBO data

**Timeline:** 2-3 weeks
**Goal:** Working QBO-only MVP for advisors

---

## **💡 Why This Approach**

1. **Clear Focus** - One document, one roadmap
2. **Immediate Value** - Get QBO MVP working first
3. **Learn & Iterate** - Use real usage to inform architecture
4. **Clean Progression** - Each step builds on the previous

**Ready to start with QBO MVP dashboard?**
