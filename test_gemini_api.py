#!/usr/bin/env python3
"""Test Gemini API connectivity and response quality."""

import os
from app.config import Settings
from app.core.llm.gemini_llm import GeminiLLM
from app.core.llm.free_llm import LocalLLM

def test_gemini():
    """Test Gemini API."""
    print("=" * 60)
    print("TESTING GEMINI API")
    print("=" * 60)
    
    settings = Settings()
    
    print(f"\n📋 Configuration:")
    print(f"   API Key: {settings.gemini_api_key[:20]}...{settings.gemini_api_key[-10:]}")
    print(f"   Model: {settings.gemini_model}")
    
    try:
        print(f"\n🔄 Initializing Gemini LLM...")
        gemini = GeminiLLM()
        print(f"   ✅ Initialized successfully")
        
        # Test simple query
        test_prompt = """Context: Python is a high-level programming language known for its simplicity and readability.

Question: What is Python known for?

Answer:"""
        
        print(f"\n🤔 Testing generation with simple query...")
        print(f"   Prompt: 'What is Python known for?'")
        
        response = gemini.generate(test_prompt, max_tokens=200, temperature=0.7)
        
        print(f"\n✅ Response received:")
        print(f"   Length: {len(response)} characters")
        print(f"   Content:\n{'-' * 60}")
        print(response)
        print('-' * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_local():
    """Test Local LLM."""
    print("\n" + "=" * 60)
    print("TESTING LOCAL LLM (for comparison)")
    print("=" * 60)
    
    try:
        print(f"\n🔄 Initializing Local LLM...")
        local = LocalLLM()
        print(f"   ✅ Initialized successfully")
        
        # Test simple query
        test_prompt = """Context: Python is a high-level programming language known for its simplicity and readability.

Question: What is Python known for?

Answer:"""
        
        print(f"\n🤔 Testing generation with simple query...")
        print(f"   Prompt: 'What is Python known for?'")
        
        response = local.generate(test_prompt, max_tokens=200, temperature=0.7)
        
        print(f"\n✅ Response received:")
        print(f"   Length: {len(response)} characters")
        print(f"   Content:\n{'-' * 60}")
        print(response)
        print('-' * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🧪 LLM Comparison Test\n")
    
    gemini_ok = test_gemini()
    local_ok = test_local()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Gemini API: {'✅ WORKING' if gemini_ok else '❌ FAILED'}")
    print(f"Local LLM:  {'✅ WORKING' if local_ok else '❌ FAILED'}")
    print("=" * 60)
