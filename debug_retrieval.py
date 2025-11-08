"""Debug script to troubleshoot RAG retrieval issues."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import Settings
from app.core.ingestion.embedder import get_embedder
from app.core.ingestion.indexer import get_index_manager
from app.core.retrieval.retriever import SemanticRetriever
from app.models.database import DatabaseManager, Document, Chunk

def debug_retrieval():
    """Debug the retrieval pipeline."""
    print("=" * 80)
    print("RAG RETRIEVAL DEBUG SCRIPT")
    print("=" * 80)
    
    # Initialize components
    print("\n1. Initializing components...")
    settings = Settings()
    embedder = get_embedder()
    index_manager = get_index_manager(dimension=embedder.get_dimension())
    db_manager = DatabaseManager()
    retriever = SemanticRetriever()
    
    print(f"✓ Embedder dimension: {embedder.get_dimension()}")
    print(f"✓ Index type: {index_manager.index_type}")
    print(f"✓ Index vectors: {index_manager.index.ntotal if index_manager.index else 0}")
    print(f"✓ Similarity threshold: {settings.similarity_threshold}")
    
    # Check database
    print("\n2. Checking database...")
    with db_manager.get_session() as session:
        doc_count = session.query(Document).count()
        chunk_count = session.query(Chunk).count()
        print(f"✓ Documents in DB: {doc_count}")
        print(f"✓ Chunks in DB: {chunk_count}")
        
        if doc_count > 0:
            docs = session.query(Document).all()
            print("\n   Documents:")
            for doc in docs:
                print(f"   - {doc.filename} (ID: {doc.id[:8]}...)")
        
        if chunk_count > 0:
            chunks = session.query(Chunk).limit(3).all()
            print("\n   Sample chunks:")
            for chunk in chunks:
                text_preview = chunk.chunk_text[:100].replace('\n', ' ')
                print(f"   - FAISS ID: {chunk.faiss_id}, Text: {text_preview}...")
    
    # Test query
    print("\n3. Testing query: 'What are the main topics in this document?'")
    query = "What are the main topics in this document?"
    
    # Generate query embedding
    print("\n   a) Generating query embedding...")
    query_embedding = embedder.embed_query(query, normalize=True)
    print(f"   ✓ Query embedding shape: {query_embedding.shape}")
    print(f"   ✓ Query embedding norm: {(query_embedding ** 2).sum() ** 0.5:.4f}")
    
    # Search FAISS with NO threshold
    print("\n   b) Searching FAISS index (top 10, NO threshold)...")
    if index_manager.index and index_manager.index.ntotal > 0:
        faiss_results = index_manager.search(query_embedding, top_k=10)
        print(f"   ✓ FAISS returned {len(faiss_results)} results")
        print("\n   FAISS Results:")
        for i, result in enumerate(faiss_results, 1):
            print(f"   {i}. Score: {result['score']:.4f}, FAISS ID: {result['faiss_id']}")
        
        # Check if scores meet threshold
        threshold = settings.similarity_threshold
        above_threshold = [r for r in faiss_results if r['score'] >= threshold]
        print(f"\n   Results above threshold ({threshold}): {len(above_threshold)}")
        
        if len(above_threshold) == 0:
            print(f"   ⚠️  WARNING: No results meet the threshold of {threshold}")
            print(f"   💡 Highest score: {faiss_results[0]['score']:.4f}")
            print(f"   💡 Recommended threshold: {max(faiss_results[0]['score'] * 0.8, 0.3):.2f}")
    else:
        print("   ✗ Index is empty!")
    
    # Test retriever with different thresholds
    print("\n4. Testing retriever with different thresholds...")
    for threshold in [0.0, 0.3, 0.5, 0.7]:
        results = retriever.search(query, top_k=5, min_score=threshold)
        print(f"   Threshold {threshold}: {len(results)} results")
        if results:
            for r in results[:2]:
                print(f"     - Score: {r['score']:.4f}, File: {r['filename']}")
    
    # Check embedder consistency
    print("\n5. Testing embedder consistency...")
    test_text = "This is a test sentence"
    emb1 = embedder.embed_text(test_text, normalize=True)
    emb2 = embedder.embed_text(test_text, normalize=True)
    similarity = (emb1 * emb2).sum()
    print(f"   Same text embedded twice, cosine similarity: {similarity:.6f}")
    if similarity < 0.99:
        print("   ⚠️  WARNING: Embeddings are not consistent!")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    
    if index_manager.index and index_manager.index.ntotal > 0:
        faiss_results = index_manager.search(query_embedding, top_k=1)
        if faiss_results:
            max_score = faiss_results[0]['score']
            if max_score < settings.similarity_threshold:
                recommended_threshold = max(max_score * 0.8, 0.3)
                print(f"✓ Lower the similarity threshold from {settings.similarity_threshold} to {recommended_threshold:.2f}")
                print(f"  Current threshold {settings.similarity_threshold} is too high!")
                print(f"  Max score found: {max_score:.4f}")
    else:
        print("✗ No vectors in index - upload documents first!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    debug_retrieval()
