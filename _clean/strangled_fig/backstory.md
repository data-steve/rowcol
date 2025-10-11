Here’s a companion brief you can include alongside the “vaccine” architecture doc — a contextual overview of *why* you’re taking this path, the shape of the system you’ve already built, and how the Strangler-Fig MVP aligns with your long-term architecture.

---

# RowCol MVP Direction & Rationale — Context for Strangler Plan

### Overview

RowCol has evolved into a large, sophisticated codebase built around a **hub-and-spoke, multi-rail architecture** designed for **CAS 2.0 firms**. The system’s long-term goal is to serve as a **Financial Control Plane** that orchestrates multiple rails — QuickBooks Online (QBO), Ramp, Plaid, and Stripe — through a unified, auditable flow:
**Approve → Execute → Verify → Record.**

Over the past several months, development has produced a deep foundation:

* A **smart sync system** with caching, retries, deduping, and orchestration.
* Extensive **domain models** across AP, AR, Bank, and Core.
* A sprawling but modular **infra layer** with QBO, Ramp, Plaid integrations, job scheduling, and configuration rules.
* A **Runway layer** containing calculators, orchestrators, and user-facing experiences.

This groundwork proves the concept but also exposed a scaling problem: the system’s complexity outpaced the MVP.

---

### The Problem

By mid-2025, the repo had grown to 50+ directories and nearly 200 files. Many pieces were half-connected or frozen mid-refactor. Cursor (and humans) kept tripping over:

* **Cross-layer coupling** — Runway calling infra directly instead of going through domain interfaces.
* **Multiple unfinished sync paradigms** — legacy “smart_sync” helpers, newer orchestrators, and stray background jobs all competing.
* **Unclear DB semantics** — code assuming both transaction-log and state-mirror behavior without a consistent boundary.
* **Feature sprawl** — early hooks for Plaid, Ramp, Stripe adding noise before QBO was stable.
* **IDE confusion** — Cursor and other tools indexing every file, “helpfully” editing deprecated orchestrators and stale services.

Despite the sophistication, the **core product still hadn’t shipped**: a working, advisor-usable QBO-only dashboard showing Bills, Balances, and Invoices with guardrails.

---

### The Realization

The team recognized that:

1. **The architecture is sound** (hub-and-spoke orchestration, sync → log → mirror model).
2. **But the build order is wrong** — trying to stabilize the entire multi-rail system before validating the single-rail experience.
3. **The tooling (Cursor)** gets lost in the noise, mixing new and old conventions.

Hence the pivot to a **controlled Strangler-Fig MVP**: carve out a small, clean nucleus inside (or alongside) the existing repo that captures the *core pattern* without the baggage.

---

### Why the Strangler-Fig Approach

The goal isn’t to rewrite everything — it’s to **quarantine complexity** and **prove the architecture in miniature**.

* Keep the proven infra pieces (QBO client, sync engine, transaction log, SQLite mirrors).
* Wrap them behind **Domain Gateways** — narrow, rail-agnostic interfaces.
* Build a new **Runway MVP layer** that consumes only those gateways.
* Enforce one-way dependencies: `runway → domains → infra`.
* Use CI, `.cursorrules`, and import guards so Cursor can’t reach back into legacy rails.

This allows incremental replacement: once the MVP is stable, other rails (Ramp, Plaid, Stripe) can attach to the same interfaces as new spokes.

---

### MVP Focus (Step 1)

**Scope:** QBO only — Bills, Balances, Invoices.
**Tech:** FastAPI + SQLite mirror + append-only log.
**Flow:**

* Read: QBO → Log (INBOUND) → Mirror → Runway.
* Write: Runway → Log (OUTBOUND) → QBO → Mirror.
* Sync: nightly recon instead of real-time webhooks (webhooks remain flaky).
  **UI:** Single “Console/Digest/Hygiene” page proving the workflow end-to-end.

This delivers something advisors can use and validates the hub-spoke control-plane pattern on one rail.

---

### Long-Term Alignment

Even while trimming for MVP, every decision keeps the future in view:

| Future Concept                                      | MVP Equivalent                                                 |
| --------------------------------------------------- | -------------------------------------------------------------- |
| Multi-rail orchestration (QBO, Ramp, Plaid, Stripe) | One rail (QBO) using the same **Sync → Log → Mirror** backbone |
| Hub-and-Spoke Financial Control Plane               | Single-hub (RowCol) orchestrating one spoke (QBO)              |
| Multi-client advisor console                        | Single-client prototype (one firm)                             |
| Real-time verification loop                         | Poll + nightly recon placeholder                               |
| Event bus & replay                                  | Append-only transaction log foundation                         |
| Complex queue & backoff                             | Simplified Sync Orchestrator with low retries                  |

Thus the MVP serves as both **prototype and proof-of-architecture**: the same seam lines scale outward later.

---

### Design Intent: Where Each Layer Lives

| Layer       | Role                                                                                   | Lives In           |
| ----------- | -------------------------------------------------------------------------------------- | ------------------ |
| **Infra**   | Implementation: external rails, sync orchestration, transaction log, mirrors, caching. | `mvp_qbo/infra/`   |
| **Domains** | Contracts: gateway interfaces, repo interfaces, data models.                           | `mvp_qbo/domains/` |
| **Runway**  | Product logic: orchestrators, calculators, experiences, DTOs.                          | `mvp_qbo/runway/`  |

Runway defines *what advisors see and do*, Domains define *what data it needs*, and Infra defines *how to get it reliably*.

---

### The Cultural Lesson

RowCol’s earlier ambition created the right architecture but too much surface area. The Strangler-Fig approach isn’t a retreat; it’s a **reset of focus and sequencing**:

* Prove value first, then scale rails.
* Protect working infrastructure by isolating it behind stable interfaces.
* Give the IDE and team a smaller, testable world where every file matters.

Once the MVP ships, the nucleus becomes the **new core** of RowCol: a clean, agentic, testable foundation for the multi-rail future.

---

**In short:**
We’re not abandoning the Control Plane vision — we’re compressing it into a single-rail, fully functioning seed that can grow safely. The MVP nucleus is the vaccine: small, strong, and immune to the old chaos.
