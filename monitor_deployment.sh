#!/bin/bash

# Monitor Streamlit deployment status
APP_URL="https://knowledge-ragbot-6kwqvc6giy2crhkortxswc.streamlit.app"

echo "🔄 Monitoring deployment status..."
echo "=================================="
echo ""
echo "App URL: $APP_URL"
echo "Press Ctrl+C to stop monitoring"
echo ""

attempt=0
max_attempts=60  # 5 minutes (60 * 5 seconds)

while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    timestamp=$(date "+%H:%M:%S")
    
    # Try to fetch the app
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$APP_URL")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "[$timestamp] ✅ SUCCESS! App is live (HTTP $HTTP_CODE)"
        echo ""
        echo "🎉 Deployment completed successfully!"
        echo "🌐 Visit: $APP_URL"
        echo ""
        echo "📋 Next steps:"
        echo "1. Configure API secrets in Streamlit Cloud dashboard"
        echo "2. Test uploading a document"
        echo "3. Ask a question to verify functionality"
        exit 0
    elif [ "$HTTP_CODE" = "000" ]; then
        echo "[$timestamp] ⏳ Deploying... (no response yet)"
    elif [ "$HTTP_CODE" = "303" ]; then
        echo "[$timestamp] 🔄 Restarting... (HTTP $HTTP_CODE)"
    elif [ "$HTTP_CODE" = "502" ] || [ "$HTTP_CODE" = "503" ]; then
        echo "[$timestamp] ⚠️  Building... (HTTP $HTTP_CODE)"
    else
        echo "[$timestamp] ⚠️  Status: HTTP $HTTP_CODE"
    fi
    
    sleep 5
done

echo ""
echo "⏰ Monitoring timed out after 5 minutes"
echo "💡 The app might still be deploying. Check manually:"
echo "   $APP_URL"
echo "   https://share.streamlit.io/"
