# Oodaloo — Strategy Doc (v1)

**One-liner:** *Jobber helps make revenue. Oodaloo helps make profit.*
**Core wedge:** Weekly **cash-basis job profitability** + **payroll runway**, fixed fast by a **dispatcher exceptions tray**.
**Integrations now:** **Jobber** + **Plaid** only. (QBO **read** optional later; QBO **write** only in paid service.)

---

## 1) What Oodaloo is (and isn’t)

* **Is:** Profit decisions + cash-in autopilot for Jobber/HCP shops. We reconcile **bank reality ↔ Jobber**, compute **cash job GM** and **payroll runway**, and **prioritize** the few AR actions that move cash this week.
* **Is not:** Full bookkeeping, payroll, or an estimating/field ops suite. No new CRM to learn.

**Owner experience:** One Friday email (“Did we cover payroll?”), one weekly approval (“Collect these top N to add +Y weeks”), and a dispatcher clears a few exceptions (<10 min/wk).

---

## 2) Why it works

* **Bank-truth vs platform-truth.** Jobber shows revenue/AR; we tie it to **bank deposits**, fees, and off-platform payments. That ends “why doesn’t the bank match?” churn and stops chasing already-paid invoices.
* **Pareto on collections.** 10–20 invoices drive most runway. We rank them by **amount × age × pay-likelihood** and show the payoff (**+weeks of runway**).
* **Low-friction workflow.** Dispatcher fixes the few data issues (confirm/split/assign/ignore) in a fast tray; owners just read and approve.

---

## 3) Who we serve (and who we downplay)

**Best fit (8–20 staff; \$1–\$5M revenue):**
HVAC & plumbing (installs), electrical, glass/garage door, light roofing/remodel, commercial janitorial/landscaping, pool service (routes + equipment). These see **AR lag** and **materials spend**.

**Lower fit (for add-ons):** One-off consumer cash jobs (cleaning/handyman). Still buy **Core** (profit email + bank↔Jobber tie-out); AR add-on is optional/hidden if DSO <5 days.

---

## 4) Product overview (modules & flow)

**A) Profit Clarity (Core SaaS)**

* **Exceptions tray (dispatcher):** confirm/assign expenses to jobs, split lump payouts, off-job income, ignore personal spend, make vendor rules.
* **Bank↔Jobber reconciliation:** deposits ↔ payments (fee-aware), gaps/off-platform.
* **Cash job GM & runway:** revenue (payments) − tagged costs − labor burden ⇒ **job winners/losers** + **weeks of payroll runway**.
* **Friday owner digest:** runway, cash collected, AR at risk, bank↔Jobber gaps, top losers/winners, **data-health** row.

**B) Cash Discipline (Add-on)**

* **AR plan:** rank top N invoices (amount × age × pay-likelihood), suggest cadence, cap special engagements/day, respect VIP “do-not-nag”.
* **Attempt logging & audit:** log in Oodaloo **and** write a small **note/custom field** back to Jobber.
* **No duplicate sends:** we **prioritize** and create call tasks / open invoice links; native Jobber automations keep sending. Stop chasing the instant **bank** shows paid.

**C) Unbundling (Add-on)**

* Split Stripe/JobberPay net payouts into invoices (+fees), with cadence priors; prevents fake overdues and improves trust.

**D) AP Assist (Light Add-on)**

* **Due-soon map** (late-fee risks; large auto-debits next 7 days).
* **Duplicate/NSF/fee catcher.**
* **Delay-OK nudges:** “Delay \$X (vendor OK) → **+0.6 weeks** runway.”
* **Assign-to-job suggestions** for obvious materials (COGS pronto).

**E) Later: Benchmarking**

* Cohorts (trade × crew × revenue). Show medians/IQR when N≥20; quarterly PDF with 3 “plays”.

---

## 5) Pricing & packaging (by firm type/size)

**Simple, company-based pricing (no per-seat).** Seats: Owner + Dispatcher/Admin included.

| Tier                                 | What’s included                                                                       | Who buys it            | Price                          |
| ------------------------------------ | ------------------------------------------------------------------------------------- | ---------------------- | ------------------------------ |
| **Core**                             | Profit email, Exceptions Tray, Bank↔Jobber tie-out, Job cash GM & runway, Data-health | Everyone               | **\$179/mo** (founder \$149)   |
| **Core + Cash Discipline**           | Core + AR plan + attempt log + CRM notes                                              | Firms with DSO ≥7–10d  | **\$228/mo**                   |
| **Pro (Core + Cash + Unbundling)**   | Add payout splitter                                                                   | Stripe/JobberPay users | **\$257/mo**                   |
| **Ops Pro (add AP Assist)**          | Due-soon, duplicates, delay-OK nudges, materials tag                                  | Materials-heavy trades | **\$286–\$306/mo**             |
| **Benchmarking**                     | Monthly overlay or Quarterly PDF                                                      | After 3 months of data | **+\$20/mo** or **\$200/qtr**  |
| **Succession-Ready Close (Service)** | Month/quarter close, tie-out, posting pack, **QBO write**                             | 10–20% of logos        | **\$600+/mo** or **\$900/qtr** |

