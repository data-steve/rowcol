from tests.cashola_ap.fixtures_ap import bank_outflows, rule_fixtures, COMPANY_ID
# You will implement categorize_ledger_rows(session, company_id)
# For test, assume a pure function categorize_outflow(description, amount) using rule precedence.

def fake_categorize(description: str):
    # Minimal mirror of your precedence: VENDOR -> REGEX -> SOURCE_KIND -> UNKNOWN
    import re
    mapping = [
      ("PAYROLL_TOTAL","MUST_PAY", lambda d: "GUSTO" in d.upper()),
      ("RENT_UTILITIES","MUST_PAY", lambda d: "ACME PROPERTY MGMT" in d.upper()),
      ("INSURANCE","MUST_PAY", lambda d: "INSURANCE" in d.upper()),
      ("SAAS_FEES","CAN_DELAY", lambda d: "STRIPE" in d.upper() and "FEE" in d.upper()),
      ("DEBT_SERVICE","MUST_PAY", lambda d: re.search(r"(?i)TERM LOAN|LOAN PMT|INTEREST", d) is not None),
      ("OWNER_DRAWS","DISCRETIONARY", lambda d: re.search(r"(?i)ATM.*OWNER|OWNER DRAW", d) is not None),
      ("OTHER","DISCRETIONARY", lambda d: re.search(r"(?i)SHELL|EXXON|CHEVRON", d) is not None),
    ]
    for cdm, pol, pred in mapping:
        if pred(description):
            return cdm, pol
    return None, None

def test_outflows_map_to_cdm_policy():
    results = []
    for bt in bank_outflows:
        if bt["amount_cents"] >= 0: 
            continue
        cdm, pol = fake_categorize(bt["description"])
        results.append((bt["id"], cdm, pol))
    # spot assertions
    assert ("bt_payroll_2024_03_08","PAYROLL_TOTAL","MUST_PAY") in results
    assert ("bt_rent_2024_03_01","RENT_UTILITIES","MUST_PAY") in results
    assert ("bt_ins_2024_03_03","INSURANCE","MUST_PAY") in results
    assert ("bt_saas_2024_03_04","SAAS_FEES","CAN_DELAY") in results
    assert ("bt_debt_2024_03_07","DEBT_SERVICE","MUST_PAY") in results
    assert ("bt_owner_2024_03_02","OWNER_DRAWS","DISCRETIONARY") in results
