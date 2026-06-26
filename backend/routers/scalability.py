from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from database.models import User, Document
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(tags=["Scalability"])

# Pydantic schemas
class ScalabilityBase(BaseModel):
    user_id: UUID
    concurrent_users: int = Field(..., ge=1, le=50, description="Number of concurrent users supported")

class ScalabilityCreate(ScalabilityBase):
    pass

class ScalabilityUpdate(BaseModel):
    concurrent_users: Optional[int] = Field(None, ge=1, le=50, description="Updated number of concurrent users supported")

class ScalabilityResponse(ScalabilityBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

# Mock database table for scalability settings
class ScalabilitySetting:
    def __init__(self, id: UUID, user_id: UUID, concurrent_users: int, created_at: datetime, updated_at: datetime):
        self.id = id
        self.user_id = user_id
        self.concurrent_users = concurrent_users
        self.created_at = created_at
        self.updated_at = updated_at

# In-memory storage for scalability settings (mock implementation)
scalability_settings = []

# Routes
@router.get("/", response_model=List[ScalabilityResponse])
def list_scalability_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    List all scalability settings.
    """
    return scalability_settings

@router.get("/{setting_id}", response_model=ScalabilityResponse)
def get_scalability_setting(setting_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a specific scalability setting by ID.
    """
    for setting in scalability_settings:
        if setting.id == setting_id:
            return setting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scalability setting not found")

@router.post("/", response_model=ScalabilityResponse, status_code=status.HTTP_201_CREATED)
def create_scalability_setting(setting: ScalabilityCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new scalability setting.
    """
    new_setting = ScalabilitySetting(
        id=UUID(),
        user_id=current_user.id,
        concurrent_users=setting.concurrent_users,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    scalability_settings.append(new_setting)
    return new_setting

@router.put("/{setting_id}", response_model=ScalabilityResponse)
def update_scalability_setting(setting_id: UUID, update_data: ScalabilityUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update an existing scalability setting.
    """
    for setting in scalability_settings:
        if setting.id == setting_id:
            if update_data.concurrent_users is not None:
                setting.concurrent_users = update_data.concurrent_users
            setting.updated_at = datetime.utcnow()
            return setting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scalability setting not found")

@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scalability_setting(setting_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a scalability setting.
    """
    global scalability_settings
    scalability_settings = [setting for setting in scalability_settings if setting.id != setting_id]
    return None