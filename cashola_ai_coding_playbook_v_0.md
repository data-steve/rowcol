# Cashola AI‑Coding Playbook (v0.1)

A practical, copy‑pasteable guide for turning the techniques in *coding-with-ai.dev* into a concrete Cashola build system. Optimized for FastAPI backend, React/Tailwind frontend, GitHub Actions, and your “weekly cash check‑in” scope (bank‑truth cash, near‑term AR, must‑pay AP/payroll, runway, and collect vs pay/delay plan).

---

## 0) Repository scaffolding (1‑time)

```text
cashola/
├─ apps/
│  ├─ api/                 # FastAPI service (Auth, Bank, AR, AP, Runway, Plans)
│  ├─ worker/              # Celery/RQ or async jobs (syncs, scoring, enrichment)
│  └─ web/                 # React + Vite + Tailwind
├─ infra/                  # IaC stubs (CloudFormation/Terraform) + ECS workflows
├─ tests/                  # pytest; unit + contract + e2e (Playwright later)
├─ scripts/                # dev helpers (seed, ingest, smoke, reset)
├─ .cursorrules            # Cursor/Claude rules (see below)
├─ CLAUDE.md               # Memory file (see below)
├─ CONTRIBUTING.md         # How to run, test, commit style, DCO
├─ pyproject.toml          # Poetry or uv (preferred) config
└─ README.md               # Getting started
```

---

## 1) Memory files that “teach the repo”

### `CLAUDE.md` (drop into repo root)

```
# Project
Cashola — weekly cash check‑in for SMBs. Output: bank‑truth cash today, near‑term AR, must‑pay AP/payroll, runway days, and a ranked collect/pay plan. MVP connectors: Plaid (or Relay), CSV import; Jobber/HCP optional later. Stack: FastAPI + Postgres; React/Tailwind UI.

# Architecture
- apps/api: FastAPI, SQLAlchemy, Pydantic. Services: bank, ar, ap, runway, plans.
- apps/worker: background syncs; idempotent jobs; structured logging to STDOUT.
- tests: pytest; prefer @pytest.mark.parametrize; high‑value golden tests for runway.

# Coding rules
- Write simple, explicit code; avoid inheritance. Clear function names + docstrings.
- Test‑first for public functions and endpoints. Never edit tests to make them pass.
- Use dependency injection via small service objects; no global state.

# Logging (for agents)
- In DEBUG, emails/tokens are logged to STDOUT for test flows.
- Always log job ids, external ids, and reconciliation decisions with reasons.

# Tasks the agent can do safely
- Generate endpoints, Pydantic schemas, SQL models, migrations.
- Write tests from given I/O tables; run `uv run pytest -q`.
- Add scripts in `scripts/` and wire them into Make targets.

# Prompts
- Use “think harder” planning before edits. Present 2–3 options with pros/cons.
- Prefer boring libs with stable APIs. No surprise dependency upgrades.
```

### `.cursorrules` (minimal starter)

```
# Context
ALWAYS open CLAUDE.md first. Keep responses short and surgical. Use test‑driven regeneration: if tests fail, fix code without editing tests. Prefer parametrize.

# Style
Python: type hints, docstrings (why + what + raises), small pure functions. JS: functional React, hooks, Tailwind utility classes; keep components under 150 LOC.

# Commit
Conventional commits; one concern per commit; include test changes with code.
```

---

## 2) Test‑Driven Regeneration (TDR) workflow

**CLI** (use uv or Poetry; uv shown):

```bash
# install
uv venv && source .venv/bin/activate
uv pip install -e .[dev]

# run tests locally (agent will run the same)
uv run pytest -q
```

**Starter test files**

```
tests/test_runway_math.py        # deterministic runway calc from I/O table
tests/bank/test_plaid_mapper.py  # bank tx → CDM mapping contract tests
tests/ar/test_expected_receipts.py
```

**Pattern**
1. You (human) write failing tests describing behavior.
2. Ask model: “**think harder**. Implement only what’s required to pass these tests. Do not edit tests.”
3. Iterate until green. Commit.

---

## 3) Parallel agents with git worktrees

Use separate branches + worktrees to run 2–3 agents safely in parallel.

```bash
# create parallel sandboxes
git worktree add ../cashola-ar feature/ar-ingest
git worktree add ../cashola-ui feature/ui-shell

# later, merge via PRs into main
```

*Assignment guide*
- Agent A (feature/ar-ingest): CSV → CDM mapping + tests
- Agent B (feature/ui-shell): Dashboard skeleton + chart stubs
- Agent C (feature/runway-core): runway engine + unit tests

---

## 4) Prompt patterns (copy‑paste)

