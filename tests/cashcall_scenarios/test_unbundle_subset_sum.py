from tests.cashola_scenarios.fixtures_cashola import jobber_invoices_s4, stripe_payouts_s4
from domains.identity_graph.services import unbundle_payout  # implement per spec

def test_ambiguous_subset_sum_creates_exception(monkeypatch):
    payout = stripe_payouts_s4[0]
    # Build "ops payments" like signals (use invoice amounts as candidates)
    ops_payments = [{"invoice_id": inv["id"], "amount_cents": inv["amount_cents"], "paid_at": "2024-03-20T12:00:00Z"} for inv in jobber_invoices_s4]
    matched, exceptions = unbundle_payout(payout=payout, ops_payments=ops_payments, fee_total=0, tol=50)
    # Two combos fit -> expect AR_AMBIG exception present
    kinds = [e["kind"] for e in exceptions]
    assert "AR_AMBIG" in kinds
