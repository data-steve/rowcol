from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from domains.core.models.user import User
from domains.core.schemas.user import UserCreate, UserUpdate, User as UserSchema
from typing import List

router = APIRouter(prefix='/runway', tags=['users'])

@router.post('/users/', response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get('/users/{user_id}', response_model=UserSchema)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get('/businesses/{business_id}/users/', response_model=List[UserSchema])
def get_business_users(business_id: str, db: Session = Depends(get_db)):
    """Get all users for a business"""
    users = db.query(User).filter(User.business_id == business_id).all()
    return users

@router.put('/users/{user_id}', response_model=UserSchema)
def update_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user profile"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete('/users/{user_id}')
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete user (soft delete by setting inactive)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Soft delete - set user as inactive
    user.is_active = False
    db.commit()
    return {"message": "User deactivated successfully"}

@router.post('/users/{user_id}/permissions')
def update_user_permissions(
    user_id: str, 
    permissions: dict, 
    db: Session = Depends(get_db)
):
    """Update user permissions"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate permissions structure
    valid_permissions = {
        'can_approve_bills', 'can_manage_users', 'can_view_reports', 
        'can_modify_settings', 'can_export_data'
    }
    
    for perm in permissions.keys():
        if perm not in valid_permissions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid permission: {perm}"
            )
    
    user.permissions = permissions
    db.commit()
    return {"message": "Permissions updated successfully"}
