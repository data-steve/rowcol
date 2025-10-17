// *** CRITICAL: MISSION FIRST IS PROOF OF CONCEPT, NOT THE PRODUCT ***
// *** READ THIS BEFORE TOUCHING ANY PRODUCT SPEC BELOW ***
//////////////////////////////////////////////////////////////////////////////////
// 
// WHAT WE'RE NOT DOING:
// ============================================================================
// ❌ Building Excel generation software for Mission First nonprofit
// ❌ Hardcoding vendor names, row numbers, or client-specific logic
// ❌ Creating bespoke code that only works for one CAS firm
// 
// WHAT WE'RE ACTUALLY BUILDING:
// ============================================================================
// ✅ UNIVERSAL GL-BASED CLASSIFICATION ENGINE
//    - Works for ANY client type (nonprofit, agency, SaaS, professional services)
//    - Works for ANY CAS firm (whether they serve 1 client or 500)
//    - Uses QBO's standardized GL structure (not vendor names)
//    - Learns recurrence patterns (3+ occurrences, ±10% stability)
//    - Detects magnitude (threshold-based major vs recurring)
//    - Stores client-specific overrides (improves over time)
// 
// WHY THIS MATTERS:
// ============================================================================
// Mission First provided their cash forecast template. Beautiful template.
// BUT: If we hardcode their structure, we fail at firm #2.
// 
// The HARD PROBLEM is not the Excel. It's building detection logic that:
//   - Works for a nonprofit with grants + subscriptions
//   - Works for an agency with project billing + retainer
//   - Works for SaaS with subscription revenue + variable churn
//   - All WITHOUT hardcoding vendor names or client-specific rules
// 
// The SOLUTION: Use QBO's universal GL ranges + pattern learning
//   - 4000-4999 = Revenue (ANY client type)
//   - 6000-6999 = Expenses (ANY client type)
//   - 60100-60199 = Payroll (ANY client type)
//   - Apply recurrence + magnitude detection
//   - Store what we learn per-client
// 
// Mission First template shows us WHAT OUTPUT LOOKS LIKE.
// GL-based classification shows us HOW TO GET THERE FROM ANY QBO.
// 
// THE ACTUAL DATA FLOW:
// ============================================================================
// 
// Step 1: FETCH FROM QBO (bank, invoices, bills, payroll)
// 
// Step 2: GL-CLASSIFY (organize by universal GL ranges)
//         → "This is GL 4150, so inflow"
//         → "This is GL 6250, so expense"
//         → "This is GL 60100, so payroll"
// 
// Step 3: DETECT PATTERNS (learn from 90-day history)
//         → "GL 6250 appears 3x monthly with ±$50: RECURRING"
//         → "GL 4000 appears 1x: MAJOR/VARIABLE"
//         → Store this learning per-client
// 
// Step 4: TEMPORAL BUCKET (which month does each appear?)
//         → Invoice date + historical DSO → expected inflow month
//         → Bill due date + payment policy → expected outflow month
//         → Payroll schedule → payment dates
// 
// Step 5: POPULATE TEMPLATE (write classified values to rows)
//         → Row 2: Beginning cash (sum of bank accounts)
//         → Rows 9-21: Major inflows (GL 4000-4999, amount>threshold)
//         → Rows 28-35: Recurring vendors (GL 6000-6999, recurring pattern)
//         → Rows 46-76: Payroll breakdown (GL 60100-60199)
//         → Keep all formulas intact (totals, roll-forward, buffer)
// 
// Step 6: EXCEL OUTPUT (multi-sheet, formulas intact, board-ready)
// 
// THIS SCALES:
// ============================================================================
// - Same GL classification works for nonprofit, agency, SaaS
// - Same template structure works (rows are universal)
// - Same learning applies (per-client overrides)
// - Different client types = different GL transactions, same engine
// 
// IF YOU SEE HARDCODING:
// ============================================================================
// 
// 🚨 RED FLAG: "if vendor_name == 'Mission First Operations'"
// 🚨 RED FLAG: "if client_type == 'nonprofit'"
// 🚨 RED FLAG: "hardcode row 29 for this firm"
// 🚨 RED FLAG: "this only works for Mission First"
// 
// ✅ CORRECT: "if GL range is 4000-4999"
// ✅ CORRECT: "if 3+ occurrences with ±10% variance"
// ✅ CORRECT: "apply this to ANY client with QBO"
// ✅ CORRECT: "Mission First is one implementation of this"
// 
// MISSION FIRST TEMPLATE STRUCTURE (from forensic analysis):
// ============================================================================
// 
// Primary Sheet: " RA Edits-Cash Flow-Ops with Sa"
//   - 13 months (C1:O1 with EOMONTH roll-forward)
//   - Row 2: Beginning Cash (seed + roll from prior month)
//   - Rows 3-25: INFLOWS (recurring 4-7, major gifts 8-21, total 25)
//   - Rows 26-77: OUTFLOWS (recurring vendors 27-35, one-time 39, 
//                            known unaccounted 42, payroll 44-76, total 77)
//   - Row 78: Change in cash
//   - Row 79: Ending cash
//   - Row 81: 2-month buffer
//   - Row 82: Net remaining
// 
// Our ENGINE (GL-based classification) feeds VALUES into this structure.
// The VALUES are different for each client type.
// The STRUCTURE is the same for all.
// 
// *** Keep this principle in mind as you read the product spec below ***
//
# RowCol MVP Product Specification
## Cash Flow Forecasting Automation for CAS Firms

