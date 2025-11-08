#!/bin/bash

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

APP_URL="https://knowledge-ragbot-6kwqvc6giy2crhkortxswc.streamlit.app"

echo "🔍 Checking Streamlit App Status..."
echo "=================================="
echo ""

# Check if app is reachable
echo -n "📡 Testing connection to app... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ App is reachable (HTTP $HTTP_CODE)${NC}"
elif [ "$HTTP_CODE" = "000" ]; then
    echo -e "${YELLOW}⏳ App might still be deploying (no response)${NC}"
else
    echo -e "${YELLOW}⚠️  App returned HTTP $HTTP_CODE${NC}"
fi

echo ""
echo "📦 Verifying critical files in git:"
echo "-----------------------------------"

FILES=(
    "streamlit_app.py"
    "requirements.txt"
    "packages.txt"
    "app/__init__.py"
    "app/config.py"
    "app/models/__init__.py"
    "app/models/database.py"
    "app/core/__init__.py"
    "app/core/ingestion/extractors.py"
    "app/core/llm/orchestrator.py"
)

ALL_PRESENT=true
for file in "${FILES[@]}"; do
    if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $file"
    else
        echo -e "${RED}❌${NC} $file ${RED}(MISSING FROM GIT!)${NC}"
        ALL_PRESENT=false
    fi
done

echo ""
if [ "$ALL_PRESENT" = true ]; then
    echo -e "${GREEN}✅ All critical files are in git${NC}"
else
    echo -e "${RED}❌ Some files are missing! Run: git add <missing-files>${NC}"
fi

echo ""
echo "🌐 App URLs:"
echo "-----------------------------------"
echo "🔗 Live App: $APP_URL"
echo "⚙️  Dashboard: https://share.streamlit.io/"
echo ""
echo "📋 Next Steps:"
echo "-----------------------------------"
echo "1. Wait 3-5 minutes for deployment to complete"
echo "2. Visit dashboard to check logs: https://share.streamlit.io/"
echo "3. Add API secrets if not already configured"
echo "4. Test the app at: $APP_URL"
echo ""
