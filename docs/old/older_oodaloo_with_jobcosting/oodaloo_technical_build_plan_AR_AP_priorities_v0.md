Got it. Here’s a single, unified, engineering-ready document—no appendices, no back-references—combining **AR unbundling (foundation)**, **job-aware spend routing (job costing)**, the **Exceptions Tray**, data model, algorithms, API, UX, metrics, and rollout. This is the one canonical spec to build against.

---

# Oodaloo — Profit Clarity Platform

### Product, Architecture & Technical Specification (v1.2)

## 0) Positioning & Promise

* **Jobber/HCP** = operations (scheduling, visits, invoices).
* **QuickBooks/Accountants** = accounting (historical closes, accrual).
* **Oodaloo** = **profit clarity**: **bank-truth cash in**, **job-aware cash out**, and **payroll runway**, resolved via a fast weekly **Exceptions Tray**.

**Owner’s questions:** “Did we cover payroll? Which jobs actually made money?”
**Oodaloo’s answer:** **Bank-truth profit & runway**, not modeled dashboards or month-late closes.

---

## 1) ICP & Cohort-Driven Entry

* **Recurring SMBs (cleaning, pool, lawn, janitorial).** Primary pain: **AR lumps & lag**.

  * **Entry:** **AR Unbundling + AR Planning** (collections prioritized by runway impact).
* **Installer/Trades (HVAC, plumbing, electrical, light remodel).** Primary pain: **unknown job winners/losers**.

  * **Entry:** **Job-Aware Spend Routing (job costing)**.
* **Both cohorts depend on AR unbundling** for credible profit clarity.

---

## 2) Phased Build Order (what ships first)

1. **AR Unbundling (Foundation)** — split net processor deposits → **invoices + fees**; make revenue bank-true.
2. **AR Planning** — rank **Top N to collect** with runway math; surface mismatches/off-platform payments.
3. **Job-Aware Spend Routing (Job Costing)** — map bank/card spend → jobs via schedule & user/merchant signals; resolve low-confidence items in a tiny **Exceptions Tray**.
4. **AP Assist (Optional)** — duplicates, “delay-OK,” vendor anomalies, nudges.
5. **Succession-Ready Close (Service Overlay)** — cash clarity → accrual optics (services layered atop the SaaS).

---

## 3) Core UX Primitive: the Exceptions Tray

* **Unifying mechanic** across AR & AP.
* **Targets:** ≥70% auto, ≤30% in tray, **<10 min/week** to clear.
* **Owner** receives a **Friday Digest**; **dispatcher/admin** clears a short, batchable tray.

---

## 4) Data Contracts & Sources

### 4.1 Ops Platform (Jobber/HCP)

* **Jobs**: `id, number, client, propertyAddress, status`
* **Visits**: `id, jobId, startAt, endAt, assignedUserIds` **(primary temporal anchor)**
* **Users**: `id, name, email`
* **Timesheets (optional)**: `userId, jobId, startedAt, endedAt` *(fidelity varies; never required)*
* **Invoices/Payments**: `invoiceId, total, status, payment timestamps`

### 4.2 Banking & Processors

* **Accounts/Cards**: `account_id`, `card_id?`, `last4`, `cardholder_name?`, `mask`, `type/subtype`
* **Transactions**: `txn_id`, `authorized_date`, `posted_date`, `amount`, `merchant_name`, `mcc`, `location(city/region/postal/latlon?)`, `payment_channel`, `currency`
* **Payouts/Deposits**: batch payouts, fees, invoice references where available

### 4.3 Oodaloo Directory (Onboarding)

* **Users** (synced), **Crews** (optional), **Cards discovered** from feeds
* Owner mappings: **card ↔ user/crew**, **shared?**, friendly **label**.

---

## 5) Unified Data Model (PostgreSQL)

