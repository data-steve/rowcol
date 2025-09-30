# F01: Firm-First Multi-Tenant Foundation

**Status**: 🔴 READY TO START  
**Effort**: 180 hours (6-8 weeks)  
**Priority**: P0 CRITICAL  
**Phase**: 3-6 (Foundation → CAS Firm Pilots)

---

## Context

**STRATEGIC PIVOT (2025-09-30)**: CAS firms as primary ICP, not individual owners.

**Why**:  
- Levi Morehouse (Aiwyn.ai President) validated: "10,000% right - real need"
- But: Owners won't maintain data completeness
- Solution: CAS firms can ensure data quality, enforce ritual
- Pricing: $50/mo per client scales better than $99/mo per owner

**What Changed**:
- ❌ Agentic positioning (P0 → P2)
- ❌ Smart Policies/Budgets (P0 → P2)
- ✅ Multi-tenant foundation (NEW P0)
- ✅ Data completeness (NEW P0)

---

## Phase 3: Multi-Tenant Foundation (40h, Weeks 1-2)

### Stage 3.1: Multi-Tenant Data Model (16h)

**Add Firm Models**:
```python
class Firm(Base):
    id: int
    name: str
    contact_email: str
    active: bool
    
class FirmStaff(Base):
    id: int
    firm_id: int
    user_id: int
    role: str  # admin, staff, view_only
    
class Business(Base):  # UPDATED
    id: int
    firm_id: int | None  # NULL for future direct owners
    # ... existing fields
```

**Tasks**:
- [ ] Create Firm model in `domains/core/models/firm.py` (4h)
- [ ] Create FirmStaff model in `domains/core/models/firm_staff.py` (4h)
- [ ] Add firm_id to Business model (nullable) (2h)
- [ ] Create Alembic migration (2h)
- [ ] Test with mock firm data (4h)

### Stage 3.2: Firm-Level Authentication (12h)

**Firm Context Middleware**:
- [ ] Extract firm_id from JWT/session (4h)
- [ ] Filter queries by firm_id → client_ids (4h)
- [ ] Implement RBAC (admin/staff/view-only) (4h)

### Stage 3.3: Firm-Level Routes (12h)

**New Endpoints**:
- [ ] `GET /firms/{firm_id}/clients` - List all clients (3h)
- [ ] `GET /firms/{firm_id}/dashboard` - Batch runway view (3h)
- [ ] `GET /firms/{firm_id}/data-quality` - Completeness scores (3h)
- [ ] `POST /firms/{firm_id}/clients` - Add new client (3h)

---

## Phase 4: Data Completeness (60h, Weeks 3-4)

### Stage 4.1: Bank Feed Integration (40h)

**Plaid Integration**:
- [ ] Set up Plaid account and API keys (2h)
- [ ] Implement Plaid Link for bank connection (8h)
- [ ] Pull bank transactions in real-time (8h)
- [ ] Store bank transactions in database (4h)
- [ ] Match bank transactions to QBO bills (8h)

**Missing Bill Detection**:
- [ ] Compare bank outflows to QBO bills (6h)
- [ ] Flag unexplained cash outflows (2h)
- [ ] CAS firm workflow to enter missing bills (2h)

### Stage 4.2: Point of Sale Integration (20h)

**POS Integration**:
- [ ] Research Square, Toast, Clover APIs (3h)
- [ ] Implement Square integration (8h)
- [ ] Estimate payroll from sales patterns (4h)

**Data Quality Scoring**:
- [ ] Score data completeness per client (0-100) (3h)
- [ ] Track improvements over time (2h)

---

## Phase 5: Multi-Client Dashboard (50h, Weeks 5-6)

### Stage 5.1: Batch Runway View (30h)

**Multi-Client Dashboard**:
- [ ] List all clients with runway status (8h)
- [ ] Prioritize by runway risk (red/yellow/green) (6h)
- [ ] Show data quality score per client (4h)
- [ ] Filter by risk level, data quality (6h)
- [ ] Client detail view with navigation (6h)

### Stage 5.2: Firm-Level Analytics (20h)

**Aggregate Metrics**:
- [ ] Total clients at risk (runway < 30 days) (5h)
- [ ] Average data completeness across clients (5h)
- [ ] Export client list with runway status (5h)
- [ ] Weekly firm digest (all clients summary) (5h)

---

## Phase 6: CAS Firm Pilot Features (30h, Weeks 7-8)

### Stage 6.1: Onboarding Flow (15h)

**Firm Onboarding**:
- [ ] Firm signup and setup (4h)
- [ ] Add staff members with roles (3h)
- [ ] Connect first client QBO account (3h)
- [ ] Guided tour of firm dashboard (5h)

### Stage 6.2: White-Label Basics (15h)

**Branding Options**:
- [ ] Upload firm logo (4h)
- [ ] Customize primary color (3h)
- [ ] Custom domain (optional) (5h)
- [ ] Client-facing reports with firm branding (3h)

---

## Success Criteria

### Phase 3-6 (8 weeks)
- [ ] Multi-tenant architecture working
- [ ] Bank feed integration live (Plaid)
- [ ] Missing bill detection accurate (>90%)
- [ ] Firm dashboard loads <2s for 50 clients
- [ ] 3-5 CAS firms ready to pilot

### Pilots (3 months)
- [ ] 5-10 CAS firms signed
- [ ] 100-500 clients under management
- [ ] $5k-$25k MRR ($60k-$300k ARR)
- [ ] 85%+ data completeness across clients
- [ ] <10% churn rate for CAS firms

---

## What's NOT Included (Deprioritized to Phase 7+)

❌ Agentic positioning / "AI learns preferences" messaging  
❌ Smart Policies/Budgets  
❌ Advanced analytics with ML  
❌ Direct owner access (business.firm_id = NULL)  
❌ QBO App Store distribution  

**Why**: CAS firms care about reliability and data completeness, not AI buzzwords. Focus on making the ritual work at scale first.

---

## Dependencies

**Wait For**:
- [ ] Levi's COO design session (tactical workflow guidance)

**External**:
- [ ] Plaid account approval and API access
- [ ] Research POS integration options

**Internal**:
- ✅ Phase 0-2 complete (foundation ready)
- ✅ Architecture multi-tenant ready (`business_id` scoping)

---

## Timeline

| Week | Phase | Effort | Status |
|------|-------|--------|--------|
| 1-2 | Phase 3: Multi-tenant foundation | 40h | 🔴 Next |
| 3-4 | Phase 4: Data completeness | 60h | 📋 Planned |
| 5-6 | Phase 5: Multi-client dashboard | 50h | 📋 Planned |
| 7-8 | Phase 6: CAS firm pilots | 30h | 📋 Planned |

**Total: 180 hours (6-8 weeks solo)**

---

## Notes

- Architecture already supports this (business_id scoping)
- Not starting over - adding firm layer to what we have
- Product is the same (weekly cash call ritual)
- Just different user context (firm managing clients vs owner managing business)

---

**Status**: Ready to start after Levi's COO session  
**Owner**: Principal Architect + Product Lead  
**Branch**: `feat/firm-first`  
**Updated**: 2025-09-30

