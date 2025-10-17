from tests.cashcall_scenarios.fixtures_cashcall import bank_txns_s1, bank_txns_s2, bank_txns_s3
# suppose we have a digest math helper that consumes ledger rows
from domains.identity_graph.consolidate import consolidate_to_ledger

def test_digest_math_runway_inputs_exist():
    # crude smoke: ensure we can produce at least 1 INFLOW per settlement across scenarios
    identities = []
    edges = []
    for i, bt in enumerate(bank_txns_s1 + bank_txns_s2 + bank_txns_s3):
        identities.append({"id": f"settle{i}", "kind": "SETTLEMENT", "amount_cents": bt["amount_cents"], "posted_at": bt["posted_at"]})
    ledger = consolidate_to_ledger(identities, edges)  # no payouts -> direct settlements become ledger rows
    assert len(ledger) >= 1
    assert all(abs(row["amount_cents"]) > 0 for row in ledger)
