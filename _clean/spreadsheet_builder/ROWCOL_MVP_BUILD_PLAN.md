// *** CRITICAL ARCHITECTURAL NARRATIVE - READ FIRST ***
// *** DO NOT PROCEED WITHOUT UNDERSTANDING THIS ***
//////////////////////////////////////////////////////////////////////////////////
// 
// THE PROBLEM WE'RE SOLVING (Not just building an Excel generator):
// ============================================================================
// 
// Mission First is ONE nonprofit CAS firm serving nonprofit CLIENTS.
// But RowCol must work for ANY CAS firm serving ANY client type:
// - Nonprofits (donations, grants, recurring subscriptions)
// - Agencies (project billing, variable revenue, fixed costs)
// - SaaS/E-commerce (subscription revenue, high variability)
// - Professional services (retainer + projects, complex billing)
// - Mixed practices serving 5+ different client types simultaneously
// 
// THE HARD PROBLEM IS NOT THE EXCEL.
// ============================================================================
// 
// The hard problem is: **Building universal detection logic that classifies 
// inflows, outflows, recurrence, and magnitude WITHOUT hardcoding**
// 
// Why this matters:
// - If we hardcode "Mission First Operations LLC = vendor row 29", we fail at CAS Firm #2
// - If we use GL ranges (QBO's universal standard), we scale to ANY client type
// - If we learn recurrence patterns (3+ occurrences, ±10% stability), it adapts
// - If we store client-specific overrides (per-business learning), we improve over time
// 
// THE STRATEGY: GL-BASED UNIVERSAL CLASSIFICATION
// ============================================================================
// 
// Step 1: USE QBO's UNIVERSAL GL STRUCTURE (not vendor names)
//   - 4000-4999 range = Revenue/Inflows (any client type)
//   - 6000-6999 range = Expenses/Outflows (any client type)
//   - 60100-60199 range = Payroll (any client type)
//   - This is the same in nonprofit, agency, SaaS, everything
// 
// Step 2: DETECT RECURRENCE & MAGNITUDE (learn from history)
//   - 3+ transactions in 90 days with ±10% variance = recurring
//   - Amount > threshold = major/variable; amount < threshold = recurring
//   - Threshold is configurable per client type, learned over time
// 
// Step 3: POPULATE THE TEMPLATE (exact same structure for all)
//   - Mission First template shows desired OUTPUT shape (13-month waterfall)
//   - But the VALUES come from GL classification, not hardcoding
//   - Beginning cash (row 2) from QBO bank balance
//   - Inflows (rows 3-25) from GL 4000-4999 + recurrence detection
//   - Outflows (rows 26-77) from GL 6000-6999 + payroll from 60100-60199
//   - Formulas (EOMONTH roll-forward, SUM totals) are locked, never change
// 
// Step 4: LEARN PER-CLIENT (overrides, improvements, edge cases)
//   - Store learned rules: "XYZ Corp's revenue is biweekly, not monthly"
//   - Store corrections: "This was mis-classified, it's actually X not Y"
//   - Improve confidence over time
// 
// THE DATA FLOW (This is what we're building):
// ============================================================================
// 
// QBO Raw Data (bank, invoices, bills, payroll)
//   ↓
// GL-BASED CLASSIFICATION (use QBO's universal GL ranges)
//   - Fetch all transactions from QBO
//   - Sort into GL ranges: 4000-4999 (inflows), 6000-6999 (expenses), 60100-60199 (payroll)
//   ↓
// RECURRENCE DETECTION (learn from 90-day history)
//   - For each GL-classified group: count occurrences, check amount stability
//   - 3+ times with ±10% variance = recurring
//   - Otherwise = one-time/variable (major)
//   ↓
// TEMPORAL BUCKETING (which month does each transaction appear?)
//   - Inflows: invoice date + historical DSO (days-sales-outstanding) → expected month
//   - Outflows (AP): bill due date (or configured pay policy) → payment month
//   - Outflows (Payroll): known pay schedule → payment dates
//   ↓
// TEMPLATE POPULATION (write classified values to correct rows)
//   - Row 2: Beginning cash (sum of QBO bank accounts)
//   - Rows 9-21: Major inflows (classified as major + amount >threshold)
//   - Rows 28-35: Recurring vendors (classified as recurring + GL 6000-6999)
//   - Rows 46-76: Payroll breakdown (from GL 60100-60199)
//   - All totals/formulas preserved (renderer writes VALUES ONLY)
//   ↓
// EXCEL OUTPUT (multi-sheet, formulas intact, board-ready)
//   - Sheet 1: Primary waterfall (" RA Edits-Cash Flow-Ops with Sa")
//   - Sheet 2: Hidden reference variant (used by summary formulas)
//   - Sheet 3: Summary by vendor/class (presentation layer)
// 
// THIS ARCHITECTURE SCALES:
// ============================================================================
// 
// ✅ Works for nonprofits → agencies → SaaS → anything with QBO
// ✅ No hardcoding of vendor names (universal GL-based)
// ✅ Learns per-client (stores overrides, improves confidence)
// ✅ Adapts to data quality (learns from what exists)
// ✅ Mission First is the PROOF OF CONCEPT (the template structure)
// ✅ But the ENGINE is generic (works for any CAS + any client type)
// 
// WHERE WE'RE STARTING (Phase 0):
// ============================================================================
// 
// Task 0.1-0.7: Port GL classification infrastructure (from domains/)
//   - Business model (industry detection)
//   - Transaction model (confidence, status)
//   - COA template system (GL mapping by industry)
//   - Vendor categories (GL account mapping)
//   - Policy engine (rule-based categorization)
//   - Vendor normalization (fallback confidence scoring)
// 
// Why we're porting existing code:
//   - These models/services already implement GL-based logic
//   - They're tested, proven patterns
//   - We're not building from scratch; we're adapting existing infrastructure
//   - Multi-tenant structure is already there
// 
// PHASE 1: Build the Template Renderer
// ============================================================================
// 
// Once classification works (Phase 0), Phase 1 builds:
//   - Temporal bucketing (map transactions to month columns)
//   - Multi-sheet Excel generation (primary + hidden + summary)
//   - Formula preservation (write values, keep Excel math intact)
//   - Variant support (nonprofit vs agency vs SaaS templates)
// 
// The Mission First forensic analysis tells us EXACTLY what rows/formulas
// to preserve. But the classification engine (Phase 0) is what makes it
// work for ANY client type, not just Mission First.
// 
// KEY PRINCIPLE: UNIVERSAL FIRST, THEN SPECIFIC
// ============================================================================
// 
// ❌ WRONG: "Let's build for Mission First (hardcode their structure)"
// ❌ RESULT: Works for 1 firm, fails for firm #2
// 
// ✅ RIGHT: "Let's build GL-based classification that scales"
// ✅ THEN: "Apply it to Mission First's template structure"
// ✅ RESULT: Works for ANY CAS firm + ANY client type
// 
// If you see code being written that says:
//   - "if vendor_name == 'Mission First Operations'..."
//   - "if this is a nonprofit, then..."
//   - "hardcode this row for this firm"
// 
// STOP. That's the wrong direction. We're building GL-based, universal logic.
// 
//////////////////////////////////////////////////////////////////////////////////
// *** KEEP THIS NARRATIVE IN VIEW WHILE READING TASKS BELOW ***
//////////////////////////////////////////////////////////////////////////////////
//
# RowCol MVP Build Plan
## Detailed Implementation Roadmap

