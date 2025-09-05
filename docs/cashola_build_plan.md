
# Cashola — Weekly Cash Call Platform

### Product, Architecture & Technical Specification *(v1.2.1, consolidated for Grok/Cursor — SQLite-first)*

> **Ground truth:** This document preserves the original architecture/diagram and performs **surgical inserts** only where they tighten the MVP and delivery plan. It integrates the MVP/Post-MVP/Leave-Out guidance and keeps the identity graph + consolidation model at the core. SQL is **SQLite-friendly** for heavy dev; PostgreSQL hardening can follow.

---

## 0) What we ship (MVP, unambiguous)

**Owner promise:** a **bank-truth weekly cash call**: cash on hand, expected AR this week, must-pay AP (incl. payroll), runway, and a ranked **collect vs pay/delay** plan — with a tiny **Exceptions Tray** that clears in **<10 min/week**.

**MVP scope (must-have for pilots):**

* **AR unbundling** (bank/processor payouts → invoices + fees, no double counting).
* **Reconciliation event graph** (bank ↔ processor ↔ ops) with idempotent ingest + dedup.
* **Cash Decision Model (CDM) + Policy Engine** (normalize inflows/outflows; **MUST\_PAY** vs **CAN\_DELAY** labels).
* **Exceptions Tray** (unified; AR ambiguity, unmapped cash, timing mismatches).
* **Friday Digest** (owner-facing: runway, collect plan, pay/delay plan, exceptions summary; **email with action deep-links**).
* **Coverage gate at onboarding:** ≥95% of inflow/outflow **by value** categorized before “auto digest” is enabled.
* **Learning loop:** 3 consistent manual assignments → **proposed rule** with preview.
* **Payroll slot (proxy)**: **bank-inferred cadence + rolling average** (detect Gusto/ADP/Paychex descriptors). If inference is weak in first 7 days, **ask** for payroll frequency and typical gross during onboarding (stored as proxy).
* **Helper levers (minimal)**:
  * **AR nudge**: one-click **send reminder in Jobber** from the digest.
  * **AP deferral toggle**: mark vendor as **CAN\_DELAY**; feeds next week’s plan (**Δrunway** recalculated).
* **Debt hygiene (light)**: **credit-card balance** (when available via Plaid) and **net LOC activity trend** (month-to-date).

**KPIs/SLOs:**

* **% deposits reconciled ≥95%**
* **Automation ≥70% by week 4**
* **Exceptions <10 min/week**
* **Runway error < ±0.3 weeks** vs human baseline

**Post-MVP (add once pilots are stable):**

* **AP Assist (full)**: policy-driven delay suggestions & simple simulation; optional push to pay rails (Relay/BILL).
* **Payroll integrations (precision)**: **Gusto/ADP** for exact gross/net and schedule.
* **In-transit payout view** (Stripe/JobberPay/Square unsettled funds).
* **Export: Weekly posting pack (CSV/Excel)** for controllers (no direct QBO write-back yet).
* **Buildium connector** (first non-service-pro vertical).
* **COA → CDM mapping (read-only QBO)** for controller firms; logic stays **CDM-first**.
* **Portfolio dashboard (controller view, lite)** *(moved to separate Post-MVP spec).*

**Leave out (for now):** job costing/spend-to-job, benchmarking/recipes, heavy static reports, accrual/close overlays, offline mode, Wave integration, deep ops write-backs, job closure velocity.

---

## 1) System overview

```

Connectors (Plaid, Stripe/JobberPay/Square, Jobber/HCP/Buildium)
   │
   ▼
Ingestor ──► Raw Event Store ──► Identity + Dedup ──► Event Graph
                                    │                    │
                                    ▼                    ▼
                              Reconciliation       Policy Engine (CDM)
                                    │                    │
                                    └────► Cash Ledger ◄─┘
                                                    │
                                                    ▼
                                       Cash Engine (Runway, AR/AP Plans)
                                                    │
                                                    ▼
                                   Exceptions Tray & Friday Digest
```

**Key idea:** we **don’t** let duplicate sources double count. We build a **small event graph** tying bank deposits ↔ processor payouts ↔ balance transactions ↔ ops invoices/payments, then **consolidate** that graph into a **cash ledger** consumed by CDM and the digest.

---

## 2) Connectors (clean contracts)

### 2.1 Bank & Processor

* **Plaid.Transaction** (bank/card): `posted_at, amount, merchant, mcc, account_id, transaction_id` (idempotency key).
* **Stripe/JobberPay/Square**:

  * **Payout**: `id, net, gross, fee, arrival_date, status, destination_bank_mask`.
  * **Balance Transaction**: `id, type(charge/refund/fee/payout), amount, created, fee_details[], source_id`.
  * **Charge/Payment**: `id, amount, created, metadata(invoice_id?)`.

**Precedence (processor vs bank):**

* **Composition truth** (invoice/fees/refunds) → **processor**.
* **Settlement truth** (cash actually hit) → **bank**.
* We **link** them and **count once** (details below).

### 2.2 Ops CRM/ERP (swappable)

```python
class OpsConnector:
    def get_invoices(self, since): ...   # id, customer, issued_at, due_at, amount, status
    def get_payments(self, since): ...   # id, amount, paid_at, processor_ref?, invoice_id?
    def get_clients(self): ...
```

Start: **Jobber**. Later: **HCP**, **ST**, **Buildium/ResMan/RentManager** via the same interface.

### 2.3 (Later) Accounting (QBO/Xero)

* Read-only **Accounts, Vendors, Open AR/AP**.
* Onboarding **COA→CDM** mapping screen (labels only; CDM remains source of truth).

---

## 3) Data model (purpose-built, compact, **SQLite-friendly**)

> Types are pragmatic for SQLite (TEXT/INTEGER/REAL); enums are TEXT + `CHECK` constraints. Foreign keys are included but can be relaxed in early dev if desired. All tables are **append-only** where noted.

### 3.1 Raw events (append-only, idempotent)

```sql
CREATE TABLE IF NOT EXISTS raw_event (
  id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  src TEXT NOT NULL,                 -- 'PLAID','STRIPE','JOBBERPAY','SQUARE','JOBBER','HCP','BUILD'
  kind TEXT NOT NULL,                -- 'BANK_TXN','PAYOUT','BAL_TXN','OPS_PAYMENT','OPS_INVOICE'
  external_id TEXT NOT NULL,
  occurred_at TEXT NOT NULL,         -- ISO8601
  amount_cents INTEGER NOT NULL,     -- signed; bank debits negative, credits positive
  currency TEXT DEFAULT 'USD',
  account_ref TEXT,
  counterparty TEXT,
  mcc TEXT,
  parent_external_id TEXT,
  raw_json TEXT NOT NULL,
  UNIQUE (company_id, src, kind, external_id)
);
```

### 3.2 Identity & linkage (event graph)

```sql
CREATE TABLE IF NOT EXISTS identity (
  id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  canonical_kind TEXT NOT NULL,      -- 'SETTLEMENT','PAYOUT','CHARGE','FEE','REFUND','INVOICE','PAYMENT'
  UNIQUE(company_id, fingerprint)
);

CREATE TABLE IF NOT EXISTS identity_link (
  id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  identity_id TEXT NOT NULL,
  raw_event_id TEXT NOT NULL,
  confidence REAL NOT NULL,
  reason TEXT NOT NULL,
  FOREIGN KEY(identity_id) REFERENCES identity(id),
  FOREIGN KEY(raw_event_id) REFERENCES raw_event(id)
);

CREATE TABLE IF NOT EXISTS identity_edge (
  id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  from_identity TEXT NOT NULL,
  to_identity TEXT NOT NULL,
  kind TEXT NOT NULL,                -- 'SETTLES','COMPOSED_OF','APPLIES_TO'
  weight REAL DEFAULT 1.0,
  FOREIGN KEY(from_identity) REFERENCES identity(id),
  FOREIGN KEY(to_identity) REFERENCES identity(id)
);
```

