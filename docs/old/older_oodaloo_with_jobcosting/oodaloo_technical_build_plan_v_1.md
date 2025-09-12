# Oodaloo — Technical Build Plan (v1.0)

> **Purpose:** A copy‑pasteable engineering plan that encodes the automation‑first profit loop into shippable components. This document is intentionally compact, unambiguous, and implementation‑ready. It aligns with the Unified Strategy/Summary and emphasizes **automation assist → human approval**.

---

## 0) Scope & Non‑Goals

**In‑scope (v1):**
- Bank/processor **payout unbundling** → cash‑verified AR ageing
- **Top‑N AR planner** with runway impact
- **Expense auto‑tagging** → job/vendor mapping → **cash job GM**
- **Exceptions Tray** (dispatcher workflow) & **Friday Digest** (owner)
- **Criterion‑based benchmarking** (vertical × stage recipes, owner‑set targets)
- **QBD‑style reporting UX** (persistent context, fast drilldowns)
- **Data portability** (full exports; schedule + webhooks)
- **Light accounting bridge** (optional summary JE push later)

**Out‑of‑scope (v1):** payroll processing, bill pay, CRM/dispatch, quoting, client comms, complex accrual accounting.

---

## 1) Architecture Overview

**Services (micro‑mono acceptable for v1):**
1. **Ingestor** (bank/cards, processors, Jobber) – webhook & pollers, dedupe, normalization
2. **Matcher** (payout unbundler, expense suggestor, AR prioritizer)
3. **Ledger** (canonical facts, linkage to jobs/vendors)
4. **Exceptions** (rules, queue, state machine)
5. **Reporting** (QBD‑style reports, cache, materializations)
6. **Benchmarks** (recipes registry, calc engine)
7. **Exports** (packager, scheduler, delivery)
8. **API Gateway** (REST + authz)
9. **Notifier** (email digests, webhooks)

**Data flow:**
Plaid/Processor/Jobber → Ingestor → Normalize → Ledger → Matcher → (write matches & links) → Exceptions (unresolved) → Reporting/Benchmarks → Exports/Notifier.

**Storage:** Postgres (OLTP), S3/Blob (export packs), Redis (queues/caches), Columnar store (Parquet/Arrow inside S3) for report caching.

**Authn/z:** OAuth (Jobber), OAuth (QBO later), Plaid Link; JWT for app. RBAC: **Owner, Dispatcher, Bookkeeper, Viewer**.

---

## 2) Canonical Data Model (compact)

