

# Policy (CDM + Rules + Profiles) README

**Purpose.** The policy layer turns raw, reconciled cash events into **Cash Decision Model (CDM)** categories and **policy labels** (`MUST_PAY | CAN_DELAY | DISCRETIONARY`) that power the weekly plan (runway, AR/AP suggestions) and the Exceptions Tray learning loop.

It is **configuration-driven** per company via a `PolicyProfile`, with **vertical specializations** (e.g., ServicePro) implemented as pluggable engines that extend a small, stable core.

---

## TL;DR: What you may need to change

1. **PolicyProfile fields**

   * Ensure the model has (or add) these columns/JSON fields:

     * `vertical` (e.g., `"servicepro"`, `"property_mgmt"`)
     * `confidence_high`, `confidence_low`, `delta_gap`
     * `cdm_overrides` (JSON: vendor/account → `cdm_key`/`policy`)
     * `collect_prob_by_age` (JSON: `{"0_7":0.8,"30_60":0.4,"60_plus":0.2}`)
     * `must_pay_vendors` / `can_delay_vendors` (arrays, optional)
     * `timing_tolerance_days`, `fee_tolerance_cents` (optional)
2. **Factory wiring**

   * Add `domains/policy/services/factory.py` with `get_policy_engine(firm_id, db)` that reads the firm’s `PolicyProfile.vertical` and returns the **right engine** (base or vertical subclass).
3. **Base + vertical engine classes**

   * Keep your existing `PolicyEngineService` as **Base** (generic rules/templates, vendor categories).
   * Create `verticals/servicepro_engine.py` subclass that overrides/extends categorization heuristics (your contractor/vendor rules).
4. **Cash Ledger adapter**

   * Ensure `PolicyEngineService.categorize_ledger_rows(...)` exists (the batch mapper from ledger rows → `cdm_key`, `policy`, or an `UNMAPPED` exception).
5. **Exceptions integration**

   * Confirm your `exception` table has `kind='UNMAPPED'` and can store `context_json` with `ledger_id` for policy misses.
6. **Remove GL-first assumptions (optional)**

   * If you still have COA/GL centric names, keep them **as hints only**; the **CDM is truth** for weekly decisions.

If the above already exists in your repo (or you added it per the last step), you’re good. Everything else below is how to use/extend it.

---

## Mental model

```
reconciled cash (cash_ledger)
   │
   ▼
Policy Engine (base or vertical), guided by PolicyProfile
   │      ├─ rule templates / runtime rules
   │      ├─ vendor/category heuristics
   │      ├─ per-vertical overrides
   ▼
cdm_key + policy on cash_ledger rows
   │
   ├─ Weekly plans (runway, AR/AP)
   └─ Exceptions (UNMAPPED) → user decisions → new rules → re-norm
```

---

## Key pieces

### 1) PolicyProfile (per-company knobs)

* **What it is:** The single source of truth for policy config.
* **What it controls:** thresholds, vertical selection, vendor overrides, fee/timing tolerances, AR plan knobs, collect probabilities.
* **How engines use it:** engines **read only**; UI/services write via `PolicyProfileService`.

### 2) Base Policy Engine

* Lives at `domains/policy/services/policy_engine.py`.
* Responsibilities:

  * Run **template/runtime rules** (your existing DB-backed rules).
  * Fallback **vendor category** lookup.
  * Map `(account/category/vendor)` → `(cdm_key, policy)` using deterministic heuristics **plus** `Profile.cdm_overrides`.
  * Batch adapter: `categorize_ledger_rows(company_id, since_iso, ...)`.

### 3) Vertical Engines (plug-ins)

* Example: `domains/policy/services/verticals/servicepro_engine.py`.
* Responsibilities:

  * Override/extend categorization where a vertical has better priors (e.g., ServicePro contractor/vendor patterns).
  * Still call **base** for final CDM mapping so policy labels remain consistent.
* Selection via `factory.get_policy_engine(firm_id, db)`.

### 4) Rules (templates + runtime)

* Templates: `PolicyRuleTemplate` (global playbooks, versioned/prioritized).
* Runtime: `Rule` (customer/firm-specific rules created from tray decisions).
* **Precedence:** runtime overrides → template → vendor category → default.
* **Learning loop:** 3 consistent manual decisions ⇒ propose rule (stored → preview → publish).

---

## Data flow with cash\_ledger

1. Reconciliation writes **one** cash\_ledger row per real cash effect (bank-timed).
2. A periodic job (or on-ingest hook) calls:

   ```py
   engine = get_policy_engine(firm_id, db)
   n = engine.categorize_ledger_rows(company_id=firm_id, since_iso=...)
   ```
3. For each row:

   * Engine computes `(cdm_key, policy)`, writes them to `cash_ledger`.
   * If it can’t classify ⇒ inserts `UNMAPPED` exception with `{ledger_id,...}` context.
