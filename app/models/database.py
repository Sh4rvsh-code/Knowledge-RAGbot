"""Database models using SQLAlchemy."""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker, Session, Mapped, mapped_column
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.utils.logger import app_logger as logger


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Document(Base):
    """Document model for storing uploaded file metadata."""
    
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="processing", nullable=False)  # processing, completed, failed
    total_chunks = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"


class Chunk(Base):
    """Chunk model for storing text chunks with embeddings."""
    
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    faiss_id = Column(Integer, nullable=True, index=True)
    embedding_id = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, doc_id={self.doc_id}, chunk_index={self.chunk_index})>"


class Query(Base):
    """Query model for storing user queries and responses."""
    
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query_text = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processing_time = Column(Float, nullable=True)
    retrieved_chunks = Column(JSON, nullable=True)  # Store chunk IDs and scores
    top_k = Column(Integer, default=5)
    llm_provider = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
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
