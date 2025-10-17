
# DETAILS LOST IN SUMMARIZATION

## Critical Technical Details NOT in Task Docs

### 1. AR/AP Bucketing Logic (Lines 152-153)
**Missing**: "Bucket AR by expected receipt month (terms + days-to-pay)" and "AP by due month (or pay-on policy)"
- This is TEMPORAL BUCKETING - mapping transactions to future months based on DSO/payment terms
- Not just GL classification
- Explicitly mentioning "days-to-pay" and "pay-on policy" as decision factors

### 2. Safety Rails / Validation (Lines 204-210)
**Missing**: Specific validation checks
- Totals cross-check (Details total vs Outflows total)
- Beginning cash tie-out to QBO bank
- Variance banner if AR/AP timing deviates from last period >X%
- These are explicit "trust but verify" mechanisms

### 3. Manual Overrides Storage Pattern (Line 159)
**Missing**: "store them externally so regeneration doesn't delete them"
- Overrides are PERSISTENT (not ephemeral)
- Stored outside Excel (in DB or JSON)
- Regeneration is idempotent - runs monthly without nuking user edits

### 4. Coloring/Visual Semantics Tied to Automation Strategy (Lines 256-264)
**Missing**: Explicit mapping of color → automation type
- Orange = Frequency-based (predictable)
- Magenta = High-variance (editable, AR-driven)
- Red = Non-recurring AP (one-time flags)
- Purple = Unaccounted buffer
- Not just decoration; color = classification signal

### 5. Details by Vendor Tab is the FEEDER (Lines 56-69, 107-109)
**Missing**: "Details by Vendor" is NOT derived from main sheet; it's the SOURCE
- Vendor, GL, Months Paid, Frequency, per-month amounts
- "Either hand-entered or auto-filled from QBO Bills"
- Recurring vendor logic: if no explicit bill, use mapping (Frequency=Monthly/Quarterly/One-time)
- This drives outflows placement

### 6. Multiple Output Variants (Lines 46-54)
**Missing**: Template variants existing already in workbook
- "Cash Flow-Ops" (simpler sibling)
- "Cash Flow wsavings" (with savings treatment)
- Hint: system must support multiple output layouts

### 7. Summary by Vendor/Class is Formula-Linked to Main Sheet (Line 72)
**Missing**: Explicit note that Summary references hidden rows on main sheet
- `=SUM('RA Edits-Cash Flow-Ops'!B25:F25)` - it's cross-sheet formula linking
- Row structure must remain stable across regenerations
- Changing row 25 breaks Summary's formula

### 8. Payroll Detail (Lines 79-86)
**Missing**: Payroll Support is allocation helper (not a total)
- Breaks down wages by department (Administrative, Development, Communications/Outreach)
- Acts as "feeder" or "check against" main payroll lines
- Not auto-linked; used by humans to build payroll block

### 9. "Vendor Mapping" vs "GL Mapping" Distinction (Line 108, 116-118)
**Missing**: Vendor mapping includes more than GL
- Vendor → GL/Class (not just GL)
- Frequency = Monthly/Quarterly/One-time
- Default day-of-month
- "Any known allocations" (notes in Summary)
- This is richer than GL ranges alone

### 10. AR Timing Intelligence (Lines 100, 220)
**Missing**: DSO (Days Sales Outstanding) learning
- "historical average days-to-pay by customer"
- "AR realism toggle" - hide invoices >60d late, probability-weighted receipts
- Confidence/aging logic for inflow projection

### 11. Payment Policy Logic (Line 222)
**Missing**: Explicit AP policy configuration
- "AP policy switch (pay on Tue/Thu, 14-day buffer guardrail)"
- Not just "due date"; includes "when we actually pay" rules

### 12. Branded Output (Line 142)
**Missing**: "Optionally brand the workbook (logo, firm name, client name, run date)"
- Multi-tenant: each firm's output has firm branding
- Client name and run date for audit trail

### 13. Assumption Snapshot for Auditing (Line 181)
**Missing**: "store a JSON snapshot of assumptions (days-to-pay, frequency rules)"
- Audit trail: what assumptions were used to generate this workbook
- Reproducibility / explainability

### 14. AR/AP Confidence/Realism (Lines 220, 454)
**Missing**: The concept that initial AR/AP forecast is UNCERTAIN and needs handling
- Invoices >60d old = risky
- Probability-weighting for AR
- Variance detection for deviations from prior period

---

## What Changed Between Then and Now