**By archetype (guidance):**

* **Cash jobs (consumer):** Core (\$149–\$179).
* **Episodic mid/high-ticket:** Core + Cash (\$228); add Unbundling if payouts.
* **Recurring B2B:** Core + Cash + AP Assist (\$257–\$306).

**Why this clears \$200 ARPU:** It **moves cash** (DSO ↓, runway ↑) and **reduces rework** (reconciliation, mis-chasing), without payroll/QBO integrations.

---

## 6) What’s left for bookkeeping (and how we handle it)

**We do not replace bookkeepers.** Oodaloo automates routing & tagging; bookkeepers still own:

* Period close & reconciliations; Undeposited Funds; misapplied payments
* Sales tax & payroll tax filings; 1099s
* Accruals/deferrals, WIP, prepaids; controller-level review
* QBO hygiene

**Plan:**

* **Phase 1–2:** Build a **referral bench** (trusted CAS/bookkeepers). Offer **posting pack exports** (CSV/Excel) with tie-out reports.
* **Phase 3 (optional):** Turn on **Succession-Ready Close** in-house for selected clients. QBO **write** only here.

---

## 7) How it actually works (sources & guardrails)

* **Integrations:** Jobber GraphQL (jobs/invoices/payments/quotes), webhooks + delta poll; Plaid (bank + primary card).
* **Labor burden:** per-role weekly cost (input) allocated by job hours if present; else revenue or job count (config).
* **Quote aging:** change-data capture going forward; optional **one-time CSV/email** backfill for historical “status changed at.”
* **No duplicate sends:** We **prioritize**; the platform **sends**. We create call tasks or open links; we log attempts and write a note.
* **Data-health HUD:** last bank/Jobber sync, webhook lag, throttle hits, reconnect prompts.

---

## 8) ROI owners will feel (the 5 numbers)

1. **Runway weeks** (↑)
2. **DSO** (↓)
3. **\$ collected from plan** (weekly)
4. **% deposits reconciled** (≥95%)
5. **Median time per exception** (<60s)

Secondary AP metrics: **late fees avoided**, **duplicates caught**, **delay-OK cash shifted**, **materials tagged to jobs**.

---

## 9) Phases (what we’re building, in order)

**Phase 0 — Concierge (2 pilots; CSV ok):**

* Ship digest math + tray flows using exports. Validate burden model, runway, reconciliation.

**Phase 1 — Core (Jobber + Plaid):**

* Ingest + webhooks; Exceptions Tray (confirm/split/assign/ignore + rules + audit); Bank↔Jobber tie-out; Friday digest; Data-health HUD.

**Phase 2 — Cash Discipline (AR plan):**

* Scoring = amount × age × pay-history/engagement; policy knobs (min \$, aging focus, VIP list, daily cap, channel order); plan approve; attempt log; CRM note.

**Phase 3 — Unbundling:**

* Processor detection; net→gross; DP/greedy subset; cadence priors; confirm + remember.

**Phase 4 — AP Assist (light):**

* Due-soon map (late-fee/large auto-debits), duplicate/NSF/fee catcher, delay-OK nudges, materials assign suggestions.

**Phase 5 — Benchmarking:**

* Cohort medians + quarterly PDF (unlocked when N≥20 per band).

**Optional Adapters (post-PMF):** HCP, ServiceMonster, Workiz (same ingest loop).

---

## 10) Risks & mitigations

* **Data gaps (Jobber fields like quote status date):** CDC forward; optional CSV backfill; flag provenance.
* **Plaid noise (personal spend):** “Personal-Mixed” label; merchant ignore rules; CSV fallback for unsupported institutions.
* **Adoption risk (dispatcher time):** target <10 min/wk; show ROI in digest (cash/runway).
* **Spam/duplication:** never send in parallel; orchestrate native reminders; call tasks for escalations; write notes for audit.
* **Scope creep (payroll/QBO write):** deferred to service tier only.

---

## 11) Unit economics & targets

* **SaaS COGS:** \$15–\$25/logo (infra + Plaid + email) → **\~90% GM**.
* **Add-on attach (goal):** Cash 40–60%; Unbundling 15–30%; AP Assist 20–40%.
* **Service attach:** 10–20% of logos @ **\$600+/mo**, **50–60% GM**.
* **Milestones:**

  * 300 logos @ \$220 blended → \$792k ARR (GM \~\$670k).
  * 600 logos + 60 service clients → \$1.6M+ ARR (healthy cashflow for small team).

---

## 12) Naming & positioning

* **Brand:** **Oodaloo** (product) under **Preciate** (company) or vice-versa; keep both available.
* **External line:** *Jobber helps make revenue. Oodaloo helps make profit.*
* **Owner hook:** *Runway up. Guesswork down.*
* **In-product mantra:** *See. Decide. Collect. Grow.*

---

## 13) What success looks like (90 days)

* 10–20 paying logos on **Core**; ≥40% attach on **Cash Discipline** among AR-relevant firms.
* Median **exception time <60s**; **% deposits reconciled ≥95%**.
* Early case: **DSO −15–25%** and **runway +0.5–1.5 weeks** within 60–90 days.

