# GitHub Authentication Steps

## Your Git Configuration
✅ Git is installed and configured:
- Username: `saivigneshmn`
- Email: `saivigneshmacha@gmail.com`

## Step 1: Create Personal Access Token (Required for HTTPS)

GitHub no longer accepts passwords for HTTPS. You need a Personal Access Token:

1. **Go to GitHub Settings:**
   - Open: https://github.com/settings/tokens
   - Or: GitHub.com → Your Profile Picture → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token:**
   - Click **"Generate new token"** → **"Generate new token (classic)"**
   - **Note**: "Streamlit App Deployment" (or any name)
   - **Expiration**: Choose 90 days or 1 year (or no expiration)
   - **Select scopes**: Check at minimum:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (if you use GitHub Actions)

3. **Copy the Token:**
   - ⚠️ **IMPORTANT**: Copy the token NOW - you won't see it again!
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

4. **Save it securely** (password manager, notes app, etc.)

## Step 2: Test Authentication

After you have your token, we can test the connection.

## Alternative: Use GitHub CLI (Easier)

Install GitHub CLI for easier authentication:

```powershell
# Install via winget (Windows 11) or download from github.com/cli/cli
winget install GitHub.cli

# Or download from: https://cli.github.com/

# Then authenticate:
gh auth login
```

This is easier and handles authentication automatically!

## Step 3: Initialize Repository (Already Done)

Your repository has been initialized. Next steps:
1. Add files
2. Commit
3. Connect to GitHub remote
4. Push (will prompt for token)

---

## Quick Command Flow

```powershell
# 1. Initialize (already done)
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit: Rainfall & Crop Analysis app"

# 4. Add GitHub remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 5. Push (will ask for username and password/token)
git push -u origin main
# Username: saivigneshmn
# Password: YOUR_PERSONAL_ACCESS_TOKEN (not your GitHub password!)
```

---

**Need help?** Tell me when you have your Personal Access Token ready, and I can help you push to GitHub!