**Version:** 1.0  
**Date:** October 13, 2025  
**Status:** Ready for Development  
**Timeline:** 6 months to full Control Plane platform  

---

## 🎯 Build Overview

This build plan implements the RowCol MVP as defined in the Product Specification, leveraging an existing multi-tenant architecture to build a comprehensive cash control platform for the broader CAS market.

**Key Strategic Insights:**
- RowCol addresses a broader CAS opportunity beyond any single firm or client type
- We're ahead of the adoption curve - most CAS firms haven't seen this level of automation because no one has shown it to them yet
- The dual-mode strategy (Planner vs Control Plane) addresses the full spectrum of CAS needs
- **Existing multi-tenant architecture provides a solid foundation for rapid MVP development**

**Total Timeline:** 24 weeks (6 months)  
**Team Size:** 1-2 developers  
**Technology Stack:** Python, FastAPI, React, QBO API, openpyxl  
**Architecture Foundation:** Multi-tenant, domain-driven design with Smart Sync patterns  

---

## 🔧 Available Systems to Leverage (Strangled Fig Process)

**Following the strangled fig migration process (see `_clean/strangled_fig/migration_manifest.md`), we can leverage existing sophisticated systems:**

### **Already Built in _clean/mvp/ (REF - Use existing systems)**
- `_clean/mvp/domains/ap/gateways.py` - AP (Bills) domain gateway with Smart Sync
- `_clean/mvp/domains/ar/gateways.py` - AR (Invoices) domain gateway with Smart Sync  
- `_clean/mvp/domains/bank/gateways.py` - Bank (Balances) domain gateway with Smart Sync
- `_clean/mvp/infra/db/models.py` - Mirror tables for bills, invoices, balances with multi-tenancy
- `_clean/mvp/runway/services/console_service.py` - Console service with financial insights
- `_clean/mvp/infra/sync/orchestrator.py` - Smart Sync orchestrator for data freshness
- `_clean/mvp/infra/rails/qbo/` - QBO integration with OAuth2 and throttling

### **Available to PORT from domains/ and _parked/ (PORT - Bring over and cleanse)**
- `domains/core/models/transaction.py` - Transaction models with confidence scoring and status
- `domains/core/models/business.py` - Business model with industry field and QBO integration
- `domains/core/models/audit_log.py` - Audit logging for compliance and traceability
- `domains/ap/models/coa_template.py` - COA templates by industry
- `domains/ap/models/vendor_category.py` - Vendor categories with GL mapping
- `_parked/vendor_normalization/` - Sophisticated vendor normalization with MCC/NAICS mapping
- `_parked/policy/` - Policy engine with Cash Decision Model (CDM) categorization

### **Strangled Fig Process**
- **PORT**: Copy from legacy and cleanse (keep only what MVP needs)
- **ADAPT**: Thin wrapper around existing code (keep logic, expose new interface)
- **REF**: Refactor in place (light edits, same file)
- **DROP**: Leave out for MVP (complex features for later phases)

**Key Insight**: Use existing sophisticated data models and services, but implement simplified interfaces for MVP. This gives us enterprise-grade foundation with simple MVP functionality.

---

## 📋 Phase 0: Foundation (Weeks 1-2)
**Goal:** Leverage existing multi-tenant architecture to build Excel automation  
**Deliverable:** Working MVP with multi-client support and GL-based learning  

### Task 0.1: Port Sophisticated Domain Services via Strangled Fig Pattern
**Duration:** 3 days  
**Dependencies:** None  

#### Requirements
- [ ] Port specific models needed for template system:
  - [ ] `domains/core/models/business.py` → `_clean/mvp/domains/core/models/business.py`
  - [ ] `domains/core/models/transaction.py` → `_clean/mvp/domains/core/models/transaction.py`
  - [ ] `domains/core/models/audit_log.py` → `_clean/mvp/domains/core/models/audit_log.py`
- [ ] Port specific services needed for template system:
  - [ ] `domains/core/services/business.py` → `_clean/mvp/domains/core/services/business.py`
  - [ ] `domains/ap/services/vendor.py` → `_clean/mvp/domains/ap/services/vendor.py` (for vendor categorization)
- [ ] Port specific models for GL classification:
  - [ ] `domains/ap/models/coa_template.py` → `_clean/mvp/domains/ap/models/coa_template.py`
  - [ ] `domains/ap/models/vendor_category.py` → `_clean/mvp/domains/ap/models/vendor_category.py`
- [ ] Port vendor normalization (selective from _parked):
  - [ ] `_parked/vendor_normalization/services.py` → `_clean/mvp/infra/vendor_normalization/services.py`
  - [ ] `_parked/vendor_normalization/models/vendor_canonical.py` → `_clean/mvp/infra/vendor_normalization/models/vendor_canonical.py`
- [ ] Port policy engine (selective from _parked):
  - [ ] `_parked/policy/services/policy_engine.py` → `_clean/mvp/domains/policy/services/policy_engine.py`
  - [ ] `_parked/policy/models/suggestion.py` → `_clean/mvp/domains/policy/models/suggestion.py`
  - [ ] `_parked/policy/models/correction.py` → `_clean/mvp/domains/policy/models/correction.py`
- [ ] Verify domain gateways in `_clean/mvp/domains/` are complete for template system
- [ ] Update all imports to use `_clean/mvp/` paths
- [ ] Ensure multi-tenant structure is preserved
- [ ] Document "fast follow" enhancements for corrections, suggestions, and learning loops

#### Deliverables
- [ ] `_clean/mvp/domains/core/models/business.py` (business model for industry detection)
- [ ] `_clean/mvp/domains/core/models/transaction.py` (transaction model with confidence scoring)
- [ ] `_clean/mvp/domains/core/models/audit_log.py` (audit logging for compliance)
- [ ] `_clean/mvp/domains/core/services/business.py` (business service for validation)
- [ ] `_clean/mvp/domains/ap/models/coa_template.py` (COA templates by industry)
- [ ] `_clean/mvp/domains/ap/models/vendor_category.py` (vendor categories with GL mapping)
- [ ] `_clean/mvp/domains/ap/services/vendor.py` (vendor service for categorization)
- [ ] `_clean/mvp/infra/vendor_normalization/services.py` (vendor normalization service)
- [ ] `_clean/mvp/infra/vendor_normalization/models/vendor_canonical.py` (vendor canonical model)
- [ ] `_clean/mvp/domains/policy/services/policy_engine.py` (policy engine for categorization)
- [ ] `_clean/mvp/domains/policy/models/suggestion.py` (suggestion model for learning)
- [ ] `_clean/mvp/domains/policy/models/correction.py` (correction model for learning)
- [ ] Domain gateway verification and completion
- [ ] Updated imports throughout MVP codebase
- [ ] "Fast Follow" enhancement documentation

#### Sophisticated Capabilities Already Built

**Vendor Management (domains/ap/services/vendor.py):**
- Comprehensive vendor lifecycle management
- Payment method validation and W9 status tracking
- Payment urgency calculation and statistics updates
- Vendor normalization and matching with QBO
- Critical vendor identification and payment history

