# 🚀 Streamlit Cloud Deployment

## Automatic Redeployment

**Your app auto-redeploys** whenever you push to GitHub! No action needed.

**If you want to manually trigger a redeploy:**

1. **Go to**: https://share.streamlit.io/
2. **Sign in** with GitHub (same account: `saivigneshmn`)
3. **Find your app** in the dashboard
4. **Click** the **"⋮" (three dots)** menu next to your app
5. **Click** "Reboot app" or "Deploy again"
6. **Wait** 2-5 minutes for redeployment

## First Time Setup

1. **Go to**: https://share.streamlit.io/
2. **Sign in** with GitHub (same account: `saivigneshmn`)
3. **Click**: "New app"
4. **Fill in**:
   - Repository: `saivigneshmn/rainfall-crop-analysis`
   - **Branch: `main`** ⚠️ **CRITICAL**: Make sure it's `main`, NOT `master`!
   - Main file path: `frontend/streamlit_app.py`
5. **Click**: "Advanced settings" and configure:
   - **Python version**: Select `3.11` (recommended for netCDF4, scipy compatibility)
     - ⚠️ **Important**: Use Python 3.11 or 3.12 (NOT 3.13)
     - Python 3.13 may have compatibility issues with netCDF4 and scipy
   - **Secrets**: Leave empty (no API keys needed for this project)
6. **Click**: "Deploy!"
7. **Wait** 2-5 minutes

## Your App URL

After deployment, your app will be at:
```
https://rainfall-crop-analysis.streamlit.app
```

## Troubleshooting

- **If seeing old content/not updating**: ⚠️ **Check the branch!** Make sure Streamlit Cloud is set to deploy from `main` branch, NOT `master` or any other branch. Go to app settings → Edit → Change branch to `main` → Save.
- **If "frontend/streamlit_app.py not found"**: Check branch is `main` (not `master`)
- **If deployment fails**: Check Streamlit Cloud logs for error messages
- **If data doesn't load**: Wait a minute - data files (~50 MB) take time to download
- **If changes not showing**: 
  1. Verify you pushed to `main` branch: `git branch` and `git push origin main`
  2. Check Streamlit Cloud branch is set to `main` (not `master`)
  3. Streamlit Cloud auto-redeploys on every git push. Wait 2-5 minutes.
  4. Clear browser cache or use incognito mode

## That's It! 🎉

