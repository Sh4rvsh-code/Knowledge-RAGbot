#!/usr/bin/env python3
"""
Test improved RAG pipeline with reranker and grounded prompts.
Compares old vs new pipeline on same questions.
"""

import os
import sys

# API key loaded from environment
os.environ['LLM_PROVIDER'] = 'gemma'

print("\n" + "="*80)
print("🚀 TESTING IMPROVED RAG PIPELINE")
print("="*80 + "\n")

# Test questions about the resume
test_questions = [
    "What is Sharvesh's email?",
    "Where did Sharvesh do his internship?",
    "What projects has Sharvesh worked on?",
    "What programming languages does Sharvesh know?",
    "When did Sharvesh graduate?"
]

print("Test Questions:")
for i, q in enumerate(test_questions, 1):
    print(f"   {i}. {q}")
print()

# ============================================================================
# Test 1: OLD PIPELINE (without reranker)
# ============================================================================
print("="*80)
print("TEST 1: OLD PIPELINE (No Reranker)")
print("="*80 + "\n")

from app.services.improved_qa_service import ImprovedRAGPipeline

old_pipeline = ImprovedRAGPipeline(
    use_reranker=False,
    top_k_retrieval=20,
    top_k_final=4
)

old_results = []
for i, question in enumerate(test_questions, 1):
    print(f"\n{'─'*80}")
    print(f"Question {i}: {question}")
    print("─"*80)
    
    result = old_pipeline.answer_question(
        question,
        temperature=0.0,
        max_tokens=200,
        log_prompt=False  # Don't spam logs
    )
    
    if result['success']:
        print(f"\n📝 Answer: {result['answer']}")
        print(f"\n📊 Stats:")
        print(f"   Retrieved: {result['retrieval_count']} candidates")
        print(f"   Used: {result['final_count']} chunks")
        print(f"   Time: {result['processing_time']:.2f}s")
        print(f"\n📚 Sources:")
        for j, src in enumerate(result['sources'], 1):
            print(f"   {j}. {src['document']} (score: {src['score']:.3f})")
        
        old_results.append(result)
    else:
        print(f"\n❌ {result['answer']}")
        old_results.append(None)

# ============================================================================
# Test 2: NEW PIPELINE (with reranker)
# ============================================================================
print("\n\n" + "="*80)
print("TEST 2: NEW PIPELINE (With Cross-Encoder Reranker)")
print("="*80 + "\n")

new_pipeline = ImprovedRAGPipeline(
    use_reranker=True,
    top_k_retrieval=50,  # Get more candidates
    top_k_final=4  # Rerank to best 4
)

new_results = []
for i, question in enumerate(test_questions, 1):
    print(f"\n{'─'*80}")
    print(f"Question {i}: {question}")
    print("─"*80)
    
    result = new_pipeline.answer_question(
        question,
        temperature=0.0,
        max_tokens=200,
        log_prompt=False
    )
    
    if result['success']:
        print(f"\n📝 Answer: {result['answer']}")
        print(f"\n📊 Stats:")
        print(f"   Retrieved: {result['retrieval_count']} candidates")
        print(f"   Reranked to: {result['final_count']} chunks")
        timing = result['timing']
        print(f"   Time: {timing['total']:.2f}s (retrieval: {timing['retrieval']:.2f}s, rerank: {timing['rerank']:.2f}s, llm: {timing['llm']:.2f}s)")
        print(f"\n📚 Sources (after reranking):")
        for j, src in enumerate(result['sources'], 1):
            print(f"   {j}. {src['document']} (rerank score: {src['score']:.3f})")
        
        # Verify answer
        verification = new_pipeline.verify_answer(
            result['answer'],
            question,
            result['chunks']
        )
        print(f"\n✓ Verification: {verification['reason']}")
        
        new_results.append(result)
    else:
        print(f"\n❌ {result['answer']}")
        new_results.append(None)

# ============================================================================
# COMPARISON
# ============================================================================
print("\n\n" + "="*80)
print("📊 COMPARISON: OLD vs NEW PIPELINE")
print("="*80 + "\n")

print(f"{'Question':<40} {'Old Time':<12} {'New Time':<12} {'Improvement'}")
print("─" * 80)

for i, q in enumerate(test_questions):
    old = old_results[i]
    new = new_results[i]
    
    if old and new:
        old_time = old['processing_time']
        new_time = new['processing_time']
        diff = ((old_time - new_time) / old_time * 100) if old_time > 0 else 0
        
        q_short = q[:37] + "..." if len(q) > 40 else q
        print(f"{q_short:<40} {old_time:>6.2f}s     {new_time:>6.2f}s     {diff:+.1f}%")

print("\n" + "="*80)
print("✅ IMPROVEMENTS IMPLEMENTED:")
print("="*80 + "\n")

print("1. ✅ Cross-encoder reranker")
print("   - Retrieves top-50 with bi-encoder")
print("   - Reranks to best 4 with cross-encoder")
print("   - Higher precision in final chunks")
print()

print("2. ✅ Grounded prompts")
print("   - Strict instruction to only use context")
print("   - Clear source citations in prompt")
print("   - Forces 'I don't know' when info missing")
print()

print("3. ✅ Temperature=0 (deterministic)")
print("   - No sampling randomness")
print("   - Reproducible answers")
print()

print("4. ✅ Full prompt logging")
print("   - Can enable with log_prompt=True")
print("   - Shows exact prompt sent to LLM")
print()

print("5. ✅ Answer verification")
print("   - Checks if answer words in context")
print("   - Reports coverage percentage")
print()

print("="*80)
print("🎯 NEXT STEPS:")
print("="*80 + "\n")

print("1. Test in Streamlit UI:")
print("   - Open the app")
print("   - Ask questions about your documents")
print("   - Compare with/without reranker")
print()

print("2. Upload more documents:")
print("   - Add PDFs with rich content")
print("   - Test retrieval quality")
print()

print("3. Tune parameters:")
print("   - Adjust top_k_retrieval (20-100)")
print("   - Adjust top_k_final (3-6)")
print("   - Try different cross-encoder models")
print()

print("="*80 + "\n")
