# Oodaloo/RowCol Platform Vision

*The Advisor Platform for End-to-End Service Delivery*

---

## **The Vision: Replace the Advisor's Entire Tech Stack**

Oodaloo is not "accounting software" - it's **the platform advisors use to deliver services to clients**, from engagement letter to payment collection, without ever leaving the system.

### **The Core Insight**

Advisors (CPAs, bookkeepers, vCFOs) charge clients $1,000-5,000/month for services but cobble together 5-10 different tools:
- QuickBooks (for the books)
- ClientHub (for client comms)
- Ignition (for proposals/engagement letters)
- Keeper (for bookkeeping automation)
- Float (for cash forecasting)
- Practice management software
- Time tracking
- Billing/collections
- Tax prep software
- Email + Slack + phone calls

**Oodaloo's Vision:** Be the ONE platform that owns the entire client relationship, from "what services do you need?" to "here's your invoice".

---

## **The Three Rituals = Three Product Lines**

Advisors deliver services through three core rituals. Each ritual is a product line with its own subscription tier:

### **1. Weekly Cash Ritual → `runway/` Product Line**
**Service Delivered:** Cash flow advisory (CAS)
**Advisor Charges Client:** $500-1500/month
**Oodaloo Charges Advisor:** $50-250/client/month

**What Advisor Does:**
- Opens client in Oodaloo
- Reviews cash position (days of runway)
- Makes payment decisions (pay bills, send collections)
- Updates client on cash health

**Value to Advisor:** 
- Replaces spreadsheets
- Saves 2-4 hours/week per client
- Can serve more clients

**Competitors:**
- Float ($79/month) - Cash forecasting only
- Fathom ($49-199/month) - Reporting only
- LiveFlow ($50-200/month) - Real-time dashboards
- **None offer integrated decision-making + client comms**

### **2. Monthly Books Ritual → `bookclose/` Product Line**
**Service Delivered:** Bookkeeping + month-end close
**Advisor Charges Client:** $1,000-3,000/month
**Oodaloo Charges Advisor:** $100-300/client/month (ADDITIVE to runway/)

**What Advisor Does:**
- Reviews close checklist
- Categorizes transactions
- Reconciles accounts
- Generates financial statements
- Sends to client for review/approval

**Value to Advisor:**
- Automates close checklist
- Reduces errors
- Faster month-end close
- Professional deliverable package

**Competitors:**
- Keeper ($200-500/month) - Bookkeeping + client comms
- ClientHub ($69/month) - Client comms only
- QBO Accountant (free) - Manual, no automation
- **None offer integrated cash advisory + bookkeeping**

### **3. Yearly Tax Ritual → `tax_prep/` Product Line**
**Service Delivered:** Tax preparation + planning
**Advisor Charges Client:** $2,000-10,000/year
**Oodaloo Charges Advisor:** $200-500/client/month (ADDITIVE to bookclose/)

**What Advisor Does:**
- Tax preparation workflow
- K-1 generation for partnerships
- Tax planning recommendations
- Multi-entity consolidation
- E-filing integration

**Value to Advisor:**
- Full year of data already in system
- No re-entering data
- Tax planning throughout the year
- Automated workflows

**Competitors:**
- Keeper (adding tax prep)
- TaxDome ($50-200/month)
- Drake/Lacerte/UltraTax (traditional)
- **None have full-year client data already integrated**

---

## **The Revenue Expansion Model**

### **Customer Lifetime Value Growth**
```
Month 1-6:   runway/ only           → $50-250/client/month
Month 7-12:  + bookclose/           → $150-550/client/month
Month 13+:   + tax_prep/            → $350-1050/client/month

Total LTV: $350-1050/client/month across all three rituals
```

### **Why This Works**
1. **Start with pain:** Cash flow is immediate, weekly pain
2. **Upsell to automation:** "You're already here daily, let us do your month-end too"
3. **Lock-in with tax:** "We have all your data, tax prep is seamless"

### **TAM Expansion**
```
Phase 1 (runway/):      200,000 CAS advisors × $50-250/client/month
Phase 2 (bookclose/):   +500,000 bookkeepers × $100-300/client/month
Phase 3 (tax_prep/):    +100,000 tax preparers × $200-500/client/month

Total TAM: 800,000+ advisors
Average: 10 clients per advisor
Revenue: $35M-1B ARR potential
```

---

