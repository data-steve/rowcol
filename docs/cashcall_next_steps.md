This is great raw material. You’ve already built most of the skeleton Cashola needs. Here’s a straight-shooting alignment plan: what to **keep**, what to **shim**, what to **refactor**, and what to **park**—plus concrete renames and a migration sketch so you don’t throw away working code.

---

# TL;DR

* **Keep (as-is or near-as-is):** Jobber & Plaid integrations; tray service; bank models/routes; a big chunk of AR models + reconciliation tests; policy engine scaffolding.
* **Add (thin but new):** the **Identity + Event Graph** and **Cash Ledger** layer (this is the Cashola crux).
* **Refactor (surgical):** current reconciliation to **emit identities/edges** and **write the consolidated cash\_ledger**; policy engine to output **CDM + policy**; exceptions/tray items to match spec kinds.
* **Park / remove:** close automation, payroll, heavy AP/OCR, deep engagement/docs, QBO write flows.

Do this as a **strangler**: introduce `identity_graph` + `cash_ledger`, then point the existing AR/Tray/Digest flows at those tables without nuking your current APIs.

---

## Heatmap — Module-by-Module Call

| Area                               | Your paths                                          | Recommendation                                                                                          | Why / How                                                                                                                  |
| ---------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Integrations: Jobber**           | `integrations/jobber/{client.py,sync.py}` + tests   | **Keep**                                                                                                | Already aligned. Keep OAuth + cursors + webhooks. Ensure payments/invoices minimal fields match spec.                      |
| **Integrations: Plaid**            | `integrations/plaid/sync.py`                        | **Keep**                                                                                                | Keep `/transactions/sync`. Add descriptor → processor hints later.                                                         |
| **Integrations: Stripe/JobberPay** | *(not yet in tree)*                                 | **Add (later)**                                                                                         | Add payouts + balance txn when ready; not a blocker for pilot.                                                             |
| **Bank domain**                    | `domains/bank/*`                                    | **Keep (minor shim)**                                                                                   | Keep `BankTransaction` as a **raw\_event producer**. Don’t change schemas yet; write to `raw_event` alongside.             |
| **AR domain**                      | `domains/ar/*`                                      | **Keep core models & cash\_reconciliation**, rename routes/services for plan; **emit identities/edges** | You already have `cash_reconciliation_new.py`. Wrap its outputs to produce identity nodes/edges and `unbundle_meta`.       |
| **Tray**                           | `domains/tray/*`                                    | **Keep (rename item kinds)**                                                                            | Map to spec: `AR_AMBIG`, `UNMAPPED`, `NO_MATCH`, `GHOST_AR`, `TIMING`. Keep keyboard UX/tests.                             |
| **Policy engine**                  | `policy/*`                                          | **Refactor to CDM**                                                                                     | Collapse rules to scopes: vendor/mcc/regex/account/source\_kind. Output `cdm_key` + `policy`. Keep tests; update fixtures. |
| **Core/Engagement/Docs**           | `domains/core/*` (engagement, documents, services…) | **Park**                                                                                                | Not needed for Cashola MVP. Don’t delete; feature-flag off.                                                               |
| **AP/OCR**                         | `domains/ap/*`                                      | **Park most**                                                                                           | Keep only vendor canonical + light normalization; park bills/OCR.                                                          |
| **Close automation**               | `_parked/close/*`                                   | **Park**                                                                                                | Out of scope. Useful later for service tier.                                                                               |
| **Payroll**                        | `_parked/payroll/*`                                 | **Park**                                                                                                | MVP uses proxy slot (manual frequency/amount).                                                                             |
| **QBO**                            | `_parked/qbo/*`                                     | **Park**                                                                                                | MVP is read-only mapping later.                                                                                            |

---

## Introduce the Missing Layer (new, thin)

Create a **new domain** that your existing code can write to, with SQLite-friendly DDL.

```
domains/identity_graph/
  ├── models.py      # raw_event, identity, identity_link, identity_edge, cash_ledger, rule_version, cdm_rule, exception
  ├── services.py    # fingerprinting, linking (payout↔settlement, charge/refund↔payout, ops payment↔charge)
  ├── consolidate.py # graph → cash_ledger (count once, bank-timed)
  └── tests/         # unit tests for matcher + consolidation
```

**Do not** rip out existing AR/Bank models. Instead:

* On ingest (Plaid/Jobber), **also** write `raw_event` rows.
* After ingest, run `identity_graph.services.link()` and `consolidate.to_ledger()`.

This lets legacy endpoints keep working while the digest/tray gradually switch to reading from `cash_ledger`.

---

## Concrete Renames & Shims (low churn)

* `domains/ar/services/collections.py` → `domains/ar/services/ar_plan.py`
* `domains/ar/services/cash_reconciliation_new.py` → keep name, **append**:

  * return `identities`, `edges`, `exceptions` (in addition to your current summary)
  * write `identity_link` for the raw events it touches
* `domains/policy/services/policy_engine.py` → ensure it takes **cash\_ledger** rows and sets `cdm_key` + `policy`, respecting precedence
* `domains/tray/services/tray.py` → add mappers:

  * unknown CDM → `UNMAPPED`
  * multi-candidate AR set → `AR_AMBIG`
  * payout without settlement (age > 2d) → `NO_MATCH`
  * ops “paid” without bank/processor → `GHOST_AR`
  * late/misaligned dates/amounts → `TIMING`

---

