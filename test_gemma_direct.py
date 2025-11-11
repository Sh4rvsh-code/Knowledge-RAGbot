#!/usr/bin/env python3
"""Direct test of Gemma API to verify it's working."""

import os
import requests
import json

API_KEY = os.getenv("HUGGINGFACE_API_KEY", "your_key_here")
MODEL = "google/gemma-2-2b-it:nebius"
URL = "https://router.huggingface.co/v1/chat/completions"

print("\n" + "="*70)
print("🧪 DIRECT GEMMA API TEST")
print("="*70 + "\n")

print(f"📋 Configuration:")
print(f"   API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
print(f"   Model: {MODEL}")
print(f"   Endpoint: {URL}")

# Test 1: Simple question
print("\n" + "─"*70)
print("Test 1: Simple Question")
print("─"*70)

test_prompt = "Answer in one sentence: What is Python?"

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant that answers questions concisely."},
        {"role": "user", "content": test_prompt}
    ],
    "max_tokens": 200,
    "temperature": 0.7
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print(f"\n📤 Sending request...")
try:
    response = requests.post(URL, json=payload, headers=headers, timeout=30)
    
    print(f"📥 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        answer = data['choices'][0]['message']['content'].strip()
        
        print(f"✅ Response ({len(answer)} chars):")
        print("─"*70)
        print(answer)
        print("─"*70)
        
    else:
        print(f"❌ Error Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 2: RAG-style question
print("\n" + "─"*70)
print("Test 2: RAG-Style Question")
print("─"*70)

rag_prompt = """Based on the following context, answer the question:

Context: Python is a high-level programming language known for its clear syntax and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.

Question: What programming paradigms does Python support?

Answer:"""

payload2 = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant. Answer based on the provided context."},
        {"role": "user", "content": rag_prompt}
    ],
    "max_tokens": 300,
    "temperature": 0.7
}

print(f"\n📤 Sending request...")
try:
    response = requests.post(URL, json=payload2, headers=headers, timeout=30)
    
    print(f"📥 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        answer = data['choices'][0]['message']['content'].strip()
        
        print(f"✅ Response ({len(answer)} chars):")
        print("─"*70)
        print(answer)
        print("─"*70)
        
    else:
        print(f"❌ Error Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70)
print("✅ GEMMA API DIRECT TEST COMPLETE")
print("="*70)
print("\n💡 If both tests passed, Gemma is fully working!")
print("   Open Streamlit and select 'Google Gemma (HF)' to use it.\n")
