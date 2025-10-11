Here’s the **long-lived architecture brief (“vaccine” doc)** you can drop into a repo (or a brand-new one). It tells Cursor exactly what to keep, what to ignore, and how to rebuild the **QBO-only MVP** around the **infra → domains → runway** seam with a **Sync Orchestrator + Transaction Log + State Mirror**. It also encodes guards so the IDE can’t drift.

---

# RowCol — MVP QBO Strangler Plan (Cursor Handbook)

**Purpose (read me first):**
We are carving a **minimal, safe MVP** from a large codebase. The MVP is **QBO-only** and includes: **Bills**, **Balances**, **Invoices**. It must retain the **Sync Orchestrator**, a **Transaction Log (append-only)**, and a **State Mirror (mutable)**.
We are enforcing a clean seam: **runway/** → **domains/** → **infra/**. Cursor must not cross that seam.

---

## 0) Scope & Non-Negotiables

* **MVP Features:**

  * Read: QBO **Bills**, **Invoices**, **Balances** (bank account balances if available via QBO; Plaid comes *later*).
  * Write: Approve/Schedule **Bill Payment** (idempotent).
  * Views: One combined **Digest/Console/Hygiene** page.

* **Architecture:**

  * **Runway (product)**: orchestration & product calculators (business value), DTOs, HTTP routes.
  * **Domains (rail-agnostic contracts)**: gateway interfaces + domain models + repo interfaces (mirror/log).
  * **Infra (implementations)**: QBO client/mapper, **Sync Orchestrator**, **Transaction Log repo**, **Mirror repos**, DB session.

* **Data Stores:**

  * **Transaction Log (append-only, durable)**: outbound intents + inbound facts (webhook/poll).
  * **State Mirror (mutable)**: current, denormalized rows for fast reads.
  * **Cache (ephemeral)**: optional, safe to flush, never a source of truth.

* **Dependency direction:**
  `runway/ → domains/ → infra/` (no back edges, ever).

---

## 1) Folder Layout (MVP nucleus)

```
mvp_qbo/
  pyproject.toml         # (or requirements.txt)
  .cursorrules           # edit-scope guard (see below)
  scripts/
    ci_guard.sh          # blocks edits outside MVP lane
  src/
    mvp_qbo/
      api/
        routes.py        # FastAPI endpoints: /snapshot, /approve
      services/
        runway_orchestrator.py  # composes gateways + calculators
        calculators/            # (existing product math you keep)
      schemas/
        dto.py
      wiring.py          # composition root (bind interfaces→impls)
      domains/
        ap/
          models.py
          gateways.py          # interfaces (BillsGateway, PaymentsGateway)
          repositories.py      # interfaces (BillsMirrorRepo, PaymentsMirrorRepo, LogRepo)
        ar/
          models.py
          gateways.py          # InvoicesGateway
          repositories.py
        bank/
          models.py
          gateways.py          # BalancesGateway
          repositories.py
      infra/
        db/
          session.py
          schema.sql           # tables: integration_log, mirror_bills, mirror_invoices, mirror_payments
        repos/
          ap_repo.py    # implements BillsMirrorRepo/PaymentsMirrorRepo
          ar_repo.py    # implements Invoices mirror
          log_repo.py   # implements LogRepo
        rails/
          qbo/
            client.py          # QBO auth/client
            mappers.py         # QBO DTO → domain
        sync/
          orchestrator.py      # freshness, idempotency key helper, strict-refresh flow
```

> **Note:** This is a **new nucleus**. We will copy only a curated subset of files from the old repo into `mvp_qbo/src/mvp_qbo/infra/...` (see Whitelist below). Everything else stays behind.

---

## 2) Who does what (precise)

### Runway layer

* **routes.py**: HTTP handlers (FastAPI).
* **runway_orchestrator.py**: composes domain gateways (+ product calculators) to build the **Snapshot** (Digest/Console/Hygiene).
* **calculators/**: *product* math (runway buffer, priorities). These belong in Runway, not in domains or infra.

### Domains layer (contracts only)

* **gateways.py**: rail-agnostic interfaces.

  * `BillsGateway.list(q), BillsGateway.schedule_payment(...)`
  * `InvoicesGateway.list(q)`
  * `BalancesGateway.get(q)`
* **repositories.py**: mirror + log **interfaces** only.

### Infra layer (implementations)

* **rails/qbo/**: QBO client + mappers (no business rules).
* **sync/orchestrator.py**: strict-refresh logic, TTL policy, idempotency key.
* **repos/**: SQLite implementations for **Mirror** and **Transaction Log**.
* **db/schema.sql**: 3–4 tables created here.

---

## 3) Data Flow (MVP rules)

### Read (default CACHED_OK; STRICT at experience edge)

1. Runway → Domains(Gateway) → Domains(Repo Mirror).
2. If `freshness_hint=STRICT` **or** mirror stale:
   a) Infra.Sync fetch from QBO,
   b) **append INBOUND** to **Transaction Log**,
   c) **upsert Mirror**,
   d) return from Mirror.

### Write (approve/schedule payment)

1. Runway → Domains(Gateway).
2. Infra.Log **OUTBOUND intent** with **idempotency key**.
3. Call QBO; log result.
4. Optimistically update Mirror; confirm later via webhook/recon (post-MVP if webhooks remain flaky, do nightly recon).

### Sync (webhooks/recon)

* Infra handler → **INBOUND log** → Mirror upsert.
* Hygiene flags are produced in Runway if mirrors are stale or last sync failed.

---

## 4) Where business logic lives (your concern addressed)

* **Runway** holds **product calculators** (runway buffer math, priority, insights). That’s correct.
* **Domains** do **data orchestration contracts**: they define *what* data is needed (Bills, Invoices, Balances) and provide a stable interface.
* **Infra** does **how** to get it (QBO adapters, sync, retries, log/mirror writes).

> In other words: your current “data orchestrators” that *fetch and shape data for Runway* should become **domain gateways** (interfaces) + **infra gateway implementations** (QBO), while the *business/value math* stays in **Runway calculators**.

---

## 5) File Selection — What to Bring (Whitelist) vs Skip (Blacklist)

> Cursor: copy **only** the items below into `mvp_qbo/src/mvp_qbo/infra/...`. Everything else stays in the legacy repo.

### Whitelist (copy now; minimal)

* **QBO client & mapping** (read/write only; no feature sprawl)

  * `infra/qbo/client.py` (or your equivalent) → `infra/rails/qbo/client.py`
  * `infra/qbo/qbo_mapper.py` and `infra/qbo/dtos.py` → `infra/rails/qbo/mappers.py`
  * Minimal `infra/qbo/auth.py` if needed for tokens
* **Sync core (adapted)**

  * Your `infra/jobs/base_sync_service.py` (or `base_sync_service.py`) **only if** it’s reasonably self-contained. Otherwise, create a **tiny** `sync/orchestrator.py` with: strict-refresh, TTL policy, idempotency helper, and a light retry.
* **SQLite session**

  * `infra/database/session.py` (or a 20-line replacement)
* **Transaction Log + Mirror repos**

  * Port just the pieces needed for 3 tables (below)

### Blacklist (do **not** bring into MVP nucleus)

* `runway/services/data_orchestrators/*` (deprecated; replaced by gateways)
* `infra/qbo/*` not needed for Bills/Invoices/Payments auth/DTOs
* `infra/jobs/job_scheduler.py`, `job_storage.py`, **priority queues** (post-MVP)
* Non-QBO rails (Plaid, Ramp, Stripe)
* Cross-rail identity graphs, advanced reconciliation utilities
* Legacy routes under domains/*/routes (HTTP belongs in Runway)