```sql
-- Companies & users
CREATE TABLE company (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  vertical TEXT CHECK (vertical IN ('hvac','plumbing','cleaning','lawn','pool','other')),
  stage   TEXT CHECK (stage IN ('growth','mature')),
  timezone TEXT NOT NULL DEFAULT 'America/New_York',
  created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE app_user (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL REFERENCES company(id),
  email TEXT NOT NULL,
  role TEXT CHECK (role IN ('OWNER','DISPATCHER','BOOKKEEPER','VIEWER')),
  created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- External connections
CREATE TABLE connection (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL REFERENCES company(id),
  kind TEXT CHECK (kind IN ('PLAID','JOBBER','QBO','WAVE','STRIPE','SQUARE')),
  status TEXT CHECK (status IN ('ACTIVE','DISCONNECTED')),
  meta JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- Canonical ledger facts (cash‑basis primary, accrual optional)
CREATE TABLE fact_transaction (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL REFERENCES company(id),
  occurred_at TIMESTAMP NOT NULL,         -- cash date
  booked_at TIMESTAMP,                    -- optional accrual date
  source TEXT CHECK (source IN ('BANK','CARD','PROCESSOR','JOBBER','QBO','WAVE')),
  source_ref TEXT,                        -- payout id, invoice id, txn id
  amount_cents BIGINT NOT NULL,           -- signed; fees negative
  currency CHAR(3) NOT NULL DEFAULT 'USD',
  vendor_id UUID,
  customer_id UUID,
  job_id UUID,
  coa_category_id UUID,
  tag_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- Jobber mirrors (read‑only cache)
CREATE TABLE job (
  id UUID PRIMARY KEY,                    -- app uuid
  company_id UUID NOT NULL,
  jobber_id TEXT NOT NULL,
  customer_id UUID,
  name TEXT,
  status TEXT,
  started_on DATE,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE invoice (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL,
  jobber_id TEXT NOT NULL,
  job_id UUID,
  issue_date DATE,
  due_date DATE,
  total_cents BIGINT,
  status TEXT CHECK (status IN ('OPEN','PAID','VOID','PARTIAL')),
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE payout (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL,
  processor TEXT CHECK (processor IN ('JOBBERPAY','STRIPE','SQUARE')),
  payout_id TEXT,
  payout_date DATE,
  net_cents BIGINT NOT NULL,
  gross_cents BIGINT,
  fee_cents BIGINT,
  created_at TIMESTAMP DEFAULT now()
);

-- Matching join tables
CREATE TABLE payout_item (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL,
  payout_id UUID NOT NULL REFERENCES payout(id),
  invoice_id UUID,
  gross_cents BIGINT NOT NULL,
  fee_cents BIGINT NOT NULL DEFAULT 0,
  refund_cents BIGINT NOT NULL DEFAULT 0,
  source_ref TEXT
);

CREATE TABLE exception (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL,
  code TEXT,                              -- E001..E00N
  severity TEXT CHECK (severity IN ('low','med','high')),
  status TEXT CHECK (status IN ('open','ack','resolved')) DEFAULT 'open',
  context JSONB NOT NULL,                 -- payload for UI (txn ids, suggestions)
  created_at TIMESTAMP DEFAULT now(),
  resolved_at TIMESTAMP
);

CREATE TABLE rule (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL,
  code TEXT,
  condition_json JSONB NOT NULL,
  action_json JSONB NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT now()
);

-- Benchmarking registry
CREATE TABLE dim_metric (
  id UUID PRIMARY KEY,
  key TEXT UNIQUE NOT NULL,               -- 'ad_spend_pct','labor_direct_pct','gpm','net_margin'
  name TEXT NOT NULL,
  formula TEXT NOT NULL                   -- DSL expression
);

CREATE TABLE benchmark_recipe (
  id UUID PRIMARY KEY,
  vertical TEXT, stage TEXT,
  metric_key TEXT REFERENCES dim_metric(key),
  target_min NUMERIC, target_max NUMERIC, target_ideal NUMERIC,
  source TEXT
);

CREATE TABLE company_target_override (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL,
  metric_key TEXT NOT NULL,
  target_min NUMERIC, target_max NUMERIC, target_ideal NUMERIC,
  reason TEXT, created_at TIMESTAMP DEFAULT now()
);

-- Reports & caching
CREATE TABLE dim_report_definition (
  id UUID PRIMARY KEY,
  company_id UUID,
  name TEXT,
  spec_json JSONB NOT NULL,
  created_by UUID,
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE rpt_execution (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL,
  report_id UUID,
  spec_hash CHAR(64),
  rowcount INT,
  executed_at TIMESTAMP,
  duration_ms INT,
  result_uri TEXT                         -- s3://.../arrow.parquet
);
```

---

## 3) External Integrations (minimal spec)

**Plaid:**
- Products: Transactions, Auth, Webhooks (`TRANSACTIONS_REMOVED/UPDATED`)
- Store Plaid `account_id` → `company_id` mapping; enrich with merchant names, MCC
- Poll daily; ingest webhooks in real time; dedupe by `transaction_id`

**Jobber:**
- Scopes: read jobs, invoices, clients, payments, timesheets; payouts (via JobberPay if exposed)
- Rate limit & backoff; nightly full sync + hourly delta
- Mirror `jobber_id` to internal ids

**Processors (Stripe/Square/JobberPay):**
- Payouts & balance transactions (gross, fee, refund, settlement times)
- Join on payout IDs when present; fallback to date/window heuristics

