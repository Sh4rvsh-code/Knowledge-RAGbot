#!/usr/bin/env python3
"""
Rebuild FAISS index from database.
Use this when the FAISS index is out of sync with the database.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from app.config import Settings
from app.core.ingestion.embedder import get_embedder
from app.core.ingestion.indexer import get_index_manager
from app.models.database import DatabaseManager, Chunk
import numpy as np

def rebuild_faiss_index():
    """Rebuild FAISS index from all chunks in database."""
    
    print("=" * 80)
    print("REBUILDING FAISS INDEX FROM DATABASE")
    print("=" * 80)
    
    settings = Settings()
    embedder = get_embedder()
    db_manager = DatabaseManager(settings.database_url)
    
    print("\n1. Fetching all chunks from database...")
    with db_manager.get_session() as session:
        chunks = session.query(Chunk).all()
        print(f"   Found {len(chunks)} chunks")
        
        if not chunks:
            print("   No chunks found! Upload documents first.")
            return
        
        # Extract data
        chunk_texts = [chunk.chunk_text for chunk in chunks]
        chunk_ids = [chunk.id for chunk in chunks]
        
    print("\n2. Generating embeddings...")
    embeddings = embedder.embed_chunks(chunk_texts)
    print(f"   Generated {len(embeddings)} embeddings")
    
    print("\n3. Creating new FAISS index...")
    index_manager = get_index_manager(dimension=embedder.get_dimension())
    
    # Clear existing index
    index_manager.create_index()
    
    print("\n4. Adding vectors to FAISS...")
    with db_manager.get_session() as session:
        chunks = session.query(Chunk).all()
        
        metadata_list = []
        for chunk in chunks:
            metadata = {
                'doc_id': chunk.doc_id,
                'chunk_index': chunk.chunk_index,
                'chunk_text': chunk.chunk_text[:200],
                'start_char': chunk.start_char,
                'end_char': chunk.end_char
            }
            metadata_list.append(metadata)
        
        # Add to FAISS
        faiss_ids = index_manager.add_vectors(embeddings, metadata_list)
        print(f"   Added {len(faiss_ids)} vectors")
        
        # Update FAISS IDs in database
        print("\n5. Updating FAISS IDs in database...")
        for chunk, faiss_id in zip(chunks, faiss_ids):
            chunk.faiss_id = faiss_id
        
        session.commit()
        print(f"   Updated {len(chunks)} chunk records")
    
    print("\n6. Saving FAISS index to disk...")
    index_manager.save_index()
    print(f"   Index saved: {settings.index_dir}")
    
    print("\n" + "=" * 80)
    print(f"✅ FAISS INDEX REBUILT SUCCESSFULLY!")
    print(f"   Total vectors: {index_manager.index.ntotal}")
    print("=" * 80)

if __name__ == "__main__":
    rebuild_faiss_index()