**Version:** 2.0  
**Date:** October 13, 2025  
**Status:** Ready for Development  
**Updated:** Corrected understanding of core technical challenges

---

## 🎯 Executive Summary

RowCol MVP is an "embarrassingly humble" cash flow forecasting automation tool designed for the broader Client Accounting Services (CAS) market. While the deliverable is an Excel spreadsheet, the real value lies in solving the **hard technical problem** of resilient data ingestion and intelligent transaction classification across diverse CAS firm data variations.

**Core Value Proposition:** Transform 2-4 hours of manual spreadsheet work per client per month into a push-button automation that generates board-ready cash flow forecasts, while building the data intelligence foundation for a scalable CAS platform that serves both traditional CAS 1.0 firms and emerging CAS 2.0 advisory practices.

**The Real Challenge:** The spreadsheet generation is straightforward. The hard part is building a **resilient data ingestion and classification system** that can handle the diversity of CAS firm data (different GL structures, business types, data quality levels) and learn from historical patterns to create accurate cash flow projections across multiple market segments.

**Market Opportunity:** RowCol addresses a broader CAS opportunity beyond any single firm or client type. We're ahead of the adoption curve - most CAS firms haven't seen this level of automation because no one has shown it to them yet. The market spans from traditional monthly-forecast firms to high-velocity weekly cash management practices.

---

## 🧭 Market Positioning

### Dual-Mode Strategy: Bridging CAS 1.0 and CAS 2.0

RowCol serves two distinct but related markets through a unified platform:

| Mode | Target | Cadence | Value | Deliverable |
|------|--------|---------|-------|-------------|
| **Planner Mode** | CAS 1.0 Firms (Traditional CAS) | Monthly | Automate manual forecasting | Excel/PDF forecast from QBO |
| **Control Plane Mode** | CAS 2.0 Firms (Advisory-Focused) | Weekly/Continuous | Proactive cash management | Interactive dashboards, alerts |

**Core Insight:** RowCol bridges traditional CAS (automation of existing workflows) and modern advisory services (infrastructure for new client relationships). This dual-mode approach addresses the full spectrum of CAS needs, from basic automation to proactive client management.

### Market Segmentation by Data Velocity and Business Model

| Segment | Data Velocity | Cadence | Mode Fit | Business Model | Market Size |
|---------|---------------|---------|----------|----------------|-------------|
| **Nonprofits** | Low | Monthly | Planner | Stable, donor-based | Large, underserved |
| **Agencies/Service** | High | Weekly | Control Plane | Project-based billing | Growing, high-value |
| **Construction/Property** | Medium | Biweekly | Both | Progress billing | Steady, complex |
| **E-commerce/SaaS** | Very High | Daily | Control Plane | Subscription-based | Fastest growing |
| **Professional Services** | Medium | Biweekly | Both | Retainer + projects | Established, premium |

### Market Opportunity: Ahead of the Adoption Curve

**Key Insight:** Most CAS firms haven't seen this level of automation because no one has shown it to them yet. RowCol is positioned ahead of the adoption curve with:

- **CAS 1.0 Firms:** Seeking automation to make existing business more profitable
- **CAS 2.0 Firms:** Needing infrastructure to enable new advisory relationships
- **Mixed-Practice Firms:** Requiring flexible solutions that adapt to diverse client needs

The market spans from traditional monthly-forecast firms to high-velocity weekly cash management practices, creating a scalable opportunity across the entire CAS spectrum.

---

## 💰 Pricing Strategy

### Cadence-Based Pricing Model: Scaling with Client Value

RowCol's pricing scales with the value delivered through refresh frequency and data complexity:

