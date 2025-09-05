from tests.cashola_ap.fixtures_ap import bank_outflows
# Using your consolidate_to_ledger() for SETTLEMENT-only outflows (no processor).
from domains.identity_graph.consolidate import consolidate_to_ledger

def test_bank_debits_become_outflow_rows():
    identities = []
    edges = []
    for i, bt in enumerate(bank_outflows):
        identities.append({
          "id": f"settle_out_{i}",
          "kind":"SETTLEMENT",
          "amount_cents": bt["amount_cents"],
          "posted_at": bt["posted_at"] if "posted_at" in bt else bt["posted_at"] if "posted_at" in bt else "2024-03-01T00:00:00Z",
          "description": bt["description"]
        })
    ledger = consolidate_to_ledger(identities, edges)
    # Only negative amounts should be OUTFLOW
    outs = [r for r in ledger if r["direction"]=="OUTFLOW"]
    assert len(outs) >= 1
    assert all(r["amount_cents"] < 0 for r in outs)
