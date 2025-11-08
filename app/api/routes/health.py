"""Health check and status endpoints."""
from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.orm import Session
import os

from app.models.schemas import HealthCheck, StatusResponse, SystemStats
from app.models.database import Document, Chunk, Query
from app.api.dependencies import get_db
from app.config import settings
from app.core.ingestion.indexer import get_index_manager
from app.utils.logger import app_logger as logger

router = APIRouter()

# Store start time
START_TIME = datetime.utcnow()


@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Returns basic system health status.
    """
    try:
        # Check database
        db.execute("SELECT 1")
        database_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_connected = False
    
    # Check index
    try:
        index_manager = get_index_manager()
        index_loaded = index_manager.index is not None
    except Exception as e:
        logger.error(f"Index health check failed: {e}")
        index_loaded = False
    
    return HealthCheck(
        status="healthy" if database_connected and index_loaded else "unhealthy",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        database_connected=database_connected,
        index_loaded=index_loaded
    )


@router.get("/api/v1/status", response_model=StatusResponse)
async def get_status(db: Session = Depends(get_db)):
    """
    Get detailed system status.
    
    Returns comprehensive statistics and health information.
    """
    # Calculate uptime
    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    
    # Get statistics
    total_documents = db.query(Document).count()
    total_chunks = db.query(Chunk).count()
    total_queries = db.query(Query).count()
    
    # Get index stats
    index_manager = get_index_manager()
    index_stats = index_manager.get_stats()
    
    # Get database size
    db_path = settings.database_url.replace("sqlite:///", "")
    database_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    
    # Build stats
    stats = SystemStats(
        total_documents=total_documents,
        total_chunks=total_chunks,
        total_queries=total_queries,
        index_size=index_stats.get("total_vectors", 0),
        database_size=database_size,
        embedding_model=settings.embedding_model,
        index_type=settings.faiss_index_type
    )
    
    # Get health
    try:
        db.execute("SELECT 1")
        database_connected = True
    except:
        database_connected = False
    
    health = HealthCheck(
        status="healthy" if database_connected else "unhealthy",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        database_connected=database_connected,
        index_loaded=index_manager.index is not None
    )
    
    return StatusResponse(
        status="operational",
        version=settings.app_version,
        uptime=uptime,
        stats=stats,
        health=health
    )
