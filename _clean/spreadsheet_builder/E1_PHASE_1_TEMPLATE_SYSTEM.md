// *** PHASE 1 GUARDRAIL: TEMPLATE RENDERING WITH UNIVERSAL ENGINE ***
// 
// This phase builds the template renderer using GL-classified data from Phase 0.
// 
// THE MISSION FIRST TEMPLATE PROVES STRUCTURE:
// - 13 months (C1:O1) with EOMONTH roll-forward
// - Row 2: Beginning cash + roll-forward from prior month
// - Rows 3-25: INFLOWS (recurring/major + total)
// - Rows 26-77: OUTFLOWS (vendors/one-time/payroll + total)
// - Formulas locked: we write VALUES ONLY, never touch formulas
// 
// HOW WE POPULATE (using universal GL classification from Phase 0):
// - Row 2: Sum of QBO bank accounts (any client type)
// - Rows 9-21: Major inflows (GL 4000-4999, amount > threshold, any client)
// - Rows 28-35: Recurring vendors (GL 6000-6999, recurring pattern, any client)
// - Rows 46-76: Payroll (GL 60100-60199, any client)
// 
// THE HARD PART IS NOT THE EXCEL:
// - The hard part is temporal bucketing (invoice date + DSO → month)
// - The hard part is recurrence detection (3+ with ±10% variance)
// - The hard part is storing per-client learning (overrides improve confidence)
// - The hard part is making it work for nonprofit/agency/SaaS/professional services
// 
// WHAT WE'RE NOT DOING:
// ❌ Hardcoding "if vendor_name == 'Mission First Operations'"
// ❌ Hardcoding "if this is a nonprofit"
// ❌ Building Mission First-specific logic
// 
// WHAT WE'RE DOING:
// ✅ Temporal bucketing (universal algorithm)
// ✅ Multi-sheet Excel generation (primary + hidden reference + summary)
// ✅ Formula preservation (write values, let Excel compute)
// ✅ Variant support (nonprofit vs agency vs SaaS templates)
// 
// BY END OF PHASE 1:
// - Template renders for ANY client type using GL classification
// - Mission First is one test case, not the target
// - System scales to CAS Firm #2, #3, etc. with zero code changes
// 
// *** Remember: Structure is universal (rows, formulas, layout) ***
// *** Values differ by client type (driven by GL classification) ***
// *** Learning improves per-client (stored overrides) ***
//

# RowCol MVP Phase 1 - Template System Implementation

**Status:** Ready for Execution  
**Phase:** Core Features (Weeks 3-6)  
**Goal:** Build Excel template generation system with GL classification  
**Dependencies:** Phase 0 complete  

---

## **CRITICAL: Context Files (MANDATORY)**

### **Architecture Context:**
- `_clean/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy
- `_clean/architecture/comprehensive_architecture.md` - Overall architecture

### **Product Context:**
- `_clean/mvp/mvp_comprehensive_prd.md` - MVP PRD

### **Phase 0 Reference:**
- `_clean/spreadsheet_builder/E0_PHASE_0_PORTING_AND_INTEGRATION.md` - Completed porting tasks

### **Current Phase Context:**
- **Goal:** Build template generation system using ported models/services
- **Architecture:** Runway → Domain Gateways → Infra Services
- **Leveraging:** BusinessService, VendorService, PolicyEngine, VendorNormalization
- **Testing:** Real QBO API, no mocking

---

## **E1.1: Enhance Existing QBO Client for Template System**

**Status:** `[ ]` Not started  
**Priority:** P0 Critical  
**Duration:** 2 days  
**Dependencies:** Phase 0 complete

### **Problem Statement**
Existing QBO client in `_clean/mvp/infra/rails/qbo/` needs enhancement to support template-specific operations: industry detection, COA template retrieval, vendor category fetching, and transaction classification by GL.

### **Solution Overview**
Extend existing QBOClient class with methods for:
- Business industry detection
- COA template retrieval by industry
- Vendor category fetching with GL mapping
- Transaction fetching with confidence scoring
- GL account classification

### **Discovery Commands:**
```bash
# Check existing QBO client
ls -la _clean/mvp/infra/rails/qbo/
grep -r "class QBO" _clean/mvp/infra/rails/qbo/ --include="*.py"

