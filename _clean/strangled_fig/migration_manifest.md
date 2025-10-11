You’re right—you need a **fully comprehensive, file-aware recovery plan** that matches your repo, not a hand-wave. Here’s a concrete **Strangler Migration Manifest (QBO MVP)** that says exactly what to **add new**, what to **bring over (cleansed)**, what to **refactor in flight**, and what to **leave out for now**—including the **transaction log** and **smart sync** pieces.

---

# RowCol Strangler Migration Manifest — QBO MVP (Bills, Invoices, Balances)

**Goal:** Create a clean MVP nucleus (can be in-place or in a `mvp_qbo/` package) with the seam `runway → domains → infra`, using:

* **State Mirror (mutable)**
* **Transaction Log (append-only)**
* **Smart Sync Orchestrator** (freshness + idempotency, light retries)
* **QBO only**: Bills, Invoices, Balances (read-only ledger hub)

## **Core Decisions Made (CONCRETE)**

### **1. Transaction Log Strategy: Hybrid Approach**
- **Keep existing domain-specific tables** for current data (`BillTransactionLog`, `VendorTransactionLog`, etc.)
- **Create new generic `integration_log` table** for new sync orchestrator
- **Migration path**: Gradually move new operations to generic table
- **Why**: Preserves existing data, allows clean new implementation

### **2. Sync Orchestrator Interface: Policy-Driven Facade (CONCRETE)**
- **Keep `BaseSyncService.execute_sync_call()`** as the low-level workhorse
- **Add `SyncOrchestrator` facade** with concrete interface:
  - `read_refresh(entity, client_id, hint, mirror_is_fresh, fetch_remote, upsert_mirror, read_from_mirror, on_hygiene)`
  - `write_idempotent(operation, client_id, idem_key, call_remote, optimistic_apply, on_hygiene)`
- **Use entity policy table** for TTLs per entity type
- **Enforce log → mirror order** and error → hygiene mapping

### **3. Advisor-First Model: Primary Identifier (CONCRETE)**
- **`advisor_id` is the primary identifier** (not `client_id` or `business_id`)
- **`business_id` is foreign key** to business (QBO realm)
- **All queries filtered by `advisor_id` first**, then `business_id`
- **Authentication context**: `advisor_id` → `business_id` mapping
- **Database schema**: All tables include `advisor_id` and `business_id` columns

Use the **Action Legend** to guide Cursor:

* **ADD** = net-new file (tiny & focused)
* **PORT** = copy from legacy and cleanse (keep only what MVP needs)
* **ADAPT** = thin wrapper around existing code (keep logic, expose new interface)
* **REF** = refactor in place (light edits, same file)
* **DROP** = leave out for MVP

---

## A) Net-New Adds (the minimum seam)

These are small but non-negotiable so Runway never touches rails again.

**Domains (interfaces only)**

* **ADD** `domains/ap/gateways.py`

  * `class BillsGateway(Protocol): list(q), schedule_payment(...)`
* **ADD** `domains/ar/gateways.py`

  * `class InvoicesGateway(Protocol): list(q)`
* **ADD** `domains/bank/gateways.py`

  * `class BalancesGateway(Protocol): get(q)`
* **ADD** `domains/ap/repositories.py`

  * `BillsMirrorRepo`, `PaymentsMirrorRepo`, `LogRepo` (interfaces)
* **ADD** `domains/ar/repositories.py`

  * `InvoicesMirrorRepo` (interface)

**Infra (implementations)**

* **ADD** `infra/gateways/ap_qbo_gateway.py`

  * Implements `BillsGateway` using QBO client + Sync Orchestrator + LogRepo + MirrorRepo.
* **ADD** `infra/gateways/ar_qbo_gateway.py`

  * Implements `InvoicesGateway`.
* **ADD** `infra/gateways/bank_qbo_gateway.py` (if you keep QBO-only balances)

  * Implements `BalancesGateway` (best-effort from QBO).
* **ADD** `infra/repos/ap_repo.py`

  * Implements `BillsMirrorRepo`, `PaymentsMirrorRepo`.
* **ADD** `infra/repos/ar_repo.py`

  * Implements `InvoicesMirrorRepo`.
* **ADD** `infra/repos/log_repo.py`

  * Implements `LogRepo` (append-only integration_log).
* **ADD** `infra/sync/orchestrator.py`

  * Minimal strict refresh, TTLs, idempotency helper (can leverage your enums).
* **ADD** `infra/db/schema.sql`

  * `integration_log`, `mirror_bills`, `mirror_invoices`, `mirror_payments` (tables).
* **ADD** `runway/wiring.py`

  * Composition root: binds domain interfaces → infra implementations.
* **ADD** `runway/services/runway_orchestrator.py`

  * Builds snapshot using gateways + your existing calculators.

**Guards**

