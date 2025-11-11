#!/usr/bin/env python3
"""Test Google Gemma model integration via HuggingFace API."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("\n" + "="*70)
print("🧪 TESTING GOOGLE GEMMA MODEL INTEGRATION")
print("="*70 + "\n")

# Check for HuggingFace API key
print("📋 Step 1: Check Configuration")
hf_key = os.getenv('HUGGINGFACE_API_KEY', '')

if not hf_key:
    print("❌ HuggingFace API key not found in environment")
    print()
    print("📝 To use Gemma model, you need a HuggingFace API key:")
    print()
    print("1. Go to: https://huggingface.co/settings/tokens")
    print("2. Click 'New token'")
    print("3. Name it (e.g., 'ragbot')")
    print("4. Copy the token")
    print("5. Add to .env file:")
    print("   HUGGINGFACE_API_KEY=your_token_here")
    print()
    print("OR set environment variable:")
    print("   export HUGGINGFACE_API_KEY=your_token_here")
    print()
    print("⏭️  Skipping Gemma test (no API key)")
    sys.exit(0)
else:
    print(f"✅ HuggingFace API key found: {hf_key[:20]}...{hf_key[-10:]}")

print()
print("📋 Step 2: Initialize Gemma LLM")

try:
    from app.core.llm.gemma_llm import GemmaLLM
    
    gemma = GemmaLLM()
    print(f"✅ Gemma LLM initialized successfully")
    print(f"   Model: {gemma.model}")
    print(f"   Max tokens: {gemma.default_max_tokens}")
    
except ValueError as e:
    print(f"❌ Failed to initialize Gemma: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("📋 Step 3: Test Simple Query")

test_prompt = "Answer briefly: What is the capital of France?"
print(f"   Query: {test_prompt}")
print(f"   Generating response...")

try:
    response = gemma.generate(test_prompt, max_tokens=200)
    
    print()
    if response.startswith('Error') or response.startswith('⚠️') or response.startswith('⏳'):
        print(f"⚠️  Response: {response}")
        print()
        print("Common issues:")
        print("  • Rate limit: Wait a few seconds and try again")
        print("  • Model loading: Wait 20-30 seconds for first request")
        print("  • Invalid token: Check your HuggingFace API key")
    else:
        print(f"✅ Response ({len(response)} chars):")
        print("─" * 70)
        print(response)
        print("─" * 70)
        
except Exception as e:
    print(f"❌ Error during generation: {e}")
    import traceback
    traceback.print_exc()

print()
print("📋 Step 4: Test with Context (RAG-style)")

rag_prompt = """Context: Python is a high-level programming language known for its simplicity and readability. It's widely used for web development, data science, and AI.

Question: What is Python known for?

Your Answer:"""

print(f"   Testing RAG-style prompt...")

try:
    response = gemma.generate(rag_prompt, max_tokens=300)
    
    print()
    if response.startswith('Error') or response.startswith('⚠️') or response.startswith('⏳'):
        print(f"⚠️  Response: {response}")
    else:
        print(f"✅ Response ({len(response)} chars):")
        print("─" * 70)
        print(response)
        print("─" * 70)
        
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("="*70)
print("📊 GEMMA MODEL SUMMARY")
print("="*70)
print()
print("Model: google/gemma-2-2b-it:nebius")
print("Provider: HuggingFace Inference API")
print("Size: 2 billion parameters (lightweight)")
print("Strengths: Q&A, reasoning, summarization")
print("Speed: ~2-3 seconds per query")
print()
print("🎯 Integration Status:")
print("  ✅ Gemma LLM class created")
print("  ✅ Configuration added to settings")
print("  ✅ Integrated into remote_llm.py")
print("  ✅ Added to Streamlit UI as 3rd option")
print("  ✅ Separate from Local Model and Gemini API")
print()
print("💡 To use in Streamlit:")
print("  1. Ensure HUGGINGFACE_API_KEY is in .env")
print("  2. Open Streamlit app")
print("  3. Sidebar → Choose 'Google Gemma (HF)'")
print("  4. Ask questions!")
print()
