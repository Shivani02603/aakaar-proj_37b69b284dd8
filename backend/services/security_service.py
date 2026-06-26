import os
import jwt
import hashlib
import subprocess
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import User, Document
from database.config import get_db

class SecurityService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, token: str) -> User:
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid authentication token.")
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found.")
            return user
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired.")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid authentication token.")

    def scan_file_for_malware(self, file_path: str) -> bool:
        try:
            # Example: Using ClamAV for malware scanning
            result = subprocess.run(["clamscan", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return True  # No malware detected
            else:
                raise HTTPException(status_code=400, detail="Malware detected in the uploaded file.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error scanning file for malware: {str(e)}")

    def create_document(self, user_id: UUID, filename: str, file_path: str, file_size: int) -> Document:
        if not self.scan_file_for_malware(file_path):
            raise HTTPException(status_code=400, detail="Malware detected in the uploaded file.")
        
        new_document = Document(
            id=UUID(os.urandom(16).hex()),
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            status="uploaded",
            uploaded_at=datetime.utcnow(),
            processed_at=None
        )
        self.db.add(new_document)
        self.db.commit()
        self.db.refresh(new_document)
        return new_document

    def get_document_by_id(self, document_id: UUID) -> Document:
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")
        return document

    def list_all_documents(self, user_id: UUID) -> List[Document]:
        documents = self.db.query(Document).filter(Document.user_id == user_id).all()
        return documents

    def update_document_status(self, document_id: UUID, status: str) -> Document:
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")
        document.status = status
        document.processed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete_document(self, document_id: UUID) -> None:
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")
        self.db.delete(document)
        self.db.commit()