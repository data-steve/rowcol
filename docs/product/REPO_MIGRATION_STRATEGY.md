# Repository Migration Strategy: Oodaloo → RowCol

*Moving from owner-first to advisor-first platform*

---

## **The Strategic Split**

### **Current State:**
```
oodaloo/ (this repo)
├── Owner-first legacy code
├── Strategic documentation
├── Mixed positioning
└── Confused identity
```

### **Target State:**
```
oodaloo/ (QBO App Repo)
├── Digest email ONLY
├── QBO Marketplace app
├── Lead gen to Escher.cpa
└── Simple, focused

rowcol/ (Platform Repo)
├── Advisor console platform
├── Three product lines (runway/, bookclose/, tax_prep/)
├── Escher.cpa service delivery
└── Full-featured platform
```

---

## **What Stays in Oodaloo Repo**

### **Core Oodaloo App (QBO Marketplace):**
- ✅ Weekly digest email service
- ✅ Basic runway calculation
- ✅ Bills due / Overdue AR summary
- ✅ "Work with Escher.cpa" CTA
- ✅ QBO integration (read-only)
- ✅ Simple webhook handling
- ✅ Basic user management

### **What Gets REMOVED:**
- ❌ All advisor console features
- ❌ Decision making tools
- ❌ Client management
- ❌ Batch processing
- ❌ Complex workflows
- ❌ All runway/ product line code

### **New Oodaloo Positioning:**
```
"Oodaloo: Your Weekly Cash Runway Digest"
- $75/month (filters for serious clients)
- QBO App Marketplace distribution
- Lead generation funnel to Escher.cpa
- Habit formation for weekly ritual
```

---

## **What Moves to RowCol Repo**

### **Full Platform Codebase:**
- ✅ All current `runway/` code (becomes RowCol core)
- ✅ All `domains/` code (QBO primitives)
- ✅ All `infra/` code (shared infrastructure)
- ✅ All strategic documentation
- ✅ All advisor console features
- ✅ All decision making tools

### **New RowCol Structure:**
```
rowcol/
├── runway/          # Weekly cash runway (Phase 1)
├── bookclose/       # Monthly bookkeeping (Phase 2)
├── tax_prep/        # Yearly tax prep (Phase 3)
├── advisor/         # Cross-product advisor features
├── domains/         # QBO primitives (shared)
├── infra/           # Shared infrastructure
├── escher/          # Escher.cpa service delivery
└── docs/            # All strategic documentation
```

---

## **The Migration Process**

### **Phase 1: Prepare RowCol Repo**
1. ✅ Create `rowcol/` repository on GitHub
2. ✅ Copy all strategic docs to `docs/product/`
3. ✅ Set up README with two-brand strategy
4. ✅ Initialize with current codebase

### **Phase 2: Strip Down Oodaloo**
1. ✅ Remove all advisor console features
2. ✅ Keep only digest email functionality
3. ✅ Add $75/month pricing
4. ✅ Add "Work with Escher.cpa" CTAs
5. ✅ Prepare for QBO Marketplace submission

### **Phase 3: Build RowCol Platform**
1. ✅ Migrate all platform code to RowCol repo
2. ✅ Implement advisor/ layer
3. ✅ Build Client List + 3-Tab View
4. ✅ Add feature gating for subscription tiers

### **Phase 4: Launch Both**
1. ✅ Submit Oodaloo to QBO Marketplace
2. ✅ Launch RowCol beta to advisors
3. ✅ Launch Escher.cpa service delivery
4. ✅ Prove the lead gen funnel works

---

## **The README Strategy**

### **Oodaloo Repo README:**
```markdown
# Oodaloo: Weekly Cash Runway Digest

**The simple way to know your runway every Friday morning.**

## What is Oodaloo?
Oodaloo sends you a weekly digest email with:
- Days of cash runway remaining
- Bills due this week
- Overdue accounts receivable
- Simple, actionable insights

## Pricing
$75/month - filters for serious clients who can benefit from professional help

## Need More Help?
Work with [Escher.cpa](https://escher.cpa) - our tech-first CPA firm that built Oodaloo.

## QBO App Marketplace
Available in the QuickBooks App Marketplace for seamless integration.
```

### **RowCol Repo README:**
```markdown
# RowCol: The Advisor Platform

**Get out of your spreadsheets. Scale your practice.**

## What is RowCol?
RowCol is the complete platform for CAS advisors, bookkeepers, and vCFOs:
- **Client List**: See all clients at a glance
- **3-Tab View**: Digest + Hygiene Tray + Decision Console
- **Batch Decisions**: Pay bills, send collections, schedule payments
- **Smart Features**: AI-powered insights and automation

## Product Lines
- **runway/**: Weekly cash runway management ($50-250/client/month)
- **bookclose/**: Monthly bookkeeping automation (+$100-300/client/month)
- **tax_prep/**: Yearly tax preparation (+$200-500/client/month)

## Built by Escher.cpa
RowCol is built and proven by Escher.cpa, our tech-first CPA firm serving 500+ clients.

## Pricing
$50-1050/client/month based on features and client count.
```

---

## **The Strategic Benefits**

### **1. Clear Brand Separation**
- Oodaloo = Simple, owner-focused
- RowCol = Complex, advisor-focused
- No confusion about target market

### **2. Focused Development**
- Oodaloo team = Digest email + QBO integration
- RowCol team = Full platform + advisor features
- No feature creep or scope confusion

### **3. Clean Repositories**
- Each repo has single responsibility
- Easier to onboard new developers
- Clearer code organization

### **4. Independent Scaling**
- Oodaloo can scale in QBO Marketplace
- RowCol can scale with advisor features
- Different go-to-market strategies

### **5. Lead Gen Optimization**
- Oodaloo optimized for conversion to Escher
- RowCol optimized for advisor productivity
- Clear handoff between brands

---

## **The Implementation Timeline**

### **Week 1: Repository Setup**
- [ ] Create RowCol GitHub repository
- [ ] Copy strategic documentation
- [ ] Set up README with two-brand strategy
- [ ] Initialize with current codebase

### **Week 2: Oodaloo Simplification**
- [ ] Remove advisor console features
- [ ] Keep only digest email functionality
- [ ] Add $75/month pricing
- [ ] Add Escher.cpa CTAs

### **Week 3: RowCol Platform**
- [ ] Migrate all platform code
- [ ] Implement advisor/ layer
- [ ] Build Client List + 3-Tab View
- [ ] Add feature gating

### **Week 4: Launch Preparation**
- [ ] Submit Oodaloo to QBO Marketplace
- [ ] Launch RowCol beta
- [ ] Launch Escher.cpa website
- [ ] Test lead gen funnel

---

## **The Long-Term Vision**

### **Oodaloo (5 Years):**
- 10,000+ users in QBO Marketplace
- 5% conversion rate to Escher.cpa
- 500+ new Escher clients per year
- $0 CAC for service delivery business

### **RowCol (5 Years):**
- 1,000+ advisor customers
- 10,000+ client licenses
- $6M-30M ARR
- Market leader in advisor tools

### **Escher.cpa (5 Years):**
- 500+ clients at $1,500/month average
- $7.5M ARR
- Proof point for RowCol sales
- Tech-forward CPA firm reputation

---

**Three brands. One vision. Total market domination.** 🚀

*Last Updated: 2025-01-27*  
*Status: Ready for Migration*
