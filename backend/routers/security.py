from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import User, Document
from database.config import get_db
from backend.services.auth import get_current_user
import os
import shutil
import subprocess

router = APIRouter(tags=["Security"])

# Pydantic Schemas
class DocumentBase(BaseModel):
    filename: str
    file_size: int
    status: str

class DocumentResponse(DocumentBase):
    id: UUID
    user_id: UUID
    uploaded_at: str
    processed_at: Optional[str]

class DocumentCreate(BaseModel):
    filename: str
    file_size: int

class DocumentUpdate(BaseModel):
    status: str

# Helper function for malware scanning
def scan_file_for_malware(file_path: str) -> bool:
    try:
        # Example: Using ClamAV for malware scanning
        result = subprocess.run(["clamscan", file_path], capture_output=True, text=True)
        if "FOUND" in result.stdout:
            return False  # Malware detected
        return True  # No malware detected
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error scanning file for malware")

# Routes
@router.post("/documents/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Save file to temporary location
        temp_dir = "uploads/temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Scan file for malware
        if not scan_file_for_malware(file_path):
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Malware detected in uploaded file")

        # Move file to permanent storage
        permanent_dir = "uploads/permanent"
        os.makedirs(permanent_dir, exist_ok=True)
        permanent_path = os.path.join(permanent_dir, file.filename)
        shutil.move(file_path, permanent_path)

        # Create document record in database
        document = Document(
            user_id=current_user.id,
            filename=file.filename,
            file_path=permanent_path,
            file_size=os.path.getsize(permanent_path),
            status="uploaded",
            uploaded_at=datetime.utcnow(),
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error uploading document")

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = document_update.status
    db.commit()
    db.refresh(document)
    return document

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove file from storage
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete document record from database
    db.delete(document)
    db.commit()