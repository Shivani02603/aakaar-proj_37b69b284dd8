import json
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import User, Document, ChatSession, ChatMessage
from database.config import get_db

# Configure logging for structured JSON logs
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("observability_service")

class ObservabilityService:
    def __init__(self, db: Session):
        self.db = db

    def log_operation(self, operation: str, entity: str, entity_id: Optional[UUID] = None, details: Optional[dict] = None):
        """
        Logs structured JSON for critical operations.
        """
        log_entry = {
            "operation": operation,
            "entity": entity,
            "entity_id": str(entity_id) if entity_id else None,
            "details": details,
        }
        logger.info(json.dumps(log_entry))

    def create_log(self, operation: str, entity: str, entity_id: Optional[UUID] = None, details: Optional[dict] = None):
        """
        Create a log entry for an operation.
        """
        self.log_operation(operation, entity, entity_id, details)

    def get_log_by_id(self, log_id: UUID) -> dict:
        """
        Retrieve a log entry by its ID.
        """
        # Simulated retrieval logic (actual implementation would depend on log storage)
        raise HTTPException(status_code=404, detail="Log entry not found")

    def list_all_logs(self) -> List[dict]:
        """
        List all log entries.
        """
        # Simulated retrieval logic (actual implementation would depend on log storage)
        return []

    def update_log(self, log_id: UUID, updated_details: dict):
        """
        Update a log entry.
        """
        # Simulated update logic (actual implementation would depend on log storage)
        raise HTTPException(status_code=404, detail="Log entry not found")

    def delete_log(self, log_id: UUID):
        """
        Delete a log entry.
        """
        # Simulated delete logic (actual implementation would depend on log storage)
        raise HTTPException(status_code=404, detail="Log entry not found")

    def log_upload_operation(self, document: Document):
        """
        Logs an upload operation for a document.
        """
        details = {
            "filename": document.filename,
            "file_size": document.file_size,
            "status": document.status,
        }
        self.log_operation("upload", "Document", document.id, details)

    def log_embedding_operation(self, document: Document, embedding_details: dict):
        """
        Logs an embedding operation for a document.
        """
        details = {
            "filename": document.filename,
            "embedding_details": embedding_details,
        }
        self.log_operation("embedding", "Document", document.id, details)

    def log_query_operation(self, chat_session: ChatSession, query_details: dict):
        """
        Logs a query operation for a chat session.
        """
        details = {
            "session_title": chat_session.title,
            "query_details": query_details,
        }
        self.log_operation("query", "ChatSession", chat_session.id, details)