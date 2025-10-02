# Advisor-First Architecture

*How Oodaloo is Architectured to Support Multi-Product Service Delivery*

---

## **The Architecture Principle**

Oodaloo is built with **four layers** that support **three product lines**:

```
┌─────────────────────────────────────────────────────────────┐
│  Product Lines (Revenue Expansion)                           │
├─────────────────────────────────────────────────────────────┤
│  runway/      bookclose/      tax_prep/                      │
│  (Phase 1)    (Phase 2)       (Phase 3)                      │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  advisor/ (Advisor-Client Workflow Layer)                    │
│  - Client management (list, selector, subscription tiers)    │
│  - Communication (portal, emails, activity log)              │
│  - Practice management (multi-advisor, RBAC, analytics)      │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  domains/ (Business Logic Layer)                             │
│  - AP/AR primitives                                          │
│  - General Ledger                                            │
│  - Tax entities                                              │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  infra/ (Infrastructure Layer)                               │
│  - QBO integration                                           │
│  - Plaid/bank feeds                                          │
│  - Database/auth                                             │
│  - Smart sync patterns                                       │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle:** Build each layer once, use it across all product lines.

---

## **Layer 1: `infra/` (Infrastructure)**

### **Purpose:**
Foundation services that ALL product lines depend on.

### **Structure:**
```
infra/
├── qbo/                    # QuickBooks Online integration
│   ├── client.py           # Raw QBO HTTP client
│   ├── smart_sync.py       # Resilience layer (retry, dedup, rate limiting)
│   └── utils.py            # QBO field parsing, date handling
├── database/
│   ├── session.py          # Database connection management
│   └── transaction.py      # Transaction context managers
├── auth/
│   ├── auth.py             # JWT authentication
│   └── rbac.py             # Role-based access control
├── integrations/           # Third-party integrations
│   ├── plaid/              # Bank feed integration (Tier 2+)
│   ├── stripe/             # Payment processor integration (Tier 2+)
│   └── zapier/             # Workflow automation (Tier 4)
└── config.py               # Configuration management
```

### **Design Principles:**
1. **Build Once, Use Everywhere:** Every product line uses same QBO integration
2. **Multi-Tenant by Default:** All operations scoped by `advisor_id` + `business_id`
3. **Resilience First:** Handle QBO API failures gracefully
4. **Extensible:** Easy to add new integrations (Plaid, Stripe, etc.)

### **Used By:**
- ✅ runway/ (cash flow data from QBO)
- ✅ bookclose/ (transaction data from QBO)
- ✅ tax_prep/ (full year of data from QBO)

---

## **Layer 2: `domains/` (Business Logic)**

### **Purpose:**
Core accounting primitives that ALL product lines use.

### **Structure:**
```
domains/
├── core/
│   ├── models/
│   │   ├── business.py         # Business entity (advisor's client)
│   │   ├── user.py             # User authentication
│   │   └── metadata.py         # Business metadata (state storage)
│   └── services/
│       ├── base_service.py     # TenantAwareService pattern
│       └── auth_service.py     # Authentication logic
├── ap/                          # Accounts Payable
│   ├── models/
│   │   ├── bill.py             # Bill entity
│   │   ├── vendor.py           # Vendor entity
│   │   └── payment.py          # Payment entity
│   └── services/
│       ├── bill_ingestion.py   # Bill CRUD + QBO sync
│       ├── payment.py          # Payment execution
│       └── vendor.py           # Vendor management
├── ar/                          # Accounts Receivable
│   ├── models/
│   │   ├── invoice.py          # Invoice entity
│   │   └── customer.py         # Customer entity
│   └── services/
│       ├── invoice.py          # Invoice CRUD + QBO sync
│       └── collections.py      # Collections workflow
└── gl/                          # General Ledger (bookclose/ feature)
    ├── models/
    │   ├── account.py          # Chart of accounts
    │   ├── transaction.py      # GL transactions
    │   └── journal_entry.py    # Manual journal entries
    └── services/
        ├── categorization.py   # Transaction categorization
        └── reconciliation.py   # Account reconciliation