* **ADD** `.cursorrules` (+ CI script) to restrict edits/imports to the MVP lane and block `runway` from importing `infra.qbo`, `infra.jobs`, etc.

---

## B) Bring Over, Cleansed (PORT)

Keep the good stuff, but **copy only the parts** needed for Bills/Invoices/Balances.

**QBO client & mapping**

* **PORT** `infra/qbo/client.py` → `infra/rails/qbo/client.py`

  * Keep auth + endpoints for: `list_bills`, `post_bill_payment`, `list_invoices`, (optional) account/balance reads.
  * Drop unused endpoints for MVP.
* **PORT** `infra/qbo/qbo_mapper.py` + `infra/qbo/dtos.py` → `infra/rails/qbo/mappers.py`

  * Keep DTOs/mappers used by the 3 entities only.

**DB session**

* **PORT** `infra/database/session.py`

  * Reuse engine/session creation.

**Transaction log**

* **PORT (option A)** `domains/core/services/transaction_log_service.py` → fold into `infra/repos/log_repo.py` implementing `LogRepo` interface (prefer 1 generic `integration_log` table).
* **PORT (option B)** If you must keep domain-specific log tables under `domains/ap/models_trans/*`, still expose them through **one** `LogRepo` interface and hide specifics in the repo impl.

---

## C) Adapt (thin wrappers to reuse your smart sync)

You already have robust sync pieces. We’ll **wrap**, not rewrite.

**Smart sync core**

* **ADAPT** `infra/jobs/base_sync_service.py` → used **inside** `infra/sync/orchestrator.py`

  * Keep dedupe/idempotency and light retries.
  * Expose a **tiny** API the gateways call:

    * `read_refresh(entity, client_id, fetch_fn) -> raw_data, version`
    * Handles: TTL check, fetch, **INBOUND log**, mirror upsert.
    * For MVP, you can **skip background scheduling**; run “simple mode.”
* **ADAPT** `infra/jobs/enums.py` / `infra/jobs/sync_strategies.py` → if helpful for mapping `STRICT/CACHED_OK` to your strategies.
* **ADAPT (later)** nightly recon: you can re-use a subset of `job_scheduler.py`/`job_storage.py` **or** create a simple CLI command for a single nightly pass. For MVP, defer heavy scheduling.

**Existing mirror models**

* You have mirror-ish models in `infra/database/models.py` and domain models in `domains/*/models/*`.

  * **ADAPT** repos to upsert into whichever mirror table set is already wired/easiest.
  * Avoid duplicating mirrors in domains; keep physical tables under `infra/database` and expose via **repo impls in `infra/repos/*`**.

---

## D) Refactor In-Flight (REF)

Small, surgical edits where you already have pieces.

* **REF** `domains/qbo/services/sync_service.py` (if present):

  * Do **not** instantiate it from domains anymore.
  * Extract any still-useful helpers into `infra/sync/orchestrator.py` and call them **only from infra gateways**.

* **REF** `domains/*/services/*.py` (AP/AR)

  * If these currently call rails/sync directly, adjust them to depend on **gateway interfaces** instead.
  * Over time, move any pure product/value logic to **Runway calculators**.

* **REF** `runway/routes/*.py` (console/digest/tray)

  * Swap imports from legacy “data_orchestrators” to **runway_orchestrator** + gateway wiring.
  * Start with one route (console), then expand.

---

## E) Leave Out for MVP (DROP)

These stay in legacy; do not import from the MVP lane.

* `runway/services/data_orchestrators/*` (deprecated: replaced by gateway + runway_orchestrator)
* `infra/jobs/job_scheduler.py`, `infra/jobs/job_storage.py` (complex scheduler; bring back after MVP if needed)
* `infra/qbo/qbo_sync_jobs.py`, `infra/qbo/qbo_sync_scheduler.py` (same reason)
* Non-QBO rails: `infra/plaid/*`, `infra/ramp/*`, `infra/stripe/*`
* Cross-rail vendor identity graph; advanced reconciliation beyond “nightly” pass
* `webhooks/routes.py` (optional: keep a stub endpoint but MVP can rely on poll/recon)

---

## F) Transaction Log, State Mirror, Cache — exact rules

**Transaction Log (append-only, durable)**

* **Always log writes** (OUTBOUND intent + result).
* **Log STRICT reads** as INBOUND when they hit the rail.
* Columns: `direction, rail, operation, idem_key, http_code, status, payload_json, source_version, client_id, created_at`.

**State Mirror (mutable)**

* Tables: `mirror_bills`, `mirror_invoices`, `mirror_payments`.
* Upsert on STRICT or recon; read path returns **from mirror** (even after refresh).
* Store `source_version` and `last_synced_at`.

**Cache (optional)**

* In-memory/Redis. Flush anytime. Never replaces the log. Fine to omit for MVP.

---

## G) Gateways — method contracts (for Cursor to generate against)

