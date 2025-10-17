from tests.cashcall_scenarios.fixtures_cashcall import jobber_invoices_s5
# assume a helper that inspects ops "paid" without bank/processor and raises exception
from domains.identity_graph.services import detect_ghost_ar

def test_ops_paid_without_bank_or_processor_becomes_ghost_ar():
    ex = detect_ghost_ar(invoices=jobber_invoices_s5, processor_events=[], bank_events=[])
    assert ex and ex["kind"] == "GHOST_AR"
