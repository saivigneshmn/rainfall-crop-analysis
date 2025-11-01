"""
Project Samarth - Build for Bharat
Zero-dependency markdown table formatting (no tabulate required)
Version: 2025-01 - Production Ready
"""
import sys
import os
from data_loader import RainfallLoader, CropDataLoader
from data_harmonization import StateDistrictMapper, TemporalHarmonizer
from query_engine import QueryEngine
import pandas as pd


class RainfallCropAnalyzer:
    """Main analyzer class that orchestrates all components"""
    
    def __init__(self, nc_file_path: str, crop_file_path: str):
        """
        Initialize the analyzer
        
        Args:
            nc_file_path: Path to NetCDF rainfall file
            crop_file_path: Path to crop production file
        """
        self.nc_file_path = nc_file_path
        self.crop_file_path = crop_file_path
        
        # Load data
        print("Loading rainfall data...")
        self.rainfall_loader = RainfallLoader(nc_file_path)
        self.rainfall_loader.load()
        
        print("Loading crop data...")
        self.crop_loader = CropDataLoader(crop_file_path)
        self.crop_loader.load()
        
        # Initialize harmonization
        print("Initializing data harmonization...")
        self.mapper = StateDistrictMapper(
            self.rainfall_loader.lon,
            self.rainfall_loader.lat
        )
        
        # Get available years from both datasets
        rainfall_years = self.rainfall_loader.years if hasattr(self.rainfall_loader, 'years') else []
        crop_years = []
        if self.crop_loader.df is not None and 'Year' in self.crop_loader.df.columns:
            crop_years = sorted(self.crop_loader.df['Year'].dropna().unique().astype(int).tolist())
        
        print(f"Rainfall years: {rainfall_years}")
        print(f"Crop years: {crop_years}")
        
        self.harmonizer = TemporalHarmonizer(
            rainfall_years=rainfall_years,
            crop_years=crop_years
        )
        
        # Initialize query engine
        print("Initializing query engine...")
        self.query_engine = QueryEngine(
            self.rainfall_loader,
            self.crop_loader,
            self.mapper,
            self.harmonizer
        )
        
        print("Setup complete!")
    
    def close(self):
        """Close resources"""
        if self.rainfall_loader:
            self.rainfall_loader.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def dataframe_to_markdown(df: pd.DataFrame, index: bool = False) -> str:
    """
    Convert DataFrame to markdown table format.
    This is a custom implementation that doesn't require tabulate.
    
    Args:
        df: pandas DataFrame to convert
        index: Whether to include index column
        
    Returns:
        Markdown-formatted string table
    """
    if df is None or df.empty:
        return "*(No data available)*"
    
    try:
        lines = []
        # Header
        cols = [str(col) for col in df.columns.tolist()]
        if index:
            cols = [''] + cols
        lines.append('| ' + ' | '.join(cols) + ' |')
        # Separator
        lines.append('| ' + ' | '.join(['---'] * len(cols)) + ' |')
        # Rows
        for idx, row in df.iterrows():
            # Handle NaN values and convert all to strings
            values = []
            for val in row.values:
                if pd.isna(val):
                    values.append('N/A')
                else:
                    # Format numbers nicely
                    if isinstance(val, (int, float)):
                        if val == int(val):
                            values.append(str(int(val)))
                        else:
                            values.append(f"{val:.2f}")
                    else:
                        values.append(str(val))
            
            if index:
                values = [str(idx)] + values
            lines.append('| ' + ' | '.join(values) + ' |')
        return '\n'.join(lines)
    except Exception as e:
        # Fallback if anything goes wrong
        return f"*(Error formatting table: {str(e)})*"


