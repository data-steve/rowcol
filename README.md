# RowCol: The Advisor Platform

**Get out of your spreadsheets. Scale your practice.**

---

## 🚀 **What Just Happened: The Strategic Pivot**

This repository represents a **complete strategic pivot** from Oodaloo (owner-first QBO app) to RowCol (advisor-first platform). Here's the story:

### **The Problem We Discovered**
- **Original Vision**: Oodaloo as owner-centric QBO app for small business owners
- **Market Reality**: Advisors charge $1000/month to clients but are stuck in spreadsheets
- **Opportunity**: Build the platform advisors actually need to scale their practice

### **The Strategic Pivot**
- **From**: Owner-first QBO app (Oodaloo)
- **To**: Advisor-first platform (RowCol) with three product lines
- **Result**: Complete platform for CAS advisors, bookkeepers, and vCFOs

### **The Three-Brand Ecosystem**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Oodaloo     │───▶│   Escher.cpa    │    │     RowCol      │
│  (Lead Gen)     │    │ (Service Firm)  │    │ (Advisor Platform)│
│                 │    │                 │    │                 │
│ • QBO App       │    │ • Tech-first    │    │ • Client List   │
│ • $75/month     │    │ • CPA firm      │    │ • 3-Tab View    │
│ • Lead gen      │    │ • $500-3000/mo  │    │ • $50-1050/mo   │
│ • Runway digest │    │ • 500+ clients  │    │ • Advisors      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## What is RowCol?

RowCol is the complete platform for CAS advisors, bookkeepers, and vCFOs who want to scale their practice with technology instead of spreadsheets.

### Core Experience
- **Client List**: See all clients at a glance, sorted by "needs attention"
- **3-Tab View**: Digest + Hygiene Tray + Decision Console
- **Batch Decisions**: Pay bills, send collections, schedule payments
- **Smart Features**: AI-powered insights and automation

---

## Product Lines

### **runway/** - Weekly Cash Runway Management
*$50-250/client/month*
- Client List with runway status
- 3-Tab View (Digest + Tray + Console)
- Batch payment decisions
- Reserve allocation
- Collections management

### **bookclose/** - Monthly Bookkeeping Automation
*+$100-300/client/month*
- Month-end close automation
- Transaction categorization
- Financial statement generation
- Accrual accounting support
- Workflow management

### **tax_prep/** - Yearly Tax Preparation
*+$200-500/client/month*
- Tax preparation workflow
- K-1 generation
- Tax planning tools
- E-filing integration
- Multi-entity support

---

## Built by Escher.cpa

