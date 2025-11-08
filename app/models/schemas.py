"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# Document Schemas
class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    doc_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    message: str
    
    model_config = ConfigDict(from_attributes=True)


class DocumentInfo(BaseModel):
    """Document information."""
    id: str
    filename: str
    file_type: str
    file_size: int
    upload_date: datetime
    status: str
    total_chunks: int
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class DocumentList(BaseModel):
    """List of documents."""
    documents: List[DocumentInfo]
    total: int


# Query Schemas
class QueryRequest(BaseModel):
    """Request for question answering."""
    query: str = Field(..., min_length=1, max_length=1000, description="Question to ask")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    min_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum similarity score")
    include_sources: bool = Field(default=True, description="Include source citations")


class SourceInfo(BaseModel):
    """Source citation information."""
    document: str
    chunk_index: int
    chunk_text: str
    score: float
    start_char: int
    end_char: int
    page: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Response for question answering."""
    query: str
    answer: str
    sources: List[SourceInfo]
    processing_time: float
    retrieved_count: int
    llm_provider: Optional[str] = None


class QueryHistory(BaseModel):
    """Query history entry."""
    id: int
    query_text: str
    response: Optional[str]
    timestamp: datetime
    processing_time: Optional[float]
    top_k: int
    
    model_config = ConfigDict(from_attributes=True)


class QueryHistoryList(BaseModel):
    """List of query history."""
    queries: List[QueryHistory]
    total: int


# Chunk Schemas
class ChunkInfo(BaseModel):
    """Chunk information."""
    id: int
    doc_id: str
    chunk_index: int
    chunk_text: str
    start_char: int
    end_char: int
    faiss_id: Optional[int]
    metadata: Optional[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True)


# Admin Schemas
class ReindexRequest(BaseModel):
    """Request to reindex documents."""
    doc_ids: Optional[List[str]] = Field(default=None, description="Specific documents to reindex (None = all)")


class ReindexResponse(BaseModel):
    """Response after reindexing."""
    success: bool
    message: str
    reindexed_count: int
    total_chunks: int


class SystemStats(BaseModel):
    """System statistics."""
    total_documents: int
    total_chunks: int
    total_queries: int
    index_size: int
    database_size: int
    embedding_model: str
    index_type: str


class DeleteResponse(BaseModel):
    """Response after deletion."""
    success: bool
    message: str
    deleted_count: int


# Health Check Schemas
class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    database_connected: bool
    index_loaded: bool


class StatusResponse(BaseModel):
    """Detailed status response."""
    status: str
    version: str
    uptime: float
    stats: SystemStats
    health: HealthCheck


# Error Schema
class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Models package initialization
class ModelInfo(BaseModel):
    """Model information."""
    name: str
    type: str
    dimension: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