**QBO/Wave (optional later):**
- OAuth2; read COA/vendors/customers; write monthly summary JEs (feature‑flag)

---

## 4) Core Algorithms (pseudocode)

### 4.1 Payout Unbundling (net deposit → invoices + fees)
```python
def unbundle_payout(payout, items, tolerance=50):  # cents
    # 1) direct grouping if processor provides payout_id on items
    direct = [it for it in items if it.payout_id == payout.id]
    if abs(sum(it.gross - it.fee - it.refund for it in direct) - payout.net_cents) <= tolerance:
        return direct, []

    # 2) greedy subset by descending gross
    target = payout.net_cents
    chosen, rest = [], sorted(items, key=lambda x: x.gross, reverse=True)
    for it in rest:
        value = it.gross - it.fee - it.refund
        if value <= target + tolerance:
            chosen.append(it); target -= value
        if abs(target) <= tolerance: break

    # 3) residual handling → exception
    if abs(target) > tolerance:
        return chosen, [{"code":"E001","residual":target,"payout":payout.id}]
    return chosen, []
```

### 4.2 Expense Auto‑Tagging (suggest job/vendor)
```python
def suggest_tags(txn, vendor_catalog, job_hints):
    score = 0; sugg = {"job_id": None, "vendor_id": None, "confidence": 0}
    v = fuzzy_vendor_match(txn.merchant, vendor_catalog)         # text/MCC/amount cadence
    if v: sugg["vendor_id"], score = v.id, score + v.score
    j = likely_job_for_txn(txn, job_hints)                       # time/window, location, tech, amount
    if j: sugg["job_id"], score = j.id, score + j.score
    sugg["confidence"] = min(100, score)
    return sugg
```

100%—those two are the engine. Here’s a tight, implementation-ready spec for each, with signals, scoring, data structures, and pseudocode. Drop-in friendly to your current `suggest_tags` flow.

---

# `fuzzy_vendor_match(txn.merchant, vendor_catalog)`

## Goal

Resolve a messy merchant descriptor (e.g., `SQ*HOME DEPOT 1234`, `AMZN Mktp US*12AB3`) to a **canonical vendor** with a confidence score and reasons.

## Inputs

* `merchant_raw`: free-text descriptor from bank/processor
* `mcc`: Merchant Category Code (if available)
* `amount_cents`, `occurred_at`, optional `merchant_latlon`
* `vendor_catalog` (per company + global):

  ```json
  {
    "vendor_id": "...",
    "name": "Home Depot",
    "aliases": ["HOMEDPOT", "HOME DEPOT", "THE HOME DEPOT", "HDEPOT"],
    "patterns": ["HOM(E)? DEP(OT)?\\s*#?\\d{3,4}", "HD\\s*\\d{3,4}"],
    "mccs": [5200, 5211],
    "risk_flags": ["personal_risk": false, "split_often": true],
    "geo": [{"lat":..,"lon":..,"radius_m":5000}],
    "amount_cadence": {"median": 18500, "mad": 9000}
  }
  ```

## Feature pipeline

1. **Normalize** `merchant_raw` → `merchant_norm`

   * Unicode NFKC, casefold, strip punctuation, collapse spaces.
   * Remove common junk tokens: `SQ*`, `PAYMENT*`, `WWW.`, `INC`, `LLC`, `#1234` store as `store_num`.
2. **String similarity (text)**

   * Token/BM25 score against `name + aliases`.
   * Char 3-gram cosine/Jaro-Winkler; keep top-k.
3. **Pattern/regex hits**

   * Regex from `patterns` extract `store_num`/city.
4. **MCC prior**

   * If `mcc ∈ vendor.mccs`, add weight; else slight penalty.
5. **Geo proximity (if available)**

   * Haversine distance to any `vendor.geo` location; score if < radius.
6. **Amount cadence**

   * Z-score vs vendor’s historical median/MAD; penalize outliers.