---

## 6) DB Schema (SQLite, minimal)

```sql
-- Append-only transaction log (audit, retry/replay)
CREATE TABLE IF NOT EXISTS integration_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  direction TEXT CHECK(direction IN ('OUTBOUND','INBOUND')) NOT NULL,
  rail TEXT NOT NULL,           -- 'qbo'
  operation TEXT NOT NULL,      -- 'list_bills', 'post_bill_payment'
  idem_key TEXT,                -- stable key for writes
  http_code INTEGER,
  status TEXT,                  -- 'OK','RETRY','FAILED'
  payload_json TEXT,            -- raw rail payload
  source_version TEXT,          -- etag or change token if available
  client_id TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- State mirrors (fast reads)
CREATE TABLE IF NOT EXISTS mirror_bills (
  bill_id TEXT PRIMARY KEY,
  client_id TEXT NOT NULL,
  vendor_id TEXT,
  due_date TEXT,
  amount NUMERIC,
  status TEXT,                  -- 'OPEN','SCHEDULED','PAID'
  source_version TEXT,
  last_synced_at DATETIME
);

CREATE TABLE IF NOT EXISTS mirror_invoices (
  invoice_id TEXT PRIMARY KEY,
  client_id TEXT NOT NULL,
  customer_id TEXT,
  due_date TEXT,
  amount NUMERIC,
  status TEXT,                  -- 'OPEN','PARTIAL','PAID'
  source_version TEXT,
  last_synced_at DATETIME
);

CREATE TABLE IF NOT EXISTS mirror_payments (
  payment_id TEXT PRIMARY KEY,
  bill_id TEXT,
  client_id TEXT NOT NULL,
  amount NUMERIC,
  paid_on TEXT,
  source_version TEXT,
  last_synced_at DATETIME
);
```

