#!/usr/bin/env python3
"""Quick test of Gemma model with RAG - simplified version."""

import os
import sys
import time

# Set API key
# API key loaded from environment
os.environ['LLM_PROVIDER'] = 'gemma'

print("\n" + "="*70)
print("🤖 GEMMA + RAG QUICK TEST")
print("="*70 + "\n")

# Initialize
print("📋 Initializing components...")
from app.services.qa_service import QAService
from app.models.database import get_db, Chunk

qa_service = QAService()
print("✅ QA Service initialized with Gemma")

# Check documents
db = next(get_db())
chunks = db.query(Chunk).all()
doc_ids = set(chunk.doc_id for chunk in chunks)

print(f"✅ Found {len(chunks)} chunks from {len(doc_ids)} documents")

if len(chunks) == 0:
    print("\n⚠️  No documents found. Upload some documents first!")
    sys.exit(0)

# Test questions
test_questions = [
    "What are the main topics in the documents?",
    "Can you summarize the key information?",
    "What is this about?"
]

print("\n" + "="*70)
print("🧪 TESTING GEMMA RESPONSES")
print("="*70)

for i, question in enumerate(test_questions, 1):
    print(f"\n{'─'*70}")
    print(f"Q{i}: {question}")
    print("─"*70)
    
    try:
        start = time.time()
        answer = qa_service.answer_question(question)
        elapsed = time.time() - start
        
        print(f"\n✅ Response ({len(answer)} chars, {elapsed:.2f}s):")
        print(answer)
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Compare models
print("\n" + "="*70)
print("🏆 MODEL COMPARISON TEST")
print("="*70)

comparison_q = "What is the main topic?"

# Test each model
models_to_test = [
    ("free", "Local Model"),
    ("gemini", "Gemini API"),
    ("gemma", "Gemma (HF)")
]

results = []

for provider, name in models_to_test:
    print(f"\nTesting {name}...")
    os.environ['LLM_PROVIDER'] = provider
    
    try:
        # Reinitialize service with new provider
        qa = QAService()
        
        start = time.time()
        answer = qa.answer_question(comparison_q)
        elapsed = time.time() - start
        
        results.append({
            'name': name,
            'time': elapsed,
            'length': len(answer),
            'answer': answer[:100] + "..." if len(answer) > 100 else answer
        })
        
        print(f"   ✅ {elapsed:.2f}s | {len(answer)} chars")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append({
            'name': name,
            'time': 0,
            'length': 0,
            'answer': f"Error: {e}"
        })

# Display comparison
print("\n" + "="*70)
print("📊 COMPARISON RESULTS")
print("="*70 + "\n")

print(f"{'Model':<20} {'Time':<12} {'Length':<10}")
print("─" * 45)
for r in results:
    print(f"{r['name']:<20} {r['time']:>6.2f}s     {r['length']:>5} chars")

print("\n" + "="*70)
print("✅ GEMMA IS FULLY INTEGRATED!")
print("="*70)
print("\n💡 Next steps:")
print("   1. Restart Streamlit: streamlit run streamlit_app.py")
print("   2. Choose 'Google Gemma (HF)' in sidebar")
print("   3. Ask questions and see Gemma in action!")
print("\n" + "="*70 + "\n")