**Policy Engine (_parked/policy/):**
- Rule-based transaction categorization with confidence scoring
- Correction and suggestion models for learning loops
- Policy profiles with vertical specializations
- Vendor category fallback with sophisticated matching
- Real business rules with priority and confidence computation

**Payment Services (domains/ap/services/payment.py):**
- Complete payment lifecycle from creation to reconciliation
- Payment status tracking and retry logic
- QBO synchronization and runway impact calculations
- Provider pattern with mock and real implementations

**Statement Reconciliation (domains/ap/services/statement_reconciliation.py):**
- Bank statement reconciliation capabilities
- Transaction matching and validation

#### Code Implementation
```python
# STRANGLED FIG PATTERN: Selective porting for template system needs
# Step 1: Port only specific models/services needed for template generation
# Step 2: Port policy engine components for transaction categorization
# Step 3: Port vendor normalization for GL mapping
# Step 4: Update imports to use _clean/mvp/ paths

# PORT: Core Models (selective)
# domains/core/models/business.py → _clean/mvp/domains/core/models/business.py
# domains/core/models/transaction.py → _clean/mvp/domains/core/models/transaction.py
# domains/core/models/audit_log.py → _clean/mvp/domains/core/models/audit_log.py

# PORT: Core Services (selective)
# domains/core/services/business.py → _clean/mvp/domains/core/services/business.py

# PORT: AP Models (selective)
# domains/ap/models/coa_template.py → _clean/mvp/domains/ap/models/coa_template.py
# domains/ap/models/vendor_category.py → _clean/mvp/domains/ap/models/vendor_category.py

# PORT: AP Services (selective)
# domains/ap/services/vendor.py → _clean/mvp/domains/ap/services/vendor.py

# PORT: Policy Engine (selective from _parked)
# _parked/policy/services/policy_engine.py → _clean/mvp/domains/policy/services/policy_engine.py
# _parked/policy/models/suggestion.py → _clean/mvp/domains/policy/models/suggestion.py
# _parked/policy/models/correction.py → _clean/mvp/domains/policy/models/correction.py

# PORT: Vendor Normalization (selective from _parked)
# _parked/vendor_normalization/services.py → _clean/mvp/infra/vendor_normalization/services.py
# _parked/vendor_normalization/models/vendor_canonical.py → _clean/mvp/infra/vendor_normalization/models/vendor_canonical.py

# After porting, update all imports to use _clean/mvp/ paths:
from _clean.mvp.domains.core.models.transaction import Transaction
from _clean.mvp.domains.core.models.business import Business
from _clean.mvp.domains.core.models.audit_log import AuditLog, AuditAction, AuditSource
from _clean.mvp.domains.core.services.business import BusinessService
from _clean.mvp.domains.core.services.coa_sync import COASyncService
from _clean.mvp.domains.ap.models.coa_template import COATemplate
from _clean.mvp.domains.ap.models.vendor_category import VendorCategory
from _clean.mvp.domains.ap.models.vendor import Vendor
from _clean.mvp.domains.ar.models.invoice import Invoice
from _clean.mvp.domains.bank.models.account import Account
from _clean.mvp.infra.vendor_normalization.services import VendorNormalizationService
from _clean.mvp.domains.policy.services.policy_engine import PolicyEngineService
from _clean.mvp.domains.policy.models.suggestion import Suggestion
from _clean.mvp.domains.policy.models.correction import Correction

# REF: Leverage existing architecture components
from _clean.mvp.infra.rails.qbo.client import QBOClient
from _clean.mvp.infra.sync.orchestrator import SyncOrchestrator
from _clean.mvp.runway.services.console_service import ConsoleService
from _clean.mvp.domains.ap.gateways import APGateway
from _clean.mvp.domains.ar.gateways import ARGateway

# Add template system to existing structure
from _clean.mvp.infra.templates import TemplateRenderer
from _clean.mvp.infra.templates import GLClassifier
```

#### Success Criteria
- [ ] Only template-system-specific models and services ported to `_clean/mvp/`
- [ ] Policy engine components ported for transaction categorization
- [ ] Vendor normalization service ported for GL mapping
- [ ] Domain gateways verified and completed for template system
- [ ] All imports updated to use `_clean/mvp/` paths
- [ ] Multi-tenant structure preserved in all ported models
- [ ] Template system leverages existing sophisticated services
- [ ] "Fast Follow" enhancements documented for future development
- [ ] No unnecessary wholesale porting of unused services

#### Fast Follow Enhancements (Post-MVP)
**Learning Loop Integration:**
- [ ] Integrate correction/suggestion models for template learning
- [ ] Implement policy engine feedback loop for GL classification improvements
- [ ] Add user correction tracking for template accuracy

**Advanced Vendor Management:**
- [ ] Integrate vendor payment history into template generation
- [ ] Use vendor criticality flags for template prioritization
- [ ] Leverage W9 status for compliance-aware templates

**Policy Engine Sophistication:**
- [ ] Implement vertical specializations (ServicePro, Property Management)
- [ ] Add rule learning from user corrections
- [ ] Integrate confidence scoring with template generation

**Payment Integration:**
- [ ] Use payment urgency calculations in cash flow templates
- [ ] Integrate payment method preferences into vendor categorization
- [ ] Add payment history insights to template recommendations

---

### Task 0.2: Enhance Existing QBO Integration
**Duration:** 3 days  
**Dependencies:** Task 0.1  

#### Requirements
- [ ] Review existing QBO client in `_clean/mvp/infra/rails/qbo/`
- [ ] Enhance existing OAuth2 flow for multi-client support
- [ ] Extend data fetching functions for template system needs
- [ ] Leverage existing error handling and retry logic

#### Deliverables
- [ ] Enhanced QBO client for template system
- [ ] Multi-client authentication support
- [ ] Extended data fetching for GL classification
- [ ] Integration with existing sync orchestrator

