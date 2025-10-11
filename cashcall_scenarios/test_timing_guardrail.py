from tests.cashcall_scenarios.fixtures_cashcall import stripe_payouts_s6, bank_txns_s6
from domains.identity_graph.services import timing_guardrail

def test_late_settlement_triggers_timing_exception():
    payout = stripe_payouts_s6[0]
    settlement = bank_txns_s6[0]
    ex = timing_guardrail(payout_arrival_date=payout["arrival_date"], settlement_posted_at=settlement["posted_at"])
    assert ex and ex["kind"] == "TIMING"
