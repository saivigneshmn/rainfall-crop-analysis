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
   - Branch: `main`
   - Main file path: `frontend/streamlit_app.py`
5. **Click**: "Deploy!"
6. **Wait** 2-5 minutes

## Your App URL

After deployment, your app will be at:
```
https://rainfall-crop-analysis.streamlit.app
```

## Troubleshooting

- **If "frontend/streamlit_app.py not found"**: Check branch is `main`
- **If deployment fails**: Check Streamlit Cloud logs
- **If data doesn't load**: Wait a minute - data files (~50 MB) take time to download
- **If changes not showing**: Streamlit Cloud auto-redeploys on every git push. Wait 2-5 minutes.

## That's It! 🎉

