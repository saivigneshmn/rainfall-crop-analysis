# 🚀 Quick Start - Get Your App Online!

## For Your Submission:

### ✅ Loom Video Link
**Your link:** https://www.loom.com/share/81f5b965662e49a1a0ed0779d4ca0d0c

**Verify it works:**
1. Open the link in an incognito browser
2. Video should play without login
3. ✅ If it plays, you're done with Loom!

---

## Option A: Quick Demo (ngrok - ~2 minutes) ⚡

**Best for:** Immediate sharing, testing

1. **Install ngrok** (if not installed):
   - Download: https://ngrok.com/download
   - Extract and add to PATH, or run from folder

2. **Run these commands in TWO separate terminals:**

   **Terminal 1:**
   ```powershell
   cd "C:\Users\Vignesh\Downloads\Bharat"
   streamlit run streamlit_app.py
   ```

   **Terminal 2:**
   ```powershell
   ngrok http 8501
   ```

3. **Copy the HTTPS URL** from ngrok (e.g., `https://abc123.ngrok.io`)
   - This is your public app link!

⚠️ **Note**: Free ngrok links expire after 2 hours.

---

## Option B: Permanent Hosting (Streamlit Cloud - ~10 minutes) 🌐

**Best for:** Permanent link, no expiration

### Step 1: Initialize Git & Push to GitHub

```powershell
cd "C:\Users\Vignesh\Downloads\Bharat"

# Initialize git
git init
git add .
git commit -m "Rainfall & Crop Analysis App"

# Create a new repository on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**Or use GitHub Desktop** (easier):
- Download: https://desktop.github.com/
- Add repository
- Commit and push

### Step 2: Deploy on Streamlit Cloud

1. Visit: **https://share.streamlit.io/**
2. Sign in with **GitHub**
3. Click **"New app"**
4. Fill in:
   - **Repository**: Select your GitHub repo
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. Click **"Deploy!"**
6. Wait 2-3 minutes
7. **Your permanent link**: `https://YOUR-APP-NAME.streamlit.app`

---

## 📋 Submission Format

Copy this format:

```
Public loom link for your recorded submission ⬇️

https://www.loom.com/share/81f5b965662e49a1a0ed0779d4ca0d0c

BONUS: Working prototype link:

[Paste your Streamlit Cloud URL or ngrok URL here]
```

---

## 🆘 Need Help?

**If ngrok doesn't work:**
- Make sure Streamlit is running first (Terminal 1)
- Check Windows Firewall settings
- Try different port: `streamlit run streamlit_app.py --server.port 8502`

**If Streamlit Cloud fails:**
- Check that `data/` folder is in your repo
- Verify `requirements.txt` exists
- Check deployment logs on Streamlit Cloud dashboard

**If Loom link doesn't work:**
- Go to https://www.loom.com/
- Find your video → Settings → Make sure visibility is "Anyone with link"

