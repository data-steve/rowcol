# Development Standards & Anti-Patterns

## Quick Reference
- [Build Plan](Oodaloo_v4.2_Build_Plan.md)


## ✅ **GOOD PATTERNS TO REPLICATE**

### **Code Organization**
- `domains/`: QBO-facing primitives (e.g., `APIngestionService`, `PolicyEngineService`, `identity_graph/`).
- `runway/`: Product-specific orchestration (e.g., `tray/`, `digest/`, `onboarding`).
- Use subfolders (`models`, `schemas`, `services`, `routes`, `tests`) in `domains/` and `runway/tray/`.
- Export components via `__init__.py` (e.g., `domains/ap/services/__init__.py` exports `APIngestionService`).



### **Safe External Ingest & Testing (General Policy)**
- **Short answer**: We never push to external CRMs/Payment platforms by default. Ingest endpoints are dry-run first, use provider test modes only, and never call live APIs in CI unless explicitly allowlisted. Payloads and invariants are validated before any commit. Only with `commit=true` and the proper feature flag do we persist.

- **Dry-run default**:
  - Endpoints like `/api/ingest/{platform}` run in preview mode by default (no DB writes, no external mutations).
  - Return a diff-style preview (counts and samples of would-be creates/updates/deletes).

- **Explicit commit required**:
  - Writes require BOTH `commit=true` (or header `X-Commit: true`) AND `EXTERNAL_WRITE_ENABLED=true`.
  - Without both, the service returns preview and refuses to mutate.

- **Environment gates**:
  - Stripe: enforce test-mode keys only (`sk_test_…`). Reject `sk_live_…` by default.
  - Maintain a per-platform allowlist; block all others even if `commit=true`.

- **Idempotency & safety**:
  - For any POST/PUT to external systems, require an `Idempotency-Key` header.
  - Log every attempted write with rationale, allowlist verdict, and idempotency key.

- **Schema + invariant validation (before commit)**:
  - Validate payloads against strict JSON Schemas per platform.
  - Stripe examples: amounts in cents, timestamps valid, `net + fee ≈ gross` within tolerance.
  - If any invariant fails, reject with a precise error.

- **Proving test data is correct (before real writes)**:
  - Use deterministic fixtures and seeds as the single source of truth: `tests/fixtures/*` and `data/seed_data.sql`.
  - During dry-run, validate outbound shapes against JSON Schemas derived from vendor docs.
  - Enforce invariants: bundled sums, date windows, no duplicate IDs, FKs resolvable.
  - Keep snapshot previews for review and PR diffs; optional record/replay (e.g., httpx + cassettes) to verify contracts without touching live APIs.

- **Operational guardrails**:
  - `TESTING` blocks external writes by default.
  - Set `EXTERNAL_WRITE_ENABLED=false` in all non-prod envs; flip only for supervised runs.
  - Route-level guards: refuse live ops when using live keys or non-allowlisted tenants.

- **Next-step template for any new platform**:
  1) Add `/api/ingest/{platform}` with dry-run default and preview output.
  2) Add JSON Schema for request/response contracts and invariant checks.
  3) Gate writes behind `commit=true` + `EXTERNAL_WRITE_ENABLED=true` + allowlist + idempotency key.
  4) Enforce provider test-mode credentials; reject live by default.
  5) Document a seeding path: how to create provider-side test data that mirrors `tests/fixtures/*` scenarios.
