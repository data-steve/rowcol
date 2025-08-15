from pydantic import BaseModel
from typing import Optional, Dict

class UserBase(BaseModel):
    firm_id: str
    role: str
    email: str
    permissions: Optional[Dict] = None
    training_level: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: int

    class Config:
        from_attributes = True