---

## 7) Interfaces (keep tiny and stable)

**domains/ap/gateways.py**

```python
from typing import Protocol, List, Literal
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

class Bill(BaseModel):
    id: str
    vendor_id: str | None = None
    due_date: date | None = None
    amount: Decimal
    status: Literal["OPEN","SCHEDULED","PAID"]

class ListBillsQuery(BaseModel):
    client_id: str
    status: Literal["OPEN","ALL"] = "OPEN"
    freshness_hint: Literal["CACHED_OK","STRICT"] = "CACHED_OK"

class BillsGateway(Protocol):
    def list(self, q: ListBillsQuery) -> List[Bill]: ...
    def schedule_payment(self, client_id: str, bill_id: str, amount: Decimal, pay_on: date) -> str: ...
```

**domains/ar/gateways.py**

```python
from typing import Protocol, List, Literal
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

class Invoice(BaseModel):
    id: str
    customer_id: str | None = None
    due_date: date | None = None
    amount: Decimal
    status: Literal["OPEN","PARTIAL","PAID"]

class ListInvoicesQuery(BaseModel):
    client_id: str
    status: Literal["OPEN","ALL"] = "OPEN"
    freshness_hint: Literal["CACHED_OK","STRICT"] = "CACHED_OK"

class InvoicesGateway(Protocol):
    def list(self, q: ListInvoicesQuery) -> List[Invoice]: ...
```

**domains/bank/gateways.py**

```python
from typing import Protocol, List, Literal
from pydantic import BaseModel

class AccountBalance(BaseModel):
    account_id: str
    available: float

class BalancesQuery(BaseModel):
    client_id: str
    freshness_hint: Literal["CACHED_OK","STRICT"] = "CACHED_OK"

class BalancesGateway(Protocol):
    def get(self, q: BalancesQuery) -> List[AccountBalance]: ...
```

**repositories.py** (pattern)

```python
from typing import Protocol, List, Any
from datetime import datetime

class BillsMirrorRepo(Protocol):
    def list_open(self, client_id: str) -> list[Any]: ...
    def upsert_many(self, client_id: str, raw: list[dict], source_version: str | None, synced_at: datetime): ...

class LogRepo(Protocol):
    def append(self, *, direction: str, rail: str, operation: str, client_id: str,
               idem_key: str | None = None, http_code: int | None = None,
               status: str | None = None, payload_json: str | None = None,
               source_version: str | None = None) -> None: ...
```

---

## 8) Composition Root (runway/wiring.py)

