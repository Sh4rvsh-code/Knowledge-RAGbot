"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.utils.logger import app_logger as logger
from app.models.database import get_db_manager
from app.core.ingestion.embedder import get_embedder
from app.core.ingestion.indexer import get_index_manager

# Import routers
from app.api.routes import health, upload, query, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 50)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 50)
    
    # Initialize database
    logger.info("Initializing database...")
    db_manager = get_db_manager()
    db_manager.create_tables()
    
    # Initialize embedder
    logger.info("Loading embedding model...")
    embedder = get_embedder()
    logger.info(f"Embedding dimension: {embedder.get_dimension()}")
    
    # Initialize/load FAISS index
    logger.info("Loading FAISS index...")
    index_manager = get_index_manager(dimension=embedder.get_dimension())
    if not index_manager.load_index():
        logger.info("No existing index found, creating new index...")
        index_manager.create_index(embedder.get_dimension())
        index_manager.save_index()
    
    stats = index_manager.get_stats()
    logger.info(f"Index loaded: {stats['total_vectors']} vectors")
    
    logger.info("=" * 50)
    logger.info("Application startup complete!")
    logger.info(f"API available at: http://{settings.api_host}:{settings.api_port}")
    logger.info(f"Docs available at: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info("=" * 50)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    db_manager.close()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Production-ready RAG (Retrieval-Augmented Generation) system for document Q&A.
    
    ## Features
    
    * **Document Upload**: Support for PDF, DOCX, and TXT files
    * **Semantic Search**: Advanced vector similarity search using FAISS
    * **Question Answering**: LLM-powered answers with source citations
    * **Source Tracking**: Precise character-level citations
    * **Admin Tools**: Reindexing, statistics, and data management
    
    ## Usage
    
    1. Upload documents via `/api/v1/upload`
    2. Ask questions via `/api/v1/query`
    3. Get answers with source citations
    """,
    lifespan=lifespan,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