4. Tray resolves `UNMAPPED` ⇒ can create a rule; publish re-norms last N days.

---

## How CDM mapping works (MVP)

* **Inflows:** `CUSTOMER_RECEIPTS`, `REFUNDS_CHARGEBACKS`, `OTHER_INCOME`
* **Outflows:** `PAYROLL_TOTAL`, `RENT_UTILITIES`, `INSURANCE`, `SAAS_FEES`, `DEBT_SERVICE`, `TAXES_GOVT`, `OWNER_DRAWS`, `CAPEX`, `OTHER`
* **Policy labels:** `MUST_PAY` / `CAN_DELAY` / `DISCRETIONARY`

Mapping order:

1. `Profile.cdm_overrides` (vendor/account exact hits)
2. Vertical hints (e.g., “Stripe fee” → `SAAS_FEES / CAN_DELAY`)
3. Base heuristics (keywords on account/category/vendor)
4. Default: `OTHER / CAN_DELAY` (and log weak confidence) or open `UNMAPPED`

---

## Extending to a new vertical (recipe)

1. Add an engine file:

   ```
   domains/policy/services/verticals/property_mgmt_engine.py
   ```

   ```py
   from domains.policy.services.policy_engine import PolicyEngineService

   class PropertyMgmtPolicyEngine(PolicyEngineService):
       def categorize_vertical_first(self, txn: dict) -> dict:
           # stronger hints for HOA/tenant/PM vendors, utilities schedules, etc.
           return super().categorize_transaction(txn, self.firm_id)
   ```

   (You can override a `categorize_vertical_first` method and have base fall back.)
2. Add vertical value to `PolicyProfile.vertical` and wire factory:

   ```py
   if v in {"property_mgmt","buildium","entrata"}:
       return PropertyMgmtPolicyEngine(db, firm_id=firm_id)
   ```
3. Add any vertical-specific rule templates and tests.

---

## Exceptions loop (policy side)

* `UNMAPPED` (policy): ledger row lacks `(cdm_key, policy)`.
* Tray actions:

  * Assign CDM category + policy for this row.
  * **Create rule** (runtime) from the decision (exact/regex/vendor).
  * Re-norm last N days in background.
* Goal: **≥95% by value** categorized before enabling weekly digest.

---

## Testing checklist

* **Determinism:** same inputs → same `(cdm_key, policy)`.
* **Precedence:** runtime > template > vertical > base > vendor category > default.
* **SQLite friendliness:** JSON updates use `json_set` / `json_extract` when available; otherwise store blob.
* **Backfill safety:** `categorize_ledger_rows` idempotent; no duplicate exceptions for same `ledger_id`.
* **Profile thresholds:** raising/lowering `confidence_high/low` changes auto vs exception behavior predictably.

---

## Example: calling the engine

```python
from sqlalchemy.orm import Session
from domains.policy.services.factory import get_policy_engine

def on_new_ledger_rows(db: Session, firm_id: str, since_iso: str):
    engine = get_policy_engine(firm_id, db)
    updated = engine.categorize_ledger_rows(company_id=firm_id, since_iso=since_iso, firm_id=firm_id)
    return updated
```

---

## Gotchas

* **Firm vs Company IDs:** be consistent—if they’re the same in dev, keep one alias, but make the engine accept both params.
* **GL bias:** Do not block classification on a COA; treat GL labels as hints only. CDM is the contract.
* **Threshold drift:** If you tune defaults in code, mirror them in `PolicyProfile` so tenants can override without redeploys.
* **Vendor aliasing:** Normalize vendor names before applying `cdm_overrides` (lowercase, strip punctuation).

---

## Directory map (quick)

```
domains/policy/
  models/
    policy_profile.py         # per-company knobs
    rule.py, suggestion.py,
    correction.py             # rules + learning artifacts
  services/
    policy_engine.py          # Base engine (your existing class, plus ledger adapter)
    factory.py                # choose engine by PolicyProfile.vertical
    verticals/
      servicepro_engine.py    # Contractor-specific overrides (your vendor rules)
  routes/                     # (optional) policy endpoints
  schemas/                    # pydantic DTOs
  README.md                   # this file
```

---

## Migration note (dev on SQLite)

* You don’t need Alembic now; just ensure:

  * `policy_profile` has the fields above (add JSON/text columns if missing).
  * `cash_ledger` includes `cdm_key TEXT NULL`, `policy TEXT NULL`, `provenance_json TEXT/JSON NULL`.
  * `exception` table supports `kind TEXT`, `status TEXT`, `context_json TEXT/JSON`.
* Where JSON functions differ, the engine already branches on dialect (`sqlite` vs others).

---

That’s it. With the profile + factory in place, your **existing** policy engine becomes the **Base**, your contractor rules live cleanly in the **ServicePro** subclass, and adding new verticals is just one file and one factory case—no “stuff everywhere.”