* Instantiate `QBOClient`, `SyncOrchestrator`, `LogRepo`, and mirror repos.
* Build `BillsGateway`/`InvoicesGateway`/`BalancesGateway` implementations in **infra/gateways/**.
* Inject gateways into `RunwayOrchestrator`.

> **Runway must only import domain interfaces + wiring.** Never import rails or sync from Runway.

---

## 9) Operational Mode Flags (“simple mode” for MVP)

Set via env:

```
SYNC_ENABLE_RETRY=false         # or 1 retry
SYNC_ENABLE_DEDUP=true          # writes
SYNC_CACHE_TTL_BILLS=900        # 15 min
SYNC_CACHE_TTL_INVOICES=900
SYNC_CACHE_TTL_BALANCES=120
SYNC_SCHEDULER_ENABLED=false    # no background churn yet
SYNC_NIGHTLY_RECON_HOUR=03      # one recon pass nightly
STRICT_ON_SNAPSHOT=true         # strict freshness at experience edge
```

---

## 10) Tests the MVP **must** include (and pass)

1. **STRICT beats cache (snapshot edge)**

   * With warm mirrors, `freshness_hint=STRICT` triggers QBO fetch → INBOUND log → mirror upsert → returns mirror.

2. **Idempotent bill payment**

   * Two identical approves (same bill/amount/date) produce one QBO payment (same idempotency key).

3. **Throttle hygiene (QBO 429)**

   * On list/approve, one bounded retry (per flag); hygiene flag visible in snapshot.

4. **Recon without webhook**

   * Mark a bill paid directly in QBO; nightly recon logs INBOUND and updates mirror.

5. **Stale mirror hygiene**

   * If mirror past hard TTL, snapshot shows hygiene flag but still returns last known state.

---

## 11) Cursor Guards (make drift impossible)

**.cursorrules** (place in both repo root and `mvp_qbo/`)

```
You may modify files ONLY under:
- mvp_qbo/**
Do not create, edit, or delete files outside the paths above.

When asked to use legacy code, prefer:
- Implementing a thin adapter in mvp_qbo/infra/gateways/** to call existing QBO client/sync code
- Or copying only the minimal functions needed into mvp_qbo/infra/**

Do not import from legacy folders:
- runway/services/data_orchestrators/**
- infra/qbo/** (legacy paths outside MVP)
- infra/jobs/** (job scheduler, job storage)
- plaid/**, ramp/**, stripe/**

All Runway code must depend on Domains gateway interfaces only.
```

**scripts/ci_guard.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail
CHANGED=$(git diff --name-only origin/main...HEAD || true)
echo "$CHANGED" | grep -Ev '^(mvp_qbo/|scripts/|\.github/|README\.md)' >/dev/null && {
  echo "❌ Changes outside MVP lane detected."; exit 1; } || true
```

**Runtime import guard** (optional, belt-and-suspenders; import once in `api/routes.py`)

```python
# mvp_qbo/src/mvp_qbo/_import_guard.py
import sys
FORBIDDEN = ("runway.services.data_orchestrators", "plaid.", "ramp.", "stripe.", "infra.jobs.")
class GuardFinder:
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith(FORBIDDEN):
            raise ImportError(f"Forbidden import in MVP: {fullname}")
        return None
sys.meta_path.insert(0, GuardFinder())
```

---

## 12) Migration Playbook (Cursor step-by-step)

**Step 1 — Bootstrap nucleus**

* Create `mvp_qbo/` layout above.
* Add `.cursorrules`, `scripts/ci_guard.sh`, basic `pyproject.toml`, and `FastAPI` app in `api/routes.py` with `/healthz`.

**Step 2 — Copy minimal QBO client & mappers**

* Bring only what’s needed for: list bills, list invoices, post bill payment, (optional) balances via QBO endpoints.

**Step 3 — Build domain interfaces**

* Add `domains/*/gateways.py` and `repositories.py` (interfaces only).

**Step 4 — Implement infra repos**

* Create `infra/db/schema.sql`, `session.py`, and `infra/repos/*_repo.py` for Mirror + Log.

**Step 5 — Implement Sync Orchestrator**

* Minimal strict-refresh + TTL; use idempotency helper.

**Step 6 — Implement infra gateways**

* `infra/gateways/ap_qbo_gateway.py`, `ar_qbo_gateway.py`, `bank_qbo_gateway.py` implementing domain interfaces using client + orchestrator + repos.

**Step 7 — Wire Runway**

* `runway/wiring.py` binds interfaces → impls.
* `runway/services/runway_orchestrator.py` composes gateways + calculators.
* `api/routes.py` exposes `/snapshot` and `/approve`.

**Step 8 — Add the 5 tests**

* Place under `mvp_qbo/tests/`. Make them green.

**Step 9 — Manual smoke with QBO sandbox**

* Use 3–5 seeded tenants. Verify digest/console/hygiene loads; one approve path works idempotently.

---

## 13) What *not* to optimize now

* Multi-rail (Plaid, Ramp, Stripe) — **later**
* Priority queues / complex schedulers — **later**
* Cross-rail vendor graph — **later**
* Event bus fan-out — **later**
* Moving legacy folders — **leave in place**, just don’t import them

---

## 14) Acceptance Criteria (Definition of Done)

* Runway imports **only** domain gateway interfaces + wiring.
* Strict reads **log INBOUND** then **upsert mirror**.
* Writes **log OUTBOUND** with **idempotency**; mirror updated optimistically.
* Nightly recon path exists (can be a callable runner; scheduler optional).
* The 5 MVP tests pass.
* CI and `.cursorrules` prevent edits/imports outside `mvp_qbo/**`.

---

### Final notes to Cursor

* When in doubt, **prefer adapters over refactors**.
* If a legacy function is tempting to reuse, **copy only that function** into `mvp_qbo/infra/...` and strip it down.
* Do not “improve” legacy layers from within MVP. Propose comments instead.
* Keep PRs tiny and sequential: Step 1 bootstrap → Step 2 client → … → Step 8 tests.

---

This document is the **single source of truth** for the MVP nucleus. Follow it literally. If the code you generate differs in shape, the **patterns and contracts above still apply** and must not be violated.