# Find existing methods
grep -r "def " _clean/mvp/infra/rails/qbo/client.py | head -20

# Check how it's currently used
grep -r "QBO.*Client\|from.*qbo.*client" _clean/mvp/ --include="*.py"
```

### **Enhancement Requirements:**
- [ ] Add method: `get_business_industry(business_id: str) -> str`
- [ ] Add method: `get_coa_template(industry: str) -> COATemplate`
- [ ] Add method: `get_vendor_categories() -> List[VendorCategory]`
- [ ] Add method: `get_transactions_with_confidence(business_id: str, days_back: int) -> List[Transaction]`
- [ ] Add method: `classify_transactions_by_gl(...) -> Dict[str, List[Transaction]]`

### **Implementation Points:**
1. Import ported models (Business, Transaction, COATemplate, VendorCategory)
2. Use BusinessService to get industry
3. Query COATemplate by industry from database
4. Query VendorCategory from database
5. Fetch transactions from QBO with existing client
6. Classify using COA templates

### **Verification:**
```bash
python -c "
from _clean.mvp.infra.rails.qbo.client import QBOClient

client = QBOClient(business_id='test123')
# Verify new methods exist
assert hasattr(client, 'get_business_industry')
assert hasattr(client, 'get_coa_template')
assert hasattr(client, 'get_vendor_categories')
assert hasattr(client, 'get_transactions_with_confidence')
assert hasattr(client, 'classify_transactions_by_gl')
print('✓ All template methods available')
"
```

### **Definition of Done:**
- [ ] QBO client extended with 5 new template-specific methods
- [ ] All methods use ported models (Business, Transaction, COATemplate, VendorCategory)
- [ ] Methods can be imported without errors
- [ ] Documentation added for each new method

### **Git Commit:**
```bash
git add _clean/mvp/infra/rails/qbo/
git commit -m "feat: enhance QBO client with template-specific methods"
```

---

## **E1.2: Create Transaction Classification Service**

**Status:** `[ ]` Not started  
**Priority:** P0 Critical  
**Duration:** 3 days  
**Dependencies:** E1.1 complete, Phase 0 complete

### **Problem Statement**
Template system needs a service to classify transactions using:
1. Policy engine for rule-based categorization
2. Vendor normalization for vendor → GL mapping
3. COA templates for industry-specific GL structures
4. Confidence scoring from existing transaction models

### **Solution Overview**
Create `_clean/mvp/infra/templates/classification_service.py` that:
- Takes classified transactions from domain gateways
- Applies policy engine for categorization
- Applies vendor normalization for GL mapping
- Groups by cash flow categories (inflows, outflows, payroll, etc.)
- Returns classified data with confidence scores

### **Discovery Commands:**
```bash
# Check if classification service exists
ls -la _clean/mvp/infra/templates/
grep -r "classification" _clean/mvp/ --include="*.py"

# Check domain gateways for reference
ls -la _clean/mvp/domains/ap/
ls -la _clean/mvp/domains/ar/
ls -la _clean/mvp/domains/bank/
```

### **Service Architecture:**
```
Input: advisor_id, business_id, domain gateways, console service
        ↓
Get Business (industry) via BusinessService
        ↓
Get COA Template for industry
        ↓
Get Vendor Categories
        ↓
For each transaction:
  - Apply PolicyEngine for categorization (if policy exists)
  - Apply VendorNormalization for GL mapping (fallback)
  - Use default GL account (final fallback)
  ↓
Group by cash flow categories
        ↓
