
# Δ What changed vs. your “Cashola — Unified Strategy v2.1”

* **MVP adds**

  * **Payroll slot (proxy)** via bank-inferred cadence + rolling average (with onboarding fallback questions).
  * **Helper levers (minimal)**: one-click **AR reminder in Jobber** and **AP deferral toggle** (marks vendor CAN\_DELAY; affects next digest).
  * **Debt hygiene (light)**: show **credit-card balance** (when available via Plaid) and **net LOC activity trend** MTD.
  * **Digest delivery**: **email + Slack** with **action deep-links** to the above levers and exceptions.
  * **collect\_prob** made explicit & tunable per company (aging buckets).
* **MVP removes**

  * **Portfolio dashboard (controller view)** → moved to **Post-MVP**.
* **No change** to core architecture, event graph, CDM, unbundling, or leave-outs.

---

# Cashola — Weekly Cash Call Product *(v2.2, surgical updates)*

## One-liner

**The weekly cash control cockpit for owner-operators.**
Bank feeds in. Cash clarity out. Owners decide in minutes.

---

## Positioning

* **Ops systems (Jobber, HCP, ServiceTitan, Buildium, Entrata):** Manage jobs, tenants, invoices, and payments. They are operational CRMs/ERPs.
* **Accounting systems (QBO, Xero, NetSuite):** Do historical accrual closes, taxes, audits. Too slow for weekly cash decisions.
* **Oodaloo / Cashola:** Provides the **missing operating layer**: weekly, bank-verified AR/AP decisions + **payroll runway clarity**.

This is a **packaged ritual** (the “Weekly Cash Call”) that owners and controller firms already pay humans to run. Oodaloo makes it software.

---

## Core Promise

* **Connect once.** Bank + ops system (Jobber now; Buildium, ST, HCP later).
* **Auto-match 70%+ of cashflows.** Exceptions tray for the rest (<10 min/week).
* **Output a digest (email & Slack with action deep-links):**

  * Cash today & projected runway (weeks).
  * Top invoices to collect (AR) **with one-click reminder in Jobber**.
  * Bills/vendors to pay vs delay (AP) **with a CAN\_DELAY toggle**.
  * **Payroll status (proxy: covered or shortfall; cadence inferred from bank or captured in onboarding).**
  * **Debt hygiene (light): card balance and net LOC activity trend.**

---

## Scope & Non-Goals

**In-scope (MVP):**

* Bank/processor ingest (Plaid, Stripe/JobberPay).
* Ops AR ingest (Jobber invoices → AR expectations).
* Identity graph + reconciliation (bank ↔ processor ↔ ops).
* Rules engine for normalization (vendor/MCC/regex/account/source\_kind).
* AR unbundling: payouts → invoices + fees.
* Exceptions tray + Friday digest **(email/Slack; action deep-links)**.
* Runway calculator (cash inflows − **must-pay outflows incl. payroll proxy**).
* **Payroll slot (proxy):** bank-inferred cadence + rolling average; if weak, onboarding asks frequency & typical gross.
* **Helper levers (minimal):** one-click **AR reminder in Jobber**; **AP deferral toggle** (marks vendor CAN\_DELAY; impacts next plan).
* **Debt hygiene (light):** **card balance** (when available) and **net LOC trend** MTD.
* **collect\_prob by aging bucket** (current/30–60/>60) **configurable per company**.

**Out-of-scope (MVP):**

* Payroll processing (we ingest timing/amount only; **Gusto/ADP integrations Post-MVP**).
* Bill pay (we suggest pay/delay, user executes elsewhere; push-to-rails Post-MVP).
* Full job costing (optional future upsell).
* Accrual accounting, tax, compliance (remains in QBO/Xero).
* **Portfolio dashboard (controller view)** *(moved to Post-MVP).*

---

## Cash Decision Model (CDM)

A small, universal schema for weekly cash clarity.

### Inflows

* `CUSTOMER_RECEIPTS`
* `REFUNDS_CHARGEBACKS`
* `OTHER_INCOME`

### Outflows

* `PAYROLL_TOTAL`
* `COGS_SUBCONTRACTORS`
* `RENT_UTILITIES`
* `INSURANCE`
* `SAAS_FEES` (incl. processor fees)
* `DEBT_SERVICE`
* `TAXES_GOVT`
* `OWNER_DRAWS`
* `CAPEX`
* `OTHER`

### Policy labels

* `MUST_PAY` | `CAN_DELAY` | `DISCRETIONARY`

### Timing lenses

