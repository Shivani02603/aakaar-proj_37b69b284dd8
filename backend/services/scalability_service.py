from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import User
from database.config import get_db


class ScalabilityService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, hashed_password: str) -> User:
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = User(email=email, hashed_password=hashed_password)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def get_user_by_id(self, user_id: UUID) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def list_all_users(self) -> List[User]:
        users = self.db.query(User).all()
        return users

    def update_user(self, user_id: UUID, email: Optional[str] = None, hashed_password: Optional[str] = None) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if email:
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user and existing_user.id != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")
            user.email = email

        if hashed_password:
            user.hashed_password = hashed_password

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: UUID) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        self.db.delete(user)
        self.db.commit()