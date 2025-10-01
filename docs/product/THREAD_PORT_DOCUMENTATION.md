# Thread Port Documentation: Oodaloo → RowCol Strategic Pivot

**Date**: January 2025  
**Purpose**: Complete context transfer for AI assistant continuity across Cursor sessions  
**Status**: CRITICAL - This document contains essential context for continuing development

---

## 🎯 **EXECUTIVE SUMMARY**

This document captures the complete strategic pivot from **Oodaloo** (owner-first QBO app) to **RowCol** (advisor-first platform) that occurred in this thread. The AI assistant needs this context to continue development without losing the strategic vision, architectural decisions, and implementation progress.

**Key Outcome**: We've successfully migrated the entire codebase to a new `RowCol` repository and documented a comprehensive advisor-first platform strategy. The next phase is implementing the core advisor platform features.

---

## 📋 **WHAT WE ACCOMPLISHED IN THIS THREAD**

### 1. **Strategic Reframe: Owner-First → Advisor-First**
- **Problem**: Oodaloo was positioned as an owner-centric QBO app, but the real market opportunity is advisors who charge $1000/month to clients
- **Solution**: Pivot to "The Advisor's Client Console" with three primitives:
  - **Client List**: See all clients at a glance
  - **Client Snapshot**: 3-tab view (Digest + Hygiene Tray + Decision Console)
  - **Decision Making**: Batch operations for efficiency

### 2. **Three-Product Platform Vision**
- **`runway/`**: Weekly cash ritual (current focus)
- **`bookclose/`**: Monthly books ritual (future)
- **`tax_prep/`**: Yearly tax ritual (future)
- **Shared Infrastructure**: `infra/`, `domains/`, and new `advisor/` layer

### 3. **Subscription Tier Strategy**
- **Tier 1**: $50/client/month "Basic Advisory Console" (minimum viable features)
- **Tier 2**: $125/client/month "Async Advisory" (Uncat-style emails, client communication)
- **Tier 3**: $250/client/month "Advisory Deliverables" (advanced features, reporting)
- **Tier 4**: Enterprise "Practice Management" (multi-advisor, advanced workflows)

### 4. **Two-Brand Strategy**
- **RowCol**: B2B SaaS for advisors (main platform)
- **Oodaloo**: QBO App for owners (lead gen funnel to Escher.cpa)
- **Escher.cpa**: Tech-first CPA firm (vertically integrated)

### 5. **Repository Migration**
- **Source**: `git@github.com:data-steve/oodaloo.git`
- **Destination**: `git@github.com:data-steve/rowcol.git`
- **Status**: Complete - full codebase copied to both repos

---

## 📁 **CRITICAL DOCUMENTS CREATED**

### **Strategic Vision Documents** (`docs/product/`)
1. **`PLATFORM_VISION.md`** - Complete platform strategy and market positioning
2. **`ADVISOR_FIRST_ARCHITECTURE.md`** - Technical architecture for advisor-first platform
3. **`BUILD_PLAN_PHASE1_RUNWAY.md`** - Phase 1 implementation plan
4. **`TWO_BRAND_STRATEGY.md`** - RowCol/Oodaloo/Escher.cpa strategy
5. **`REPO_MIGRATION_STRATEGY.md`** - Migration and cleanup plan

### **Architecture Documents** (`docs/architecture/`)
- **`ADR-001-domains-runway-separation.md`** - Service boundary principles
- **`ADR-003-multi-tenancy-strategy.md`** - Multi-tenancy patterns
- **`ADR-005-qbo-api-strategy.md`** - QBO integration strategy
- **`ADR-007-service-boundaries.md`** - Service layer organization

---

## 🏗️ **TECHNICAL IMPLEMENTATION PROGRESS**

### **Completed Tasks**
1. **QBOMapper Implementation** ✅
   - Created `runway/services/utils/qbo_mapper.py`
   - Replaced all direct QBO field access with mapper calls
   - Updated routes: `runway/routes/invoices.py`, `runway/routes/collections.py`
   - Updated services: `domains/ar/services/invoice.py`, `domains/ar/services/collections.py`, `domains/ap/services/bill_ingestion.py`

2. **Strategic Documentation** ✅
   - All four strategic documents created and committed
   - Repository migration completed
   - Project metadata updated (`pyproject.toml`)

### **Pending Tasks** (Next Phase)
1. **Database Migration**: `firm_id` → `advisor_id` throughout codebase
2. **Create `advisor/` Layer**: New architectural layer for advisor-client interaction
3. **Feature Gating System**: Implement subscription tier-based feature flags
4. **Console Payment Workflow**: Implement advisor-only payment decision workflow
5. **TestDrive Data Orchestrator**: Complete implementation following established patterns

---

## 🔧 **CURRENT CODEBASE STATE**

### **Repository Structure**
```
rowcol/
├── docs/
│   ├── product/           # Strategic vision documents
│   └── architecture/      # Technical architecture decisions
├── domains/               # Domain services (ar, ap, bank, core, policy)
├── infra/                 # Infrastructure services
├── runway/                # Runway product (weekly cash ritual)
│   ├── services/
│   │   ├── 0_data_orchestrators/  # Data orchestration
│   │   ├── 1_calculators/         # Business logic
│   │   ├── 2_experiences/         # User experiences
│   │   └── utils/                 # Utilities (QBOMapper)
│   └── routes/            # API endpoints
├── advisor/               # NEW: Advisor layer (to be created)
└── pyproject.toml         # Updated for RowCol project
```

