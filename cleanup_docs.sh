#!/bin/bash
# Clean up unnecessary markdown documentation files
# Keep only the essential documentation

echo "🧹 Cleaning up unnecessary documentation files..."

# Files to KEEP (essential documentation)
KEEP_FILES=(
    "README.md"
    "API_REFERENCE.md"
    "ARCHITECTURE.md"
    "PROJECT_SUMMARY.md"
    "SETUP_GUIDE.md"
    "PIPELINE_DETAILED_REPORT.md"
    "RERANKER_INTEGRATION_COMPLETE.md"
    "PIPELINE_BEFORE_AFTER.md"
)

# Files to DELETE (redundant, outdated, or interim documentation)
DELETE_FILES=(
    "ADVANCED_IMPROVEMENTS.md"
    "ALL_FIXED.md"
    "CACHE_PIPELINE_FIXES.md"
    "CHECKLIST.md"
    "DEPLOYMENT_CHECKLIST.md"
    "DEPLOYMENT_COMPLETE.md"
    "DEPLOYMENT_FIXES_SUMMARY.md"
    "DEPLOYMENT_OPTIONS.md"
    "DEPLOYMENT_READY.md"
    "FINAL_DEPLOYMENT_FIX.md"
    "FIXES_APPLIED.md"
    "FREE_LLM_SETUP.md"
    "GEMINI_API_WORKING.md"
    "GEMINI_SETUP_FINAL.md"
    "GEMMA_INTEGRATION_COMPLETE.md"
    "GEMMA_QUICKSTART.md"
    "HOW_TO_FIX_API_KEY_ERROR.md"
    "INITIALIZATION_FIXED.md"
    "METADATA_RESERVED_WORD_FIX.md"
    "PACKAGES_TXT_FIX.md"
    "PYTHON_313_FIX.md"
    "RAG_BOT_WORKING.md"
    "README_STREAMLIT.md"
    "RESPONSE_DISPLAY_FIXED.md"
    "RETRIEVAL_FIX.md"
    "SPEED_IMPROVEMENTS_IMPLEMENTED.md"
    "START_APP.md"
    "START_HERE.md"
    "STREAMLIT_DEPLOY.md"
    "SUCCESS_GEMMA_WORKING.md"
    "SYSTEM_ANALYSIS_AND_FIXES.md"
    "SYSTEM_ANALYSIS_COMPLETE.md"
    "SYSTEM_OPERATIONAL.md"
    "TROUBLESHOOTING_QUICK.md"
)

# Delete unnecessary files
for file in "${DELETE_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "✅ Deleted: $file"
    fi
done

echo ""
echo "📁 Keeping essential documentation:"
for file in "${KEEP_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    fi
done

echo ""
echo "✨ Cleanup complete!"