### 3.3 Cash Ledger (post-reconciliation)

```sql
CREATE TABLE IF NOT EXISTS cash_ledger (
  id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  identity_id TEXT NOT NULL,
  posted_at TEXT NOT NULL,
  direction TEXT NOT NULL CHECK(direction IN ('INFLOW','OUTFLOW')),
  amount_cents INTEGER NOT NULL,
  currency TEXT DEFAULT 'USD',
  cdm_key TEXT,                      -- set by Policy Engine
  policy TEXT,                       -- 'MUST_PAY','CAN_DELAY','DISCRETIONARY'
  confidence REAL NOT NULL DEFAULT 1.0,
  provenance_json TEXT NOT NULL,
  FOREIGN KEY(identity_id) REFERENCES identity(id)
);
```

### 3.4 CDM rules & exceptions (versioned)

```sql
CREATE TABLE IF NOT EXISTS rule_version (
  id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cdm_rule (
  id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  version_id TEXT NOT NULL,
  scope TEXT NOT NULL,               -- 'VENDOR','MCC','REGEX','ACCOUNT','SOURCE_KIND'
  predicate_json TEXT NOT NULL,      -- e.g. {"descriptor_regex":"..."} or {"mcc_in":["5541"]}
  outcome_cdm_key TEXT NOT NULL,
  outcome_policy TEXT,               -- 'MUST_PAY','CAN_DELAY','DISCRETIONARY'
  priority INTEGER NOT NULL DEFAULT 100,
  active INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY(version_id) REFERENCES rule_version(id)
);

CREATE TABLE IF NOT EXISTS exception (
  id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  kind TEXT NOT NULL,                -- 'AR_AMBIG','UNMAPPED','TIMING','NO_MATCH','GHOST_AR'
  status TEXT NOT NULL DEFAULT 'open',
  context_json TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  resolved_at TEXT
);
```

> **Note:** If running with foreign keys off during early dev, keep IDs consistent and add periodic integrity checks.

---

## 4) Identity + de-dup: **the hard part solved**

### 4.1 Canonical fingerprints

We compute a **fingerprint** per raw event so the same real-world event from different sources collapses to one identity.

* **BANK\_TXN (Plaid)** → `fp = sha256("SETTLEMENT", bank_account_id, abs(amount), normalize_date(posted_at), merchant_norm)`
* **PAYOUT (Stripe/Square/JobberPay)** → `fp = sha256("PAYOUT", provider, payout_id)`
* **BAL\_TXN type=payout** → same as above (links to Payout)
* **BAL\_TXN type=charge|refund|fee** → `fp = sha256(type, provider, balance_txn_id)`
* **OPS\_PAYMENT** → `fp = sha256("PAYMENT", ops_provider, payment_id)`
* **OPS\_INVOICE** → `fp = sha256("INVOICE", ops_provider, invoice_id)`

**Why this works:** processor IDs are stable; bank txns aren’t, so we build a **settlement fingerprint** that tolerates description variance but locks on amount/date/account.

### 4.2 Linking algorithm (bank ↔ payout ↔ charges)

1. **Payout→Settlement (processor→bank)**

* Candidate bank credits within **arrival\_date ± 2d** and **|amount − net| ≤ tolerance (≤\$1)**.
* If **1** candidate → link with confidence 1.0 (`SETTLES`).
* If **>1** → choose nearest date, if tie then descriptor similarity; else open `AR_AMBIG` exception.

2. **Charge/Refund/Fee→Payout (composition)**

* Use `balance_txn.payout` or `payout_id` from processor → `COMPOSED_OF` edge.
* If missing, window by date + provider account; sum to net; ambiguous → exception.

