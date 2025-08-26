Below is the updated `DEVELOPMENT_STANDARDS.md` reflecting the reorganized file/folder structure, with tests moved to domain-specific `tests` subfolders (e.g., `domains/ap/tests`, `domains/core/tests`) and other structural changes. The update focuses on the **File Naming & Import Chaos**, **Code Organization**, and related sections, while preserving the original anti-patterns, good patterns, and other guidance unchanged unless impacted by the new structure. New commands and troubleshooting tips are added to align with the domain-based organization.

---

```markdown
# Development Standards & Anti-Patterns

*Based on Stage 0-1C implementation experience - critical for avoiding common pitfalls*

## Quick Reference
- [Development Plan](dev_plans/1_ServicePro_plan.markdown)


## 🚫 **CRITICAL ANTI-PATTERNS TO AVOID**

### **File Naming & Import Chaos**
- ❌ **Don't:** Use ambiguous or redundant prefixes in filenames (e.g., `ap_bill.py`, `core_service.py` in `domains` subfolders).
- ❌ **Don't:** Bulk rename files or move them between `domains` (e.g., `ap` to `core`) without updating ALL imports across the codebase.
- ❌ **Don't:** Assume imports will resolve after moving files to domain-specific folders (e.g., `domains/ap/models` to `domains/core/models`).
- ✅ **Do:** Use clear, domain-specific filenames within `domains` (e.g., `bill.py` in `domains/ap/models`, `service.py` in `domains/core/models`).
- ✅ **Do:** Update imports systematically after file reorganization, using relative imports within domains (e.g., `from ..models.bill import Bill` in `domains/ap/services`).
- ✅ **Do:** Verify imports with `poetry run python -c "import domains.ap.routes.ingest"` after changes.

### **Schema vs. Model Confusion**
- ❌ **Don't:** Use SQLAlchemy models (e.g., `domains/ap/models/bill.py`) as `response_model` in FastAPI routes.
- ❌ **Don't:** Mix Pydantic schemas (e.g., `domains/ap/schemas/bill.py`) and SQLAlchemy models in API responses.
- ❌ **Don't:** Assume `from_attributes = True` fixes all serialization issues.
- ✅ **Do:** Create separate Pydantic schemas in `domains/*/schemas` (e.g., `BillBase`, `BillCreate`, `Bill`) for API validation.
- ✅ **Do:** Use Pydantic schemas for `response_model` in `domains/*/routes`, SQLAlchemy models for database operations in `domains/*/services`.
- ✅ **Do:** Alias SQLAlchemy models in routes (e.g., `from domains.ap.models.bill import Bill as BillModel`).

### **Database Schema Mismatches**
- ❌ **Don't:** Create seed data (e.g., `domains/close/data/seed_data.sql`) that doesn't match SQLAlchemy models in `domains/*/models`.
- ❌ **Don't:** Assume database columns exist without checking model definitions in `domains/*/models`.
- ❌ **Don't:** Use hardcoded field names that don't match the database schema.
- ✅ **Do:** Ensure seed data in `domains/*/data` matches model definitions in `domains/*/models`.
- ✅ **Do:** Use consistent field names across models, schemas, and seed data.
- ✅ **Do:** Test database seeding (`scripts/load_seed_data.py`) before building frontend features.

### **Missing Required Fields**
- ❌ **Don't:** Forget to add required fields like `firm_id`, `client_id` in `domains/*/models` for multi-tenancy.
- ❌ **Don't:** Create models that inherit from `domains/core/models/base.py` but omit required fields.
- ❌ **Don't:** Assume optional fields are truly optional without checking business logic in `domains/*/services`.
- ✅ **Do:** Explicitly add required fields (`firm_id`, `client_id`) in all new models.
- ✅ **Do:** Use database constraints in `domains/*/models` to enforce required fields.
- ✅ **Do:** Validate seed data includes all required fields.

### **Route Registration & Import Issues**
- ❌ **Don't:** Assume routes in `domains/*/routes` register automatically without inclusion in `domains/*/routes/__init__.py`.
- ❌ **Don't:** Import non-existent modules in `domains/*/routes/__init__.py` (causes circular imports).
- ❌ **Don't:** Forget to include domain-specific routers in `main.py` via `app.include_router`.
- ✅ **Do:** Test route registration after changes to `domains/*/routes/__init__.py` or `main.py`.
- ✅ **Do:** Verify all imported modules exist before adding to `domains/*/routes`.
- ✅ **Do:** Use minimal working examples to isolate routing issues (e.g., `poetry run python -c "from domains.ap.routes.ingest import router"`).

### **Seed Data & Business Logic Integration**
- ❌ **Don't:** Hardcode business logic responses in `domains/*/services`.
- ❌ **Don't:** Return mock data from services instead of querying the database.
- ❌ **Don't:** Use static responses for dynamic business rules.
- ✅ **Do:** Use seed data (e.g., `domains/close/data/seed_data.sql`) for configurable business rules.
- ✅ **Do:** Query real data for compliance, task templates, policy rules in `domains/*/services`.
- ✅ **Do:** Make business logic data-driven and configurable via `domains/core/services/policy_engine.py`.

### **Complex Dependencies in Templates**
- ❌ **Don't:** Load heavy third-party libraries (e.g., drag-and-drop) in `templates` (e.g., `preclose_dashboard.html`, `BankMatching.jsx`).
- ❌ **Don't:** Assume CDN libraries will load correctly or have expected global variables.
- ❌ **Don't:** Mix complex JavaScript with Jinja2 syntax in `templates`.
- ✅ **Do:** Start with basic React components in `templates` (e.g., `BankMatching.jsx`) and add complexity incrementally.
- ✅ **Do:** Test external library loading before building complex features.
- ✅ **Do:** Use raw JavaScript blocks or escape Jinja2 syntax conflicts in `templates`.

### **Database Seeding Issues**
- ❌ **Don't:** Call seeding functions (`scripts/load_seed_data.py`) multiple times without checking data existence.
- ❌ **Don't:** Use SQLAlchemy queries to check table existence before seeding.
- ❌ **Don't:** Assume seeding works after table creation without error handling.
- ✅ **Do:** Use raw SQL in `scripts/load_seed_data.py` to check table existence and data counts.
- ✅ **Do:** Implement error handling in seeding functions.
- ✅ **Do:** Test seeding with fresh databases (`scripts/create_tables.py`).

## ✅ **GOOD PATTERNS TO REPLICATE**

### **Systematic Problem Solving**
- ✅ **Do:** Fix one issue at a time, test, then move to the next.
- ✅ **Do:** Use error messages to guide fixes rather than guessing.
- ✅ **Do:** Test APIs directly with `curl` before testing frontend in `templates`.
- ✅ **Do:** Check server logs for detailed error information.
- ✅ **Do:** Use minimal working examples to isolate complex issues.

### **Incremental Template Development**
- ✅ **Do:** Start with simple templates in `templates` (e.g., `document_review.html`) that display data.
- ✅ **Do:** Add interactive features only after basic functionality works.
- ✅ **Do:** Use console logging to debug frontend data flow in `templates/*.jsx`.
- ✅ **Do:** Test templates in isolation before integrating with complex features.

### **Proper Test Structure**
- ✅ **Do:** Use fixtures in `domains/*/tests/conftest.py` for reusable test data.
- ✅ **Do:** Mock external API calls (e.g., QBO, Jobber) in `domains/*/tests/conftest.py` to prevent test hangs.
- ✅ **Do:** Test database operations with proper setup/teardown in `domains/*/tests`.
- ✅ **Do:** Use descriptive test names and organize tests logically in `domains/*/tests`.
- ✅ **Do:** Centralize common mocks (e.g., QBO) in `domains/core/tests/conftest.py`.

### **Multi-Tenant Architecture**
- ✅ **Do:** Implement `TenantMixin` from `domains/core/models/base.py` across all models.
- ✅ **Do:** Add `firm_id`, `client_id` filtering to all list endpoints in `domains/*/routes`.
- ✅ **Do:** Use proper foreign key relationships with explicit constraints in `domains/*/models`.
- ✅ **Do:** Test tenant isolation thoroughly in `domains/*/tests`.
- ✅ **Do:** Always include `firm_id`, `client_id` in domain objects.

### **Code Organization**
- ✅ **Do:** Organize code by domain (`ap`, `ar`, `bank`, `close`, `core`, `payroll`, `webhooks`) under `domains`.
- ✅ **Do:** Use subfolders (`models`, `schemas`, `services`, `routes`, `tests`) within each domain for separation of concerns:
  - `models`: SQLAlchemy models for database operations.
  - `schemas`: Pydantic schemas for API validation and responses.
  - `services`: Business logic and data processing.
  - `routes`: FastAPI endpoints.
  - `tests`: Pytest tests specific to the domain.
- ✅ **Do:** Consolidate domain routers in `domains/*/routes/__init__.py` and include in `main.py`.
- ✅ **Do:** Use consistent naming (e.g., `bill.py` for model, schema, service, routes, tests in `domains/ap`).
- ✅ **Do:** Implement proper error handling with HTTP status codes in `domains/*/routes`.

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
  - Jobber (or other CRMs lacking sandboxes): use a mock adapter by default; allow live only for allowlisted `firm_id`/`client_id`.
  - Maintain a per-platform allowlist; block all others even if `commit=true`.

- **Idempotency & safety**:
  - For any POST/PUT to external systems, require an `Idempotency-Key` header.
  - Log every attempted write with rationale, allowlist verdict, and idempotency key.

- **Schema + invariant validation (before commit)**:
  - Validate payloads against strict JSON Schemas per platform.
  - Stripe examples: amounts in cents, timestamps valid, `net + fee ≈ gross` within tolerance.
  - CRM examples (Jobber/others): job/invoice dates valid, totals consistent, cross-links resolvable (`invoice.job_id` exists), bundled deposit sums align with invoice sums within tolerance, date variance within policy.
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

## 🔧 **IMPLEMENTATION CHECKLIST**

### **Before Starting New Feature**
- [ ] Check existing models and schemas in `domains/*/models`, `domains/*/schemas` for consistency.
- [ ] Verify database schema matches model definitions in `domains/*/models`.
- [ ] Ensure seed data exists in `domains/*/data` or `data` for business logic.
- [ ] Plan multi-tenant implementation (`firm_id`, `client_id`) in `domains/*/models`.

### **During Development**
- [ ] Test route registration in `domains/*/routes` after adding new endpoints.
- [ ] Verify imports work without circular dependencies in `domains/*/routes`, `domains/*/services`.
- [ ] Test database operations with real data in `domains/*/services`.
- [ ] Ensure proper error handling and status codes in `domains/*/routes`.

### **Before Committing**
- [ ] Run full test suite: `poetry run pytest domains/*/tests -q --disable-warnings`.
- [ ] Verify all routes in `domains/*/routes` are accessible (no 404s).
- [ ] Check that seed data loads correctly (`scripts/load_seed_data.py`).
- [ ] Ensure multi-tenant isolation works in `domains/*/tests`.

## 📚 **COMMON COMMANDS**

```bash
# Database setup
python scripts/create_tables.py
python scripts/load_seed_data.py

# Testing
poetry run pytest domains/*/tests -q --disable-warnings
poetry run pytest domains/ap/tests/test_bill_ingestion.py -v