Return: classified transactions with GL accounts and confidence scores
```

### **Classification Logic:**
1. **Policy Engine Priority (if available):**
   - Use PolicyEngineService to categorize
   - Get top suggestion with confidence
   - Use suggested GL account

2. **Vendor Normalization Fallback:**
   - Use VendorNormalizationService to normalize vendor name
   - Get vendor's canonical GL account
   - Use normalized vendor category

3. **Default Fallback:**
   - Use COA template type-based GL mapping
   - Default to "6000-6999" (general expense)
   - Low confidence score (0.3)

### **Verification:**
```bash
python -c "
from _clean.mvp.infra.templates.classification_service import TemplateClassificationService

# Create service
service = TemplateClassificationService(
    advisor_id='test',
    business_id='test',
    bills_gateway=None,  # Mocked for now
    invoices_gateway=None,
    balances_gateway=None,
    console_service=None,
    business_service=None,
    vendor_normalization_service=None,
    policy_engine=None
)

# Verify main methods exist
assert hasattr(service, 'classify_transactions_for_template')
assert hasattr(service, '_map_transaction_to_gl')
assert hasattr(service, '_get_vendor_category')
print('✓ Classification service working')
"
```

### **Definition of Done:**
- [ ] `TemplateClassificationService` created in `_clean/mvp/infra/templates/`
- [ ] Implements transaction classification using policy engine + vendor normalization
- [ ] Groups transactions by cash flow categories
- [ ] Returns data structure with GL accounts and confidence scores
- [ ] Service can be imported without errors
- [ ] Uses ported models and services (PolicyEngine, VendorNormalization, BusinessService)

### **Git Commit:**
```bash
git add _clean/mvp/infra/templates/
git commit -m "feat: create transaction classification service with policy engine and vendor normalization"
```

---

## **E1.3: Create Excel Template Renderer (Config-Driven, Flexible Rows)**

**Status:** `[ ]` Not started  
**Priority:** P0 Critical  
**Duration:** 4 days  
**Dependencies:** E1.1, E1.2 complete

### **Problem Statement**

Template renderer must:
1. **NOT hardcode row numbers** (row 2=Beginning, row 9=Inflows, etc.)
2. Load archetype config that defines section structure, category order, and row allocations
3. Use **rolling window algorithm** to place classified data within allocated rows
4. Preserve **all Excel formulas** (never write formulas, only values)
5. Support multiple archetypes (Nonprofit, Agency, Product/Inventory) with **zero code changes**
6. Generate multi-sheet workbook (primary + hidden reference for summary linkage)

### **Solution Overview**

Instead of:
```python
# ❌ WRONG: Hardcoded rows
ws['C9'] = recurring_inflow    # Always row 9
ws['C28'] = recurring_vendors  # Always row 28
```

We do:
```python
# ✅ RIGHT: Config-driven rolling windows
config = load_archetype_config("nonprofit")
section = config['sections']['inflows']
current_row = section['start_row']  # From config (e.g., 3)

for category in section['categories']:
    rows_allocated = category['row_budget']  # From config (e.g., 3)
    data = classify_qbo_data(qbo, category['filter'])
    
    # Write label
    ws.cell(current_row, col_A).value = category['label']
    current_row += 1
    
    # Write detail lines (up to rows_allocated)
    for detail in data[:rows_allocated]:
        write_month_values(ws, current_row, detail)
        current_row += 1
    
    # Pad remaining rows with blanks (preserves visual structure)
    for _ in range(rows_allocated - len(data)):
        current_row += 1
```

This makes the template **archetype-agnostic**: change config, not code.

### **Archetype Config Format**

Load from YAML (example `nonprofit_archetype.yaml`):

```yaml
archetype: "nonprofit"
cadence: "monthly"
horizon: 13
beginning_cash_row: 2

