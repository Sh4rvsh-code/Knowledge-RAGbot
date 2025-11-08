"""Admin endpoints for system management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import (
    ReindexRequest,
    ReindexResponse,
    DeleteResponse,
    SystemStats
)
from app.models.database import Document, Chunk, Query
from app.services.document_service import DocumentService
from app.api.dependencies import get_db, get_doc_service
from app.core.ingestion.indexer import get_index_manager
from app.config import settings
from app.utils.logger import app_logger as logger
import os

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/reindex", response_model=ReindexResponse)
async def reindex_documents(
    request: ReindexRequest,
    db: Session = Depends(get_db),
    doc_service: DocumentService = Depends(get_doc_service)
):
    """
    Rebuild the FAISS index from documents.
    
    Use this if the index becomes corrupted or needs to be rebuilt.
    Optionally specify document IDs to reindex only specific documents.
    """
    logger.info(f"Reindex request: {request.doc_ids}")
    
    try:
        reindexed_count = doc_service.reindex_documents(request.doc_ids, db)
        
        # Get total chunks
        if request.doc_ids:
            total_chunks = db.query(Chunk).filter(
                Chunk.doc_id.in_(request.doc_ids)
            ).count()
        else:
            total_chunks = db.query(Chunk).count()
        
        return ReindexResponse(
            success=True,
            message=f"Successfully reindexed {reindexed_count} documents",
            reindexed_count=reindexed_count,
            total_chunks=total_chunks
        )
        
    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Reindex failed: {str(e)}"
        )


@router.delete("/clear-all", response_model=DeleteResponse)
async def clear_all_data(
    confirm: bool = False,
    db: Session = Depends(get_db)
):
    """
    Clear all data from the system.
    
    **WARNING**: This will delete ALL documents, chunks, queries, and the index.
    This action cannot be undone!
    
    Set confirm=true to proceed.
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must set confirm=true to clear all data"
        )
    
    logger.warning("Clearing all data...")
    
    try:
        # Get counts before deletion
        doc_count = db.query(Document).count()
        chunk_count = db.query(Chunk).count()
        query_count = db.query(Query).count()
        
        # Delete from database
        db.query(Query).delete()
        db.query(Chunk).delete()
        db.query(Document).delete()
        db.commit()
        
        # Clear FAISS index
        index_manager = get_index_manager()
        index_manager.clear()
        index_manager.save_index()
        
        # Delete uploaded files
        upload_dir = settings.upload_dir
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path) and filename != ".gitkeep":
                    os.remove(file_path)
        
        total_deleted = doc_count + chunk_count + query_count
        
        logger.warning(f"Cleared all data: {doc_count} docs, {chunk_count} chunks, {query_count} queries")
        
        return DeleteResponse(
            success=True,
            message=f"Cleared all data successfully",
            deleted_count=total_deleted
        )
        
    except Exception as e:
        logger.error(f"Clear all failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear data: {str(e)}"
        )


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(db: Session = Depends(get_db)):
    """
    Get comprehensive system statistics.
    """
    # Get database counts
    total_documents = db.query(Document).count()
    total_chunks = db.query(Chunk).count()
    total_queries = db.query(Query).count()
    
    # Get index stats
    index_manager = get_index_manager()
    index_stats = index_manager.get_stats()
    
    # Get database size
    db_path = settings.database_url.replace("sqlite:///", "")
    database_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    
    return SystemStats(
        total_documents=total_documents,
        total_chunks=total_chunks,
        total_queries=total_queries,
        index_size=index_stats.get("total_vectors", 0),
        database_size=database_size,
        embedding_model=settings.embedding_model,
        index_type=settings.faiss_index_type
    )
