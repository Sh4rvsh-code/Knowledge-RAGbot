#!/usr/bin/env python3
"""
Comprehensive RAG Pipeline Test
Tests document upload, retrieval, and answer generation
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from app.core.retrieval.retriever import SemanticRetriever
from app.core.llm.orchestrator import LLMOrchestrator
from app.core.llm.remote_llm import get_llm

def test_queries():
    """Test multiple queries to verify RAG is working."""
    
    print("\n" + "=" * 80)
    print("TESTING RAG BOT - MULTIPLE QUERIES")
    print("=" * 80)
    
    # Initialize components
    retriever = SemanticRetriever(top_k=3, similarity_threshold=0.0)  # Lower threshold
    llm = get_llm()
    orchestrator = LLMOrchestrator(llm)
    
    # Test queries
    test_cases = [
        {
            "query": "What is Python?",
            "description": "Basic definition question"
        },
        {
            "query": "Tell me about Python programming language features",
            "description": "Features question"
        },
        {
            "query": "What can Python be used for?",
            "description": "Use cases question"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        description = test_case["description"]
        
        print(f"\n{'─' * 80}")
        print(f"TEST {i}: {description}")
        print(f"{'─' * 80}")
        print(f"Query: {query}\n")
        
        # Retrieve
        results = retriever.search(query, top_k=3, min_score=0.0)
        
        if not results:
            print("❌ No chunks retrieved!")
            continue
            
        print(f"✓ Retrieved {len(results)} chunks:\n")
        
        for j, result in enumerate(results, 1):
            print(f"  [{j}] Score: {result['score']:.4f} | File: {result['filename']}")
            print(f"      Text: {result['chunk_text'][:100]}...")
            print()
        
        # Generate answer
        print("Generating answer...")
        answer = orchestrator.answer_question(query, results, max_tokens=150, temperature=0.7)
        
        print(f"\n📝 Answer:")
        print(f"   {answer}")
        print()
    
    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_queries()
