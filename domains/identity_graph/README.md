

# Identity Graph (Events → Identities → Links → Cash Ledger)

**Purpose.** Turn noisy, overlapping feeds (bank, processors, ops) into a **single, deduped event graph** so we:

* **Link** payouts ↔ bank settlements ↔ charges/refunds/fees ↔ ops invoices/payments,
* **Count cash once** (bank-timed) in the **cash\_ledger**, and
* Feed the **Policy/CDM** and **Exceptions Tray** with explainable provenance.

This folder owns: **fingerprints**, **linking**, **graph edges**, and the **ledger consolidation** pass.

---

## TL;DR: What you may need to change

1. **SQLite-friendly tables**
   Ensure you have (or add) these compact tables (names can map to your existing models):

   * `raw_event` (append-only; idempotent on `(company_id, src, kind, external_id)`)
   * `identity`, `identity_link`, `identity_edge`
   * `cash_ledger` (target of consolidation; add `provenance_json` TEXT/JSON)
2. **Fingerprints**
   Implement the stable fingerprint funcs (bank settlement, payout, balance\_txn, ops payment/invoice).
3. **Matchers**
   Implement/link the three core matchers:

   * **Payout→Settlement** (processor→bank)
   * **Charge/Refund/Fee→Payout** (composition)
   * **Ops Payment→Charge** (ops↔processor)
4. **Consolidation pass**
   Ship a `graph_to_ledger()` that writes **one** ledger row per real cash movement (bank-timed; no doubles).
5. **Exceptions hooks**
   On ambiguity or misses, open exceptions: `AR_AMBIG`, `NO_MATCH`, `GHOST_AR`, `TIMING`.

If you already have the AR unbundling engine and a subset-sum matcher, you can **reuse it** inside `Charge/Refund/Fee→Payout` unbundling.

---

## Mental model

```
Connectors → Ingestor → raw_event
                 │
              (fingerprints)
                 ▼
            identity  ← identity_link (event→identity)
                 │
             identity_edge (PAYOUT—SETTLES→SETTLEMENT, CHARGE—COMPOSED_OF→PAYOUT, etc.)
                 │
         graph_to_ledger(): bank-timed, no doubles
                 │
             cash_ledger  → Policy/CDM → Weekly plans + Digest
                 └→ Exceptions (for gaps/ambiguity)
```

---

## Data contracts (SQLite-friendly)

> Use TEXT for JSON (`*_json`), and branch on dialect for `json_extract/json_set` if needed.

**raw\_event**

* `id TEXT PK`, `company_id TEXT`,
  `src TEXT` (`PLAID|STRIPE|JOBBERPAY|SQUARE|JOBBER|HCP|BUILD`),
  `kind TEXT` (`BANK_TXN|PAYOUT|BAL_TXN|OPS_PAYMENT|OPS_INVOICE`),
  `external_id TEXT`, `occurred_at TEXT(ISO8601)`,
  `amount_cents INTEGER` (signed; credits +), `currency CHAR(3)`,
  `account_ref TEXT`, `counterparty TEXT`, `mcc TEXT`, `parent_external_id TEXT`,
  `raw_json TEXT`,
  **unique** `(company_id, src, kind, external_id)`.

**identity**

* `id TEXT PK`, `company_id TEXT`, `fingerprint TEXT`, `canonical_kind TEXT`
  (`SETTLEMENT|PAYOUT|CHARGE|FEE|REFUND|INVOICE|PAYMENT`),
  **unique** `(company_id, fingerprint)`.

**identity\_link**

* `id TEXT PK`, `company_id TEXT`, `identity_id TEXT`, `raw_event_id TEXT`,
  `confidence REAL`, `reason TEXT`.

**identity\_edge**

* `id TEXT PK`, `company_id TEXT`,
  `from_identity TEXT`, `to_identity TEXT`,
  `kind TEXT` (`SETTLES|COMPOSED_OF|APPLIES_TO`), `weight REAL`.

**cash\_ledger**

