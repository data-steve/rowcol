from pydantic import BaseModel

class StaffBase(BaseModel):
    firm_id: str
    user_id: int
    role: str
    training_level: str

class StaffCreate(StaffBase):
    pass

class Staff(StaffBase):
    staff_id: int

    class Config:
        from_attributes = True