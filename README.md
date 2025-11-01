# 🇮🇳 Project Samarth

## Build for Bharat

**An Intelligent Q&A System for Government Agricultural & Climate Data**

A comprehensive Natural Language Q&A system designed to extract cross-domain insights from India's agricultural economy and climate patterns, sourced from data.gov.in portal datasets.

---

## 🎯 Project Vision

Government portals like data.gov.in host thousands of valuable, high-granularity datasets released for public use. However, data exists in varied formats across different ministries, making it difficult for policymakers and researchers to derive cross-domain insights needed for effective decision-making.

**Project Samarth** bridges this gap by providing an intelligent interface that can reason across multiple, inconsistent data sources to answer complex natural language questions.

---

## 🚀 Features

- **Natural Language Queries**: Ask questions in plain English about agriculture and climate
- **Multi-part Query Processing**: Combine rainfall comparisons with crop production rankings
- **Cross-state Analysis**: Compare districts across different states
- **Trend Analysis**: Analyze production trends with climate correlation
- **Policy Support**: Generate data-backed arguments for agricultural policies
- **Source Citations**: Every answer includes traceable data source citations
- **32+ Example Questions**: Pre-built queries covering all challenge question types

---

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
├── data/             # Government datasets from data.gov.in
│   ├── RF25_ind2022_rfp25.nc (IMD Rainfall Data)
│   └── horizontal_crop_vertical_year_report.xls (Agriculture Ministry Data)
├── requirements.txt
└── README.md
```

---

## 📊 Data Sources

This system integrates data from:
- **India Meteorological Department (IMD)**: Rainfall/climate datasets
- **Ministry of Agriculture & Farmers Welfare**: Crop production statistics

### Dataset Coverage
- **33 crops** across **24 states**
- **473 districts** with production data
- **Years**: 2022, 2023
- **Rainfall data**: 2022 (NetCDF format)
- **Crop data**: 2022-2023 (Excel format)

---

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
**Deploy on Streamlit Cloud**: https://share.streamlit.io/

1. Go to https://share.streamlit.io/
2. Connect your GitHub repository
3. Set main file: `frontend/streamlit_app.py`
4. Deploy!

---

## 💬 Challenge Questions Supported

This system addresses all Project Samarth challenge questions:

1. **Multi-domain Comparison**: Compare rainfall across states and list top crops with citations
2. **Cross-state District Analysis**: Identify highest/lowest production districts across states
3. **Trend & Correlation**: Analyze production trends with climate data correlation
4. **Policy Arguments**: Generate three data-backed arguments for crop promotion policies

### Example Queries

- **Multi-part**: "Compare average annual rainfall in Tamil Nadu and Karnataka for last 2 years. In parallel, list top 5 crops in each state."
- **District Comparison**: "Identify district in Tamil Nadu with highest Sugarcane production and compare with lowest in West Bengal"
- **Trend Analysis**: "Analyze production trend of Sugarcane in Andhra Pradesh and correlate with climate data"
- **Policy Support**: "What are three data-backed arguments to promote Sugarcane over Banana in Tamil Nadu?"

---

## 🔧 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python (Pandas, NumPy, SciPy)
- **Data Processing**: NetCDF4, XArray
- **Natural Language**: Regex-based query parsing
- **Visualization**: Matplotlib, Seaborn
- **Data Sources**: data.gov.in portal datasets

---

## 📝 Core Capabilities

✅ **Accuracy & Traceability**: Every answer includes source dataset citations  
✅ **Multi-source Integration**: Handles different data formats and structures  
✅ **Cross-domain Reasoning**: Synthesizes information across agriculture and climate  
✅ **Error Handling**: Graceful handling of missing or inconsistent data  
✅ **Policy Support**: Data-backed arguments for decision-making  

---

## 🎥 Submission

- **Video Demo**: [Loom](https://www.loom.com/share/81f5b965662e49a1a0ed0779d4ca0d0c)
- **Live Prototype**: [Streamlit Cloud](https://rainfall-crop-analysis.streamlit.app)
- **Repository**: [GitHub](https://github.com/saivigneshmn/rainfall-crop-analysis)

---

## 🏛️ System Architecture

The system is architected to handle:
- **Data Harmonization**: Different structures and coded values across ministries
- **Temporal Alignment**: Matching time periods across datasets
- **Geographic Mapping**: State and district name variations
- **Real-time Query Processing**: Determines data sources, queries, and combines results

---

## 📄 License

MIT License

---

**Built for Bharat 🇮🇳 | Project Samarth**