#### Code Implementation
```python
# Enhance existing QBO client to leverage COA and transaction models
from _clean.mvp.infra.rails.qbo.client import QBOClient
from _clean.mvp.infra.rails.qbo.auth import QBOAuth
# Import ported models from _clean/mvp/
from _clean.mvp.domains.core.models.transaction import Transaction
from _clean.mvp.domains.core.models.business import Business
from _clean.mvp.domains.ap.models.coa_template import COATemplate
from _clean.mvp.domains.ap.models.vendor_category import VendorCategory

class TemplateQBOClient(QBOClient):
    def __init__(self, business_id: str, db_session):
        super().__init__(business_id)
        self.business_id = business_id
        self.db = db_session
    
    def get_business_industry(self) -> str:
        """Get business industry from existing Business model"""
        # NOTE: Leverage existing Business model with industry field
        business = self.db.query(Business).filter(Business.business_id == self.business_id).first()
        return business.industry if business else "general"
    
    def get_coa_template(self) -> COATemplate:
        """Get COA template based on business industry"""
        # NOTE: Leverage existing COA template system by industry
        industry = self.get_business_industry()
        return self.db.query(COATemplate).filter(
            COATemplate.industry == industry,
            COATemplate.is_active == True
        ).first()
    
    def get_vendor_categories(self) -> List[VendorCategory]:
        """Get vendor categories with GL mapping"""
        # NOTE: Leverage existing vendor category system
        return self.db.query(VendorCategory).all()
    
    def get_transactions_with_confidence(self, days_back=90) -> List[Transaction]:
        """Get transactions with existing confidence scoring and status"""
        # NOTE: Leverage existing Transaction model with confidence and status
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        return self.db.query(Transaction).filter(
            Transaction.business_id == self.business_id,
            Transaction.date >= cutoff_date,
            Transaction.status.in_(["matched", "unmatched"])
        ).all()
    
    def classify_transactions_by_gl(self, transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
        """Classify transactions using existing COA template and vendor categories"""
        # NOTE: Use existing COA template and vendor categories for GL classification
        coa_template = self.get_coa_template()
        vendor_categories = self.get_vendor_categories()
        
        classified = {
            "revenue": [],
            "expenses": [],
            "payroll": [],
            "unclassified": []
        }
        
        for tx in transactions:
            # Use COA template to map GL accounts
            gl_account = self._map_to_gl_account(tx, coa_template, vendor_categories)
            
            if gl_account.startswith("4"):  # Revenue range
                classified["revenue"].append(tx)
            elif gl_account.startswith("601"):  # Payroll range
                classified["payroll"].append(tx)
            elif gl_account.startswith("6"):  # Expense range
                classified["expenses"].append(tx)
            else:
                classified["unclassified"].append(tx)
        
        return classified
    
    def _map_to_gl_account(self, tx: Transaction, coa_template: COATemplate, vendor_categories: List[VendorCategory]) -> str:
        """Map transaction to GL account using existing COA template and vendor categories"""
        # NOTE: Use existing vendor categories for GL mapping
        if tx.vendor_name:
            for category in vendor_categories:
                if category.category_name.lower() in tx.vendor_name.lower():
                    return category.default_gl_account
        
        # Fallback to COA template mapping
        if coa_template:
            # Use COA template to determine GL account based on transaction type
            if tx.type in ["deposit", "revenue"]:
                return "4000-4999"  # Revenue range
            elif tx.type in ["expense", "bill"]:
                return "6000-6999"  # Expense range
            elif tx.type == "payroll":
                return "60100-60199"  # Payroll range
        
        return "6000-6999"  # Default to expense
```

#### Success Criteria
- [ ] Existing QBO client enhanced for template system
- [ ] Multi-client support working properly
- [ ] GL classification data accessible
- [ ] Integration with existing sync patterns

---

### Task 0.3: Leverage Existing Classification Systems
**Duration:** 4 days  
**Dependencies:** Task 0.2  

#### Requirements
- [ ] Integrate with existing vendor normalization system (`_parked/vendor_normalization/`)
- [ ] Use existing policy engine for Cash Decision Model (CDM) categorization
- [ ] Leverage existing COA templates by industry (`domains/ap/models/coa_template.py`)
- [ ] Integrate with existing vendor categories and GL mapping (`coa_map.yaml`)

#### Deliverables
- [ ] `_clean/mvp/infra/templates/classification_service.py` - Integration with existing systems
- [ ] Enhanced vendor normalization for template system
- [ ] Policy engine integration for cash flow categorization
- [ ] COA template selection based on business industry