7. **Company memory**

   * If this company previously approved this merchant → vendor, big boost.

## Scoring (to 0–100)

```
score = w_text*text_sim + w_regex*pattern_hit + w_mcc*mcc_match +
        w_geo*geo_match + w_amount*amount_fit + w_memory*memory_hit
# Typical weights: 35/15/10/10/10/20; clamp 0–100
```

## Output

```python
VendorMatch(vendor_id, score, reasons=[...])
```

* **Autoconfirm** if `score ≥ 90`
* **Needs review** if `60–89`
* **No match** if `< 60`

## Pseudocode

```python
def fuzzy_vendor_match(merchant_raw, mcc, amount_cents, latlon, catalog, hist):
    m = normalize(merchant_raw)                      # NFKC, casefold, strip
    cands = text_knn(m, catalog)                     # BM25+trigram top-K
    best = None
    for v in cands:
        s_text   = jw(m, best_name_or_alias(v))
        s_regex  = 1.0 if regex_hit(m, v.patterns) else 0
        s_mcc    = 1.0 if mcc and mcc in v.mccs else 0
        s_geo    = geo_score(latlon, v.geo)
        s_amt    = cadence_score(amount_cents, v.amount_cadence)
        s_mem    = 1.0 if hist.approved(v.vendor_id, m) else 0
        score = 35*s_text + 15*s_regex + 10*s_mcc + 10*s_geo + 10*s_amt + 20*s_mem
        if not best or score > best.score:
            best = VendorMatch(v.vendor_id, min(100, round(score/1.0)), reasons=explain(...))
    return best if best.score >= 60 else None
```

---

# `likely_job_for_txn(txn, job_hints)`

## Goal

Given a transaction and the company’s active/nearby jobs, suggest the **most likely job** (or `None` if OPEX) with confidence and reasons.

## Inputs

* `txn`: { occurred\_at, amount\_cents, merchant\_norm, mcc, latlon?, card\_last4?, memo? }
* `job_hints`: list of candidate jobs with context:

  ```json
  {
    "job_id": "...", "status": "scheduled|in_progress|invoiced|closed",
    "window_start": "...", "window_end": "...",
    "client_latlon": [lat,lon],
    "assigned_tech_ids": ["u1","u2"],
    "po_numbers": ["PO-74218"],
    "job_type": "install|service|maintenance",
    "expected_material_vendors": ["Home Depot","Ferguson"],
    "budget_range_cents": [min,max]
  }
  ```
* Optional: tech/device pings, cardholder map (who carries which card)

## Signals

1. **Time proximity**: txn time within job window ± buffer (e.g., −3h to +6h).
2. **Geo proximity**: merchant/store location or txn latlon within X miles of client address.
3. **Assignment linkage**: cardholder/tech match; or tech device ping near merchant at txn time.
4. **Vendor fit**: resolved vendor ∈ job’s `expected_material_vendors` (by trade).
5. **Amount fit**: within job’s `budget_range` or typical spend for `job_type`.
6. **Lifecycle fit**: jobs `in_progress` > `scheduled` >> `invoiced/closed`.
7. **PO/Reference clue**: PO or job# substring in memo/receipt.
8. **Company memory**: this merchant was previously tagged to this job type for this company.

## Scoring (to 0–100 per job)

```
score =  w_time*time_score + w_geo*geo_score + w_assign*assign_score +
         w_vendor*vendor_fit + w_amt*amount_fit + w_stage*stage_prior +
         w_ref*ref_hit + w_mem*memory_hit
# Typical weights: 15/15/15/15/10/10/10/10
```

Tie-breakers: higher `stage_prior`, closer geo, then higher vendor fit.

## Output

```python
JobMatch(job_id, score, reasons=[...])
```

* **Autoconfirm** if `≥ 90`
* **Needs review** `60–89` (show top 3)
* **No job** `< 60` → suggest OPEX

## Pseudocode