* `0–7d`, `8–14d`, `15–30d`

---

## Workflow Loop (Weekly Cadence)

1. **Ingest:** Bank txns, processor payouts, ops invoices (AR).
2. **Normalize:** Apply rules; unknowns hit tray.
3. **Unbundle AR:** Tie payouts → invoices + fees.
4. **Reconcile:** Use event graph to prevent double counting.
5. **Compute runway:** `Cash today + E[AR next 7d]*collect_prob − MustPay outflows (incl. payroll proxy)`.
6. **Digest:** Push a Friday summary **via email/Slack with action deep-links**.
7. **Exceptions:** Dispatcher clears unknowns; rules engine improves coverage.
8. **Repeat weekly.**

---

## Backend Architecture

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

* **Services:** `ingestor`, `normalizer`, `cash_engine`, `exceptions`, `digest`.
* **Storage:** SQLite/Postgres (OLTP), S3 (raw payloads/exports), Redis (queues).
* **Integrations:** Plaid, Stripe/JobberPay, Jobber (now); Buildium/HCP/ST later; optional QBO/Xero (read-only for COA mapping).

---

## Ops Connector Abstraction

```python
class OpsConnector:
    def get_invoices(self, since_date): ...
    def get_clients(self): ...
    def get_payments(self, since_date): ...
    def get_jobs(self, since_date): ...
```

* Jobber/HCP/ST implementors → service pros.
* Buildium/ResMan/Entrata → property mgmt.
* Same CDM downstream.

---

## Frontend / UX

* **Onboarding wizard:** Connect Plaid + ops; **capture payroll frequency & typical gross if inference weak**; confirm vendor mappings; backtest coverage.
* **Exceptions tray:** 5–10 unknowns; keyboard-first triage; hotkeys + undo; **quick actions for AR reminder and CAN\_DELAY**.
* **Weekly digest (owner):** Runway (weeks), AR plan (**with one-click reminders**), must-pay vendors/payroll, **debt hygiene panel**, exceptions summary; **email/Slack with deep-links**.
* ~~**Portfolio dashboard (controller/PE mode):**~~ *(moved to Post-MVP).*

---

## Deployment

* **Backend:** FastAPI + SQLite (dev) / Postgres (prod) + Celery/Redis.
* **Frontend:** React + Tailwind.
* **Auth:** OAuth (Plaid, Jobber, later Buildium/QBO); JWT internally.
* **Infra:** Containerized; deploy on AWS ECS/Fargate or Render/Fly.

---

## Test Plan

* Golden dataset (90 days anonymized txns).
* Gates: ≥95% deposit reconciliation; automation ≥70% by week 4; exceptions cleared <10 min/wk; runway error <0.3 weeks vs controller baseline.
* Property tests: rule precedence deterministic; reconciliation idempotent; **payroll inference cadence stability**.

---

## Go-to-Market

* **Start:** Jobber App Marketplace wedge (HVAC/plumbing 5–15 techs).
* **Expand:** Buildium for property mgmt; ST/HCP later.
* **Message:** *“The Weekly Cash Call — without the call.”*
* **Pricing:** Company-based (\$179–\$250/mo); ~~portfolio pricing for controller shops~~ *(portfolio view Post-MVP).*

---

## Future Modules

* **Job Costing (Profit Clarity):** Assign materials/labor to jobs; compute cash job GM. Upsell where jobs matter most.
* **AP Assist:** Duplicate/late-fee/“delay OK” nudges; **later push-to-rails** (Relay/BILL).
* **Benchmarking:** Criteria-based GM%/labor%/overhead bands per trade/stage.
* **Succession-ready close:** Optional service; QBO write-backs for PE prep.
* **Portfolio dashboard (controller/PE mode):** *(moved here; implement after single-client flows are stable).*
* **Payroll integrations (precision):** **Gusto/ADP** for exact gross/net and dates.

---

## Why PE/Controller Firms Care

* Converts \$3–10M service shops into **cash-coherent, diligence-ready targets** without adding headcount.
* ~~Portfolio dashboard = controller leverage (one view, many clients).~~ *(Post-MVP.)*
* Creates **synergy pre-consolidation**: keeps tuck-ins healthy on Jobber/HCP before migrating to ST.

---

✅ **Summary:**
The **Weekly Cash Call** MVP now includes: **payroll proxy**, **minimal helper levers**, **debt hygiene**, **email/Slack digests with deep-links**, and **tunable collect\_prob**.
**Portfolio dashboard** is **Post-MVP**. Everything else remains as written.