3. **Ops Payment→Charge**

* Prefer explicit `processor_ref` metadata; else **amount + ±24h + descriptor/customer** similarity; ambiguous → exception.

4. **Invoice→Payment (ops)**

* Use native ops linkage. If ops shows invoice **open** but processor shows paid (off-platform), create **`GHOST_AR`**.

We store **links** as `identity_link` and **edges** as `identity_edge` with reasons + confidences. Downstream logic uses **identities**, not raw events.

### 4.3 Consolidation → **Cash Ledger (count once)**

* If a **Payout** has a **Settlement** link, recognize **cash inflow** **once** at the **bank settlement date**, amount = **net**.

  * Composition (charges/refunds/fees) stays for explainability but **doesn’t double count cash**.
* If **processor exists** but **no settlement** yet → show **in-transit** but **exclude from cash**.
* If **Ops Payment** exists without processor/bank, treat as **non-cash** signal — exclude until confirmed.

```python
# Pseudocode
for payout in identities(kind='PAYOUT'):
    settle = edge(payout, kind='SETTLES', to='SETTLEMENT')
    if settle:
        yield ledger_row(settle.posted_at, 'INFLOW', payout.net)
    else:
        mark_in_transit(payout)

for sett in identities(kind='SETTLEMENT'):
    if not has_incoming_edge(sett, kind='SETTLES'):
        yield ledger_row(sett.posted_at, 'INFLOW' if sett.amount>0 else 'OUTFLOW', sett.amount)
```

---

## 5) AR unbundling (foundation, explainable)

When processors provide **payout composition** (best case), map **charges → invoices** via metadata/ops refs. Otherwise **infer**.

**Algorithm (fallback):**

1. Candidate invoice set for a payout using:

   * Ops payments stamped within the payout window.
   * Amount proximity to charge totals (gross before fees).
   * Customer/descriptor similarity.
2. **Greedy subset / DP** to match `gross − fees` to payout **net** (tolerance in cents).
3. If unique → auto; if multiple sets match within tolerance → **`AR_AMBIG`** exception.

```python
def unbundle_payout(payout, ops_payments, fee_total, tol=50):
    targets = filter_by_time(ops_payments, window=payout.day±2)
    combos = subset_sums(targets, target=payout.net_cents + fee_total, tol=tol)
    if len(combos) == 1: return combos[0], []
    if len(combos) == 0: return [], [exc('NO_MATCH', ...)]
    return best_by_customer_confidence(combos), [exc('AR_AMBIG', candidates=len(combos))]
```

**KPI:** `% deposits reconciled ≥95%` (MVP gate).

---

## 6) CDM / Policy Engine (deterministic, versioned)

**Goal:** Map **cash\_ledger** rows to a compact **CDM** and attach **policy labels** used by the weekly plan.

**Inflows:** `CUSTOMER_RECEIPTS`, `REFUNDS_CHARGEBACKS`, `OTHER_INCOME`

**Outflows:** `PAYROLL_TOTAL`, `RENT_UTILITIES`, `INSURANCE`, `SAAS_FEES`(incl. processor fees), `DEBT_SERVICE`, `TAXES_GOVT`, `OWNER_DRAWS`, `CAPEX`, `OTHER`

**Rule precedence:** `VENDOR → MCC → REGEX(descriptor) → ACCOUNT → SOURCE_KIND → UNKNOWN`

**Learning loop:** 3 consistent manual assignments of similar UNKNOWN (same vendor/regex hit) → engine **proposes** a rule with preview; one-click **publish** bumps **rule\_version** and **re-normalize** last N days. Prior versions preserved.

---

## 7) Runway & weekly plans

**Runway (weeks):**

```
cash_today
+ E[AR due 0..7d] * collect_prob
- must_pay_AP(0..7d) - payroll(0..7d) - taxes(0..7d)
= Δweek
(roll forward weekly until balance < 0)
```