```python
# domains/ap/gateways.py
class BillsGateway(Protocol):
    def list(self, q: ListBillsQuery) -> list[Bill]: ...
    def schedule_payment(self, client_id: str, bill_id: str, amount: Decimal, pay_on: date) -> str: ...

# domains/ar/gateways.py
class InvoicesGateway(Protocol):
    def list(self, q: ListInvoicesQuery) -> list[Invoice]: ...

# domains/bank/gateways.py
class BalancesGateway(Protocol):
    def get(self, q: BalancesQuery) -> list[AccountBalance]: ...
```

> **Infra gateway impl rule:** For reads with `STRICT` **or** stale mirror → call QBO → **append INBOUND log** → **upsert mirror** → return mirror.
> For writes → **append OUTBOUND intent** → call QBO (idempotent) → **append OUTBOUND result** → optimistic mirror update (confirmed by recon/webhook).

---

## H) Concrete mapping from *your* tree (what to do with each area)

### `infra/qbo/*`

* `auth.py`, `client.py`, `dtos.py`, `qbo_mapper.py`, `utils.py` → **PORT** essentials only into `infra/rails/qbo/*`.
* `health.py`, `setup.py`, broad configs → **DROP** for MVP.

### `infra/jobs/*`

* `base_sync_service.py`, `enums.py`, `sync_strategies.py` → **ADAPT** (use inside `infra/sync/orchestrator.py`).
* `job_scheduler.py`, `job_storage.py` → **DROP** (MVP); re-evaluate post-MVP.

### `infra/database/*`

* `session.py`, `base.py`, `models.py` → **PORT/ADAPT** as needed for mirror tables.
* `transaction.py` → **DROP** unless it’s your generic integration_log; prefer **one** `log_repo.py`.

### `domains/ap/*`

* `models/*` → **ADAPT**: use as source for Mirror shape if aligned; otherwise keep domain models separate from physical mirror models.
* `models_trans/*` → **DROP** for MVP **unless** you rely on them for log storage; if so, hide them behind `LogRepo`.
* `services/*.py` → **REF** to consume gateway interfaces **or** **DROP** from MVP path.
* `routes/*` → **DROP** (HTTP belongs in Runway).
* `schemas/*` → **KEEP** if used by Runway DTOs; otherwise **DROP**.

### `domains/ar/*`, `domains/bank/*`

* Same pattern as AP: **ADD** gateway interfaces; **ADAPT** models; avoid direct rails usage.

### `domains/core/services/transaction_log_service.py`

* **PORT** into `infra/repos/log_repo.py` (or wrap it) and expose `LogRepo` interface. Ensure it supports both OUTBOUND and INBOUND entries + `source_version`.

### `domains/qbo/services/sync_service.py`

* **REF**: extract helpers to `infra/sync/orchestrator.py`. Do **not** instantiate from domains anymore.

### `runway/*`

* `services/calculators/*` → **KEEP**
* `services/data_orchestrators/*` → **DROP** (deprecated)
* `routes/*` → **REF** one route (console) first to go through `runway_orchestrator` + gateways
* `core/data_orchestrators/*` → **DROP** for MVP

### `plaid/*`, `ramp/*`, `stripe/*`

* **DROP** (MVP is QBO only)

### `webhooks/routes.py`

* **DROP** or keep a **stub** (MVP can rely on recon)

---

## I) “Simple mode” config for MVP (so you don’t fight infra)

* `SYNC_ENABLE_RETRY=false` (or retry=1)
* `SYNC_ENABLE_DEDUP=true` (writes)
* `SYNC_CACHE_TTL_BILLS=900`, `SYNC_CACHE_TTL_INVOICES=900`, `SYNC_CACHE_TTL_BALANCES=120`
* `SYNC_SCHEDULER_ENABLED=false` (no background churn)
* `SYNC_NIGHTLY_RECON_HOUR=03` (optional single pass)
* `STRICT_ON_SNAPSHOT=true`

---

## J) Acceptance Tests (must pass before you let Cursor roam)

1. **STRICT beats cache → mirror is updated** (Bills/Invoices).
2. **Idempotent bill payment** (two identical approvals → one rail payment).
3. **Throttle hygiene** (QBO 429 → bounded retry → hygiene flag visible).
4. **Recon without webhook** (change in QBO → recon logs INBOUND → mirror reflects).
5. **Stale mirror hygiene** (hard TTL breach shows a flag but returns last known mirror).

---

### Bottom line

* Transaction log: **IN** (generic `integration_log`, via `LogRepo`).
* State mirror: **IN** (mirror tables + repos).
* Smart sync: **IN**, but **wrapped** inside infra gateways (domains don’t instantiate it; runway never sees it).
* Runway calculators: **IN** (that’s your product value).
* Data orchestrators (legacy): **OUT** (replaced by gateways).

If you want, I can also draft a one-page **“Move Plan”** per file with concrete commit steps (old path → new path + TODOs).
