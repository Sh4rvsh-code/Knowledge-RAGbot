#!/usr/bin/env python3
"""
Test script to verify RAG bot initialization and basic functionality.
Run this to ensure everything is working before using the Streamlit app.
"""

import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        from app.config import Settings
        from app.core.ingestion.embedder import get_embedder
        from app.core.ingestion.indexer import get_index_manager
        from app.core.retrieval.retriever import SemanticRetriever
        from app.core.llm.orchestrator import LLMOrchestrator
        from app.core.llm.remote_llm import get_llm
        from app.models.database import DatabaseManager
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_initialization():
    """Test that all components can be initialized."""
    print("\nTesting component initialization...")
    
    try:
        from app.config import Settings
        from app.core.ingestion.embedder import get_embedder
        from app.core.ingestion.indexer import get_index_manager
        from app.core.retrieval.retriever import SemanticRetriever
        from app.core.llm.orchestrator import LLMOrchestrator
        from app.core.llm.remote_llm import get_llm
        from app.models.database import DatabaseManager
        
        # Load settings
        print("  - Loading settings...")
        settings = Settings()
        print(f"    LLM Provider: {settings.llm_provider}")
        
        # Create directories
        print("  - Creating directories...")
        os.makedirs(settings.upload_dir, exist_ok=True)
        os.makedirs(settings.data_dir, exist_ok=True)
        os.makedirs(settings.index_dir, exist_ok=True)
        
        # Initialize database
        print("  - Initializing database...")
        db_manager = DatabaseManager(settings.database_url)
        db_manager.create_tables()
        
        # Initialize embedder
        print("  - Initializing embedder...")
        embedder = get_embedder()
        
        # Initialize index manager
        print("  - Initializing FAISS index...")
        index_manager = get_index_manager(dimension=384)
        print(f"    Vectors in index: {index_manager.index.ntotal}")
        
        # Initialize retriever
        print("  - Initializing retriever...")
        retriever = SemanticRetriever(
            top_k=settings.top_k_results,
            similarity_threshold=settings.similarity_threshold
        )
        
        # Initialize LLM
        print("  - Initializing LLM...")
        llm = get_llm()
        print(f"    LLM Type: {type(llm).__name__}")
        
        # Initialize orchestrator
        print("  - Initializing orchestrator...")
        orchestrator = LLMOrchestrator(llm)
        
        print("✅ All components initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm():
    """Test that the LLM can generate responses."""
    print("\nTesting LLM generation...")
    
    try:
        from app.core.llm.remote_llm import get_llm
        
        llm = get_llm()
        print(f"  LLM Type: {type(llm).__name__}")
        
        # Test generation
        print("  - Generating test response...")
        response = llm.generate("What is 2+2? Answer in one word.", max_tokens=10)
        print(f"  Response: {response}")
        
        print("✅ LLM generation successful")
        return True
        
    except Exception as e:
        print(f"❌ LLM generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("RAG Bot Initialization Test")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Initialization", test_initialization),
        ("LLM Generation", test_llm),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("=" * 60)
    if all_passed:
        print("✅ All tests passed! Your RAG bot is ready to use.")
        print("\nTo start the app, run:")
        print("  streamlit run streamlit_app.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
