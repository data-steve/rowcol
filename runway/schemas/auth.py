from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any

class LoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class LoginResponse(BaseModel):
    """Response schema for successful login"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: Dict[str, Any]
    business: Optional[Dict[str, Any]] = None

class TokenRefreshRequest(BaseModel):
    """Request schema for token refresh"""
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    """Response schema for token refresh"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

class RegisterRequest(BaseModel):
    """Request schema for user registration"""
    email: EmailStr
    password: str
    confirm_password: str
    business_name: str
    user_role: Optional[str] = "owner"
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class PasswordResetRequest(BaseModel):
    """Request schema for password reset"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Request schema for password reset confirmation"""
    token: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
