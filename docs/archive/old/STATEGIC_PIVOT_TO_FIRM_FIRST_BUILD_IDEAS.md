# Oodaloo v6.0: Firm-First (CAS Multi-Client) Build Plan

**Version**: 6.0 (Strategic Pivot to CAS Firms)  
**Date**: 2025-09-30  
**Updated From**: v5.1 Agentic (Owner-First)  
**Critical Changes**: 
- **PRIMARY ICP**: CAS firms serving 20-100 clients (not individual owners)
- **PRICING**: $50/mo per client ($30k ARR for 50-client firm)
- **P0 PRIORITY**: Data completeness (bank feeds, missing bill detection)
- **P2 PRIORITY**: Agentic positioning (nice-to-have, not must-have)
- **CURRENT STATUS**: Phase 0-2 complete, ready for multi-tenant layer

---

## **🎯 Strategic Positioning: CAS Firm Weekly Cash Call Tool**

### **The Market Reality (Per Levi Morehouse)**

**Problem Validated**: "10,000% right - real need"

**Owner Challenge**: 
- They check bank accounts daily, run everything from banks
- They won't enter missing bills into QBO
- Missing bills = wrong runway = broken trust = broken ritual

**CAS Firm Opportunity**:
- CAS firms buy one-off tools for specific needs
- They can ensure data completeness (they enter missing bills)
- They have the relationship to enforce the ritual
- Weekly cash call is unaddressed opportunity in market
- $50/mo per client is realistic pricing

### **The Product**

**For CAS Firms**: Multi-client weekly cash call automation

**Core Capabilities**:
- Batch runway reviews across 20-100 clients
- Prioritize clients by runway risk
- Data completeness scoring per client
- Must Pay vs Can Delay categorization
- One approval → batch QBO actions per client

**Value Proposition**:
- Save 5-7 hours per week per firm
- Differentiate from bookkeeping-only firms
- Maintain advisory relationship with clients
- Scale weekly cash calls to 50-100 clients

---

## **📊 Current Implementation Status**

### **✅ Phase 0-2: Foundation (COMPLETE)**
**Architecture**: 222 files across 70 directories
- ✅ `domains/` - QBO primitives (ap, ar, bank, core, policy, vendor_normalization)
- ✅ `runway/` - Orchestration (data orchestrators, calculators, experiences)
- ✅ `infra/` - Infrastructure (qbo, auth, database, jobs, monitoring)

**What's Working**:
- ✅ Weekly digest with runway analysis
- ✅ Must Pay vs Can Delay categorization
- ✅ QBO integration and sync
- ✅ AP/AR services and routes
- ✅ Runway calculation and reserve system

**Multi-Tenant Ready**:
- ✅ All models use `business_id` scoping
- ✅ Architecture supports `firm_id` + `client` pattern
- ✅ Build plan already specified: `business` in Oodaloo = `client` in RowCol

---

## **🚀 ROADMAP: Firm-First Development**

### **Phase 3: Multi-Tenant Foundation (40h, Weeks 1-2)** 🔴 P0 CRITICAL

**Timeline**: Next 2 weeks  
**Goal**: Add firm context to existing single-tenant architecture

#### **Stage 3.1: Multi-Tenant Data Model (16h)**

**Add Firm Models** *Effort: 8h*:
```python
class Firm(Base):
    id: int
    name: str
    contact_email: str
    active: bool
    created_at: datetime
    
class FirmStaff(Base):
    id: int
    firm_id: int
    user_id: int
    role: str  # admin, staff, view_only
    active: bool
    
class Business(Base):  # UPDATED
    id: int
    firm_id: int | None  # NULL for direct owner, FK for CAS firm
    name: str
    qbo_realm_id: str
    # ... existing fields
```

**Migration Strategy** *Effort: 8h*:
- Add `firm_id` to Business model (nullable)
- Create Firm and FirmStaff tables
- Migrate existing businesses to NULL firm_id (direct owners)
- Test with mock firm data

#### **Stage 3.2: Firm-Level Authentication (12h)**

**Firm Context Middleware** *Effort: 8h*:
- Extract firm_id from JWT/session
- Filter all queries by firm_id
- Ensure staff can only access their firm's clients

**Role-Based Access** *Effort: 4h*:
- Admin: Full access to all firm clients
- Staff: Read-only access to assigned clients
- View-only: Dashboard access only

#### **Stage 3.3: Firm-Level Routes (12h)**

**New Firm Endpoints** *Effort: 12h*:
- `GET /firms/{firm_id}/clients` - List all clients
- `GET /firms/{firm_id}/dashboard` - Batch runway view
- `GET /firms/{firm_id}/data-quality` - Completeness scores
- `POST /firms/{firm_id}/clients` - Add new client
- `PUT /firms/{firm_id}/clients/{client_id}` - Update client

---

### **Phase 4: Data Completeness Features (60h, Weeks 3-4)** 🔴 P0 CRITICAL

