#!/usr/bin/env python3
"""
System Verification Script

Run this script to verify that all components are working correctly.
"""

import sys
import os

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_imports():
    """Test that all required packages can be imported."""
    print_header("Testing Package Imports")
    
    packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("sqlalchemy", "SQLAlchemy"),
        ("sentence_transformers", "Sentence Transformers"),
        ("faiss", "FAISS"),
        ("fitz", "PyMuPDF"),
        ("docx", "python-docx"),
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
    ]
    
    failed = []
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name:25} ... OK")
        except ImportError as e:
            print(f"❌ {name:25} ... FAILED")
            failed.append(name)
    
    if failed:
        print(f"\n⚠️  Failed to import: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All packages imported successfully!")
    return True

def test_configuration():
    """Test configuration loading."""
    print_header("Testing Configuration")
    
    try:
        from app.config import settings
        
        print(f"✅ App Name: {settings.app_name}")
        print(f"✅ Version: {settings.app_version}")
        print(f"✅ LLM Provider: {settings.llm_provider}")
        print(f"✅ Embedding Model: {settings.embedding_model}")
        print(f"✅ Chunk Size: {settings.chunk_size}")
        print(f"✅ Database URL: {settings.database_url}")
        
        # Check API key
        if settings.llm_provider == "remote":
            if settings.openai_api_key:
                print(f"✅ OpenAI API Key: {'*' * 20}{settings.openai_api_key[-4:]}")
            elif settings.anthropic_api_key:
                print(f"✅ Anthropic API Key: {'*' * 20}{settings.anthropic_api_key[-4:]}")
            else:
                print("⚠️  No LLM API key found. Set in .env file.")
        
        print("\n✅ Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database():
    """Test database connection."""
    print_header("Testing Database")
    
    try:
        from app.models.database import get_db_manager, Document
        
        db_manager = get_db_manager()
        db = db_manager.get_session()
        
        # Try a simple query
        count = db.query(Document).count()
        print(f"✅ Database connected")
        print(f"✅ Documents in database: {count}")
        
        db.close()
        print("\n✅ Database working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_embedder():
    """Test embedding generation."""
    print_header("Testing Embeddings")
    
    try:
        from app.core.ingestion.embedder import get_embedder
        
        embedder = get_embedder()
        print(f"✅ Embedder loaded")
        print(f"✅ Model: {embedder.model_name}")
        print(f"✅ Dimension: {embedder.get_dimension()}")
        
        # Test embedding
        test_text = "This is a test sentence."
        embedding = embedder.embed_text(test_text)
        print(f"✅ Generated embedding shape: {embedding.shape}")
        
        print("\n✅ Embeddings working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Embedder error: {e}")
        print("Note: First run will download the model (~90MB)")
        return False

def test_faiss_index():
    """Test FAISS index."""
    print_header("Testing FAISS Index")
    
    try:
        from app.core.ingestion.indexer import get_index_manager
        from app.core.ingestion.embedder import get_embedder
        
        embedder = get_embedder()
        index_manager = get_index_manager(dimension=embedder.get_dimension())
        
        stats = index_manager.get_stats()
        print(f"✅ Index Manager loaded")
        print(f"✅ Index type: {stats['index_type']}")
        print(f"✅ Total vectors: {stats['total_vectors']}")
        print(f"✅ Dimension: {stats['dimension']}")
        
        print("\n✅ FAISS index working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ FAISS error: {e}")
        return False

def test_text_extraction():
    """Test text extraction."""
    print_header("Testing Text Extraction")
    
    try:
        from app.core.ingestion.extractors import ExtractorFactory
        
        factory = ExtractorFactory()
        print(f"✅ Extractor factory created")
        print(f"✅ Available extractors: PDF, DOCX, TXT")
        
        print("\n✅ Text extraction working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return False

def test_chunker():
    """Test text chunking."""
    print_header("Testing Text Chunking")
    
    try:
        from app.core.ingestion.chunker import RecursiveChunker
        
        chunker = RecursiveChunker(chunk_size=100, chunk_overlap=20)
        
        test_text = "This is a test. " * 50
        chunks = chunker.chunk(test_text, "test-doc")
        
        print(f"✅ Chunker created")
        print(f"✅ Test text length: {len(test_text)}")
        print(f"✅ Number of chunks: {len(chunks)}")
        print(f"✅ Chunk size: {chunker.chunk_size}")
        print(f"✅ Overlap: {chunker.chunk_overlap}")
        
        print("\n✅ Chunking working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Chunker error: {e}")
        return False

def test_retriever():
    """Test retrieval system."""
    print_header("Testing Retrieval System")
    
    try:
        from app.core.retrieval.retriever import get_retriever
        
        retriever = get_retriever()
        print(f"✅ Retriever created")
        print(f"✅ Top-k: {retriever.top_k}")
        print(f"✅ Similarity threshold: {retriever.similarity_threshold}")
        
        print("\n✅ Retrieval system working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Retriever error: {e}")
        return False

def test_services():
    """Test service layer."""
    print_header("Testing Services")
    
    try:
        from app.services.document_service import get_document_service
        from app.services.qa_service import get_qa_service
        
        doc_service = get_document_service()
        print(f"✅ Document service created")
        
        qa_service = get_qa_service()
        print(f"✅ QA service created")
        
        print("\n✅ Services working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Service error: {e}")
        return False

def test_directory_structure():
    """Test directory structure."""
    print_header("Testing Directory Structure")
    
    required_dirs = [
        "data",
        "data/uploads",
        "data/faiss_index",
        "logs"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path:25} ... EXISTS")
        else:
            print(f"❌ {dir_path:25} ... MISSING")
            all_exist = False
    
    if not all_exist:
        print("\nCreating missing directories...")
        for dir_path in required_dirs:
            os.makedirs(dir_path, exist_ok=True)
        print("✅ Directories created!")
    
    print("\n✅ Directory structure OK!")
    return True

def main():
    """Run all verification tests."""
    print("\n" + "█"*60)
    print("  RAG DOCUMENT Q&A SYSTEM - VERIFICATION")
    print("█"*60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_configuration),
        ("Directory Structure", test_directory_structure),
        ("Database", test_database),
        ("Text Extraction", test_text_extraction),
        ("Text Chunking", test_chunker),
        ("Embeddings", test_embedder),
        ("FAISS Index", test_faiss_index),
        ("Retrieval System", test_retriever),
        ("Services", test_services),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("  VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} | {name}")
    
    print("="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All systems operational! Ready to use.")
        print("\nNext steps:")
        print("  1. Configure your API key in .env")
        print("  2. Run: ./run.sh")
        print("  3. Visit: http://localhost:8000/docs")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Run: pip install -r requirements.txt")
        print("  - Check .env configuration")
        print("  - Ensure all directories exist")
        return 1

if __name__ == "__main__":
    sys.exit(main())
