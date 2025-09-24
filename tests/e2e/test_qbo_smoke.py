import os
import pytest

pytestmark = pytest.mark.e2e

QBO_LIVE = os.getenv("QBO_LIVE") == "1"

# This is a placeholder test. It will fail without a proper 'qbo_live_client' fixture.
@pytest.mark.skipif(not QBO_LIVE, reason="Set QBO_LIVE=1 to run live smoke test")
def test_qbo_smoke_live(qbo_live_client):
    payments = qbo_live_client.get_payments(limit=1)
    assert payments and "Id" in payments[0]