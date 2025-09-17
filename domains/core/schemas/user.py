from pydantic import BaseModel
from typing import Optional, Dict

class UserBase(BaseModel):
    business_id: str
    role: str
    email: str
    permissions: Optional[Dict] = None
    training_level: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    role: Optional[str] = None
    email: Optional[str] = None
    permissions: Optional[Dict] = None
    training_level: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    user_id: str
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True