**Timeline**: Weeks 3-4  
**Goal**: Ensure reliable data for runway calculations

#### **Stage 4.1: Bank Feed Integration (40h)**

**Plaid Integration** *Effort: 30h*:
- Set up Plaid account and API keys
- Implement Plaid Link for bank connection
- Pull bank transactions in real-time
- Store bank transactions in database
- Match bank transactions to QBO bills

**Missing Bill Detection** *Effort: 10h*:
- Compare bank outflows to QBO bills
- Flag unexplained cash outflows
- Suggest bills that should be entered
- CAS firm workflow to enter missing bills

#### **Stage 4.2: Point of Sale Integration (20h)**

**POS Integration** *Effort: 15h*:
- Research Square, Toast, Clover APIs
- Pull daily sales data
- Estimate payroll from sales patterns
- Flag payroll timing risks

**Data Quality Scoring** *Effort: 5h*:
- Score data completeness per client (0-100)
- Flag clients with missing data
- Track data quality improvements over time

---

### **Phase 5: Multi-Client Dashboard (50h, Weeks 5-6)** 🔴 P0 CRITICAL

**Timeline**: Weeks 5-6  
**Goal**: Build firm-level batch runway views

#### **Stage 5.1: Batch Runway View (30h)**

**Multi-Client Dashboard** *Effort: 20h*:
- List all clients with runway status
- Prioritize by runway risk (red/yellow/green)
- Show data quality score per client
- Filter by risk level, data quality
- Sort by runway days, payroll date

**Client Detail View** *Effort: 10h*:
- Existing single-client console
- Add "Back to Firm Dashboard" navigation
- Show data completeness warnings

#### **Stage 5.2: Firm-Level Analytics (20h)**

**Aggregate Metrics** *Effort: 10h*:
- Total clients at risk (runway < 30 days)
- Average data completeness across clients
- Total AP due this week across clients
- Total AR overdue across clients

**Export & Reporting** *Effort: 10h*:
- Export client list with runway status
- Weekly firm digest (all clients summary)
- PDF reports for firm partners

---

### **Phase 6: CAS Firm Pilot Features (30h, Weeks 7-8)** 🟡 P1 HIGH

**Timeline**: Weeks 7-8  
**Goal**: Polish for 3-5 CAS firm pilots

#### **Stage 6.1: Onboarding Flow (15h)**

**Firm Onboarding** *Effort: 10h*:
- Firm signup and setup
- Add staff members with roles
- Connect first client QBO account
- Guided tour of firm dashboard

**Client Onboarding** *Effort: 5h*:
- Add client to firm
- Connect client QBO account
- Connect bank feed (Plaid)
- Initial data quality check

#### **Stage 6.2: White-Label Basics (15h)**

**Branding Options** *Effort: 10h*:
- Upload firm logo
- Customize primary color
- Custom domain (optional)
- Firm name in all client-facing content

**Client-Facing Reports** *Effort: 5h*:
- Weekly digest with firm branding
- Client portal with firm logo
- PDF exports with firm letterhead

---

### **Phase 7: Smart Features (Later)** 🟢 P2 NICE-TO-HAVE

**Timeline**: Q2 2026 (After CAS firm validation)  
**Goal**: Add intelligence layer once reliability is proven

**Smart Policies/Budgets** *Effort: 90h*:
- Policy Engine with learning
- Budget constraints
- Vacation Mode
- "AI learns preferences" messaging

**Advanced Analytics** *Effort: 60h*:
- Predictive runway scenarios
- Customer payment profiles
- Vendor payment optimization
- Industry benchmarking

---

## **📐 Architectural Changes**

### **Multi-Tenant Pattern**

**Current (Single-Tenant)**:
```
User → Business → QBO Account
```

**New (Multi-Tenant)**:
```
User → Firm → Clients (Businesses) → QBO Accounts
         ↓
    FirmStaff (roles)
```

### **Data Scoping**

**Current**:
```python
# All queries filtered by business_id
bills = Bill.query.filter_by(business_id=business_id).all()
```

**New**:
```python
# All queries filtered by firm_id → client_id
clients = Business.query.filter_by(firm_id=firm_id).all()
bills = Bill.query.filter(
    Bill.business_id.in_([c.id for c in clients])
).all()
```

### **Authentication**

**Current**:
```python
# JWT contains: user_id, business_id
@require_auth
def get_bills(business_id: int):
    # Direct business access
```

**New**:
```python
# JWT contains: user_id, firm_id, role
@require_firm_auth
def get_firm_dashboard(firm_id: int):
    # Firm-level access with role check
    # Can access all firm's clients
```

---

## **💰 Pricing & Revenue Model**

### **CAS Firm Pricing**

**Base Pricing**: $50/mo per client

**Tiers**:
- **Starter** (1-10 clients): $50/mo per client = $500/mo
- **Professional** (11-50 clients): $45/mo per client = $2,250/mo for 50 clients
- **Enterprise** (51+ clients): $40/mo per client = $4,000/mo for 100 clients