## **The Agentic Platform Vision**

### **From Manual to Automated Service Delivery**

The architecture we're building now supports **agentic automation** in the future:

```
TODAY (Manual):
Advisor → Reviews items → Makes decisions → Executes actions

TOMORROW (Agentic):
AI Agent → Reviews items → Recommends decisions → Advisor approves → Agent executes

FUTURE (Fully Automated):
AI Agent → Reviews items → Makes decisions → Executes actions → Notifies advisor
```

### **Why Our Architecture Enables This**

Every feature we build has clear **decision points** that can be automated:

**Example: Cash Runway Decisions**
```python
# Today (Manual):
advisor.review_bills() → advisor.select_bills_to_pay() → advisor.execute_payment()

# Tomorrow (AI-Assisted):
agent.analyze_bills() → agent.recommend_payment_plan() → advisor.approve() → agent.execute()

# Future (Fully Automated):
agent.analyze_bills() → agent.execute_payment_plan() → agent.notify_advisor()
```

**The key:** We're building the **decision framework** today that agents will use tomorrow.

---

## **The Service Delivery Platform (Future Vision)**

### **Beyond the Three Rituals**

Once we own the full client relationship, we become the platform for ALL service delivery:

```
SERVICE DEFINITION:
├── Service catalog (what you offer)
├── Dynamic pricing (by service + client)
└── Custom service bundles

PROPOSAL GENERATION:
├── Auto-generate proposals from service catalog
├── Client-specific pricing
└── E-signature integration

ENGAGEMENT LETTERS:
├── Scope of work from selected services
├── Terms and conditions
└── Automated contract generation

CLIENT PORTAL:
├── Picklists generated from engagement letter
├── Client uploads documents
├── Client approves deliverables
└── Client sees billing transparency

WORK MANAGEMENT:
├── Tasks auto-generated from engagement letter
├── Assigned to staff based on role
├── Time tracked automatically
└── Status updates to client

BILLING & COLLECTIONS:
├── Tasks → Time tracking → WIP → Invoice
├── Automated billing based on engagement letter
├── Client portal payment processing
└── Collections workflow for overdue

ENGAGEMENT CLOSING:
├── All tasks completed
├── Final deliverables sent
├── Client satisfaction survey
└── Archive for next year
```

**This is the Aiwyn vision you designed - but built on QBO as the system of record, not custom tax software.**

---

## **Why QBO is the Foundation**

### **QBO Won the Integration War**

QBO isn't great software, but it has:
- 7+ million businesses using it
- 200+ integrations with other tools
- Bank feed connectivity
- Industry standard for small business accounting

**Key Insight:** Advisors don't need to touch QBO directly anymore. Oodaloo becomes the interface.

```
OLD WORKFLOW:
Advisor → Opens QBO → Manually enters data → Manually categorizes → Manually reconciles

NEW WORKFLOW:
Advisor → Opens Oodaloo → Reviews AI suggestions → Approves → Syncs to QBO automatically

Advisor never opens QBO directly. QBO is just the database.
```

### **Keeper's Vision (That We'll Surpass)**

Keeper's vision: "Advisors don't need to use QBO anymore, we handle it all"

**Oodaloo's Vision:** "Advisors don't need to use QBO, Ignition, ClientHub, Float, or 5 other tools anymore - Oodaloo handles it all"

---

## **Competitive Positioning Strategy**

### **Phase 1: runway/ (2025)**
**Position:** "The Cash Runway Console for Advisors"
**Compete Against:** Float, Fathom, LiveFlow (cash forecasting tools)
**Win Because:** Integrated decision-making + client comms, not just dashboards

### **Phase 2: bookclose/ (2026)**
**Position:** "The Bookkeeping Automation Platform"
**Compete Against:** Keeper, ClientHub, QBO Accountant
**Win Because:** Already have advisor relationship from runway/, seamless upsell

### **Phase 3: tax_prep/ (2026-2027)**
**Position:** "The Full-Service Advisory Platform"
**Compete Against:** Keeper, TaxDome, traditional tax software
**Win Because:** Full year of client data, no re-entry, advisor already locked in

### **Phase 4: Platform (2027+)**
**Position:** "The Advisor's Operating System"
**Compete Against:** Practice management systems, proposal tools, billing platforms
**Win Because:** Own the full client relationship, end-to-end service delivery

---

## **Why This Architecture Works**

