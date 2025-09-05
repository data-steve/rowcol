Here’s a **fully rewritten version of your ServicePro scenario doc** so it’s directly useful for **Cashola** development and testing. I’ve cut out all the accrual/job-costing/rev-rec content and re-framed the scenarios as **AR unbundling, payout→settlement matching, exception handling, and digest validation**—all aligned with the current Cashola strategyand build plan.

---

# Cashola Test Scenarios — AR Unbundling & Reconciliation

## 🎯 Purpose

Provide **realistic, messy input cases** to validate Cashola’s core loop:

1. Ingest raw events (bank via Plaid, payouts via Stripe/JobberPay, invoices/payments via Jobber).
2. Build an **identity graph** (link payouts → settlements, charges → payouts, payments → invoices).
3. Consolidate to the **cash ledger** (count once, bank-timed).
4. Run **AR unbundling** (payout composition → invoices).
5. Surface **exceptions** (`AR_AMBIG`, `NO_MATCH`, `UNMAPPED`, `TIMING`, `GHOST_AR`).
6. Confirm **Friday digest math** (cash, runway, AR plan, must-pay AP).

---

## 🏗️ Scenario Set

### Scenario 1: Multi-Installment Job

* **Invoice 1:** \$7,500 due Feb 25, paid Feb 28.
* **Invoice 2:** \$7,500 due Mar 20, paid Apr 3.
* **Processor:** Stripe creates payouts Mar 1 and Apr 5 (net of fees).
* **Bank:** Credits Mar 1 (\$7,252.20) and Apr 5.
* **Test Points:**

  * Payout→settlement match with ±2d window.
  * April settlement should **not double count March work**.
  * Unbundling confirms invoices sum = gross.

### Scenario 2: Clean Single-Job Invoice

* **Invoice:** \$3,200 issued Mar 15, paid Mar 28.
* **Stripe:** Fee \$122.80, net \$3,077.20.
* **Bank:** Credit Mar 30 (\$3,077.20).
* **Test Points:**

  * Exact invoice↔charge match → ledger INFLOW only once.
  * Fee recorded as composition under payout, CDM = `SAAS_FEES`.

### Scenario 3: Recurring + Emergency

* **Recurring Contract:** \$1,200/mo, paid Mar 1.
* **Emergency Add-on:** \$800 invoiced Mar 20, paid Apr 5.
* **Test Points:**

  * Multiple invoices tied to one customer; some settled in-period, some delayed.
  * Emergency invoice → **GHOST\_AR** until Apr bank credit arrives.

### Scenario 4: Ambiguous Multi-Job Payout

* **Invoices:** Job A \$2,550, Job B \$1,983.
* **Stripe:** Bundles into one payout \$4,533 (after fees).
* **Bank:** Credit Mar 22.
* **Test Points:**

  * Subset-sum has >1 candidate match set → create `AR_AMBIG` exception.
  * Tray shows candidate sets, dispatcher resolves.

---

## 💵 Payment Flow Complications

* **Stripe Fees:**

  * Applied per charge; should stay under payout as `COMPOSED_OF` edges.
  * Ledger counts **net once at bank date**.
* **Bank Settlement Lag:**

  * T+2 business days; end-of-month rollovers create **TIMING** exceptions.
* **Off-platform Cash:**

  * Bank credit with no processor ref → create `UNMAPPED` → tray action to categorize (e.g. `OTHER_INCOME`).

---

## 🧪 Test Cases

1. **payout\_settlement\_match\_test**

   * Unique settlement match → confidence=1.0.
   * Multiple candidates → `AR_AMBIG`.
   * No candidates → `NO_MATCH`.

2. **unbundle\_subset\_sum\_test**

   * Unique subset of invoices matches gross → auto.
   * Multiple subsets → `AR_AMBIG`.
   * No subsets → `NO_MATCH`.

3. **fee\_handling\_test**

   * Fee rows remain composition; not double-counted in ledger.
   * CDM assigns `SAAS_FEES`.

4. **ghost\_ar\_test**

   * Ops shows invoice “paid,” but no bank/processor → `GHOST_AR`.

5. **timing\_guardrail\_test**

   * Settlement arrives >2d outside expected → `TIMING`.

6. **digest\_consistency\_test**

   * Runway calculation matches: `cash_today + E[AR 0–7d] − must_pay_outflows`.
   * Exceptions summary lists open items.

---

## 🚦 Success Criteria

* **Reconciled deposits:** ≥95% of inflow value correctly linked.
* **Exceptions load:** <10 items, cleared <10 min/wk.
* **Automation:** ≥70% matches by week 4.
* **Runway error:** < ±0.3 weeks vs human baseline.

---

## 📂 Suggested File Placement

```
tests/cashola_scenarios/
  SCENARIOS_AR_Unbundling.md
  test_payout_settlement_match.py
  test_unbundle_subset_sum.py
  test_fee_handling.py
  test_ghost_ar.py
  test_timing_guardrail.py
  test_digest_consistency.py
```

---

✅ This version drops accrual/rev-rec and job costing. It’s now a **scenario + test plan file** aligned to Cashola’s **identity graph + cash ledger** model.

Do you want me to actually generate the **pytest skeletons** for these 6 test files so you can drop them straight into `tests/`?