sections:
  inflows:
    order: 1
    label: "INFLOWS"
    start_row: 3
    color_scheme: "warm"
    categories:
      - name: "Recurring"
        label: "Bank Account Trends (recurring gifts, donations, average)"
        color_hex: "#FF9900"
        row_budget: 3
        
      - name: "Major"
        label: "Based on Pledges or Accounts Receivable (Named gifts, Awarded, Pledged)"
        color_hex: "#FF00FF"
        row_budget: 13
    
    guard_row: 24
    total_row: 25
    total_formula: "=SUM(C{start}:C{end})"

  outflows:
    order: 2
    label: "OUTFLOWS"
    start_row: 26
    color_scheme: "cool"
    categories:
      - name: "Recurring"
        label: "Recurring Payments / Subscriptions"
        color_hex: "#F6B26B"
        row_budget: 8
      
      - name: "OneTime"
        label: "One-Time Payments"
        color_hex: "#EA9999"
        row_budget: 3
      
      - name: "Payroll"
        label: "Payroll and Related Costs"
        color_hex: "#6D9EEB"
        row_budget: 31
    
    guard_row: 76
    total_row: 77
    total_formula: "=SUM(C{start}:C{end})"

cash_metrics:
  - key: "change_in_cash"
    row: 78
    formula: "=C25-C77"
  
  - key: "ending_cash"
    row: 79
    formula: "=C2+C78"
  
  - key: "buffer"
    row: 81
    formula: "=SUM(D46:E76)"
  
  - key: "net_remaining"
    row: 82
    formula: "=C79-C81"
```

### **Rolling Window Algorithm**

```python
def render_template_from_config(config: dict, classified_data: dict, month_columns: list) -> Workbook:
    """
    Core renderer: takes archetype config + classified data, outputs Excel.
    
    Key principle: Config defines STRUCTURE (what goes where), code fills VALUES.
    Same code works for nonprofit/agency/saas - just different configs.
    """
    
    wb = Workbook()
    ws = wb.active
    ws.title = config.get('sheet_name', 'Cash Flow')
    
    # === STEP 1: Month headers (formulas, never change) ===
    start_date = config['beginning_cash_row']  # e.g., "2025-08-01"
    for i, month_col in enumerate(month_columns):
        if i == 0:
            ws.cell(row=1, column=col_map[month_col]).value = start_date
        else:
            prev_col = month_columns[i-1]
            ws.cell(row=1, column=col_map[month_col]).value = f"=EOMONTH({prev_col}1,1)"
    
    # === STEP 2: Beginning cash (seed formula, never change) ===
    bc_row = config['beginning_cash_row']
    ws.cell(row=bc_row, column=1).value = "Beginning Cash"
    for i, month_col in enumerate(month_columns):
        if i == 0:
            # First month: seed from config (e.g., =SUM(bank_accounts))
            ws.cell(row=bc_row, column=col_map[month_col]).value = config['beginning_cash_seed_formula']
        else:
            # Other months: link to prior month ending cash
            prev_col = month_columns[i-1]
            ws.cell(row=bc_row, column=col_map[month_col]).value = f"={prev_col}{ending_cash_row}"
    
    # === STEP 3: Render each section in order ===
    for section in config['sections']:
        section_start = section['start_row']
        current_row = section_start
        
        # Write section header
        ws.cell(row=current_row, column=1).value = section['label']
        ws.cell(row=current_row, column=1).fill = PatternFill(
            start_color=section.get('header_color', '#CCCCCC'),
            fill_type='solid'
        )
        current_row += 1
        
        # === STEP 4: Render each category within section ===
        for category in section['categories']:
            # Get data for this category
            category_data = classified_data.get(f"{section['key']}:{category['name']}", [])
            rows_allocated = category['row_budget']
            
            # Write category label (color-coded)
            ws.cell(row=current_row, column=1).value = category['label']
            ws.cell(row=current_row, column=1).fill = PatternFill(
                start_color=category['color_hex'],
                fill_type='solid'
            )
            current_row += 1
            
            # === STEP 5: Rolling window - write detail lines ===
            rows_used = 0
            for detail in category_data:
                if rows_used >= rows_allocated:
                    break  # Cap at allocated rows
                
                # Write detail line for each month
                for month_col in month_columns:
                    value = detail.get(month_col, 0)
                    ws.cell(row=current_row, column=col_map[month_col]).value = value
                
                current_row += 1
                rows_used += 1
            
            # === STEP 6: Pad remaining rows (preserve visual structure) ===
            for _ in range(rows_allocated - rows_used):
                current_row += 1
        
        # === STEP 7: Guard row + Total (formulas, never change) ===
        guard_row = section['guard_row']
        ws.cell(row=guard_row, column=1).value = "Insert above this line"
        
        total_row = section['total_row']
        ws.cell(row=total_row, column=1).value = f"TOTAL {section['label'].upper()}"
        ws.cell(row=total_row, column=1).fill = PatternFill(
            start_color=section.get('total_color', '#D9EAD3'),
            fill_type='solid'
        )
        
        # Write total formulas (never write values)
        for month_col in month_columns:
            start = section['start_row']
            end = guard_row - 1
            ws.cell(row=total_row, column=col_map[month_col]).value = f"=SUM({month_col}{start}:{month_col}{end})"
    
    # === STEP 8: Cash metrics (formulas, never change) ===
    for metric in config['cash_metrics']:
        row = metric['row']
        col = 1
        ws.cell(row=row, column=col).value = metric['label']
        
        for month_col in month_columns:
            # Formula with month column substitution
            formula = metric['formula'].replace("{month}", month_col)
            ws.cell(row=row, column=col_map[month_col]).value = formula
    
    # === STEP 9: Multi-sheet generation ===
    # Copy to hidden variant sheet (for Summary By Vendor linkage)
    ws_hidden = wb.copy_worksheet(ws)
    ws_hidden.title = "RA Edits-Cash Flow-Ops"  # Hidden reference for Summary
    ws_hidden.sheet_state = 'hidden'
    
    wb.save(output_path)
    return output_path
