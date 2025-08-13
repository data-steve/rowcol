from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.service import Service as ServiceModel  
from schemas.service import Service, ServiceCreate, ServicePreview
from database import get_db

router = APIRouter(prefix="/api", tags=["Services"])

@router.post("/services", response_model=Service)
async def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    db_service = ServiceModel(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.get("/services", response_model=list[Service])
async def list_services(tier: str = None, preview: bool = False, firm_id: str = None, db: Session = Depends(get_db)):
    query = db.query(ServiceModel)
    if firm_id:
        query = query.filter(ServiceModel.firm_id == firm_id)
    if tier:
        query = query.filter(ServiceModel.tier == tier)
    services = query.all()
    return services

@router.get("/services/{service_id}", response_model=Service)
async def get_service(service_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = db.query(ServiceModel).filter(
        ServiceModel.service_id == service_id,
        ServiceModel.firm_id == firm_id
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.get("/services/{service_id}/preview", response_model=ServicePreview)
async def preview_service(service_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = db.query(ServiceModel).filter(
        ServiceModel.service_id == service_id,
        ServiceModel.firm_id == firm_id
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return ServicePreview(
        service_id=service.service_id,
        name=service.name,
        task_sequence=service.task_sequence,
        compliance_requirements=[{"form": "bookkeeping", "requirement": "Provide QBO access"}]
    )