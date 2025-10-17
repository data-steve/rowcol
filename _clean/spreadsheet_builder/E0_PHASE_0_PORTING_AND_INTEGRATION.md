// *** PHASE 0 GUARDRAIL: PORTING GL-BASED INFRASTRUCTURE ***
// 
// This phase ports existing GL-based classification models/services from
// domains/ to _clean/mvp/ following the strangled fig pattern.
// 
// WHY NOT BUILDING FROM SCRATCH:
// - domains/ already has GL classification logic (proven patterns)
// - We're adapting, not inventing
// - Multi-tenant structure is already there
// 
// WHAT WE'RE PORTING (selective, not wholesale):
// ✅ Business model (industry detection for COA selection)
// ✅ Transaction model (confidence, status for learning)
// ✅ COA templates (GL mapping by industry - universal, not vendor-specific)
// ✅ Vendor categories (GL account mapping for classification)
// ✅ Policy engine (rule-based categorization foundation)
// ✅ Vendor normalization (fallback confidence scoring)
// 
// WHAT WE'RE NOT DOING:
// ❌ Porting AR/bank/payment services (not needed for MVP)
// ❌ Porting anything with hardcoded vendor names
// ❌ Porting anything specific to Mission First
// 
// THE GOAL:
// By end of Phase 0, have GL-based classification infrastructure in _clean/mvp/
// ready for Phase 1 to use for temporal bucketing and template population.
// 
// *** Remember: GL ranges (4000-4999, 6000-6999, 60100-60199) work for ANY client ***
// *** NOT vendor names, NOT client-specific rules ***
//

# RowCol MVP Phase 0 - Porting and Integration Tasks

**Status:** Ready for Execution  
**Phase:** Foundation (Weeks 1-2)  
**Goal:** Leverage existing architecture and port selective components for template system

---

## **CRITICAL: Context Files (MANDATORY)**

### **Architecture Context:**
- `_clean/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy
- `_clean/architecture/ADR-001-domains-runway-separation.md` - Domain separation

### **Product Context:**
- `_clean/mvp/mvp_comprehensive_prd.md` - MVP PRD

### **Recovery Context:**
- `_clean/strangled_fig/migration_manifest.md` - Strangled fig process

### **Current Phase Context:**
- **Goal:** Port only template-system-specific models/services selectively
- **Principle:** Only PORT what MVP needs, ADAPT where helpful, REF existing systems
- **Database:** SQLite `rowcol.db`
- **Testing:** Real QBO API calls, no mocking

---

## **E0.1: Port Core Models (Business, Transaction, Audit)**

**Status:** `[ ]` Not started  
**Priority:** P0 Critical  
**Duration:** 2 days  
**Dependencies:** None

### **Problem Statement**
Template system needs Business model (industry detection), Transaction model (confidence scoring), and AuditLog model (compliance tracking) to function properly.

### **Solution Overview**
Copy specific core models from `domains/core/models/` to `_clean/mvp/domains/core/models/`, preserving multi-tenant structure and removing legacy dependencies.

### **CRITICAL: Assumption Validation Before Execution**

**Discovery Documentation:**
```
### What Actually Exists:
- [Search for existing core models in domains/core/]

### What the Task Assumed:
- [Task assumes these models exist and are used by template system]

### Assumptions That Were Wrong:
- [List any mismatches found]

### Architecture Mismatches:
- [Where current differs from intended]

### Task Scope Issues:
- [Are we solving the right problem?]
```

### **Discovery Commands:**
```bash
# Find core models
find domains/core/models/ -name "*.py" -type f

# Check for business model
grep -r "class Business" . --include="*.py" | head -5

# Check for transaction model
grep -r "class Transaction" . --include="*.py" | head -5

# Check for audit log model
grep -r "class AuditLog" . --include="*.py" | head -5

# Find imports of these models
grep -r "from domains.core.models" . --include="*.py" | head -20
```

### **Files to Port (SELECTIVE):**
- `domains/core/models/business.py` → `_clean/mvp/domains/core/models/business.py`
- `domains/core/models/transaction.py` → `_clean/mvp/domains/core/models/transaction.py`
- `domains/core/models/audit_log.py` → `_clean/mvp/domains/core/models/audit_log.py`

### **Porting Process:**
1. Read each source file completely
2. Identify all imports and dependencies
3. Check for legacy code that needs removing
4. Copy to new location
5. Update imports to work in _clean/mvp structure
6. Verify no broken imports

### **Verification:**
```bash
# Test imports
python -c "from _clean.mvp.domains.core.models.business import Business; print('✓ Business model imported')"
python -c "from _clean.mvp.domains.core.models.transaction import Transaction; print('✓ Transaction model imported')"
python -c "from _clean.mvp.domains.core.models.audit_log import AuditLog; print('✓ AuditLog model imported')"
```

### **Definition of Done:**
- [ ] All 3 core models copied to `_clean/mvp/domains/core/models/`
- [ ] All imports updated to work in new structure
- [ ] No legacy dependencies remaining
- [ ] Models can be imported without errors
- [ ] Multi-tenant structure preserved (business_id fields intact)

### **Git Commit:**
```bash
git add _clean/mvp/domains/core/models/
git commit -m "feat: port core models (business, transaction, audit_log) to MVP"
```

---

## **E0.2: Port AP Models (COA Templates, Vendor Categories)**

**Status:** `[ ]` Not started  
**Priority:** P0 Critical  
**Duration:** 1 day  
**Dependencies:** E0.1 complete

### **Problem Statement**
Template system needs COATemplate model (industry-specific GL structures) and VendorCategory model (GL mapping) to classify transactions correctly.

### **Solution Overview**
Copy specific AP models from `domains/ap/models/` to `_clean/mvp/domains/ap/models/`, preserving relationships to core models.

### **Discovery Commands:**
```bash
# Find AP models
find domains/ap/models/ -name "*.py" -type f

# Check for COA template model
grep -r "class COATemplate" . --include="*.py"

# Check for vendor category model
grep -r "class VendorCategory" . --include="*.py"

# Find imports/dependencies
grep -r "from domains.ap.models" . --include="*.py" | head -10
grep -r "from domains.core.models" domains/ap/models/ --include="*.py"
```

### **Files to Port (SELECTIVE):**
- `domains/ap/models/coa_template.py` → `_clean/mvp/domains/ap/models/coa_template.py`
- `domains/ap/models/vendor_category.py` → `_clean/mvp/domains/ap/models/vendor_category.py`

### **Porting Process:**
1. Read each source file completely
2. Identify all dependencies on core models
3. Verify core models already ported (E0.1)
4. Copy to new location
5. Update imports to use _clean/mvp paths
6. Verify relationships to core models work

### **Verification:**
```bash
python -c "from _clean.mvp.domains.ap.models.coa_template import COATemplate; print('✓ COATemplate imported')"
python -c "from _clean.mvp.domains.ap.models.vendor_category import VendorCategory; print('✓ VendorCategory imported')"
```

### **Definition of Done:**
- [ ] Both AP models copied to `_clean/mvp/domains/ap/models/`
- [ ] All imports updated to use _clean/mvp paths
- [ ] Dependencies on core models verified
- [ ] Models can be imported without errors

### **Git Commit:**
```bash
git add _clean/mvp/domains/ap/models/
git commit -m "feat: port AP models (COA templates, vendor categories) to MVP"
```

---

## **E0.3: Port Core Services (BusinessService)**

**Status:** `[ ]` Not started  
**Priority:** P0 Critical  
**Duration:** 1 day  
**Dependencies:** E0.1 complete

### **Problem Statement**
Template system needs BusinessService for business validation and data retrieval (industry detection, business metadata).

### **Solution Overview**
Copy BusinessService from `domains/core/services/` to `_clean/mvp/domains/core/services/`, updating imports to use ported models.

### **Discovery Commands:**
```bash
# Find business service
grep -r "class BusinessService" . --include="*.py"

# Check what it imports
grep -r "from domains" domains/core/services/business.py

# Find all usages
grep -r "BusinessService" . --include="*.py" | head -10
```

### **Files to Port (SELECTIVE):**
- `domains/core/services/business.py` → `_clean/mvp/domains/core/services/business.py`

### **Porting Process:**
1. Read BusinessService completely
2. Identify all model and service dependencies
3. Update imports to use _clean/mvp paths
4. Copy to new location
5. Verify all dependencies are available

### **Verification:**
```bash
python -c "from _clean.mvp.domains.core.services.business import BusinessService; print('✓ BusinessService imported')"
```

### **Definition of Done:**
- [ ] BusinessService copied to `_clean/mvp/domains/core/services/`
- [ ] All imports updated to use _clean/mvp models
- [ ] Service can be imported without errors
- [ ] Dependencies verified available

### **Git Commit:**
```bash
git add _clean/mvp/domains/core/services/
git commit -m "feat: port BusinessService to MVP"
```

---

## **E0.4: Port AP Services (VendorService)**

**Status:** `[ ]` Not started  
**Priority:** P0 High  
**Duration:** 2 days  
**Dependencies:** E0.2 complete

### **Problem Statement**
Template system needs VendorService for vendor categorization and GL mapping to properly classify transactions by vendor.

### **Solution Overview**
Copy VendorService from `domains/ap/services/` to `_clean/mvp/domains/ap/services/`, updating imports to use ported models.

### **Discovery Commands:**
```bash
# Find vendor service
grep -r "class VendorService" . --include="*.py"

# Check dependencies
grep -r "from domains" domains/ap/services/vendor.py

# Find usages
grep -r "VendorService" . --include="*.py" | head -10
```

### **Files to Port (SELECTIVE):**
- `domains/ap/services/vendor.py` → `_clean/mvp/domains/ap/services/vendor.py`

### **Porting Process:**
1. Read VendorService completely
2. Identify all dependencies
3. Update imports to use _clean/mvp paths
4. Copy to new location
5. Verify all model dependencies available

### **Verification:**
```bash
python -c "from _clean.mvp.domains.ap.services.vendor import VendorService; print('✓ VendorService imported')"
```

### **Definition of Done:**
- [ ] VendorService copied to `_clean/mvp/domains/ap/services/`
- [ ] All imports updated to use _clean/mvp models
- [ ] Service can be imported without errors

### **Git Commit:**
```bash
git add _clean/mvp/domains/ap/services/
git commit -m "feat: port VendorService to MVP"
```

---

## **E0.5: Port Vendor Normalization (Selective from _parked)**

**Status:** `[ ]` Not started  
**Priority:** P1 High  
**Duration:** 2 days  
**Dependencies:** E0.2 complete

### **Problem Statement**
Template system needs vendor normalization for GL mapping - standardizing vendor names and mapping them to Chart of Accounts.

### **Solution Overview**
Copy specific vendor normalization components from `_parked/vendor_normalization/` to `_clean/mvp/infra/vendor_normalization/`, porting only what MVP needs.

### **Discovery Commands:**
```bash
# Find vendor normalization files
find _parked/vendor_normalization/ -name "*.py" -type f

# Check structure
ls -la _parked/vendor_normalization/

# Find what imports these
grep -r "from.*vendor_normalization" . --include="*.py" | head -10
```

### **Files to Port (SELECTIVE):**
- `_parked/vendor_normalization/services.py` → `_clean/mvp/infra/vendor_normalization/services.py`
- `_parked/vendor_normalization/models/vendor_canonical.py` → `_clean/mvp/infra/vendor_normalization/models/vendor_canonical.py`

### **Porting Process:**
1. Read both files completely
2. Identify dependencies and legacy code
3. Remove anything not needed for MVP
4. Update imports
5. Copy to new location

### **Verification:**
```bash
python -c "from _clean.mvp.infra.vendor_normalization.services import VendorNormalizationService; print('✓ VendorNormalizationService imported')"
```

### **Definition of Done:**
- [ ] Vendor normalization files copied to `_clean/mvp/infra/vendor_normalization/`
- [ ] All imports updated
- [ ] Only MVP-needed code included (no extra complexity)
- [ ] Can be imported without errors

### **Git Commit:**
```bash
git add _clean/mvp/infra/vendor_normalization/
git commit -m "feat: port vendor normalization to MVP (selective)"
```

---

## **E0.6: Port Policy Engine (Selective from _parked)**

**Status:** `[ ]` Not started  
**Priority:** P1 High  
**Duration:** 2 days  
**Dependencies:** E0.5 complete

### **Problem Statement**
Template system needs policy engine for rule-based transaction categorization with confidence scoring and learning loop support (corrections/suggestions).

### **Solution Overview**
Copy specific policy engine components from `_parked/policy/` to `_clean/mvp/domains/policy/`, porting only core categorization logic for MVP.

### **Discovery Commands:**
```bash
# Find policy files
find _parked/policy/ -name "*.py" -type f

