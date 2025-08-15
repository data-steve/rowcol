from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domains.core.services.staff import StaffService
from domains.core.schemas.staff import Staff
from database import get_db

router = APIRouter(prefix="/api", tags=["Staff"])

@router.post("/staff", response_model=Staff)
async def create_staff(staff: Staff, db: Session = Depends(get_db)):
    service = StaffService(db)
    return service.create_staff(staff)

@router.get("/staff/{staff_id}", response_model=Staff)
async def get_staff(staff_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = StaffService(db)
    try:
        return service.get_staff(staff_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))