### Original Assumption (Thread): Vendor-Specific Hardcoding
```json
{ "Mission First Operations, LLC": { "frequency": "monthly", "default_day": 15 } }
```
**Problem Identified**: Scales only to Mission First, not universal

### Shift to GL-Based: Not Mentioned in Summary
- GL ranges (4000-4999, 6000-6999, 60100-60199) as universal classifier
- Thresholds (major vs recurring based on amount)
- Learning from recurrence (3+ occurrences, ±10% variance)
- This is a REASONABLE response to the problem, but wasn't in thread

---

## What Should Be in the Docs But Isn't

1. **"Details by Vendor" is not derived; it's the source feeder** - need to explicit state this
2. **Temporal bucketing logic** - DSO, payment terms, pay-on-policy (not just GL)
3. **Safety rails / validation checks** - cross-checks, tie-outs, variance detection
4. **Override persistence pattern** - stored externally, idempotent regeneration
5. **AR/AP confidence/realism** - aging logic, probability-weighting
6. **Variant workbook support** - Cash Flow-Ops, Cash Flow wsavings
7. **Color = Classification signal** - not just decoration
8. **Assumption audit trail** - JSON snapshot for reproducibility

---

## TROUBLING CONTRADICTIONS & ARCHITECTURAL SHIFTS

### Issue 1: GL-Based Classification vs. Vendor Mapping
**Thread Says** (Lines 108, 116-118):
- Vendor Mapping is rich: `{vendor, frequency, default_day, gl, class}`
- Uses "Vendor→GL/Class" mapping, not just GL ranges
- "Frequency = Monthly/Quarterly/One-time"

**Current Docs Say**:
- GL ranges are universal (4000-4999, 6000-6999, 60100-60199)
- No mention of frequency as part of vendor config
- No mention of "default_day" or class mapping

**Why It Matters**:
- Thread: Vendor identity matters (who is paying, when, recurrence pattern)
- Current: Only GL matters (what account category)
- These are DIFFERENT problems; one is about vendor patterns, one is about account types
- **Question**: Are we building a GL classifier or a vendor recurrence detector?

### Issue 2: "Details by Vendor" Origin
**Thread Says** (Lines 56-69):
- "Details by Vendor" is the FEEDER tab
- "Either hand-entered or auto-filled from QBO Bills"
- Drives outflows placement (is the SOURCE)

**Current Docs Say**:
- Template renders from classified data
- No explicit mention that "Details by Vendor" is the source
- Implies classification happens first, then Details by Vendor is derived

**Why It Matters**:
- Thread: Details by Vendor = human input + QBO bills → defines what goes in main sheet
- Current: Main sheet is derived from classification → Details is reference
- **Data flow is reversed**
- **Question**: Does Details by Vendor flow INTO the system, or is it OUTPUT FROM it?

### Issue 3: Temporal Bucketing Missing from Phase 1 Tasks
**Thread Says** (Lines 152-153):
- "Bucket AR by expected receipt month (terms + days-to-pay)"
- "Bucket AP by due month (or pay-on policy)"
- This is explicitly called out as part of the "Planner layer"

**Current Docs Say**:
- E1.3 talks about GL classification and rolling windows
- No mention of DSO, payment terms, or pay-on-policy
- No algorithm for "when will this invoice actually be paid"

**Why It Matters**:
- Thread: Temporal logic is critical (invoice on Jan 1, 30-day terms → cash in Feb)
- Current: Only classifies type (major vs recurring), not timing
- **Question**: Are we predicting AMOUNT or TIMING or BOTH?

### Issue 4: AR/AP Confidence & Realism
**Thread Says** (Lines 220):
- "AR realism toggle (e.g., 'hide invoices >60d late' or 'only probability-weighted receipts')"
- Acknowledges AR forecast is UNCERTAIN

**Current Docs Say**:
- Data quality score (mapped GL count / total)
- No mention of invoice aging, confidence scoring, or AR risk

**Why It Matters**:
- Thread: AR is probabilistic (old invoice less likely to pay)
- Current: All classified transactions treated equally
- **Question**: Do we need invoice aging logic? Is this Phase 0 or Phase 2?

### Issue 5: Variant Workbook Support
**Thread Says** (Lines 46-54):
- "Cash Flow-Ops" (simpler sibling)
- "Cash Flow wsavings" (with savings treatment)
- "Your generator can produce either style off one template"

**Current Docs Say**:
- Talk about archetype templates (nonprofit, agency, product)
- No mention of variants like "Cash Flow wsavings"
- Imply variants are firm-specific, not built-in alternatives

