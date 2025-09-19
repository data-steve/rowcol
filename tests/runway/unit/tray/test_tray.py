from sqlalchemy.orm import Session
from runway.tray.services.tray import TrayService
from runway.tray.models.tray_item import TrayItem
from datetime import datetime

def test_get_tray_items(db: Session):
    tray_item = TrayItem(
        business_id=1,
        type="bill",
        qbo_id="bill_001",
        status="pending",
        priority="high",
        due_date=datetime.utcnow()
    )
    db.add(tray_item)
    db.commit()
    tray_service = TrayService(db)
    items = tray_service.get_tray_items(business_id=1)
    assert len(items) == 1
    assert items[0]["type"] == "bill"
    assert items[0]["qbo_id"] == "bill_001"
