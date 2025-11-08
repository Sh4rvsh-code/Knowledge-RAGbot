"""Database models using SQLAlchemy."""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, String, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker, Session, Mapped, mapped_column
from sqlalchemy.pool import StaticPool
import json

from app.config import settings
from app.utils.logger import app_logger as logger


class Base(DeclarativeBase):
    """Base class for all database models."""
    type_annotation_map = {
        Dict[str, Any]: Text
    }


class Document(Base):
    """Document model for storing uploaded file metadata."""
    
    __tablename__ = "documents"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String, default="processing", nullable=False)
    total_chunks: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    chunks: Mapped[list["Chunk"]] = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"


class Chunk(Base):
    """Chunk model for storing text chunks with embeddings."""
    
    __tablename__ = "chunks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    doc_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)
    faiss_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    embedding_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, doc_id={self.doc_id}, chunk_index={self.chunk_index})>"


class Query(Base):
    """Query model for storing user queries and responses."""
    
    __tablename__ = "queries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processing_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    retrieved_chunks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    top_k: Mapped[int] = mapped_column(Integer, default=5)
    llm_provider: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Query(id={self.id}, query_text={self.query_text[:50]}...)>"


# Database engine and session
class DatabaseManager:
    """Manage database connections and sessions."""
    
    def __init__(self, database_url: str = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url or settings.database_url
        
        # Configure engine based on database type
        if self.database_url.startswith("sqlite"):
            # SQLite-specific configuration
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=settings.debug
            )
        else:
            self.engine = create_engine(
                self.database_url,
                echo=settings.debug
            )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Database initialized: {self.database_url}")
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")
    
    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Database tables dropped")
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def close(self):
        """Close database connections."""
        self.engine.dispose()
        logger.info("Database connections closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get or create global database manager instance."""
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.create_tables()
    
    return _db_manager


def get_db() -> Session:
    """
    Get database session for dependency injection.
    
    Usage in FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db_manager = get_db_manager()
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()
