from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field
from database.models import User
from database.config import get_db

router = APIRouter(tags=["Sessions"])

class SessionCreate(BaseModel):
    title: str = "New Chat"

class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime

class MessageCreate(BaseModel):
    role: str
    content: str

class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

class ChatSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

async def get_current_user(token: str, db: Session = Depends(get_db)):
    # Implementation similar to auth.py
    pass

@router.get("/")
async def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()
    return sessions

@router.post("/", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_session = ChatSession(user_id=current_user.id, title=session_data.title)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.delete("/{session_id}")
async def delete_session(session_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"detail": "Session deleted successfully"}

@router.get("/{session_id}/messages")
async def list_messages(session_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return messages

@router.post("/{session_id}/messages", response_model=MessageResponse)
async def create_message(session_id: UUID, message_data: MessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    new_message = ChatMessage(session_id=session_id, role=message_data.role, content=message_data.content)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message