# Check structure
ls -la _parked/policy/

# Find policy engine
grep -r "class PolicyEngine" . --include="*.py"

# Find imports
grep -r "from.*policy" . --include="*.py" | head -10
```

### **Files to Port (SELECTIVE):**
- `_parked/policy/services/policy_engine.py` → `_clean/mvp/domains/policy/services/policy_engine.py`
- `_parked/policy/models/suggestion.py` → `_clean/mvp/domains/policy/models/suggestion.py`
- `_parked/policy/models/correction.py` → `_clean/mvp/domains/policy/models/correction.py`

### **Porting Process:**
1. Read policy engine and models completely
2. Identify core categorization logic needed for MVP
3. Remove learning loop code (fast follow)
4. Update imports
5. Copy to new location

### **Verification:**
```bash
python -c "from _clean.mvp.domains.policy.services.policy_engine import PolicyEngineService; print('✓ PolicyEngineService imported')"
python -c "from _clean.mvp.domains.policy.models.suggestion import Suggestion; print('✓ Suggestion imported')"
python -c "from _clean.mvp.domains.policy.models.correction import Correction; print('✓ Correction imported')"
```

### **Definition of Done:**
- [ ] Policy engine files copied to `_clean/mvp/domains/policy/`
- [ ] All imports updated
- [ ] Only core categorization logic included (learning loop deferred)
- [ ] Models can be imported without errors

### **Git Commit:**
```bash
git add _clean/mvp/domains/policy/
git commit -m "feat: port policy engine to MVP (selective, learning loop deferred)"
```

---

## **E0.7: Update All Imports Across MVP Codebase**

**Status:** `[ ]` Not started  
**Priority:** P0 Critical  
**Duration:** 1 day  
**Dependencies:** E0.1 through E0.6 complete

### **Problem Statement**
After porting models and services, all existing `_clean/mvp/` code needs to be updated to import from the ported locations instead of legacy paths.

### **Solution Overview**
Find all imports across `_clean/mvp/` that reference ported models/services and update them to use new paths.

### **Discovery Commands:**
```bash
# Find legacy imports
grep -r "from domains\." _clean/mvp/ --include="*.py"
grep -r "from _parked\." _clean/mvp/ --include="*.py"

# Find what needs updating
grep -r "import.*Business\|import.*Transaction\|import.*AuditLog" _clean/mvp/ --include="*.py"
grep -r "import.*COATemplate\|import.*VendorCategory" _clean/mvp/ --include="*.py"
grep -r "import.*BusinessService\|import.*VendorService" _clean/mvp/ --include="*.py"
grep -r "import.*VendorNormalization\|import.*PolicyEngine" _clean/mvp/ --include="*.py"
```

### **Import Update Checklist:**

Replace all instances of:
```python
from domains.core.models import Business, Transaction, AuditLog
→ from _clean.mvp.domains.core.models.business import Business
→ from _clean.mvp.domains.core.models.transaction import Transaction
→ from _clean.mvp.domains.core.models.audit_log import AuditLog

from domains.ap.models import COATemplate, VendorCategory
→ from _clean.mvp.domains.ap.models.coa_template import COATemplate
→ from _clean.mvp.domains.ap.models.vendor_category import VendorCategory

from domains.core.services import BusinessService
→ from _clean.mvp.domains.core.services.business import BusinessService