```

### **Design Principles:**
1. **Domain-Driven Design:** Each subdomain owns its entities and logic
2. **QBO Primitives Only:** No product-line-specific logic here
3. **CRUD + Sync:** Domain services handle database + QBO synchronization
4. **TenantAware:** All services inherit from `TenantAwareService` for multi-tenancy

### **Used By:**
- ✅ runway/ (uses AP/AR for cash decisions)
- ✅ bookclose/ (uses AP/AR/GL for month-end close)
- ✅ tax_prep/ (uses AP/AR/GL for tax preparation)

---

## **Layer 3: `advisor/` (Advisor-Client Workflow)**

### **Purpose:**
Features that support HOW ADVISORS WORK, regardless of which product line they're using.

### **Structure:**
```
advisor/
├── client_management/           # Tier 1 (Basic)
│   ├── models/
│   │   ├── advisor.py          # Advisor entity (was firm.py)
│   │   ├── subscription.py     # Subscription tier management
│   │   └── feature_flags.py    # Feature gating
│   └── services/
│       ├── client_list.py      # List all clients, sort by last worked
│       ├── client_selector.py  # Select which client to work on
│       └── subscription_mgmt.py # Manage subscription tiers
├── communication/               # Tier 2 (Communication)
│   ├── models/
│   │   ├── client_portal.py    # Client portal interactions
│   │   ├── email_interaction.py # Email Q&A tracking
│   │   └── activity_log.py     # Client activity tracking
│   └── services/
│       ├── portal_service.py   # Generate deeplinks, handle responses
│       ├── email_service.py    # Send questions, track responses
│       └── notification_service.py # Notify advisor of client actions
└── practice/                    # Tier 4 (Enterprise)
    ├── models/
    │   ├── practice.py         # Multi-advisor practice entity
    │   ├── staff.py            # Staff members
    │   └── role.py             # Role-based permissions
    └── services/
        ├── practice_dashboard.py # See all clients across all advisors
        ├── workflow_assignment.py # Assign clients to staff
        └── practice_analytics.py # Benchmark across portfolio
```

### **Design Principles:**
1. **Advisor Workflow Focus:** Features here are about HOW advisors work
2. **Cross-Product:** Every product line uses client list, communication, etc.
3. **Tier Gating:** Higher tiers unlock more advisor/ features
4. **Multi-Tenant Safety:** All operations scoped by `advisor_id`

### **Used By:**
- ✅ runway/ (advisor opens client, sees cash position)
- ✅ bookclose/ (advisor opens client, sees close checklist)
- ✅ tax_prep/ (advisor opens client, sees tax prep workflow)

**Key Insight:** Client list and communication features work the same across ALL product lines.

---

## **Layer 4: Product Lines (Revenue Expansion)**

### **Purpose:**
Specific service delivery workflows that advisors charge clients for.

### **Structure:**

#### **Product Line 1: `runway/` (Weekly Cash Ritual)**
```
runway/
├── calculators/                 # Pure calculation logic
│   ├── runway_calculator.py    # Days of cash remaining
│   ├── priority_calculator.py  # Bill/invoice prioritization
│   ├── impact_calculator.py    # Payment impact on runway
│   └── scenario_calculator.py  # "What if" scenarios (Tier 3)
├── orchestrators/               # Data pulling + state management
│   ├── decision_console_data_orchestrator.py
│   ├── hygiene_tray_data_orchestrator.py
│   └── reserve_runway.py       # Reserve allocation management
└── experiences/                 # User-facing workflows
    ├── tray/                   # What needs attention (cash items only)
    ├── console/                # Payment decision-making
    └── digest/                 # Cash position dashboard
