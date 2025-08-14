from sqlalchemy.orm import Session
from models.user import User as UserModel
from schemas.user import User
from typing import List

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: User) -> UserModel:
        """Create a new user."""
        db_user = UserModel(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user(self, user_id: int) -> UserModel:
        """Get a user by ID."""
        user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        return user

    def list_users(self) -> List[UserModel]:
        """List all users."""
        users = self.db.query(UserModel).all()
        return users
