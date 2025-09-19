from sqlalchemy.orm import Session
from runway.tray.services.tray import TrayService

def test_get_tray_items(db: Session, test_tray_item):
    tray_service = TrayService(db)
    items = tray_service.get_tray_items(business_id=test_tray_item.business_id)
    assert len(items) == 1
    assert items[0]["type"] == "bill"
    assert items[0]["qbo_id"] == "bill_001"

def test_confirm_action(db: Session, test_tray_item):
    tray_service = TrayService(db)
    item = tray_service.confirm_action(
        business_id=test_tray_item.business_id,
        tray_item_id=test_tray_item.id,
        action="confirm",
        invoice_ids=[1]
    )
    assert item.status == "resolved"
    assert item.invoice_ids == [1]