```

**Tier Structure:**
- **Tier 1 ($50):** Tray + Console + Digest + Basic runway
- **Tier 2 ($125):** + Smart prioritization + Payment recommendations
- **Tier 3 ($250):** + 13-week forecast + Scenario analysis

#### **Product Line 2: `bookclose/` (Monthly Books Ritual)**
```
bookclose/
├── calculators/
│   ├── close_checklist_calculator.py  # Generate close checklist
│   ├── variance_calculator.py         # Budget vs actual
│   └── ratio_calculator.py            # Financial ratios
├── orchestrators/
│   ├── close_data_orchestrator.py     # Pull month-end data
│   └── reconciliation_orchestrator.py # Coordinate reconciliations
└── experiences/
    ├── close_checklist/               # Month-end close workflow
    ├── categorization/                # Bulk categorization UI
    └── statements/                    # Financial statement generation
```

**Tier Structure:**
- **Tier 1 ($100):** Close checklist + Categorization + Basic statements
- **Tier 2 ($200):** + Automation + Variance analysis
- **Tier 3 ($300):** + Custom reports + Budget management

#### **Product Line 3: `tax_prep/` (Yearly Tax Ritual)**
```
tax_prep/
├── calculators/
│   ├── tax_calculator.py          # Tax liability calculations
│   ├── deduction_calculator.py    # Maximize deductions
│   └── planning_calculator.py     # Tax planning scenarios
├── orchestrators/
│   ├── tax_data_orchestrator.py   # Pull full year of data
│   └── k1_generator.py            # Generate K-1s for partnerships
└── experiences/
    ├── tax_workflow/              # Tax prep workflow
    ├── planning/                  # Tax planning tools
    └── filing/                    # E-filing integration
```

**Tier Structure:**
- **Tier 1 ($200):** Tax prep workflow + K-1 generation
- **Tier 2 ($350):** + Tax planning + Multi-entity
- **Tier 3 ($500):** + E-filing + Audit support

---

## **Multi-Product Subscription Model**

### **Advisor Subscription Structure:**

```python
class Advisor:
    advisor_id: str                      # Primary key (was firm_id)
    email: str
    name: str
    
    # Product subscriptions (per client)
    runway_tier: str                     # "basic", "communication", "intelligence", None
    bookclose_tier: str                  # "basic", "automation", "advanced", None
    tax_prep_tier: str                   # "basic", "planning", "premium", None
    
    # Practice-level subscription
    practice_tier: str                   # None, "enterprise"
    
    # Feature overrides
    feature_flags: Dict[str, bool]       # Override tier defaults
    
    # Billing
    total_monthly_cost: float            # Sum across all products
    clients_count: int                   # Number of clients
```

### **Feature Gating:**

```python
def can_use_feature(advisor: Advisor, feature: str) -> bool:
    """Check if advisor can use a feature based on their subscription tiers."""
    
    # runway/ features
    runway_features = {
        "basic": ["tray", "console", "digest", "basic_runway"],
        "communication": [...basic, "client_portal", "email_interactions", "smart_priority"],
        "intelligence": [...communication, "scenarios", "forecasting", "insights"]
    }
    
    # bookclose/ features
    bookclose_features = {
        "basic": ["close_checklist", "categorization", "basic_statements"],
        "automation": [...basic, "auto_categorization", "variance_analysis"],
        "advanced": [...automation, "custom_reports", "budget_management"]
    }
    
    # tax_prep/ features
    tax_prep_features = {
        "basic": ["tax_workflow", "k1_generation"],
        "planning": [...basic, "tax_planning", "multi_entity"],
        "premium": [...planning, "efiling", "audit_support"]
    }
    
    # Check which product line the feature belongs to
    if feature in runway_features.get(advisor.runway_tier, []):
        return True
    if feature in bookclose_features.get(advisor.bookclose_tier, []):
        return True
    if feature in tax_prep_features.get(advisor.tax_prep_tier, []):
        return True
    
    # Check feature flag overrides
    if advisor.feature_flags.get(feature):
        return True
    
    return False