**Add-Ons**:
- White-label branding: +$200/mo
- Priority support: +$300/mo
- Custom integrations: Custom pricing

### **Revenue Projections**

**Year 1** (10 CAS firms, 10 clients each):
- 10 firms × 10 clients × $50/mo = $5,000 MRR
- $5,000 MRR × 12 months = **$60,000 ARR**

**Year 2** (15 CAS firms, 20 clients each):
- 15 firms × 20 clients × $50/mo = $15,000 MRR
- $15,000 MRR × 12 months = **$180,000 ARR**

**Year 3** (30 CAS firms, 30 clients each):
- 30 firms × 30 clients × $50/mo = $45,000 MRR
- $45,000 MRR × 12 months = **$540,000 ARR**

---

## **🔑 Critical Success Factors**

### **Data Completeness** (Make or Break)
1. Bank feed integration working reliably
2. Missing bill detection accurate
3. CAS firms can easily enter missing bills
4. Data quality scoring helps prioritize cleanup

### **Multi-Client Scalability**
1. Firm dashboard loads fast (<2s for 100 clients)
2. Batch operations work reliably
3. Role-based access prevents data leaks
4. Firm-level analytics are accurate

### **CAS Firm Adoption**
1. Onboarding takes <30 minutes
2. First client shows value immediately
3. White-label options feel professional
4. Pricing is clear and realistic

---

## **🎯 Success Metrics**

### **Phase 3-5: MVP (8 weeks)**
- [ ] Multi-tenant architecture working
- [ ] Bank feed integration live (Plaid)
- [ ] Missing bill detection accurate (>90%)
- [ ] Firm dashboard loads <2s for 50 clients
- [ ] 3-5 CAS firms ready to pilot

### **Phase 6: Pilots (3 months)**
- [ ] 5-10 CAS firms signed
- [ ] 100-500 clients under management
- [ ] $5k-$25k MRR ($60k-$300k ARR)
- [ ] 85%+ data completeness across clients
- [ ] <10% churn rate for CAS firms

### **Phase 7: Scale (6-12 months)**
- [ ] 20-50 CAS firms signed
- [ ] 500-2,000 clients under management
- [ ] $25k-$100k MRR ($300k-$1.2M ARR)
- [ ] 90%+ data completeness across clients
- [ ] <5% churn rate for CAS firms

---

## **🚀 Immediate Action Items**

### **This Week** (After Levi's COO Session):
1. [ ] Wait for COO design session (tactical workflow guidance)
2. [ ] Research bank feed integration (Plaid pricing, capabilities)
3. [ ] Sketch multi-tenant database schema
4. [ ] Draft CAS firm pitch deck

### **Next 2 Weeks** (Phase 3):
1. [ ] Build multi-tenant foundation (40h)
2. [ ] Add Firm, FirmStaff, Business.firm_id models
3. [ ] Implement firm-level authentication and routes
4. [ ] Test with 2-3 mock firms

### **Next 4 Weeks** (Phase 4):
1. [ ] Build bank feed integration (40h)
2. [ ] Build missing bill detection (20h)
3. [ ] Validate with real bank data
4. [ ] Get Levi's feedback on data completeness

### **Next 8 Weeks** (Phase 5-6):
1. [ ] Build multi-client dashboard (50h)
2. [ ] Build firm-level analytics (20h)
3. [ ] Polish for CAS firm pilots (30h)
4. [ ] Sign 3-5 CAS firms for pilots

---

## **📋 What Changed from Owner-First (v5.1)**

### **Deprioritized**
- ❌ Agentic positioning (P0 → P2)
- ❌ Smart Policies/Budgets (P0 → P2)
- ❌ QBO App Store distribution
- ❌ Premium pricing ($99-$299/mo)

### **New Priorities**
- ✅ Multi-tenant foundation (NEW P0)
- ✅ Bank feed integration (NEW P0)
- ✅ Missing bill detection (NEW P0)
- ✅ Multi-client dashboard (EXISTING → P0)
- ✅ Data completeness scoring (NEW P1)

### **What Stayed**
- ✅ Weekly cash call ritual
- ✅ Must Pay vs Can Delay categorization
- ✅ One approval → batch QBO actions
- ✅ Runway-first orientation
- ✅ 3-layer architecture (orchestrators → calculators → experiences)

---

## **💡 The Bottom Line**

**We're not starting over - we're adding a multi-tenant layer to what we have.**

**Timeline**: 180 hours (6-8 weeks) to CAS firm pilot-ready

**Architecture**: Already multi-tenant ready (`business_id` scoping)

**Product**: Same weekly cash call ritual, just multi-client context

**The Unlock**: Levi's COO design session will give us exact workflow requirements

---

**Status**: Strategic pivot complete, ready for Phase 3 implementation  
**Next Review**: After Levi's COO design session  
**Owner**: Principal Architect + Product Lead  
**Branch**: `feat/firm-first` (to be created from main)
