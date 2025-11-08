"""
RAG Document Q&A System - Usage Examples
========================================

This file contains example API calls and Python code snippets for using the system.
"""

# ============================================================================
# 1. UPLOAD A DOCUMENT
# ============================================================================

# Using curl:
"""
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
"""

# Using Python requests:
"""
import requests

with open("document.pdf", "rb") as f:
    files = {"file": ("document.pdf", f, "application/pdf")}
    response = requests.post("http://localhost:8000/api/v1/upload", files=files)
    print(response.json())
"""

# ============================================================================
# 2. ASK A QUESTION
# ============================================================================

# Using curl:
"""
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main findings?",
    "top_k": 5,
    "min_score": 0.7,
    "include_sources": true
  }'
"""

# Using Python requests:
"""
import requests

query_data = {
    "query": "What are the main findings?",
    "top_k": 5,
    "min_score": 0.7,
    "include_sources": True
}

response = requests.post("http://localhost:8000/api/v1/query", json=query_data)
result = response.json()

print(f"Answer: {result['answer']}")
print(f"\\nSources:")
for i, source in enumerate(result['sources'], 1):
    print(f"  {i}. {source['document']} (score: {source['score']:.3f})")
    print(f"     {source['chunk_text'][:100]}...")
"""

# ============================================================================
# 3. LIST DOCUMENTS
# ============================================================================

# Using curl:
"""
curl -X GET "http://localhost:8000/api/v1/documents"
"""

# Using Python:
"""
import requests

response = requests.get("http://localhost:8000/api/v1/documents")
documents = response.json()

for doc in documents['documents']:
    print(f"{doc['filename']} - {doc['status']} - {doc['total_chunks']} chunks")
"""

# ============================================================================
# 4. DELETE A DOCUMENT
# ============================================================================

# Using curl:
"""
curl -X DELETE "http://localhost:8000/api/v1/documents/{doc_id}"
"""

# Using Python:
"""
import requests

doc_id = "your-document-id-here"
response = requests.delete(f"http://localhost:8000/api/v1/documents/{doc_id}")
print(response.json())
"""

# ============================================================================
# 5. GET SYSTEM STATISTICS
# ============================================================================

# Using curl:
"""
curl -X GET "http://localhost:8000/api/v1/admin/stats"
"""

# Using Python:
"""
import requests

response = requests.get("http://localhost:8000/api/v1/admin/stats")
stats = response.json()

print(f"Total Documents: {stats['total_documents']}")
print(f"Total Chunks: {stats['total_chunks']}")
print(f"Total Queries: {stats['total_queries']}")
print(f"Embedding Model: {stats['embedding_model']}")
"""

# ============================================================================
# 6. REINDEX DOCUMENTS
# ============================================================================

# Reindex all documents:
"""
curl -X POST "http://localhost:8000/api/v1/admin/reindex" \
  -H "Content-Type: application/json" \
  -d '{}'
"""

# Reindex specific documents:
"""
curl -X POST "http://localhost:8000/api/v1/admin/reindex" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_ids": ["doc-id-1", "doc-id-2"]
  }'
"""

# ============================================================================
# 7. COMPLETE WORKFLOW EXAMPLE
# ============================================================================

"""
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Upload a document
print("Uploading document...")
with open("research_paper.pdf", "rb") as f:
    files = {"file": ("research_paper.pdf", f, "application/pdf")}
    response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
    doc_info = response.json()
    print(f"Document uploaded: {doc_info['doc_id']}")

# Wait for processing
time.sleep(2)

# 2. Ask questions
questions = [
    "What is the main hypothesis?",
    "What methodology was used?",
    "What are the key findings?",
    "What are the limitations?"
]

for question in questions:
    print(f"\\nQ: {question}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/query",
        json={
            "query": question,
            "top_k": 3,
            "include_sources": True
        }
    )
    
    result = response.json()
    print(f"A: {result['answer']}")
    print(f"   (Retrieved {result['retrieved_count']} sources in {result['processing_time']:.2f}s)")

# 3. Get statistics
response = requests.get(f"{BASE_URL}/api/v1/admin/stats")
stats = response.json()
print(f"\\nSystem Stats:")
print(f"  Documents: {stats['total_documents']}")
print(f"  Chunks: {stats['total_chunks']}")
print(f"  Queries: {stats['total_queries']}")
"""

# ============================================================================
# 8. BATCH PROCESSING EXAMPLE
# ============================================================================

"""
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"

# Upload multiple documents
documents_dir = Path("documents/")
uploaded_docs = []

for pdf_file in documents_dir.glob("*.pdf"):
    print(f"Uploading {pdf_file.name}...")
    
    with open(pdf_file, "rb") as f:
        files = {"file": (pdf_file.name, f, "application/pdf")}
        response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
        
        if response.status_code == 200:
            doc_info = response.json()
            uploaded_docs.append(doc_info['doc_id'])
            print(f"  ✓ Uploaded: {doc_info['doc_id']}")
        else:
            print(f"  ✗ Failed: {response.text}")

print(f"\\nTotal uploaded: {len(uploaded_docs)} documents")
"""

# ============================================================================
# 9. ERROR HANDLING EXAMPLE
# ============================================================================

"""
import requests

def ask_question(query, max_retries=3):
    '''Ask a question with retry logic.'''
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/query",
                json={"query": query, "top_k": 5},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.json().get('detail', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return None

# Use the function
result = ask_question("What is machine learning?")
if result:
    print(result['answer'])
else:
    print("Failed to get answer after retries")
"""