* `id TEXT PK`, `company_id TEXT`, `identity_id TEXT`,
  `posted_at TEXT(ISO8601)`, `direction TEXT` (`INFLOW|OUTFLOW`),
  `amount_cents INTEGER`, `currency CHAR(3)`,
  `cdm_key TEXT NULL`, `policy TEXT NULL`,
  `provenance_json TEXT` (edges, rule versions, matcher reasons).

**exception** (shared)

* `id TEXT PK`, `company_id TEXT`, `kind TEXT`, `status TEXT`,
  `context_json TEXT`, `created_at TEXT`, `resolved_at TEXT NULL`.

---

## Fingerprints (deterministic)

> Collapse the same real-world event across sources.

* **BANK\_TXN (Plaid)** →
  `sha256("SETTLEMENT", bank_account_id, abs(amount), normalize_date(posted_at), merchant_norm)`
* **PAYOUT (Stripe/Square/JobberPay)** →
  `sha256("PAYOUT", provider, payout_id)`
* **BAL\_TXN**

  * `type=payout` → same as payout (links immediately)
  * `type=charge|refund|fee` → `sha256(type, provider, balance_txn_id)`
* **OPS\_PAYMENT** → `sha256("PAYMENT", ops_provider, payment_id)`
* **OPS\_INVOICE** → `sha256("INVOICE", ops_provider, invoice_id)`

Normalize vendors/descriptors to lower, strip punctuation/whitespace, collapse common tokens (“stripe”, “jobber pay”).

---

## Matchers (clean precedence)

### 1) Payout → Settlement (processor → bank)

* **Candidates:** bank credits within `arrival_date ± 2d`, amount close to **net** (`≤$1` tolerance).
* If exactly 1 candidate → `SETTLES` edge (confidence 1.0).
* If >1 → pick nearest posted date, tiebreaker: descriptor similarity; else open `AR_AMBIG` with candidate set.

### 2) Charge/Refund/Fee → Payout (composition)

* Prefer processor’s `balance_txn.payout` / `payout_id` (direct edge `COMPOSED_OF`).
* If missing, time-window within payout batch; if ambiguous set → `AR_AMBIG`.

### 3) Ops Payment → Charge

* Prefer explicit `processor_ref` / metadata.
* Fallback: amount + ±24h + customer/descriptor similarity; ambiguity → exception.

### 4) Invoice ↔ Payment (ops)

* Use native ops linkage. If ops says “paid” but no bank/processor → `GHOST_AR` (exclude from cash).

---

## Consolidation: graph → ledger (count once, bank-timed)

Rules:

* If **Payout** has **Settlement** → **one INFLOW** at **bank posted\_at**, amount = **net**.
  Keep composition edges for explainability; **do not double count**.
* If **processor exists** with **no settlement yet** → track **in-transit** (exclude from cash).
* Direct **BANK\_TXN** without processor links (checks, off-platform) → post inflow/outflow using bank sign.
* **Chargebacks/refunds after settlement** → bank **OUTFLOW**, CDM later maps to `REFUNDS_CHARGEBACKS`.

Minimal pseudo:

```python
def graph_to_ledger(db, company_id, since_iso):
    for payout in identities(kind='PAYOUT', since=since_iso):
        settle = edge_to(payout, 'SETTLES', 'SETTLEMENT')
        if settle:
            write_ledger(settle.posted_at, 'INFLOW', payout.net_cents, prov=edges_trace(payout, settle))
        else:
            mark_in_transit(payout.id)

    for sett in identities(kind='SETTLEMENT', since=since_iso):
        if not has_incoming_edge(sett, 'SETTLES'):
            write_ledger(sett.posted_at, 'INFLOW' if sett.amount_cents>0 else 'OUTFLOW',
                         sett.amount_cents, prov=single_trace(sett))
```

---

## Exceptions (identity graph side)