#### Code Implementation
```python
# _clean/mvp/infra/templates/classification_service.py
# NOTE: Leverage existing systems in _clean/mvp/ and PORT additional models
# Already available in _clean/mvp/:
# - _clean.mvp.domains.ap.gateways.BillsGateway (REF: existing AP gateway)
# - _clean.mvp.domains.ar.gateways.InvoicesGateway (REF: existing AR gateway)
# - _clean.mvp.domains.bank.gateways.BalancesGateway (REF: existing bank gateway)
# - _clean.mvp.infra.db.models.MirrorBill, MirrorInvoice, MirrorBalance (REF: existing mirror tables)
# - _clean.mvp.runway.services.console_service.ConsoleService (REF: existing console service)
# Available to PORT:
# - domains/ap/models/coa_template.py (PORT: COA templates by industry)
# - domains/ap/models/vendor_category.py (PORT: vendor categories with GL mapping)
# - _parked/vendor_normalization/ (ADAPT: vendor normalization - use selectively)

from typing import Dict, Tuple, Any, List
from _clean.mvp.domains.ap.gateways import BillsGateway, ListBillsQuery
from _clean.mvp.domains.ar.gateways import InvoicesGateway, ListInvoicesQuery
from _clean.mvp.domains.bank.gateways import BalancesGateway, ListBalancesQuery
from _clean.mvp.runway.services.console_service import ConsoleService
# Import ported models from _clean/mvp/
from _clean.mvp.domains.ap.models.coa_template import COATemplate
from _clean.mvp.domains.ap.models.vendor_category import VendorCategory

class TemplateClassificationService:
    def __init__(self, advisor_id: str, business_id: str, 
                 bills_gateway: BillsGateway, invoices_gateway: InvoicesGateway, 
                 balances_gateway: BalancesGateway, console_service: ConsoleService,
                 business_service: BusinessService, vendor_normalization_service: VendorNormalizationService,
                 policy_engine: PolicyEngineService):
        self.advisor_id = advisor_id
        self.business_id = business_id
        self.bills_gateway = bills_gateway
        self.invoices_gateway = invoices_gateway
        self.balances_gateway = balances_gateway
        self.console_service = console_service
        self.business_service = business_service
        self.vendor_normalization_service = vendor_normalization_service
        self.policy_engine = policy_engine
    
    async def classify_transactions_for_template(self) -> Tuple[Dict[str, Dict], Dict[str, Any]]:
        """Classify transactions using existing services and domain gateways"""
        # Get business using existing BusinessService
        # NOTE: Leverage existing BusinessService for business operations
        business = self.business_service.get_business(self.business_id)
        if not business:
            raise ValueError(f"Business {self.business_id} not found")
        industry = business.industry
        
        # Get COA template for industry
        # NOTE: Leverage existing COA template system by industry
        coa_template = self.db.query(COATemplate).filter(
            COATemplate.industry == industry,
            COATemplate.is_active == True
        ).first()
        
        # Get vendor categories with GL mapping
        # NOTE: Leverage existing vendor category system
        vendor_categories = self.db.query(VendorCategory).all()
        
        # Get transactions with existing confidence scoring and status
        # NOTE: Leverage existing Transaction model with confidence and status
        transactions = self.db.query(Transaction).filter(
            Transaction.business_id == self.business_id,
            Transaction.status.in_(["matched", "unmatched"])
        ).all()
        
        # Classify transactions using existing COA template and vendor categories
        classified_transactions = []
    
        for tx in transactions:
            # Use sophisticated policy engine for transaction categorization
            # NOTE: Leverage existing PolicyEngineService for rule-based categorization
            txn_data = {
                "txn_id": tx.transaction_id,
                "description": tx.description or "",
                "amount": float(tx.amount),
                "vendor_name": tx.vendor_name,
                "category": tx.type
            }
            
            # Get policy engine categorization with confidence scoring
            suggestion = self.policy_engine.categorize_transaction(txn_data, self.business_id)
            
            # Use top suggestion from policy engine
            if suggestion.top_k:
                top_suggestion = suggestion.top_k[0]
                gl_account = top_suggestion["account"]
                vendor_category = top_suggestion["rule_name"]
                confidence = top_suggestion["confidence"]
            else:
                # Fallback to vendor normalization
                if tx.vendor_name:
                    vendor_canonical = self.vendor_normalization_service.normalize_vendor(
                        tx.vendor_name, self.business_id
                    )
                    gl_account = vendor_canonical.default_gl_account
                    vendor_category = vendor_canonical.canonical_name
                    confidence = vendor_canonical.confidence
                else:
                    gl_account = "6000-6999"  # Default expense
                    vendor_category = "Other Expenses"
                    confidence = 0.3
            
            classified_transactions.append({
                "id": tx.transaction_id,
                "type": tx.type,  # deposit, expense, reimbursement, payroll
                "amount": float(tx.amount),
                "date": tx.date,
                "vendor_name": tx.vendor_name,
                "gl_account": gl_account,
                "category": vendor_category,
                "confidence": tx.confidence,
                "status": tx.status
            })
        
        # Get additional data from domain gateways for context
        bills_query = ListBillsQuery(
            advisor_id=self.advisor_id,
            business_id=self.business_id,
            status="ALL",
            freshness_hint="CACHED_OK"
        )
        bills = await self.bills_gateway.list(bills_query)
        
        invoices_query = ListInvoicesQuery(
            advisor_id=self.advisor_id,
            business_id=self.business_id,
            status="ALL",
            freshness_hint="CACHED_OK"
        )
        invoices = await self.invoices_gateway.list(invoices_query)
        
        balances_query = ListBalancesQuery(
            advisor_id=self.advisor_id,
            business_id=self.business_id,
            freshness_hint="CACHED_OK"
        )
        balances = await self.balances_gateway.list(balances_query)
        
        return self._group_by_cash_flow_categories(classified_transactions, balances, coa_template)
    
    def _map_transaction_to_gl(self, tx: Transaction, coa_template: COATemplate, vendor_categories: List[VendorCategory]) -> str:
        """Map transaction to GL account using existing COA template and vendor categories"""
        # NOTE: Use existing vendor categories for GL mapping
        if tx.vendor_name:
            for category in vendor_categories:
                if category.category_name.lower() in tx.vendor_name.lower():
                    return category.default_gl_account
        
        # Fallback to COA template mapping
        if coa_template:
            # Use COA template to determine GL account based on transaction type
            if tx.type in ["deposit", "revenue"]:
                return "4000-4999"  # Revenue range
            elif tx.type in ["expense", "bill"]:
                return "6000-6999"  # Expense range
            elif tx.type == "payroll":
                return "60100-60199"  # Payroll range
        
        return "6000-6999"  # Default to expense
    
    def _get_vendor_category(self, tx: Transaction, vendor_categories: List[VendorCategory]) -> str:
        """Get vendor category using existing vendor category system"""
        # NOTE: Use existing vendor categories for categorization
        if tx.vendor_name:
            for category in vendor_categories:
                if category.category_name.lower() in tx.vendor_name.lower():
                    return category.category_name
        
        # Fallback to simple categorization
        if tx.type == "payroll":
            return "Payroll"
        elif tx.type in ["deposit", "revenue"]:
            return "Revenue"
        else:
            return "Other Expenses"
    
    def _map_bill_to_gl(self, bill) -> str:
        """Map bill to GL account using existing vendor data"""
        # TODO: Enhance with vendor normalization system after PORTing
        # For now, use simple mapping based on vendor name
        vendor_name = bill.vendor_name.lower() if bill.vendor_name else ""
        
        if any(word in vendor_name for word in ["rent", "lease", "office"]):
            return "6100-6199"  # Rent & Utilities
        elif any(word in vendor_name for word in ["payroll", "salary", "wage"]):
            return "60100-60199"  # Payroll
        elif any(word in vendor_name for word in ["software", "saas", "subscription"]):
            return "6200-6299"  # Software Subscriptions
        else:
            return "6000-6999"  # General Expenses
    
    def _categorize_bill(self, bill) -> str:
        """Categorize bill for cash flow template"""
        # TODO: Use vendor categories after PORTing
        vendor_name = bill.vendor_name.lower() if bill.vendor_name else ""
        
        if any(word in vendor_name for word in ["rent", "lease", "office"]):
            return "Rent & Utilities"
        elif any(word in vendor_name for word in ["payroll", "salary", "wage"]):
            return "Payroll"
        elif any(word in vendor_name for word in ["software", "saas", "subscription"]):
            return "Software Subscriptions"
        else:
            return "Other Expenses"
```

#### Success Criteria
- [ ] Integration with existing vendor normalization system
- [ ] Policy engine CDM categorization working
- [ ] COA template selection by industry
- [ ] Confidence scoring from existing transaction models

---

### Task 0.4: Excel Template System with COA Integration
**Duration:** 3 days  
**Dependencies:** Task 0.3  

#### Requirements
- [ ] Create Excel template system using existing COA templates by industry
- [ ] Implement formula preservation system with GL account mapping
- [ ] Add color coding based on vendor categories and CDM classifications
- [ ] Integrate with existing runway orchestration and audit logging

#### Deliverables
- [ ] `_clean/mvp/infra/templates/template_renderer.py` - Excel population with COA integration
- [ ] Industry-specific template generation using COATemplate models
- [ ] Template validation using existing vendor categories
- [ ] Integration with existing console service and audit logging

