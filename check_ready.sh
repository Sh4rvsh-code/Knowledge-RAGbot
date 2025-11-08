#!/bin/bash
# Final verification before deployment

echo "🎯 Final Pre-Deployment Check"
echo "=============================="
echo ""

# Check all required files exist
echo "📁 Checking files..."
files=(
    "streamlit_app.py"
    "requirements.txt"
    "packages.txt"
    ".streamlit/config.toml"
    ".streamlit/secrets.toml.example"
    "START_HERE.md"
    "STREAMLIT_DEPLOY.md"
    "DEPLOYMENT_CHECKLIST.md"
    "deploy_streamlit.sh"
)

all_good=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MISSING!"
        all_good=false
    fi
done

echo ""
echo "📊 Project Summary:"
echo "  Total Python files: $(find . -name "*.py" -not -path "./venv*" -not -path "./.venv*" | wc -l | tr -d ' ')"
echo "  Documentation files: $(find . -name "*.md" | wc -l | tr -d ' ')"
echo "  Configuration files: $(find . -name "*.toml" -o -name "*.yml" -o -name "*.txt" | grep -v venv | wc -l | tr -d ' ')"

echo ""
if [ "$all_good" = true ]; then
    echo "✅ All required files present!"
    echo ""
    echo "🚀 Ready to deploy!"
    echo ""
    echo "Next steps:"
    echo "  1. Read START_HERE.md"
    echo "  2. Run: ./deploy_streamlit.sh"
    echo "  3. Deploy to Streamlit Cloud"
    echo ""
else
    echo "❌ Some files are missing!"
    echo "Please ensure all files are created before deploying."
fi
