"""Document upload endpoints."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Path as PathParam
from sqlalchemy.orm import Session
from typing import List

from app.models.schemas import DocumentUploadResponse, DocumentInfo, DocumentList, DeleteResponse
from app.services.document_service import DocumentService
from app.api.dependencies import get_db, get_doc_service
from app.utils.logger import app_logger as logger

router = APIRouter(prefix="/api/v1", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    doc_service: DocumentService = Depends(get_doc_service)
):
    """
    Upload a document (PDF, DOCX, TXT).
    
    The document will be processed, chunked, and indexed for retrieval.
    """
    logger.info(f"Received upload request: {file.filename}")
    
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md']
    file_extension = '.' + file.filename.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Upload and process document
        document = await doc_service.upload_document(
            file=file.file,
            filename=file.filename,
            db=db
        )
        
        return DocumentUploadResponse(
            doc_id=document.id,
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            status=document.status,
            message="Document uploaded and processed successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents", response_model=DocumentList)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    doc_service: DocumentService = Depends(get_doc_service)
):
    """
    List all uploaded documents.
    
    Supports pagination with skip and limit parameters.
    """
    return doc_service.list_documents(db=db, skip=skip, limit=limit)


@router.get("/documents/{doc_id}", response_model=DocumentInfo)
async def get_document(
    doc_id: str = PathParam(..., description="Document ID"),
    db: Session = Depends(get_db),
    doc_service: DocumentService = Depends(get_doc_service)
):
    """
    Get document details by ID.
    """
    document = doc_service.get_document(doc_id, db)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentInfo.model_validate(document)


@router.delete("/documents/{doc_id}", response_model=DeleteResponse)
async def delete_document(
    doc_id: str = PathParam(..., description="Document ID"),
    db: Session = Depends(get_db),
    doc_service: DocumentService = Depends(get_doc_service)
):
    """
    Delete a document and all associated data.
    
    This will remove the document, its chunks, and embeddings from the system.
    """
    success = doc_service.delete_document(doc_id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DeleteResponse(
        success=True,
        message=f"Document {doc_id} deleted successfully",
        deleted_count=1
    )