```

### **Why This Architecture**

✅ **Scales without code changes**: Nonprofit uses `nonprofit.yaml`, Agency uses `agency.yaml`, same renderer  
✅ **Flexible row allocation**: Each archetype controls its own row budgets  
✅ **Handles data quality**: If you have 5 recurring gifts but only 3 rows allocated, show top 3 by amount  
✅ **Preserves structure**: Pad with blanks so layout is always readable  
✅ **Formulas locked**: Guard rows prevent accidental insertions, totals are formulas never values  
✅ **Future-proof**: Add new archetype (Product/Inventory) with just a new YAML, zero code changes  

### **Testing/Verification**

```python
# Test 1: Load nonprofit config and render
nonprofit_config = load_yaml("_clean/config/archetypes/nonprofit.yaml")
output = render_template_from_config(
    nonprofit_config,
    classified_data={
        "inflows:recurring": [
            {"2025-08": 5000, "2025-09": 5000},
            {"2025-08": 3000, "2025-09": 3000}
        ],
        "inflows:major": [
            {"2025-08": 50000, "2025-09": 0},
            {"2025-08": 25000, "2025-09": 0}
        ],
        "outflows:recurring": [...],
        "outflows:payroll": [...]
    },
    month_columns=['C', 'D', 'E']
)

# Verify structure
wb = load_workbook(output)
ws = wb.active

# Check formulas are preserved (never values)
assert ws['C25'].value.startswith('=SUM'), "Total should be formula"
assert ws['C79'].value.startswith('='), "Ending cash should be formula"

# Check rolling window worked
assert ws['C5'].value == 5000, "First recurring inflow"
assert ws['C6'].value == 3000, "Second recurring inflow"
assert ws['C7'].value is None, "Row 7 padded (blank)"  # 3rd row in budget

