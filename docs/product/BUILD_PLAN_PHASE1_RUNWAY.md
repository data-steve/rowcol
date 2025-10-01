# Build Plan: Phase 1 - runway/ MVP

*Ship the $50/client/month Advisor Console*

---

## **Phase 1 Goal: Prove the Value Hypothesis**

**Hypothesis:** Advisors will pay $50/client/month for a tool that replaces their cash flow spreadsheets with a 3-tab console (Digest + Tray + Console) that saves them 2-4 hours/week per client.

**Success Criteria:**
- ✅ 10 paying advisors
- ✅ Used daily for client work
- ✅ Advisor says "I can't go back to spreadsheets"
- ✅ Average 30+ minutes saved per client per week

---

## **What We're Building (Tier 1: $50/client/month)**

### **The Core Experience:**

```
ADVISOR OPENS APP:
└── Client List View (advisor/client_management/)
    ├── See all clients
    ├── Sort by "Last worked" (ritual cadence tracking)
    ├── Visual health indicators (green/yellow/red)
    └── Click client → Opens 3-tab view

ADVISOR CLICKS CLIENT:
└── 3-Tab Client View
    ├── Tab 1: DIGEST (runway/experiences/digest/)
    │   ├── Cash position: "47 days of runway"
    │   ├── Bills due this week: "$12,500"
    │   ├── Overdue AR: "$8,300"
    │   └── Recent activity feed
    ├── Tab 2: HYGIENE TRAY (runway/experiences/tray/)
    │   ├── Progress: "7 of 12 items fixed"
    │   ├── Cash-related issues only:
    │   │   ├── Bills missing payment method
    │   │   ├── Invoices missing due date
    │   │   └── Bank balance warnings
    │   └── Click item → Fix inline or deeplink to QBO
    └── Tab 3: DECISION CONSOLE (runway/experiences/console/)
        ├── Progress: "3 of 8 decisions made"
        ├── Bills to pay:
        │   ├── Checkbox list
        │   ├── Runway impact preview
        │   └── "Pay now" or "Schedule" button
        ├── AR to collect:
        │   ├── Checkbox list
        │   └── "Send reminder" button
        └── "Finalize all decisions" button → Batch execution
```

---

## **What We're NOT Building (Tier 2+ Features)**

To ship fast and prove value, we're explicitly NOT building:

❌ **Client Portal** (Tier 2: $125/client/month)
❌ **Email Interactions** (Tier 2: $125/client/month)
❌ **Smart Prioritization** (Tier 2: $125/client/month)
❌ **Payment Recommendations** (Tier 2: $125/client/month)
❌ **Plaid Integration** (Tier 2 add-on: $10/client/month)
❌ **13-Week Forecast** (Tier 3: $250/client/month)
❌ **Scenario Analysis** (Tier 3: $250/client/month)
❌ **Practice Management** (Tier 4: Enterprise)
❌ **TestDrive Experience** (Owner-first feature, not advisor workflow)
❌ **Friday Digest Email** (Owner-first feature, not advisor workflow)

**Why:** These are valuable upsells, but NOT required to prove the core value hypothesis.

---

## **Technical Foundation (Must Complete First)**

### **1. Database Migration: `firm_id` → `advisor_id`**

**Why:** "Firm" is ambiguous - could mean individual advisor or multi-advisor practice. "Advisor" is clear.

**Migration:**
```sql
-- Rename tables
ALTER TABLE firms RENAME TO advisors;

-- Rename columns
ALTER TABLE advisors RENAME COLUMN firm_id TO advisor_id;
ALTER TABLE businesses RENAME COLUMN firm_id TO advisor_id;
-- ... update all foreign keys

-- Add subscription tier tracking
ALTER TABLE advisors ADD COLUMN runway_tier VARCHAR(50) DEFAULT 'basic';
ALTER TABLE advisors ADD COLUMN feature_flags JSONB DEFAULT '{}';
```

**Files to Update:**
- All model files (replace `firm_id` with `advisor_id`)
- All service files (replace `firm_id` with `advisor_id`)
- All route files (replace `firm_id` with `advisor_id`)
- ADR-003 multi-tenancy document (update hierarchy)