#### Code Implementation
```python
# _clean/mvp/infra/templates/template_renderer.py
# NOTE: Leverage existing systems in _clean/mvp/ and PORT additional models
# Already available in _clean/mvp/:
# - _clean.mvp.runway.services.console_service.ConsoleService (REF: existing console service)
# - _clean.mvp.domains.ap.gateways.BillsGateway (REF: existing AP gateway)
# - _clean.mvp.domains.ar.gateways.InvoicesGateway (REF: existing AR gateway)
# - _clean.mvp.domains.bank.gateways.BalancesGateway (REF: existing bank gateway)
# Available to PORT:
# - domains/ap/models/coa_template.py (PORT: COA templates by industry)
# - domains/ap/models/vendor_category.py (PORT: vendor categories with GL mapping)
# - domains/core/models/audit_log.py (PORT: audit logging for compliance)

from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from typing import Dict, List
from _clean.mvp.runway.services.console_service import ConsoleService
from _clean.mvp.domains.ap.gateways import BillsGateway
from _clean.mvp.domains.ar.gateways import InvoicesGateway
from _clean.mvp.domains.bank.gateways import BalancesGateway
# Import ported models from _clean/mvp/
from _clean.mvp.domains.ap.models.coa_template import COATemplate
from _clean.mvp.domains.ap.models.vendor_category import VendorCategory
# from _clean.mvp.domains.core.models.audit_log import AuditLog, AuditAction, AuditSource

class COATemplateRenderer:
    def __init__(self, advisor_id: str, business_id: str, 
                 console_service: ConsoleService, classification_service):
        self.advisor_id = advisor_id
        self.business_id = business_id
        self.console_service = console_service
        self.classification_service = classification_service
    
    async def render_workbook_from_coa(self, industry: str, output_path: str) -> str:
        """Render Excel workbook using existing models and console service"""
        # Get business industry from existing Business model
        # NOTE: Leverage existing Business model with industry field
        business = self.db.query(Business).filter(Business.business_id == self.business_id).first()
        actual_industry = business.industry if business else industry
        
        # Get COA template for industry
        # NOTE: Leverage existing COA template system by industry
        coa_template = self.db.query(COATemplate).filter(
            COATemplate.industry == actual_industry,
            COATemplate.is_active == True
        ).first()
        
        # Get financial snapshot using existing console service
        # NOTE: Leverage existing console service for financial data
        snapshot = await self.console_service.get_console_snapshot()
        
        # Get classified transactions using existing classification service
        # NOTE: Use existing classification service for transaction data
        classified_data, data_quality = await self.classification_service.classify_transactions_for_template()
        
        # Create workbook based on COA template
        # NOTE: Use existing COA template structure
        wb = self._create_workbook_from_coa_template(coa_template)
        ws = wb["Cash Flow"]
        
        # Populate with existing financial data
        # NOTE: Use existing console service financial data and COA template structure
        self._populate_cash_flow_data(ws, snapshot, classified_data, coa_template)
        
        # Apply color coding based on vendor categories
        # NOTE: Use existing vendor categorization
        self._apply_color_coding(ws, classified_data)
        
        # Log template generation for audit trail
        # NOTE: Use existing audit logging after PORTing
        self._log_template_generation(output_path, coa_template)
    
    wb.save(output_path)
    return output_path
    
    def _create_workbook_from_coa_template(self, coa_template: COATemplate):
        """Create workbook structure based on existing COA template"""
        # NOTE: Use existing COA template structure for workbook creation
        if coa_template:
            # Use COA template to structure the workbook
            wb = load_workbook("templates/base_template.xlsx")
            # TODO: Customize workbook structure based on COA template
            return wb
        else:
            # Fallback to generic template
            wb = load_workbook("templates/base_template.xlsx")
            return wb
    
    def _populate_cash_flow_data(self, ws, snapshot: Dict, classified_data: Dict, coa_template: COATemplate):
        """Populate cash flow data using existing console service data and COA template"""
        # NOTE: Use existing console service financial data and COA template structure
        # Beginning cash from balances
        ws["C2"] = snapshot.get("cash_position", 0)
        
        # Inflows from classified transactions
        inflows = classified_data.get("inflows", [])
        for i, inflow in enumerate(inflows):
            ws[f"C{4+i}"] = inflow["amount"]
            # Use COA template for GL account mapping
            if coa_template:
                ws[f"B{4+i}"] = f"{inflow['gl_account']} - {inflow['category']}"
        
        # Outflows from classified transactions
        outflows = classified_data.get("outflows", [])
        for i, outflow in enumerate(outflows):
            ws[f"C{27+i}"] = outflow["amount"]
            # Use COA template for GL account mapping
            if coa_template:
                ws[f"B{27+i}"] = f"{outflow['gl_account']} - {outflow['category']}"
        
        # Calculate ending cash
        ws["C63"] = "=C2+C25-C77"  # Beginning + Inflows - Outflows
    
    def _apply_color_coding(self, ws, classified_data: Dict):
        """Apply color coding based on vendor categories"""
        # NOTE: Use existing vendor categorization for color coding
        colors = {
            "Rent & Utilities": "FFE6E6",  # Light red
            "Payroll": "E6F3FF",           # Light blue
            "Software Subscriptions": "E6FFE6",  # Light green
            "Other Expenses": "F0F0F0"     # Light gray
        }
        
        # Apply colors to outflow rows
        outflows = classified_data.get("outflows", [])
        for i, outflow in enumerate(outflows):
            category = outflow.get("category", "Other Expenses")
            color = colors.get(category, "F0F0F0")
            fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
            ws[f"C{27+i}"].fill = fill
    
    def _log_template_generation(self, output_path: str, coa_template: COATemplate):
        """Log template generation for audit trail using existing audit log model"""
        # NOTE: Use existing audit logging after PORTing
        # Import ported models from _clean/mvp/
        from _clean.mvp.domains.core.models.audit_log import AuditLog, AuditAction, AuditSource
        
        # Create audit log entry for template generation
        # audit_log = AuditLog(
        #     performed_by_user_id=self.advisor_id,
        #     context_business_id=self.business_id,
        #     source=AuditSource.TEMPLATE_SYSTEM,
        #     action=AuditAction.TEMPLATE_GENERATED,
        #     entity_type="template",
        #     entity_id=output_path,
        #     new_values={
        #         "template_type": "cash_flow",
        #         "industry": coa_template.industry if coa_template else "general",
        #         "output_path": output_path,
        #         "coa_template_id": coa_template.id if coa_template else None
        #     }
        # )
        # self.db.add(audit_log)
        # self.db.commit()
        pass
```

#### Success Criteria
- [ ] COA template integration working by industry
- [ ] Vendor category color coding applied
- [ ] GL account mapping from COA templates
- [ ] Audit logging for template generation

---

### Task 0.5: Enhance Existing API Infrastructure
**Duration:** 2 days  
**Dependencies:** Task 0.4  

#### Requirements
- [ ] Enhance existing FastAPI application in `_clean/mvp/api/`
- [ ] Add template system endpoints to existing API
- [ ] Integrate with existing error handling and logging
- [ ] Extend existing API documentation

#### Deliverables
- [ ] Enhanced API routes for template system
- [ ] Integration with existing runway orchestration
- [ ] Multi-client workbook generation endpoints
- [ ] Updated API documentation

