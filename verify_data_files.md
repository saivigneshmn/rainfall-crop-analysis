# Data Files Verification

## ✅ Data Files Status for Deployment

Your data files are **properly configured** to be included in Git and deployment:

### File Sizes
- `data/RF25_ind2022_rfp25.nc` - ~48.5 MB ✅
- `data/horizontal_crop_vertical_year_report.xls` - ~1.75 MB ✅
- **Total: ~50 MB** ✅ (Well within GitHub's 100MB file limit)

### .gitignore Configuration
✅ Data files are **INCLUDED** in repository:
- `data/*.nc` is **commented out** (not ignored)
- `data/*.xls` is **commented out** (not ignored)
- Added explicit comments confirming inclusion
- Created `data/.gitkeep` to ensure folder is tracked

### Verification Commands

When you initialize Git, verify data files will be tracked:

```bash
# Initialize git (if not already done)
git init

# Check what will be tracked
git add --dry-run data/

# You should see both data files listed:
# - data/RF25_ind2022_rfp25.nc
# - data/horizontal_crop_vertical_year_report.xls
```

### For Streamlit Cloud Deployment

✅ Data files will be included when you:
1. Push to GitHub: `git add .` includes the data folder
2. Deploy on Streamlit Cloud: It clones your repo including data files
3. App runs: Data files are available at `data/` path

### Important Notes

- **DO NOT** uncomment `data/*.nc` or `data/*.xls` in `.gitignore`
- Files are required for the app to function
- Total size (50MB) is acceptable for GitHub and Streamlit Cloud
- Both files are needed: NetCDF for rainfall, Excel for crop data

### If Files Don't Appear in Git

If data files aren't being tracked (shouldn't happen, but just in case):

```bash
# Force add data files explicitly
git add -f data/RF25_ind2022_rfp25.nc
git add -f data/horizontal_crop_vertical_year_report.xls

# Or add entire data folder
git add -f data/
```

But this shouldn't be necessary since the patterns are commented out in `.gitignore`.