| Tier | Cadence | Price/Client/Month | Target Segment | Value Proposition |
|------|---------|-------------------|----------------|-------------------|
| **Planner** | Monthly | $50-100 | Nonprofits, stable firms | Automate board packet generation |
| **Pro** | Biweekly | $100-150 | Moderately active firms | Semi-active oversight and control |
| **Control Plane** | Weekly/Always-on | $200-400 | High-velocity firms | Active cash management and alerts |

### Strategic Pricing Framework

**Base License (Engine Access):** $50/mo/client for monthly refresh
**Cadence Multiplier:** +50% for biweekly, +100% for weekly
**Template Packs:** Optional verticalized templates for specific industries
**Advisory Tier:** $299-499/mo/client for Control Plane dashboards and alerts

### Value Justification Across Market Segments

**For CAS 1.0 Firms (Planner Mode):**
- CAS firms charge $2K-3K/month/client for advisory services
- RowCol automates 2-4 hours/month of manual work per client
- 15-30x ROI for firms using the tool
- Enables higher client capacity without additional staff

**For CAS 2.0 Firms (Control Plane Mode):**
- Enables premium advisory services at $3K-5K/month/client
- Transforms reactive reporting into proactive cash management
- Creates differentiated service offerings
- Builds client stickiness through continuous value delivery

**Pilot Strategy:** $0 for first month across all segments to validate adoption and demonstrate value

---

## ⚙️ Technical Architecture

### Built on Multi-Tenant Foundation

RowCol MVP leverages an existing multi-tenant architecture designed for CAS firms managing multiple clients:

**Existing Architecture Components:**
- **Multi-Tenant Database**: Firm-first hierarchy with `firm_id` → `client_id` (business_id)
- **Domain-Driven Design**: Clean separation between domains (AP, AR, Bank) and runway orchestration
- **Smart Sync Pattern**: Local mirroring with live data synchronization
- **QBO Integration**: Robust OAuth2 flow with token refresh and throttling
- **Repository Pattern**: Clean data access layer with business_id filtering

### Core Components

1. **Data Ingestion Engine** (The Hard Part)
   - QBO API integration with robust error handling and throttling
   - GL-based transaction classification (not vendor-specific)
   - Historical pattern learning from 90-day transaction history
   - Data quality scoring and adaptation
   - Learning system that improves over time

2. **Classification Intelligence** (The Real Value)
   - GL range mapping (4000-4999 for Revenue, 6000-6999 for Expenses)
   - Recurrence detection (3+ occurrences, stable amounts ±10%)
   - Amount threshold classification (major vs recurring)
   - Client-specific learning and overrides
   - "Pending" bucket for unmapped items

3. **Template Renderer** (The Deliverable)
   - Excel generation with preserved formulas
   - YAML-based template configuration
   - Color coding and formatting
   - Multi-format output (Excel, PDF, Web)

4. **Template Library** (Configurable)
   - Pre-built templates (Nonprofit, Agency, SaaS)
   - Client-specific customizations
   - Version control and updates

5. **Firm Console** (Management)
   - Multi-client management with firm-level dashboard
   - Client onboarding and QBO connection
   - Template selection and configuration
   - Refresh scheduling and monitoring
   - Data quality dashboards

### Data Flow Architecture

```
QBO Data → GL Classification → Pattern Learning → Template Population → Excel Output
    ↓              ↓                ↓                    ↓
Bank Balances  GL Ranges      Recurrence Detection   Formula Preservation
Invoices       Thresholds     Client Overrides       Color Coding
Bills          Payroll GLs    Manual Inputs          Multi-tab Structure
    ↓              ↓                ↓                    ↓
Raw QBO Data  Smart Mapping    Learning System      Professional Output
```

### The Real Technical Challenge: Universal Data Intelligence

