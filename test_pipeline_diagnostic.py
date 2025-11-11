#!/usr/bin/env python3
"""
Diagnostic script to trace the entire RAG pipeline.
Tests: Query -> Embedding -> Retrieval -> Context Building -> LLM -> Answer
"""

import os
import sys

# Set environment
# API key loaded from environment
os.environ['LLM_PROVIDER'] = 'gemma'

print("\n" + "="*80)
print("🔍 RAG PIPELINE DIAGNOSTIC TEST")
print("="*80 + "\n")

# Test questions (similar but different)
test_questions = [
    "What is AI?",
    "What is artificial intelligence?",
    "Explain AI",
    "What are the main topics?"
]

print("📋 Testing with similar questions to check cache behavior:\n")
for i, q in enumerate(test_questions, 1):
    print(f"   {i}. {q}")

print("\n" + "="*80)
print("STEP 1: INITIALIZE COMPONENTS")
print("="*80 + "\n")

from app.config import settings
from app.core.ingestion.embedder import get_embedder
from app.core.ingestion.indexer import get_index_manager
from app.core.retrieval.retriever import SemanticRetriever
from app.core.llm.remote_llm import get_llm
from app.core.llm.orchestrator import LLMOrchestrator
from app.core.cache import get_cache
from app.models.database import get_db, Chunk, Document

print("✅ Embedder initialized")
embedder = get_embedder()

print("✅ Index manager initialized")
index_manager = get_index_manager(dimension=embedder.get_dimension())

print("✅ Retriever initialized")
retriever = SemanticRetriever(top_k=5, similarity_threshold=0.15)

print("✅ LLM initialized")
llm = get_llm()
print(f"   Using: {type(llm).__name__}")

print("✅ Orchestrator initialized")
orchestrator = LLMOrchestrator(llm)

print("✅ Cache initialized")
cache = get_cache()
cache_stats = cache.get_stats()
print(f"   Cache size: {cache_stats['query_cache_size']} entries")
print(f"   TTL: {cache_stats['ttl']}s (10 minutes)")

# Check documents
db = next(get_db())
chunks = db.query(Chunk).all()
docs = db.query(Document).all()
print(f"\n✅ Database ready: {len(docs)} documents, {len(chunks)} chunks")

# Clear cache for clean test
print("\n🗑️ Clearing cache for clean test...")
cache.clear()

print("\n" + "="*80)
print("STEP 2: PROCESS EACH QUESTION")
print("="*80 + "\n")

import time

for i, question in enumerate(test_questions, 1):
    print(f"\n{'─'*80}")
    print(f"Question {i}: {question}")
    print("─"*80)
    
    # Check cache first
    cached = cache.get(question, "gemma")
    if cached:
        print(f"⚡ CACHE HIT - answer already stored")
        print(f"   Age: {int(time.time() - cached['timestamp'])}s")
        continue
    else:
        print(f"❌ CACHE MISS - will process full pipeline")
    
    # Step 2A: Generate query embedding
    print(f"\n2A. Generating query embedding...")
    start = time.time()
    query_embedding = embedder.embed_query(question, normalize=True)
    embed_time = time.time() - start
    print(f"   ✅ Embedding: shape={query_embedding.shape}, time={embed_time:.3f}s")
    
    # Step 2B: Search FAISS index
    print(f"\n2B. Searching FAISS index...")
    start = time.time()
    results = retriever.search(question, top_k=5, min_score=0.15)
    search_time = time.time() - start
    print(f"   ✅ Found {len(results)} results, time={search_time:.3f}s")
    
    if results:
        print(f"\n   Top 3 results:")
        for j, r in enumerate(results[:3], 1):
            print(f"      {j}. Score: {r['score']:.3f} | {r['filename']} | {r['chunk_text'][:60]}...")
    else:
        print(f"   ⚠️ No results found!")
        continue
    
    # Step 2C: Build context
    print(f"\n2C. Building context...")
    context = orchestrator._build_context(results)
    print(f"   ✅ Context: {len(context)} chars")
    print(f"   Preview: {context[:150]}...")
    
    # Step 2D: Generate answer with LLM
    print(f"\n2D. Generating answer with LLM...")
    start = time.time()
    answer = orchestrator.answer_question(question, results, max_tokens=200, temperature=0.7)
    llm_time = time.time() - start
    print(f"   ✅ Answer: {len(answer)} chars, time={llm_time:.3f}s")
    print(f"\n   Answer:")
    print(f"   {answer}")
    
    # Step 2E: Cache the answer
    print(f"\n2E. Caching answer...")
    cache.set(question, answer, results, "gemma")
    print(f"   ✅ Cached for future queries")
    
    total_time = embed_time + search_time + llm_time
    print(f"\n📊 Total time: {total_time:.3f}s (embed: {embed_time:.3f}s, search: {search_time:.3f}s, llm: {llm_time:.3f}s)")

print("\n" + "="*80)
print("STEP 3: TEST CACHE BEHAVIOR")
print("="*80 + "\n")

print("Testing if similar questions incorrectly share cache...\n")

# Test same question again
print("Test: Asking same question twice (should use cache)")
q1 = "What is AI?"
print(f"   Q1: {q1}")

start = time.time()
cached = cache.get(q1, "gemma")
if cached:
    print(f"   ✅ CACHE HIT (as expected) - {(time.time()-start)*1000:.1f}ms")
else:
    print(f"   ❌ CACHE MISS (unexpected!)")

# Test slightly different question
print(f"\nTest: Asking slightly different question (should NOT use same cache)")
q2 = "What is AI"  # No question mark
print(f"   Q2: {q2}")

start = time.time()
cached = cache.get(q2, "gemma")
if cached:
    print(f"   ⚠️ CACHE HIT - questions normalized to same hash")
    print(f"      This is OK if questions are truly equivalent")
else:
    print(f"   ✅ CACHE MISS (as expected) - different question")

# Test very different question
print(f"\nTest: Asking completely different question")
q3 = "What are the main topics?"
print(f"   Q3: {q3}")

start = time.time()
cached = cache.get(q3, "gemma")
if cached:
    print(f"   ⚠️ CACHE HIT - this might indicate improper caching!")
    print(f"      Q1: {q1}")
    print(f"      Q3: {q3}")
    print(f"      These should NOT share cache!")
else:
    print(f"   ✅ CACHE MISS (correct) - different question")

print("\n" + "="*80)
print("STEP 4: ANALYSIS")
print("="*80 + "\n")

final_stats = cache.get_stats()
print(f"📊 Final Cache Stats:")
print(f"   Entries: {final_stats['query_cache_size']}")
print(f"   TTL: {final_stats['ttl']}s (10 min)")
print(f"   Max size: {final_stats['max_size']}")

print(f"\n✅ DIAGNOSTIC COMPLETE")
print(f"\n💡 Key Points:")
print(f"   • Cache now validates document version (clears if docs change)")
print(f"   • TTL reduced from 1 hour to 10 minutes for freshness")
print(f"   • Query normalization removes extra spaces and punctuation")
print(f"   • Each LLM provider has separate cache")
print(f"   • Streamlit UI has 'Clear Cache' button and cache toggle")
print(f"\n🔧 If answers still seem stale:")
print(f"   1. Click 'Clear Cache' button in Streamlit sidebar")
print(f"   2. Uncheck 'Enable Response Cache' to force fresh retrieval")
print(f"   3. Check logs for 'CACHE HIT' vs 'CACHE MISS' messages")
print("\n" + "="*80 + "\n")
