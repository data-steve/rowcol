import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from domains.core.models import Firm

# Load mocks
with open('static/qbo_mock_data.json', 'r') as f:
    MOCK_BASE = json.load(f)

# Adapt from realistic_test_data.json
MOCK_DATA = MOCK_BASE.copy()
MOCK_DATA['invoices'] = [
    {"qbo_id": "inv_009", "customer": "Pine Valley HOA", "amount": 1983.34, "due_date": "2025-08-01", "aging_days": 42}
]
MOCK_DATA['bills'] = [
    {"qbo_id": "bill_001", "vendor": "Rent LLC", "amount": 5000.0, "due_date": "2025-09-22"}
]
MOCK_DATA['accounts'] = [{"id": "checking", "current_balance": 6000.0}]

class QBOIntegration:
    def __init__(self, firm: Firm):
        self.firm = firm
        self.tenant_id = firm.qbo_tenant_id

    def get_bills(self, due_days: int = 14) -> List[Dict[str, Any]]:
        today = datetime.now().date()
        return [b for b in MOCK_DATA['bills'] if (today - datetime.strptime(b['due_date'], '%Y-%m-%d').date()).days <= due_days]

    def get_invoices(self, aging_days: int = 30) -> List[Dict[str, Any]]:
        return [i for i in MOCK_DATA['invoices'] if i.get('aging_days', 0) > aging_days]

    def get_account_balance(self) -> float:
        return MOCK_DATA['accounts'][0]['current_balance']

def handle_webhook(payload: Dict) -> str:
    return "OK"
