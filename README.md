# 🌾 Rainfall & Crop Production Analysis System

A comprehensive Natural Language Q&A system for analyzing Indian rainfall data and crop production statistics with data-backed insights.

## 🚀 Features

- **Natural Language Queries**: Ask questions in plain English
- **Multi-part Query Processing**: Combine rainfall comparisons with crop rankings
- **Cross-state Analysis**: Compare districts across different states
- **Trend Analysis**: Analyze production trends with climate correlation
- **Policy Support**: Generate data-backed arguments for agricultural policies
- **32+ Example Questions**: Pre-built queries covering all use cases

## 📁 Project Structure

```
├── backend/          # Core analysis engine
│   ├── data_loader.py
│   ├── data_harmonization.py
│   ├── query_engine.py
│   ├── nl_query_parser.py
│   └── main.py
├── frontend/         # Streamlit web interface
│   └── streamlit_app.py
├── data/             # Dataset files (~50 MB)
│   ├── RF25_ind2022_rfp25.nc
│   └── horizontal_crop_vertical_year_report.xls
├── requirements.txt
└── README.md
```

## 🛠️ Installation

```bash
# Clone repository
git clone https://github.com/saivigneshmn/rainfall-crop-analysis.git
cd rainfall-crop-analysis

# Install dependencies
pip install -r requirements.txt
```

## ▶️ Usage

### Local Development
```bash
streamlit run frontend/streamlit_app.py
```

### Web Deployment
**Live App**: [Deploy on Streamlit Cloud](https://share.streamlit.io/)

1. Go to https://share.streamlit.io/
2. Connect your GitHub repository
3. Set main file: `frontend/streamlit_app.py`
4. Deploy!

**Note**: For Streamlit Cloud, update the main file path to: `frontend/streamlit_app.py`

## 📊 Dataset

- **33 crops** across **24 states**
- **473 districts** with production data
- **Years**: 2022, 2023
- **Rainfall data**: 2022 (NetCDF format)
- **Crop data**: 2022-2023 (Excel format)

## 💬 Example Queries

- **Rainfall Comparison**: "Compare average annual rainfall in Tamil Nadu and Karnataka"
- **Top Crops**: "List the top 10 most produced crops in Maharashtra"
- **District Analysis**: "Identify the district with highest Sugarcane production in Tamil Nadu"
- **Trend Analysis**: "Analyze the production trend of Banana in Karnataka"
- **Policy Support**: "What are three data-backed arguments to promote Sugarcane over Banana in Tamil Nadu?"

## 🔧 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python (Pandas, NumPy, SciPy)
- **Data Processing**: NetCDF4, XArray
- **Natural Language**: Regex-based query parsing
- **Visualization**: Matplotlib, Seaborn

## 📝 Key Capabilities

✅ Multi-part query processing  
✅ Cross-state district comparisons  
✅ Production trend analysis  
✅ Rainfall-production correlation  
✅ Data-backed policy arguments  
✅ Citation management  
✅ Error handling for missing data  

## 🌐 Links

- **Live Demo**: [Streamlit Cloud](https://rainfall-crop-analysis.streamlit.app)
- **Repository**: [GitHub](https://github.com/saivigneshmn/rainfall-crop-analysis)
- **Video Demo**: [Loom](https://www.loom.com/share/81f5b965662e49a1a0ed0779d4ca0d0c)

## 📄 License

MIT License

---

Built with ❤️ for agricultural data analysis