### **Shared Infrastructure = Compounding Value**

Every feature built in `infra/`, `domains/`, or `advisor/` layers benefits ALL product lines:

```
BUILD ONCE, USE 3X:

infra/ (QBO, Plaid, Auth):
└── Benefits runway/, bookclose/, tax_prep/

domains/ (AP, AR, GL, Tax):
└── Benefits runway/, bookclose/, tax_prep/

advisor/ (Client mgmt, comms, PMMS):
└── Benefits runway/, bookclose/, tax_prep/
```

### **Natural Upsell Path = Lower CAC**

```
Acquire customer once (runway/)
Upsell to bookclose/ (50% conversion = +$100-300/month)
Upsell to tax_prep/ (30% conversion = +$200-500/month)

Result: $350-1050/client/month ARPU from single acquisition
```

### **Competitive Moats Stack**

Each product line makes the next one stickier:

1. **runway/**: Advisor using daily for cash decisions
2. **+ bookclose/**: Advisor has all accounting data in Oodaloo
3. **+ tax_prep/**: Full year of data, impossible to leave

**By Phase 3, switching cost is so high that advisors never leave.**

---

## **The Three-Horizon Growth Strategy**

### **Horizon 1: Build runway/ MVP (2025)**
**Goal:** 100 paying advisors using it daily
**Metric:** $50-250/client/month ARPU
**Focus:** Nail the weekly cash ritual workflow

### **Horizon 2: Ship bookclose/ (2026)**
**Goal:** 50% of runway/ customers upgrade
**Metric:** $150-550/client/month ARPU
**Focus:** Automate the month-end close workflow

### **Horizon 3: Ship tax_prep/ (2027)**
**Goal:** 30% of bookclose/ customers upgrade
**Metric:** $350-1050/client/month ARPU
**Focus:** Seamless tax prep with full-year data

### **Horizon 4: Become the Platform (2028+)**
**Goal:** Replace 5-10 tools in advisor's tech stack
**Metric:** $500-2000/advisor/month (across all clients)
**Focus:** End-to-end service delivery platform

---

## **Success Criteria by Phase**

### **Phase 1 Success (runway/ MVP):**
- ✅ 10 advisors paying $50/client/month
- ✅ Used daily for cash decisions
- ✅ Replaces advisor's cash flow spreadsheet
- ✅ Advisor says "I can't go back to spreadsheets"

### **Phase 2 Success (bookclose/ launch):**
- ✅ 50% of Phase 1 advisors upgrade to bookclose/
- ✅ Used monthly for close process
- ✅ Replaces advisor's close checklist + manual work
- ✅ Advisor says "I'm closing books 50% faster"

### **Phase 3 Success (tax_prep/ launch):**
- ✅ 30% of Phase 2 advisors upgrade to tax_prep/
- ✅ Used yearly for tax preparation
- ✅ Replaces advisor's tax software + data re-entry
- ✅ Advisor says "I have all the data I need already"

### **Phase 4 Success (Platform transformation):**
- ✅ Advisors don't need ClientHub, Ignition, Float, etc.
- ✅ Advisors manage entire client relationship in Oodaloo
- ✅ New advisors say "Oodaloo is my practice management system"
- ✅ Oodaloo becomes verb: "I'll Oodaloo this client"

---

## **The North Star Metric**

**"Do advisors ONLY use Oodaloo to deliver services to clients?"**

If the answer is YES, we've won.

They might still use:
- QBO (as the database, but they never open it)
- Email (for non-client communication)
- Calendar (for scheduling)

But for actual CLIENT SERVICE DELIVERY, it's all Oodaloo.

---

## **Key Principles for All Future Decisions**

1. **Multi-Product Architecture:** Every feature should work across runway/, bookclose/, tax_prep/
2. **Advisor-First:** Build for the advisor workflow, not the owner workflow
3. **Service Delivery Focus:** Features should help advisors deliver services, not just "do accounting"
4. **Upsell Path:** Each product line should naturally lead to the next
5. **Platform Vision:** Every feature is a step toward replacing advisor's entire tech stack
6. **QBO as Database:** QBO is the system of record, Oodaloo is the interface
7. **Agentic-Ready:** Build decision frameworks that can be automated later

---

**This is the vision. Now let's build it.**

*Last Updated: 2025-01-27*
*Status: Strategic Foundation Document*
