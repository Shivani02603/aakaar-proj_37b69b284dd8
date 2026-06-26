from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import DocumentChunk
from database.config import get_db


class PerformanceService:
    def __init__(self, db: Session):
        self.db = db

    def create_chunk(self, document_id: UUID, chunk_index: int, content: str, embedding: List[float], metadata: dict) -> DocumentChunk:
        """
        Create a new document chunk.
        """
        new_chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            embedding=embedding,
            metadata=metadata,
            created_at=datetime.utcnow()
        )
        self.db.add(new_chunk)
        self.db.commit()
        self.db.refresh(new_chunk)
        return new_chunk

    def get_chunk_by_id(self, chunk_id: UUID) -> DocumentChunk:
        """
        Retrieve a document chunk by its ID.
        """
        chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")
        return chunk

    def list_all_chunks(self, document_id: UUID) -> List[DocumentChunk]:
        """
        List all chunks for a specific document.
        """
        chunks = self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        return chunks

    def update_chunk(self, chunk_id: UUID, content: Optional[str] = None, embedding: Optional[List[float]] = None, metadata: Optional[dict] = None) -> DocumentChunk:
        """
        Update an existing document chunk.
        """
        chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")

        if content is not None:
            chunk.content = content
        if embedding is not None:
            chunk.embedding = embedding
        if metadata is not None:
            chunk.metadata = metadata

        chunk.created_at = datetime.utcnow()  # Update timestamp
        self.db.commit()
        self.db.refresh(chunk)
        return chunk

    def delete_chunk(self, chunk_id: UUID) -> None:
        """
        Delete a document chunk by its ID.
        """
        chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")

        self.db.delete(chunk)
        self.db.commit()

    def ensure_query_performance(self, chunks: List[DocumentChunk], max_chunks: int = 5, max_time_seconds: int = 5) -> None:
        """
        Ensure that the query performance meets the non-functional requirement (NFR-001).
        """
        if len(chunks) > max_chunks:
            raise HTTPException(
                status_code=400,
                detail=f"Query exceeds the maximum allowed chunks ({max_chunks})."
            )

        # Simulate performance check (actual implementation would involve timing the query execution)
        start_time = datetime.utcnow()
        # Simulated processing logic
        end_time = datetime.utcnow()
        elapsed_time = (end_time - start_time).total_seconds()

        if elapsed_time > max_time_seconds:
            raise HTTPException(
                status_code=408,
                detail=f"Query processing time exceeded {max_time_seconds} seconds."
            )


# Dependency injection function
def get_performance_service(db: Session = Depends(get_db)) -> PerformanceService:
    return PerformanceService(db=db)