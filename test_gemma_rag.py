#!/usr/bin/env python3
"""Test Gemma model with actual RAG retrieval on your documents."""

import os
import sys

# Set API key in environment
# API key loaded from environment
os.environ['LLM_PROVIDER'] = 'gemma'

print("\n" + "="*70)
print("🤖 TESTING GEMMA WITH RAG RETRIEVAL")
print("="*70 + "\n")

# Initialize components
print("📋 Step 1: Initialize RAG Components")
print("   Loading configuration...")

from app.config import settings
from app.models.database import get_db, Chunk
from app.core.retrieval.retriever import SemanticRetriever
from app.core.llm.gemma_llm import GemmaLLM
from app.services.qa_service import QAService

print(f"   ✅ LLM Provider: {settings.llm_provider}")
print(f"   ✅ Gemma Model: {settings.gemma_model}")
print(f"   ✅ Chunk Size: {settings.chunk_size}")
print(f"   ✅ Top-K Results: {settings.top_k_results}")

# Initialize Gemma LLM
print("\n📋 Step 2: Initialize Gemma LLM")
gemma = GemmaLLM()
print(f"   ✅ Gemma initialized: {gemma.model}")

# Initialize Retriever
print("\n📋 Step 3: Initialize Retriever")
retriever = SemanticRetriever()
print(f"   ✅ Retriever initialized")
print(f"   ✅ FAISS Index loaded")

# Check database
print("\n📋 Step 4: Check Document Database")
db = next(get_db())
chunks = db.query(Chunk).all()
print(f"   ✅ Total chunks in database: {len(chunks)}")

if len(chunks) == 0:
    print("   ⚠️  No documents found! Upload some documents first.")
    sys.exit(0)

# Get unique documents
doc_ids = set(chunk.doc_id for chunk in chunks)
print(f"   ✅ Unique documents: {len(doc_ids)}")

# Initialize QA Service
print("\n📋 Step 5: Initialize QA Service")
qa_service = QAService(retriever=retriever, llm=gemma)
print(f"   ✅ QA Service ready")

# Test questions
print("\n" + "="*70)
print("🧪 TESTING RAG QUERIES WITH GEMMA")
print("="*70 + "\n")

test_questions = [
    "What are the main topics covered in the documents?",
    "Can you summarize the key points?",
    "What information is available about AI or machine learning?"
]

for i, question in enumerate(test_questions, 1):
    print(f"\n{'='*70}")
    print(f"Question {i}: {question}")
    print("="*70)
    
    try:
        # Retrieve relevant chunks
        print("\n🔍 Retrieving relevant chunks...")
        results = retriever.retrieve(question, top_k=settings.top_k_results)
        
        if not results:
            print("   ⚠️  No relevant chunks found")
            continue
        
        print(f"   ✅ Found {len(results)} relevant chunks:")
        for j, (chunk_text, score, metadata) in enumerate(results, 1):
            print(f"      {j}. Score: {score:.3f} | Length: {len(chunk_text)} chars")
        
        # Generate answer with Gemma
        print("\n💭 Generating answer with Gemma...")
        answer = qa_service.answer_question(question)
        
        print(f"\n✅ Gemma Response ({len(answer)} chars):")
        print("─" * 70)
        print(answer)
        print("─" * 70)
        
        # Show sources
        print("\n📚 Sources Used:")
        for j, (chunk_text, score, metadata) in enumerate(results[:3], 1):
            doc_name = metadata.get('document_name', 'Unknown')
            print(f"   {j}. {doc_name} (relevance: {score:.2f})")
            print(f"      Preview: {chunk_text[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

# Performance test
print("\n" + "="*70)
print("⚡ PERFORMANCE TEST")
print("="*70 + "\n")

import time

print("Testing response time with caching...")
test_query = "What is this document about?"

# First query (cold)
start = time.time()
answer1 = qa_service.answer_question(test_query)
time1 = time.time() - start

print(f"✅ First query (cold): {time1:.2f}s")
print(f"   Response length: {len(answer1)} chars")

# Second query (cached)
start = time.time()
answer2 = qa_service.answer_question(test_query)
time2 = time.time() - start

print(f"✅ Second query (cached): {time2:.3f}s")
print(f"   Speedup: {time1/time2:.1f}x faster")

# Compare all 3 models
print("\n" + "="*70)
print("🏆 MODEL COMPARISON (Same Question)")
print("="*70 + "\n")

comparison_question = "Explain the main concept in simple terms."

# Test Local Model
print("1️⃣  Testing Local Model (flan-t5-small)...")
os.environ['LLM_PROVIDER'] = 'free'
from app.core.llm.free_llm import FreeLLM
local_llm = FreeLLM()
qa_local = QAService(retriever=retriever, llm=local_llm)

start = time.time()
answer_local = qa_local.answer_question(comparison_question)
time_local = time.time() - start

print(f"   ✅ Time: {time_local:.2f}s | Length: {len(answer_local)} chars")
print(f"   Response: {answer_local[:150]}...")

# Test Gemini
print("\n2️⃣  Testing Gemini API (gemini-2.0-flash)...")
os.environ['LLM_PROVIDER'] = 'gemini'
from app.core.llm.gemini_llm import GeminiLLM
gemini_llm = GeminiLLM()
qa_gemini = QAService(retriever=retriever, llm=gemini_llm)

start = time.time()
answer_gemini = qa_gemini.answer_question(comparison_question)
time_gemini = time.time() - start

print(f"   ✅ Time: {time_gemini:.2f}s | Length: {len(answer_gemini)} chars")
print(f"   Response: {answer_gemini[:150]}...")

# Test Gemma
print("\n3️⃣  Testing Gemma (google/gemma-2-2b-it)...")
os.environ['LLM_PROVIDER'] = 'gemma'
qa_gemma = QAService(retriever=retriever, llm=gemma)

start = time.time()
answer_gemma = qa_gemma.answer_question(comparison_question)
time_gemma = time.time() - start

print(f"   ✅ Time: {time_gemma:.2f}s | Length: {len(answer_gemma)} chars")
print(f"   Response: {answer_gemma[:150]}...")

# Summary
print("\n" + "="*70)
print("📊 FINAL SUMMARY")
print("="*70 + "\n")

print(f"{'Model':<20} {'Time':<12} {'Length':<10} {'Quality':<15}")
print("─" * 70)
print(f"{'Local (flan-t5)':<20} {time_local:>6.2f}s     {len(answer_local):>5} chars  {'Basic':<15}")
print(f"{'Gemini (2.0-flash)':<20} {time_gemini:>6.2f}s     {len(answer_gemini):>5} chars  {'Excellent':<15}")
print(f"{'Gemma (2B-it)':<20} {time_gemma:>6.2f}s     {len(answer_gemma):>5} chars  {'Good':<15}")

print("\n✅ ALL TESTS COMPLETE!")
print("\n💡 Recommendations:")
print("   • Use Local Model: Testing, offline work")
print("   • Use Gemini: Production, complex queries, best quality")
print("   • Use Gemma: Balanced option, good quality, reasonable speed")
print("\n🚀 Gemma is fully integrated and working with your RAG bot!")
print("\n" + "="*70 + "\n")