# Test 2: Load agency config, same code
agency_config = load_yaml("_clean/config/archetypes/agency.yaml")
output2 = render_template_from_config(agency_config, classified_data, month_columns)
# Different layout, same formula preservation, same logic
```

### **Definition of Done**

- [ ] `ArchetypeTemplateRenderer` class created in `_clean/mvp/infra/templates/`
- [ ] Loads archetype configs from YAML (nonprofit, agency, product templates)
- [ ] Implements rolling window algorithm for row allocation
- [ ] Generates workbook with **formulas never written, only values**
- [ ] Creates multi-sheet workbook (primary + hidden variant for Summary linkage)
- [ ] Preserves guard rows ("Insert above this line")
- [ ] Applies color coding per config
- [ ] Handles variable numbers of detail lines (pads or prioritizes)
- [ ] Works for nonprofit, agency, and product/inventory archetypes
- [ ] No hardcoded row numbers in code (all from config)
- [ ] Can be imported without errors
- [ ] Renderer is **archetype-agnostic** (same code, different configs)

### **Git Commit**

```bash
git add _clean/mvp/infra/templates/
git add _clean/config/archetypes/*.yaml
git commit -m "feat: config-driven template renderer with rolling-window row allocation

- Loads archetype configs (nonprofit, agency, product) from YAML
- Implements rolling window algorithm for flexible row placement
- Preserves formulas (never writes values to formula cells)
- Generates multi-sheet workbooks with hidden reference variant
- Same code works for all archetypes (config changes, not code)"
```

---

## **E1.4: Create API Endpoints for Template Generation**

**Status:** `[ ]` Not started  
**Priority:** P1 High  
**Duration:** 2 days  
**Dependencies:** E1.3 complete

### **Problem Statement**
Existing API in `_clean/mvp/api/routes.py` needs new endpoints to:
1. Generate workbooks for specific businesses
2. Check data quality metrics
3. Retrieve COA templates
4. Retrieve vendor categories

### **Solution Overview**
Add 4 new endpoints to existing FastAPI application:
- `POST /templates/generate-workbook/{business_id}` - Generate and return Excel file
- `GET /businesses/{business_id}/data-quality` - Get data quality metrics
- `GET /businesses/{business_id}/coa-template` - Get COA template info
- `GET /businesses/{business_id}/vendor-categories` - Get vendor categories

### **Discovery Commands:**
```bash
# Check existing API structure
grep -r "class.*Router\|@router\|@app" _clean/mvp/api/ --include="*.py"

# Check how FastAPI is set up
grep -r "FastAPI\|APIRouter" _clean/mvp/api/ --include="*.py"

# Check existing endpoints
grep -r "@.*get\|@.*post" _clean/mvp/api/ --include="*.py" | head -10
```

### **Endpoint Specifications:**

**E1.4.1: Generate Workbook**
```
POST /templates/generate-workbook/{business_id}
Request: { }
Response: 
{
  "success": true,
  "business_id": "test123",
  "output_path": "output/test123_cash_flow.xlsx",
  "business_name": "Acme Corp",
  "industry": "services"
}
```

**E1.4.2: Data Quality Metrics**
```
GET /businesses/{business_id}/data-quality
Response:
{
  "total_transactions": 150,
  "matched_transactions": 145,
  "unmatched_transactions": 5,
  "high_confidence_transactions": 140,
  "data_quality_score": 0.93,
  "last_sync": "2025-10-17T10:30:00Z",
  "sync_status": "success"
}
```

**E1.4.3: COA Template Info**
```
GET /businesses/{business_id}/coa-template
Response:
{
  "business_id": "test123",
  "business_name": "Acme Corp",
  "industry": "services",
  "coa_template": {
    "id": "template_001",
    "template_name": "Service Industry COA",
    "industry": "services",
    "is_active": true
  }
}
```

**E1.4.4: Vendor Categories**
```
GET /businesses/{business_id}/vendor-categories
Response:
{
  "business_id": "test123",
  "vendor_categories": [
    {
      "id": "cat_001",
      "name": "Rent & Utilities",
      "gl_account": "6100-6199",
      "description": "Office rent and utilities",
      "is_active": true
    },
    ...
  ],
  "total_categories": 12
}
```

### **Implementation Notes:**
1. All endpoints use existing domain gateways
2. Use BusinessService for business validation
3. Query Transaction, COATemplate, VendorCategory models
4. Return consistent JSON responses
5. Include proper error handling

### **Verification:**
```bash
# Start the app
uvicorn _clean.mvp.api.routes:app --reload &

# Test endpoints
curl -X GET http://localhost:8000/businesses/test123/data-quality
curl -X GET http://localhost:8000/businesses/test123/coa-template
curl -X GET http://localhost:8000/businesses/test123/vendor-categories
curl -X POST http://localhost:8000/templates/generate-workbook/test123
```

### **Definition of Done:**
- [ ] All 4 endpoints added to `_clean/mvp/api/routes.py`
- [ ] Each endpoint uses ported models and services
- [ ] Proper error handling and validation
- [ ] Consistent JSON response format
- [ ] Endpoints work without errors
- [ ] API documentation updated

### **Git Commit:**
```bash
git add _clean/mvp/api/
git commit -m "feat: add template system API endpoints (generate, data quality, COA, vendor categories)"
```

---

## **E1.5: Multi-Client Pilot Validation**

**Status:** `[ ]` Not started  
**Priority:** P1 High  
**Duration:** 3 days  
**Dependencies:** E1.4 complete

### **Problem Statement**
Template system needs validation across multiple client types to ensure:
1. Template adaptability across different industries
2. Data quality metrics consistent across segments
3. GL classification working for diverse business types
4. Vendor normalization effective for different vendor naming patterns

### **Solution Overview**
Test template system with at least 3 different client types:
- Service industry (consulting, agencies, etc.)
- Nonprofit organization
- SaaS/Software company

Validate:
- Template generation completes without errors
- Data quality score > 80%
- GL accounts properly mapped
- Vendor categories effective

### **Pilot Validation Checklist:**

For each client type:
- [ ] Create test business record
- [ ] Create COA template for industry
- [ ] Create vendor categories
- [ ] Set up vendor normalization rules
- [ ] Generate template
- [ ] Verify output file
- [ ] Check data quality metrics
- [ ] Document findings

### **Metrics to Track:**
- Template generation time
- Data quality score by client type
- Vendor normalization accuracy
- GL classification accuracy
- File generation success rate

### **Definition of Done:**
- [ ] Templates generated successfully for 3+ client types
- [ ] Data quality score > 80% for each client
- [ ] GL classification validated for each industry
- [ ] Vendor normalization working effectively
- [ ] Pilot findings documented
- [ ] Ready for Phase 2 (Advanced Features)

### **Git Commit:**
```bash
git add .
git commit -m "docs: complete Phase 1 pilot validation across multiple client types"
```

---

## **Success Criteria for Phase 1**

- [ ] QBO client enhanced with template-specific methods
- [ ] Transaction classification service working with policy engine + vendor normalization
- [ ] Excel template renderer generating workbooks with COA integration
- [ ] 4 API endpoints operational and tested
- [ ] Multi-client pilots successful (3+ client types)
- [ ] Data quality metrics > 80% across segments
- [ ] Template system ready for advanced features
- [ ] All code imported without errors
- [ ] Ready for Phase 2 (Advanced Features)

---

## **Phase 1 Architecture**

```
FastAPI Routes (E1.4)
    ↓
TemplateClassificationService (E1.2)
    ↓
ConsoleService + Domain Gateways + PolicyEngine + VendorNormalization
    ↓
Enhanced QBO Client (E1.1)
    ↓
TemplateRenderer (E1.3)
    ↓
Excel Workbook Output
```

**Data Flow:**
1. API receives request for workbook generation
2. Classification service fetches and classifies transactions
3. Template renderer creates Excel with COA structure
4. Policy engine and vendor normalization applied during classification
5. Workbook returned to user

**Models Used:**
- Business (industry detection)
- Transaction (confidence scoring)
- COATemplate (GL structure)
- VendorCategory (GL mapping)
- AuditLog (compliance)
- PolicyEngine (categorization)
- VendorNormalization (GL mapping)
