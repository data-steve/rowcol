from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from ..services.tray import TrayService
from database import get_db

router = APIRouter(prefix="/api/v1/tray", tags=["Tray"])

@router.get("/")
def get_tray(firm_id: int, db: Session = Depends(get_db)):
    return TrayService(db).get_tray_items(firm_id)

@router.post("/{id}/confirm")
def confirm_action(firm_id: int, id: int, action: str, invoice_ids: Optional[List[int]] = None, db: Session = Depends(get_db)):
    return TrayService(db).confirm_action(firm_id, id, action, invoice_ids)
