# F02: Update All Documentation for Firm-First Strategy

**Status**: 🔴 READY TO EXECUTE  
**Effort**: 2-3 hours  
**For**: Auto mode / junior model

---

## OBJECTIVE

Update all remaining docs to reflect firm-first CAS strategy instead of owner-first strategy.

**What Changed**: CAS firms (20-100 clients) are PRIMARY ICP, not individual owners.

---

## 🧠 RAMIFICATIONS - Understand This First

### The Strategic Flip

**BEFORE (Owner-First)**:
- Target: Individual business owner managing their own QBO
- Use Case: "I need to know if I can make payroll this Friday"
- Distribution: QBO App Store (self-serve)
- Pricing: $99-$299/mo per business
- User: Business owner logs in, sees their runway
- Value Prop: "Agentic AI automates your weekly cash call"

**AFTER (Firm-First)**:
- Target: CAS firm managing 20-100 client businesses
- Use Case: "Which of my 50 clients are at runway risk this week?"
- Distribution: Direct sales to CAS firms
- Pricing: $50/mo per client ($2,500/mo for 50 clients)
- User: Firm staff logs in, sees batch view of all clients
- Value Prop: "Multi-client cash call automation with data quality enforcement"

### What This Means for Docs

**ANY mention of**:
- "business owner" → think "CAS firm managing clients"
- "self-serve" → think "direct sales to firms"
- "QBO App Store" → deprioritized to Phase 7+ (future)
- "agentic" / "AI learns" → deprioritized to Phase 7+ (nice-to-have)
- "single business" → think "firm with 20-100 clients"

**NEW priorities**:
1. **Multi-tenant**: Firm → Clients hierarchy
2. **Data completeness**: Bank feeds, missing bill detection
3. **Batch workflows**: View all clients at once
4. **RBAC**: Firm staff roles (admin/staff/view-only)
5. **Reliability**: Data quality over AI features

### Why We Pivoted

