Got it. Here’s a concrete, “keep-it-simple” build plan for RowCol as the **firm-grade control layer on top of QBO + Bill/ Ramp + Plaid + Stripe** (and optionally “consume” Digits if/when present). It’s faithful to the realities in your docs: multi-client portfolio, deterministic policies, audit-proof, CSV fallbacks, and minimal reinvention.

# 0) North Star (what RowCol *is*)

* **One job:** Run the weekly cash-discipline loop across many clients:
  **Approve → Execute → Verify → Record → Digest.**
* **Position:** *We orchestrate rails; we don’t replace them.* QBO is the ledger. Bill/Ramp execute. Plaid verifies cash. Stripe hints at AR.
* **Principle:** **Deterministic control, not generative decisioning.** Rules + a small state machine; AI only for explanations/hints.

# 1) System shape (mental model)

Think **“Terraform plan/apply for money”**:

* **Plan:** simulate runway impact if we pay these N bills.
* **Apply:** send only the approved subset to the rail with guardrails enforced.
* **State:** append-only, human-readable audit log; immutable event stream.

# 2) Minimal data model (KISS, firm-native)

Single sacred schema that everything hangs on:

```
Firm
 └─ Client (tenant)
     ├─ Accounts (bank, card) ← Plaid
     ├─ Bills/AP (id, vendor, due, amount, status) ← QBO + Bill/Ramp
     ├─ Invoices/AR (id, customer, due, amount, status) ← QBO + Stripe (read-only)
     ├─ Payroll windows (next date, est amount) ← CSV or Gusto-read (later)
     ├─ Policies (JSON; versioned)
     ├─ Decisions (approve/hold; actor; timestamp; rationale; evidence)
     ├─ Executions (rail, op_id, status, webhook receipts)
     ├─ CashSnapshots (T0..T+14 balances; computed)
     └─ Digests (rendered HTML/PDF; versioned)
```

**Notes**

* Keep **IDs rail-native** and mirror them (e.g., `bill.source="QBO" | "Ramp"`; `bill.source_id`).
* **No denormalized spaghetti.** Use views to combine; store raw + normalized.

# 3) Core loop (the five steps)

## (A) Approve

* **Inputs:** Current balances (Plaid), open bills (QBO/Ramp), upcoming payroll (CSV), AR receipts (Stripe read), client policy.
* **Engine:** Deterministic evaluator applies guardrails (e.g., `buffer_days_after >= 14`, “essentials first”, vendor caps).
* **UI:** Bills tray with live “buffer after pay” meter; batch select; overrides require reason.
* **Output:** `DecisionSet` (approved | held | needs data).

## (B) Execute

* **Adapter:** `RailExecutor` per rail (start with Ramp; Bill.com next).
* **Contract:** `release(bill_ids[], date)` → returns rail `op_ids`.
* **Idempotency:** client + bill + decision hash.
* **Retries:** exponential backoff; dead-letter queue with operator banner in UI.

## (C) Verify

* **Webhooks → Event bus:** Ramp/Bill payment statuses, Plaid balance changes, QBO BillPayment created.
* **Reconcile:** match `Execution(op_id)` → rail callback → QBO reflects payment.
* **Drift detection:** if rail says “paid” but QBO missing BillPayment after X mins, raise Hygiene issue.

## (D) Record

* **Ledger sync:** Post memo notes/comments to QBO (or add an “AuditNote” via journal memo if needed).
* **Audit log:** append event with policy hits, overrides, user, timestamp, before/after cash, linked evidence.

## (E) Digest

* **Per-client & portfolio:** “What we approved, what we held, why, buffer now, next payroll readiness.”
* **Rendering:** HTML (email/web) + optional PDF; keep the copy deterministic with token templates.
* **Links:** deep-links back to QBO/Bill/Ramp items.

# 4) Integrations (start narrow, be reliable)

**Phase A (MVP)**

* **QBO (read+light write):** bills, vendors, invoices, BillPayments (confirm), memo notes.
* **Ramp (read+execute):** get bills (if used), release payments, webhooks for payment status.
* **Plaid (read):** balances + last updated.
* **CSV fallback:** AR list, payroll dates/amounts.

**Phase B**

* **Bill.com (execute + status).**
* **Stripe (read):** upcoming payouts, recent payments → AR liquidity hints.
* **Gusto (read):** next payroll date/estimate (or CSV until API).

**Phase C**

* **Digits (optional upstream):** if a firm uses Digits, accept their normalized AR/AP as “clean feed” to reduce hygiene load.

# 5) Policy engine (deterministic, explainable)

* **Policy object:** JSON with parameters, not code. Versioned with `policy_id`, `version`, `effective_at`.
* **Evaluator:** pure function; inputs are **snapshot + bills** → **result with reasons**.
* **Library of rules (MVP):**

  * `min_buffer_days` (block/allow, essentials list)
  * `pay_on_days` (Tue/Thu guard)
  * `vendor_daily_cap` / `per_bill_cap`
  * `priority_buckets` (payroll, rent, taxes before discretionary)
  * `override_require_reason`
* **Explainability:** every decision has `rule_hits[]` with human-readable messages logged.

# 6) Hygiene tray (only what protects decisions)