**Problem:** CAS firms serve diverse clients with varying data structures:
- Different GL account setups (non-profit vs for-profit vs industry-specific)
- Varying data quality levels (some use Keeper/ClientHub, others don't)
- Different business types (agencies, e-commerce, SaaS, nonprofits, professional services)
- Inconsistent vendor naming and categorization across clients
- Mixed practice firms serving multiple client types

**Solution:** GL-based learning system that scales across all CAS segments:
- Uses QBO's standardized GL structure (not hardcoded vendor names)
- Learns from historical transaction patterns across diverse client types
- Adapts to data quality levels automatically
- Provides manual override capabilities for edge cases
- Improves over time with usage across multiple clients
- Enables rapid onboarding of new client types through pattern recognition

**Key Innovation:** The system learns from QBO's universal GL structure rather than relying on hardcoded vendor mappings, making it applicable to any CAS firm serving any client type.

---

## 📊 Universal Workbook Structure

### Cash Flow Waterfall Layout

```
BEGINNING CASH (Row 2)
├── INFLOWS
│   ├── Recurring (e.g., subscriptions, donations)
│   └── Major/Variable (e.g., grants, client payments)
├── OUTFLOWS
│   ├── Recurring Vendors (e.g., rent, utilities)
│   ├── One-time AP (e.g., equipment purchases)
│   └── Payroll (wages, taxes, benefits)
└── ENDING CASH (formula-driven roll-forward)
```

### Required Tabs

1. **Main Cash Flow Sheet**
   - Time-based columns (months/weeks)
   - Waterfall rows with roll-forward formulas
   - Color-coded sections for visual clarity

2. **Details by Vendor/GL**
   - Vendor-to-GL mappings driving outflows
   - Frequency and amount tracking
   - Historical pattern analysis

3. **Summary by Vendor/Class**
   - Presentation-ready rollups
   - Client-facing summaries
   - Advisory insights

4. **Payroll Support**
   - Wage and tax breakdowns
   - Department/class allocations
   - Pay cycle management

5. **Pivot Tables/Totals**
   - Analytical layer
   - Variance analysis
   - Trend identification

---

## 🔧 GL-Based Classification System

### The Core Innovation: Learning from QBO Data Structure

**Why GL-Based Learning Works:**
- QBO uses standardized GL account structures across all clients
- GL codes (4000-4999 for Revenue, 6000-6999 for Expenses) are universal
- Historical transaction patterns reveal recurring behavior
- Amount thresholds help distinguish major vs recurring items
- No need to hardcode vendor names or client-specific rules

### Configuration Schema

```json
{
  "inflows": {
    "gl_range": ["4000-4999"],
    "threshold_major": 1000,
    "recurring_pattern": "monthly"
  },
  "outflows": {
    "gl_range": ["6000-6999"],
    "threshold_one_time": 500,
    "recurring_pattern": "monthly"
  },
  "payroll": {
    "gl_range": ["60100-60199"],
    "source": "Payroll.Gusto"
  }
}
```

### Learning Algorithm

**Recurrence Detection:**
- Analyze 90-day transaction history
- 3+ occurrences with stable amounts (±10%) → "monthly" recurring
- Store learned patterns in `client_gl_mappings.json`
- Improve over time with advisor feedback

**GL Range Mapping:**
- Leverage QBO's standardized accounting structure
- Map GL codes to cash flow categories automatically
- Handle different business types (non-profit vs for-profit GL structures)

**Threshold Classification:**
- Amount-based categorization (major vs recurring)
- Configurable thresholds per client
- Learn optimal thresholds from historical data

**Client Overrides:**
- Manual mapping for edge cases
- Advisor approval/rejection loop
- Continuous learning and improvement

### Data Quality Adaptation Across Market Segments

**For CAS 1.0 Firms (Traditional CAS):**
- RowCol acts as a **standin** for advanced bookkeeping
- Learns GL mappings from raw QBO data
- Provides 80-90% automation with learning system
- Flags unmapped items for manual review
- Enables firms to serve more clients without additional staff

**For CAS 2.0 Firms (Advisory-Focused):**
- RowCol **benefits** from always-on data cleaning
- Higher accuracy with pre-mapped GL accounts
- Faster deployment and more reliable results
- Enhanced Control Plane features for proactive management
- Enables premium advisory services

**For Mixed-Practice Firms:**
- Adapts to data quality level automatically per client
- Starts with learning mode, refines with clean data
- Provides consistent experience across diverse client types
- Scales from nonprofit monthly forecasts to agency weekly cash calls
- Enables firms to serve multiple market segments efficiently

**Universal Learning System:**
- Pattern recognition works across all client types
- GL-based classification scales to any business model
- Learning improves with each new client type
- Reduces onboarding time for new client segments

### Data Quality Scoring

- **Quality Score**: Mapped transactions / Total transactions
- **Pending Bucket**: Unmapped items flagged for manual review
- **Learning Feedback**: Advisor approval/rejection loop
- **Adaptive Thresholds**: Adjust learning parameters based on data quality

---

## 🎨 Template System: Generalized Template Model

### Core Principle: Structure is Universal, Details are Flexible

**The Fundamental Truth:**
Every CAS firm's cash forecast has the same logical structure:

```
BEGINNING CASH
├─ INFLOWS (recurring + variable/major)
├─ OUTFLOWS (recurring vendors + one-time AP + payroll)
ENDING CASH (with roll-forward)
```

What changes across firms:
- ✅ **Labeling** (what's called what: "Donations" vs "Client Receipts" vs "Sales")
- ✅ **Grouping** (how many categories per section: 2 inflow types vs 5)
- ✅ **Visibility** (which sections to show: all firms need payroll, not all need CapEx)

What **NEVER** changes:
- ❌ The logical flow (Beginning → Inflows → Outflows → Ending)
- ❌ The formula chains (roll-forward, totals, buffer calculations)
- ❌ The month/column structure (EOMONTH roll, 13-month horizon by default)

### Three Archetypes (MVP Covers All)

Every CAS firm fits one of these patterns. All use **the same renderer**, different **configs**:

| Archetype | Example Clients | Recurring Inflows | Variable Inflows | Recurring Outflows | One-Time | Payroll? |
|-----------|-----------------|------------------|------------------|-------------------|----------|---------|
| **Nonprofit** | Nonprofits, foundations, associations | Recurring giving, subscriptions | Major gifts, grants, pledges | Vendors, subscriptions | Events, projects | Yes |
| **Agency/Service** | Consulting, agencies, law firms | Retainer fees, ongoing contracts | Project billing, contingency | Vendor, contractors | Equipment, travel | Yes |
| **Product/Inventory** | E-commerce, SaaS, manufacturers | Subscription/recurring sales | Project/major sales, one-time | Vendors, COGS, operations | Equipment, CapEx | Yes |

**Key insight**: All three archetypes use the same semantic sections. Only the **row count and labels** change.

### Template Configuration (Flexible, Not Hardcoded)

Instead of hardcoding row 2 = Beginning Cash, row 9-21 = Major Gifts, we define:

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
    categories:
      - name: "Recurring"
        label: "Bank Account Trends (recurring gifts, donations, average)"
        color: "#FF9900"  # Orange
        type: "auto"      # Auto-populated from QBO
        rows: 3
      - name: "Major"
        label: "Based on Pledges or Accounts Receivable (Named gifts, Awarded, Pledged)"
        color: "#FF00FF"  # Magenta
        type: "manual"    # Advisor populates
        rows: 13
    guard_row: 24
    total_row: 25

  outflows:
    order: 2
    label: "OUTFLOWS"
    start_row: 26
    categories:
      - name: "Recurring"
        label: "Recurring Payments / Subscriptions"
        color: "#F6B26B"  # Tan/Beige
        type: "auto"
        rows: 8
      - name: "Major"
        label: "Recurring Major Costs"
        color: "#F6B26B"
        type: "auto"
        rows: 3
      - name: "OneTime"
        label: "One-Time Payments"
        color: "#EA9999"  # Light red
        type: "semi-auto"  # From QBO bills not yet paid
        rows: 3
      - name: "Unaccounted"
        label: "Known Unaccounted for Payments"
        color: "#D9D2E9"  # Lavender
        type: "manual"
        rows: 1
      - name: "Payroll"
        label: "Payroll and Related Costs"
        color: "#6D9EEB"  # Blue
        type: "auto"
        rows: 31  # Payroll header + detail lines
    guard_row: 76
    total_row: 77

cash_metrics:
  - name: "Change in Cash"
    row: 78
    formula: "=total_inflows - total_outflows"
  - name: "Ending Cash"
    row: 79
    formula: "=beginning_cash + change_in_cash"
  - name: "Buffer (2-month forward)"
    row: 81
    formula: "=sum(next_2_months_outflows)"
  - name: "Net Cash Remaining"
    row: 82
    formula: "=ending_cash - buffer"
```

### How the Renderer Works (Pseudo-code)

```python
def render_template(archetype_config, qbo_data):
    """
    1. Load archetype config (defines sections, rows, order)
    2. Classify QBO data using GL ranges (not vendor names)
    3. Populate rows WITHIN each section using rolling windows
    4. Preserve all formulas (never write formulas, only values)
    5. Output multi-sheet workbook
    """
    
    # Load template structure from config
    wb = create_workbook()
    ws = wb.active
    
    # Set month headers and beginning cash (formulas, never change)
    set_month_headers(ws, archetype_config)
    set_beginning_cash_formula(ws, archetype_config)
    
    # Render each section in order
    for section in archetype_config.sections:
        section_start = section['start_row']
        current_row = section_start
        
        # Render categories within section (in order)
        for category in section['categories']:
            # Get data for this category
            data = classify_qbo_data(qbo_data, category['type'])
            
            # Place category label (row advances by category row count)
            write_label(ws, current_row, category['label'], category['color'])
            current_row += 1
            
            # Write detail lines (rolling window: as many rows as allocated)
            for detail in data[:category['rows']]:
                write_values(ws, current_row, detail, month_columns)
                current_row += 1
            
            # Fill remaining rows with blanks (preserve structure)
            for i in range(category['rows'] - len(data)):
                current_row += 1
        
        # Write guard row and total (formulas, never change)
        write_guard_row(ws, section['guard_row'])
        write_total_formula(ws, section['total_row'], section_start)
    
    # Write ending cash formulas (never change)
    set_ending_cash_formulas(ws, archetype_config)
    set_buffer_formulas(ws, archetype_config)
    set_net_remaining_formula(ws, archetype_config)
    
    return wb
```

### Flexibility in Practice

**Example: Nonprofit vs Agency, same renderer:**

```python
# Nonprofit config
nonprofit = {
    "archetype": "nonprofit",
    "sections": {
        "inflows": {
            "categories": [
                {"name": "Recurring", "rows": 3, "label": "Bank Account Trends (recurring gifts)"},
                {"name": "Major", "rows": 13, "label": "Pledges/AR (Named gifts, Awarded, Pledged)"}
            ]
        },
        "outflows": {
            "categories": [
                {"name": "Recurring", "rows": 8, "label": "Recurring Payments / Subscriptions"},
                {"name": "Payroll", "rows": 31, "label": "Payroll and Related Costs"}
            ]
        }
    }
}

# Agency config (same structure, different rows/labels)
agency = {
    "archetype": "agency",
    "sections": {
        "inflows": {
            "categories": [
                {"name": "Retainer", "rows": 5, "label": "Retainer Fees"},
                {"name": "Project", "rows": 10, "label": "Project Billing"}
            ]
        },
        "outflows": {
            "categories": [
                {"name": "Recurring", "rows": 10, "label": "Vendor Subscriptions"},
                {"name": "Contractor", "rows": 8, "label": "Contractor Payments"},
                {"name": "Payroll", "rows": 25, "label": "Employee Payroll"}
            ]
        }
    }
}

# Same render engine
render_template(nonprofit, nonprofit_qbo_data)  # Generates nonprofit sheet
render_template(agency, agency_qbo_data)        # Generates agency sheet (different layout, same math)
```

### Rolling Window Row Placement Algorithm

**How detail rows are allocated within each category:**

```
Category "Recurring Gifts" allocated 3 rows
QBO data has 2 recurring gift sources: "Monthly Campaign", "Paypal Trend"

Write:
├─ Row 4: Label "Recurring Gifts"
├─ Row 5: "Monthly Campaign" + data
├─ Row 6: "Paypal Trend" + data
└─ Row 7: [blank, preserves structure]

Category "Major Gifts" allocated 13 rows
QBO data has 7 major gift sources

Write:
├─ Row 8: Label "Major Gifts"
├─ Rows 9-15: 7 individual donors
└─ Rows 16-21: [blank, preserves structure]
```

**The key**: Each category gets a fixed row budget from config. If we have fewer items, we pad with blanks. If we have more, we prioritize (top N by amount, or by confidence score).

### YAML Configuration Reference

```yaml
archetype_name: "nonprofit"  # or "agency", "product", "custom"
cadence: "monthly"           # Frequency (monthly, weekly for Control Plane)
horizon: 13                  # Number of month columns
currency: "USD"
timezone: "America/New_York"

beginning_cash_row: 2
beginning_cash_seed_formula: "=SUM(bank_accounts)"  # Pulls from QBO

sections:
  - section_key: "inflows"
    label: "INFLOWS"
    order: 1
    color_scheme: "warm"
    categories:
      - category_key: "recurring"
        label: "Recurring"
        color_hex: "#FF9900"
        data_source: "qbo_invoices"
        filter: "recurrence_pattern=recurring"
        row_budget: 3
        type: "auto"
        
      - category_key: "major"
        label: "Major Gifts"
        color_hex: "#FF00FF"
        data_source: "qbo_ar"
        filter: "amount>threshold"
        row_budget: 13
        type: "manual"
    
    guard_row: 24
    total_row: 25
    total_formula: "=SUM(rows_for_all_categories)"
    
  - section_key: "outflows"
    label: "OUTFLOWS"
    order: 2
    # ... similar structure

cash_metrics:
  - key: "ending_cash"
    row: 79
    formula: "=C2+C78"  # Beginning + change
  - key: "buffer"
    row: 81
    formula: "=SUM(next_2_months_outflows)"
```

### Why This Works

✅ **Scales to any firm**: Config changes, renderer stays the same  
✅ **Preserves structure**: Rows always in logical order, formulas locked  
✅ **Adapts to data quality**: Fewer items = pad with blanks, more items = prioritize by amount  
✅ **Supports learning**: Per-client config can be stored and updated (firm changes labels, adds category)  
✅ **No hardcoding**: GL ranges work for nonprofits, agencies, SaaS, all the same  

---

## 🚀 MVP Scope and Limitations

### What RowCol MVP CAN Do

✅ **Multi-Tenant Foundation (Already Built)**
- Firm-first multi-tenancy with business_id filtering
- Multi-client management through existing console service
- Domain-driven architecture with clean separation
- Smart Sync pattern for live data synchronization
- Robust QBO integration with OAuth2 and throttling

✅ **Data Intelligence (The Real Value)**
- Connect to QBO and fetch bank balances, invoices, and bills
- Classify transactions using GL codes and amount thresholds (not hardcoded vendors)
- Learn recurring patterns from 90-day historical data
- Adapt to different data quality levels (with/without Keeper/ClientHub)
- Handle diverse business types (non-profit, agency, e-commerce, SaaS)
- Provide data quality scoring and learning feedback loops

✅ **Template Management**
- Use pre-built templates for common CAS firm types
- Support client-specific customizations via YAML
- Preserve Excel formulas and formatting
- Generate multiple output formats

✅ **Learning System**
- Build client-specific GL mappings over time
- Learn optimal thresholds from historical data
- Provide manual override capabilities for edge cases
- Track data quality improvement and learning progress
- Flag unmapped items for advisor review

✅ **Scalable Foundation**
- GL-based classification works across all QBO setups
- Learning system improves with usage
- Template system adapts to different workflows
- Foundation for future AI-driven classification
- Built on proven multi-tenant architecture

### What RowCol MVP CANNOT Do (Initial Limitations)

❌ **Advanced Features**
- Real-time data synchronization (scheduled refreshes only)
- Complex financial modeling beyond cash flow forecasting
- Integration with non-QBO accounting systems
- Advanced AI/ML for transaction categorization
- Multi-currency support
- Complex approval workflows

❌ **Enterprise Features**
- Advanced security/compliance features (SOC2, etc.)
- Custom reporting beyond cash flow
- Advanced user management and permissions
- Enterprise SSO and advanced RBAC

❌ **Control Plane Features**
- Real-time dashboards and alerts
- Interactive decision prompts
- Client-facing portals
- Advanced analytics and insights
- Automated email notifications

### Known Technical Limitations

1. **QBO API Dependencies**
   - Rate limits may impact large data pulls
   - OAuth token refresh complexity
   - Limited historical data access

2. **Template Flexibility**
   - Row-based mapping limits complex layouts
   - Color schemes are predefined
   - Formula complexity is constrained

3. **Data Quality Dependencies**
   - Requires some level of QBO GL mapping
   - Learning algorithm needs sufficient historical data
   - Manual review required for edge cases

---

## 🎯 Success Metrics

### Phase 0 (Foundation) Success Criteria

- [ ] Generate working Excel workbook from QBO data across multiple client types
- [ ] Achieve 80%+ data quality score on diverse test data (nonprofit, agency, SaaS)
- [ ] Complete pilot with 2+ different CAS firm types
- [ ] Demonstrate 2+ hour time savings per client per month across segments
- [ ] Validate GL-based learning system with diverse GL structures

### Phase 1 (Firm Console) Success Criteria

- [ ] Support 5+ clients across different market segments
- [ ] Achieve 90%+ data quality score through learning system
- [ ] Complete 3+ firm pilots across CAS 1.0 and CAS 2.0 segments
- [ ] Generate $1K+ monthly recurring revenue
- [ ] Demonstrate template adaptability across client types

### Phase 2 (Market Expansion) Success Criteria

- [ ] 25+ active clients across 5+ different CAS firms
- [ ] $5K+ monthly recurring revenue
- [ ] 90%+ client retention rate across segments
- [ ] Successful deployment of both Planner and Control Plane modes
- [ ] Template library supporting 3+ industry verticals

### Long-term Success Metrics

- [ ] 100+ active clients across 10+ CAS firms
- [ ] $25K+ monthly recurring revenue
- [ ] 95%+ client retention rate
- [ ] Market leadership in CAS automation space
- [ ] Successful transition to full Control Plane platform

---

## 🔄 Evolution Path

### Phase 0 → Phase 1 (Leveraging Existing Architecture)
- **Template System**: Build YAML-based template configuration on existing multi-tenant foundation
- **GL Learning**: Implement GL-based classification using existing QBO integration
- **Excel Generation**: Add template renderer to existing runway orchestration
- **Firm Console**: Enhance existing console service for multi-client management

### Phase 1 → Phase 2 (Expanding Capabilities)
- **Template Library**: Build comprehensive template library for different client types
- **Learning Enhancement**: Improve GL learning algorithms using existing data patterns
- **Multi-Format Output**: Add PDF and web output to existing template system
- **Advanced Scheduling**: Leverage existing sync orchestrator for automated refreshes

### Phase 2 → Phase 3 (Control Plane Transition)
- **Real-time Dashboards**: Build on existing runway services and console
- **Client Portals**: Extend existing multi-tenant architecture for client access
- **Advanced Analytics**: Add analytics layer to existing data repository pattern
- **Integration Expansion**: Add Ramp, Plaid, Stripe to existing rail architecture

### Phase 3 → Phase 4 (Full Platform)
- **Multi-Firm Support**: Scale existing firm-first multi-tenancy
- **Advanced Integrations**: Leverage existing Smart Sync pattern for new rails
- **Enterprise Features**: Add SOC2 compliance and advanced RBAC
- **AI/ML Enhancement**: Build on existing learning system for advanced classification

---

## 📋 Risk Assessment

### High-Risk Areas

1. **Market Adoption Across Segments**
   - Risk: Different CAS segments may have varying adoption rates
   - Mitigation: Start with CAS 1.0 (easier adoption), expand to CAS 2.0
   - Monitoring: Segment-specific usage metrics and feedback

2. **QBO API Reliability and Rate Limits**
   - Risk: API failures could impact multiple clients across segments
   - Mitigation: Robust error handling, fallback mechanisms, and rate limiting
   - Monitoring: API health checks, alerting, and performance metrics

3. **Data Quality Dependencies Across Client Types**
   - Risk: Learning system may struggle with diverse data quality levels
   - Mitigation: Adaptive learning algorithms and manual override capabilities
   - Monitoring: Quality score tracking and improvement metrics per segment

### Medium-Risk Areas

1. **Template Complexity Across Industries**
   - Risk: YAML system may not scale to all industry verticals
   - Mitigation: Modular template system with industry-specific packs
   - Monitoring: Client feedback and usage analytics per vertical

2. **Scalability Across Market Segments**
   - Risk: System may not scale efficiently across diverse client types
   - Mitigation: Modular architecture and cloud infrastructure
   - Monitoring: Performance metrics and capacity planning per segment

3. **Competitive Response**
   - Risk: Established players may copy RowCol's approach
   - Mitigation: Focus on learning system and network effects
   - Monitoring: Competitive intelligence and feature differentiation

### Low-Risk Areas

1. **Technical Architecture**
   - Risk: GL-based learning system may be too complex
   - Mitigation: Proven QBO API patterns and incremental development
   - Monitoring: Development velocity and technical debt metrics

---

## 🎉 Conclusion

RowCol MVP represents a focused, valuable solution to a real problem faced by the broader CAS market. By leveraging an existing multi-tenant architecture and starting with an "embarrassingly humble" Excel automation tool, we can validate the market across multiple segments while building on a proven foundation.

**Key Strategic Insights:**
- RowCol addresses a broader CAS opportunity beyond any single firm or client type
- We're ahead of the adoption curve - most CAS firms haven't seen this level of automation because no one has shown it to them yet
- The dual-mode strategy (Planner vs Control Plane) addresses the full spectrum of CAS needs
- GL-based learning system scales across diverse client types and business models
- **Existing multi-tenant architecture provides a solid foundation for rapid MVP development**

**Technical Advantage:**
- Built on proven multi-tenant architecture with firm-first hierarchy
- Domain-driven design with clean separation of concerns
- Smart Sync pattern already implemented for live data synchronization
- Robust QBO integration with OAuth2 and throttling already in place

The key to success is leveraging the existing architecture foundation while maintaining focus on the core value proposition. This MVP is not just a product—it's the first step in transforming how CAS firms manage and advise on client cash flow across the entire market spectrum.

**Market Positioning:** RowCol bridges traditional CAS (automation of existing workflows) and modern advisory services (infrastructure for new client relationships), creating a scalable opportunity across the entire CAS industry.

---

**Next Steps:** Proceed to the detailed build plan for implementation guidance, leveraging existing architecture and task breakdown across multiple market segments.