**Estimated Effort:** 4-6 hours

---

### **2. Create `advisor/` Layer**

**Why:** Advisor workflow features (client list, subscription management) don't belong in `runway/` - they're cross-product.

**Structure:**
```
advisor/
├── __init__.py
├── client_management/
│   ├── __init__.py
│   ├── models/
│   │   ├── advisor.py              # Advisor entity (renamed from firm.py)
│   │   └── subscription.py         # Subscription tier management
│   ├── services/
│   │   ├── client_list_service.py  # List all clients, sort by last worked
│   │   └── client_selector_service.py # Select client to work on
│   └── schemas/
│       └── client_list.py          # API response schemas
├── routes/
│   └── client_list.py              # Client list API endpoints
└── README.md                        # Architecture explanation
```

**Estimated Effort:** 6-8 hours

---

### **3. Feature Gating System**

**Why:** Need to gate Tier 2+ features now, even if not built yet.

**Implementation:**
```python
# advisor/client_management/services/feature_gating.py

TIER_FEATURES = {
    "basic": [
        "client_list",
        "tray",
        "console", 
        "digest",
        "basic_runway"
    ],
    "communication": [
        # All basic features, plus:
        "client_portal",
        "email_interactions",
        "smart_priority",
        "payment_recommendations"
    ],
    "intelligence": [
        # All communication features, plus:
        "scenarios",
        "forecasting",
        "insights",
        "advanced_runway"
    ]
}

def can_use_feature(advisor: Advisor, feature: str) -> bool:
    """Check if advisor's tier includes this feature."""
    tier = advisor.runway_tier or "basic"
    return feature in TIER_FEATURES.get(tier, [])
```

**API Middleware:**
```python
@app.before_request
def check_feature_access():
    advisor = get_current_advisor()
    feature = get_requested_feature()
    
    if not can_use_feature(advisor, feature):
        return jsonify({
            "error": "Feature not available in your tier",
            "current_tier": advisor.runway_tier,
            "required_tier": "communication",  # or "intelligence"
            "upgrade_url": "/pricing"
        }), 403
```

**Estimated Effort:** 4 hours

---

## **MVP Feature Development (Priority Order)**

### **Priority 1: Client List View**

**Why:** Advisors need to see all their clients and pick which one to work on.

**User Story:** As an advisor, I want to see all my clients in one place, sorted by how long since I last worked them, so I know which clients need attention.

**Acceptance Criteria:**
- ✅ Shows all clients for logged-in advisor
- ✅ Displays client name, last worked date, health indicator
- ✅ Sortable by: "Last worked", "Needs attention", "Alphabetical"
- ✅ Click client → Opens client view
- ✅ Shows "X items need attention" badge if hygiene tray has issues

**Files to Create:**
- `advisor/client_management/services/client_list_service.py`
- `advisor/routes/client_list.py`
- `advisor/client_management/schemas/client_list.py`

**Files to Update:**
- Add `last_worked_at` timestamp to `businesses` table
- Update `businesses` model with health calculation

**Estimated Effort:** 8 hours

**Blocked By:** Database migration (`firm_id` → `advisor_id`)

---

### **Priority 2: Hygiene Tray (Cash Items Only)**

**Why:** Advisors need to see what needs attention before making cash decisions.

**User Story:** As an advisor, I want to see all cash-related items that need my attention (bills missing payment methods, invoices missing due dates), so I can fix them before making payment decisions.

**Acceptance Criteria:**
- ✅ Shows progress: "7 of 12 items fixed"
- ✅ Lists ONLY cash-related issues:
  - Bills missing payment method
  - Bills missing due date
  - Invoices missing due date
  - Unusual payment amounts (flag for review)
