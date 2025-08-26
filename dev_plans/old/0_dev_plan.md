Awesome—here’s your **single, consolidated hand-off** for Grok/Cursor. It merges the latest Oodaloo plan with every relevant “Preciate” detail you shared (CDC for quotes, CSV email-ingest fallback, Jobber rate/cost realities, tray UX, AR plan, Unbundling, AP-Assist, feature flags, metrics, pricing). No code—just precise specs, flows, endpoints, tables, and DoD so you can build immediately.

---

# Oodaloo — Engineering Handoff (v1.1, consolidated)

**One-liner:** *Jobber helps make revenue. Oodaloo helps make profit.*
**Wedge:** Friday **profit & runway** email + **dispatcher exceptions tray**.
**Integrations (now):** **Jobber GraphQL + webhooks** and **Plaid Transactions**.
**Explicit non-goals (v1):** payroll integrations, QBO write, line-item sync, SMS.
**Operating principle:** **Bank is truth.** Cash-basis first; accruals are service-tier later.

---

## 1) Stack & repo alignment (solo-friendly)

**Tech:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Redis (queues/rate), Postgres (prod) / SQLite (dev), Postmark (email), Sentry, OTEL, Prometheus.

**Keep/adapt from your repo**

* `domains/bank/*` → Plaid sink (+ `company_id`, `processor`, `unbundle_meta`).
* `domains/ar/*` → invoices/payments + **AR Plan** (rename `services/collections.py` → `services/ar_plan.py`).
* `domains/ap/*` → keep vendor models only (materials→job suggestions). Park OCR/bills.
* `domains/core/*` → keep user/firm/integration/job/client/task/audit/transaction; park heavy engagement/document code.
* `domains/policy/*` → slim to `rules` (vendor→jobtype, ignore merchant, processor fee priors).
* `webhooks/*` → add Jobber + Plaid handlers.
* `templates/bank_matching.html`, `templates/collections_dashboard.html` → visual cues for tray & AR.

**Add (new)**

```
domains/integrations/jobber/{client.py, schemas.py, sync.py, notes.py}
domains/integrations/plaid/{link.py, sync.py}
domains/tray/services/tray.py        # build exceptions list + actions
domains/core/routes/tiles.py         # owner tiles + digest feed
domains/rules/services/vendor_rules.py
```


**No Alembic yet** (dev). Bootstrap schema on app start; when you go multi-tenant in prod, add migrations.

---

## 2) Minimal data surface (tables & key fields)

All tables include `company_id`. Index `company_id, updated_at`.

**Company**
`id, name, policy_json {min_amount, aging_focus, vip[], daily_cap, channel_order[]}, burden_json {role weekly_cost + alloc_method}, created_at`

**Integration**
`id, company_id, kind('jobber'|'plaid'), access_blob(enc), refresh_blob(enc), cursor_json, status, last_sync_at`

**BankTransaction**
`id, company_id, account_id, date, amount, description, mcc?, merchant?, processor('JOBBER_PAY'|'STRIPE'|'ACH'|'CHECK'|...), unbundle_meta{fee,candidates[],confidence}, invoice_ids[], status`

**Invoice**
`id, company_id, external_id(jobber), client_id, job_id?, total, due_date?, status(sent|partial|overdue|paid), created_at, updated_at`

**Payment**
`id, company_id, external_id(jobber), invoice_id?, amount, received_on, deposit_tx_id(BankTransaction.id?)`

**Quote** *(CDC going forward; optional CSV for history)*
`id, company_id, external_id(jobber), total, status, created_at, status_changed_at?, provenance('cdc'|'csv'|null)`

**Attempt** *(AR/quote follow-ups)*
`id, company_id, invoice_id, channel('email'|'call'|'task'), when, outcome('sent'|'answered'|'promise'|'dispute'|'no_answer'), meta{}`

**Rule**
`id, company_id, kind('vendor_to_jobtype'|'ignore_merchant'|'processor_fee'), pattern, value, confidence, created_by`

**Audit**
`id, company_id, actor_id, action, target_type, target_id, at, meta{}`

**SyncCursor**
`id, company_id, source('jobber:invoices'|'jobber:payments'|'jobber:quotes'|'plaid'), cursor, last_full_backfill_at`

---

## 3) Integrations (what to fetch; how to stay within cost/rate)

