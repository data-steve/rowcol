from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from db.session import get_db
from runway.tray.services.tray import TrayService

router = APIRouter()

@router.get("/")
def get_tray(business_id: int, db: Session = Depends(get_db)):
    service = TrayService(db)
    return service.get_tray_items(business_id)

@router.post("/{id}/confirm")
def confirm_action(business_id: int, id: int, action: str, invoice_ids: Optional[List[int]] = None, db: Session = Depends(get_db)):
    return TrayService(db).confirm_action(business_id, id, action, invoice_ids)
