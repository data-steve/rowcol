import vcr
import pytest

# This is a placeholder test. It will fail without a proper 'qbo_client' fixture.
# We can implement the fixture when we work on a QBO-related task.
@pytest.mark.skip(reason="qbo_client fixture not yet implemented")
@vcr.use_cassette("tests/cassettes/qbo_get_payments.yaml")
def test_get_payments_contract(qbo_client):
    rows = qbo_client.get_payments(limit=2)
    assert all({"Id", "TxnDate"} <= set(r) for r in rows)