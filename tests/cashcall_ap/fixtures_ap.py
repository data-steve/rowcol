COMPANY_ID = "co_demo"
BANK_ACCOUNT_ID = "ba_demo_operating"

# Bank debits (posted_at ISO strings, amounts negative in cents)
bank_outflows = [
  # Payroll (Gusto) – MUST_PAY, near Friday
  {"id":"bt_payroll_2024_03_08", "posted_at":"2024-03-08T10:02:00Z", "amount_cents":-18_750_00, "description":"GUSTO*PAYROLL 555-1234"},
  # Rent – MUST_PAY, monthly cadence
  {"id":"bt_rent_2024_03_01", "posted_at":"2024-03-01T09:03:00Z", "amount_cents":-3_200_00, "description":"ACME PROPERTY MGMT RENT"},
  # Insurance – MUST_PAY (often monthly/quarterly)
  {"id":"bt_ins_2024_03_03", "posted_at":"2024-03-03T11:10:00Z", "amount_cents":-1_150_00, "description":"STATEWIDE INSURANCE PREMIUM"},
  # SaaS fees – CAN_DELAY (policy: ok to push 1 week if needed)
  {"id":"bt_saas_2024_03_04", "posted_at":"2024-03-04T08:40:00Z", "amount_cents":-249_00, "description":"STRIPE*MONTHLY PLATFORM FEE"},
  # Fuel – DISCRETIONARY by default (or OTHER), not must-pay
  {"id":"bt_fuel_2024_03_05", "posted_at":"2024-03-05T12:01:00Z", "amount_cents":-380_00, "description":"SHELL OIL 1234 ANYTOWN"},
  # Debt service – MUST_PAY
  {"id":"bt_debt_2024_03_07", "posted_at":"2024-03-07T09:00:00Z", "amount_cents":-2_450_00, "description":"FIRST BANK TERM LOAN PMT"},
  # Owner draw – DISCRETIONARY
  {"id":"bt_owner_2024_03_02", "posted_at":"2024-03-02T13:00:00Z", "amount_cents":-1_000_00, "description":"ATM WITHDRAWAL *OWNER"},
  # Odd timing (policy: rent due 1st, settled 6th) -> TIMING exception
  {"id":"bt_rent_late_2024_04_06", "posted_at":"2024-04-06T09:00:00Z", "amount_cents":-3_200_00, "description":"ACME PROPERTY MGMT RENT"}
]

# Minimal rule set (CDM + Policy). In product, these live in cdm_rule table.
# Here we keep as test-time inputs for the policy adapter.
rule_fixtures = [
  # VENDOR → CDM + policy
  {"scope":"VENDOR","predicate":{"icontains":"GUSTO"}, "outcome_cdm_key":"PAYROLL_TOTAL","outcome_policy":"MUST_PAY","priority":10},
  {"scope":"VENDOR","predicate":{"icontains":"ACME PROPERTY MGMT"}, "outcome_cdm_key":"RENT_UTILITIES","outcome_policy":"MUST_PAY","priority":10},
  {"scope":"VENDOR","predicate":{"icontains":"STATEWIDE INSURANCE"}, "outcome_cdm_key":"INSURANCE","outcome_policy":"MUST_PAY","priority":10},
  {"scope":"VENDOR","predicate":{"regex":"(?i)STRIPE.*FEE|PLATFORM"}, "outcome_cdm_key":"SAAS_FEES","outcome_policy":"CAN_DELAY","priority":20},
  {"scope":"VENDOR","predicate":{"regex":"(?i)SHELL|EXXON|CHEVRON"}, "outcome_cdm_key":"OTHER","outcome_policy":"DISCRETIONARY","priority":50},
  {"scope":"REGEX", "predicate":{"regex":"(?i)TERM LOAN|LOAN PMT|INTEREST"}, "outcome_cdm_key":"DEBT_SERVICE","outcome_policy":"MUST_PAY","priority":30},
  {"scope":"REGEX", "predicate":{"regex":"(?i)ATM.*OWNER|OWNER DRAW"}, "outcome_cdm_key":"OWNER_DRAWS","outcome_policy":"DISCRETIONARY","priority":40}
]

# Company policy knobs that AP plan might reference
company_policy = {
  "can_delay_days_default": 7,
  "must_pay_window_days": 7
}