**Levi Morehouse (Aiwyn.ai President) said**:
- ✅ Problem is "10,000% right - real need"
- ❌ BUT: "Owners won't do the work" (won't maintain data completeness)
- ✅ Solution: CAS firms can ensure data quality
- ✅ Pricing: $50/mo per client is realistic for firms

**The killer insight**: Missing bills = wrong runway = broken trust = churned customer. Owners won't enter missing bills. CAS firms will.

### How to Think About Updates

**If you see owner-first language**, ask:
1. Does this apply to firm staff managing clients? (probably yes)
2. Should I mention "firm" or "multi-client"? (probably yes)
3. Is this about self-serve onboarding? (deprioritize to Phase 7+)
4. Is this about AI/agentic features? (deprioritize to Phase 7+)

**Core principle**: Same product (weekly cash call ritual), different user context (firm managing many clients vs owner managing own business).

### What Stays The Same

✅ Weekly cash call ritual  
✅ Must Pay vs Can Delay logic  
✅ One approval → batch QBO actions  
✅ Runway-first orientation  
✅ 3-layer architecture (orchestrators → calculators → experiences)  
✅ All the code we built  

### What Changes

🔄 PRIMARY user = CAS firm staff (not business owner)  
🔄 PRIMARY view = batch dashboard (not single business console)  
🔄 PRIMARY priority = data completeness (not agentic AI)  
🔄 PRIMARY pricing = $50/mo per client (not $99/mo per business)  
🔄 PRIMARY distribution = direct sales (not QBO App Store)  

---

## 💡 AUTO-MODE DECISION FRAMEWORK

When you encounter a section, ask yourself:

### 1. Is this about the USER?
- **OLD**: "business owner"
- **NEW**: "CAS firm staff" or "firm managing clients"
- **ACTION**: Update or add firm-first context

### 2. Is this about DISTRIBUTION?
- **OLD**: "QBO App Store", "self-serve", "marketplace"
- **NEW**: "direct sales to CAS firms" (primary), App Store is Phase 7+
- **ACTION**: Mention CAS firms first, owner self-serve as future

### 3. Is this about FEATURES?
- **OLD**: "Agentic AI", "Smart Policies", "AI learns preferences"
- **NEW**: "Data completeness", "bank feeds", "missing bill detection"
- **ACTION**: Deprioritize AI features, emphasize reliability

### 4. Is this about PRICING?
- **OLD**: "$99-$299/mo"
- **NEW**: "$50/mo per client" (CAS firms), $99/mo (future owners)
- **ACTION**: Update pricing, mention per-client model

### 5. Is this about ARCHITECTURE?
- **OLD**: Single business tenant
- **NEW**: Firm → Clients hierarchy
- **ACTION**: Mention multi-tenant, firm_id → client_id

### 6. Is this TECHNICAL (not user-facing)?
- **EXAMPLES**: Service boundaries, OODA loop, data orchestrators
- **ACTION**: Probably fine as-is, maybe add "firm-first context" note

### When In Doubt

**ASK**: "Would a CAS firm managing 50 clients care about this?"
- **YES**: Update for firm-first context
- **NO**: Probably about owner self-serve → mention as Phase 7+ future

**DON'T OVERTHINK**: If it's a minor mention, just add "firm-first: [context]" note

---

## STEP 1: Archive Old Build Plan (10 min)

**ACTION**: Move old build plan to archive

```bash
# Move the old build plan
mv docs/build_plan_v5.md archive/owner-first/build_plan_v5.md

# Commit
git add -A
git commit -m "archive: move build_plan_v5.md to owner-first archive"
```

**VERIFY**: `docs/build_plan_v5.md` no longer exists

---

## STEP 2: Update Product Vision Doc (30 min)

**FILE**: `docs/product/Oodaloo_RowCol_cash_runway_ritual.md`

**FIND THIS** (around line 1-30):
```markdown
# Oodaloo / RowCol — The Cash Runway Ritual

**Who it's for:**

* Professional services businesses (creative/marketing/IT, $1–5M revenue, 10–30 staff) on QBO.
```

**REPLACE WITH**:
```markdown
# Oodaloo — The Weekly Cash Call for CAS Firms

**Primary ICP:** CAS accounting firms serving 20-100 clients

**Secondary ICP (Future):** Professional services businesses (creative/marketing/IT, $1–5M revenue, 10–30 staff) on QBO.

**Why CAS Firms First:**
- Owners won't maintain data completeness (missing bills = broken trust)
- CAS firms can ensure data quality and enforce the ritual
- $50/mo per client scales better than $99/mo per owner
- Weekly cash call is unaddressed opportunity for CAS firms
```

**FIND THIS** (around line 90-100):
```markdown
**Phase 1: QBO Marketplace (Oodaloo)**
Oodaloo is the self-serve wedge:

* Owners and lone bookkeepers can adopt it directly from the QBO App Store.
```

**REPLACE WITH**:
```markdown
**Phase 1: CAS Firm Channel (Oodaloo Firms)**
CAS firms are the primary wedge:

* Direct sales to CAS firms serving 20-100 clients
* $50/mo per client pricing ($2,500/mo for 50-client firm)
* Multi-client dashboard with batch runway reviews
* Data completeness features (bank feeds, missing bill detection)

**Phase 2 (Future): QBO Marketplace (Oodaloo Solo)**
After CAS firm validation:

* Self-serve owners via QBO App Store
* Requires bank feed integration for data completeness
* $99/mo pricing for single-client
```

**COMMIT**:
```bash
git add docs/product/Oodaloo_RowCol_cash_runway_ritual.md
git commit -m "docs: update product vision for firm-first strategy"
```

---

## STEP 3: Update Other ADRs (If Needed) (30 min)

**CHECK THESE FILES** for owner-first references:

1. `docs/architecture/ADR-001-domains-runway-separation.md`
2. `docs/architecture/ADR-006-data-orchestrator-pattern.md`
3. `docs/architecture/ADR-007-service-boundaries.md`

**IF** you find "owner" or "QBO App Store" or "self-serve":

**ADD THIS SECTION** at the top (after the header):

```markdown
---
**STRATEGIC UPDATE (2025-09-30)**: CAS firms are now primary ICP. This ADR's technical patterns remain valid, but consider firm-first context (firm managing 20-100 clients) instead of single-owner context.
---
```

**COMMIT EACH**:
```bash
git add docs/architecture/ADR-XXX.md
git commit -m "docs: add firm-first context to ADR-XXX"
```

---

## STEP 4: Update COMPREHENSIVE_ARCHITECTURE.md (20 min)

**FILE**: `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md`

**FIND** (in the introduction section):
```markdown
**Target Market**: Service agencies using cash accounting
```

**REPLACE WITH**:
```markdown
**Primary Market**: CAS accounting firms serving 20-100 clients ($50/mo per client)
**Secondary Market (Future)**: Service agencies using cash accounting ($99/mo)
```

**FIND** (search for "owner" or "business owner"):

**UPDATE** any instances to mention "CAS firm" or "firm staff" as primary user.

**EXAMPLE**:
- OLD: "business owner reviews weekly digest"
- NEW: "CAS firm staff review batch digest across all clients"

**COMMIT**:
```bash
git add docs/architecture/COMPREHENSIVE_ARCHITECTURE.md
git commit -m "docs: update architecture overview for firm-first"
```

---

## STEP 5: Archive Agentic Positioning Docs (10 min)

**CHECK IF ALREADY ARCHIVED**: Look in `archive/owner-first/`

**IF NOT**, archive these files:

```bash
# These should already be in archive/owner-first/ but verify:
ls -la archive/owner-first/

# If any are missing:
cp docs/BUILD_PLAN_AGENTIC_V5.1.md archive/owner-first/ 2>/dev/null || echo "Already archived"
cp docs/product/AGENTIC_POSITIONING_STRATEGY.md archive/owner-first/ 2>/dev/null || echo "Already archived"

# Commit if anything moved
git add archive/owner-first/
git commit -m "docs: ensure all agentic docs archived"
```

---

## STEP 6: Update README or Index (if exists) (10 min)

**IF** there's a `docs/README.md` or `docs/index.md`:

**ADD THIS SECTION** at the top:

```markdown
## Current Strategy (2025-09-30)

**PRIMARY ICP**: CAS accounting firms serving 20-100 clients
**PRICING**: $50/mo per client
**PRIORITY**: Data completeness > Agentic features

**Key Documents**:
- [Firm-First Build Plan](BUILD_PLAN_FIRM_FIRST_V6.0.md) - Current roadmap
- [Strategic Pivot Analysis](STRATEGIC_PIVOT_CAS_FIRST.md) - Why we pivoted
- [ADR-003: Multi-Tenancy](architecture/ADR-003-multi-tenancy-strategy.md) - Firm-first architecture

**Archived (Owner-First)**:
- [archive/owner-first/](../archive/owner-first/) - All agentic positioning docs
```

---

## STEP 7: Final Verification (10 min)

**RUN THESE CHECKS**:

```bash
# 1. Verify old build plan is archived
test ! -f docs/build_plan_v5.md && echo "✅ Old build plan archived" || echo "❌ Old build plan still exists"

# 2. Check for "owner-first" or "QBO App Store" in active docs
grep -r "QBO App Store" docs/ --exclude-dir=archive 2>/dev/null | head -5

# 3. Check for "agentic" mentions in active docs (should be minimal)
grep -r "agentic" docs/ --exclude-dir=archive --exclude="AGENTIC_ALIGNMENT_COMPLETE.md" 2>/dev/null | wc -l

# 4. Verify firm-first docs exist
test -f docs/BUILD_PLAN_FIRM_FIRST_V6.0.md && echo "✅ Firm-first build plan exists"
test -f zzz_fix_backlog/working/F01_FIRM_FIRST_FOUNDATION.md && echo "✅ Implementation task exists"
```

**EXPECTED OUTPUT**:
```
✅ Old build plan archived
✅ Firm-first build plan exists
✅ Implementation task exists
```

---

## STEP 8: Push Changes (5 min)

```bash
# Review what changed
git status

# Push to feat/firm-first branch
git push origin feat/firm-first
```

---

## SUCCESS CRITERIA

After completing all steps:

✅ Old build_plan_v5.md is in `archive/owner-first/`  
✅ Product vision doc leads with CAS firms  
✅ ADRs mention firm-first context  
✅ No active docs promote "owner-first" or "QBO App Store" as primary  
✅ All agentic docs are archived  
✅ Changes pushed to `feat/firm-first` branch  

---

## IF YOU GET STUCK

**Problem**: Can't find a file or section  
**Solution**: Skip it and note in commit message

**Problem**: Not sure if something should be updated  
**Solution**: If it mentions "owner", "self-serve", or "QBO App Store", add firm-first context

**Problem**: Merge conflict  
**Solution**: Stop and report - don't resolve conflicts

---

## ESTIMATED TIME

- Step 1: 10 min
- Step 2: 30 min
- Step 3: 30 min
- Step 4: 20 min
- Step 5: 10 min
- Step 6: 10 min
- Step 7: 10 min
- Step 8: 5 min

**Total: ~2 hours**

---

**Status**: Ready for auto mode execution  
**Branch**: `feat/firm-first`  
**No thinking required - just follow the steps!**

