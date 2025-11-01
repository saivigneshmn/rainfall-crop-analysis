"""
Query Engine Module
Functions for querying and analyzing rainfall and crop data
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from scipy import stats
from data_harmonization import StateDistrictMapper, TemporalHarmonizer
import warnings


class CitationManager:
    """Manages data citations for outputs"""
    
    def __init__(self):
        self.citations = []
    
    def add_citation(self, dataset_name: str, source: str, year: Optional[str] = None, 
                    resolution: Optional[str] = None):
        """Add a citation"""
        citation = {
            'dataset': dataset_name,
            'source': source,
            'year': year,
            'resolution': resolution
        }
        self.citations.append(citation)
    
    def format_citations(self) -> str:
        """Format citations as markdown"""
        if not self.citations:
            return ""
        
        lines = ["### Data Citations", ""]
        for i, cit in enumerate(self.citations, 1):
            parts = [f"**{cit['dataset']}**"]
            if cit['source']:
                parts.append(f"Source: {cit['source']}")
            if cit['year']:
                parts.append(f"Year: {cit['year']}")
            if cit['resolution']:
                parts.append(f"Resolution: {cit['resolution']}")
            lines.append(f"{i}. " + " | ".join(parts))
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear citations"""
        self.citations = []


class QueryEngine:
    """Main query engine for rainfall and crop analysis"""
    
    def __init__(self, rainfall_loader, crop_loader, mapper: StateDistrictMapper, 
                 harmonizer: TemporalHarmonizer):
        """
        Initialize query engine
        
        Args:
            rainfall_loader: RainfallLoader instance
            crop_loader: CropDataLoader instance
            mapper: StateDistrictMapper instance
            harmonizer: TemporalHarmonizer instance
        """
        self.rainfall_loader = rainfall_loader
        self.crop_loader = crop_loader
        self.mapper = mapper
        self.harmonizer = harmonizer
        self.citation_manager = CitationManager()
    
    def get_avg_rainfall(self, state_name: str, years: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Get average annual rainfall for a state
        
        Args:
            state_name: Name of the state
            years: Optional list of years to filter
            
        Returns:
            Dictionary with results and citation
        """
        self.citation_manager.clear()
        
        # Get grid indices for state
        lat_indices, lon_indices = self.mapper.get_grid_indices_for_state(state_name)
        
        if len(lat_indices) == 0 or len(lon_indices) == 0:
            return {
                'error': f"State '{state_name}' not found or no data available",
                'average_rainfall': None,
                'years': years,
                'citation': ""
            }
        
        # Extract rainfall data for state
        rainfall_data = self.rainfall_loader.rainfall_data
        aggregated = self.mapper.aggregate_rainfall_for_state(
            rainfall_data, state_name
        )
        
        if len(aggregated) == 0:
            return {
                'error': f"No rainfall data available for {state_name}",
                'average_rainfall': None,
                'years': years,
                'citation': ""
            }
        
        # Calculate average - ensure array is writable
        aggregated = np.array(aggregated, copy=True) if not aggregated.flags.writeable else aggregated
        avg_rainfall = float(np.nanmean(aggregated))
        
        # Add citation
        metadata = self.rainfall_loader.get_metadata()
        self.citation_manager.add_citation(
            "IMD Rainfall Data",
            f"NetCDF: {metadata['filename']}",
            "2022-2023",
            metadata.get('spatial_resolution', 'Grid-based')
        )
        
        result = {
            'state': state_name,
            'average_rainfall': avg_rainfall,
            'unit': 'mm',
            'years': years or "All available",
            'citation': self.citation_manager.format_citations()
        }
        
        return result
    
    def compare_rainfall(self, state_names: List[str], years: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Compare average annual rainfall between states
        
        Args:
            state_names: List of state names to compare
            years: Optional list of years
            
        Returns:
            Dictionary with comparison results
        """
        self.citation_manager.clear()
        
        results = []
        for state in state_names:
            result = self.get_avg_rainfall(state, years)
            if 'error' not in result:
                results.append({
                    'State': state,
                    'Average Rainfall (mm)': result['average_rainfall']
                })
        
        if not results:
            return {
                'error': "Could not retrieve rainfall data for any state",
                'comparison': None,
                'citation': ""
            }
        
        df_comparison = pd.DataFrame(results)
        
        # Add citation
        metadata = self.rainfall_loader.get_metadata()
        self.citation_manager.add_citation(
            "IMD Rainfall Data",
            f"NetCDF: {metadata['filename']}",
            "2022-2023",
            metadata.get('spatial_resolution', 'Grid-based')
        )
        
        return {
            'comparison': df_comparison,
            'years': years or "All available",
            'citation': self.citation_manager.format_citations()
        }
    
    def get_top_crops(self, state_name: str, years: Optional[List[int]] = None, 
                     top_n: int = 10) -> Dict[str, Any]:
        """
        Get top N crops by production for a state
        
        Args:
            state_name: Name of the state
            years: Optional list of years to filter
            top_n: Number of top crops to return
            
        Returns:
            Dictionary with top crops and citation
        """
        self.citation_manager.clear()
        
        if self.crop_loader.df is None:
            return {
                'error': "Crop data not loaded",
                'top_crops': None,
                'citation': ""
            }
        
        # Filter by state
        df = self.crop_loader.df.copy()
        df_state = df[df['State'].str.contains(state_name, case=False, na=False)]
        
        if len(df_state) == 0:
            return {
                'error': f"No crop data found for state: {state_name}",
                'top_crops': None,
                'citation': ""
            }
        
        # Filter by years if specified
        if years:
            df_state = df_state[df_state['Year'].isin(years)]
        
        # Find all production columns
        production_cols = [c for c in df_state.columns if c.endswith('_production')]
        
        if not production_cols:
            return {
                'error': "No production data found in crop dataset",
                'top_crops': None,
                'citation': ""
            }
        
        # Aggregate production by crop
        crop_totals = []
        for col in production_cols:
            crop_name = col.replace('_production', '')
            total_production = df_state[col].sum()
            
            # Get unit from column name or metadata
            unit = 'Tonnes'  # Default
            if 'nuts' in col.lower() or 'Nuts' in col:
                unit = 'Nuts'
            elif 'bales' in col.lower() or 'Bales' in col:
                unit = 'Bales'
            
            crop_totals.append({
                'Crop': crop_name,
                'Total Production': total_production,
                'Unit': unit
            })
        
        # Sort and get top N
        crop_df = pd.DataFrame(crop_totals)
        crop_df = crop_df.sort_values('Total Production', ascending=False)
        crop_df = crop_df.head(top_n)
        crop_df = crop_df.reset_index(drop=True)
        crop_df.index = crop_df.index + 1  # Start from 1
        
        # Add citation
        metadata = self.crop_loader.get_metadata()
        years_str = f"{min(years)}-{max(years)}" if years else "All available"
        self.citation_manager.add_citation(
            "Agriculture Production Data",
            f"File: {metadata['filename']}",
            years_str,
            "District-level"
        )
        
        return {
            'state': state_name,
            'top_crops': crop_df,
            'top_n': top_n,
            'years': years or "All available",
            'citation': self.citation_manager.format_citations()
        }
    
    def get_crop_production_by_district(self, crop_name: str, state_name: Optional[str] = None,
                                       year: Optional[int] = None, 
                                       top_n: Optional[int] = None,
                                       ascending: bool = False) -> Dict[str, Any]:
        """
        Get crop production by district
        
        Args:
            crop_name: Name of the crop
            state_name: Optional state to filter
            year: Optional year to filter
            top_n: Optional number of top districts
            ascending: Sort order (False = highest first)
            
        Returns:
            Dictionary with district-level production
        """
        self.citation_manager.clear()
        
        if self.crop_loader.df is None:
            return {
                'error': "Crop data not loaded",
                'districts': None,
                'citation': ""
            }
        
        df = self.crop_loader.df.copy()
        
        # Filter by state
        if state_name:
            df = df[df['State'].str.contains(state_name, case=False, na=False)]
        
        # Filter by year
        if year:
            df = df[df['Year'] == year]
        
        # Find production column for crop - improved matching
        production_col = None
        crop_lower = crop_name.lower().strip()
        
        # Try exact match first
        for col in df.columns:
            col_lower = col.lower()
            base_col = col_lower.replace('_production', '').replace('_area', '').replace('_yield', '')
            if crop_lower == base_col and 'production' in col_lower:
                production_col = col
                break
        
        # If no exact match, try substring
        if production_col is None:
            for col in df.columns:
                col_lower = col.lower()
                if crop_lower in col_lower and 'production' in col_lower:
                    production_col = col
                    break
        
        if production_col is None:
            available = [c.replace('_production', '') for c in df.columns if '_production' in c]
            # Try to suggest similar crop names
            crop_lower = crop_name.lower()
            suggestions = [c for c in available if crop_lower in c.lower() or c.lower() in crop_lower][:3]
            error_msg = f"Crop '{crop_name}' not found in dataset."
            if suggestions:
                error_msg += f" Did you mean: {', '.join(suggestions)}?"
            else:
                error_msg += f" Available crops include: {', '.join(available[:10])}..."
            return {
                'error': error_msg,
                'districts': None,
                'citation': ""
            }
        
        # Aggregate by district
        district_data = df.groupby(['State', 'District']).agg({
            production_col: 'sum',
            'Year': 'first'
        }).reset_index()
        
        district_data = district_data.rename(columns={production_col: 'Production'})
        district_data = district_data.sort_values('Production', ascending=ascending, na_position='last')
        
        # Get unit
        unit = 'Tonnes'
        if 'nuts' in production_col.lower():
            unit = 'Nuts'
        elif 'bales' in production_col.lower():
            unit = 'Bales'
        
        district_data['Unit'] = unit
        
        if top_n:
            district_data = district_data.head(top_n)
        
        district_data = district_data.reset_index(drop=True)
        
        # Add citation
        metadata = self.crop_loader.get_metadata()
        year_str = str(year) if year else "All available"
        self.citation_manager.add_citation(
            "Agriculture Production Data",
            f"File: {metadata['filename']}",
            year_str,
            "District-level"
        )
        
        return {
            'crop': crop_name,
            'state': state_name or "All states",
            'year': year or "All years",
            'districts': district_data,
            'citation': self.citation_manager.format_citations()
        }
    
    def analyze_trends(self, crop_name: str, state_name: Optional[str] = None,
                      years: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Analyze decadal trends in crop production
        
        Args:
            crop_name: Name of the crop
            state_name: Optional state to filter
            years: Optional years to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        self.citation_manager.clear()
        
        if self.crop_loader.df is None:
            return {
                'error': "Crop data not loaded",
                'trend': None,
                'citation': ""
            }
        
        df = self.crop_loader.df.copy()
        
        # Filter by state
        if state_name:
            df = df[df['State'].str.contains(state_name, case=False, na=False)]
        
        # Filter by years
        if years:
            df = df[df['Year'].isin(years)]
        
        # Find production column - improved matching
        production_col = None
        crop_lower = crop_name.lower().strip()
        
        # Try exact match first
        for col in df.columns:
            col_lower = col.lower()
            base_col = col_lower.replace('_production', '').replace('_area', '').replace('_yield', '')
            if crop_lower == base_col and 'production' in col_lower:
                production_col = col
                break
        
        # If no exact match, try substring
        if production_col is None:
            for col in df.columns:
                col_lower = col.lower()
                if crop_lower in col_lower and 'production' in col_lower:
                    production_col = col
                    break
        
        if production_col is None:
            available = [c.replace('_production', '') for c in df.columns if '_production' in c][:10]
            return {
                'error': f"Crop '{crop_name}' not found. Available crops: {', '.join(available)}...",
                'trend': None,
                'citation': ""
            }
        
        # Aggregate by year
        yearly_data = df.groupby('Year').agg({
            production_col: 'sum'
        }).reset_index()
        yearly_data = yearly_data.sort_values('Year')
        yearly_data = yearly_data.rename(columns={production_col: 'Production'})
        
        # Calculate trend (linear regression)
        if len(yearly_data) > 1:
            x = yearly_data['Year'].values
            y = yearly_data['Production'].values
            
            # Remove NaN values
            mask = ~np.isnan(y)
            x = x[mask]
            y = y[mask]
            
            if len(x) > 1:
                # Get linregress result (returns tuple or LinregressResult, both are indexable)
                result = stats.linregress(x, y)
                # Use indexing to avoid type checker issues with tuple unpacking
                # Type checker has issues with scipy return types, but runtime values are numeric
                slope = float(result[0])  # type: ignore
                intercept = float(result[1])  # type: ignore
                r_value = float(result[2])  # type: ignore
                p_value = float(result[3])  # type: ignore
                
                trend = {
                    'slope': slope,
                    'intercept': intercept,
                    'r_squared': float(r_value ** 2),
                    'p_value': p_value,
                    'trend_direction': 'Increasing' if slope > 0 else 'Decreasing',
                    'yearly_data': yearly_data
                }
            else:
                trend = {
                    'error': "Insufficient data for trend analysis",
                    'yearly_data': yearly_data
                }
        else:
            trend = {
                'error': "Insufficient data points for trend analysis",
                'yearly_data': yearly_data
            }
        
        # Add citation
        metadata = self.crop_loader.get_metadata()
        years_str = f"{years[0]}-{years[-1]}" if years and len(years) > 1 else "All available"
        self.citation_manager.add_citation(
            "Agriculture Production Data",
            f"File: {metadata['filename']}",
            years_str,
            "District-level"
        )
        
        return {
            'crop': crop_name,
            'state': state_name or "All states",
            'trend_analysis': trend,
            'citation': self.citation_manager.format_citations()
        }
    
    def correlate_rainfall_production(self, crop_name: str, state_name: str,
                                     years: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Calculate correlation between rainfall and crop production
        
        Args:
            crop_name: Name of the crop
            state_name: Name of the state
            years: Optional years to analyze
            
        Returns:
            Dictionary with correlation results
        """
        self.citation_manager.clear()
        
        # Get rainfall data
        rainfall_result = self.get_avg_rainfall(state_name, years)
        if 'error' in rainfall_result:
            return {
                'error': f"Could not get rainfall data: {rainfall_result['error']}",
                'correlation': None,
                'citation': ""
            }
        
        # Get crop production data
        if self.crop_loader.df is None:
            return {
                'error': "Crop data not loaded",
                'correlation': None,
                'citation': ""
            }
        
        df = self.crop_loader.df.copy()
        df_state = df[df['State'].str.contains(state_name, case=False, na=False)]
        
        # Find production column - improved matching
        production_col = None
        crop_lower = crop_name.lower().strip()
        
        # Try exact match first
        for col in df_state.columns:
            col_lower = col.lower()
            base_col = col_lower.replace('_production', '').replace('_area', '').replace('_yield', '')
            if crop_lower == base_col and 'production' in col_lower:
                production_col = col
                break
        
        # If no exact match, try substring
        if production_col is None:
            for col in df_state.columns:
                col_lower = col.lower()
                if crop_lower in col_lower and 'production' in col_lower:
                    production_col = col
                    break
        
        if production_col is None:
            available = [c.replace('_production', '') for c in df_state.columns if '_production' in c][:10]
            return {
                'error': f"Crop '{crop_name}' not found. Available crops: {', '.join(available)}...",
                'correlation': None,
                'citation': ""
            }
        
        # Aggregate production by year
        if years:
            df_state = df_state[df_state['Year'].isin(years)]
        
        yearly_production = df_state.groupby('Year')[production_col].sum().reset_index()
        yearly_production = yearly_production.sort_values('Year')
        
        # For simplicity, use average rainfall for correlation
        # In a full implementation, you'd match rainfall to each year
        avg_rainfall = rainfall_result['average_rainfall']
        
        # Create correlation data
        # Note: This is a simplified correlation. Full implementation would
        # match rainfall year-by-year with production
        
        correlation_data = {
            'average_rainfall_mm': avg_rainfall,
            'production_data': yearly_production,
            'note': 'For detailed year-by-year correlation, year-specific rainfall data is needed'
        }
        
        # Add citations
        metadata_rf = self.rainfall_loader.get_metadata()
        self.citation_manager.add_citation(
            "IMD Rainfall Data",
            f"NetCDF: {metadata_rf['filename']}",
            "2022-2023",
            metadata_rf.get('spatial_resolution', 'Grid-based')
        )
        
        metadata_crop = self.crop_loader.get_metadata()
        years_str = f"{years[0]}-{years[-1]}" if years and len(years) > 1 else "All available"
        self.citation_manager.add_citation(
            "Agriculture Production Data",
            f"File: {metadata_crop['filename']}",
            years_str,
            "District-level"
        )
        
        return {
            'crop': crop_name,
            'state': state_name,
            'correlation': correlation_data,
            'citation': self.citation_manager.format_citations()
        }
    
    def compare_crops(self, crop_a: str, crop_b: str, state_name: str,
                     year: Optional[int] = None, years: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Compare two crops in a region (provide three data-backed arguments)
        
        Args:
            crop_a: First crop name
            crop_b: Second crop name
            state_name: State to compare
            year: Optional year to filter
            
        Returns:
            Dictionary with comparison arguments
        """
        self.citation_manager.clear()
        
        if self.crop_loader.df is None:
            return {
                'error': "Crop data not loaded",
                'comparison': None,
                'citation': ""
            }
        
        df = self.crop_loader.df.copy()
        df_state = df[df['State'].str.contains(state_name, case=False, na=False)]
        
        # Filter by year(s)
        if years and len(years) > 0:
            df_state = df_state[df_state['Year'].isin(years)]
        elif year:
            df_state = df_state[df_state['Year'] == year]
        
        # Find production columns - improved matching
        prod_col_a = None
        prod_col_b = None
        crop_a_lower = crop_a.lower().strip()
        crop_b_lower = crop_b.lower().strip()
        
        # Try exact match first, then substring
        for col in df_state.columns:
            col_lower = col.lower()
            if 'production' in col_lower:
                base_col = col_lower.replace('_production', '').replace('_area', '').replace('_yield', '')
                # Exact match
                if crop_a_lower == base_col and prod_col_a is None:
                    prod_col_a = col
                elif crop_a_lower in col_lower and prod_col_a is None:
                    prod_col_a = col
                    
                if crop_b_lower == base_col and prod_col_b is None:
                    prod_col_b = col
                elif crop_b_lower in col_lower and prod_col_b is None:
                    prod_col_b = col
        
        if prod_col_a is None:
            available = [c.replace('_production', '') for c in df_state.columns if '_production' in c][:5]
            return {'error': f"Crop '{crop_a}' not found. Available crops: {', '.join(available)}...", 'comparison': None, 'citation': ""}
        if prod_col_b is None:
            available = [c.replace('_production', '') for c in df_state.columns if '_production' in c][:5]
            return {'error': f"Crop '{crop_b}' not found. Available crops: {', '.join(available)}...", 'comparison': None, 'citation': ""}
        
        # Filter out null/zero rows for more meaningful comparison
        df_state_filtered = df_state[
            (df_state[prod_col_a].notna() & (df_state[prod_col_a] > 0)) |
            (df_state[prod_col_b].notna() & (df_state[prod_col_b] > 0))
        ]
        
        # If filtered dataset is empty, check if any data exists
        if len(df_state_filtered) == 0:
            # Check if crops exist but all values are 0/NaN
            has_data_a = df_state[prod_col_a].notna().any()
            has_data_b = df_state[prod_col_b].notna().any()
            
            if not has_data_a or not has_data_b:
                available_years = sorted(df_state['Year'].dropna().unique().tolist()) if 'Year' in df_state.columns else []
                return {
                    'error': f"One or both crops may not have production data for {state_name}. "
                            f"Available years in dataset: {available_years}. "
                            f"Try selecting different crops or checking data availability.",
                    'comparison': None,
                    'citation': ""
                }
        
        # Use filtered data if available, otherwise use original
        df_to_use = df_state_filtered if len(df_state_filtered) > 0 else df_state
        
        # Calculate statistics
        total_a = df_to_use[prod_col_a].sum()
        total_b = df_to_use[prod_col_b].sum()
        
        area_col_a = prod_col_a.replace('_production', '_area')
        area_col_b = prod_col_b.replace('_production', '_area')
        
        area_a = df_to_use[area_col_a].sum() if area_col_a in df_to_use.columns else None
        area_b = df_to_use[area_col_b].sum() if area_col_b in df_to_use.columns else None
        
        yield_a = None
        yield_b = None
        if area_a and area_a > 0:
            yield_a = total_a / area_a
        if area_b and area_b > 0:
            yield_b = total_b / area_b
        
        # Generate three arguments
        arguments = []
        
        # Argument 1: Production volume
        if total_a > total_b:
            arguments.append({
                'argument': f"{crop_a} has higher total production",
                'data': f"{crop_a}: {total_a:,.0f} vs {crop_b}: {total_b:,.0f}",
                'metric': 'Total Production'
            })
        else:
            arguments.append({
                'argument': f"{crop_b} has higher total production",
                'data': f"{crop_b}: {total_b:,.0f} vs {crop_a}: {total_a:,.0f}",
                'metric': 'Total Production'
            })
        
        # Argument 2: Yield efficiency
        if yield_a and yield_b:
            if yield_a > yield_b:
                arguments.append({
                    'argument': f"{crop_a} has higher yield per hectare",
                    'data': f"{crop_a}: {yield_a:.2f} vs {crop_b}: {yield_b:.2f}",
                    'metric': 'Yield (Production/Area)'
                })
            else:
                arguments.append({
                    'argument': f"{crop_b} has higher yield per hectare",
                    'data': f"{crop_b}: {yield_b:.2f} vs {crop_a}: {yield_a:.2f}",
                    'metric': 'Yield (Production/Area)'
                })
        
        # Argument 3: Geographic distribution
        districts_a = df_to_use[df_to_use[prod_col_a].notna() & (df_to_use[prod_col_a] > 0)]['District'].nunique()
        districts_b = df_to_use[df_to_use[prod_col_b].notna() & (df_to_use[prod_col_b] > 0)]['District'].nunique()
        
        if districts_a > districts_b:
            arguments.append({
                'argument': f"{crop_a} is grown in more districts",
                'data': f"{crop_a}: {districts_a} districts vs {crop_b}: {districts_b} districts",
                'metric': 'Geographic Spread'
            })
        else:
            arguments.append({
                'argument': f"{crop_b} is grown in more districts",
                'data': f"{crop_b}: {districts_b} districts vs {crop_a}: {districts_a} districts",
                'metric': 'Geographic Spread'
            })
        
        # Add citation
        metadata = self.crop_loader.get_metadata()
        year_str = str(year) if year else "All available"
        self.citation_manager.add_citation(
            "Agriculture Production Data",
            f"File: {metadata['filename']}",
            year_str,
            "District-level"
        )
        
        # Add note if all values are zero
        note = None
        if total_a == 0 and total_b == 0:
            available_years = sorted(df_state['Year'].dropna().unique().tolist()) if 'Year' in df_state.columns else []
            note = (f"Note: Both crops show zero production. Available years in dataset: {available_years}. "
                   f"This may indicate limited data availability for these crops in {state_name}.")
        
        result_dict = {
            'crop_a': crop_a,
            'crop_b': crop_b,
            'state': state_name,
            'year': year or (f"Years: {years}" if years else "All years"),
            'arguments': arguments,
            'comparison': pd.DataFrame({
                'Crop': [crop_a, crop_b],
                'Total Production': [total_a, total_b],
                'Area (Hectares)': [area_a, area_b],
                'Yield': [yield_a, yield_b],
                'Districts': [districts_a, districts_b]
            }),
            'citation': self.citation_manager.format_citations()
        }
        
        if note:
            result_dict['note'] = note
        
        return result_dict