### **Key Files Modified**
- **`runway/services/utils/qbo_mapper.py`** - NEW: Centralized QBO field mapping
- **`runway/routes/invoices.py`** - Updated to use QBOMapper
- **`runway/routes/collections.py`** - Updated to use QBOMapper
- **`domains/ar/services/invoice.py`** - Updated to use QBOMapper
- **`domains/ar/services/collections.py`** - Updated to use QBOMapper
- **`domains/ap/services/bill_ingestion.py`** - Updated to use QBOMapper
- **`pyproject.toml`** - Updated project name and description

---

## 🎯 **IMMEDIATE NEXT STEPS**

### **Phase 1: Foundation (Next 2-3 weeks)**
1. **Database Migration**: `firm_id` → `advisor_id`
   - Update all models, services, and routes
   - Update database schema
   - Update tests

2. **Create `advisor/` Layer**:
   ```
   advisor/
   ├── client_management/
   │   ├── models/
   │   ├── services/
   │   └── routes/
   ├── communication/
   │   ├── models/
   │   ├── services/
   │   └── routes/
   └── practice_management/
       ├── models/
       ├── services/
       └── routes/
   ```

3. **Feature Gating System**:
   - Add `subscription_tier` to advisor model
   - Implement feature flag system
   - Gate features based on tier

### **Phase 2: Core Features (Next 4-6 weeks)**
1. **Client List View**: Show all clients with key metrics
2. **3-Tab Client View**: Digest + Hygiene Tray + Decision Console
3. **Batch Decision Making**: Pay bills, send collections
4. **Uncat-style Emails**: Client communication for Tier 2+

---

## 🧠 **CRITICAL CONTEXT FOR AI ASSISTANT**

### **Strategic Vision**
- **Target Market**: CAS advisors charging $1000/month to clients
- **Value Proposition**: "Get out of your spreadsheets. Scale your practice."
- **Core Problem**: Advisors are stuck in spreadsheets, can't scale efficiently
- **Solution**: Complete platform with Client List + 3-Tab View + Decision Making

### **Architectural Principles**
- **Advisor-First**: Everything revolves around advisor workflow
- **Multi-Tenant**: `advisor_id` as primary tenant identifier
- **Service Boundaries**: Clear separation between `domains/`, `runway/`, `advisor/`
- **Feature Gating**: Subscription tier-based feature access
- **QBO Integration**: Centralized through QBOMapper

### **Business Model**
- **RowCol**: B2B SaaS for advisors ($50-250/client/month)
- **Oodaloo**: QBO App for owners (lead gen to Escher.cpa)
- **Escher.cpa**: Tech-first CPA firm (vertically integrated)

### **Technical Debt to Address**
1. **Over-engineered Dependency Injection**: Replace `get_services()` pattern
2. **Direct QBO Field Access**: Already fixed with QBOMapper
3. **Missing Advisor Layer**: Need to create complete advisor management system
4. **Feature Gating**: Need subscription tier system

---

## 📚 **REFERENCE MATERIALS**

### **Key Documents to Read First**
1. **`docs/product/PLATFORM_VISION.md`** - Complete strategic vision
2. **`docs/product/ADVISOR_FIRST_ARCHITECTURE.md`** - Technical architecture
3. **`docs/product/BUILD_PLAN_PHASE1_RUNWAY.md`** - Implementation plan
4. **`runway/services/README.md`** - Current service organization

### **Code Patterns to Follow**
- **Data Orchestrators**: `runway/services/0_data_orchestrators/`
- **Calculators**: `runway/services/1_calculators/`
- **Experiences**: `runway/services/2_experiences/`
- **QBOMapper**: `runway/services/utils/qbo_mapper.py`

### **Existing Examples**
- **Decision Console**: `runway/core/data_orchestrators/decision_console_data_orchestrator.py`
- **Hygiene Tray**: `runway/core/data_orchestrators/hygiene_tray_data_orchestrator.py`
- **Runway Calculator**: `runway/services/1_calculators/runway_calculator.py`

---

## 🚨 **CRITICAL WARNINGS**

### **DO NOT**
- Revert to owner-first thinking
- Create features without advisor context
- Ignore subscription tier requirements
- Break the service boundary patterns
- Access QBO fields directly (use QBOMapper)

### **ALWAYS**
- Think advisor-first
- Consider multi-tenancy (`advisor_id`)
- Follow established service patterns
- Document architectural decisions
- Test with advisor workflow in mind

---

## 🔄 **CONTINUITY CHECKLIST**

When starting work in the new RowCol project:

1. **Read Strategic Docs**: Start with `docs/product/PLATFORM_VISION.md`
2. **Understand Architecture**: Review `docs/product/ADVISOR_FIRST_ARCHITECTURE.md`
3. **Check Current State**: Review `runway/services/README.md`
4. **Identify Next Task**: Look at pending tasks in this document
5. **Follow Patterns**: Use existing data orchestrators and calculators as examples
6. **Think Advisor-First**: Every feature should serve advisor workflow

---

## 📞 **CONTACT & CONTEXT**

**Original Thread**: This documentation was created from a comprehensive strategic pivot discussion  
**Key Decisions**: All major architectural and strategic decisions are documented in `docs/product/`  
**Implementation Status**: QBOMapper complete, strategic docs complete, ready for Phase 1 implementation  
**Next Phase**: Database migration (`firm_id` → `advisor_id`) and advisor layer creation  

**Remember**: This is a complete platform pivot. The advisor is the primary user, not the business owner. Everything should be designed around advisor workflow, client management, and practice scaling.

---

*This document serves as the complete context transfer for continuing development of the RowCol advisor platform. All strategic decisions, technical progress, and next steps are documented here.*
