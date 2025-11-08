"""Document management service."""
from typing import List, Optional, BinaryIO
from pathlib import Path
import os
import shutil
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.database import Document, Chunk, get_db_manager
from app.models.schemas import DocumentInfo, DocumentList
from app.core.ingestion.extractors import ExtractorFactory
from app.core.ingestion.chunker import RecursiveChunker
from app.core.ingestion.embedder import get_embedder
from app.core.ingestion.indexer import get_index_manager
from app.config import settings
from app.utils.helpers import generate_doc_id, calculate_file_hash
from app.utils.logger import app_logger as logger


class DocumentService:
    """
    Service for managing document uploads, processing, and storage.
    """
    
    def __init__(self):
        """Initialize document service."""
        self.extractor_factory = ExtractorFactory()
        self.chunker = RecursiveChunker()
        self.embedder = get_embedder()
        self.index_manager = get_index_manager(dimension=self.embedder.get_dimension())
        self.db_manager = get_db_manager()
        
        logger.info("DocumentService initialized")
    
    async def upload_document(
        self,
        file: BinaryIO,
        filename: str,
        db: Session
    ) -> Document:
        """
        Upload and process a document.
        
        Args:
            file: File object
            filename: Original filename
            db: Database session
            
        Returns:
            Document object
        """
        logger.info(f"Starting upload for: {filename}")
        
        # Generate document ID
        doc_id = generate_doc_id(filename)
        
        # Save file temporarily
        file_extension = Path(filename).suffix
        temp_path = os.path.join(settings.upload_dir, f"{doc_id}{file_extension}")
        
        try:
            # Write file
            with open(temp_path, 'wb') as f:
                shutil.copyfileobj(file, f)
            
            file_size = os.path.getsize(temp_path)
            
            # Check file size
            if file_size > settings.max_upload_size_bytes:
                os.remove(temp_path)
                raise ValueError(
                    f"File too large: {file_size} bytes "
                    f"(max: {settings.max_upload_size_bytes})"
                )
            
            # Create document record
            document = Document(
                id=doc_id,
                filename=filename,
                file_type=file_extension.lstrip('.'),
                file_size=file_size,
                upload_date=datetime.utcnow(),
                status="processing"
            )
            
            db.add(document)
            db.commit()
            
            logger.info(f"Document record created: {doc_id}")
            
            # Process document asynchronously (or synchronously for now)
            try:
                self._process_document(doc_id, temp_path, db)
                
                # Update status
                document.status = "completed"
                db.commit()
                
                logger.info(f"Document processing completed: {doc_id}")
                
            except Exception as e:
                logger.error(f"Document processing failed: {e}")
                document.status = "failed"
                document.error_message = str(e)
                db.commit()
                raise
            
            return document
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
    
    def _process_document(self, doc_id: str, file_path: str, db: Session):
        """
        Process document: extract, chunk, embed, and index.
        
        Args:
            doc_id: Document ID
            file_path: Path to file
            db: Database session
        """
        logger.info(f"Processing document: {doc_id}")
        
        # 1. Extract text
        extraction_result = self.extractor_factory.extract(file_path)
        text = extraction_result.text
        metadata = extraction_result.metadata
        
        logger.info(f"Extracted {len(text)} characters")
        
        # 2. Chunk text
        chunks = self.chunker.chunk(
            text=text,
            doc_id=doc_id,
            metadata=metadata
        )
        
        logger.info(f"Created {len(chunks)} chunks")
        
        # 3. Generate embeddings
        chunk_texts = [chunk.chunk_text for chunk in chunks]
        embeddings = self.embedder.embed_chunks(chunk_texts, normalize=True)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # 4. Add to FAISS index
        metadata_list = []
        for chunk in chunks:
            metadata_list.append({
                "doc_id": chunk.doc_id,
                "chunk_index": chunk.chunk_index,
                "chunk_text": chunk.chunk_text,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                "metadata": chunk.metadata
            })
        
        faiss_ids = self.index_manager.add_vectors(embeddings, metadata_list)
        
        logger.info(f"Added {len(faiss_ids)} vectors to index")
        
        # 5. Save chunks to database
        for chunk, faiss_id in zip(chunks, faiss_ids):
            db_chunk = Chunk(
                doc_id=chunk.doc_id,
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.chunk_text,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                faiss_id=faiss_id,
                metadata=chunk.metadata
            )
            db.add(db_chunk)
        
        # Update document
        document = db.query(Document).filter(Document.id == doc_id).first()
        if document:
            document.total_chunks = len(chunks)
            document.metadata = metadata
        
        db.commit()
        
        # 6. Save index
        self.index_manager.save_index()
        
        logger.info(f"Document processing complete: {doc_id}")
    
    def get_document(self, doc_id: str, db: Session) -> Optional[Document]:
        """Get document by ID."""
        return db.query(Document).filter(Document.id == doc_id).first()
    
    def list_documents(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> DocumentList:
        """
        List all documents.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            DocumentList
        """
        total = db.query(Document).count()
        documents = db.query(Document).offset(skip).limit(limit).all()
        
        return DocumentList(
            documents=[DocumentInfo.model_validate(doc) for doc in documents],
            total=total
        )
    
    def delete_document(self, doc_id: str, db: Session) -> bool:
        """
        Delete document and associated chunks.
        
        Args:
            doc_id: Document ID
            db: Database session
            
        Returns:
            True if deleted successfully
        """
        logger.info(f"Deleting document: {doc_id}")
        
        # Get document
        document = db.query(Document).filter(Document.id == doc_id).first()
        
        if not document:
            return False
        
        # Delete from FAISS index
        self.index_manager.delete_by_doc_id(doc_id)
        self.index_manager.save_index()
        
        # Delete from database (cascades to chunks)
        db.delete(document)
        db.commit()
        
        # Delete file if exists
        file_path = os.path.join(
            settings.upload_dir,
            f"{doc_id}.{document.file_type}"
        )
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logger.info(f"Document deleted: {doc_id}")
        return True
    
    def reindex_documents(
        self,
        doc_ids: Optional[List[str]],
        db: Session
    ) -> int:
        """
        Reindex documents.
        
        Args:
            doc_ids: Optional list of document IDs (None = all)
            db: Database session
            
        Returns:
            Number of documents reindexed
        """
        logger.info("Starting reindexing...")
        
        # Get documents to reindex
        query = db.query(Document)
        if doc_ids:
            query = query.filter(Document.id.in_(doc_ids))
        
        documents = query.all()
        
        # Clear index if reindexing all
        if not doc_ids:
            self.index_manager.clear()
        
        # Reindex each document
        reindexed_count = 0
        for document in documents:
            try:
                file_path = os.path.join(
                    settings.upload_dir,
                    f"{document.id}.{document.file_type}"
                )
                
                if os.path.exists(file_path):
                    # Delete existing chunks
                    db.query(Chunk).filter(Chunk.doc_id == document.id).delete()
                    db.commit()
                    
                    # Reprocess
                    self._process_document(document.id, file_path, db)
                    reindexed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to reindex {document.id}: {e}")
        
        logger.info(f"Reindexed {reindexed_count} documents")
        return reindexed_count


# Global service instance
_document_service: Optional[DocumentService] = None


def get_document_service() -> DocumentService:
    """Get or create document service instance."""
    global _document_service
    
    if _document_service is None:
        _document_service = DocumentService()
    
    return _document_service
