from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.staff import Staff as StaffModel
from schemas.staff import Staff
from database import get_db

router = APIRouter(prefix="/api", tags=["Staff"])

@router.post("/staff", response_model=Staff)
async def create_staff(staff: Staff, db: Session = Depends(get_db)):
    db_staff = StaffModel(**staff.dict())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff

@router.get("/staff/{staff_id}", response_model=Staff)
async def get_staff(staff_id: int, firm_id: str, db: Session = Depends(get_db)):
    staff = db.query(StaffModel).filter(StaffModel.staff_id == staff_id, StaffModel.firm_id == firm_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff