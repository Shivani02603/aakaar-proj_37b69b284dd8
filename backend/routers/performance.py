from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import DocumentChunk
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(tags=["Performance"])

# Pydantic schemas
class DocumentChunkBase(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    created_at: datetime

class DocumentChunkResponse(DocumentChunkBase):
    embedding: Optional[List[float]] = None
    metadata: Optional[dict] = None

class PerformanceMetrics(BaseModel):
    query_time: float = Field(..., description="Time taken to generate the answer in seconds")
    chunk_count: int = Field(..., description="Number of chunks processed in the query")

# Endpoint to fetch performance metrics
@router.get("/metrics", response_model=PerformanceMetrics)
async def get_performance_metrics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Fetch performance metrics for the system.
    """
    try:
        # Simulate fetching metrics (replace with actual logic)
        query_time = 4.5  # Example: Query time in seconds
        chunk_count = db.query(DocumentChunk).count()  # Count all chunks in the database

        return PerformanceMetrics(query_time=query_time, chunk_count=chunk_count)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch performance metrics",
        )

# Endpoint to validate query performance
@router.post("/validate", response_model=PerformanceMetrics)
async def validate_query_performance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Validate query performance against the defined non-functional requirements.
    """
    try:
        # Simulate query performance validation (replace with actual logic)
        start_time = datetime.utcnow()
        
        # Example: Fetch up to 5 chunks (replace with actual query logic)
        chunks = db.query(DocumentChunk).limit(5).all()
        chunk_count = len(chunks)

        end_time = datetime.utcnow()
        query_time = (end_time - start_time).total_seconds()

        if query_time > 5.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Query performance validation failed. Time taken: {query_time} seconds",
            )

        return PerformanceMetrics(query_time=query_time, chunk_count=chunk_count)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate query performance",
        )