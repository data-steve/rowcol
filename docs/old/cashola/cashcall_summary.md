# Cashola — Oodaloo's Unified Strategy for Weekly Cash Call Product (v2.1)

## One-liner

**The Weekly Cash Call — without the call.**
Bank feeds in. Cash clarity out. Owners decide in minutes.

---

## Positioning

* **Ops systems (Jobber, HCP, ServiceTitan, Buildium, Entrata):** Manage jobs, tenants, invoices, and payments. They are operational CRMs/ERPs.
* **Accounting systems (QBO, Xero, NetSuite):** Do historical accrual closes, taxes, audits. Too slow for weekly cash decisions.
* **Oodaloo / Cashola:** Provides the **missing operating layer**: weekly, bank-verified AR/AP decisions + payroll runway clarity.

This is a **packaged ritual** (the “Weekly Cash Call”) that owners and controller firms already pay humans to run. Oodaloo makes it software.

---

## Core Promise

* **Connect once.** Bank + ops system (Jobber now; Buildium, ST, HCP later).
* **Auto-match 70%+ of cashflows.** Exceptions tray for the rest (<10 min/week).
* **Output a digest:**

  * Cash today & projected runway (weeks).
  * Top invoices to collect (AR).
  * Bills/vendors to pay vs delay (AP).
  * Payroll status (covered or shortfall).

---

## Scope & Non-Goals

**In-scope (MVP):**

* Bank/processor ingest (Plaid, Stripe/JobberPay).
* Ops AR ingest (Jobber invoices → AR expectations).
* Identity graph + reconciliation (bank ↔ processor ↔ ops).
* Rules engine for normalization (vendor/MCC/regex/account/source\_kind).
* AR unbundling: payouts → invoices + fees.
* Exceptions tray + Friday digest.
* Runway calculator (cash inflows − must-pay outflows).
* Portfolio dashboard (multi-client view for controllers).

**Out-of-scope (MVP):**

* Payroll processing (we ingest timing/amount only).
* Bill pay (we suggest pay/delay, user executes elsewhere).
* Full job costing (optional future upsell).
* Accrual accounting, tax, compliance (remains in QBO/Xero).

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
5. **Compute runway:** `Cash today + E[AR next 7d] − MustPay outflows`.
6. **Digest:** Push a Friday summary to owner/controller.
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

* **Onboarding wizard:** Connect Plaid + ops; confirm vendor mappings; backtest coverage.
* **Exceptions tray:** 5–10 unknowns; keyboard-first triage; hotkeys + undo.
* **Weekly digest (owner):** Runway (weeks), AR plan, must-pay vendors/payroll, exceptions summary.
* **Portfolio dashboard (controller/PE mode):** Multi-client runway, AR/AP plans, automation %.

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
* Property tests: rule precedence deterministic; reconciliation idempotent.

---

## Go-to-Market

* **Start:** Jobber App Marketplace wedge (HVAC/plumbing 5–15 techs).
* **Expand:** Buildium for property mgmt; ST/HCP later.
* **Message:** *“The Weekly Cash Call — without the call.”*
* **Pricing:** Company-based (\$179–\$250/mo); portfolio pricing for controller shops.

---

## Future Modules

* **Job Costing (Profit Clarity):** Assign materials/labor to jobs; compute cash job GM. Upsell where jobs matter most.
* **AP Assist:** Duplicate/late-fee/“delay OK” nudges.
* **Benchmarking:** Criteria-based GM%/labor%/overhead bands per trade/stage.
* **Succession-ready close:** Optional service; QBO write-backs for PE prep.

---

## Why PE/Controller Firms Care

* Converts \$3–10M service shops into **cash-coherent, diligence-ready targets** without adding headcount.
* Portfolio dashboard = **controller leverage** (one view, many clients).
* Creates **synergy pre-consolidation**: keeps tuck-ins healthy on Jobber/HCP before migrating to ST.

---

✅ **Summary:**
Your strategy and engineering plans are unified. The **Weekly Cash Call** MVP = AR unbundling, reconciliation, AP/payroll runway, digest, and tray.
Identity graph + CDM + tray are the differentiators. Job costing and benchmarking come later. Connectors are swappable; QBO integration optional.
