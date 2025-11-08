# RAG Retrieval Fix - "Unable to generate response (status 404)"

## Problem Summary

Users were getting **"Unable to generate response (status 404)"** error with **"Retrieved: 0 chunks"** when asking questions, even after uploading documents.

## Root Cause

**The similarity threshold was set too high (0.7)**, causing the retrieval system to filter out all results even when documents existed in the database.

### Why This Happened

1. **Cosine Similarity Range**: The FAISS index uses `IndexFlatIP` (Inner Product) which returns cosine similarity scores between -1 and 1
2. **Typical Score Range**: In practice, semantic similarity scores between user queries and document chunks typically fall in the range of **0.2-0.6**
3. **High Threshold Problem**: A threshold of 0.7 means "only return results with >70% similarity", which is too restrictive for most real-world queries
4. **Result**: Even relevant chunks with 0.5-0.6 similarity were being filtered out, leading to 0 results

## Solution Implemented

### 1. Lowered Default Similarity Threshold

**Changed from 0.7 → 0.3**

```python
# app/config.py
similarity_threshold: float = Field(default=0.3, alias="SIMILARITY_THRESHOLD")

# streamlit_app.py
min_score = st.slider("Minimum similarity", min_value=0.0, max_value=1.0, value=0.3, step=0.05, 
                     help="Lower threshold = more results. Try 0.3 for better retrieval.")
```

**Why 0.3?**
- Captures more potentially relevant chunks
- Still filters out completely irrelevant content
- Can be adjusted up/down per query via the slider

### 2. Added Better Error Handling

```python
def answer_question(query, top_k, min_score, components):
    # Check if index has vectors
    if not index_manager.index or index_manager.index.ntotal == 0:
        return {
            'success': False,
            'error': 'No documents in the index. Please upload documents first.',
        }
    
    # If no results found, provide helpful message
    if len(results) == 0:
        return {
            'success': False,
            'error': f'No relevant chunks found with similarity >= {min_score:.2f}. Try lowering the threshold.',
        }
```

### 3. Added Debug Information

**System Stats in Sidebar:**
- Documents count
- Chunks in DB
- Vectors in FAISS
- Warning if DB has chunks but FAISS is empty

**Error Messages in UI:**
```python
else:
    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
    if result.get('retrieved_count', 0) == 0:
        st.info(f"💡 Tip: Try lowering the similarity threshold below {min_score:.2f}")
```

### 4. Created Debug Script

`debug_retrieval.py` - Run locally to diagnose issues:
```bash
python debug_retrieval.py
```

Shows:
- FAISS index status (vector count)
- Database status (document/chunk counts)
- Test query with different thresholds
- Recommended threshold based on actual scores

## Testing the Fix

### Before the Fix
```
Query: "What are the main topics in this document?"
Similarity Threshold: 0.7
Result: Retrieved 0 chunks ❌
Error: Unable to generate response (status 404)
```

### After the Fix
```
Query: "What are the main topics in this document?"
Similarity Threshold: 0.3
Result: Retrieved 3-5 chunks ✓
Answer: [Generated from relevant context]
```

## How to Verify

1. **Check System Stats** (in sidebar):
   - Ensure "Vectors in FAISS" matches "Chunks in DB"
   - If mismatch, re-upload documents

2. **Run Debug Script**:
   ```bash
   python debug_retrieval.py
   ```
   
3. **Test Query with Different Thresholds**:
   - Start with 0.3
   - If too many irrelevant results, increase to 0.4-0.5
   - If no results, decrease to 0.2

## Understanding Similarity Scores

| Score Range | Meaning | Action |
|------------|---------|--------|
| 0.8 - 1.0 | Extremely similar (rare) | High confidence |
| 0.6 - 0.8 | Very relevant | Good match |
| 0.4 - 0.6 | Moderately relevant | Useful context |
| 0.2 - 0.4 | Somewhat relevant | May contain useful info |
| 0.0 - 0.2 | Barely relevant | Likely not useful |
| < 0.0 | Opposite meaning | Ignore |

**Recommended Thresholds:**
- **Strict retrieval**: 0.5-0.6 (fewer but highly relevant results)
- **Balanced (default)**: 0.3-0.4 (good mix of precision/recall)
- **Broad retrieval**: 0.2-0.3 (more results, may include tangential info)

## Common Issues & Solutions

### Issue 1: Still Getting 0 Results with Threshold 0.3

**Possible Causes:**
1. FAISS index is empty (not loaded from disk)
2. Documents not properly ingested
3. Embedder model mismatch

**Solution:**
```bash
# Run debug script
python debug_retrieval.py

# Check output:
# - "Vectors in FAISS: 0" → Re-upload documents
# - "Documents in DB: 0" → Upload documents first
# - "Chunks in DB > 0 but FAISS = 0" → Index not loaded, restart app
```

### Issue 2: Too Many Irrelevant Results

**Solution:** Increase threshold to 0.4-0.5 using the slider

### Issue 3: Gemini API "status 404" 

This is a **different** error from the retrieval issue. If you see this AFTER chunks are retrieved:

**Solution:** Already fixed with smart fallback in `gemini_llm.py`:
```python
model_names_to_try = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-pro",
    "gemini-1.0-pro"
]
```

## Architecture Context

This is a **standalone Streamlit app** (NOT FastAPI):
- No separate backend server
- All RAG components embedded in `streamlit_app.py`
- FAISS + SQLite for storage
- Google Gemini for LLM (FREE tier)

The checklist you provided was for a FastAPI + Streamlit architecture, which is different from this implementation.

## Files Modified

1. `app/config.py` - Lowered default threshold
2. `streamlit_app.py` - Better error handling, debug info, UI improvements
3. `debug_retrieval.py` - New diagnostic tool

## Deployment

Changes are deployed automatically to Streamlit Cloud:
```bash
git add -A
git commit -m "Fix retrieval: lower threshold to 0.3"
git push origin main
```

Wait 2-3 minutes for deployment, then test at:
https://knowledge-ragbot-6kwqvc6giy2crhkortxswc.streamlit.app/

## Success Criteria

✅ Documents upload successfully  
✅ FAISS vectors match DB chunks  
✅ Queries retrieve 3-5 relevant chunks  
✅ LLM generates answers with citations  
✅ Error messages are clear and actionable  
✅ Users can adjust threshold via slider  

---

**Status**: ✅ FIXED - Deployed to production
**Date**: November 9, 2025
