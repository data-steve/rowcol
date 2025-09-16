import pytest
from domains.integrations.qbo_integration import QBOIntegration
from domains.core.models import Firm

@pytest.fixture
def mock_firm():
    return Firm(id=1, name="Test", qbo_tenant_id="test123", current_balance=6000.0)

def test_get_bills(mock_firm):
    qbo = QBOIntegration(mock_firm)
    bills = qbo.get_bills(14)
    assert len(bills) >= 1
    assert bills[0]['amount'] == 5000.0

def test_get_invoices(mock_firm):
    qbo = QBOIntegration(mock_firm)
    invoices = qbo.get_invoices(30)
    assert len(invoices) == 1
    assert invoices[0]['aging_days'] > 30
