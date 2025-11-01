# Deployment Guide - Streamlit App

## Option 1: Streamlit Cloud (Recommended - Free & Easy)

### Steps:
1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Rainfall & Crop Analysis App"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set **Main file path**: `streamlit_app.py`
   - Click "Deploy!"
   - Your app will be live at: `https://YOUR-APP-NAME.streamlit.app`

### Important Notes:
- Make sure `data/` folder with `.nc` and `.xls` files is committed to GitHub
- If data files are > 100MB, consider using Git LFS or external storage
- Streamlit Cloud provides free hosting with reasonable limits

---

## Option 2: Quick ngrok Tunnel (For Immediate Demo)

### Steps:
1. **Run Streamlit locally**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **In another terminal, run ngrok**
   ```bash
   # Install ngrok first: https://ngrok.com/download
   ngrok http 8501
   ```

3. **Share the ngrok URL**
   - Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
   - Share this link
   - **Note**: Free ngrok URLs expire after 2 hours. Paid plans provide permanent URLs.

---

## Option 3: Other Cloud Platforms

### Heroku
- Add `Procfile`: `web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
- Add `setup.sh` for dependencies
- Deploy via Git

### AWS/GCP/Azure
- Use EC2/Compute Engine/Virtual Machine
- Run Streamlit as a service
- Configure firewall rules for port 8501

---

## Verification Checklist

Before sharing:
- [ ] App loads successfully
- [ ] Data files are accessible
- [ ] "Load Data" button works
- [ ] At least one example query works
- [ ] Visualizations render correctly
- [ ] Link is publicly accessible (no login required)
- [ ] Link doesn't expire (or you note expiration time)

---

## Current App Features to Test

1. ✅ Natural Language Q&A
2. ✅ Data Overview
3. ✅ Rainfall Analysis
4. ✅ Crop Production Analysis
5. ✅ Trend Analysis
6. ✅ Correlation Analysis
7. ✅ Crop Comparison

---

## Loom Video Link

Your Loom video link: https://www.loom.com/share/81f5b965662e49a1a0ed0779d4ca0d0c

**To ensure it remains open:**
- Go to Loom video settings
- Make sure "Visibility" is set to "Anyone with the link"
- Remove password if any
- Verify the link works in incognito mode