def format_query_result(result: dict) -> str:
    """Format query result as markdown"""
    if not isinstance(result, dict):
        return f"**Error:** Invalid result format"
    
    if 'error' in result:
        return f"**Error:** {result['error']}"
    
    output = []
    
    # Add title/header based on query type
    if 'comparison' in result:
        output.append("## Rainfall Comparison\n")
        if isinstance(result['comparison'], pd.DataFrame):
            output.append(dataframe_to_markdown(result['comparison'], index=False))
        else:
            output.append("*(No comparison data available)*")
        output.append(f"\n*Years: {result.get('years', 'N/A')}*\n")
    elif 'top_crops' in result:
        output.append(f"## Top {result.get('top_n', 10)} Crops in {result.get('state', 'N/A')}\n")
        if isinstance(result['top_crops'], pd.DataFrame):
            output.append(dataframe_to_markdown(result['top_crops']))
        else:
            output.append("*(No crop data available)*")
        output.append(f"\n*Years: {result.get('years', 'N/A')}*\n")
    elif 'districts' in result:
        output.append(f"## Crop Production by District\n")
        output.append(f"**Crop:** {result.get('crop', 'N/A')}\n")
        output.append(f"**State:** {result.get('state', 'N/A')}\n")
        output.append(f"**Year:** {result.get('year', 'N/A')}\n\n")
        if isinstance(result['districts'], pd.DataFrame):
            output.append(dataframe_to_markdown(result['districts'], index=False))
        else:
            output.append("*(No district data available)*")
    elif 'trend_analysis' in result:
        output.append(f"## Crop Production Trend Analysis\n")
        output.append(f"**Crop:** {result.get('crop', 'N/A')}\n")
        output.append(f"**State:** {result.get('state', 'N/A')}\n\n")
        
        trend = result['trend_analysis']
        if 'error' not in trend:
            output.append(f"**Trend Direction:** {trend.get('trend_direction', 'N/A')}\n")
            output.append(f"**R-squared:** {trend.get('r_squared', 0):.4f}\n")
            output.append(f"**P-value:** {trend.get('p_value', 0):.4f}\n\n")
            output.append("**Yearly Production Data:**\n")
            if isinstance(trend.get('yearly_data'), pd.DataFrame):
                output.append(dataframe_to_markdown(trend['yearly_data'], index=False))
            else:
                output.append("*(No yearly data available)*")
        else:
            output.append(f"**Error:** {trend.get('error', 'Unknown error')}\n")
    elif 'correlation' in result:
        output.append(f"## Rainfall-Production Correlation\n")
        output.append(f"**Crop:** {result.get('crop', 'N/A')}\n")
        output.append(f"**State:** {result.get('state', 'N/A')}\n\n")
        corr = result['correlation']
        output.append(f"**Average Rainfall:** {corr.get('average_rainfall_mm', 0):.2f} mm\n\n")
        output.append("**Production Data:**\n")
        if isinstance(corr.get('production_data'), pd.DataFrame):
            output.append(dataframe_to_markdown(corr['production_data'], index=False))
        else:
            output.append("*(No production data available)*")
        if 'note' in corr:
            output.append(f"\n*Note: {corr['note']}*\n")
    elif 'arguments' in result:
        output.append(f"## Crop Comparison: {result.get('crop_a', 'N/A')} vs {result.get('crop_b', 'N/A')}\n")
        output.append(f"**State:** {result.get('state', 'N/A')}\n")
        output.append(f"**Year:** {result.get('year', 'N/A')}\n\n")
        output.append("### Three Data-Backed Arguments:\n\n")
        for i, arg in enumerate(result['arguments'], 1):
            output.append(f"{i}. **{arg['argument']}**\n")
            output.append(f"   - {arg['data']}\n")
            output.append(f"   - Metric: {arg['metric']}\n\n")
        output.append("### Comparison Table:\n")
        if isinstance(result.get('comparison'), pd.DataFrame):
            output.append(dataframe_to_markdown(result['comparison'], index=False))
        else:
            output.append("*(No comparison data available)*")
        if 'note' in result:
            output.append(f"\n*{result['note']}*\n")
    elif 'average_rainfall' in result:
        output.append(f"## Average Annual Rainfall\n")
        output.append(f"**State:** {result.get('state', 'N/A')}\n")
        output.append(f"**Average Rainfall:** {result.get('average_rainfall', 0):.2f} {result.get('unit', 'mm')}\n")
        output.append(f"**Years:** {result.get('years', 'N/A')}\n")
    elif 'query_type' in result and result['query_type'] == 'district_comparison_cross_state':
        output.append(f"## District Comparison: Highest vs Lowest Production\n")
        output.append(f"**Crop:** {result.get('crop', 'N/A')}\n")
        output.append(f"**Year:** {result.get('year', 'N/A')}\n\n")
        
        # Highest district
        highest = result.get('highest_district', {})
        if 'districts' in highest and isinstance(highest['districts'], pd.DataFrame) and len(highest['districts']) > 0:
            output.append(f"### Highest Production District in {result.get('highest_state', 'N/A')}\n")
            output.append(dataframe_to_markdown(highest['districts'], index=False))
        elif 'error' in highest:
            output.append(f"### Highest Production District\n**Error:** {highest['error']}\n")
        
        output.append("\n")
        
        # Lowest district
        lowest = result.get('lowest_district', {})
        if 'districts' in lowest and isinstance(lowest['districts'], pd.DataFrame) and len(lowest['districts']) > 0:
            output.append(f"### Lowest Production District in {result.get('lowest_state', 'N/A')}\n")
            output.append(dataframe_to_markdown(lowest['districts'], index=False))
        elif 'error' in lowest:
            output.append(f"### Lowest Production District\n**Error:** {lowest['error']}\n")
    
    # Add citation
    if 'citation' in result and result['citation']:
        output.append("\n---\n")
        output.append(result['citation'])
    
    return "\n".join(output)


# Example usage and test functions
if __name__ == "__main__":
    # File paths
    nc_file = "data/RF25_ind2022_rfp25.nc"
    crop_file = "data/horizontal_crop_vertical_year_report.xls"
    
    if not os.path.exists(nc_file):
        print(f"Error: NetCDF file not found at {nc_file}")
        sys.exit(1)
    
    if not os.path.exists(crop_file):
        print(f"Error: Crop file not found at {crop_file}")
        sys.exit(1)
    
    # Initialize analyzer
    with RainfallCropAnalyzer(nc_file, crop_file) as analyzer:
        print("\n" + "="*60)
        print("Rainfall and Crop Production Analysis System")
        print("="*60 + "\n")
        
        # Example queries
        print("\n1. Getting average rainfall for Andhra Pradesh...")
        result = analyzer.query_engine.get_avg_rainfall("Andhra Pradesh")
        print(format_query_result(result))
        
        print("\n2. Comparing rainfall between two states...")
        result = analyzer.query_engine.compare_rainfall(["Andhra Pradesh", "Karnataka"])
        print(format_query_result(result))
        
        print("\n3. Getting top 10 crops in Andhra Pradesh...")
        result = analyzer.query_engine.get_top_crops("Andhra Pradesh", top_n=10)
        print(format_query_result(result))
        
        print("\n4. Analyzing crop production trends...")
        result = analyzer.query_engine.analyze_trends("Sugarcane", "Andhra Pradesh")
        print(format_query_result(result))