RowCol is built and proven by [Escher.cpa](https://escher.cpa), our tech-first CPA firm serving 500+ clients. Every feature is battle-tested with real clients before release.

**The Build → Prove → Release Cycle:**
1. Build new feature in RowCol
2. Test with Escher.cpa clients
3. Prove value with real outcomes
4. Release to all advisors

---

## Pricing

### **Tier 1: Spreadsheet Replacement** - $50/client/month
- Client List + 3-Tab View
- Basic runway calculations
- Batch payment decisions
- QBO integration

### **Tier 2: Smart Features** - $150/client/month
- Everything in Tier 1
- AI-powered insights
- Automated categorization
- Smart recommendations
- Client communication tools

### **Tier 3: Advanced Analytics** - $350/client/month
- Everything in Tier 2
- Advanced forecasting
- Custom dashboards
- API access
- Priority support

### **Tier 4: Practice Management** - $1050/client/month
- Everything in Tier 3
- Multi-advisor dashboard
- Staff RBAC
- Workflow assignment
- White-label options

---

## 🔄 **The Oodaloo Recovery Plan**

### **Current State: Oodaloo Repository**
- **Status**: Contains complete RowCol codebase (backup)
- **Purpose**: Will be stripped down to digest-only QBO app
- **Timeline**: After RowCol Phase 1 MVP is complete

### **Future State: Oodaloo as Lead Gen**
- **Core Feature**: Weekly cash runway digest email
- **Target**: Small business owners who need runway visibility
- **Pricing**: $75/month (credibility filter + lead gen)
- **CTA**: "Need help? Contact Escher.cpa"
- **Distribution**: QuickBooks App Marketplace

### **The Recovery Steps**
1. **Phase 1**: Complete RowCol MVP (current focus)
2. **Phase 2**: Strip Oodaloo to digest-only
3. **Phase 3**: Add Escher.cpa lead gen CTAs
4. **Phase 4**: Launch on QBO Marketplace
5. **Phase 5**: Escher.cpa becomes testbed for RowCol features

---

## The Three-Brand Strategy

RowCol is part of a three-brand ecosystem:

### **RowCol** (This Platform)
- **Target**: Advisors managing 5-50 clients
- **Positioning**: "Get out of your spreadsheets"
- **Revenue**: $50-1050/client/month subscription
- **Distribution**: Direct sales, app store

### **Escher.cpa** (Service Delivery)
- **Target**: Small business owners
- **Positioning**: "We built the software, we run your books"
- **Revenue**: $500-3000/month service fees
- **Distribution**: Organic from Oodaloo funnel

### **Oodaloo** (Lead Generation)
- **Target**: Small business owners
- **Positioning**: "Know your runway"
- **Revenue**: $75/month (lead gen to Escher)
- **Distribution**: QuickBooks App Marketplace

---

## Architecture

### **Four-Layer Structure**
```
┌─────────────────────────────────────┐
│  Product Lines (runway/, bookclose/, tax_prep/)  │
├─────────────────────────────────────┤
│  Advisor Layer (cross-product features)          │
├─────────────────────────────────────┤
│  Domains (QBO primitives, business logic)        │
├─────────────────────────────────────┤
│  Infrastructure (database, auth, integrations)   │
└─────────────────────────────────────┘
```

### **Key Principles**
- **Service Boundaries**: Clear separation between domains/ and product lines
- **Data Orchestrator Pattern**: Centralized data management
- **Feature Gating**: Subscription-based access control
- **Multi-Tenancy**: advisor_id + business_id hierarchy

---

## Getting Started

### **For Advisors**
1. Sign up for RowCol account
2. Connect QuickBooks Online
3. Import your client list
4. Start with Client List + 3-Tab View
5. Scale up with additional features

### **For Developers**
1. Clone this repository
2. Set up development environment
3. Read `docs/architecture/` for technical details
4. Follow `DEVELOPMENT_STANDARDS.md`
5. Build features following established patterns

---

## Documentation

### **Strategic Vision**
- **[Platform Vision](docs/product/PLATFORM_VISION.md)** - The three-product platform strategy
- **[Advisor-First Architecture](docs/product/ADVISOR_FIRST_ARCHITECTURE.md)** - Technical architecture
- **[Build Plan Phase 1](docs/product/BUILD_PLAN_PHASE1_RUNWAY.md)** - What to build now
- **[Two-Brand Strategy](docs/product/TWO_BRAND_STRATEGY.md)** - RowCol + Escher + Oodaloo
- **[Repository Migration](docs/product/REPO_MIGRATION_STRATEGY.md)** - From Oodaloo to RowCol

### **Context & Continuity**
- **[Thread Port Documentation](docs/product/THREAD_PORT_DOCUMENTATION.md)** - Complete context transfer for AI assistant continuity
- **[Development Standards](DEVELOPMENT_STANDARDS.md)** - Coding standards and patterns
- **[Architecture Decisions](docs/architecture/)** - ADR documents for technical decisions

---

## The Vision

**RowCol will become the platform that advisors use for end-to-end service delivery across cash, bookkeeping, and tax.**

We're building the future where advisors can:
- Scale from 5 to 500 clients
- Replace spreadsheets with purpose-built tools
- Focus on advisory work, not data entry
- Deliver consistent, high-quality service
- Grow their practice with technology

---

## Contact

- **Website**: [rowcol.com](https://rowcol.com)
- **Escher.cpa**: [escher.cpa](https://escher.cpa)
- **Oodaloo**: [oodaloo.com](https://oodaloo.com)
- **Email**: hello@rowcol.com

---

## 🎯 **Next Steps**

### **Immediate (Next 2-3 weeks)**
1. **Database Migration**: `firm_id` → `advisor_id` throughout codebase
2. **Create Advisor Layer**: New architectural layer for advisor-client interaction
3. **Feature Gating System**: Implement subscription tier-based feature flags
4. **Console Payment Workflow**: Implement advisor-only payment decision workflow

### **Phase 1 MVP (Next 4-6 weeks)**
1. **Client List View**: Show all clients with key metrics
2. **3-Tab Client View**: Digest + Hygiene Tray + Decision Console
3. **Batch Decision Making**: Pay bills, send collections
4. **Basic Subscription Tiers**: Tier 1 ($50/client/month) features

### **Phase 2 (Next 8-12 weeks)**
1. **Uncat-style Emails**: Client communication for Tier 2+
2. **Advanced Features**: AI insights, automation
3. **Oodaloo Recovery**: Strip down to digest-only QBO app
4. **Escher.cpa Integration**: Lead gen and testbed features

---

**Three brands. One platform. Total market domination.** 🚀

*Last Updated: 2025-01-27*  
*Status: Ready for Development - Phase 1 MVP*