## Minimal Schemas to Add (SQLite-friendly)

Add a single `models.py` with the compact tables you already approved in the spec (TEXT ids, ISO timestamps). You can literally copy these into SQLAlchemy models:

* `raw_event(id, company_id, src, kind, external_id, occurred_at, amount_cents, currency, account_ref, counterparty, mcc, parent_external_id, raw_json)`
* `identity(id, company_id, fingerprint, canonical_kind)`
* `identity_link(id, company_id, identity_id, raw_event_id, confidence, reason)`
* `identity_edge(id, company_id, from_identity, to_identity, kind, weight)`
* `cash_ledger(id, company_id, identity_id, posted_at, direction, amount_cents, currency, cdm_key, policy, confidence, provenance_json)`
* `rule_version`, `cdm_rule`, `exception`

No need to delete any existing tables.

---

## Migration Sketch (no data loss)

1. **Backfill `raw_event`:**

   * From `domains/bank.models.bank_transaction`: emit `BANK_TXN`.
   * From `domains/ar.models.payment`: emit `OPS_PAYMENT`.
   * From `domains/ar.models.invoice`: emit `OPS_INVOICE`.
2. **Build identities:**

   * Hash fingerprints per spec; upsert into `identity`; link via `identity_link`.
3. **Link edges:**

   * Use your existing `cash_reconciliation_new` matches to create:

     * `PAYOUT ─SETTLES→ SETTLEMENT`
     * `CHARGE/REFUND/FEE ─COMPOSED_OF→ PAYOUT`
     * `OPS_PAYMENT ─APPLIES_TO→ CHARGE` (when known)
4. **Consolidate:**

   * Emit `cash_ledger` rows (count once, bank-timed).
5. **Categorize:**

   * Run policy engine to set `cdm_key` + `policy`. Create `UNMAPPED` exceptions for unknowns.
6. **Flip readers:**

   * Dashboard tiles + digest read from `cash_ledger` + CDM, not raw bank/AR joins.
   * Tray reads from `exception` plus any ambiguous link candidates.

Rollback is trivial (tables are new and additive).

---

## Tests You Can Reuse Almost As-Is

* `integrations/jobber/tests/test_jobber_sync.py` → **Keep** (ingest correctness).
* `domains/bank/tests/*` → **Keep**.
* `domains/ar/tests/test_ar_integration.py` + `test_collections.py` → **Keep**, but add assertions that `raw_event`/`identity_link` are produced.
* `tests/test_reconciliation_guardrails.py` → **Keep**, add cases for “count once” rules.
* `policy/tests/test_policy_engine.py` → **Refit** expectations to use `cash_ledger` inputs and assert `cdm_key` + `policy`.
* `tray/tests/test_tray.py` → **Adjust** to new exception kinds.
* Seed/fixtures: `realistic_test_data.json` → extend with a couple of **payout+settlement** pairs and one **chargeback**.

Add new unit tests under `domains/identity_graph/tests/`:

* payout→settlement matching (±2d window, multi candidates)
* subset-sum AR unbundling (unique/ambiguous/no-match)
* consolidation (no double count; bank-timed)

---

## Routing/Endpoint Impact (non-breaking)

* Keep existing endpoints; add the spec’d ones as **new** (`/v1/...`). Behind the scenes, they read `cash_ledger`.
* Mark old “pre-ledger” reads with a deprecation header or feature flag so you can sunset later.

---

## Folder Shape After Alignment

```
domains/
  identity_graph/        # NEW (models/services/consolidate/tests)
  ar/                    # KEEP (adds identity emission + new ar_plan)
  bank/                  # KEEP
  tray/                  # KEEP (new kinds)
  policy/                # KEEP (outputs CDM+policy)
integrations/
  jobber/                # KEEP
  plaid/                 # KEEP
  stripe/                # NEW (post-MVP)
```

Feature-flag everything non-MVP (close, payroll, AP/OCR, deep docs) so you don’t regress tests elsewhere.

---

## What You Definitely Shouldn’t Rewrite

* **Jobber sync** (auth, cursors, webhook handlers): it’s compliant with the plan.
* **Plaid sync** loop: exactly what we need.
* **Your reconciliation algorithms** (subset sum / greedy): re-use; just **write graph/ledger outputs** in addition to your current summaries.
* **Tray service & UI**: keep; only map item kinds and add hotkeys you already supported.

---

## What’s Worth a Clean Add (small, surgical)

* **Identity graph + ledger** (new domain). It prevents double counting and unlocks explainability.
* **Policy engine adapter** that takes **ledger rows** (not raw txns) and returns a `(cdm_key, policy)`.

Everything else fits around those two pieces.

---

## Smoke Checklist (to know you’re “Cashola-aligned”)

* Ingest a seed tenant → see **raw\_event** rows for bank, payouts, invoices/payments.
* Identities materialize with stable fingerprints; edges exist (payout→settlement).
* `cash_ledger` shows **one** INFLOW per settlement date; no double counts when both bank & processor exist.
* Policy engine sets `cdm_key` + `policy` for ≥95% of ledger value (on seed).
* Tray shows ≤10 items; actions resolve to rules or links and reduce exceptions.
* Friday digest pulls from **ledger + CDM** and matches the tiles math.

---

If you want, I can produce a tiny PR-style diff (new files and the 6–8 specific touch points in existing services) and a minimal SQLAlchemy models file you can drop in to create the graph/ledger tables.