```python
def likely_job_for_txn(txn, job_hints, vendor_match=None, telemetry=None):
    best = None
    for j in job_hints:
        s_time  = time_window_score(txn.occurred_at, j.window_start, j.window_end, buffer=(-3, +6))
        s_geo   = geo_prox_score(txn.latlon, j.client_latlon) or store_to_site_score(vendor_match, j)
        s_asgn  = assignment_score(txn.card_last4, j.assigned_tech_ids, telemetry)
        s_vend  = 1.0 if vendor_match and vendor_match.vendor_id in j.expected_material_vendors else 0
        s_amt   = amount_fit_score(txn.amount_cents, j.budget_range_cents, j.job_type)
        s_stage = stage_prior(j.status)
        s_ref   = ref_hit_score(txn.memo, j.po_numbers, j.job_id)
        s_mem   = memory_hit(company=…, vendor=vendor_match, job_type=j.job_type)
        score = 15*s_time + 15*s_geo + 15*s_asgn + 15*s_vend + 10*s_amt + 10*s_stage + 10*s_ref + 10*s_mem
        if not best or score > best.score:
            best = JobMatch(j.job_id, min(100, round(score)), reasons=explain(...))
    return best if best and best.score >= 60 else None
```

---

## Confidence & actions (shared)

* **≥ 90** → auto-assign; log reason codes; surface “undo”.
* **60–89** → show top 3 candidates + “OPEX” in Exceptions Tray; single-key choose/split.
* **< 60** → leave unassigned; create E002/E004-style exception if large/personal-risk vendor.

**Calibration:** Use Platt scaling or isotonic regression on historical approvals to map raw scores → calibrated probability. Maintain **per-company** weights with global fallbacks.

---

## Learning & memory

* Every approval/edit becomes a labeled example:

  * `(merchant_norm → vendor_id)` positive/negative pairs
  * `(txn → job_id|OPEX)` positive/negative pairs
* Update:

  * Alias table with newly seen patterns (`HOMEDPOT#4567` → “Home Depot”).
  * Per-company weight nudges (e.g., some firms rely on tech assignment more than geo).
  * **Blocklists/allowlists** (e.g., “Starbucks” → never job).

---

## Explainability (UI)

Show 2–4 top reasons for each auto-suggestion:

