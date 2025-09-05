from tests.cashola_scenarios.fixtures_cashola import COMPANY_ID, bank_txns_s1, stripe_payouts_s1
from domains.identity_graph.services import link_payout_to_settlement

def test_unique_payout_settlement_match():
    payout = stripe_payouts_s1[0]  # po_mall_50
    candidates = [( "id_settle_1", bank_txns_s1[0]["amount_cents"], bank_txns_s1[0]["posted_at"], bank_txns_s1[0]["description"] )]
    res = link_payout_to_settlement(company_id=COMPANY_ID, payout_identity_id="id_payout_1", candidate_settlements=candidates, net_amount_cents=payout["net_cents"])
    assert res is not None
    sid, conf, reason = res
    assert conf >= 0.8
