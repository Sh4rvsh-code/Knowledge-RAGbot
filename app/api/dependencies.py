"""Shared dependencies for API routes."""
from typing import Generator
from sqlalchemy.orm import Session

from app.models.database import get_db_manager
from app.services.document_service import get_document_service
from app.services.qa_service import get_qa_service


def get_db() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection.
    
    Usage:
        @router.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db_manager = get_db_manager()
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


def get_doc_service():
    """Get document service instance."""
    return get_document_service()


def get_qa_svc():
    """Get QA service instance."""
    return get_qa_service()
