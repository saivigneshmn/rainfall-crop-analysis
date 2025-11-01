"""
Project Samarth - Build for Bharat
Intelligent Q&A System for Government Agricultural & Climate Data
"""

from __future__ import annotations
from typing import Any

import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import RainfallCropAnalyzer, format_query_result  # type: ignore
from nl_query_parser import NLQueryParser  # type: ignore

# Page config
st.set_page_config(
    page_title="Project Samarth - Build for Bharat",
    page_icon="🇮🇳",
    layout="wide"
)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
    st.session_state.data_loaded = False
    st.session_state.chat_history = []
    st.session_state.selected_example = None


def load_data() -> bool:
    """Load data into session state"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nc_file = os.path.join(base_dir, "data", "RF25_ind2022_rfp25.nc")
    crop_file = os.path.join(base_dir, "data", "horizontal_crop_vertical_year_report.xls")
    
    if not os.path.exists(nc_file):
        st.error(f"NetCDF file not found at {nc_file}")
        return False
    
    if not os.path.exists(crop_file):
        st.error(f"Crop file not found at {crop_file}")
        return False
    
    try:
        with st.spinner("Loading data... This may take a minute."):
            st.session_state.analyzer = RainfallCropAnalyzer(nc_file, crop_file)
            st.session_state.data_loaded = True
        return True
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return False


def main() -> None:
    st.title("🇮🇳 Project Samarth")
    st.markdown("### Build for Bharat")
    st.markdown("*Intelligent Q&A System for Government Agricultural & Climate Data*")
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose Analysis",
        [
            "Natural Language Q&A",
            "Data Overview",
            "Rainfall Analysis",
            "Crop Production Analysis",
            "Trend Analysis",
            "Correlation Analysis",
            "Crop Comparison"
        ]
    )
    
    # Load data if not loaded
    if not st.session_state.data_loaded:
        st.info("👈 Click the button below to load data")
        if st.button("Load Data"):
            if load_data():
                st.success("Data loaded successfully!")
                st.rerun()
        return
    
    analyzer = st.session_state.analyzer
    
    # Get available states and crops
    if analyzer.crop_loader.df is not None:
        available_states = sorted(analyzer.crop_loader.df['State'].dropna().unique().tolist())
        # Get crop names from columns
        crop_cols = [c for c in analyzer.crop_loader.df.columns if '_production' in c]
        available_crops = sorted([c.replace('_production', '') for c in crop_cols])
        available_years = sorted(analyzer.crop_loader.df['Year'].dropna().unique().astype(int).tolist())
    else:
        available_states = []
        available_crops = []
        available_years = []
    
    # Route to appropriate page
    if page == "Natural Language Q&A":
        show_nl_qa(analyzer)
    elif page == "Data Overview":
        show_data_overview(analyzer)
    elif page == "Rainfall Analysis":
        show_rainfall_analysis(analyzer, available_states)
    elif page == "Crop Production Analysis":
        show_crop_analysis(analyzer, available_states, available_crops, available_years)
    elif page == "Trend Analysis":
        show_trend_analysis(analyzer, available_states, available_crops)
    elif page == "Correlation Analysis":
        show_correlation_analysis(analyzer, available_states, available_crops)
    elif page == "Crop Comparison":
        show_crop_comparison(analyzer, available_states, available_crops, available_years)


def show_nl_qa(analyzer: RainfallCropAnalyzer) -> None:
    # Enhanced CSS styling with cohesive color scheme
    st.markdown("""
    <style>
    /* Color Palette */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --primary-light: #818cf8;
        --secondary: #8b5cf6;
        --success: #10b981;
        --error: #ef4444;
        --warning: #f59e0b;
        --info: #3b82f6;
        --dark-bg: #1e293b;
        --dark-surface: #334155;
        --light-bg: #f8fafc;
        --light-surface: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }
    
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .example-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #6366f1;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
        border: 1px solid #e2e8f0;
    }
    
    .example-card:hover {
        background: #f1f5f9;
        transform: translateX(3px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left-color: #4f46e5;
    }
    
    .chat-message {
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #3b82f6;
        color: #1e40af;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border-left: 4px solid #10b981;
        color: #065f46;
    }
    
    .error-message {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 4px solid #ef4444;
        color: #991b1b;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin: 0.5rem;
        border: 1px solid #e2e8f0;
    }
    
    .result-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    /* Button styling overrides */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3);
    }
    
    div[data-testid="stButton"] > button:not([kind="primary"]) {
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    div[data-testid="stButton"] > button:not([kind="primary"]):hover {
        background: #e2e8f0;
        border-color: #94a3b8;
        transform: translateY(-1px);
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Query type badge */
    .query-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with gradient
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; color: white;">💬 Natural Language Q&A</h1>
        <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.9);">
            Ask questions in natural language about government agricultural & climate data<br>
            <small style="font-size: 0.9em; opacity: 0.95;">Project Samarth Challenge Questions - Cross-domain insights from data.gov.in</small>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize parser
    parser = NLQueryParser(analyzer.query_engine)
    
    # Sidebar with quick stats
    with st.sidebar:
        st.markdown("### 📊 Quick Stats")
        if analyzer.crop_loader.df is not None:
            total_states = analyzer.crop_loader.df['State'].nunique()
            total_districts = analyzer.crop_loader.df['District'].nunique() if 'District' in analyzer.crop_loader.df.columns else 0
            total_years = len(analyzer.crop_loader.df['Year'].unique()) if 'Year' in analyzer.crop_loader.df.columns else 0
            st.metric("States", total_states)
            st.metric("Districts", total_districts)
            st.metric("Years", total_years)
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Display chat history (show last 3 conversations to avoid clutter)
    if st.session_state.chat_history:
        st.markdown("### 💭 Recent Conversations")
        recent_chats = st.session_state.chat_history[-3:]  # Show last 3
        
        for idx, chat in enumerate(recent_chats):
            with st.expander(f"💬 {chat['question'][:60]}...", expanded=(idx == len(recent_chats) - 1)):
                # User message
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong style="color: #1e40af;">👤 You:</strong> 
                    <span style="color: #1e40af;">{chat['question']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Assistant response
                if chat.get('success'):
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong style="color: #065f46;">🤖 Assistant:</strong> 
                        <span style="color: #065f46;">Query processed successfully! ✅</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif chat.get('error'):
                    st.markdown(f"""
                    <div class="chat-message error-message">
                        <strong style="color: #991b1b;">❌ Error:</strong> 
                        <span style="color: #991b1b;">{chat.get('error', 'Unknown error')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong style="color: #065f46;">🤖 Assistant:</strong> 
                        <span style="color: #065f46;">Processing...</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Example questions - Only 8 guaranteed working questions
    st.markdown("### 💡 Project Samarth Challenge Questions")
    st.markdown("**Click on any question to load it into the input box below:**")
    
    # Only proven working questions
    examples = [
        # === CHALLENGE QUESTIONS (Original 4) ===
        {
            "icon": "🌧️🌾",
            "text": "Compare the average annual rainfall in Tamil Nadu and Karnataka for the last 2 available years. In parallel, list the top 5 most produced crops in Tamil Nadu and Karnataka during the same period, citing all data sources.",
            "category": "Challenge Question 1"
        },
        {
            "icon": "📍",
            "text": "Identify the district in Tamil Nadu with the highest production of Sugarcane in the most recent year available and compare that with the district with the lowest production of Sugarcane in West Bengal",
            "category": "Challenge Question 2"
        },
        {
            "icon": "📈🌧️",
            "text": "Analyze the production trend of Sugarcane in Andhra Pradesh. Correlate this trend with the corresponding climate data for the same period and provide a summary of the apparent impact.",
            "category": "Challenge Question 3"
        },
        {
            "icon": "⚖️📊",
            "text": "A policy advisor is proposing a scheme to promote Sugarcane over Banana in Tamil Nadu. Based on historical data from the last 3 years, what are the three most compelling data-backed arguments to support this policy? Your answer must synthesize data from both climate and agricultural sources.",
            "category": "Challenge Question 4"
        },
        {
            "icon": "🌧️",
            "text": "What is the average annual rainfall in Maharashtra?",
            "category": "Simple Query"
        },
        {
            "icon": "🌾",
            "text": "List the top 10 most produced crops in Karnataka",
            "category": "Simple Query"
        },
        {
            "icon": "📍",
            "text": "Which district in Andhra Pradesh has the highest production of Coconut?",
            "category": "Simple Query"
        },
        {
            "icon": "📊",
            "text": "Compare rainfall between Kerala and Tamil Nadu",
            "category": "Simple Query"
        }
    ]
    
    # Display all 8 examples in a grid
    cols = st.columns(2)
    for idx, example in enumerate(examples):
        with cols[idx % 2]:
            if st.button(
                f"{example['icon']} **{example['category']}**\n\n{example['text'][:120]}...",
                key=f"example_{idx}",
                use_container_width=True,
                help=example['text']
            ):
                st.session_state.question_input = example['text']
                st.rerun()
    
    # Question input with better styling
    st.markdown("### ✍️ Ask Your Question")
    
    # Get question from session state (set by button clicks)
    # Clear it after using so it doesn't persist
    default_question = st.session_state.get('question_input', '')
    
    # Create text area - use key that syncs with session state
    question = st.text_area(
        "Enter your question:",
        value=default_question if default_question else "",
        height=120,
        placeholder="Type your question here or click a question above to load it...",
        label_visibility="collapsed",
        key="question_input"
    )
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ask_button = st.button("🚀 Ask Question", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    with col3:
        help_button = st.button("❓ Help", use_container_width=True)
    
    if clear_button:
        st.session_state.question_input = ""
        st.rerun()
    
    if help_button:
        with st.expander("💡 Tips for asking questions", expanded=True):
            st.markdown("""
            **Tips for better results:**
            - ✅ Use state names (e.g., "Andhra Pradesh", "Karnataka")
            - ✅ Mention crop names (e.g., "Rice", "Wheat", "Sugarcane")
            - ✅ Specify years if needed (e.g., "for 2023", "last 5 years")
            - ✅ Use phrases like "compare", "top", "highest", "trend"
            
            **Challenge Question Types:**
            1. **Multi-part queries**: Combine rainfall comparison with crop listings
               - "Compare rainfall in State_X and State_Y. In parallel, list top M crops..."
            
            2. **District comparison**: Find highest/lowest production districts
               - "Identify district in State_X with highest production of Crop_Z..."
            
            3. **Trend & correlation**: Analyze production trends with climate data
               - "Analyze production trend of Crop_X in State_Y over the last decade..."
            
            4. **Policy arguments**: Get data-backed arguments for crop promotion
               - "Promote Crop_A over Crop_B in State_Y. What are three compelling arguments..."
            """)
    
    if ask_button:
        # Get the current question value
        # Streamlit widgets with keys store their value in both:
        # 1. The return value of the widget (question variable)
        # 2. st.session_state[key] (st.session_state.question_input)
        # Both should be the same, but let's prioritize session_state as it's more reliable
        
        # Get question from text area or session state
        if question and question.strip():
            current_question = question.strip()
        elif st.session_state.get('question_input'):
            current_question = str(st.session_state.question_input).strip()
        else:
            st.warning("⚠️ Please enter a question before submitting")
            return
        
        question = current_question
        
        # Add to chat history
        st.session_state.chat_history.append({
            'question': question,
            'success': False,
            'error': None
        })
        
        # Create container for result
        result_container = st.container()
        
        with result_container:
            # Processing indicator with progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.info("🔄 Parsing your question...")
            progress_bar.progress(20)
            
            try:
                # Parse and execute
                query_result = parser.execute_query(question)
                progress_bar.progress(60)
                status_text.info("🔄 Executing query...")
                
                progress_bar.progress(80)
                
                # Result section
                if 'error' in query_result and query_result['result'] is None:
                    # Error handling
                    st.session_state.chat_history[-1]['error'] = query_result['error']
                    
                    st.markdown("""
                    <div class="chat-message error-message">
                        <strong style="color: #991b1b;">❌ Error:</strong> 
                        <span style="color: #991b1b;">{error}</span>
                    </div>
                    """.format(error=query_result['error']), unsafe_allow_html=True)
                    
                    if 'suggested_functions' in query_result.get('parsed_info', {}):
                        with st.expander("💡 Suggested Query Functions", expanded=True):
                            st.markdown("Try using these specific functions:")
                            for func in query_result['parsed_info']['suggested_functions']:
                                st.code(func, language='python')
                    
                    # Show parsing details
                    with st.expander("🔍 Query Parsing Details", expanded=False):
                        st.json(query_result.get('parsed_info', {}))
                
                else:
                    result = query_result.get('result', {})
                    st.session_state.chat_history[-1]['success'] = True
                    
                    progress_bar.progress(100)
                    status_text.success("✅ Query executed successfully!")
                    
                    # Show query type badge
                    query_type = query_result.get('parsed_info', {}).get('query_type', 'unknown')
                    query_type_names = {
                        'compare_rainfall': '🌧️ Rainfall Comparison',
                        'top_crops': '🌾 Top Crops',
                        'district_production': '📍 District Analysis',
                        'trend_analysis': '📈 Trend Analysis',
                        'correlation': '🔗 Correlation',
                        'crop_comparison': '⚖️ Crop Comparison',
                        'multi_part': '🔄 Multi-part Query'
                    }
                    
                    badge_name = query_type_names.get(query_type, query_type.replace('_', ' ').title())
                    st.markdown(f"""
                    <div class="query-badge">
                        {badge_name}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Handle multi-part and trend_correlation results
                    query_type = query_result.get('parsed_info', {}).get('query_type')
                    
                    if isinstance(result, dict) and (query_type == 'multi_part' or query_type == 'trend_correlation'):
                        if query_type == 'multi_part':
                            st.markdown("### 🎉 Multi-part Query Results")
                        else:
                            st.markdown("### 📈📊 Trend & Correlation Analysis")
                        
                        tabs = st.tabs([part.replace('_', ' ').title() for part in result.keys()])
                        
                        for tab, (part_name, part_result) in zip(tabs, result.items()):
                            with tab:
                                if 'error' in part_result:
                                    st.error(f"Error in {part_name}: {part_result['error']}")
                                else:
                                    _display_result(part_result, part_name)
                    
                    elif 'error' in result:
                        st.error(f"❌ Query Error: {result['error']}")
                    else:
                        _display_result(result)
                    
                    # Show parsing details in expander
                    with st.expander("🔍 Technical Details", expanded=False):
                        st.json(query_result.get('parsed_info', {}))
                
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                st.session_state.chat_history[-1]['error'] = str(e)
                st.error(f"❌ Unexpected error: {str(e)}")
                progress_bar.empty()
                status_text.empty()


def _display_result(result: dict[str, Any], part_name: str | None = None) -> None:
    """Helper function to display results with enhanced UI"""
    # Display result in styled container
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    
    # Format and display result
    formatted = format_query_result(result)
    st.markdown(formatted)
    
    # Enhanced visualizations
    if 'comparison' in result and isinstance(result['comparison'], pd.DataFrame):
        df = result['comparison']
        
        if 'Average Rainfall (mm)' in df.columns:
            # Rainfall comparison chart
            fig, ax = plt.subplots(figsize=(12, 6))
            colors = sns.color_palette("husl", len(df))
            bars = ax.bar(df['State'], df['Average Rainfall (mm)'], color=colors)
            ax.set_xlabel('State', fontsize=12, fontweight='bold')
            ax.set_ylabel('Average Rainfall (mm)', fontsize=12, fontweight='bold')
            ax.set_title('Rainfall Comparison by State', fontsize=14, fontweight='bold', pad=20)
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
        elif 'Crop' in df.columns:
            # Crop comparison chart
            fig, axes = plt.subplots(1, 2, figsize=(16, 6))
            
            if 'Total Production' in df.columns:
                colors = ['#4CAF50', '#2196F3']
                axes[0].bar(df['Crop'], df['Total Production'], color=colors[:len(df)])
                axes[0].set_title('Total Production', fontsize=12, fontweight='bold')
                axes[0].set_ylabel('Production', fontsize=11)
                axes[0].tick_params(axis='x', rotation=45)
            
            if 'Yield' in df.columns:
                yields = [y if isinstance(y, (int, float)) and not pd.isna(y) else 0 
                          for y in df['Yield']]
                axes[1].bar(df['Crop'], yields, color=colors[:len(df)])
                axes[1].set_title('Yield Comparison', fontsize=12, fontweight='bold')
                axes[1].set_ylabel('Yield', fontsize=11)
                axes[1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
    
    elif 'top_crops' in result and isinstance(result['top_crops'], pd.DataFrame):
        df = result['top_crops']
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = plt.get_cmap('viridis')(np.linspace(0, 1, len(df)))
        bars = ax.barh(df['Crop'], df['Total Production'], color=colors)
        ax.set_xlabel('Total Production', fontsize=12, fontweight='bold')
        ax.set_ylabel('Crop', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {result.get("top_n", 10)} Crops by Production', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Add value labels
        for i, (idx, row) in enumerate(df.iterrows()):
            ax.text(row['Total Production'], i, 
                   f"  {row['Total Production']:,.0f}",
                   va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    elif 'trend_analysis' in result:
        trend = result['trend_analysis']
        if 'error' not in trend and 'yearly_data' in trend:
            df = trend['yearly_data']
            fig, ax = plt.subplots(figsize=(14, 7))
            
            ax.plot(df['Year'], df['Production'], marker='o', linewidth=3, 
                   markersize=10, color='#2196F3', label='Production')
            
            # Add trend line
            if 'slope' in trend:
                z = np.polyfit(df['Year'], df['Production'], 1)
                p = np.poly1d(z)
                ax.plot(df['Year'], p(df['Year']), "r--", alpha=0.7, 
                       linewidth=2, label='Trend Line')
            
            ax.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax.set_ylabel('Production', fontsize=12, fontweight='bold')
            ax.set_title('Production Trend Analysis', fontsize=14, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=11)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
    
    elif 'districts' in result and isinstance(result['districts'], pd.DataFrame):
        df = result['districts'].head(20)
        fig, ax = plt.subplots(figsize=(12, max(8, len(df) * 0.5)))
        
        colors = plt.get_cmap('plasma')(np.linspace(0.2, 0.8, len(df)))
        bars = ax.barh(df['District'], df['Production'], color=colors)
        ax.set_xlabel('Production', fontsize=12, fontweight='bold')
        ax.set_ylabel('District', fontsize=12, fontweight='bold')
        ax.set_title(f'{result.get("crop", "Crop")} Production by District', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    elif 'arguments' in result:
        # Display policy arguments in cards
        st.markdown("### 🎯 Three Data-Backed Arguments")
        cols = st.columns(3)
        
        for idx, arg in enumerate(result['arguments']):
            with cols[idx]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #667eea; margin-bottom: 0.5rem;">
                        Argument {idx + 1}
                    </h4>
                    <p style="font-weight: bold; margin-bottom: 0.5rem;">
                        {arg['argument']}
                    </p>
                    <p style="color: #666; font-size: 0.9em; margin-bottom: 0.3rem;">
                        📊 {arg['data']}
                    </p>
                    <p style="color: #888; font-size: 0.85em;">
                        Metric: {arg['metric']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    elif 'query_type' in result and result['query_type'] == 'district_comparison_cross_state':
        # Display cross-state district comparison
        st.markdown("### 📍 Cross-State District Comparison")
        st.markdown(f"**Crop:** {result.get('crop', 'N/A')}")
        st.markdown(f"**Year:** {result.get('year', 'N/A')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### 🏆 Highest in {result.get('highest_state', 'N/A')}")
            highest = result.get('highest_district', {})
            if 'districts' in highest and isinstance(highest['districts'], pd.DataFrame) and len(highest['districts']) > 0:
                st.dataframe(highest['districts'])
            elif 'error' in highest:
                st.error(highest['error'])
        
        with col2:
            st.markdown(f"#### 📉 Lowest in {result.get('lowest_state', 'N/A')}")
            lowest = result.get('lowest_district', {})
            if 'districts' in lowest and isinstance(lowest['districts'], pd.DataFrame) and len(lowest['districts']) > 0:
                st.dataframe(lowest['districts'])
            elif 'error' in lowest:
                st.error(lowest['error'])
        
        # Show citation
        if result.get('citation'):
            st.markdown("---")
            st.markdown(result['citation'])
    
    st.markdown('</div>', unsafe_allow_html=True)


def show_data_overview(analyzer: RainfallCropAnalyzer) -> None:
    st.header("📊 Data Overview")
    st.markdown("*Data sources: India Meteorological Department (IMD) & Ministry of Agriculture & Farmers Welfare*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Rainfall Data")
        rf_metadata = analyzer.rainfall_loader.get_metadata()
        st.json(rf_metadata)
    
    with col2:
        st.subheader("Crop Production Data")
        crop_metadata = analyzer.crop_loader.get_metadata()
        st.json(crop_metadata)
    
    st.subheader("Sample Crop Data")
    if analyzer.crop_loader.df is not None:
        st.dataframe(analyzer.crop_loader.df.head(20))


def show_rainfall_analysis(analyzer: RainfallCropAnalyzer, available_states: list[str]) -> None:
    st.header("🌧️ Rainfall Analysis")
    
    tab1, tab2 = st.tabs(["Average Rainfall", "Compare States"])
    
    with tab1:
        st.subheader("Get Average Rainfall by State")
        state = st.selectbox("Select State", available_states, key="rf_state")
        
        if st.button("Get Average Rainfall"):
            result = analyzer.query_engine.get_avg_rainfall(state)
            
            if 'error' not in result:
                st.metric("Average Rainfall", f"{result['average_rainfall']:.2f} mm")
                st.markdown(format_query_result(result))
            else:
                st.error(result['error'])
    
    with tab2:
        st.subheader("Compare Rainfall Between States")
        states = st.multiselect("Select States to Compare", available_states, key="rf_states", max_selections=5)
        
        if len(states) >= 2:
            if st.button("Compare Rainfall"):
                result = analyzer.query_engine.compare_rainfall(states)
                
                if 'error' not in result:
                    st.dataframe(result['comparison'])
                    
                    # Visualization
                    fig, ax = plt.subplots(figsize=(10, 6))
                    df = result['comparison']
                    ax.bar(df['State'], df['Average Rainfall (mm)'])
                    ax.set_xlabel('State')
                    ax.set_ylabel('Average Rainfall (mm)')
                    ax.set_title('Rainfall Comparison')
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)
                    
                    st.markdown(format_query_result(result))
                else:
                    st.error(result['error'])
        else:
            st.info("Please select at least 2 states")


def show_crop_analysis(analyzer: RainfallCropAnalyzer, available_states: list[str], available_crops: list[str], available_years: list[int]) -> None:
    st.header("🌾 Crop Production Analysis")
    
    tab1, tab2 = st.tabs(["Top Crops", "District Analysis"])
    
    with tab1:
        st.subheader("Top Crops by Production")
        state = st.selectbox("Select State", available_states, key="top_crop_state")
        top_n = st.slider("Number of Top Crops", 5, 20, 10, key="top_n")
        years = st.multiselect("Filter by Years (optional)", available_years, key="top_crop_years")
        
        if st.button("Get Top Crops"):
            result = analyzer.query_engine.get_top_crops(
                state, 
                years if years else None, 
                top_n
            )
            
            if 'error' not in result:
                st.dataframe(result['top_crops'])
                
                # Visualization
                fig, ax = plt.subplots(figsize=(12, 6))
                df = result['top_crops']
                ax.barh(df['Crop'], df['Total Production'])
                ax.set_xlabel('Total Production')
                ax.set_ylabel('Crop')
                ax.set_title(f'Top {top_n} Crops in {state}')
                st.pyplot(fig)
                
                st.markdown(format_query_result(result))
            else:
                st.error(result['error'])
    
    with tab2:
        st.subheader("Crop Production by District")
        crop = st.selectbox("Select Crop", available_crops, key="district_crop")
        state = st.selectbox("Select State (optional)", [None] + available_states, key="district_state")
        year = st.selectbox("Select Year (optional)", [None] + available_years, key="district_year")
        top_n = st.slider("Number of Districts", 5, 50, 10, key="district_top_n")
        
        if st.button("Get District Data"):
            result = analyzer.query_engine.get_crop_production_by_district(
                crop,
                state,
                year,
                top_n
            )
            
            if 'error' not in result:
                st.dataframe(result['districts'])
                
                # Visualization
                fig, ax = plt.subplots(figsize=(12, 8))
                df = result['districts'].head(top_n)
                ax.barh(df['District'], df['Production'])
                ax.set_xlabel('Production')
                ax.set_ylabel('District')
                ax.set_title(f'{crop} Production by District')
                st.pyplot(fig)
                
                st.markdown(format_query_result(result))
            else:
                st.error(result['error'])


def show_trend_analysis(analyzer: RainfallCropAnalyzer, available_states: list[str], available_crops: list[str]) -> None:
    st.header("📈 Trend Analysis")
    
    crop = st.selectbox("Select Crop", available_crops, key="trend_crop")
    state = st.selectbox("Select State (optional)", [None] + available_states, key="trend_state")
    
    if st.button("Analyze Trends"):
        result = analyzer.query_engine.analyze_trends(crop, state)
        
        if 'error' not in result:
            trend = result['trend_analysis']
            
            if 'error' not in trend:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Trend", trend.get('trend_direction', 'N/A'))
                with col2:
                    st.metric("R-squared", f"{trend.get('r_squared', 0):.4f}")
                with col3:
                    st.metric("P-value", f"{trend.get('p_value', 0):.4f}")
                
                # Visualization
                fig, ax = plt.subplots(figsize=(12, 6))
                df = trend['yearly_data']
                ax.plot(df['Year'], df['Production'], marker='o')
                ax.set_xlabel('Year')
                ax.set_ylabel('Production')
                ax.set_title(f'{crop} Production Trend')
                ax.grid(True)
                st.pyplot(fig)
                
                st.dataframe(df)
                st.markdown(format_query_result(result))
            else:
                st.error(trend['error'])
        else:
            st.error(result['error'])


def show_correlation_analysis(analyzer: RainfallCropAnalyzer, available_states: list[str], available_crops: list[str]) -> None:
    st.header("🔗 Correlation Analysis")
    
    st.markdown("Analyze correlation between rainfall and crop production")
    
    crop = st.selectbox("Select Crop", available_crops, key="corr_crop")
    state = st.selectbox("Select State", available_states, key="corr_state")
    
    if st.button("Calculate Correlation"):
        result = analyzer.query_engine.correlate_rainfall_production(crop, state)
        
        if 'error' not in result:
            corr = result['correlation']
            st.metric("Average Rainfall", f"{corr.get('average_rainfall_mm', 0):.2f} mm")
            
            st.subheader("Production by Year")
            st.dataframe(corr['production_data'])
            
            # Visualization
            fig, ax = plt.subplots(figsize=(12, 6))
            df = corr['production_data']
            ax.plot(df['Year'], df['Production'], marker='o', label='Production')
            ax.axhline(y=corr.get('average_rainfall_mm', 0), color='r', linestyle='--', label='Average Rainfall (mm)')
            ax.set_xlabel('Year')
            ax.set_ylabel('Production / Rainfall')
            ax.set_title(f'Rainfall vs {crop} Production in {state}')
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
            
            st.markdown(format_query_result(result))
        else:
            st.error(result['error'])


def show_crop_comparison(analyzer: RainfallCropAnalyzer, available_states: list[str], available_crops: list[str], available_years: list[int]) -> None:
    st.header("⚖️ Crop Comparison")
    
    st.markdown("Compare two crops and get three data-backed arguments")
    
    col1, col2 = st.columns(2)
    with col1:
        crop_a = st.selectbox("First Crop", available_crops, key="comp_crop_a")
    with col2:
        crop_b = st.selectbox("Second Crop", available_crops, key="comp_crop_b", 
                             index=min(1, len(available_crops)-1))
    
    state = st.selectbox("Select State", available_states, key="comp_state")
    year = st.selectbox("Select Year (optional)", [None] + available_years, key="comp_year")
    
    if crop_a == crop_b:
        st.warning("Please select two different crops")
        return
    
    if st.button("Compare Crops"):
        result = analyzer.query_engine.compare_crops(crop_a, crop_b, state, year)
        
        if 'error' not in result:
            st.subheader("Three Data-Backed Arguments")
            for i, arg in enumerate(result['arguments'], 1):
                with st.expander(f"Argument {i}: {arg['argument']}"):
                    st.write(f"**Data:** {arg['data']}")
                    st.write(f"**Metric:** {arg['metric']}")
            
            st.subheader("Comparison Table")
            st.dataframe(result['comparison'])
            
            # Visualization
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            
            df = result['comparison']
            crops = df['Crop'].tolist()
            
            # Total Production
            axes[0].bar(crops, df['Total Production'])
            axes[0].set_title('Total Production')
            axes[0].set_ylabel('Production')
            
            # Yield
            yields = []
            for y in df['Yield']:
                if isinstance(y, (int, float)) and not np.isnan(y):
                    yields.append(y)
                else:
                    yields.append(0)
            axes[1].bar(crops, yields)
            axes[1].set_title('Yield')
            axes[1].set_ylabel('Yield')
            
            # Districts
            axes[2].bar(crops, df['Districts'])
            axes[2].set_title('Number of Districts')
            axes[2].set_ylabel('Districts')
            
            plt.tight_layout()
            st.pyplot(fig)
            
            st.markdown(format_query_result(result))
        else:
            st.error(result['error'])


if __name__ == "__main__":
    main()