* **Stale balances** (Plaid > 24h).
* **Mismatch** (rail “paid” but no QBO BillPayment after X).
* **Unknown vendor mapping** (cannot classify essential vs discretionary).
* **Missing payroll data** for next 14 days.
  Each item links to “Fix” (refresh, map, upload CSV, open in rail).

# 7) Reliability & failure modes (keep it boring)

* **Event bus:** small queue (e.g., Redis streams / SQS) to decouple webhooks and evaluators.
* **Idempotency keys** everywhere (per client + bill + action hash).
* **Dead-letter queues** surfaced in UI as “Operator attention.”
* **Outbox pattern** for DB→rail writes.
* **Clock skews:** all times UTC; show local in UI only.
* **Partial success:** if batch approve fails on 2 of 20 bills, continue, and banner the failures.

# 8) Security & roles (lean but real)

* **Roles:** PARTNER, CONTROLLER, STAFF, CLIENT (read-only digest).
* **Least privilege tokens** per integration, stored per client.
* **Audit everything:** read/view decision, changes to policy, approvals, overrides.
* **SOC2-ready habits:** secrets vaulted, logs immutable (WORM bucket), background job health checks.

# 9) UI surface (don’t overdesign)

* **Portfolio board:** clients rows → buffer color, next payroll, AR/AP exposure, “Run Check” button.
* **Client Cash Check:** three tabs

  1. **Digest** (7–14 day buffer & summary),
  2. **Console** (bills tray with buffer impact, approve/hold),
  3. **Hygiene** (fix-first list).
* **Batch actions:** approve essentials, hold discretionary, schedule next run.
* **Zero-to-value:** connect QBO + Plaid, import CSV payroll, click “Run Check,” see a digest in 15 minutes.

# 10) Testing strategy (how we stay sane)

* **Contract tests per adapter** (QBO, Ramp, Plaid): deterministic fixtures; simulate time.
* **Policy tests**: table-driven (`@pytest.mark.parametrize`) across bill sets and buffers.
* **E2E happy path:** approve→execute→verify→record→digest with fakes.
* **Chaos cases:** webhook out-of-order, duplicate events, rail timeouts, 500s, partial payments.
* **Regression harness:** “golden digests” snapshots to catch copy drift.

# 11) Delivery plan (phases with shippable proofs)

**Phase 0 (2–4 weeks): Offline proof**

* CSV loader for Bills/AP, AR, balances.
* Policy evaluator + buffer math.
* HTML digest output.
  **Goal:** Show a real firm a before/after digest; confirm guardrail logic resonates.

**Phase 1 (6–8 weeks): Live read + simulated apply**

* Live QBO read + Plaid balances.
* Ramp sandbox adapter (don’t actually pay yet).
* Approve/hold UI; export “intended payments” CSV.
  **Goal:** Save 20–30 min/client/week; pilot 2–3 clients.

**Phase 2 (8–12 weeks): Real apply + verify**

* Ramp production execution + webhooks.
* QBO BillPayment confirmation + audit notes.
* Hygiene tray for stale/mismatch.
  **Goal:** First closed-loop execution with proof; 1–2 design-partner firms, 10–20 clients total.

**Phase 3 (12–20 weeks): Scale to firm reality**

* Multi-client console, batch ops, user roles, email digests.
* Bill.com adapter; Stripe read.
* Nightly health scans + operator dashboard.
  **Goal:** 3–5 firms; 50–100 clients; weekly cadence; references.

# 12) What we explicitly **don’t** build (now)

* **Email inbox/OCR** (defer to rails or CSV).
* **ML bookkeeping** (deterministic rules suffice; consume others’ outputs).
* **Full FP&A** (stick to 7–14-day control horizon; 30–60-day trend only in digest).
* **Owning rails/ledger** (our wedge is governance, not replacement).

# 13) “Digits moved off QBO” reality check (our stance)

* If a firm runs **Digits-stack end-to-end**, RowCol can *still* be sold as the **policy + proof overlay** (consume their normalized AR/AP/balances via API if exposed).
* Our real beachhead is the much larger set of firms who **won’t rip QBO/Ramp/Bill** in the next 3–5 years. We make that stack *behave like one system*.

# 14) KPIs & acceptance criteria (prove we matter)

* **Time:** <10 min/client/week to run Friday check (from 30–45).
* **Coverage:** ≥50% of bills flow through RowCol approvals by week 4.
* **Safety:** 0 payroll misses tied to approvals; override rate <15%.
* **Hygiene:** stale-balance incidents fall by 80% after week 2.
* **Trust:** 100% of approvals have human-readable rationale + evidence links.
* **Retention signal:** partners forward digests to clients without edits.

# 15) “If you must add AI” (tight, optional)

* **Digest prose:** turn structured reasons → sentences (LLM guarded, no decisions).
* **Hygiene hinting:** rank which issue to fix first.
* **Mapping helpers:** fuzzy vendor matching suggestions.
  Everything must be **read-only suggestions** with human accept; all decisions remain deterministic.

---

### Bottom line

Build the **control plane** that makes QBO + Bill/Ramp + Plaid + Stripe act like a single, disciplined system. Keep the loop small, the rules deterministic, the logs immutable, and the UI boringly trustworthy. Ship in thin vertical slices that produce a digest a partner can send the same day. That’s the fastest, safest way to catch up *and* stay differentiated.
