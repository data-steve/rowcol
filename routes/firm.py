from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.firm import FirmService
from schemas.firm import Firm
from database import get_db

router = APIRouter(prefix="/api", tags=["Firms"])

@router.post("/firms", response_model=Firm)
async def create_firm(firm: Firm, db: Session = Depends(get_db)):
    service = FirmService(db)
    return service.create_firm(firm)

@router.get("/firms/{firm_id}", response_model=Firm)
async def get_firm(firm_id: str, db: Session = Depends(get_db)):
    service = FirmService(db)
    try:
        return service.get_firm(firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))