```

---

## **The Multi-Tenancy Model**

### **Current (Phase 1 - runway/ only):**
```
advisor_id (was firm_id)
  ├── business_id (client 1)
  ├── business_id (client 2)
  └── business_id (client N)
```

### **Phase 2 (+ bookclose/):**
```
advisor_id
  ├── business_id (client 1)
  │   ├── runway_subscription: "basic"
  │   └── bookclose_subscription: "basic"
  ├── business_id (client 2)
  │   ├── runway_subscription: "intelligence"
  │   └── bookclose_subscription: None
  └── business_id (client N)
      ├── runway_subscription: "communication"
      └── bookclose_subscription: "automation"
```

### **Phase 4 (+ practice management):**
```
practice_id (multi-advisor firm)
  ├── advisor_id (staff member 1)
  │   ├── role: "senior_accountant"
  │   └── assigned_clients: [business_id_1, business_id_2]
  ├── advisor_id (staff member 2)
  │   ├── role: "junior_accountant"
  │   └── assigned_clients: [business_id_3]
  └── advisor_id (staff member N)
      ├── role: "admin"
      └── assigned_clients: [all]
```

---

## **Database Schema Evolution**

### **Phase 1 (Current - runway/ only):**

```sql
-- RENAME firm_id → advisor_id throughout
ALTER TABLE firms RENAME TO advisors;
ALTER TABLE advisors RENAME COLUMN firm_id TO advisor_id;
ALTER TABLE businesses RENAME COLUMN firm_id TO advisor_id;

-- ADD subscription tier tracking
ALTER TABLE advisors ADD COLUMN runway_tier VARCHAR(50);
ALTER TABLE advisors ADD COLUMN feature_flags JSONB;
```

### **Phase 2 (+ bookclose/):**

```sql
-- ADD bookclose subscription
ALTER TABLE advisors ADD COLUMN bookclose_tier VARCHAR(50);

-- Per-client subscription overrides
CREATE TABLE business_subscriptions (
    business_id VARCHAR PRIMARY KEY,
    advisor_id VARCHAR REFERENCES advisors(advisor_id),
    runway_tier VARCHAR(50),
    bookclose_tier VARCHAR(50),
    custom_pricing JSONB
);
```

### **Phase 3 (+ tax_prep/):**

```sql
-- ADD tax_prep subscription
ALTER TABLE advisors ADD COLUMN tax_prep_tier VARCHAR(50);
ALTER TABLE business_subscriptions ADD COLUMN tax_prep_tier VARCHAR(50);
```

### **Phase 4 (+ practice management):**

```sql
-- ADD practice hierarchy
CREATE TABLE practices (
    practice_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    enterprise_tier VARCHAR(50)
);

ALTER TABLE advisors ADD COLUMN practice_id VARCHAR REFERENCES practices(practice_id);
ALTER TABLE advisors ADD COLUMN role VARCHAR(50);

-- Staff permissions
CREATE TABLE staff_permissions (
    advisor_id VARCHAR REFERENCES advisors(advisor_id),
    business_id VARCHAR REFERENCES businesses(business_id),
    permissions JSONB
);
```

---

## **API Architecture**

### **Product Line Routing:**

```
/api/v1/
├── advisor/                    # advisor/ layer endpoints
│   ├── /clients               # List all clients
│   ├── /clients/{id}          # Select client
│   └── /subscription          # Manage subscription
├── runway/                     # runway/ product endpoints
│   ├── /tray                  # Hygiene tray
│   ├── /console               # Decision console
│   └── /digest                # Cash dashboard
├── bookclose/                  # bookclose/ product endpoints (Phase 2)
│   ├── /checklist             # Close checklist
│   ├── /categorization        # Transaction categorization
│   └── /statements            # Financial statements
└── tax_prep/                   # tax_prep/ product endpoints (Phase 3)
    ├── /workflow              # Tax prep workflow
    ├── /k1                    # K-1 generation
    └── /planning              # Tax planning
