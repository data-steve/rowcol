# RowCol Advisor-First: Complete Build Plan for runway/ Product

**Product**: RowCol runway/ - Weekly Cash Ritual Platform  
**Target**: Individual CAS advisors managing 5-50 clients  
**Pricing**: $50-250/client/month subscription tiers  
**Timeline**: Phase 1 (4 weeks) → Phase 2 (3-4 months) → Phase 3 (4-5 months) → Phase 4 (4-5 months)  
**Updated**: 2025-10-01  
**Status**: Complete Multi-Phase Build Plan

## ⚠️ **CRITICAL BUILD PLAN REALITY CHECK**

**This build plan is naively simplistic and handwavy over massive complexity.**

### **What This Build Plan Actually Is:**
- **Phases and stages** - not detailed requirements
- **High-level direction** - not implementation specifications
- **Hopelessly underspecified** - missing critical details
- **Needs massive healing** - like we did with v5 build plan on Oodaloo

### **What This Build Plan Is NOT:**
- ❌ **Real requirement doc** - too simplistic for actual complexity
- ❌ **Implementation guide** - missing critical details
- ❌ **Ready for execution** - needs discovery and solutioning first
- ❌ **Accurate time estimates** - based on assumptions, not reality

### **Required Healing Process:**
1. **Discovery Phase** - understand what actually exists vs. what build plan assumes
2. **Gap Analysis** - identify where build plan is wrong or missing details
3. **Solutioning Phase** - design actual solutions for complex problems
4. **Self-Healing Tasks** - convert build plan to executable/solutioning tasks
5. **Reality Grounding** - base tasks on actual codebase, not assumptions

### **Core Demands Are Same as Oodaloo v5:**
- **Multi-tenancy complexity** - advisor-client relationships
- **QBO integration challenges** - API fragility, rate limiting, data sync
- **Service boundary issues** - domains vs runway separation
- **Authentication complexity** - advisor-scoped access control
- **Data orchestration** - complex data flows across multiple systems

**This build plan is a starting point, not a finish line.**

---

## **🚨 CRITICAL LEGAL & COMPLIANCE REQUIREMENTS**

### **Financial Advice Liability - CRITICAL**
**APPLIES TO ALL PHASES, ALL FEATURES, ALL COPY**

- **NEVER use language that could be construed as financial advice**
- We are **NOT financial advisors** - we provide tools and insights only
- **Approved Language**: "data shows", "common strategies", "insights to consider", "tools to help you decide"
- **PROHIBITED Language**: "recommendations", "advice", "we suggest", "you should", "we recommend"
- All UI copy, API responses, and documentation must be reviewed for compliance
- Users make all financial decisions - we only provide information and analysis tools
- **Legal Risk**: Significant liability exposure if we appear to give financial advice

### **Implementation Requirements**
- [ ] **Audit all existing copy** for prohibited financial advice language
- [ ] **Update API response schemas** to use compliant terminology
- [ ] **Review UI components** for advice-like language
- [ ] **Create copy review checklist** for all new features
- [ ] **Legal review process** for customer-facing content

---

## **🎯 STRATEGIC CONTEXT**

### **The Market Opportunity**

**Problem**: CAS advisors charge clients $1,000/month for bookkeeping but are stuck in spreadsheets managing weekly cash decisions.

**Solution**: RowCol = Purpose-built advisor console that replaces spreadsheets with a streamlined 3-tab interface (Digest + Tray + Console).

**Value Proposition**: "Get out of your spreadsheets. Scale your practice."

### **The Economics**

```
Advisor charges client:  $1,000/month for bookkeeping services
Advisor pays RowCol:     $50-250/client/month (5-25% of service cost)
Advisor margin:          75-95%

Key Insight: Value is TIME SAVINGS, not intelligence
```

### **The Product Strategy**

RowCol is the FIRST product in a three-product platform:
1. **runway/** - Weekly cash ritual (THIS DOCUMENT)
2. **bookclose/** - Monthly books ritual (Future)
3. **tax_prep/** - Yearly tax ritual (Future)

This document focuses exclusively on **runway/** product development across all tiers.

---

## **📊 TIER STRUCTURE & PRICING**

### **Tier 1: $50/client/month - "Spreadsheet Replacement"**
**Target Advisor**: Entry-level CAS advisor with 5-15 clients  
**Value Prop**: Stop building spreadsheets every month  
**Features**: Client List + 3-Tab View + Basic Runway  
**Timeline**: Phase 1 (4 weeks)

### **Tier 2: $125/client/month - "Async Advisory"**
**Target Advisor**: Growing CAS practice with 15-30 clients  
**Value Prop**: Serve more clients through async workflows  
**Features**: + Data completeness + Client portal + Smart features  
**Timeline**: Phase 2 (3-4 months after Phase 1)

### **Tier 3: $250/client/month - "Advisory Deliverables"**
**Target Advisor**: Established advisor with 30-50 premium clients  
**Value Prop**: Advanced forecasting and intelligence for premium advisory  
**Features**: + 13-week forecast + Scenario analysis + Collections automation  
**Timeline**: Phase 3 (4-5 months after Phase 2)

### **Tier 4: Enterprise - "Practice Management"**
**Target Advisor**: Multi-advisor practices with staff  
**Value Prop**: Practice-wide management and white-label branding  
**Features**: + Multi-advisor dashboard + Staff RBAC + White-label  
**Timeline**: Phase 4 (4-5 months after Phase 3)

---

## **🚀 PHASE 1: TIER 1 MVP ($50/client/month)**

**Goal**: Prove the value hypothesis - advisors will pay $50/client/month for spreadsheet replacement

**Timeline**: 4 weeks  
**Effort**: 140 hours  
**Success Criteria**: 10 paying advisors using it daily

### **Week 1: Foundation (36h)**

#### **1.1: Database Migration - `firm_id` → `advisor_id` (16h)**

**Why**: "Firm" is ambiguous (could mean practice or individual). "Advisor" is clear.

**Migration Script**:
```sql
-- Rename tables
ALTER TABLE firms RENAME TO advisors;

-- Rename columns
ALTER TABLE advisors RENAME COLUMN firm_id TO advisor_id;
ALTER TABLE businesses RENAME COLUMN firm_id TO advisor_id;

-- Update all foreign keys throughout database

-- Add subscription tier tracking
ALTER TABLE advisors ADD COLUMN runway_tier VARCHAR(50) DEFAULT 'basic';
ALTER TABLE advisors ADD COLUMN feature_flags JSONB DEFAULT '{}';
```

**Files to Update**:
- All model files: `domains/*/models/*.py`
- All service files: `domains/*/services/*.py`
- All route files: `domains/*/routes/*.py` + `runway/routes/*.py`
- Update `ADR-003-multi-tenancy-strategy.md`

**Verification**:
```bash
# Check for firm_id references
grep -r "firm_id" . --include="*.py"

# Run tests
pytest tests/

# Test application startup
uvicorn main:app --reload
```

**Estimated Effort**: 16 hours

---

#### **1.2: Create `advisor/` Layer Structure (16h)**

**Why**: Advisor workflow features (client management, subscription) don't belong in `runway/` - they're cross-product.

**Directory Structure**:
```
advisor/
├── __init__.py
├── client_management/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── advisor.py              # Advisor entity (renamed from firm.py)
│   │   └── subscription.py         # Subscription tier management
│   ├── services/
│   │   ├── __init__.py
│   │   ├── client_list_service.py  # List all clients, sort, filter
│   │   └── subscription_service.py # Manage subscription tiers
│   └── schemas/
│       ├── __init__.py
│       ├── advisor.py              # Advisor API schemas
│       └── client_list.py          # Client list response schemas
├── routes/
│   ├── __init__.py
│   └── client_management.py        # Client list API endpoints
└── README.md                        # Architecture explanation
```

**Key Models**:

```python
# advisor/client_management/models/advisor.py
from sqlalchemy import Column, String, JSONB
from infra.database.base import Base

class Advisor(Base):
    __tablename__ = "advisors"
    
    advisor_id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    
    # Subscription tiers (per-product)
    runway_tier = Column(String, default="basic")  # basic, communication, intelligence
    bookclose_tier = Column(String, nullable=True)  # Future: Phase 2
    tax_prep_tier = Column(String, nullable=True)   # Future: Phase 3
    
    # Feature overrides
    feature_flags = Column(JSONB, default={})
    
    # Practice management (Tier 4 - Enterprise)
    practice_id = Column(String, nullable=True)  # RESERVED for Tier 4
```

**Estimated Effort**: 16 hours

---

#### **1.3: Feature Gating System (4h)**

**Why**: Need to gate Tier 2+ features now, even if not built yet.

**Implementation**:

```python
# advisor/client_management/services/feature_gating.py

RUNWAY_TIER_FEATURES = {
    "basic": [
        # Tier 1 ($50/client/month)
        "client_list",
        "client_list_batch_runway",
        "tray",
        "console", 
        "digest",
        "basic_runway_calculator"
    ],
    "communication": [
        # All basic features, plus Tier 2 ($125/client/month)
        "bank_feed_integration",
        "missing_bill_detection",
        "data_quality_scoring",
        "client_portal",
        "email_interactions",
        "smart_prioritization",
        "payment_recommendations",
        "customer_payment_profiles"
    ],
    "intelligence": [
        # All communication features, plus Tier 3 ($250/client/month)
        "thirteen_week_forecast",
        "scenario_analysis",
        "budget_constraints",
        "collections_automation",
        "ar_priority_scoring",
        "vendor_payment_optimization",
        "industry_benchmarking"
    ]
}

def can_use_feature(advisor: Advisor, feature: str) -> bool:
    """Check if advisor's tier includes this feature."""
    tier = advisor.runway_tier or "basic"
    
    # Get all features for this tier (includes lower tiers)
    if tier == "intelligence":
        allowed_features = RUNWAY_TIER_FEATURES["intelligence"]
    elif tier == "communication":
        allowed_features = RUNWAY_TIER_FEATURES["communication"]
    else:
        allowed_features = RUNWAY_TIER_FEATURES["basic"]
    
    # Check feature flag overrides
    if advisor.feature_flags.get(feature):
        return True
    
    return feature in allowed_features

def require_feature(feature: str):
    """Decorator to gate routes by feature."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            advisor = get_current_advisor()
            if not can_use_feature(advisor, feature):
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Feature not available in your tier",
                        "current_tier": advisor.runway_tier,
                        "required_tier": get_required_tier(feature),
                        "upgrade_url": "/pricing"
                    }
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

**API Middleware**:

```python
# main.py or advisor/routes/client_management.py
@app.get("/api/v1/advisor/clients")
@require_feature("client_list")
def get_client_list(advisor: Advisor = Depends(get_current_advisor)):
    """Get all clients for this advisor with runway data."""
    # Implementation in Priority 1 below
    pass
```

**Estimated Effort**: 4 hours

---

### **Week 2: Core Features (26h)**

#### **2.1: Client List View with Batch Runway (12h)**

**Why**: This IS the spreadsheet replacement. Advisors need to see all clients with runway days visible to triage which client needs attention.

**User Story**: As an advisor, I want to see all my clients in one table with their runway days visible, sorted by priority, so I can quickly identify which clients need immediate attention.

**Acceptance Criteria**:
- ✅ Shows all clients for logged-in advisor
- ✅ **Batch runway view**: All clients with runway days visible in table
- ✅ **Visual priority system**: Red (<30 days), Yellow (30-60 days), Green (>60 days)
- ✅ Displays: client name, runway days, last worked date, items needing attention
- ✅ **Aggregate metric at top**: "5 clients under 30 days runway"
- ✅ Sortable by: "Runway days" (ascending), "Last worked", "Alphabetical"
- ✅ Click client → Opens 3-tab client view
- ✅ **Performance requirement**: <2s load time for 50 clients

**Implementation**:

```python
# advisor/client_management/services/client_list_service.py
from typing import List, Dict
from domains.core.models.business import Business
from runway.services.calculators.runway_calculator import RunwayCalculator

class ClientListService:
    def __init__(self, db: Session, advisor_id: str):
        self.db = db
        self.advisor_id = advisor_id
        self.runway_calculator = RunwayCalculator(db)
    
    def get_client_list_with_runway(self, sort_by: str = "runway_days") -> Dict:
        """Get all clients with batch runway calculations."""
        
        # Get all businesses for this advisor
        businesses = self.db.query(Business).filter(
            Business.advisor_id == self.advisor_id
        ).all()
        
        # Batch calculate runway for all clients
        client_data = []
        clients_at_risk = 0
        
        for business in businesses:
            # Calculate runway for this client
            runway_data = self.runway_calculator.calculate_runway(
                business_id=business.id
            )
            
            runway_days = runway_data.get("runway_days", 0)
            
            # Determine priority color
            if runway_days < 30:
                priority = "red"
                clients_at_risk += 1
            elif runway_days < 60:
                priority = "yellow"
            else:
                priority = "green"
            
            # Get items needing attention from tray
            tray_items = self._get_tray_item_count(business.id)
            
            client_data.append({
                "business_id": business.id,
                "business_name": business.name,
                "runway_days": runway_days,
                "priority": priority,
                "last_worked_at": business.last_worked_at,
                "items_needing_attention": tray_items
            })
        
        # Sort by specified field
        if sort_by == "runway_days":
            client_data.sort(key=lambda x: x["runway_days"])
        elif sort_by == "last_worked":
            client_data.sort(key=lambda x: x["last_worked_at"] or datetime.min)
        else:  # alphabetical
            client_data.sort(key=lambda x: x["business_name"])
        
        return {
            "clients": client_data,
            "aggregate_metrics": {
                "total_clients": len(client_data),
                "clients_at_risk": clients_at_risk,
                "clients_yellow": len([c for c in client_data if c["priority"] == "yellow"]),
                "clients_green": len([c for c in client_data if c["priority"] == "green"])
            }
        }
    
    def _get_tray_item_count(self, business_id: str) -> int:
        """Get count of items needing attention for this client."""
        # TODO: Integrate with TrayService when Priority 2 is complete
        return 0
```

**API Endpoint**:

```python
# advisor/routes/client_management.py
from fastapi import APIRouter, Depends
from advisor.client_management.services.client_list_service import ClientListService

router = APIRouter(prefix="/api/v1/advisor", tags=["advisor"])

@router.get("/clients")
@require_feature("client_list")
def get_client_list(
    sort_by: str = "runway_days",
    advisor: Advisor = Depends(get_current_advisor),
    db: Session = Depends(get_db)
):
    """Get all clients for this advisor with runway data."""
    service = ClientListService(db, advisor.advisor_id)
    return service.get_client_list_with_runway(sort_by=sort_by)
```

**Files to Create**:
- `advisor/client_management/services/client_list_service.py`
- `advisor/routes/client_management.py`
- `advisor/client_management/schemas/client_list.py`

**Files to Update**:
- Add `last_worked_at` timestamp to `domains/core/models/business.py`
- Update `main.py` to include advisor router

**Estimated Effort**: 12 hours

---

#### **2.2: Hygiene Tray - Cash Items Only (6h)**

**Why**: Advisors need to see what needs attention before making cash decisions. Focus ONLY on cash-related issues (not bookkeeping).

**User Story**: As an advisor, I want to see all cash-related items that need my attention (bills missing payment methods, invoices missing due dates), so I can fix them before making payment decisions.

**Acceptance Criteria**:
- ✅ Shows progress: "7 of 12 items fixed"
- ✅ Lists ONLY cash-related issues:
  - Bills missing payment method
  - Bills missing due date
  - Invoices missing due date
  - Unusual payment amounts (flag for review)
- ✅ Click item → Fix inline OR deeplink to QBO
- ✅ "Mark as reviewed" button (for items advisor can't fix)
- ✅ Updates progress bar as items are fixed

**What's NOT Included** (These are bookkeeping tasks, not cash decisions):
- ❌ Uncategorized transactions
- ❌ Chart of accounts issues
- ❌ Tax categorization

**Files to Update**:
- `runway/services/2_experiences/tray.py` (already exists, needs cleanup)
- Remove bookkeeping-related checks
- Focus on cash decision blockers only

**Estimated Effort**: 6 hours

---

#### **2.3: Digest Dashboard (8h)**

**Why**: Advisors need a snapshot of client cash position when they open a client.

**User Story**: As an advisor, when I open a client, I want to immediately see their cash position (days of runway, bills due, overdue AR), so I understand their current state.

**Acceptance Criteria**:
- ✅ Cash position card: "47 days of runway" with trend indicator
- ✅ Bills due card: "5 bills due this week ($12,500)"
- ✅ Overdue AR card: "3 invoices overdue ($8,300)"
- ✅ Recent activity feed: Last 10 transactions
- ✅ Updates in real-time when decisions are executed

**Files to Update**:
- `runway/services/2_experiences/digest/` (already exists, needs cleanup)
- Remove owner-first features (Friday email, etc.)
- Focus on dashboard view only

**Estimated Effort**: 8 hours

---

### **Week 3: Decision Making (20h)**

#### **3.1: Decision Console - Simplified for Advisor-Only (12h)**

**Why**: Advisors need to make batch payment decisions and see runway impact. Simplified for MVP: no approval layer, assume full delegation.

**User Story**: As an advisor, I want to select which bills to pay and which AR to collect, see the runway impact, and execute decisions in one batch, so I can make good cash decisions quickly.

**Acceptance Criteria**:
- ✅ Shows progress: "3 of 8 decisions made"
- ✅ Bills section:
  - Checkbox list of bills due
  - Shows runway impact: "Paying these 3 bills = -5 days of runway"
  - "Pay now" button (immediate) or "Schedule" button (future date)
- ✅ AR section:
  - Checkbox list of overdue invoices
  - "Send reminder" button
- ✅ "Finalize all decisions" button:
  - Executes all selected actions in batch
  - Shows confirmation with results
  - Updates runway calculation

**Simplified for MVP**:
- ❌ No approval workflow (advisor has full authority)
- ❌ No smart prioritization (Tier 2 feature)
- ❌ No payment recommendations (Tier 2 feature)
- ❌ No client portal for owner approval (Tier 2 feature)

**Workflow**:
```
1. Advisor Reviews Bills (from Tray)
2. Advisor Makes Decisions (Console)
3. Advisor Executes Batch (Finalize button)
4. System Updates QBO (Background via SmartSync)
5. System Updates Runway Calculation
```

**Files to Update**:
- `runway/services/2_experiences/console/` (already exists, needs simplification)
- `runway/services/0_data_orchestrators/decision_console_data_orchestrator.py`
- Remove `_process_decision()` stub, implement real payment execution
- Integrate with `domains/ap/services/payment.py` for execution

**Estimated Effort**: 12 hours

---

#### **3.2: Basic Runway Calculator (4h)**

**Why**: Need to show "days of runway" throughout the app. Simplified for MVP: basic calculation only, no advanced scenarios.

**User Story**: As an advisor, I want to see how many days of cash runway my client has, so I can advise them on payment timing.

**Acceptance Criteria**:
- ✅ Calculates: `runway_days = current_cash / average_daily_burn`
- ✅ Shows in Digest dashboard
- ✅ Updates when payment decisions are executed
- ✅ Shows impact preview in Decision Console

**Files to Update**:
- `runway/services/1_calculators/runway_calculator.py` (already exists)
- Simplify to basic calculation only
- Remove advanced features (scenarios = Tier 3)

**Estimated Effort**: 4 hours

---

#### **3.3: End-to-End Testing (4h)**

**Why**: Verify full workflow works before shipping to beta advisors.

**Test Scenarios**:
1. Advisor logs in → Sees client list with runway days
2. Advisor clicks client → Opens 3-tab view
3. Advisor fixes tray items → Progress updates
4. Advisor makes payment decisions → Runway impact shows
5. Advisor executes batch → QBO updates, runway recalculates

**Estimated Effort**: 4 hours

---

### **Week 4: Polish & Beta Launch (18h)**

#### **4.1: UI/UX Polish (16h)**

**UI/UX Standards** (Reference: `ui/PLAYBOOK.md`)

Every UI element must answer three questions in order:
1. **Where am I?** (state) → concise, linear time indicator
2. **What changed?** (delta) → variance vs plan/last week  
3. **What do I do now?** (one primary action) → explicit runway delta from the action

**Required Component Standards**:
- **RunwayCoverageBar**: Linear time visualization (REPLACES circular gauges)
- **Runway Flowband**: Signature visualization (sparse, top-N events, List Mode parity)
- **VarianceChip**: Aggregated variance tracking with one-click CTA routing
- **PaymentTimeline**: Per-item control with constrained slider and runway delta preview
- **PrepTrayList**: Game board layout (Must Pay / Can Delay / Chasing)

**Design Token Enforcement**:
- Use only defined tokens (--brand, --bg, --fg, etc.) - ban raw hexes
- Narrative-first copy ("Do X → +Y days"), celebratory states ("Payroll safe 🎉")
- WCAG AA compliance, List Mode parity, keyboard navigation

**Performance Requirements**:
- Flowband renders <300ms, ≤25 event pills
- Dashboard loads <2s
- All interactions feel responsive (<100ms)

**Tasks**:
- Visual design improvements (8h)
- Responsive layout (3h)
- Loading states (2h)
- Error handling (2h)
- Performance optimization (1h)

#### **4.2: Beta Advisor Onboarding (8h)**
- Manual onboarding process (using `infra/qbo/setup`)
- Documentation for beta advisors
- Initial data load and verification

#### **4.3: Monitor & Fix (8h)**
- Monitor usage patterns
- Fix critical bugs
- Gather feedback

**Estimated Effort**: 18 hours

---

## **PHASE 1 SUMMARY**

**Total Timeline**: 4 weeks  
**Total Effort**: 140 hours

**Features Delivered**:
- ✅ Client List with batch runway view
- ✅ Hygiene Tray (cash items only)
- ✅ Decision Console (simplified)
- ✅ Digest Dashboard
- ✅ Basic Runway Calculator
- ✅ Feature gating system
- ✅ `advisor/` layer foundation

**NOT Delivered** (Deferred to Phase 2+):
- ❌ Smart prioritization
- ❌ Client portal
- ❌ Bank feed integration
- ❌ Onboarding flow (manual for beta)
- ❌ TestDrive/Digest (Oodaloo features)

---

### **PHASE 1 SUCCESS CRITERIA**

**Product Adoption**:
- ✅ 10 paying advisors using it daily
- ✅ 100+ client accounts managed
- ✅ 80%+ weekly active rate
- ✅ 90%+ retention after 30 days

**Performance & Quality**:
- ✅ Client list loads <2s for 50 clients
- ✅ Runway calculation accuracy within ±1 day
- ✅ Dashboard renders <2s
- ✅ Zero critical bugs in production

**Time Savings**:
- ✅ <30 min per client per week (vs 45+ min with spreadsheets)
- ✅ Advisors report 10-20 hours saved per week across portfolio
- ✅ 70%+ advisors say it's faster than spreadsheets

**User Satisfaction**:
- ✅ 70%+ advisors mention they like the interface
- ✅ Clear feedback on what's missing for Tier 2
- ✅ No legal/compliance issues in copy

---

## **🚀 PHASE 2: TIER 2 FEATURES ($125/client/month)**

**Goal**: Enable advisors to serve more clients through async workflows

**Timeline**: 3-4 months after Phase 1 launch  
**Effort**: 150 hours  
**Success Criteria**: 50% of Tier 1 advisors upgrade to Tier 2

### **2.1: Data Completeness (60h)**

**Why This Matters**: Levi's feedback - "Missing bills = wrong runway = broken trust." Advisors need to catch what clients miss.

#### **Bank Feed Integration (Plaid) - 40h**

**User Story**: As an advisor, I want to connect my client's bank accounts so I can see real-time transactions and catch missing bills.

**Features**:
- Set up Plaid account and API keys - 5h
- Implement Plaid Link for bank connection - 10h
- Pull bank transactions in real-time - 10h
- Store bank transactions in database - 5h
- Match bank transactions to QBO bills - 10h

**New Models**:
```python
# domains/bank/models/bank_connection.py
class BankConnection(Base):
    __tablename__ = "bank_connections"
    
    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    plaid_access_token = Column(String, encrypted=True)
    plaid_item_id = Column(String)
    institution_name = Column(String)
    account_mask = Column(String)
    active = Column(Boolean, default=True)

# domains/bank/models/bank_transaction.py
class BankTransaction(Base):
    __tablename__ = "bank_transactions"
    
    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    bank_connection_id = Column(String, ForeignKey("bank_connections.id"))
    plaid_transaction_id = Column(String, unique=True)
    
    date = Column(Date)
    amount = Column(Float)
    description = Column(String)
    category = Column(String)
    
    # Matching
    matched_bill_id = Column(String, ForeignKey("bills.id"), nullable=True)
    match_confidence = Column(Float, nullable=True)
```

**API Endpoints**:
- `POST /api/v1/bank/connect` - Initiate Plaid Link
- `GET /api/v1/bank/accounts` - List connected accounts
- `GET /api/v1/bank/transactions` - Get bank transactions
- `POST /api/v1/bank/match` - Match transaction to bill

**Add-on Pricing**: $10/client/month

**Estimated Effort**: 40 hours

---

#### **Missing Bill Detection - 10h**

**User Story**: As an advisor, I want to be alerted when there are unexplained cash outflows, so I can add missing bills to QBO.

**Features**:
- Compare bank outflows to QBO bills - 4h
- Flag unexplained cash outflows - 3h
- Suggest bills that should be entered - 3h

**Algorithm**:
```python
# domains/bank/services/missing_bill_detector.py
def detect_missing_bills(business_id: str, date_range: DateRange):
    """Compare bank outflows to QBO bills, flag unexplained."""
    
    # Get all bank outflows in date range
    bank_outflows = get_bank_transactions(
        business_id=business_id,
        type="debit",
        date_range=date_range
    )
    
    # Get all QBO bills paid in date range
    qbo_bills = get_bills_paid(
        business_id=business_id,
        date_range=date_range
    )
    
    # Find unmatched outflows
    unmatched = []
    for outflow in bank_outflows:
        if not outflow.matched_bill_id:
            # Try to match by amount and date
            potential_matches = find_potential_bill_matches(outflow, qbo_bills)
            if not potential_matches:
                unmatched.append({
                    "transaction": outflow,
                    "suggested_action": "Add missing bill to QBO"
                })
    
    return unmatched
```

**UI Integration**: Add to Hygiene Tray as new item type

**Estimated Effort**: 10 hours

---

#### **Data Quality Scoring - 5h**

**User Story**: As an advisor, I want to see a data quality score for each client, so I know which clients need data cleanup.

**Features**:
- Score completeness per client (0-100) - 3h
- Track improvements over time - 2h

**Scoring Algorithm**:
```python
def calculate_data_quality_score(business_id: str) -> int:
    """Calculate data quality score (0-100)."""
    score = 100
    
    # Deduct points for missing data
    bills = get_bills(business_id)
    for bill in bills:
        if not bill.payment_method:
            score -= 2
        if not bill.due_date:
            score -= 2
    
    invoices = get_invoices(business_id)
    for invoice in invoices:
        if not invoice.due_date:
            score -= 2
    
    # Deduct points for unmatched bank transactions
    unmatched_count = count_unmatched_bank_transactions(business_id)
    score -= (unmatched_count * 1)
    
    return max(0, score)
```

**UI Integration**: Show in Client List view as badge

**Estimated Effort**: 5 hours

---

#### **POS Integration (Square/Toast/Clover) - 15h**

**User Story**: As an advisor for restaurants/retail, I want to see daily sales data so I can estimate payroll timing and cash needs.

**Features**:
- Research Square, Toast, Clover APIs - 3h
- Pull daily sales data - 8h
- Estimate payroll from sales patterns - 4h

**New Models**:
```python
# domains/bank/models/pos_integration.py
class POSIntegration(Base):
    __tablename__ = "pos_integrations"
    
    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    provider = Column(String)  # square, toast, clover
    api_token = Column(String, encrypted=True)
    active = Column(Boolean, default=True)

# domains/bank/models/daily_sales.py
class DailySales(Base):
    __tablename__ = "daily_sales"
    
    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    date = Column(Date)
    gross_sales = Column(Float)
    net_sales = Column(Float)
    transaction_count = Column(Integer)
```

**Estimated Effort**: 15 hours

---

### **2.2: Async Client Communication (40h)**

**Why This Matters**: Tier 2 is about enabling advisors to scale by working async with clients.

#### **Client Portal - 20h**

**User Story**: As an advisor, I want to send my client a link where they can upload documents or answer questions, so I don't have to email back and forth.

**Features**:
- Generate deeplinks for client input - 8h
- Client uploads documents - 6h
- Client approves decisions - 6h

**New Models**:
```python
# advisor/communication/models/portal_request.py
class PortalRequest(Base):
    __tablename__ = "portal_requests"
    
    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    advisor_id = Column(String, ForeignKey("advisors.advisor_id"))
    
    request_type = Column(String)  # document_upload, approval, question
    deeplink_token = Column(String, unique=True)
    expires_at = Column(DateTime)
    
    # Request details
    prompt_text = Column(String)
    required_documents = Column(JSONB)
    
    # Response tracking
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    response_data = Column(JSONB)
```

**API Endpoints**:
- `POST /api/v1/advisor/portal/request` - Create portal request
- `GET /portal/{token}` - Client-facing portal page
- `POST /portal/{token}/submit` - Client submits response

**Estimated Effort**: 20 hours

---

#### **Email Interactions - 15h**

**User Story**: As an advisor, I want to send questions to my clients via email and track their responses in one place.

**Features**:
- Send questions to clients - 6h
- Track responses - 5h
- Activity log - 4h

**New Models**:
```python
# advisor/communication/models/email_interaction.py
class EmailInteraction(Base):
    __tablename__ = "email_interactions"
    
    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    advisor_id = Column(String, ForeignKey("advisors.advisor_id"))
    
    sent_at = Column(DateTime)
    subject = Column(String)
    body = Column(String)
    
    # Response tracking
    responded_at = Column(DateTime, nullable=True)
    response_body = Column(String, nullable=True)
    status = Column(String)  # sent, opened, responded, expired
```

**Estimated Effort**: 15 hours

---

#### **Notification System - 5h**

**User Story**: As an advisor, I want to be notified when a client responds to my request, so I don't have to keep checking.

**Features**:
- Notify advisor of client actions - 3h
- Email/SMS alerts - 2h

**Estimated Effort**: 5 hours

---

### **2.3: Smart Features - Level 1 (50h)**

**Why This Matters**: Tier 2 adds intelligence to help advisors make better decisions faster.

#### **Smart Prioritization - 20h**

**User Story**: As an advisor, I want the system to suggest which bills I should pay first, so I don't have to manually prioritize.

**Features**:
- AI-powered bill payment ordering - 10h
- Optimize for runway extension - 10h

**Algorithm**:
```python
def prioritize_bills(bills: List[Bill], current_cash: float) -> List[Bill]:
    """Prioritize bills by payment urgency and runway impact."""
    
    scored_bills = []
    for bill in bills:
        score = 0
        
        # Factor 1: Days until due (more urgent = higher score)
        days_until_due = (bill.due_date - date.today()).days
        if days_until_due < 0:
            score += 100  # Overdue - highest priority
        else:
            score += max(0, 30 - days_until_due)  # Due soon
        
        # Factor 2: Vendor relationship importance
        if bill.vendor.is_critical:
            score += 50
        
        # Factor 3: Late fee risk
        if bill.has_late_fee_terms:
            score += 20
        
        # Factor 4: Runway impact (smaller bills = higher score if low cash)
        if current_cash < 10000:
            score += (1000 / bill.amount) * 10
        
        scored_bills.append((bill, score))
    
    # Sort by score descending
    scored_bills.sort(key=lambda x: x[1], reverse=True)
    return [bill for bill, score in scored_bills]
```

**Estimated Effort**: 20 hours

---

#### **Payment Recommendations - 20h**

**User Story**: As an advisor, I want the system to suggest a payment plan, so I can quickly review and approve.

**Features**:
- AI-suggested payment plans - 15h
- Runway impact preview - 5h

**Algorithm**:
```python
def recommend_payment_plan(
    bills: List[Bill],
    current_cash: float,
    min_runway_days: int = 30
) -> PaymentPlan:
    """Recommend which bills to pay now vs delay."""
    
    prioritized_bills = prioritize_bills(bills, current_cash)
    
    pay_now = []
    delay = []
    
    remaining_cash = current_cash
    daily_burn = calculate_daily_burn(business_id)
    
    for bill in prioritized_bills:
        # Check if we can afford this bill while maintaining min runway
        if remaining_cash - bill.amount >= (min_runway_days * daily_burn):
            pay_now.append(bill)
            remaining_cash -= bill.amount
        else:
            delay.append(bill)
    
    return PaymentPlan(
        pay_now=pay_now,
        delay=delay,
        runway_impact={
            "before": current_cash / daily_burn,
            "after": remaining_cash / daily_burn
        }
    )
```

**Estimated Effort**: 20 hours

---

#### **Customer Payment Profiles - 10h**

**User Story**: As an advisor, I want to see which customers pay on time vs late, so I can adjust my collection timing.

**Features**:
- Track who pays on time vs late - 6h
- Adjust AR collection timing - 4h

**Algorithm**:
```python
def calculate_payment_reliability(customer_id: str) -> float:
    """Calculate customer payment reliability score (0-100)."""
    
    invoices = get_customer_invoices(customer_id)
    
    on_time_count = 0
    late_count = 0
    
    for invoice in invoices:
        if invoice.paid_date:
            days_late = (invoice.paid_date - invoice.due_date).days
            if days_late <= 0:
                on_time_count += 1
            else:
                late_count += 1
    
    total = on_time_count + late_count
    if total == 0:
        return 50  # No history, assume neutral
    
    return (on_time_count / total) * 100
```

**Estimated Effort**: 10 hours

---

## **PHASE 2 SUMMARY**

**Total Timeline**: 3-4 months  
**Total Effort**: 150 hours

**Features Delivered**:
- ✅ Bank feed integration (Plaid) - $10/mo add-on
- ✅ Missing bill detection
- ✅ Data quality scoring
- ✅ POS integration (Square/Toast/Clover)
- ✅ Client portal (deeplinks)
- ✅ Email interactions
- ✅ Notification system
- ✅ Smart prioritization
- ✅ Payment recommendations
- ✅ Customer payment profiles

---

### **PHASE 2 SUCCESS CRITERIA**

**Upgrade & Adoption**:
- ✅ 50% of Tier 1 advisors upgrade to Tier 2
- ✅ 85%+ data quality score across clients
- ✅ 3+ client portal requests per week per advisor
- ✅ <5% churn rate

**Smart Feature Performance**:
- ✅ 80%+ advisors use earmarking feature
- ✅ 70%+ collection email response rate
- ✅ 85%+ payment matching accuracy (bulk deposits)
- ✅ Variance alerts <1 per client per day (aggregated)

**Time Savings**:
- ✅ 2-3 hours saved per client per week
- ✅ Advisors manage 5-10 more clients than Tier 1

**Quality**:
- ✅ Smart prioritization matches advisor intuition 85%+ of time
- ✅ Auto-pause collections on payment 95%+ success rate

---

## **🚀 PHASE 3: TIER 3 FEATURES ($250/client/month)**

**Goal**: Advanced forecasting and intelligence for premium advisory work

**Timeline**: 4-5 months after Phase 2 launch  
**Effort**: 130 hours  
**Success Criteria**: 30% of Tier 2 advisors upgrade to Tier 3

### **3.1: Advanced Runway & Forecasting (60h)**

#### **13-Week Cash Forecast - 25h**

**User Story**: As an advisor, I want to see a 13-week cash forecast, so I can have strategic conversations with my clients about future cash needs.

**Features**:
- Predictive runway scenarios - 15h
- Week-by-week forecast - 8h
- Confidence intervals - 2h

**Algorithm**:
```python
def generate_13_week_forecast(business_id: str) -> ForecastData:
    """Generate 13-week cash forecast with confidence intervals."""
    
    # Get historical data
    historical_burn = get_historical_daily_burn(business_id, days=90)
    historical_revenue = get_historical_daily_revenue(business_id, days=90)
    
    # Get scheduled items
    scheduled_bills = get_scheduled_bills(business_id, weeks=13)
    expected_invoices = get_expected_invoice_payments(business_id, weeks=13)
    
    forecast = []
    current_cash = get_current_cash_balance(business_id)
    
    for week in range(1, 14):
        # Predict burn (with confidence interval)
        predicted_burn = {
            "low": historical_burn.percentile(25),
            "mid": historical_burn.mean(),
            "high": historical_burn.percentile(75)
        }
        
        # Predict revenue
        predicted_revenue = {
            "low": historical_revenue.percentile(25),
            "mid": historical_revenue.mean(),
            "high": historical_revenue.percentile(75)
        }
        
        # Calculate net cash flow
        net_cash_flow = predicted_revenue["mid"] - predicted_burn["mid"]
        current_cash += net_cash_flow
        
        forecast.append({
            "week": week,
            "ending_cash": current_cash,
            "burn": predicted_burn,
            "revenue": predicted_revenue,
            "runway_days": current_cash / predicted_burn["mid"]
        })
    
    return forecast
```

**Estimated Effort**: 25 hours

---

#### **Scenario Analysis ("What If") - 25h**

**User Story**: As an advisor, I want to model different scenarios (e.g., "What if we delay this bill?"), so I can show my client the impact of different decisions.

**Features**:
- Model different decisions - 15h
- Compare outcomes - 8h
- Stress testing - 2h

**UI Features**:
- Create scenario (copy current state)
- Modify bills/invoices in scenario
- Run forecast with modifications
- Compare side-by-side with baseline

**Estimated Effort**: 25 hours

---

#### **Budget Constraints - 10h**

**User Story**: As an advisor, I want to set budget limits for my client, so I can alert them when they're overspending.

**Features**:
- Set budget limits - 4h
- Track against budget - 4h
- Alert on overages - 2h

**New Models**:
```python
# domains/policy/models/budget.py
class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    
    category = Column(String)  # "payroll", "rent", "utilities", etc.
    monthly_limit = Column(Float)
    alert_threshold = Column(Float)  # Alert at 80% of limit
```

**Estimated Effort**: 10 hours

---

### **3.2: Collections & AR Automation (40h)**

#### **3-Stage Email Sequences - 20h**

**User Story**: As an advisor, I want to automatically send collection emails at 30/45/60 days overdue, so I don't have to manually track and email.

**Features**:
- 30d gentle reminder - 8h
- 45d urgent notice - 8h
- 60d final warning - 4h

**Email Templates**:
```python
# templates/collections/gentle.html (30 days)
GENTLE_REMINDER = """
Hi {customer_name},

Just a friendly reminder that invoice #{invoice_number} for ${amount} was due on {due_date}.

If you've already paid, please disregard this email. Otherwise, we'd appreciate payment at your earliest convenience.

Thank you!
{business_name}
"""

# templates/collections/urgent.html (45 days)
URGENT_NOTICE = """
Hi {customer_name},

Invoice #{invoice_number} for ${amount} is now 45 days overdue. We need to receive payment by {deadline} to avoid late fees.

Please contact us if you have any questions.

{business_name}
"""

# templates/collections/final.html (60 days)
FINAL_WARNING = """
Hi {customer_name},

This is a final notice that invoice #{invoice_number} for ${amount} is now 60 days overdue.

If we don't receive payment by {deadline}, we may need to escalate to collections.

Please contact us immediately.

{business_name}
"""
```

**Estimated Effort**: 20 hours

---

#### **Priority Scoring - 10h**

**User Story**: As an advisor, I want to see which overdue invoices to prioritize, so I focus on the highest-value collections.

**Features**:
- Score by amount, age, customer history - 6h
- Prioritize collection efforts - 4h

**Algorithm**:
```python
def prioritize_collections(overdue_invoices: List[Invoice]) -> List[Invoice]:
    """Prioritize overdue invoices by collection urgency."""
    
    scored_invoices = []
    
    for invoice in overdue_invoices:
        score = 0
        
        # Factor 1: Amount (higher = more urgent)
        score += invoice.amount / 100
        
        # Factor 2: Days overdue (more overdue = more urgent)
        days_overdue = (date.today() - invoice.due_date).days
        score += days_overdue * 2
        
        # Factor 3: Customer reliability (less reliable = more urgent)
        reliability = get_customer_payment_reliability(invoice.customer_id)
        score += (100 - reliability)
        
        scored_invoices.append((invoice, score))
    
    scored_invoices.sort(key=lambda x: x[1], reverse=True)
    return [invoice for invoice, score in scored_invoices]
```

**Estimated Effort**: 10 hours

---

#### **Auto-Pause on Payment - 10h**

**User Story**: As an advisor, I want collection emails to automatically stop when a customer pays, so I don't send embarrassing follow-ups.

**Features**:
- Detect payments - 5h
- Pause collection sequence - 5h

**Implementation**:
```python
# domains/ar/services/collections_automation.py
def handle_payment_received(invoice_id: str):
    """Auto-pause collections when payment is detected."""
    
    # Find active collection sequence
    sequence = get_active_collection_sequence(invoice_id)
    
    if sequence:
        # Mark as complete
        sequence.status = "completed"
        sequence.completed_at = datetime.now()
        sequence.completion_reason = "payment_received"
        
        # Cancel any scheduled emails
        cancel_scheduled_emails(sequence.id)
```

**Estimated Effort**: 10 hours

---

### **3.3: Analytics & Insights (45h)**

#### **Runway Flowband Visualization - 15h**

**User Story**: As an advisor, I want to see a visual timeline of upcoming cash events (bills, invoices, payroll) so I can understand the client's cash flow story at a glance.

**Features**:
- Signature sparse visualization (top-N events, 8-12 max)
- Chart.js streamplot with coral/green/red segments for AR/AP events
- Payroll markers with risk states
- Drag-and-drop events for "What If" scenarios (Tier 3)
- List Mode parity for accessibility

**Why This Matters**: This is the **signature visual** that makes RowCol feel intelligent, not just another spreadsheet.

**Performance Requirements**:
- Flowband renders <300ms
- ≤25 event pills maximum
- Smooth animations, responsive interactions

**Success Criteria**:
- ≥70% pilots mention Flowband positively
- ≥30% AP/AR actions initiated from Flowband
- Loads instantly, feels delightful

**Files**:
- `runway/services/flowband_data.py` - Event aggregation
- `templates/components/runway_flowband.html` - Visualization
- UI components for event pills, timeline

**Estimated Effort**: 15 hours

---

#### **Executive Narrative Dashboard - 15h**

**User Story**: As an advisor, I want a story-driven dashboard that answers "Where am I? What changed? What do I do now?" so I can quickly understand client state.

**Features**:
- Narrative-first microcopy throughout interface
- Story-driven dashboard (not data dump)
- Actionable insight cards with explicit runway deltas
- Replace circular gauges with RunwayCoverageBar (linear indicators)

**Design Principles** (from ui/PLAYBOOK.md):
- Reads like advisor insights, not accounting jargon
- Prioritizes actions, not just data
- Connects data to decisions
- Feels professional, not utilitarian

**Why Tier 3**: This elevates from "tools" to "advisory insights"

**Success Criteria**:
- Dashboard loads <3s with narrative generation
- Reads like insights, not data
- 85%+ advisors say it helps client conversations

**Files**:
- `runway/services/narrative_generator.py` - Story generation
- `templates/executive_dashboard.html` - Dashboard layout
- UI components for insight cards

**Estimated Effort**: 15 hours

---

### **3.4: Optimization & Intelligence (30h)**

#### **Vendor Payment Optimization - 15h**

**User Story**: As an advisor, I want to optimize when I pay vendors to maximize runway, so my client has more cash cushion.

**Features**:
- Optimize payment timing - 10h
- Maximize cash runway - 5h

**Algorithm**:
```python
def optimize_vendor_payment_timing(
    bills: List[Bill],
    current_cash: float,
    min_runway_days: int = 30
) -> OptimizedPlan:
    """Optimize payment timing to maximize runway."""
    
    # Sort bills by latest safe pay date (without penalties)
    bills_with_safe_dates = []
    for bill in bills:
        latest_safe_date = calculate_latest_safe_pay_date(bill)
        bills_with_safe_dates.append((bill, latest_safe_date))
    
    bills_with_safe_dates.sort(key=lambda x: x[1])
    
    # Schedule payments as late as possible while maintaining runway
    optimized_schedule = []
    for bill, safe_date in bills_with_safe_dates:
        # Can we delay this bill to the safe date?
        if can_afford_at_date(bill, safe_date, current_cash, min_runway_days):
            optimized_schedule.append({
                "bill": bill,
                "recommended_pay_date": safe_date,
                "runway_impact": calculate_delay_benefit(bill, date.today(), safe_date)
            })
    
    return optimized_schedule
```

**Estimated Effort**: 15 hours

---

#### **Industry Benchmarking - 15h**

**User Story**: As an advisor, I want to compare my client's metrics to industry standards, so I can show them how they're performing.

**Features**:
- Compare to peers - 10h
- Industry standards - 5h

**Metrics to Benchmark**:
- Days of runway (by industry)
- Average days to collect AR (by industry)
- Average days to pay AP (by industry)
- Cash conversion cycle

**Estimated Effort**: 15 hours

---

## **PHASE 3 SUMMARY**

**Total Timeline**: 4-5 months  
**Total Effort**: 130 hours

**Features Delivered**:
- ✅ 2-4 week cash flow forecasting (prerequisite)
- ✅ 13-week cash forecast (strategic)
- ✅ Scenario analysis ("what if")
- ✅ Budget constraints
- ✅ Collections automation (3-stage emails)
- ✅ AR priority scoring
- ✅ Auto-pause on payment
- ✅ Vendor payment optimization
- ✅ Industry benchmarking (RMA/NAICS integration)
- ✅ Executive narrative dashboard
- ✅ Customer payment profiles

---

### **PHASE 3 SUCCESS CRITERIA**

**Upgrade & Adoption**:
- ✅ 30% of Tier 2 advisors upgrade to Tier 3
- ✅ Advisors use scenario analysis 2+ times per month
- ✅ 90%+ advisors reference benchmarks in client meetings
- ✅ <3% churn rate

**Analytics Accuracy**:
- ✅ 90%+ forecasting accuracy over 7-day window
- ✅ 75%+ forecasting accuracy over 14-day window
- ✅ Financial ratio calculations match CPA standards within 0.1%
- ✅ Industry benchmarks feel credible to CPA-trained users

**Advisory Impact**:
- ✅ Collections automation reduces AR aging by 20%
- ✅ Scenario modeling shows measurable runway impact within 5%
- ✅ Executive dashboard loads <3s with narrative generation
- ✅ Benchmark comparisons connect to RMA/Sageworks successfully

**User Experience**:
- ✅ Narrative dashboard reads like advisor insights
- ✅ What-if scenarios accurately model runway impact
- ✅ Customer payment profiles predict timing within ±5 days

---

## **🚀 PHASE 4: TIER 4 FEATURES (ENTERPRISE)**

**Goal**: Multi-advisor practices with staff and workflow management

**Timeline**: 4-5 months after Phase 3 launch  
**Effort**: 120 hours  
**Success Criteria**: 10+ enterprise practices signed

### **4.1: Multi-Advisor Foundation (40h)**

#### **Practice Hierarchy - 20h**

**User Story**: As a practice owner, I want to add multiple advisors to my practice, so we can all use RowCol together.

**New Models**:
```python
# advisor/practice/models/practice.py
class Practice(Base):
    __tablename__ = "practices"
    
    practice_id = Column(String, primary_key=True)
    name = Column(String)
    owner_advisor_id = Column(String, ForeignKey("advisors.advisor_id"))
    
    # Enterprise tier settings
    enterprise_tier = Column(String)  # "basic", "premium"
    max_advisors = Column(Integer)
    max_clients = Column(Integer)

# Update advisor model to include practice_id
class Advisor(Base):
    # ... existing fields
    practice_id = Column(String, ForeignKey("practices.practice_id"), nullable=True)
    role_in_practice = Column(String, nullable=True)  # "owner", "senior", "junior", "staff"
```

**Estimated Effort**: 20 hours

---

#### **Staff RBAC - 20h**

**User Story**: As a practice owner, I want to assign different permission levels to staff, so junior staff can't make risky decisions.

**Roles**:
- **Owner**: Full access to all clients and settings
- **Senior Advisor**: Full access to assigned clients
- **Junior Advisor**: View-only access to assigned clients
- **Staff**: Limited access (e.g., data entry only)

**Permissions System**:
```python
# advisor/practice/services/rbac.py
ROLE_PERMISSIONS = {
    "owner": [
        "view_all_clients",
        "edit_all_clients",
        "execute_payments",
        "manage_staff",
        "manage_settings"
    ],
    "senior": [
        "view_assigned_clients",
        "edit_assigned_clients",
        "execute_payments"
    ],
    "junior": [
        "view_assigned_clients"
    ],
    "staff": [
        "view_assigned_clients",
        "enter_data"
    ]
}

def can_perform_action(advisor: Advisor, action: str, business_id: str) -> bool:
    """Check if advisor can perform action on this business."""
    
    # Get advisor's role in practice
    if not advisor.practice_id:
        # Solo advisor, full permissions
        return True
    
    role = advisor.role_in_practice
    
    # Check role permissions
    if action not in ROLE_PERMISSIONS.get(role, []):
        return False
    
    # Check client assignment
    if "all_clients" not in ROLE_PERMISSIONS[role]:
        if not is_client_assigned(advisor.advisor_id, business_id):
            return False
    
    return True
```

**Estimated Effort**: 20 hours

---

### **4.2: Practice Management (50h)**

#### **Multi-Advisor Dashboard - 20h**

**User Story**: As a practice owner, I want to see all clients across all advisors in one view, so I can manage workload and identify bottlenecks.

**Features**:
- See all clients across all advisors - 10h
- Practice-wide analytics - 8h
- Staff utilization - 2h

**New Views**:
- Practice Overview: All clients, all advisors
- Workload by Advisor: Clients per advisor, hours worked
- Client Health: Runway distribution across practice
- Revenue by Advisor: Track billable work

**Estimated Effort**: 20 hours

---

#### **Workflow Assignment - 20h**

**User Story**: As a practice owner, I want to assign clients to staff members, so I can balance workload across the team.

**Features**:
- Assign clients to staff - 10h
- Task management - 8h
- Workload balancing - 2h

**New Models**:
```python
# advisor/practice/models/client_assignment.py
class ClientAssignment(Base):
    __tablename__ = "client_assignments"
    
    id = Column(String, primary_key=True)
    practice_id = Column(String, ForeignKey("practices.practice_id"))
    advisor_id = Column(String, ForeignKey("advisors.advisor_id"))
    business_id = Column(String, ForeignKey("businesses.id"))
    
    role = Column(String)  # "primary", "secondary", "reviewer"
    assigned_at = Column(DateTime)
    assigned_by = Column(String, ForeignKey("advisors.advisor_id"))
```

**Estimated Effort**: 20 hours

---

#### **Practice Analytics - 10h**

**User Story**: As a practice owner, I want to see analytics across my entire portfolio, so I can identify trends and optimize operations.

**Features**:
- Benchmark across portfolio - 6h
- Revenue per advisor - 2h
- Client profitability - 2h

**Analytics Metrics**:
- Average runway days across practice
- Total clients at risk
- Average time to close runway review
- Revenue per client
- Advisor utilization rate

**Estimated Effort**: 10 hours

---

### **4.3: White-Label & Customization (30h)**

#### **Branding Options - 15h**

**User Story**: As a practice owner, I want to use my own branding on all client-facing materials, so RowCol looks like my firm's tool.

**Features**:
- Upload practice logo - 5h
- Custom primary color - 5h
- Custom domain (optional) - 5h

**Settings Page**:
```python
# advisor/practice/models/branding.py
class PracticeBranding(Base):
    __tablename__ = "practice_branding"
    
    practice_id = Column(String, ForeignKey("practices.practice_id"), primary_key=True)
    
    logo_url = Column(String)
    primary_color = Column(String)  # Hex color code
    custom_domain = Column(String, nullable=True)
    
    # Email branding
    from_name = Column(String)  # e.g., "Smith & Associates"
    from_email = Column(String)  # e.g., "noreply@smithcpa.com"
```

**Estimated Effort**: 15 hours

---

#### **Client-Facing Reports - 15h**

**User Story**: As a practice owner, I want all client-facing reports to have my practice's branding, so it looks professional.

**Features**:
- Practice branding on all exports - 8h
- Custom letterhead - 5h
- White-label client portal - 2h

**Branded Outputs**:
- PDF exports (with practice logo/letterhead)
- Email templates (with practice branding)
- Client portal (with custom domain)

**Estimated Effort**: 15 hours

---

## **PHASE 4 SUMMARY**

**Total Timeline**: 4-5 months  
**Total Effort**: 120 hours

**Features Delivered**:
- ✅ Practice hierarchy (`practice_id`)
- ✅ Staff RBAC (4 role levels)
- ✅ Client assignment
- ✅ Multi-advisor dashboard
- ✅ Workflow assignment
- ✅ Practice analytics
- ✅ White-label branding
- ✅ Custom domain
- ✅ Branded client-facing reports
- ✅ Budget-based automation rules
- ✅ Conditional scheduled payments
- ✅ Runway protection automation

---

### **PHASE 4 SUCCESS CRITERIA**

**Enterprise Adoption**:
- ✅ 10+ enterprise practices signed
- ✅ Average 5+ advisors per practice
- ✅ 95%+ staff adoption rate
- ✅ <2% churn rate

**Automation Performance**:
- ✅ 95%+ automation rule execution success rate
- ✅ Dry-run mode prevents 100% of unintended actions
- ✅ Rule confidence scoring correlates with actual performance >80%
- ✅ Zero unintended approvals (guardrails work)

**Practice Management**:
- ✅ Practice owners report 10+ hours saved per week
- ✅ Advisors manage 2x more clients than without automation
- ✅ Workload balancing reduces bottlenecks by 40%

**White-Label Quality**:
- ✅ Branded reports match practice visual identity
- ✅ Custom domains work reliably
- ✅ Email delivery from practice domains >95%

---

## **🎯 COMPLETE DEVELOPMENT TIMELINE**

```
Phase 1 (Tier 1):   4 weeks      = 140 hours = $50/client/month
Phase 2 (Tier 2):   3-4 months   = 150 hours = $125/client/month
Phase 3 (Tier 3):   4-5 months   = 130 hours = $250/client/month
Phase 4 (Tier 4):   4-5 months   = 120 hours = Enterprise
───────────────────────────────────────────────────────────────
Total:              12-15 months = 540 hours = Full runway/ product
```

---

## **📊 REVENUE PROJECTIONS**

### **Year 1 (Phase 1-2)**
```
Target: 100 advisors
Mix: 70% Tier 1 ($50), 30% Tier 2 ($125)
Avg clients per advisor: 10

Revenue:
70 advisors × 10 clients × $50 = $35,000 MRR
30 advisors × 10 clients × $125 = $37,500 MRR
────────────────────────────────────────────
Total: $72,500 MRR = $870,000 ARR
```

### **Year 2 (Phase 3-4)**
```
Target: 500 advisors
Mix: 40% Tier 1, 40% Tier 2, 15% Tier 3, 5% Tier 4 (Enterprise)
Avg clients per advisor: 12

Revenue:
200 advisors × 12 clients × $50 = $120,000 MRR
200 advisors × 12 clients × $125 = $300,000 MRR
75 advisors × 12 clients × $250 = $225,000 MRR
25 advisors × 12 clients × $300 = $90,000 MRR (Enterprise avg)
────────────────────────────────────────────
Total: $735,000 MRR = $8.8M ARR
```

---

## **✅ SUCCESS METRICS BY PHASE**

### **Phase 1 Success:**
- ✅ 10 paying advisors
- ✅ 100+ client accounts
- ✅ 80%+ weekly active rate
- ✅ <30 min per client per week
- ✅ 90%+ retention after 30 days

### **Phase 2 Success:**
- ✅ 50% of Tier 1 upgrade to Tier 2
- ✅ 85%+ data quality score across clients
- ✅ 3+ client portal requests per week per advisor
- ✅ <5% churn rate

### **Phase 3 Success:**
- ✅ 30% of Tier 2 upgrade to Tier 3
- ✅ Advisors use scenario analysis 2+ times per month
- ✅ Collections automation reduces AR aging by 20%
- ✅ <3% churn rate

### **Phase 4 Success:**
- ✅ 10+ enterprise practices signed
- ✅ Average 5+ advisors per practice
- ✅ 95%+ staff adoption rate
- ✅ <2% churn rate

---

## **🚨 CRITICAL DEPENDENCIES**

### **External Dependencies:**
- Plaid API (Phase 2) - $0.50/transaction
- Square/Toast/Clover APIs (Phase 2) - Free or negotiated rates
- Email service (Phase 2-3) - SendGrid or similar
- SMS service (Phase 2) - Twilio or similar

### **Infrastructure Dependencies:**
- Database migration (`firm_id` → `advisor_id`) - MUST complete before Phase 1
- QBO OAuth flow - Already exists in `infra/qbo/setup`
- Feature gating system - Phase 1 Week 1
- `advisor/` layer - Phase 1 Week 1

### **Technical Debt:**
- QBO mocking cleanup - 21h (separate work stream)
- Real data integration - Part of Phase 1
- Test coverage - Ongoing

---

## **📚 RELATED DOCUMENTS**

### **Build Plan Documents** (`docs/build_plan/`)
- **`0_BUILD_PLAN_PHASE1_RUNWAY_DETAILED.md`** - Week-by-week Phase 1 execution plan
- **`1_BUILD_PLAN_PHASE2_SMART_TIER.md`** - Detailed Tier 2 smart features plan
- **`2_SMART_FEATURES_REFERENCE.md`** - Complete smart features catalog (Tier 1-4)
- **`PRODUCTION_READINESS_CHECKLIST.md`** - Pre-deployment production checklist

### **Strategic Documents** (`docs/product/`)
- **`PLATFORM_VISION.md`** - Complete 3-product platform strategy
- **`ADVISOR_FIRST_ARCHITECTURE.md`** - Technical architecture foundation
- **`TWO_BRAND_STRATEGY.md`** - RowCol/Oodaloo/Escher.cpa strategy
- **`RowCol_Cash_Runway_Ritual.md`** - Shareable positioning document
- **`THREAD_PORT_DOCUMENTATION_V2.md`** - Thread continuity context

### **Reference Materials** (`docs/archive/`)
- **`build_plan_v5.md`** - Original V5 build plan (reference for UI/UX standards, testing approach, legal language)

---

## **Document Status**

*Last Updated: 2025-10-01*  
*Status: Complete Multi-Phase Build Plan*  
*Next Review: After Phase 1 completion*

**Note**: This document supersedes `BUILD_PLAN_FIRM_FIRST_V6.0.md` and provides the complete roadmap for RowCol's runway/ product across all tiers.

