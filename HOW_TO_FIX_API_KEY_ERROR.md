# 🔧 FIX: Configure Secrets in Streamlit Cloud

## ⚠️ The Error You're Seeing

```
Failed to initialize system: OpenAI API key not provided
```

**Why?** The app doesn't have the Gemini API key configured in Streamlit Cloud yet!

---

## ✅ SOLUTION: Add Secrets to Streamlit Cloud

### Step 1: Go to Streamlit Cloud Dashboard
1. Visit: **https://share.streamlit.io/**
2. Sign in with your GitHub account

### Step 2: Find Your App
- Look for: **Knowledge-RAGbot** or **knowledge-ragbot-6kwqvc6giy2crhkortxswc**
- You should see it in your app list

### Step 3: Open App Settings
1. **Click on your app name** (Knowledge-RAGbot)
2. Look for the **⚙️ Settings** button (top right or in menu)
3. Click **Settings**

### Step 4: Go to Secrets Section
1. In the Settings menu, find **"Secrets"** tab
2. Click on **"Secrets"**
3. You'll see a text editor

### Step 5: Paste Your Configuration
**DELETE everything** in the secrets editor and paste this:

```toml
LLM_PROVIDER = "gemini"
GEMINI_API_KEY = "AIzaSyAnBzRQneAK2VTL-48rwhtpRlWxuX8zKxA"
GEMINI_MODEL = "gemini-pro"
DATABASE_URL = "sqlite:///./data/rag.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7
```

### Step 6: Save Configuration
1. Click the **"Save"** button (bottom right)
2. You'll see "Secrets saved successfully" message

### Step 7: Reboot the App
1. After saving secrets, look for **"Reboot app"** button
2. Click **"Reboot app"** to force restart
3. Wait 30-60 seconds

### Step 8: Clear Browser Cache (Optional)
If still showing errors:
1. Press **Ctrl+Shift+R** (Windows/Linux) or **Cmd+Shift+R** (Mac)
2. This forces a hard refresh

---

## 📸 Visual Guide

### Where to Find Settings:

```
Streamlit Cloud Dashboard
├── Your Apps
│   └── Knowledge-RAGbot  ← Click here
│       ├── ⚙️ Settings   ← Click here
│       │   ├── General
│       │   ├── Secrets   ← Click here (THIS IS WHERE YOU ADD THE CONFIG)
│       │   ├── Advanced
│       │   └── Delete
│       └── Manage app
│           └── Reboot app ← Click here after saving secrets
```

---

## 🔍 How to Verify It Worked

After saving secrets and rebooting:

1. Visit: https://knowledge-ragbot-6kwqvc6giy2crhkortxswc.streamlit.app
2. You should see:
   - ✅ "RAG Document Q&A Bot" title
   - ✅ Upload documents section
   - ✅ No error messages!

If you still see errors:
- Wait 1 more minute (deployment takes time)
- Check Streamlit logs: Settings → Manage app → Logs
- Verify secrets are saved (Settings → Secrets)

---

## 🚨 Common Mistakes

❌ **Mistake 1:** Not clicking "Save" after pasting secrets  
✅ **Solution:** Always click Save button!

❌ **Mistake 2:** Adding comments (#) in secrets.toml  
✅ **Solution:** Use the exact format above, no extra comments

❌ **Mistake 3:** Not rebooting the app  
✅ **Solution:** Click "Reboot app" after saving secrets

❌ **Mistake 4:** Waiting at wrong URL  
✅ **Solution:** Use: https://knowledge-ragbot-6kwqvc6giy2crhkortxswc.streamlit.app

---

## 💡 Alternative: If You Can't Find Settings

If you're having trouble finding the Settings:

1. Go to: https://share.streamlit.io/
2. Click on **your profile/name** (top right)
3. Select **"Your apps"**
4. Find **Knowledge-RAGbot**
5. Click the **three dots (⋮)** next to the app name
6. Select **"Settings"**
7. Click **"Secrets"** tab

---

## 🎯 Expected Result

After completing all steps, your app will:

✅ Start without errors  
✅ Show "Upload documents" interface  
✅ Use Gemini AI for free  
✅ Answer questions about your documents  

---

## 📞 Still Not Working?

### Check Logs:
1. Go to: https://share.streamlit.io/
2. Click your app → Manage app → Logs
3. Look for errors in the logs
4. Share the error message if you need help

### Verify Secrets:
1. Go to Settings → Secrets
2. Make sure it shows your configuration
3. Verify `GEMINI_API_KEY` is there
4. Verify `LLM_PROVIDER = "gemini"`

### Force Fresh Deploy:
1. Make a small change to any file (like README.md)
2. Commit and push to GitHub
3. Streamlit will auto-redeploy

---

## 🎊 You're Almost There!

The code is deployed and working. You just need to configure the secrets in Streamlit Cloud!

**Remember:**
1. Paste secrets → Save → Reboot → Wait 1 minute → Check app

Good luck! 🚀
