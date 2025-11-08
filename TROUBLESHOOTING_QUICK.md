# Quick Troubleshooting Guide - RAG Bot

## Error: "Unable to generate response (status 404)" with "Retrieved: 0 chunks"

### ✅ SOLUTION: Lower the similarity threshold

**In the UI:**
1. Open sidebar
2. Find "Minimum similarity" slider
3. **Set to 0.3** (or lower if still no results)
4. Try your query again

**Why it works:** The default threshold of 0.7 was too strict. Most relevant chunks score between 0.3-0.6.

---

## Check System Health

**Sidebar → System Stats**

Look for these indicators:

✅ **Healthy:**
```
Documents: 3
Chunks in DB: 150
Vectors in FAISS: 150
```

❌ **Problem:**
```
Documents: 3
Chunks in DB: 150
Vectors in FAISS: 0  ← Missing vectors!
```

**Fix:** Re-upload documents or restart the app.

---

## Understanding Similarity Scores

| Threshold | What You Get |
|-----------|-------------|
| 0.3 | **RECOMMENDED** - Good balance, 3-5 relevant results |
| 0.5 | Stricter - Only very similar chunks |
| 0.7 | Too strict - Usually 0 results |
| 0.2 | Very broad - May include tangential info |

---

## Quick Diagnostic (Local Development)

```bash
# Run this to see what's happening
python debug_retrieval.py
```

It will show:
- How many vectors are in FAISS
- How many chunks are in the database
- What similarity scores your query gets
- Recommended threshold

---

## Common Scenarios

### Scenario 1: Just deployed, no documents yet
**What you see:** "No documents uploaded yet!"  
**Solution:** Upload documents in the "Upload Documents" tab

### Scenario 2: Documents uploaded, still 0 results
**What you see:** "No relevant chunks found with similarity >= 0.70"  
**Solution:** Lower the threshold to 0.3

### Scenario 3: FAISS vectors = 0, but DB has chunks
**What you see:** Warning in sidebar  
**Solution:** FAISS index didn't load. Re-upload documents or restart app.

### Scenario 4: Getting results, but they're irrelevant
**Solution:** Increase threshold to 0.4-0.5

---

## Architecture Notes

This is a **standalone Streamlit app**, NOT a FastAPI + Streamlit setup:
- ✅ All components run in one process
- ✅ FAISS + SQLite for local storage
- ✅ Google Gemini API (FREE tier)
- ❌ No separate backend server
- ❌ No uvicorn or FastAPI

The debugging checklist you shared was for a different architecture (FastAPI backend + Streamlit frontend), which is **not what this app uses**.

---

## Still Having Issues?

1. Check the sidebar System Stats
2. Run `python debug_retrieval.py` locally
3. Try threshold 0.2 (very permissive)
4. Verify documents uploaded successfully
5. Check Streamlit Cloud logs for errors

---

**Last Updated:** November 9, 2025  
**Status:** Fixed and deployed ✅