* `AR_AMBIG` — multiple invoice/charge sets fit a payout (store candidate ids + scores).
* `NO_MATCH` — payout/settlement seen but cannot map composition or ops counterpart.
* `GHOST_AR` — ops shows paid; no processor/bank evidence.
* `TIMING` — payment far outside expected window; flag drift.

The **Tray** resolves these (split/confirm/ignore), and we log decisions with `identity_edge` updates + `provenance_json`.

---

## Services & modules (suggested layout)

```
domains/identity_graph/
  __init__.py
  fingerprints.py          # stable hash funcs
  matchers/
    payout_settlement.py   # processor → bank
    composition.py         # balance txns → payout; unbundling hook
    ops_payment.py         # ops ↔ processor
  graph.py                 # link/write identity & edges
  consolidate.py           # graph → cash_ledger
  exceptions.py            # open/resolve helpers
  routes/                  # optional: /v1/ingest/status, /v1/payouts, etc.
  tests/
    test_fingerprints.py
    test_payout_settlement.py
    test_composition.py
    test_consolidate.py
```

**Where your existing code plugs in**

* Your **subset-sum AR unbundler** (from `domains/ar/services/cash_reconciliation*.py`) can be imported by `matchers/composition.py` to split payout totals to invoices/fees when processors don’t provide line-items.

---

## APIs (minimal, practical)

* `GET /v1/ingest/status` → freshness, dedupe counts, deposits\_reconciled %
* `GET /v1/payouts?from=&to=` → payout nodes + settlement status + ambiguity flags
* `POST /v1/payouts/{id}/split` → confirm/custom mapping (writes edges)
* `GET /v1/exceptions?status=open` → identity-side exceptions
* (Consolidation runs via worker or endpoint):
  `POST /v1/consolidate?since=` → graph\_to\_ledger + summary

---

## Testing checklist

* **Fingerprints**

  * Same real event across sources collapses (bank vs processor vs ops).
  * Different merchants same day same amount **don’t** collide (include merchant\_norm).
* **Payout→Settlement**

  * Exact net match within ±2d → single candidate; multi-candidate → tie rules; no candidate → in-transit.
* **Composition unbundling**

  * Unique subset → auto; multiple subsets → `AR_AMBIG`; fees handled; refunds negative.
* **Consolidation**

  * No double counting; settlement date is cash timing; composition preserved only in provenance.
* **Exceptions**

  * Inserted once per context; resolving updates edges and clears exceptions.

---

## Gotchas

* **Bank batching**: One payout landing as **two bank credits** → link both partials to one settlement identity; sum must equal net.
* **Fee day shift**: Fees settling different day → keep under payout composition; do not create separate outflow if net is already recognized at bank.
* **Timezone**: Store UTC, display in company TZ; date windows use local midnight.
* **Idempotency**: All ingest writes must be idempotent on `(company_id, src, kind, external_id)`; linking re-runs safe.
* **JSON in SQLite**: Use TEXT but keep paths consistent (`policy_debug`, `edges`, `reasons`) so migrations to Postgres are trivial.

---

## Example: using from a worker

```python
from sqlalchemy.orm import Session
from domains.identity_graph import fingerprints, graph
from domains.identity_graph.consolidate import graph_to_ledger

def on_new_events(db: Session, company_id: str, new_raw_events: list):
    # 1) upsert raw_event rows (idempotent)
    # 2) compute fingerprints → create identities + identity_link
    # 3) run matchers to add identity_edge rows
    # 4) consolidate to cash_ledger
    updated = graph_to_ledger(db=db, company_id=company_id, since_iso="2025-01-01T00:00:00Z")
    return updated
```

---

## KPIs (graph health)

* `% deposits reconciled` (payouts with settlements / all payouts)
* `% cash by value reconciled` (ledger rows backed by graph edges)
* `exceptions_open` and median time-to-resolution
* `in_transit_payouts` count and aging

---

With this in place, **Cashola** gets a deterministic, explainable spine: **events → identities → edges → ledger**, guaranteed **no double counting**, and ready for the **CDM/Policy** pass and the **Friday Digest**.