```

### **Feature Gating Middleware:**

```python
@app.before_request
def check_feature_access():
    """Middleware to gate features by subscription tier."""
    advisor = get_current_advisor()
    requested_feature = get_requested_feature()
    
    if not can_use_feature(advisor, requested_feature):
        return jsonify({
            "error": "Feature not available in your tier",
            "upgrade_to": suggest_upgrade_tier(requested_feature)
        }), 403
```

---

## **Key Architectural Decisions**

### **ADR-007: Why `advisor/` is a Top-Level Layer**

**Decision:** Create `advisor/` as a peer to `infra/`, `domains/`, and product lines.

**Rationale:**
1. Advisor workflow features (client list, communication) are used across ALL product lines
2. Not infrastructure (not QBO/database)
3. Not business logic (not AP/AR primitives)
4. Not product-specific (not just runway/)
5. Deserves its own layer because it's core to the platform vision

### **ADR-008: Product Line Separation**

**Decision:** Separate `runway/`, `bookclose/`, `tax_prep/` as distinct product lines.

**Rationale:**
1. Each is a separate subscription with its own pricing
2. Each serves a different advisor ritual (weekly/monthly/yearly)
3. Each has its own tier structure
4. Natural upsell path from one to the next
5. Can be developed and released independently

### **ADR-009: Multi-Product Tenancy**

**Decision:** Use `advisor_id` + per-product tier flags.

**Rationale:**
1. Single advisor can subscribe to different products for different clients
2. Flexible pricing (not all clients need all products)
3. Easy to add new product lines without schema changes
4. Feature flags allow custom overrides
5. Enterprise tier adds `practice_id` for multi-advisor firms

---

## **Implementation Strategy**

### **Phase 1 (Current): Foundation + runway/ MVP**
1. ✅ Rename `firm_id` → `advisor_id`
2. ✅ Add `runway_tier` and `feature_flags` to advisors table
3. ✅ Create `advisor/client_management/` layer
4. ✅ Implement feature gating for runway/ tiers
5. ✅ Ship runway/ Tier 1 MVP ($50/client/month)

### **Phase 2: Add bookclose/**
1. ✅ Add `bookclose_tier` to advisors table
2. ✅ Create `bookclose/` product line structure
3. ✅ Create `gl/` domain for general ledger
4. ✅ Implement close checklist + categorization
5. ✅ Ship bookclose/ Tier 1 ($100/client/month)

### **Phase 3: Add tax_prep/**
1. ✅ Add `tax_prep_tier` to advisors table
2. ✅ Create `tax_prep/` product line structure
3. ✅ Create tax domain entities
4. ✅ Implement tax prep workflow
5. ✅ Ship tax_prep/ Tier 1 ($200/client/month)

### **Phase 4: Add practice management**
1. ✅ Create `practices` table and hierarchy
2. ✅ Add staff RBAC to `advisor/practice/`
3. ✅ Implement multi-advisor dashboard
4. ✅ Ship Enterprise tier

---

## **Success Metrics**

### **Architecture Quality Metrics:**
1. **Shared Code Ratio:** % of code shared across product lines (target: 60%+)
2. **Feature Reuse:** # of features used by multiple product lines
3. **API Consistency:** All product lines follow same API patterns
4. **Test Coverage:** All layers have >80% test coverage

### **Business Metrics:**
1. **Upsell Conversion:** % of runway/ customers who add bookclose/
2. **Multi-Product ARPU:** Average revenue per advisor across all products
3. **Feature Adoption:** % of advisors using tier 2+ features
4. **Churn by Product:** Which product lines have lowest churn

---

**This architecture enables the platform vision while maintaining clean separation of concerns.**

*Last Updated: 2025-01-27*
*Status: Architectural Foundation Document*