```text
-- Tenancy
Company(id, name, timezone, created_at)

-- Directory
User(id, company_id, jobber_user_id, name, email, role)        -- OWNER | DISPATCHER
Crew(id, company_id, name)
CrewMember(id, company_id, crew_id, user_id)

-- Banking & Cards
Account(id, company_id, provider, external_account_id, name, mask, type, subtype)
Card(id, company_id, provider, external_card_id NULL, account_id, last4, label,
     shared BOOL, default_user_id NULL)
CardUserMap(id, company_id, card_id, user_id, weight FLOAT, active_bool)

-- Raw financial data
TransactionRaw(id, company_id, provider, external_txn_id,
               account_id, card_id NULL, authorized_at, posted_at,
               amount_minor, currency, merchant_name, mcc,
               location_city, location_region, location_postal, location_lat, location_lon,
               payment_channel, raw_json, dedupe_key UNIQUE, ingest_at)

ProcessorPayout(id, company_id, provider, external_payout_id, posted_at, amount_minor, currency, raw_json)
ProcessorPayoutSplit(id, company_id, payout_id, invoice_ref NULL, fee_minor NULL,
                     amount_minor, type ENUM('INVOICE','FEE','OTHER'))

-- Ops (Jobber)
JobberJob(id, company_id, jobber_job_id, job_number, client_name, property_address, status)
JobberVisit(id, company_id, jobber_visit_id, job_id, starts_at, ends_at)
JobberVisitAssignment(id, company_id, visit_id, jobber_user_id)
JobberTimesheet(id, company_id, jobber_ts_id, jobber_user_id, jobber_job_id, started_at, ended_at)

-- Matching (AP/job costing)
MatchCandidate(id, company_id, transaction_id, job_id, visit_id NULL, candidate_score FLOAT, candidate_reason JSONB)
MatchDecision(id, company_id, transaction_id,
              decision_type ENUM('AUTO','USER','ASK_CREW','NO_JOB','OVERHEAD','INVENTORY'),
              job_id NULL, visit_id NULL, confidence FLOAT, decided_by_user_id NULL, decided_at, provenance JSONB)
JobAssignment(id, company_id, transaction_id, job_id, visit_id NULL,
              status ENUM('ASSIGNED','REVERTED'), created_at)

-- Learning & Audit
RuleSignal(id, company_id, signal_hash UNIQUE, count, last_seen_at,
           last_outcome ENUM('JOB','OVERHEAD','INVENTORY'), decay FLOAT)
AuditLog(id, company_id, actor_type ENUM('SYSTEM','USER','CREW_LINK'),
         actor_id NULL, action, payload JSONB, created_at)
```

**Notes**

* `TransactionRaw.dedupe_key` = idempotent ingest.
* `ProcessorPayout*` enables AR unbundling (bank-truth revenue).
* `MatchDecision` is canonical for expense→job mapping. **No write-back to Jobber** in this phase; Oodaloo is the source of truth.

---

## 6) AR Unbundling (Foundation)

### 6.1 Ingest & Detection

* Pull **payouts/deposits** into `ProcessorPayout`.
* If itemized line-items exist, populate `ProcessorPayoutSplit`.
* Else, **match invoices** using:

  * Greedy / DP subset match on amounts within a payout window
  * Tolerances for cents-off/fees
  * Known fee schedules & timing

### 6.2 Decisioning & Exceptions

* **AUTO** when line-items exist or subset match is unique/high confidence.
* **EXCEPTION** when multiple invoice sets fit → **AR Tray** for confirm/split/ignore.
* Always isolate **fees** (`type='FEE'`).

### 6.3 Outputs & KPIs

* Invoice-level payment confirmations (kept in Oodaloo).
* **KPI:** `% deposits reconciled` (goal ≥95%).
* **Digest:** cash collected, AR at risk (Top N invoices), runway impact.

---

## 7) Job-Aware Spend Routing (Job Costing)

### 7.1 Candidate Generation (fast SQL)

For each `TransactionRaw t`:

**Visit window (±2h):**

```sql
SELECT v.id AS visit_id, j.id AS job_id
FROM JobberVisit v
JOIN JobberJob j ON j.id = v.job_id
WHERE v.starts_at - INTERVAL '2 hours' <= t.authorized_at
  AND v.ends_at   + INTERVAL '2 hours' >= t.authorized_at
  AND j.company_id = t.company_id;
```

**User/crew narrowing (if card→user known):**

```sql
AND EXISTS (
  SELECT 1 FROM JobberVisitAssignment a
  WHERE a.visit_id = v.id
    AND a.jobber_user_id IN (
      SELECT u.jobber_user_id
      FROM CardUserMap m JOIN "User" u ON u.id = m.user_id
      WHERE m.card_id = t.card_id AND m.active_bool
    )
)
```