**Why It Matters**:
- Thread: Multiple layouts within ONE workbook (visible/hidden variants)
- Current: Multiple archetype configs across different firms
- **Question**: Is this about workbook variants or template archetypes?

### Issue 6: Safety Rails / Validation
**Thread Says** (Lines 204-210):
- "Totals cross-check (Details total vs Outflows total)"
- "Beginning cash tie-out to QBO bank"
- "Variance banner if AR/AP timing deviates from last period >X%"
- These are GUARDRAILS for trust

**Current Docs Say**:
- Data quality score only
- No cross-checks or tie-outs mentioned
- No variance detection

**Why It Matters**:
- Thread: System has VALIDATION layer (catches errors)
- Current: Only scoring layer (reports what happened)
- **Question**: Is Phase 0 about validation or just classification?

### Issue 7: Override Persistence & Idempotency
**Thread Says** (Line 159):
- "Inject manual overrides last (and store them externally so regeneration doesn't delete them)"
- Monthly regeneration is SAFE (doesn't nuke advisor edits)

**Current Docs Say**:
- Nothing about override persistence
- Nothing about regeneration safety
- Implies values are recalculated each time

**Why It Matters**:
- Thread: Advisor edits are STICKY across regen
- Current: Undefined (might wipe out advisor changes)
- **Question**: How are manual adjustments preserved? DB? Versioning?

---

## REAL GAPS TO RESOLVE (Not Ambiguity from Evolution)

### Gap A: DSO Calculation Algorithm
**Thread mentions it** (Line 100): "historical average days-to-pay by customer"
**No docs specify**: How to calculate or apply DSO
- Is it per-customer or per-GL account?
- How many months of history?
- Fallback if no history?

### Gap B: Payment Policy Config
**Thread mentions** (Line 222): "AP policy switch (pay on Tue/Thu, 14-day buffer guardrail)"
**Current docs don't specify**: Format, storage, or application
- Is this a firm-wide config or per-client?
- Does it override due dates?

### Gap C: Vendor Mapping Schema
**Thread shows** (Line 116-118): `{vendor, frequency, default_day, gl, class}`
**Current docs use**: GL ranges only
- Where does vendor mapping live? (JSON? DB?)
- How is it updated (manually, learned, hybrid)?
- What about vendor name normalization?

### Gap D: Branded Output Details
**Thread mentions** (Line 142): "Optionally brand the workbook (logo, firm name, client name, run date)"
**Current docs don't say**:
- Where logos come from (S3? Config?)
- How firm name/client name are injected
- Is this Phase 0 or Phase 1?

### Gap E: Assumption Audit Trail
**Thread mentions** (Line 181): "store a JSON snapshot of assumptions (days-to-pay, frequency rules) for auditing"
**Current docs don't mention**:
- What gets stored (which assumptions exactly)?
- Where stored (DB? Separate file?)
- How is it used for auditing/reproducibility?

---

## MOST TROUBLING: Data Flow Direction

**Thread mental model**:
```
QBO Bills + AR + Bank
    ↓
Vendor Mapping (who pays, how often, when)
    ↓
Details by Vendor (feeder table)
    ↓
Temporal bucketing (when does it land in which month)
    ↓
Outflows/Inflows placement in main sheet
```

**Current docs mental model**:
```
QBO Transactions
    ↓
GL Classification (4000s, 6000s, 601xx)
    ↓
Thresholds + recurrence (major vs recurring)
    ↓
Template population (write to rows)
```

**These are not equivalent.** First is about VENDOR BEHAVIOR + TIMING. Second is about ACCOUNT CATEGORIZATION + AMOUNT.
- Thread is solving: "Which vendor, how often, when will they pay?"
- Current is solving: "Which GL account, major or recurring?"

**FINALIZED UNDERSTANDING** (from end of thread, lines 2000-2242):

The thread **DID** evolve to a GL-based approach, but it's more sophisticated than current docs suggest:

### What the Thread Actually Concluded:
1. **GL-Based Classification + Learning**: Use GL ranges (4000s, 6000s, 601xx) as foundation, BUT also learn recurring patterns from historical data
2. **Hybrid Approach**: Combine pre-mapped GLs with learned vendor patterns (3+ occurrences, ±10% stability)
3. **Data Quality Adaptation**: Handle incomplete GL mappings with "Pending" bucket and quality scoring
4. **Client Overrides**: Store learned mappings in `client_gl_mappings.json` for advisor approval
5. **Working Code Delivered**: Actual Python modules (`mapping_engine.py`, `renderer.py`) with FastAPI endpoint

### The Thread's Final Architecture:
```
QBO Transactions
    ↓
GL Classification (4000s, 6000s, 601xx) + Thresholds (major vs recurring)
    ↓
Recurrence Learning (3+ occurrences, ±10% stability) 
    ↓
Client Override Storage (client_gl_mappings.json)
    ↓
Template Population (preserve formulas, add Pending row)
    ↓
Data Quality Flagging (mapped/total ratio)
```

### What's Missing from Current Docs:
1. **Recurrence Learning Algorithm**: The thread delivered working code for learning vendor patterns from historical data
2. **Client Override Storage**: `client_gl_mappings.json` for advisor-approved mappings
3. **Data Quality Adaptation**: "Pending" bucket for unmapped transactions
4. **Working Code Modules**: `mapping_engine.py`, `renderer.py`, FastAPI endpoint
5. **Hybrid Learning**: Not just GL ranges, but GL + learned patterns

**CONCLUSION**: The thread DID solve the vendor-specific hardcoding problem with GL-based classification, but it's more sophisticated than current docs show. The missing piece is the **learning/recurrence detection** layer that makes it truly universal.

---

## SPECIFIC LOCATIONS WHERE MISSING PIECES SHOULD BE ADDED

### **1. E0_PHASE_0_PORTING_AND_INTEGRATION.md - MISSING ENTIRELY**

**Current State**: No mention of recurrence learning, client overrides, or data quality adaptation
**Should Add**: New task E0.6 for learning/recurrence detection

**Specific Design Missing**:
```python
# E0.6: Implement Recurrence Learning Engine
def detect_recurring_transactions(qbo_client, business_id, days_back=90):
    """Learn recurring patterns from historical QBO data"""
    transactions = qbo_client.get_transactions(business_id, days_back)
    recurring_patterns = {}
    
    for tx in transactions:
        vendor = tx.get("EntityRef", {}).get("name")
        gl = tx.get("AccountRef", {}).get("value")
        amount = float(tx.get("TotalAmt", 0))
        date = tx.get("TxnDate")
        
        if vendor and gl:
            key = (vendor, gl)
            if key not in recurring_patterns:
                recurring_patterns[key] = {"amounts": [], "dates": []}
            recurring_patterns[key]["amounts"].append(amount)
            recurring_patterns[key]["dates"].append(date)
    
    learned_mappings = {}
    for (vendor, gl), data in recurring_patterns.items():
        if len(data["dates"]) >= 3:
            avg_amount = sum(data["amounts"]) / len(data["amounts"])
            variance = max(data["amounts"]) - min(data["amounts"])
            if variance / avg_amount <= 0.1:  # ±10% stability
                learned_mappings[vendor] = {
                    "gl": gl, 
                    "frequency": "monthly", 
                    "amount": avg_amount,
                    "confidence": min(len(data["dates"]) / 3, 1.0)
                }
    
    return learned_mappings

# Store in client_gl_mappings.json
def store_client_mappings(business_id, learned_mappings):
    """Persist learned patterns for advisor approval"""
    client_file = f"_clean/data/client_gl_mappings_{business_id}.json"
    with open(client_file, 'w') as f:
        json.dump(learned_mappings, f, indent=2)
```

**Location**: Add as E0.6 after E0.5, before Phase 1 dependencies

---

### **2. E1_PHASE_1_TEMPLATE_SYSTEM.md - PARTIALLY MISSING**

**Current State**: Has template renderer but missing learning integration
**Should Add**: Integration of learned mappings into template population

**Specific Design Missing**:
```python
# E1.3.1: Integrate Learning with Template Population
def populate_template_with_learning(template_path, business_id, qbo_data):
    """Combine GL classification + learned patterns + client overrides"""
    
    # Step 1: GL Classification (existing)
    gl_classified = classify_by_gl_ranges(qbo_data)
    
    # Step 2: Load learned patterns
    learned_mappings = load_client_mappings(business_id)
    
    # Step 3: Load client overrides (advisor-approved)
    client_overrides = load_client_overrides(business_id)
    
    # Step 4: Merge all three sources
    final_classification = merge_classifications(
        gl_classified,      # Universal GL ranges
        learned_mappings,   # Historical patterns
        client_overrides    # Advisor corrections
    )
    
    # Step 5: Add "Pending" bucket for unmapped
    pending_items = identify_unmapped_transactions(qbo_data, final_classification)
    final_classification["pending"] = pending_items
    
    # Step 6: Calculate data quality score
    quality_score = calculate_data_quality(final_classification, qbo_data)
    
    return final_classification, quality_score

def merge_classifications(gl_classified, learned, overrides):
    """Priority: Overrides > Learned > GL Classification"""
    merged = gl_classified.copy()
    
    # Apply learned patterns (if not overridden)
    for vendor, pattern in learned.items():
        if vendor not in overrides:
            merged[f"learned:{vendor}"] = pattern
    
    # Apply overrides (highest priority)
    for vendor, override in overrides.items():
        merged[f"override:{vendor}"] = override
    
    return merged
```

**Location**: Add as E1.3.1 before E1.3.2 (Template Renderer)

---

### **3. ROWCOL_MVP_PRODUCT_SPECIFICATION.md - MISSING IMPLEMENTATION DETAILS**

**Current State**: Mentions learning but no specific implementation
**Should Add**: Detailed learning algorithm specification

**Specific Design Missing**:
```yaml
# Learning Algorithm Configuration
learning_config:
  recurrence_threshold: 3          # Minimum occurrences to detect pattern
  stability_threshold: 0.1         # ±10% variance allowed
  history_days: 90                 # Look back 90 days
  confidence_weights:
    frequency: 0.4                 # How often it occurs
    stability: 0.3                 # Amount consistency  
    recency: 0.3                   # How recent the pattern

# Client Override Storage Schema
client_gl_mappings_schema:
  vendor_name:
    gl: "string"                   # GL account code
    frequency: "monthly|quarterly|one-time"
    amount: number                 # Expected amount
    confidence: number             # 0.0-1.0
    last_updated: "ISO_date"
    advisor_approved: boolean

# Data Quality Metrics
data_quality_metrics:
  mapped_transactions: number      # Successfully classified
  total_transactions: number       # Total from QBO
  quality_score: number           # mapped/total ratio
  pending_count: number           # Unmapped items
  learning_confidence: number     # Average confidence of learned patterns
```

**Location**: Add after line 367 (current learning section)

---

### **4. ROWCOL_MVP_BUILD_PLAN.md - MISSING PHASE 0 LEARNING TASKS**

**Current State**: Has data quality scoring but no learning implementation
**Should Add**: Specific learning tasks in Phase 0

**Specific Design Missing**:
```python
# Phase 0 Learning Tasks (add to existing Phase 0 section)

## E0.6: Implement Recurrence Learning Engine
- **Duration**: 3 days
- **Dependencies**: E0.1-E0.5 complete
- **Deliverable**: `mapping_engine.py` with learning capabilities

## E0.7: Create Client Override Storage System  
- **Duration**: 2 days
- **Dependencies**: E0.6 complete
- **Deliverable**: `client_gl_mappings.json` storage and retrieval

## E0.8: Integrate Learning with GL Classification
- **Duration**: 2 days  
- **Dependencies**: E0.6, E0.7 complete
- **Deliverable**: Hybrid classification system (GL + Learning + Overrides)
```

**Location**: Add after E0.5 in Phase 0 section

---

### **5. MISSING: Working Code Modules from Thread**

**Thread Delivered**: Actual working `mapping_engine.py` and `renderer.py`
**Current Docs**: No mention of these specific modules
**Should Add**: Reference to these as starting point

**Specific Design Missing**:
```python
# mapping_engine.py (from thread, lines 2108-2168)
def detect_transactions():
    """GL-based classification with learning integration"""
    # Implementation from thread with working code
    
def detect_recurring_transactions():
    """Learn patterns from 90-day history"""
    # Implementation from thread with working code

# renderer.py (from thread, lines 2146-2168)  
def populate_excel(template_path, output_path, mappings, data_quality):
    """Populate Excel with learned mappings and Pending bucket"""
    # Implementation from thread with working code
```

**Location**: Add as reference in E0.6 and E1.3

---

## SUMMARY: WHAT'S ACTUALLY MISSING

1. **E0.6**: Entire recurrence learning task (3 days)
2. **E0.7**: Client override storage system (2 days)  
3. **E1.3.1**: Learning integration with template population
4. **Product Spec**: Detailed learning algorithm configuration
5. **Build Plan**: Phase 0 learning tasks
6. **Working Code**: Reference to thread's `mapping_engine.py` and `renderer.py`

**Total Missing Effort**: ~7 days of development work
**Impact**: Without these, system is just GL classification, not the hybrid learning system the thread concluded was necessary


