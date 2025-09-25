from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from domains.core.models.user import User
from domains.core.models.business import Business
from runway.schemas.auth import (
    LoginRequest, LoginResponse, TokenRefreshRequest, TokenRefreshResponse,
    RegisterRequest, PasswordResetRequest, PasswordResetConfirm
)
from runway.infrastructure.middleware.auth import create_access_token, verify_token
import hashlib
import secrets

router = APIRouter(tags=['auth'])

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    return f"{salt}:{hashlib.sha256((salt + password).encode()).hexdigest()}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hash_part = hashed.split(':')
        return hashlib.sha256((salt + password).encode()).hexdigest() == hash_part
    except ValueError:
        return False

@router.post('/auth/login', response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Get user's business
    business = db.query(Business).filter(Business.business_id == user.business_id).first()
    
    # Create access token
    token_data = {
        "sub": user.user_id,
        "business_id": user.business_id,
        "email": user.email,
        "role": user.role
    }
    
    expires_in = 86400 if not login_data.remember_me else 604800  # 1 day or 7 days
    access_token = create_access_token(token_data, expires_in)
    
    return LoginResponse(
        access_token=access_token,
        expires_in=expires_in,
        user={
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role,
            "training_level": user.training_level,
            "permissions": user.permissions
        },
        business={
            "business_id": business.business_id,
            "name": business.name,
            "industry": business.industry
        } if business else None
    )

@router.post('/auth/register', response_model=LoginResponse)
def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user and business"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == register_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # Create business first
    business = Business(
        business_id=f"biz_{secrets.token_hex(8)}",
        name=register_data.business_name,
        industry="agency"  # Default for runway MVP
    )
    db.add(business)
    db.flush()  # Get business_id without committing
    
    # Create user
    user = User(
        user_id=f"user_{secrets.token_hex(8)}",
        business_id=business.business_id,
        email=register_data.email,
        password_hash=hash_password(register_data.password),
        role=register_data.user_role,
        training_level="senior",  # Default
        permissions={"can_approve_bills": True},  # Default owner permissions
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(business)
    
    # Create access token
    token_data = {
        "sub": user.user_id,
        "business_id": user.business_id,
        "email": user.email,
        "role": user.role
    }
    
    access_token = create_access_token(token_data)
    
    return LoginResponse(
        access_token=access_token,
        expires_in=86400,
        user={
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role,
            "training_level": user.training_level,
            "permissions": user.permissions
        },
        business={
            "business_id": business.business_id,
            "name": business.name,
            "industry": business.industry
        }
    )

@router.post('/auth/logout')
def logout():
    """Logout user (client-side token removal)"""
    return {'message': 'Logged out successfully'}

@router.post('/auth/refresh', response_model=TokenRefreshResponse)
def refresh_token(refresh_data: TokenRefreshRequest):
    """Refresh JWT token"""
    payload = verify_token(refresh_data.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new access token with same payload
    new_token = create_access_token(payload)
    
    return TokenRefreshResponse(
        access_token=new_token,
        expires_in=86400
    )

@router.post('/auth/password-reset')
def request_password_reset(reset_data: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset (placeholder - would send email in production)"""
    db.query(User).filter(User.email == reset_data.email).first()
    
    # Always return success to prevent email enumeration
    return {"message": "If an account with this email exists, a password reset link has been sent"}

@router.post('/auth/password-reset/confirm')
def confirm_password_reset(reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Confirm password reset with token (placeholder implementation)"""
    # In production, verify the reset token and update password
    return {"message": "Password has been reset successfully"}