**When no `card_id`** (only account/last4): fall back to window + merchant pattern + priors.

### 7.2 Scoring (deterministic MVP)

Features:

* `f_time` — proximity to visit window center
* `f_user` — cardholder assigned to the visit (1/0)
* `f_mcc` — MCC heuristic (e.g., hardware +1.0; fuel −0.5 to job)
* `f_geo` — if available, <5mi from property → +0.5 (normalized)
* `f_amount` — optional against pricebook/estimates
* `f_prior` — company-specific prior (+0.2 after consistent confirmations)

```
score = w1*f_time + w2*f_user + w3*f_mcc + w4*f_geo + w5*f_amount + w6*f_prior
```

### 7.3 Decision Policy

* **AUTO** if `top >= TH_HIGH(0.75)` **and** `(top − #2) >= DELTA(0.25)`.
* **EXCEPTION** if in gray zone (`TH_LOW..TH_HIGH`) or candidates are close.
* **OVERHEAD** if MCC ∈ {fuel, meals, SaaS, insurance} and no strong overlap.
* **INVENTORY** for known warehouse vendors not during a visit.
* **ASK\_CREW** if no candidate but card→user known (one-tap magic link; rate-limited).

**Thresholds are per-company tunables.**

### 7.4 Weak-Label Learning (no rules UI)

* Store `RuleSignal` for patterns keyed by `(merchant_norm, mcc, user_or_crew, hour_bucket, weekday, within_visit_bool)`.
* After **3 consistent confirmations**, add **+0.2 prior**; future similar cases **AUTO**.
* **Undo** penalizes the prior; decay over time for drift.

---

## 8) Directory Onboarding (Cards ↔ People/Crew)

**One simple screen:**

* Detected cards (last4 + merchant samples)
* Assign to **User** or **Crew**; **Shared?** toggle; optional **weights**
* Friendly card **label** (“Lead A’s Visa”, “Install Crew 2”)

**Runtime:** prefer `card_id → user(s)`; if only account/last4, use patterns. Encourage (not require) **virtual cards per crew/vendor** for cleaner joins.

---

## 9) No Write-Back to Jobber (v1.2)

* Oodaloo holds canonical AR splits and expense→job decisions, with full **AuditLog**.
* **No notes/stubs** pushed to Jobber in this phase.
* Oodaloo shows enough job context that field/dispatch can cross-reference without leaving.

---

## 10) Provisional vs Final Profit & Closure Velocity

* **Reality:** expenses lag revenue; job profit is a **converging view**.
* Mark jobs **Provisional** until ≥90% of eventual costs captured (company baseline from history); then **Final**.
* Track **Financial closure velocity** = avg days to reach 90% cost capture.
* **Digest** distinguishes “likely final” vs “still settling.”

---

## 11) Friday Owner Digest (Cash, AR, Jobs, Runway)

* **Runway** (weeks; Δ vs last week)
* **Cash collected** (unbundled)
* **AR at risk** (Top N; “Collect = +X weeks runway”)
* **Jobs**: winners/losers (Provisional vs Final), with % costs captured
* **Data health**: sync age, unresolved exceptions

---

## 12) Frontend (React + Tailwind) & Key Screens

**Stack:** React + Vite + Tailwind; **React Query**; `react-hotkeys-hook`.