**Function‑signature first**
```
Write Python in apps/api/domain/runway.py implementing:

async def compute_runway_days(cash_balance: Decimal, expected_inflows: list[MoneyEvent],
                              expected_outflows: list[MoneyEvent], lookahead_days: int = 14) -> int:
    """Return integer days of runway under cash‑basis schedule simulation.
    - Inflows/outflows are (date, amount) in ISO date + Decimal USD.
    - Use day‑bucket simulation; no discounting.
    - If cash goes < 0 on a day, return days until that breach.
    - Keep it pure; raise ValueError on invalid dates or currency mismatch.
    """
# Provide tests in tests/test_runway_math.py using @pytest.mark.parametrize.
```

**“Think‑hard” plan before edits**
```
think harder: Before touching files, outline a 6‑step plan with files to edit, tests to add, and a rollback plan. Show 2 alternative approaches and choose one.
```

**UI “vibe coding”**
```
Here’s a quick sketch (image attached). Make a React page `Dashboard.tsx` with a left nav, a top summary (Cash Today, AR This Week, Must‑Pay), and a table for Exceptions Tray. Add dummy data + TODO comments for real hooks.
```

**Subagent verification**
```
Spawn a subagent to check that Plaid transaction categories won’t break our CDM mapping. Produce a risk list + unit tests for edge cases.
```

---

## 5) Minimal CI that teaches the agent the loop

`.github/workflows/ci.yml`

```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv venv && . .venv/bin/activate && uv pip install -e .[dev]
      - run: uv run pytest -q
```

Add a second job later for `apps/web` with `pnpm test`.

---

## 6) Cashola Core Data Model (CDM) — seed spec for agents

**Entities**
- **BankTransaction**(id, external_id, date, amount, counterparty, memo, account_id, source, fee_flag)
- **Invoice**(id, external_id, issue_date, due_date, total, customer_id, status)
- **ExpectedReceipt**(invoice_id, expected_date, expected_amount, confidence)
- **Obligation**(id, type [vendor|payroll|tax], due_date, amount, must_pay_flag)
- **PlanDecision**(id, kind [collect|pay|delay], target_id, reason, impact_on_runway)

**Mappers (contract tests first)**
- `from_plaid(tx) -> BankTransaction`
- `from_csv(row, kind="invoice"|"obligation") -> Invoice|Obligation`

---

## 7) Logging & observability (agent‑friendly)

- **Every reconciliation decision logs**: inputs, rule chosen, and “because.”
- **In DEBUG**: email links/tokens printed to STDOUT so the agent can complete flows.
- **request‑id** middleware; job ids in logs; JSON log lines.

---

## 8) Daily build ritual (90‑minute block)

1. **/clear** context. Paste CLAUDE.md.
2. Pick 1 of 3 tracks (AR ingest, Runway math, UI shell).
3. Write/extend tests → run → red.
4. “Think harder” → implement → green.
5. Commit small; PR from worktree.
6. Screenshot UI diffs for vibe iterations.

---

## 9) Starter test tables (copy now)

```python
# tests/test_runway_math.py
import datetime as dt
import pytest
from decimal import Decimal

@pytest.mark.parametrize("cash,inflows,outflows,lookahead,expected_days", [
    (Decimal("5000"), [("2025-09-05", "2000")], [("2025-09-07", "6000")], 14, 6),
    (Decimal("10000"), [("2025-09-10", "0")], [("2025-09-12", "12000")], 14, 12),
])
def test_runway_days(cash, inflows, outflows, lookahead, expected_days):
    ...  # fill with calling compute_runway_days and asserting
```

---

## 10) Low‑risk tasks to offload immediately

- Generate `apps/api` service skeletons + routers for `/bank`, `/ar`, `/ap`, `/runway`, `/plan`.
- Implement CSV → CDM importers with strict validation + tests.
- Create `Dashboard.tsx` skeleton with Tailwind + cards + Exceptions Tray table.
- Add `scripts/seed_demo.py` to load fake bank/AR/AP for demos.

---

## 11) Guardrails & conventions (so agents don’t drift)

- No network calls in unit tests; use fixtures.
- One concern per PR; require green CI.
- Prefer explicit mapping tables over regex heuristics.
- Document assumptions in docstrings + README snippets the agent can quote.

---

## 12) Micro‑backlog (first 2 weeks)

1. **Runway engine v0**: day‑bucket sim, unit tests, pure function API.
2. **CSV ingest v0**: invoice + obligation importers, validation errors surfaced in UI tray.
3. **Bank sync stub**: mock Plaid adapter + mapper contract tests.
4. **UI shell**: nav + summary cards + tray with fake data.
5. **Plan decisions**: greedy heuristic: collect soonest, pay must‑pay, delay others; log impact.
6. **CI green**: uv + pytest on push; pnpm test for web next.

---

**That’s it.** Drop these files in, and you’ve operationalized the AI‑coding techniques directly into Cashola’s repo and rituals. Iterate daily with tests, small PRs, and screenshot‑driven UI tweaks.

