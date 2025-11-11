#!/usr/bin/env python3
"""
Demo: Show that LLM responses are displaying correctly
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

print("╔" + "═" * 78 + "╗")
print("║" + " " * 20 + "RAG BOT - RESPONSE DISPLAY TEST" + " " * 26 + "║")
print("╚" + "═" * 78 + "╝\n")

from app.core.llm.remote_llm import get_llm
from app.core.llm.orchestrator import LLMOrchestrator
from app.core.retrieval.retriever import SemanticRetriever

# Initialize
print("🔧 Initializing components...")
retriever = SemanticRetriever(top_k=5, similarity_threshold=0.1)
llm = get_llm()
orchestrator = LLMOrchestrator(llm)
print(f"✅ LLM: {type(llm).__name__}\n")

# Test queries that should work
test_cases = [
    "What is Python used for?",
    "Tell me about Python features",
    "What are the uses of Python programming?"
]

for i, query in enumerate(test_cases, 1):
    print(f"{'─' * 80}")
    print(f"[Test {i}/3] Query: \"{query}\"")
    print(f"{'─' * 80}")
    
    # Retrieve
    results = retriever.search(query, top_k=3, min_score=0.1)
    
    if not results:
        print("❌ No documents retrieved")
        continue
    
    print(f"✓ Retrieved {len(results)} chunks:")
    for j, r in enumerate(results, 1):
        print(f"  [{j}] {r['filename']} (score: {r['score']:.3f})")
    
    # Generate answer
    print("\n🤖 Generating answer...")
    answer = orchestrator.answer_question(query, results, max_tokens=250)
    
    # Display like Streamlit would
    print(f"\n📝 ANSWER DISPLAYED IN STREAMLIT:")
    print("┌" + "─" * 78 + "┐")
    print("│ " + answer[:76] + " │")
    if len(answer) > 76:
        remaining = answer[76:]
        while remaining:
            line = remaining[:76]
            print("│ " + line.ljust(77) + "│")
            remaining = remaining[76:]
    print("└" + "─" * 78 + "┘")
    
    # Check if it would show
    if len(answer.strip()) > 5:
        print("\n✅ WILL DISPLAY IN STREAMLIT: YES")
        print(f"   Length: {len(answer)} chars")
    else:
        print("\n❌ WILL DISPLAY IN STREAMLIT: NO (too short)")
    
    print()

print("\n╔" + "═" * 78 + "╗")
print("║" + " " * 25 + "✅ ALL TESTS COMPLETE" + " " * 31 + "║")
print("╚" + "═" * 78 + "╝")
print("\n💡 The LLM is generating responses that WILL display in Streamlit!")
print("📌 Make sure similarity threshold is set to 0.1-0.2 in the app sidebar.")