* **Overview Strip** (owner): automation %, exceptions to review, median review time, % deposits reconciled.
* **AR Tray**: each payout shows candidate invoice set(s); actions: **Accept**, **Split**, **Ignore**.
* **AP/Job Tray**:

  * Card row:

    * `$342.18 • Home Depot • Tue 10:14a`
    * “Near **Job #4412** (Lead A 9:30–12:00) • conf 0.72”
    * **\[Assign #4412]** • \[Pick other…] • \[Overhead] • \[Inventory] • \[Ask crew]
  * Hotkeys: `A` accept, `O` overhead, `I` inventory, `P` pick, `?` ask.
* **Assigned This Week**: review/undo (undo lowers prior).
* **Jobs**: revenue (paid), costs captured, Provisional/Final, closure velocity.
* **Digest Preview**: what ships on Friday.

**UX principles**: quiet by default (autos don’t need attention), tiny trays, strong context (“why”), company timezone applied server-side, optimistic updates.

---

## 13) API (FastAPI) Surface

**Auth & tenancy:** JWT with `company_id`, `user_id`, `role`. All queries scoped to `company_id`.

```http
# KPIs & health
GET  /v1/kpis                                         -> {automation_rate, exceptions_count, median_review_time, deposits_reconciled_pct}

# AR: payouts, splits, exceptions
GET  /v1/ar/exceptions?from=&to=                      -> [ARExceptionDTO...]
POST /v1/ar/exceptions/{id}/accept                    -> confirm chosen invoice set
POST /v1/ar/exceptions/{id}/split                     -> custom split payload {invoice_refs[], fee_minor, remainder_behavior}
POST /v1/ar/exceptions/{id}/ignore                    -> mark payout as non-AR or off-platform

# AP/Job Costing: exceptions & decisions
GET  /v1/ap/exceptions?from=&to=&mcc=&status=         -> [APExceptionDTO...]
POST /v1/ap/exceptions/{id}/assign                    -> {job_id, visit_id?}
POST /v1/ap/exceptions/{id}/overhead
POST /v1/ap/exceptions/{id}/inventory
POST /v1/ap/exceptions/{id}/ask-crew                  -> sends magic link (rate-limited)

# Review & undo
GET  /v1/ap/assigned?from=&to=                        -> [AssignedDTO...]
POST /v1/ap/assigned/{id}/undo

# Directory & sync
POST /v1/onboarding/cards/map                         -> [{account_id|card_id?, last4, label, shared, user_ids, weights?}]
GET  /v1/jobber/users
GET  /v1/jobber/visits?from=&to=
POST /v1/sync/jobber                                  -> trigger delta (admin)
POST /v1/sync/bank                                    -> trigger delta (admin)

# Exports
GET  /v1/export/posting-pack?from=&to=                -> CSV/Excel (invoices, fees, job costs)
```

**Workers & webhooks:** processor payouts & transactions (webhooks or polling), Jobber deltas (users/jobs/visits). Pipeline: normalize → candidates → score → decide → queue if needed. **Idempotent** on provider+external IDs.

---

## 14) Matching & Policy Engine (Technical)

**Feature vector** per (txn, candidate job/visit):

```
x = [
  time_overlap_score,            # [-1..1]
  user_assigned_flag,            # {0,1}
  mcc_class_weight,              # [-1..+1]
  geo_proximity_norm,            # [0..1] optional
  merchant_company_prior,        # [-0.2..+0.4] from RuleSignal
  amount_plausibility            # [0..1] optional
]
```

**Scoring (MVP):** weighted linear sum.
**Decision thresholds:** `TH_HIGH=0.75`, `TH_LOW=0.45`, `DELTA=0.25`. MCC guardrails (e.g., fuel never auto→job).
**Learning:** `RuleSignal` bumps (+0.2 after 3 consistent confirmations); undos penalize; decay for drift.
**Future** (optional): per-company logistic regression for scoring.

---

## 15) Provisional vs Final & Closure Velocity

* Each job displays **% of costs captured** and **days since completion**.
* **Rule of thumb:** mark Final at ≥90% captured (configurable).
* **Dashboard:** company’s average closure velocity; outliers flagged.

---

## 16) SLOs, Metrics & Guardrails

* **AR:** `% deposits reconciled` ≥95%
* **AP:** automation rate ≥70% by week 4; exception rate ≤30% steady state
* **Time on tray:** ≤10 min/week; **false assignment:** ≤2% (undoable)
* **Closure velocity:** avg days to 90% cost capture
* **Data health:** sync age, failure counts, % txns with geo

---

## 17) Pricing (early, cohort-aware)

* **Recurring (AR-first):** Core **\$149–\$179/mo** (Unbundling + AR Planning + Digest).
* **Installer (profit clarity):** AR + Job Costing **\$228–\$286/mo**.
* Anchor to **time saved**, **collections uplift**, and **avoided margin leakage** (vs heavier industry tools at \~\$99/user/mo).

---

## 18) Risks & Mitigations

* **High exception rate** (>40% after 4 weeks): widen visit window; improve card↔user mapping; tune priors; add geo; merchant whitelists.
* **False assignments** (>3–5%): raise `TH_HIGH`/`DELTA`; MCC clamps; prefer USER decisions; add crew-ask link.
* **Sparse card metadata**: encourage virtual cards per crew/vendor at onboarding; learn from confirmations quickly.
* **Perception risk** (becoming a “UI for Jobber”): **no write-back**, Oodaloo holds canonical decisions; Digest & Runway are Oodaloo-exclusive.

---

## 19) 90-Day Delivery Targets (Definition of “Working”)

* **AR unbundling** with high-confidence auto-splits + tiny AR tray; `% deposits reconciled ≥95%`.
* **AP/job tray MVP** with scoring + weak-label learning; **AUTO ≥65% by week 3, ≥70% by week 4**; weekly review **≤10 min**.
* **Friday Digest v1** (runway, AR at risk, provisional job results).
* Owners report: *“For the first time, I know if payroll is covered.”*

---

## 20) Pseudocode (end-to-end, AP/job matching)

```python
def handle_new_transaction(txn):
    visits = find_visits_in_window(
        company_id=txn.company_id,
        when=txn.authorized_at,
        window_hours=2,
    )

    candidates = []
    for v in visits:
        score = 0.0
        score += w_time  * time_overlap_score(txn.authorized_at, v.starts_at, v.ends_at)
        score += w_user  * user_assigned_flag(txn.card_id, v.visit_id)          # 0/1
        score += w_mcc   * mcc_weight(txn.mcc)                                  # [-1..+1]
        score += w_geo   * geo_proximity_norm(txn.location, v.job.property_address)
        score += w_prior * prior_bump(txn, v)                                   # [-0.2..+0.4]
        score += w_amt   * amount_plausibility(txn.amount, v.job)               # optional
        candidates.append((v.job.id, v.id, score))

    best = top_two(candidates)  # [(job_id, visit_id, score), ...] or []
    if not best:
        decision = decide_overhead_or_inventory(txn) or queue_exception(txn)
    else:
        (job1, visit1, s1), (job2, visit2, s2) = pad_with_none(best)
        if s1 >= TH_HIGH and (s1 - (s2 or 0)) >= DELTA:
            decision = assign(txn, job1, visit1, confidence=s1, type='AUTO')
        elif s1 >= TH_LOW:
            decision = queue_exception(txn, [job1, job2], scores=[s1, s2])
        else:
            decision = queue_exception(txn, [job1], scores=[s1])

    persist(decision)
```

---

## 21) Engineering Stack & Conventions (brief)

* **Backend:** Python 3.11, FastAPI, SQLAlchemy, Alembic, PostgreSQL 14+, Redis (queues).
* **Frontend:** React 18, Vite, Tailwind, React Query; keyboard navigation via `react-hotkeys-hook`.
* **Infra:** Docker, Terraform (envs), Fly.io/Render/AWS; env-per-tenant secrets for integrations.
* **Auth:** JWT; RBAC: OWNER, DISPATCHER.
* **Observability:** OpenTelemetry traces + app KPIs (automation %, exceptions count, review time, deposits reconciled %).
* **Security:** Row-level tenancy, PII encryption at rest, idempotent webhooks, token rotation UX.

---

## 22) What to Build This Week (kickoff checklist)

1. **DB migrations:** core tables above (Company → AuditLog).
2. **Connectors (stubs):** Jobber users/jobs/visits (delta); processor payouts; bank transactions.
3. **Directory screen:** map detected cards ↔ users/crews; shared toggle; labels.
4. **AR engine v0:** ingest payouts; line-item split if available; subset matcher; AR tray UI.
5. **AP engine v0:** candidate generation (visits ±2h), scoring (time/user/mcc), thresholds; AP tray UI.
6. **Digest v0:** runway calc, collected cash, AR at risk, provisional jobs.
7. **KPIs:** show automation %, exceptions count, median review time, deposits reconciled %.

---

**This is the single, unified blueprint.** It captures strategy, cohorts, build order, data model, algorithms, API, UX, metrics, risks, and delivery targets—aligned to **AR-first for credibility**, **job-aware routing for profit**, **no write-back**, and a **tiny weekly tray** that keeps the promise.
