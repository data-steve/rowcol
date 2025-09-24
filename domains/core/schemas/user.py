from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict

class UserBase(BaseModel):
    business_id: str
    role: str
    email: str
    full_name: str
    permissions: Optional[Dict] = None
    training_level: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: str
    is_active: Optional[bool] = True
    model_config = ConfigDict(from_attributes=True)

# API Request/Response schemas  
class UserUpdate(BaseModel):
    """Update schema for User"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[Dict] = None
    training_level: Optional[str] = None
    is_active: Optional[bool] = None