- ✅ Click item → Fix inline OR deeplink to QBO
- ✅ "Mark as reviewed" button (for items advisor can't fix)
- ✅ Updates progress bar as items are fixed

**What's NOT Included:**
- ❌ Uncategorized transactions (bookkeeping, not cash decisions)
- ❌ Chart of accounts issues (bookkeeping, not cash decisions)
- ❌ Tax categorization (tax prep, not cash decisions)

**Files to Update:**
- `runway/experiences/tray/` (already exists, needs cleanup)
- Remove bookkeeping-related checks
- Focus on cash decision blockers only

**Estimated Effort:** 6 hours

**Blocked By:** None (can start immediately)

---

### **Priority 3: Decision Console (Simplified)**

**Why:** Advisors need to make batch payment decisions and see runway impact.

**User Story:** As an advisor, I want to select which bills to pay and which AR to collect, see the runway impact, and execute decisions in one batch, so I can make good cash decisions quickly.

**Acceptance Criteria:**
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

**Simplified for MVP:**
- ❌ No approval workflow (advisor has full authority)
- ❌ No smart prioritization (Tier 2 feature)
- ❌ No payment recommendations (Tier 2 feature)
- ❌ No client portal for owner approval (Tier 2 feature)

**Files to Update:**
- `runway/experiences/console/` (already exists, needs simplification)
- `runway/services/0_data_orchestrators/decision_console_data_orchestrator.py`
- Remove `_process_decision()` stub, implement real payment execution
- Integrate with `domains/ap/services/payment.py` for execution

**Estimated Effort:** 12 hours

**Blocked By:** None (can start immediately)

---

### **Priority 4: Digest Dashboard**

**Why:** Advisors need a snapshot of client cash position when they open a client.

**User Story:** As an advisor, when I open a client, I want to immediately see their cash position (days of runway, bills due, overdue AR), so I understand their current state.

**Acceptance Criteria:**
- ✅ Cash position card: "47 days of runway" with trend indicator
- ✅ Bills due card: "5 bills due this week ($12,500)"
- ✅ Overdue AR card: "3 invoices overdue ($8,300)"
- ✅ Recent activity feed: Last 10 transactions
- ✅ Updates in real-time when decisions are executed

**Files to Update:**
- `runway/experiences/digest/` (already exists, needs cleanup)
- Remove owner-first features (Friday email, etc.)
- Focus on dashboard view only

**Estimated Effort:** 6 hours

**Blocked By:** None (can start immediately)

---

### **Priority 5: Basic Runway Calculator**

**Why:** Need to show "days of runway" throughout the app.

**User Story:** As an advisor, I want to see how many days of cash runway my client has, so I can advise them on payment timing.

**Acceptance Criteria:**
- ✅ Calculates: `runway_days = current_cash / average_daily_burn`
- ✅ Shows in Digest dashboard
- ✅ Updates when payment decisions are executed
- ✅ Shows impact preview in Decision Console

**Files to Update:**
- `runway/services/1_calculators/runway_calculator.py` (already exists)
- Simplify to basic calculation only
- Remove advanced features (scenarios = Tier 3)

**Estimated Effort:** 4 hours

**Blocked By:** None (can start immediately)

---

## **Implementation Timeline**

### **Week 1: Foundation**
- Day 1-2: Database migration (`firm_id` → `advisor_id`)
- Day 3-4: Create `advisor/` layer structure
- Day 5: Feature gating system

**Milestone:** Technical foundation complete, can start building features

---

### **Week 2: Core Features**
- Day 1-2: Client List view
- Day 3: Hygiene Tray cleanup (cash items only)
- Day 4-5: Digest Dashboard cleanup

**Milestone:** Advisor can see all clients and open client view

---

### **Week 3: Decision Making**
- Day 1-3: Decision Console simplification
- Day 4: Basic runway calculator integration
- Day 5: End-to-end testing

**Milestone:** Advisor can make batch payment decisions

---

### **Week 4: Polish & Launch**
- Day 1-2: UI/UX polish
- Day 3: Bug fixes
- Day 4: Beta advisor onboarding
- Day 5: Monitor usage, fix issues

**Milestone:** 10 advisors using it daily

---

## **Testing Strategy**

### **Unit Tests:**
- All calculators have 80%+ coverage
- All services have 80%+ coverage
- Feature gating logic has 100% coverage

### **Integration Tests:**
- Client list → Client view → Execute decisions (full workflow)
- QBO sync works correctly
- Multi-tenant isolation (advisor A can't see advisor B's clients)

### **User Acceptance Testing:**
- 3-5 beta advisors test real client workflows
- Advisor can complete weekly cash ritual in <30 minutes
- No critical bugs that block core workflow

---

## **Success Metrics (First 30 Days)**

### **Adoption Metrics:**
- ✅ 10 paying advisors signed up
- ✅ 100+ client accounts created
- ✅ 500+ payment decisions executed
- ✅ 80%+ weekly active advisor rate

### **Value Metrics:**
- ✅ Average time to complete cash ritual: <30 minutes
- ✅ Advisor NPS: 40+
- ✅ Feature usage: 90%+ use all three tabs (Digest, Tray, Console)
- ✅ Retention: 90%+ continue after 30 days

### **Technical Metrics:**
- ✅ API uptime: 99.5%+
- ✅ QBO sync success rate: 95%+
- ✅ Page load time: <2 seconds
- ✅ Zero data isolation bugs (multi-tenant safety)

---

## **Beta Advisor Recruitment**

### **Target Profile:**
- CPA or bookkeeper serving 5-15 small business clients
- Currently using spreadsheets for cash flow management
- Charges clients $1,000-3,000/month for services
- Tech-savvy enough to try new tools
- Willing to give feedback

### **Recruitment Strategy:**
1. Levi as first beta advisor (validate with his real clients)
2. Levi refers 2-3 other advisors in his network
3. LinkedIn outreach to CAS-focused advisors
4. Accounting subreddit/communities

### **Beta Program:**
- Free for first 3 months
- Weekly feedback calls
- Priority support
- Early access to Tier 2 features when launched

---

## **Post-Launch: Tier 2 Planning**

After proving Tier 1 value with 10 paying advisors, we'll begin Tier 2 development:

### **Tier 2 Focus: Async Client Communication**
- Client portal (deeplinks for client input)
- Email interactions (send questions, get answers)
- Activity log (track client responses)
- Smart prioritization (AI-powered)

**Why This Sequence:**
1. Tier 1 proves core value (spreadsheet replacement)
2. Tier 2 adds scalability (async = serve more clients)
3. Tier 3 adds intelligence (AI-powered insights)

---

## **Key Decisions Made**

### **What We're Saying NO To (For Now):**

1. ❌ **TestDrive Experience** - Owner-first feature, not advisor workflow
2. ❌ **Friday Digest Email** - Owner-first feature, not advisor workflow
3. ❌ **Smart Prioritization** - Nice to have, not required for $50 value prop
4. ❌ **Client Portal** - Valuable, but Tier 2 feature
5. ❌ **Plaid Integration** - Valuable, but Tier 2 add-on
6. ❌ **Practice Management** - Enterprise feature, Phase 4

### **What We're Saying YES To:**

1. ✅ **Client List** - Must have for advisor workflow
2. ✅ **3-Tab View** - Core interface for all product lines
3. ✅ **Hygiene Tray** - Must fix blockers before making decisions
4. ✅ **Decision Console** - Must make batch payment decisions
5. ✅ **Digest Dashboard** - Must see cash position snapshot
6. ✅ **Basic Runway** - Must show days of cash remaining

---

## **Next Actions**

### **This Week:**
1. ✅ Create database migration for `firm_id` → `advisor_id`
2. ✅ Create `advisor/` layer structure
3. ✅ Implement feature gating system
4. ✅ Update Console Payment Workflow design (simplified for advisor-only)

### **Next Week:**
1. ✅ Execute database migration
2. ✅ Build Client List view
3. ✅ Clean up Hygiene Tray (cash items only)
4. ✅ Clean up Digest Dashboard

### **Week After:**
1. ✅ Simplify Decision Console (remove approval layer)
2. ✅ Integrate basic runway calculator
3. ✅ End-to-end testing
4. ✅ Recruit beta advisors

---

**Let's ship the MVP and prove the value hypothesis.**

*Last Updated: 2025-01-27*
*Status: Active Build Plan*
