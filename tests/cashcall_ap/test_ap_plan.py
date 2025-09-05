from tests.cashola_ap.fixtures_ap import bank_outflows, company_policy
# Pretend we have build_ap_plan(ledger_rows) that separates MUST_PAY vs CAN_DELAY and computes runway deltas.

def build_ap_plan(rows, policy):
    must_pay = [r for r in rows if r.get("policy")=="MUST_PAY"]
    can_delay = [r for r in rows if r.get("policy")=="CAN_DELAY"]
    return {
        "must_pay_total": sum(r["amount_cents"] for r in must_pay),
        "can_delay_total": sum(r["amount_cents"] for r in can_delay),
        "must_pay": must_pay,
        "can_delay": can_delay
    }

def test_ap_plan_buckets_and_totals():
    # minimal synthesized ledger rows (as if categorized)
    ledger_rows = [
      {"id":"l1","direction":"OUTFLOW","amount_cents":-18_750_00,"cdm_key":"PAYROLL_TOTAL","policy":"MUST_PAY"},
      {"id":"l2","direction":"OUTFLOW","amount_cents":-3_200_00,"cdm_key":"RENT_UTILITIES","policy":"MUST_PAY"},
      {"id":"l3","direction":"OUTFLOW","amount_cents":-1_150_00,"cdm_key":"INSURANCE","policy":"MUST_PAY"},
      {"id":"l4","direction":"OUTFLOW","amount_cents":-249_00,"cdm_key":"SAAS_FEES","policy":"CAN_DELAY"},
      {"id":"l5","direction":"OUTFLOW","amount_cents":-2_450_00,"cdm_key":"DEBT_SERVICE","policy":"MUST_PAY"},
      {"id":"l6","direction":"OUTFLOW","amount_cents":-1_000_00,"cdm_key":"OWNER_DRAWS","policy":"DISCRETIONARY"},
    ]
    plan = build_ap_plan(ledger_rows, company_policy)
    assert plan["must_pay_total"] == (-18_750_00 - 3_200_00 - 1_150_00 - 2_450_00)
    assert plan["can_delay_total"] == (-249_00)
    assert len(plan["must_pay"]) == 4