# Route verification
poetry run python -c "from domains.ap.routes.ingest import router; print(len(router.routes))"

# App startup test
poetry run python -c "from main import app; print('✅ App imports successfully')"

# Domain-specific route check
poetry run python -c "from domains.core.routes.automation import router; print('✅ Core routes loaded')"

# Seed data check
python -c "from database import SessionLocal; from domains.core.models.client import Client; print(SessionLocal().query(Client).count())"
```

## 🚨 **TROUBLESHOOTING**

### **Route Registration Issues**
1. Check `domains/*/routes/__init__.py` for missing imports.
2. Verify all imported modules exist in `domains/*/routes`.
3. Test minimal route creation (e.g., `poetry run python -c "from domains.ap.routes.ingest import router"`).
4. Check for circular imports in `domains/*/routes`.

### **Database Issues**
1. Recreate tables: `python scripts/create_tables.py`.
2. Reload seed data: `python scripts/load_seed_data.py`.
3. Check model field names in `domains/*/models` match database.
4. Verify foreign key relationships in `domains/*/models`.

### **Import Errors**
1. Check file paths and naming in `domains/*/models`, `domains/*/services`, etc.
2. Verify `__init__.py` files exist in all domain subfolders.
3. Test imports individually (e.g., `poetry run python -c "from domains.ap.models.bill import Bill"`).
4. Look for circular dependencies in `domains/*/routes`, `domains/*/services`.