* “Matched **Home Depot** (alias ‘HOMEDPOT #1234’), MCC 5200, seen 37×.”
* “Within **1.2 mi** of job site and **+90 min** before scheduled start.”
* “Amount fits **install** pattern (median \$180, you spent \$165).”
* “Previously approved for **install jobs** 12× in last 90 days.”

---

## Performance & indexing

* **Text search:** trigram/BM25 index over `name+aliases`; cache top-k vendors per frequent tokens.
* **Embeddings (optional v2):** char-ngram embeddings + HNSW index for robustness on mangled strings.
* **Geo:** pre-bucket vendors by geohash; cheap radius filters.
* **Cadence:** store per-vendor EMA/median/MAD in Redis for quick z-scores.

---

## Data hygiene & privacy

* Normalize and hash raw descriptors for telemetry if needed; keep raw only where required to render explainers.
* Per-role redaction: viewers see vendor name, not full merchant string (configurable).

---

## Test cases to include

* `AMAZON Mktp` mixed-cart → suggest **split** or OPEX unless PO reference matches a job.
* Fee/credit reversals (negative amount) → pair to prior purchase; reduce confidence.
* Processor-generic strings (`PAYPAL *12345`) → rely on memo/PO/time/geo more heavily.
* Gas/fuel → route-day logic; typically OPEX, optionally allocate rule-based.

---

**Drop-in replacement for your stub**
If you want to wire it now without the ML bits, start with **rules + weights** and store approvals to backfill learning:

```python
v = fuzzy_vendor_match(txn.merchant, txn.mcc, txn.amount_cents, txn.latlon, vendor_catalog, history)
j = likely_job_for_txn(txn, job_hints, vendor_match=v, telemetry=tech_pings)
return {
  "vendor_id": v.vendor_id if v and v.score>=60 else None,
  "job_id": j.job_id if j and j.score>=60 else None,
  "confidence": min(100, int(0.6*v.score + 0.4*(j.score if j else 0))),
  "reasons": (v.reasons if v else []) + (j.reasons if j else [])
}
```

This gives you **automation assist now**, with a clean path to **learned weights** as approvals accrue.


### 4.3 AR Prioritization with Runway Impact
```python
def prioritize_ar(open_invoices, inflow_model, fixed_outflows, payroll_weekly):
    # score: amount * age_factor * pay_likelihood
    ranked = sorted(open_invoices, key=lambda inv: inv.amount_cents * age_factor(inv) * inv.likelihood, reverse=True)
    plan, collected = [], 0
    for inv in ranked:
        plan.append(inv); collected += inv.amount_cents
        if runway_weeks(inflow_model + collected, fixed_outflows, payroll_weekly) >= target_weeks():
            break
    delta_weeks = runway_weeks(inflow_model + collected, fixed_outflows, payroll_weekly) - runway_weeks(inflow_model, fixed_outflows, payroll_weekly)
    return plan, delta_weeks
```


### 4.4 Benchmarks Engine (metric DSL)
```python
def compute_metric(metric_key, window, env):
    expr = registry[metric_key]          # e.g., "advertising_expense / revenue"
    return safe_eval(expr, env.window(window))

def status_vs_target(company_id, metric_key, actual):
    tgt = get_target(company_id, metric_key)
    if tgt.min <= actual <= tgt.max: return "on_track"
    return "out_of_band"
```

---

## 5) Public API (REST, minimal)

```http
# Auth
POST /auth/login
POST /integrations/plaid/link/token
POST /integrations/jobber/oauth

# Ingest status
GET  /ingest/sources              # list connections + last sync

# AR & payouts
GET  /payouts?from=..&to=..
GET  /invoices?status=open
POST /ar/plan                     # returns Top‑N with runway impact

# Exceptions
GET  /exceptions?status=open
POST /exceptions/{id}/resolve     # body: { resolution, payload }
POST /rules                       # create/update exception rules

# Expenses & jobs
GET  /transactions?q=..           # search ledger
PATCH/transactions/{id}           # assign job/vendor/tags
POST /transactions/bulk           # bulk re‑tag

# Benchmarks
GET  /benchmarks?vertical=hvac&stage=mature
POST /companies/{id}/targets
GET  /companies/{id}/metrics?period=2025Q2

# Reports (QBD‑style)
POST /reports                     # create saved report (spec_json)
GET  /reports/{id}?state=<b64>
POST /reports/preview

# Exports
POST /exports                     # schedule export
GET  /exports/{id}/status
GET  /exports/{id}/download
```

---

## 6) UX Blueprints (concise)

**Exceptions Tray (Dispatcher):**
- Default sort: severity desc → newest
- Row hotkeys: `o` open drawer, `y` confirm, `s` split, `a` assign job, `i` ignore
- SLA badges ("due today", "2d old"); bulk actions

**Friday Digest (Owner):**
- Section 1: **Runway** (weeks → change vs last week)
- Section 2: **Top‑N AR** (3–7 invoices, sum, +Δweeks)
- Section 3: **Job winners/losers** (cash GM; top 3 each)
- Section 4: **Data health** (auto‑match %, exceptions backlog)

**Reporting (QBD‑style):**
- Persistent filters; side drawer edit; instant recompute
- Shareable URL state; keyboard nav `j/k/e/s/esc`

**Benchmarking Panel:**
- Toggle: **Peers** vs **Recipe**
- Bands (min–ideal–max), sparkline, coach notes
- “Lock target” per metric

---

## 7) Telemetry, KPIs, SLAs

**Product KPIs:** auto‑match % (payouts/expenses), exceptions cleared <10 min/week, runway Δ after Top‑N, time‑to‑reconciliation, ghost‑AR eliminated.

**SLOs:**
- Ingest freshness: <15 min from webhook; <6h nightly full sync
- Report preview: p50 <1.5s, p95 <3s (<100k rows post‑agg)
- Export (2y, 250k txns): <5m completion + webhook

**Logs/Audit:** every match/split/override with actor, before/after, reason.

---

## 8) Security & Compliance
- **Least privilege** OAuth scopes; read‑only banks; token KMS‑encrypted; rotation 90d
- PII minimization; redact in exports; per‑role data scopes
- **Data retention:** raw ingest 24 months (configurable); aggregated forever; hard delete on disconnect

---

## 9) Rollout & Feature Flags
- **Phase A (AR Core):** ingest, unbundling, AR plan, digest
- **Phase B (Job Costing):** expense auto‑tag, labor burden, cash job GM
- **Phase C (Benchmarks/Reporting):** recipes, panel, QBD reports
- **Phase D (AP Assist & Exports):** duplicate/fee alerts; full export packs
- **Phase E (GL Push – optional):** summary JE write‑back

Feature flags per module; cohort‑gated pilots by vertical/stage.

---

## 10) Testing Strategy (skeletal)
- **Unit:** unbundler edge cases (partials, splits, refunds), expense suggestor scoring, metric DSL
- **Property‑based:** payout coverage vs net deposit tolerances
- **Contract:** Jobber/Plaid adapters; rate‑limit/backoff
- **Perf:** report cache hits; export at 250k txns
- **UX tests:** keyboard flows; no filter loss across 100 edits

---

## 11) Edge Cases (enumerated)
- Net deposit mismatch ±$0.50 → E001 residual
- Invoice paid off‑platform (check/cash) → bank maps but platform open → E006 phantom AR
- Processor fee posted separate day → inter‑day grouping window
- Refunds/chargebacks in later payout → reversal logic
- Personal spend from business card → E004 vendor list
- Vendor with mixed COGS/OPEX roles → split rules by amount/pattern

---

## 12) Export & Portability (spec)
```
/export_YYYY‑MM‑DDThh‑mm‑ssZ/
  manifest.json                 # datasets, row counts, hashes, schema version
  company.json                  # profile, vertical, stage, settings
  ledger_transactions.parquet
  jobs.parquet
  payouts.parquet
  ar_open.parquet
  job_profit.csv
  benchmarks_actual_vs_target.csv
  pl_statement.csv
  bs_statement.csv
  cf_statement.csv
  README.txt
```
Delivery: direct download, S3, Google Drive; webhooks on completion.

---

## 13) RBAC (minimal)
- **OWNER:** read all, approve plans, set targets, manage exports/integrations
- **DISPATCHER:** resolve exceptions, retag txns, manage AR plan
- **BOOKKEEPER:** read all, export, notes; optional JE push (later)
- **VIEWER:** read digest & reports only

---

## 14) Configuration (company‑level)
- Vertical & Stage (defaults → recipes)
- Labor burden method (timesheets vs flat %)
- Benchmarks: adopt defaults; lock overrides
- AR target runway weeks (goal)
- Exception thresholds (amounts, vendors)
- Export schedules & delivery endpoints

---

## 15) Owner‑grade Definitions
- **Runway (weeks):** (current bank balance + expected inflows − scheduled outflows) ÷ weekly payroll
- **Cash Job GM:** (invoice cash collected − direct materials − labor burden − direct fees)
- **Ghost AR:** invoice still open in platform but already satisfied in bank

---

## 16) Success Criteria (v1)
- ≥90% payout value auto‑matched within tolerance; ≤10% txn volume in exceptions
- Dispatcher median weekly time ≤10 minutes; owner digest NPS ≥ 50
- Runway deltas attributable to Top‑N AR in first 2 weeks of use
- Benchmarks panel live with defaults for HVAC/Plumbing/Cleaning/Lawn/Pool
- QBD‑style report retains context through 100 consecutive edits/drilldowns

---

**End of Build Plan v1.0**