### Jobber (GraphQL + webhooks; **at-least-once** delivery)

* **OAuth:** store encrypted access/refresh per tenant.
* **Shallow fields only** (cheap):

  * payments: `id amount receivedOn invoice{id job{id}}`
  * invoices: `id total status dueDate job{id} client{id}`
  * jobs: `id title number`
  * quotes: `id total status createdAt`
* **Pagination & cost:** always `first: N` + cursors; shallow projections; backoff on `THROTTLED` with jitter; per-tenant worker.
* **Webhooks:** push to Redis queue; **dedupe** by `(source, external_id, day_bucket)`; idempotent upsert.
* **Backfills:** nightly delta by cursor; weekly “shallow safety” scan.
* **Notes writer:** when logging a follow-up, write a tiny Jobber note if allowed; else keep local.

### Plaid (Transactions Sync)

* **Link:** multi-select; default include operating checking + primary card. Allow label **Personal-Mixed**.
* **Sync:** `/transactions/sync` per item; persist `added/modified/removed`; update `SyncCursor`.
* **Fallback:** unsupported institutions → per-account **CSV upload** (admin page) with provenance `source:'csv'`.

### CSV / Email ingest (optional, scoped)

* Only for **historical `status_changed_at`** on quotes if owners care.
* Two paths (no stored creds): **manual upload** or **forwarded report email** to `tenant+hash@ingest.oodaloo.io` (Postmark inbound).
* CDC is the **truth forward**; CSV just fills the past; store `provenance`.

---

## 4) Core flows

**A) Daily ingest** → *webhooks → queue → idempotent upsert → freshness metrics*
**B) Reconciliation (bank↔Jobber)**

1. Classify deposit `processor` by descriptor.
2. Window Jobber **payments** ±k days.
3. Exact net→gross match else **subset** (DP/greedy) → score (closeness × cadence prior × client overlap).
4. Result: `auto` | `needs_confirm` (candidates + confidence) | `off_platform`. Persist to `unbundle_meta` and links.

**C) Exceptions tray (dispatcher)**

* Items: unconfirmed deposits, off-job income, expenses needing job tag, ignored/personal candidates.
* Sort by **impact = amount × age × wrongness\_prob**.
* Actions: **Confirm / Assign job / Split / Off-Job / Ignore / Make Rule / Undo**.
* Bulk confirm ≥85% confidence; 10s undo; inline **Audit**.

**D) AR Plan (Cash Discipline add-on)**

* Score open invoices:
  `score = 40*pay_history + 25*amount_band + 20*age_band + 10*engagement − 15*penalties`
  (neutral `pay_history=0.5` if unknown; penalties = dispute, >3 reminders, broken promise).
* Apply **policy knobs**: `min_amount, aging_focus, vip[], daily_cap, channel_order`.
* Build weekly plan to hit **“Collect \$X → +Y runway weeks”**; create Jobber **Tasks** for calls or open invoice deep links.
* **Never double-send:** we prioritize; **Jobber** sends its own reminders.
* Log each attempt (Attempt row + optional Jobber note). Stop when **bank shows paid**.

**E) Friday owner digest**

* Tiles: **Runway (weeks)**, **Cash collected (wk)**, **AR at risk** buckets, **Reconciled %**, **Winners/Losers**, **Data-Health**.
* Muted upsell tiles when signal exists (e.g., DSO>7d → “Enable Cash Discipline”).

---

## 5) API surface (stable)

**Owner & digest**

* `GET  /api/v1/owner/tiles?company_id=` → `runway_weeks, dso_days, ar_buckets, reconciled_pct, winners_losers[], data_health`
* `POST /api/v1/owner/approve-ar-plan` `{company_id, invoice_ids[]}`

**Exceptions tray**

* `GET  /api/v1/tray?company_id=` → `[ {id,type,impact,suggestions[],confidence} ]`
* `POST /api/v1/tray/{id}/confirm`
* `POST /api/v1/tray/{id}/assign_job` `{job_id}`
* `POST /api/v1/tray/{id}/split` `{parts:[{amount,invoice_id?}]}`
* `POST /api/v1/tray/{id}/ignore`
* `POST /api/v1/rules/vendor` `{pattern,value,kind}`

**AR plan**

