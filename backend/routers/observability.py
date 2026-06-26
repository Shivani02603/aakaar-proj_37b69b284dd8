from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from database.models import User, Document, ChatSession, ChatMessage
from database.config import get_db
from fastapi.security import OAuth2PasswordBearer

# OAuth2 dependency for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Initialize logger
logger = logging.getLogger("observability")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Pydantic schemas
class LogEntry(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    operation: str
    status: str
    timestamp: datetime
    details: Optional[dict]

class LogCreate(BaseModel):
    user_id: Optional[UUID]
    operation: str
    status: str
    details: Optional[dict]

class LogUpdate(BaseModel):
    status: Optional[str]
    details: Optional[dict]

# APIRouter setup
router = APIRouter(tags=["Observability"])

# Dependency to get current user from JWT token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.id == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return user

# Endpoint to log structured JSON data
@router.post("/logs", response_model=LogEntry, status_code=status.HTTP_201_CREATED)
async def create_log_entry(log: LogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log_entry = {
        "id": UUID(),
        "user_id": current_user.id if current_user else None,
        "operation": log.operation,
        "status": log.status,
        "timestamp": datetime.utcnow(),
        "details": log.details
    }
    logger.info(log_entry)
    return log_entry

# Endpoint to retrieve all logs
@router.get("/logs", response_model=List[LogEntry])
async def list_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Simulated log retrieval (replace with actual DB query if logs are stored persistently)
    logs = [
        {
            "id": UUID(),
            "user_id": current_user.id,
            "operation": "upload",
            "status": "success",
            "timestamp": datetime.utcnow(),
            "details": {"filename": "example.txt"}
        }
    ]
    return logs

# Endpoint to retrieve a specific log by ID
@router.get("/logs/{log_id}", response_model=LogEntry)
async def get_log_entry(log_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Simulated log retrieval (replace with actual DB query if logs are stored persistently)
    log_entry = {
        "id": log_id,
        "user_id": current_user.id,
        "operation": "upload",
        "status": "success",
        "timestamp": datetime.utcnow(),
        "details": {"filename": "example.txt"}
    }
    return log_entry

# Endpoint to update a log entry
@router.put("/logs/{log_id}", response_model=LogEntry)
async def update_log_entry(log_id: UUID, log_update: LogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Simulated log update (replace with actual DB query if logs are stored persistently)
    updated_log_entry = {
        "id": log_id,
        "user_id": current_user.id,
        "operation": "upload",
        "status": log_update.status or "success",
        "timestamp": datetime.utcnow(),
        "details": log_update.details or {"filename": "example.txt"}
    }
    logger.info(updated_log_entry)
    return updated_log_entry

# Endpoint to delete a log entry
@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log_entry(log_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Simulated log deletion (replace with actual DB query if logs are stored persistently)
    logger.info({"id": log_id, "operation": "delete", "status": "success", "timestamp": datetime.utcnow()})
    return