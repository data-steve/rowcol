from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domains.core.services.service import ServiceService
from domains.core.schemas.service import Service, ServiceCreate, ServicePreview
from database import get_db

router = APIRouter(prefix="/api", tags=["Services"])

@router.post("/services", response_model=Service)
async def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    service_service = ServiceService(db)
    return service_service.create_service(service)

@router.get("/services", response_model=list[Service])
async def list_services(tier: str = None, preview: bool = False, firm_id: str = None, db: Session = Depends(get_db)):
    service_service = ServiceService(db)
    return service_service.list_services(firm_id, tier)

@router.get("/services/{service_id}", response_model=Service)
async def get_service(service_id: int, firm_id: str, db: Session = Depends(get_db)):
    service_service = ServiceService(db)
    try:
        return service_service.get_service(service_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/services/{service_id}/preview", response_model=ServicePreview)
async def preview_service(service_id: int, firm_id: str, db: Session = Depends(get_db)):
    service_service = ServiceService(db)
    try:
        return service_service.preview_service(service_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))