* `GET  /api/v1/ar/plan?company_id=` → ranked list + impact (“+Y weeks if \$X collected”)
* `POST /api/v1/ar/attempt` `{invoice_id, channel, outcome?, meta?}`
* `POST /api/v1/ar/policy` `{min_amount, aging_focus, vip[], daily_cap, channel_order[]}`

**Integrations**

* `POST /api/v1/integrations/jobber/oauth/callback`
* `GET  /api/v1/integrations/plaid/link-token?company_id=`
* `POST /api/v1/integrations/plaid/exchange` `{public_token, company_id}`
* `POST /api/v1/webhooks/jobber`
* `POST /api/v1/webhooks/plaid`

---

## 6) UX spec (why support stays tiny)

**Exceptions Tray**

* Dense impact-sorted table; sticky left (vendor/amount/date) and right action bar.
* Row expander: top suggestion(s) + confidence + **delta preview** (“adds +\$1,240 to Job #442 GM”).
* One-tap actions; **bulk confirm** ≥ threshold; **Undo**.
* **Keyboard:** ↑↓ **Enter** **S**(split) **A**(assign) **O**(off-job) **I**(ignore) **R**(rule) **B**(bulk).
* Inline **Audit** and **Data-Health** strip (“Bank 2h • Jobber 3m • Throttles 0”).

**Owner tiles**

* **Runway:** `(cash_available − earmarked) / weekly_burden`.
* **DSO:** rolling calc from AR + collections.
* **Reconciled %:** matched / (matched + unmatched) deposits.
* **Winners/Losers:** cash GM (payments − tagged costs − allocated burden).
* **Data-Health:** last syncs, webhook lag, throttle hits, reconnect prompt.

---

## 7) Feature flags & packaging

* Flags: `CASH_DISCIPLINE`, `UNBUNDLING`, `AP_ASSIST`, `BENCHMARKING`.
* Gate endpoints/UI; show muted tiles as tasteful upsell when signals exist.
* Pricing mapping (engineering):

  * **Core** \$179 (founder \$149) → base flags
  * **+ Cash Discipline** \$229 → `CASH_DISCIPLINE`
  * **+ Unbundling** \$259 → `UNBUNDLING`
  * **Benchmarking** +\$20/mo → `BENCHMARKING`

---

## 8) Observability & reliability (per-tenant)

* **Freshness HUD fields:** `last_bank_sync_at`, `last_jobber_sync_at`, `webhook_lag_seconds`, `throttle_hits_24h`, `auto_match_rate`.
* **Idempotency:** webhooks key `(source, external_id, day_bucket)`; Plaid Sync key `(item,cursor)`; retries with jitter.
* **Backfills:** nightly delta; weekly safety scan (shallow).
* **Metrics:** `jobber_throttles`, `webhook_dedupes`, `auto_match_rate`, `exceptions_cleared`, `median_handle_time`, `digest_sent/open`, `reconciled_pct`, `ar_collected_weekly`, `dso_days`, `runway_weeks`.
* **Targets:** auto-match ≥80% deposit \$, median tray action <60s, reconciled ≥95%, digest open ≥60%.

---

## 9) Security & tenancy

* Encrypt OAuth/Plaid tokens (AES-GCM/Fernet); rotate on refresh failure.
* Per-tenant RBAC: roles **owner** and **dispatcher** only.
* Don’t store credentials for reports; CSV/email ingest only; provenance fields on every imported record.
* Full audit trail on all mutations; export on demand.

---

## 10) Seed dataset (for demo + QA)

* 12 weeks; \~250 bank tx (materials, fuel, SaaS, fees); 2–3 lump payouts; 8 open AR w/ varied age; 1 dispute; 3 VIPs; 1 “Personal-Mixed” merchant.
* Expected: recon % ≈95, tray median <60s, runway 2–3 weeks.

---

## 11) Testing (solo-friendly)

* **Unit:** recon sum of subset selector (exact + greedy), unbundling thresholds, AR scoring monotonicity, attempt idempotency.
* **Integration:** webhook → queue → upsert → tray item created.
* **Contract fixtures:** mock Jobber/Plaid JSON; verify field mapping & cursors.
* **Smoke:** `/healthz` checks DB + Redis + last sync timestamps.

---

## 12) Rollout plan & DoD

### Phase 1 — **Core Profit Clarity** (Weeks 1–4)

**Backend:** Jobber ingest (payments/invoices/jobs/quotes shallow) + webhooks/cursors; Plaid Link + Transactions Sync; Reconciliation; Tray v1 (confirm/split/assign/ignore + rules + audit); Tiles math; Friday digest; Data-Health.
**Frontend:** Exceptions Tray UI; Dashboard tiles; Settings (burden); Accounts (connect & labels).
**DoD:** auto-match ≥80% deposit \$; reconciled ≥95%; tray median action <60s; digest correct; HUD accurate.

### Phase 2 — **Cash Discipline** (Weeks 3–6 overlap)

**Backend:** AR scoring + policies; weekly plan approve; Attempt log; Jobber note/task write; digest adds: `$ collected`, DSO Δ, runway Δ.
**Frontend:** AR plan list, policy editor, attempt panel.
**DoD:** plan approve locks set; attempts logged; **no duplicate sends** with Jobber automations; bank-paid stops chasing.

### Phase 3 — **Unbundling** (Weeks 5–7)

Processor classifier; cadence priors; DP/greedy; tray confirm; upsell trigger on detected lumps.
**DoD:** ≥95% accuracy post-confirm; fake overdues drop.

*(AP-Assist & Benchmarking scaffolds can follow after PMF.)*

---

## 13) Risks & mitigations

* **Jobber API gaps (quote status change):** CDC from install forward; optional **one-time CSV/email** backfill for history; store `provenance`.
* **Jobber cost/rate:** shallow fields, paginate, cache IDs, webhook-first, stagger backfills.
* **Plaid noise/personal spend:** **Personal-Mixed** label; ignore-merchant rules; CSV fallback if needed.
* **Adoption (dispatcher time):** target <10 min/week; show **\$ collected** & **runway impact** in digest.
* **Scope creep:** payroll/QBO write/line-items are **explicitly deferred** (service tier or later add-ons).

---

## 14) Ticket checklist (ready to paste into your tracker)

**Integrations**

* [ ] Jobber OAuth flow; token vault (encrypt at rest).
* [ ] Jobber GraphQL client with shallow queries + cursors.
* [ ] Jobber webhooks endpoint → Redis → idempotent consumer.
* [ ] Plaid Link (multi-account) + `/transactions/sync` iterator.

**Data & services**

* [ ] Bootstrap schema (tables in §2).
* [ ] Reconciliation service (net→gross, subset, fee priors).
* [ ] Tray service (impact score, suggestions, actions, rules, audit).
* [ ] Tiles service (runway, DSO, AR buckets, reconciled %, winners/losers, data-health).
* [ ] Digest renderer (Postmark template).

**AR Plan (add-on)**

* [ ] Scoring fn; policy knobs; plan builder; approve endpoint.
* [ ] Attempt logger; Jobber note/task write; stop on bank-paid.

**Unbundling (add-on)**

* [ ] Processor classifier; cadence priors; candidate set; thresholds; remember rule; upsell detector.

**Frontend**

* [ ] Exceptions Tray page (table + expander + one-taps + bulk + undo).
* [ ] Dashboard tiles; Settings (burden/policy); Accounts connect/labels.
* [ ] AR Plan page; Policy form.

**Obs & safety**

* [ ] Data-Health HUD; Prometheus counters; Sentry.
* [ ] Idempotency keys, retries with jitter; per-tenant throttles.

**Seed & QA**

* [ ] Seed dataset builder; demo tenant script.
* [ ] Unit & integration tests as in §11.

---

## 15) Pricing hooks (engineering)

* Core \$179 (founder \$149) → base flags.
* +Cash \$229 → enable `CASH_DISCIPLINE`.
* +Unbundling \$259 → enable `UNBUNDLING`.
* Benchmarking +\$20 → enable `BENCHMARKING`.
* Show **muted tiles** & **tray CTAs** only when signals exist (e.g., lump payouts, DSO>7d).

---

## 16) What to show the bookkeeper (for your upcoming chat)

* Tray flows (confirm/split/assign/ignore; rules; audit).
* Friday digest math (runway & cash GM) and AR plan knobs.
* Posting-pack CSVs you’ll export (deposits\_matched, expenses\_tagged, journal\_summary, exceptions\_open).
* Alignment: Oodaloo is **cash-basis mgmt reporting + orchestration**, not GL. QBO **write** only in the optional service tier.

