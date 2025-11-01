# GitHub Account Setup & Repository Creation Guide

## Step 1: Create GitHub Account (If you don't have one)

1. Go to https://github.com/signup
2. Enter your email, username, and password
3. Verify your email address
4. Complete the setup questions

## Step 2: Create a New Repository

### Option A: Using GitHub Website (Recommended for beginners)

1. **Go to GitHub** and sign in
2. Click the **"+"** icon (top right) → **"New repository"**
3. **Repository settings:**
   - **Repository name**: `rainfall-crop-analysis` (or any name you prefer)
   - **Description**: "Streamlit app for Rainfall & Crop Production Analysis with NL Q&A"
   - **Visibility**: Choose **Public** (free) or **Private** (if you have GitHub Pro)
   - **DO NOT** initialize with README, .gitignore, or license (we already have files)
   - Click **"Create repository"**

4. **Copy the repository URL** shown on the next page (you'll need it)

### Option B: Using GitHub CLI (Advanced)

```bash
# Install GitHub CLI first: https://cli.github.com/
gh repo create rainfall-crop-analysis --public --source=. --remote=origin --push
```

## Step 3: Initialize Git in Your Project

Open terminal/PowerShell in your project folder and run:

```powershell
# Navigate to your project (if not already there)
cd "C:\Users\Vignesh\Downloads\Bharat"

# Initialize git repository
git init

# Add all files (including data files - they're configured to be included)
git add .

# Make your first commit
git commit -m "Initial commit: Rainfall & Crop Analysis Streamlit app"

# Rename branch to main (if needed)
git branch -M main
```

## Step 4: Connect to GitHub Repository

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name:

```powershell
# Add remote repository (use HTTPS)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Or if you prefer SSH (requires SSH key setup):
# git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### If you get authentication errors:

**For HTTPS:**
- GitHub now requires Personal Access Token (not password)
- Go to: https://github.com/settings/tokens
- Generate new token (classic) with `repo` permissions
- Use token as password when prompted

**Or use GitHub Desktop** (easier):
- Download: https://desktop.github.com/
- Sign in with GitHub account
- File → Add Local Repository
- Commit and push through GUI

## Step 5: Verify Files Are Uploaded

1. Go to your repository on GitHub
2. Check that you see:
   - ✅ `streamlit_app.py`
   - ✅ `requirements.txt`
   - ✅ `data/` folder with both files:
     - `RF25_ind2022_rfp25.nc` (~48.5 MB)
     - `horizontal_crop_vertical_year_report.xls` (~1.75 MB)
   - ✅ All Python files
   - ✅ README.md

## Step 6: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with **GitHub** (authorize access)
3. Click **"New app"**
4. Fill in:
   - **Repository**: Select your repo (`YOUR_USERNAME/YOUR_REPO_NAME`)
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. Click **"Deploy!"**
6. Wait 2-3 minutes for deployment
7. Your app will be live at: `https://YOUR-APP-NAME.streamlit.app`

## Quick Command Reference

```powershell
# Check git status
git status

# See what files will be added
git add --dry-run .

# Add all files
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push origin main

# Check remote connection
git remote -v
```

## Troubleshooting

### "Repository not found" error
- Check repository name is correct
- Verify you have push access
- Make sure repository exists on GitHub

### "Authentication failed"
- Use Personal Access Token instead of password
- Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### "Large file" warning
- Your files (~50MB) should be fine
- If you get warnings, files are still uploaded (just takes longer)
- GitHub allows files up to 100MB per file

### Data files not showing in GitHub
- Verify `.gitignore` has data exclusions commented out
- Run: `git add -f data/` to force add
- Check: `git status` should show data files as "new file"

## Alternative: GitHub Desktop (Easier GUI Method)

1. **Download**: https://desktop.github.com/
2. **Sign in** with GitHub account
3. **File → Clone Repository → URL**
4. Or **File → Add Local Repository**
5. **Commit** your changes
6. **Push** to GitHub
7. Much easier than command line!

## Next Steps After GitHub Setup

Once your code is on GitHub:
1. ✅ Deploy to Streamlit Cloud (see Step 6 above)
2. ✅ Share your Loom video link
3. ✅ Share your Streamlit app link
4. ✅ You're ready for submission!

