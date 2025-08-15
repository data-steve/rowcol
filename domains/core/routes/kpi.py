from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from domains.core.services.kpi import KPIService
from database import get_db

router = APIRouter(prefix="/api", tags=["KPIs"])

@router.get("/kpis")
async def get_kpis(firm_id: str, db: Session = Depends(get_db)):
    service = KPIService(db)
    return service.calculate_kpis(firm_id)