* **collect\_prob (MVP):** current=0.8, 30–60=0.4, >60=0.2; per-vertical tunable (**company-level setting**).
* **must\_pay:** payroll, insurance, rent, taxes (from CDM/AP schedule or manual proxies).
* **can\_delay:** flagged in CDM (e.g., SaaS) with **Δrunway** if delayed.
* **Payroll slot (source-agnostic):** accepts **bank-inferred proxy** (default), **Jobber labor estimate** (optional), or **Gusto/ADP** (Post-MVP) — same interface to the engine.

**Plans:**

* **AR plan:** rank invoices by `amount * age_factor * collect_prob`, showing **Δrunway** if collected.
* **AP plan:** list **MUST\_PAY** (no debate) and top **CAN\_DELAY** with **Δrunway**.
* **Payroll:** next date + amount; coverage status ("covered / short \$X").

---

## 8) Exceptions Tray (single UI that runs the show)

**Exception types (MVP):** `AR_AMBIG`, `NO_MATCH`, `UNMAPPED`, `GHOST_AR`, `TIMING`.

**Actions (keyboard-first):** Confirm candidate set, split, reassign, mark off-platform, assign CDM category/policy, create rule from decision (with preview). Every resolve logs **provenance** and is **undoable**.

**Quick actions (MVP):**

* **AR nudge** (open-invoice row) → trigger Jobber reminder.
* **Mark vendor CAN\_DELAY** N days (unmapped/recurring vendor rows) → updates policy and feeds next digest.

**UX snippets:**

