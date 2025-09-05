from tests.cashola_scenarios.fixtures_cashola import stripe_charges_s2, bank_txns_s2
from domains.identity_graph.consolidate import consolidate_to_ledger

def test_fees_do_not_double_count_in_ledger():
    identities = [
        {"id":"id_payout","kind":"PAYOUT","net_cents": stripe_charges_s2[0]["net_cents"]},
        {"id":"id_settle","kind":"SETTLEMENT","amount_cents": bank_txns_s2[0]["amount_cents"], "posted_at": bank_txns_s2[0]["posted_at"]},
    ]
    edges = [{"from":"id_payout","to":"id_settle","kind":"SETTLES"}]
    ledger = consolidate_to_ledger(identities, edges)
    assert len(ledger) == 1
    assert ledger[0]["amount_cents"] == bank_txns_s2[0]["amount_cents"]
    assert ledger[0]["direction"] == "INFLOW"