from domains.ap.services import VendorService
→ from _clean.mvp.domains.ap.services.vendor import VendorService

from _parked.vendor_normalization import VendorNormalizationService
→ from _clean.mvp.infra.vendor_normalization.services import VendorNormalizationService

from _parked.policy import PolicyEngineService
→ from _clean.mvp.domains.policy.services.policy_engine import PolicyEngineService
```

### **Update Process:**
1. Find all occurrences of each legacy import
2. Read context around each import
3. Determine what's being imported
4. Update to use new _clean/mvp path
5. Verify no broken imports

### **Verification:**
```bash
# Verify no legacy imports remain
grep -r "from domains\." _clean/mvp/ --include="*.py" && echo "❌ Found legacy imports" || echo "✓ No legacy imports"
grep -r "from _parked\." _clean/mvp/ --include="*.py" && echo "❌ Found parked imports" || echo "✓ No parked imports"

# Test imports work
python -c "from _clean.mvp.infra.templates.classification_service import TemplateClassificationService; print('✓ All imports working')"
```

### **Definition of Done:**
- [ ] All legacy imports replaced in `_clean/mvp/`
- [ ] All new imports use `_clean/mvp/` paths
- [ ] No broken imports anywhere
- [ ] Code can run without import errors

### **Git Commit:**
```bash
git add _clean/mvp/
git commit -m "feat: update all imports to use ported models and services"
```

---

## **E0.8: Verify Selective Porting Complete**

**Status:** `[ ]` Not started  
**Priority:** P0 Critical  
**Duration:** 1 day  
**Dependencies:** E0.1 through E0.7 complete

### **Problem Statement**
After all porting is complete, we need to verify nothing is broken and unnecessary files weren't imported.

### **Solution Overview**
Run comprehensive verification to ensure only template-system-needed components were ported, all imports work, and no unused code was included.

### **Verification Commands:**
```bash
# Verify ported files exist
ls -la _clean/mvp/domains/core/models/
ls -la _clean/mvp/domains/core/services/
ls -la _clean/mvp/domains/ap/models/
ls -la _clean/mvp/domains/ap/services/
ls -la _clean/mvp/infra/vendor_normalization/
ls -la _clean/mvp/domains/policy/

# Test all imports
python -c "
from _clean.mvp.domains.core.models.business import Business
from _clean.mvp.domains.core.models.transaction import Transaction
from _clean.mvp.domains.core.models.audit_log import AuditLog
from _clean.mvp.domains.core.services.business import BusinessService
from _clean.mvp.domains.ap.models.coa_template import COATemplate
from _clean.mvp.domains.ap.models.vendor_category import VendorCategory
from _clean.mvp.domains.ap.services.vendor import VendorService
from _clean.mvp.infra.vendor_normalization.services import VendorNormalizationService
from _clean.mvp.domains.policy.services.policy_engine import PolicyEngineService
from _clean.mvp.domains.policy.models.suggestion import Suggestion
from _clean.mvp.domains.policy.models.correction import Correction
print('✓ All imports successful')
"

# Verify no unnecessary files
find _clean/mvp/domains/ -type f -name "*.py" | wc -l
find _clean/mvp/infra/vendor_normalization/ -type f -name "*.py" | wc -l
find _clean/mvp/domains/policy/ -type f -name "*.py" | wc -l
```

### **Definition of Done:**
- [ ] All expected files exist in correct locations
- [ ] All imports work without errors
- [ ] Only template-system-needed components ported
- [ ] No unused or unnecessary files included
- [ ] Multi-tenant structure preserved across all models

### **Git Commit:**
```bash
git add .
git commit -m "docs: verify Phase 0 porting complete and working"
```

---

## **Success Criteria for Phase 0**

- [ ] All 8 core models and services ported to `_clean/mvp/`
- [ ] All imports updated to use `_clean/mvp/` paths
- [ ] Only template-system-specific components ported (selective, not wholesale)
- [ ] Multi-tenant structure preserved (business_id fields intact)
- [ ] All code imports without errors
- [ ] No legacy dependencies remaining in `_clean/mvp/`
- [ ] Ready for Phase 1 (Template System Implementation)