* AR row: *“Stripe payout Tue 2:14p — 3 candidate invoice sets (Δ= \$12.41 fees).”* → **\[Accept #1] \[Split] \[Ignore]**
* Unmapped cash row: *“Bank debit • ‘GUSTO PAYROLL’ • \$12,410 • Wed 9:32a”* → **\[PAYROLL\_TOTAL + MUST\_PAY] \[Other…]**
* Vendor row: \*“‘ADOBE *PS’ • \$59.99 • monthly”* → **\[Mark CAN\_DELAY 7d]**
* Hotkeys: **A** accept, **S** split, **I** ignore, **C** categorize, **D** delay, **U** undo.

**Guardrails:** **Go-live gate** requires ≥95% value coverage before digest scheduling.

---

## 9) Portfolio (controller/PE mode) — **Moved to Post-MVP Deferred Spec**

*(See: “Cashola — Post-MVP Deferred Specs: Portfolio (Controller View)”)*

---

## 10) API surface (minimal, practical)

```http
# Connections & health
GET  /v1/connections
GET  /v1/ingest/status
GET  /v1/kpis  # automation %, exceptions count, deposits_reconciled %

# Exceptions
GET  /v1/exceptions?status=open
POST /v1/exceptions/{id}/resolve         # {resolution, payload}
POST /v1/rules/propose                   # create draft from decisions
POST /v1/rules/publish                   # version bump + re-norm window

# AR & payouts
GET  /v1/ar/open                         # invoices due (ops)
GET  /v1/payouts?from=&to=
POST /v1/payouts/{id}/split              # confirm/custom mapping
POST /v1/ar/{invoice_id}/remind          # trigger Jobber reminder (MVP helper)

# Vendor policy (AP deferral toggle)
POST /v1/vendors/{vendor_id}/policy      # {policy: 'MUST_PAY'|'CAN_DELAY'|'DISCRETIONARY', until?: ISO8601}

# Onboarding proxies (when inference is weak)
POST /v1/onboarding/payroll              # {frequency, typical_gross_cents}
POST /v1/onboarding/vendor               # {name, policy, cdm_key}
POST /v1/digest/send                     # immediate send / override schedule

# Plans & runway
GET  /v1/runway?horizon_weeks=4
GET  /v1/ar/plan?window=7d
GET  /v1/ap/plan?window=7d
```

---

## 11) Ingestor details (idempotent, resilient)

* **Webhooks + polling** for drift; **dedupe by (company, src, kind, external\_id)**.
* **Backfills** run in batches; each `raw_event` gets a **stable fingerprint**; re-runs are safe.
* **Ordering** independent; **graph builder** re-links late events.

---

## 12) Testing & quality bars (non-negotiables)

**Golden set (90 days)** per vertical; hand-labeled linkage & CDM assignments.

**Unit/property tests:**

* Payout→settlement matching (tolerance, multiple candidates, missing settlement).
* Subset-sum AR unbundling (unique/ambiguous/no-match).
* CDM rule precedence, versioning, deterministic re-norm.
* **Payroll inference** (descriptor detection, cadence stability, rolling avg bounds).

**Metrics gates:**

* `% deposits reconciled` **≥95%**
* **Automation rate** **≥70% by week 4**
* **Runway error** **< ±0.3 weeks**
* **Exceptions** cleared **<10 min/week**

---

## 13) Security, lineage, explainability

* **Row-level tenancy**, PII encryption at rest, token rotation 90d.
* **Provenance everywhere**: each ledger row stores **which identities, edges, rules, and versions** produced it; each suggestion shows **reason codes**.
* **Undo & time travel**: prior rule versions preserved; re-norm writes new rows with version pointers.

---

## 14) Delivery plan (6–12 weeks)

**Weeks 0–2**

* DB migrations: `raw_event`, `identity`, `identity_link/edge`, `cash_ledger`, `rule_version/cdm_rule`, `exception` (SQLite first).
* Plaid ingest (bank txns) + Jobber invoices/payments.
* Fingerprints + graph builder + **settlement matcher**.
* CDM rules v0 (vendor/mcc/regex/account/source\_kind).
* Exceptions API + minimal tray; manual digest trigger.
* **Payroll inference v0** (detect Gusto/ADP/Paychex descriptors; cadence + rolling avg; store proxy if user provides).

**Weeks 3–6**

* Stripe/JobberPay/Square ingest; payout→settlement + composition links.
* AR unbundling (subset-sum + ambiguity handling).
* Runway + AR/AP plans; onboarding coverage gate; **Friday email digest** (**with deep-links to actions**).
* **Helper levers**: AR reminder (Jobber), AP deferral toggle.
* **Debt hygiene (light)**: card balance (when available), net LOC trend.

**Weeks 6–12**

* Learning loop (rule proposals + preview); tray polish (hotkeys, undo).

* Basic AP Assist (policy labels, delay suggestions).
* Hardening (observability, retries, rate limits).

---

## 15) Edge cases (explicit handling)

* **Payout lands as two bank credits** (bank batching): match both partials → one settlement identity; sum equals net.
* **Fees settle on different day**: keep as **composition** under payout; don’t create separate outflow if netted in bank.
* **Chargeback after settlement**: new **bank debit** + **processor refund** link back; ledger posts **OUTFLOW** (CDM: `REFUNDS_CHARGEBACKS`).
* **Ops “paid” but no bank/processor**: `GHOST_AR` exception; exclude from cash until verified.
* **Cash/check off-platform**: bank credit without processor ref; show as `OTHER_INCOME` unless user links to invoices (exception flow).
* **Time-zone drift**: identities store **UTC** with **company timezone** for display; settlement matching uses local midnight windows.

---

## 16) What we *didn’t* omit (explicit reassurance)

* Explicit **Identity + Event Graph** model, **fingerprints**, and **matching precedence**.
* **Payout→settlement** and **charge/refund/fee→payout** linkage with ambiguity handling.
* **Ops→processor** matching and **ghost AR** detection.
* **Consolidation rules** ensure **no double counting** and **bank-timed cash**.
* **Deterministic, versioned CDM/Policy engine** with **learning** and **re-norm**.
* **Single tray** covering AR ambiguity, unmapped cash, timing mismatches — with **keyboard flows** and **rule creation**.

---

## 17) SQLite dev notes & migration hygiene

* Keep IDs as **TEXT (UUID strings)** for portability; timestamps as **TEXT (ISO8601)**.
* Avoid native ENUMs; use **TEXT + CHECK** or plain TEXT + rule validation.
* Enable `PRAGMA foreign_keys = ON` in test harness; if disabled for speed, run **integrity checks** during CI.
* Provide **idempotent** Alembic-like migration scripts (or simple DDL blocks) suitable for SQLite.

---

## 18) What to build **this week** (punch-list)

1. **Migrations** (SQLite) for `raw_event`, `identity/link/edge`, `cash_ledger`, `rules/exceptions`.
2. **Plaid ingest** (webhook + poll); **Jobber invoices/payments** sync.
3. **Fingerprint functions** + **settlement matcher** (bank↔payout placeholder; bank-only cash recognition initially).
4. **Graph→Ledger consolidation** (count once, at bank date).
5. **CDM rules v0** + **Exceptions API**.
6. **Runway calc** + **Digest v0** (manual trigger; email).
7. **Tray v0** (resolve `UNMAPPED` + simple `AR_AMBIG`; hotkeys + undo).
8. **Payroll inference v0** (descriptor detection, cadence, rolling avg; onboarding proxy if needed).
9. **Helper endpoints**: `POST /v1/ar/{id}/remind`, `POST /v1/vendors/{id}/policy`.
10. **Email delivery + action deep-links** in digest.
11. **Debt hygiene rollups** (card balance when available, net LOC trend).

````

---

```markdown
# Cashola — Post-MVP Deferred Specs: Portfolio (Controller View)

## Scope
A multi-client “controller/PE mode” view to manage risk and operations across a book of accounts. **Not part of MVP**; planned for Weeks 6–12 once single-client flows are stable.

## Table View (default)
Columns:

- **Client**
- **Runway (wks, ▲/▼ trend)**
- **AR due 7d**
- **Must-Pay 7d** (payroll, taxes, rent/insurance)
- **ΔRunway if AR plan done** (collect top-ranked invoices)
- **Exceptions** (open count)
- **Automation %** (normalized last 7d)
- **Status** (healthy / watch / critical)

Behaviors:

- Default sort by **lowest runway** then **highest Must-Pay 7d**.
- Row click → client drill-in (opens Exceptions Tray & last digest).
- Bulk actions: **send digests**, **open trays**, **export CSV posting pack** (once export exists).
- Filters: **status**, **runway < X**, **exceptions > N**, **automation < Y%**.

## Drill-in: Client Explainer
- **Runway chart** (last 8 weeks, next 4 projected).
- **AR plan** with Δrunway per invoice (open in client).
- **AP plan** with MUST_PAY vs CAN_DELAY and Δrunway.
- **Exceptions list** with reasons and links.
- **Provenance**: link out to identities/edges underpinning current cash ledger rows.

## Metrics & Alerts
- Alert rules:
  - **Runway < 1.5 weeks**
  - **Must-Pay 7d > Cash today**
  - **Exceptions > 10 / week**
  - **Automation < 50% after week 4**

- Delivery: email/Slack digest to controller team.

## Performance Expectations
- Load ≤ 2s for books ≤ 100 clients.
- Pagination + incremental fetch (cursor by `updated_at`).
- All figures derived from **cash ledger** (post-reconciliation) for consistency.

## Security & Tenancy
- Row-level tenancy across clients.
- Role: **portfolio_viewer** vs **client_operator**.
- Audit trail on bulk actions and digests.

````

If you want me to **apply this directly to your repo/files**, say where to put:

* `cashola_spec_v1.2.1.md` (main doc), and
* `cashola_post_mvp_portfolio.md` (deferred doc).
