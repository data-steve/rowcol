import pytest
from domains.tray.services.tray import TrayService
from domains.bank.models.bank_transaction import BankTransaction

def test_get_tray_items(db, test_firm, test_bank_transaction):
    service = TrayService(db)
    items = service.get_tray_items(test_firm.firm_id)
    assert len(items) == 1
    assert items[0]["id"] == test_bank_transaction.transaction_id
    assert items[0]["suggested_action"] == "manual_investigation"

def test_confirm_action(db, test_firm, test_bank_transaction):
    service = TrayService(db)
    transaction = service.confirm_action(test_firm.firm_id, test_bank_transaction.transaction_id, "confirm", [1])
    assert transaction.status == "matched"
    assert transaction.invoice_ids == [1]
