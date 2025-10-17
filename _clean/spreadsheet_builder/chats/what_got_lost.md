
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

**Hypothesis**: The shift from vendor-specific hardcoding (Mission First Operations LLC) to GL-based classification was correct, BUT it oversimplified the problem. The thread was actually solving a richer problem (vendor patterns + temporal bucketing), and we've backed it down to just GL classification.

The question is: **Is that intentional simplification for MVP, or did we lose the narrative?**


