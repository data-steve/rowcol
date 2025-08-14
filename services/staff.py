from sqlalchemy.orm import Session
from models.staff import Staff as StaffModel
from schemas.staff import Staff
from typing import List

class StaffService:
    def __init__(self, db: Session):
        self.db = db

    def create_staff(self, staff: Staff) -> StaffModel:
        """Create a new staff member."""
        db_staff = StaffModel(**staff.dict())
        self.db.add(db_staff)
        self.db.commit()
        self.db.refresh(db_staff)
        return db_staff

    def get_staff(self, staff_id: int) -> StaffModel:
        """Get a staff member by ID."""
        staff = self.db.query(StaffModel).filter(StaffModel.staff_id == staff_id).first()
        if not staff:
            raise ValueError("Staff not found")
        return staff

    def list_staff(self) -> List[StaffModel]:
        """List all staff members."""
        staff = self.db.query(StaffModel).all()
        return staff