#### Code Implementation
```python
# Enhance existing API in _clean/mvp/api/routes.py
# NOTE: Following strangled fig process - leverage existing systems
# Available systems to integrate:
# - _clean/mvp/runway/services/console_service.py (REF: existing console service)
# - _clean/mvp/infra/templates/ (ADD: new template system)
# - domains/core/models/ (PORT: transaction, business, audit models)
# - domains/ap/models/ (PORT: COA templates, vendor categories)
# - domains/ar/models/ (PORT: invoice models)
# - domains/bank/models/ (PORT: bank transaction models)

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
# TODO: Import from _clean/mvp/ after strangled fig porting:
# from _clean.mvp.runway.services.console_service import ConsoleService
# from _clean.mvp.infra.templates.template_renderer import COATemplateRenderer
# from _clean.mvp.infra.templates.classification_service import TemplateClassificationService

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("/generate-workbook/{business_id}")
async def generate_workbook(
    business_id: str,
    console_service = Depends()  # ConsoleService after porting
):
    """Generate Excel workbook for specific business using existing systems"""
    try:
        # Use existing console service for business data
        # NOTE: Leverage existing console service for business metadata
        business_info = console_service.get_business_info(business_id)
        
        # Initialize template system components
        # NOTE: Use existing classification and rendering services
        classifier = TemplateClassificationService(business_id, db_session, console_service)
        renderer = COATemplateRenderer(business_id, db_session, console_service)
        
        # Generate workbook using existing patterns
        # NOTE: Leverage existing COA templates and vendor categories
        output_path = await renderer.render_workbook_from_coa(
            business_info.get("industry"), 
            f"output/{business_id}_cash_flow.xlsx"
        )
        
        return {
            "success": True,
            "business_id": business_id,
            "output_path": output_path,
            "business_name": business_info.get("name"),
            "industry": business_info.get("industry")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/businesses/{business_id}/data-quality")
async def get_data_quality(business_id: str):
    """Get data quality metrics for business using existing models"""
    # NOTE: Leverage existing console service and transaction models for data quality metrics
    snapshot = await console_service.get_console_snapshot()
    
    # Get additional metrics from existing transaction models
    # NOTE: Leverage existing Transaction model with confidence and status
    total_transactions = db.query(Transaction).filter(
        Transaction.business_id == business_id
    ).count()
    
    matched_transactions = db.query(Transaction).filter(
        Transaction.business_id == business_id,
        Transaction.status == "matched"
    ).count()
    
    unmatched_transactions = db.query(Transaction).filter(
        Transaction.business_id == business_id,
        Transaction.status == "unmatched"
    ).count()
    
    # Calculate confidence score from existing transaction data
    # NOTE: Use existing confidence scoring from transaction models
    high_confidence_transactions = db.query(Transaction).filter(
        Transaction.business_id == business_id,
        Transaction.confidence >= 0.8
    ).count()
    
    data_quality_score = (high_confidence_transactions / total_transactions) if total_transactions > 0 else 0.0
    
    return {
        "total_transactions": total_transactions,
        "matched_transactions": matched_transactions,
        "unmatched_transactions": unmatched_transactions,
        "high_confidence_transactions": high_confidence_transactions,
        "data_quality_score": data_quality_score,
        "last_sync": snapshot.get("last_sync"),
        "sync_status": snapshot.get("sync_status")
    }

@router.get("/businesses/{business_id}/coa-template")
async def get_coa_template(business_id: str):
    """Get COA template for business industry using existing models"""
    # NOTE: Leverage existing Business and COATemplate models
    business = db.query(Business).filter(Business.business_id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get COA template based on business industry
    # NOTE: Use existing COA template system by industry
    coa_template = db.query(COATemplate).filter(
        COATemplate.industry == business.industry,
        COATemplate.is_active == True
    ).first()
    
    if not coa_template:
        # Fallback to generic template
        coa_template = db.query(COATemplate).filter(
            COATemplate.industry == "general",
            COATemplate.is_active == True
        ).first()
    
    return {
        "business_id": business_id,
        "business_name": business.name,
        "industry": business.industry,
        "coa_template": {
            "id": coa_template.id if coa_template else None,
            "template_name": coa_template.template_name if coa_template else "Generic",
            "industry": coa_template.industry if coa_template else "general",
            "is_active": coa_template.is_active if coa_template else False
        }
    }

@router.get("/businesses/{business_id}/vendor-categories")
async def get_vendor_categories(business_id: str):
    """Get vendor categories for business using existing models"""
    # NOTE: Leverage existing vendor category system
    vendor_categories = db.query(VendorCategory).all()
    
    return {
        "business_id": business_id,
        "vendor_categories": [
            {
                "id": cat.id,
                "name": cat.category_name,
                "gl_account": cat.default_gl_account,
                "description": cat.description,
                "is_active": cat.is_active
            } for cat in vendor_categories
        ],
        "total_categories": len(vendor_categories)
    }
```

#### Success Criteria
- [ ] Template endpoints integrate with existing API
- [ ] Multi-client support through business_id routing
- [ ] Data quality metrics using existing transaction models
- [ ] COA template selection using existing Business and COATemplate models
- [ ] Vendor category integration using existing VendorCategory models
- [ ] Audit logging integration using existing AuditLog model
- [ ] Error handling uses existing patterns
- [ ] API documentation includes template system

---

### Task 0.6: Multi-Client Pilot Validation
**Duration:** 3 days  
**Dependencies:** Task 0.5  

#### Requirements
- [ ] Test with multiple client types (nonprofit, agency, SaaS)
- [ ] Validate template adaptability across segments
- [ ] Gather feedback from diverse CAS firms
- [ ] Document lessons learned and market insights

#### Deliverables
- [ ] Working pilots with diverse client types
- [ ] Market segment feedback documentation
- [ ] Template adaptability improvements
- [ ] Broader market validation metrics

#### Success Criteria
- [ ] Multiple client types successfully onboarded
- [ ] Data quality score > 80% across segments
- [ ] Template adaptability proven
- [ ] Market feedback incorporated for broader appeal

---

## 📋 Phase 1: Firm Console (Weeks 3-6)
**Goal:** Multi-client management with learning feedback  
**Deliverable:** Firm dashboard and client management system  

### Task 1.1: Database Setup
**Duration:** 2 days  
**Dependencies:** Phase 0 complete  

#### Requirements
- [ ] Set up SQLite database for MVP
- [ ] Create client and firm data models
- [ ] Implement basic CRUD operations
- [ ] Add data migration system

#### Deliverables
- [ ] `app/database.py` - Database connection and models
- [ ] `app/models.py` - Pydantic models
- [ ] Database schema migration system
- [ ] Basic data access layer

---

### Task 1.2: Client Management System
**Duration:** 4 days  
**Dependencies:** Task 1.1  

#### Requirements
- [ ] Create client onboarding workflow
- [ ] Implement QBO connection management
- [ ] Add template selection system
- [ ] Create client data management

#### Deliverables
- [ ] Client onboarding API endpoints
- [ ] QBO connection management
- [ ] Template selection system
- [ ] Client data CRUD operations

---

### Task 1.3: Firm Dashboard (React Frontend)
**Duration:** 5 days  
**Dependencies:** Task 1.2  

#### Requirements
- [ ] Create React application with Tailwind CSS
- [ ] Build client list and management interface
- [ ] Add workbook generation controls
- [ ] Implement data quality monitoring

#### Deliverables
- [ ] React application with routing
- [ ] Client management dashboard
- [ ] Workbook generation interface
- [ ] Data quality monitoring display

---

### Task 1.4: Scheduling System
**Duration:** 3 days  
**Dependencies:** Task 1.3  

#### Requirements
- [ ] Implement background job scheduling
- [ ] Add automated refresh system
- [ ] Create notification system
- [ ] Add job monitoring

#### Deliverables
- [ ] Background job scheduler
- [ ] Automated refresh system
- [ ] Email notification system
- [ ] Job monitoring dashboard

---

## 📋 Phase 2: Template Manager (Weeks 7-12)
**Goal:** Configurable templates per firm  
**Deliverable:** Template management system with YAML configuration  

### Task 2.1: YAML Template System
**Duration:** 5 days  
**Dependencies:** Phase 1 complete  

#### Requirements
- [ ] Implement YAML template parser
- [ ] Create template validation system
- [ ] Add template versioning
- [ ] Build template editor

#### Deliverables
- [ ] YAML template parser
- [ ] Template validation system
- [ ] Template versioning system
- [ ] Template editor interface

---

### Task 2.2: Template Upload System
**Duration:** 4 days  
**Dependencies:** Task 2.1  

#### Requirements
- [ ] Create Excel upload functionality
- [ ] Implement template analysis
- [ ] Add template conversion to YAML
- [ ] Build template preview system

#### Deliverables
- [ ] Excel upload system
- [ ] Template analysis engine
- [ ] YAML conversion system
- [ ] Template preview interface

---

### Task 2.3: Advanced Rendering
**Duration:** 4 days  
**Dependencies:** Task 2.2  

#### Requirements
- [ ] Implement dynamic template rendering
- [ ] Add multi-format output support
- [ ] Create template customization system
- [ ] Add advanced formatting options

#### Deliverables
- [ ] Dynamic template renderer
- [ ] Multi-format output system
- [ ] Template customization interface
- [ ] Advanced formatting engine

---

## 📋 Phase 3: Advisory & Insights (Weeks 13-18)
**Goal:** Transition to Control Plane with client deliverables  
**Deliverable:** Advisory features and client-facing tools  

### Task 3.1: PDF Generation System
**Duration:** 3 days  
**Dependencies:** Phase 2 complete  

#### Requirements
- [ ] Implement PDF generation from Excel
- [ ] Add branding and customization
- [ ] Create summary report templates
- [ ] Add chart generation

#### Deliverables
- [ ] PDF generation system
- [ ] Branding customization
- [ ] Summary report templates
- [ ] Chart generation engine

---

### Task 3.2: Analytics Engine
**Duration:** 5 days  
**Dependencies:** Task 3.1  

#### Requirements
- [ ] Implement variance analysis
- [ ] Add trend detection
- [ ] Create forecasting algorithms
- [ ] Build insight generation

#### Deliverables
- [ ] Variance analysis engine
- [ ] Trend detection system
- [ ] Forecasting algorithms
- [ ] Insight generation system

---

### Task 3.3: Client Portal
**Duration:** 4 days  
**Dependencies:** Task 3.2  

#### Requirements
- [ ] Create client-facing dashboard
- [ ] Add read-only access controls
- [ ] Implement report sharing
- [ ] Add client feedback system

#### Deliverables
- [ ] Client portal application
- [ ] Access control system
- [ ] Report sharing functionality
- [ ] Client feedback system

---

## 📋 Phase 4: Control Plane Platform (Weeks 19-24)
**Goal:** Always-on advisory infrastructure  
**Deliverable:** Full Control Plane platform with real-time features  

### Task 4.1: Real-time Dashboard
**Duration:** 5 days  
**Dependencies:** Phase 3 complete  

#### Requirements
- [ ] Implement real-time data updates
- [ ] Create interactive dashboards
- [ ] Add alert system
- [ ] Build decision support tools

#### Deliverables
- [ ] Real-time dashboard system
- [ ] Interactive visualization tools
- [ ] Alert and notification system
- [ ] Decision support interface

---

### Task 4.2: Advanced Integrations
**Duration:** 4 days  
**Dependencies:** Task 4.1  

#### Requirements
- [ ] Add RAMP integration
- [ ] Implement Stripe integration
- [ ] Create API for third-party tools
- [ ] Add webhook system

#### Deliverables
- [ ] RAMP integration
- [ ] Stripe integration
- [ ] Third-party API
- [ ] Webhook system

---

### Task 4.3: Enterprise Features
**Duration:** 3 days  
**Dependencies:** Task 4.2  

#### Requirements
- [ ] Implement multi-firm architecture
- [ ] Add advanced security features
- [ ] Create enterprise billing system
- [ ] Add compliance features

#### Deliverables
- [ ] Multi-firm architecture
- [ ] Advanced security system
- [ ] Enterprise billing
- [ ] Compliance features

---

## 🧪 Testing Strategy

### Unit Testing
- [ ] API endpoint testing
- [ ] Data processing logic testing
- [ ] Template rendering testing
- [ ] QBO integration testing

### Integration Testing
- [ ] End-to-end workflow testing
- [ ] Multi-client scenario testing
- [ ] Error handling testing
- [ ] Performance testing

### User Acceptance Testing
- [ ] Mission First pilot testing
- [ ] Additional firm pilot testing
- [ ] User feedback collection
- [ ] Iteration based on feedback

---

## 📊 Success Metrics

### Phase 0 Success Criteria
- [ ] Generate working Excel workbook from QBO data across multiple client types
- [ ] Achieve 80%+ data quality score on diverse test data
- [ ] Complete pilots with 2+ different CAS firm types
- [ ] Demonstrate 2+ hour time savings per client across segments
- [ ] Validate GL-based learning system with diverse GL structures

### Phase 1 Success Criteria
- [ ] Support 5+ clients across different market segments
- [ ] Achieve 90%+ data quality score through learning system
- [ ] Complete 3+ firm pilots across CAS 1.0 and CAS 2.0 segments
- [ ] Generate $1K+ monthly recurring revenue
- [ ] Demonstrate template adaptability across client types

### Phase 2 Success Criteria
- [ ] Support 25+ clients across 5+ different CAS firms
- [ ] Achieve 95%+ data quality score
- [ ] Complete 5+ firm pilots successfully
- [ ] Generate $5K+ monthly recurring revenue
- [ ] Successful deployment of both Planner and Control Plane modes

### Phase 3 Success Criteria
- [ ] Support 50+ clients with advisory features across segments
- [ ] Achieve 98%+ data quality score
- [ ] Complete 10+ firm pilots successfully
- [ ] Generate $10K+ monthly recurring revenue
- [ ] Template library supporting 3+ industry verticals

### Phase 4 Success Criteria
- [ ] Support 100+ clients with Control Plane features
- [ ] Achieve 99%+ data quality score
- [ ] Complete 20+ firm pilots successfully
- [ ] Generate $25K+ monthly recurring revenue
- [ ] Market leadership in CAS automation space

---

## 🚨 Risk Mitigation

### Technical Risks
- **QBO API Reliability**: Implement robust error handling and fallback mechanisms
- **Data Quality Issues**: Build learning algorithms and manual override capabilities
- **Template Complexity**: Use YAML-based configuration system

### Business Risks
- **Client Adoption**: Implement pilot program and value demonstration
- **Scalability**: Use modular architecture and cloud infrastructure
- **Competition**: Focus on unique value proposition and client relationships

---

## 📝 Documentation Requirements

### Technical Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Code documentation and comments
- [ ] Database schema documentation
- [ ] Deployment and operations guide

### User Documentation
- [ ] User manual for firm console
- [ ] Template configuration guide
- [ ] Client onboarding guide
- [ ] Troubleshooting guide

---

## 🎯 Conclusion

This build plan provides a comprehensive roadmap for implementing the RowCol MVP, leveraging an existing multi-tenant architecture to build a comprehensive cash control platform for the broader CAS market. The phased approach allows for iterative development, client feedback, and risk mitigation while building toward the broader RowCol vision.

**Key Strategic Advantages:**
- **Existing Multi-Tenant Foundation**: Leverages proven architecture for rapid development
- **Broader Market Opportunity**: Addresses full spectrum of CAS needs from traditional to advisory
- **Ahead of Adoption Curve**: Most CAS firms haven't seen this level of automation yet
- **Dual-Mode Strategy**: Serves both CAS 1.0 (automation) and CAS 2.0 (advisory) firms

Each phase builds upon the existing architecture while adding increasingly sophisticated features. The focus on multiple market segments from the start provides broader validation and faster market penetration.

**Next Steps:** Begin Phase 0 implementation with Task 0.1 (Leverage Existing Architecture) to understand and map the current foundation.
