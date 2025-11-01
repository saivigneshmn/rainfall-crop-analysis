

import netCDF4
import pandas as pd
from bs4 import BeautifulSoup, Tag
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import numpy as np


class RainfallLoader:
    """Load and process NetCDF rainfall data"""
    
    def __init__(self, nc_file_path: str):
        """
        Initialize rainfall data loader
        
        Args:
            nc_file_path: Path to NetCDF file
        """
        self.nc_file_path = nc_file_path
        self.dataset: Optional[Any] = None
        self.rainfall_data: Optional[np.ndarray] = None
        self.lon: Optional[np.ndarray] = None
        self.lat: Optional[np.ndarray] = None
        self.time: Optional[Any] = None
        self.time_dates: Optional[Any] = None  # Converted dates from time variable
        self.years: List[int] = []  # Extracted years
        
    def load(self):
        """Load NetCDF dataset"""
        if not os.path.exists(self.nc_file_path):
            raise FileNotFoundError(f"NetCDF file not found: {self.nc_file_path}")
        
        self.dataset = netCDF4.Dataset(self.nc_file_path, 'r')  # type: ignore
        
        # Extract variables
        if 'RAINFALL' in self.dataset.variables:  # type: ignore
            self.rainfall_data = self.dataset.variables['RAINFALL'][:]  # type: ignore
        elif 'rainfall' in self.dataset.variables:  # type: ignore
            self.rainfall_data = self.dataset.variables['rainfall'][:]  # type: ignore
        else:
            # Try to find rainfall variable
            var_names = list(self.dataset.variables.keys())  # type: ignore
            rainfall_var = [v for v in var_names if 'rain' in v.lower() or 'rfp' in v.lower()]  # type: ignore
            if rainfall_var:
                self.rainfall_data = self.dataset.variables[rainfall_var[0]][:]  # type: ignore
            else:
                raise ValueError("Rainfall variable not found in NetCDF file")
        
        # Extract coordinates
        if 'LONGITUDE' in self.dataset.variables:  # type: ignore
            self.lon = self.dataset.variables['LONGITUDE'][:]  # type: ignore
        elif 'lon' in self.dataset.variables:  # type: ignore
            self.lon = self.dataset.variables['lon'][:]  # type: ignore
        else:
            raise ValueError("Longitude variable not found")
            
        if 'LATITUDE' in self.dataset.variables:  # type: ignore
            self.lat = self.dataset.variables['LATITUDE'][:]  # type: ignore
        elif 'lat' in self.dataset.variables:  # type: ignore
            self.lat = self.dataset.variables['lat'][:]  # type: ignore
        else:
            raise ValueError("Latitude variable not found")
            
        if 'TIME' in self.dataset.variables:  # type: ignore
            time_var = self.dataset.variables['TIME']  # type: ignore
            self.time = time_var[:]  # type: ignore
        elif 'time' in self.dataset.variables:  # type: ignore
            time_var = self.dataset.variables['time']  # type: ignore
            self.time = time_var[:]  # type: ignore
        else:
            time_var = None
        
        # Convert time to dates and extract years
        if self.time is not None and time_var is not None:
            try:
                # Get time units (e.g., "days since 1900-12-31")
                time_units = getattr(time_var, 'units', 'days since 1900-12-31')  # type: ignore
                
                # Parse reference date
                if 'since' in time_units.lower():
                    ref_date_str = time_units.lower().split('since')[-1].strip()
                    # Try to parse reference date
                    try:
                        ref_date = datetime.strptime(ref_date_str, '%Y-%m-%d')
                    except ValueError:
                        try:
                            ref_date = datetime.strptime(ref_date_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            # Default to 1900-12-31 if parsing fails
                            ref_date = datetime(1900, 12, 31)
                    
                    # Convert time values to dates
                    time_values = np.array(self.time)  # type: ignore
                    self.time_dates = [ref_date + timedelta(days=float(d)) for d in time_values]
                    
                    # Extract unique years
                    self.years = sorted(list(set([d.year for d in self.time_dates])))
                else:
                    # If units don't match expected format, try to infer from filename
                    # File name contains "2022", so assume year is 2022
                    if '2022' in os.path.basename(self.nc_file_path):
                        self.years = [2022]
                    
            except Exception as e:
                print(f"Warning: Could not parse time variable: {e}")
                # Try to infer year from filename
                if '2022' in os.path.basename(self.nc_file_path):
                    self.years = [2022]
        
        print(f"Loaded rainfall data: shape {self.rainfall_data.shape}")  # type: ignore
        print(f"Longitude range: {self.lon.min():.2f} to {self.lon.max():.2f}")  # type: ignore
        print(f"Latitude range: {self.lat.min():.2f} to {self.lat.max():.2f}")  # type: ignore
        if self.years:
            print(f"Years available in rainfall data: {self.years}")
        
    def close(self):
        """Close NetCDF dataset"""
        if self.dataset:
            self.dataset.close()  # type: ignore
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the rainfall dataset"""
        return {
            'filename': os.path.basename(self.nc_file_path),
            'spatial_resolution': f"{len(self.lon)} x {len(self.lat)} grid cells" if self.lon is not None and self.lat is not None else "Unknown",  # type: ignore
            'longitude_range': (float(self.lon.min()), float(self.lon.max())) if self.lon is not None else None,  # type: ignore
            'latitude_range': (float(self.lat.min()), float(self.lat.max())) if self.lat is not None else None,  # type: ignore
            'time_steps': len(self.time) if self.time is not None else None,  # type: ignore
            'data_shape': self.rainfall_data.shape if self.rainfall_data is not None else None,  # type: ignore
            'years': self.years  # Available years in the dataset
        }


class CropDataLoader:
    """Load and process crop production data from HTML/Excel file"""
    
    def __init__(self, crop_file_path: str):
        """
        Initialize crop data loader
        
        Args:
            crop_file_path: Path to crop production file
        """
        self.crop_file_path = crop_file_path
        self.df = None
        
    def load(self) -> Optional[pd.DataFrame]:
        """
        Load crop production data from HTML/Excel file
        Returns a pandas DataFrame
        """
        if not os.path.exists(self.crop_file_path):
            raise FileNotFoundError(f"Crop data file not found: {self.crop_file_path}")
        
        # Try to read as HTML first
        try:
            with open(self.crop_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            table = soup.find('table', {'id': 'apyreport'})
            
            if table and isinstance(table, Tag):
                # Extract headers - find the row with crop names (has colspan="3" for crops)
                header_rows = table.find_all('tr')[:5]  # Check first 5 rows
                
                # Find row with crop names (has multiple th with colspan="3")
                crops = []
                crop_name_row = None
                for row in header_rows:
                    ths = row.find_all('th')
                    # Check if this row has crop names (has colspan="3" and text is not Area/Production/Yield)
                    has_crop_names = False
                    temp_crops = []
                    for th in ths:
                        colspan = th.get('colspan', '')
                        text = th.get_text(strip=True)
                        # Crop names have colspan="3" and are not standard labels
                        if colspan == '3' and text and text not in ['Whole Year', 'Area (Hectare)', 
                                                                     'Production (Tonnes)', 'Production (Nuts)', 
                                                                     'Production (Bales)', 'Yield (Tonne/Hectare)', 
                                                                     'Yield (Nuts/Hectare)', 'Yield (Bales/Hectare)']:
                            if text not in temp_crops:
                                temp_crops.append(text)
                                has_crop_names = True
                    
                    if has_crop_names and len(temp_crops) > 5:  # Should have many crops
                        crops = temp_crops
                        crop_name_row = row
                        break
                
                # If not found above, try alternative: look for row with many colspan="3" elements
                if not crops:
                    for row in header_rows:
                        ths = row.find_all('th', {'colspan': '3'})
                        if len(ths) > 10:  # Should have many crop columns
                            for th in ths:
                                text = th.get_text(strip=True)
                                if text and text not in ['Whole Year']:
                                    crops.append(text)
                            break
                
                print(f"Found {len(crops)} crops: {crops[:10]}...") if crops else print("Warning: Could not extract crop names")
                
                # Parse data rows - handle rowspan properly
                rows_data = []
                tbody = table.find('tbody')
                if tbody and isinstance(tbody, Tag):
                    rows = tbody.find_all('tr')
                    
                    current_state = None
                    current_district = None
                    state_rowspan_remaining = 0
                    district_rowspan_remaining = 0
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 2:
                            continue
                        
                        # Process cells - handle rowspan: state/district only appear when rowspan expires
                        state_text_new = None
                        district_text_new = None
                        year_text_new = None
                        
                        # Cell 0: Either State (if state_rowspan expired) or District
                        # Cell 1: Either District (if cell 0 was state) or Year
                        # Cell 2: Either Year or first data cell
                        
                        if len(cells) > 0:
                            cell0 = cells[0].get_text(strip=True)
                            # If state_rowspan expired, cell 0 is a new state
                            if state_rowspan_remaining == 0 and cell0 and '.' in cell0:
                                parts = cell0.split('. ', 1)
                                if len(parts) == 2 and parts[0].strip().isdigit():
                                    state_text_new = parts[1].strip()
                                    if state_text_new:
                                        current_state = state_text_new
                                        state_rowspan_remaining = int(cells[0].get('rowspan', 1)) - 1
                                    # If we got a state, next cell is district
                                    if len(cells) > 1:
                                        cell1 = cells[1].get_text(strip=True)
                                        if cell1 and '.' in cell1:
                                            parts = cell1.split('. ', 1)
                                            if len(parts) == 2 and parts[0].strip().isdigit():
                                                district_text_new = parts[1].strip()
                                                if district_text_new:
                                                    current_district = district_text_new
                                                    district_rowspan_remaining = int(cells[1].get('rowspan', 1)) - 1
                                        elif ' - ' in cell1:
                                            year_text_new = cell1
                                    # Year might be in cell 2 if we have state and district
                                    if year_text_new is None and len(cells) > 2:
                                        cell2 = cells[2].get_text(strip=True)
                                        if ' - ' in cell2:
                                            year_text_new = cell2
                                else:
                                    # Cell 0 is actually a district (state continues)
                                    if '.' in cell0:
                                        parts = cell0.split('. ', 1)
                                        if len(parts) == 2:
                                            district_text_new = parts[1].strip()
                                        else:
                                            district_text_new = None
                                    else:
                                        district_text_new = None
                                    if district_text_new:
                                        current_district = district_text_new
                                        district_rowspan_remaining = int(cells[0].get('rowspan', 1)) - 1
                                    # Year is in cell 1
                                    if len(cells) > 1:
                                        cell1 = cells[1].get_text(strip=True)
                                        if ' - ' in cell1:
                                            year_text_new = cell1
                            else:
                                # State continues, cell 0 is district
                                if cell0 and '.' in cell0:
                                    parts = cell0.split('. ', 1)
                                    if len(parts) == 2 and parts[0].strip().isdigit():
                                        district_text_new = parts[1].strip()
                                        if district_text_new:
                                            current_district = district_text_new
                                            district_rowspan_remaining = int(cells[0].get('rowspan', 1)) - 1
                                # Year is in cell 1
                                if len(cells) > 1:
                                    cell1 = cells[1].get_text(strip=True)
                                    if ' - ' in cell1:
                                        year_text_new = cell1
                        
                        # Update rowspan counters (decrement for existing rowspans)
                        if state_rowspan_remaining > 0:
                            state_rowspan_remaining -= 1
                        if district_rowspan_remaining > 0:
                            district_rowspan_remaining -= 1
                        
                        # Extract year(s) - handle ranges like "2022 - 2023"
                        years = []
                        if year_text_new:
                            if ' - ' in year_text_new:
                                # Extract both start and end year from range
                                parts = year_text_new.split(' - ')
                                start_year = parts[0].strip()
                                end_year = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                                try:
                                    start_yr = int(start_year)
                                    end_yr = int(end_year)
                                    # Create records for all years in range (inclusive)
                                    years = list(range(start_yr, end_yr + 1))
                                except ValueError:
                                    # If conversion fails, just use start year
                                    years = [start_year]
                            else:
                                years = [year_text_new.strip()]
                        
                        # Extract crop data - skip state/district/year columns
                        crop_data = {}
                        data_cells = []
                        
                        # Count how many metadata columns we have
                        skip_cols = 0
                        if state_text_new:  # New state means we had state column
                            skip_cols += 1
                        if district_text_new or current_district:  # Always have district
                            skip_cols += 1
                        if year_text_new:  # Always have year
                            skip_cols += 1
                        
                        # Get all cells after metadata
                        for i, cell in enumerate(cells):
                            if i >= skip_cols:
                                data_cells.append(cell.get_text(strip=True))
                        
                        if len(crops) > 0 and len(data_cells) >= len(crops) * 3:
                            # Group data cells by crop (3 cells per crop: Area, Production, Yield)
                            for crop_idx, crop_name in enumerate(crops):
                                i = crop_idx * 3
                                if i + 2 < len(data_cells):
                                    try:
                                        area = self._parse_number(data_cells[i])
                                        production = self._parse_number(data_cells[i+1])
                                        yield_val = self._parse_number(data_cells[i+2])
                                        
                                        # Only add if at least one value is not None
                                        if area is not None or production is not None or yield_val is not None:
                                            crop_data[f'{crop_name}_area'] = area
                                            crop_data[f'{crop_name}_production'] = production
                                            crop_data[f'{crop_name}_yield'] = yield_val
                                    except (IndexError, ValueError, TypeError) as e:
                                        # Skip this crop if parsing fails
                                        pass
                        
                        # Add row(s) for each year in the range
                        if current_state and current_district and years:
                            # Check if we have any non-None crop data
                            has_data = any(v is not None for v in crop_data.values())
                            if has_data:
                                for year in years:
                                    row_dict = {
                                        'State': current_state,
                                        'District': current_district,
                                        'Year': year,
                                        **crop_data
                                    }
                                    rows_data.append(row_dict)
                
                self.df = pd.DataFrame(rows_data)
                print(f"Loaded {len(self.df)} crop production records")
                
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            # Fallback to Excel/CSV reading
            try:
                if self.crop_file_path.endswith('.xls') or self.crop_file_path.endswith('.xlsx'):
                    self.df = pd.read_excel(self.crop_file_path)
                else:
                    self.df = pd.read_csv(self.crop_file_path)
                print(f"Loaded {len(self.df)} records using pandas")
            except Exception as e2:
                raise ValueError(f"Could not parse file: {e2}")
        
        # Clean and standardize column names
        if self.df is not None:
            # Ensure State, District, Year columns exist
            if 'State' not in self.df.columns:
                # Try to find similar column
                state_cols = [c for c in self.df.columns if 'state' in c.lower()]
                if state_cols:
                    self.df['State'] = self.df[state_cols[0]]
            
            if 'District' not in self.df.columns:
                district_cols = [c for c in self.df.columns if 'district' in c.lower()]
                if district_cols:
                    self.df['District'] = self.df[district_cols[0]]
            
            if 'Year' not in self.df.columns:
                year_cols = [c for c in self.df.columns if 'year' in c.lower()]
                if year_cols:
                    self.df['Year'] = self.df[year_cols[0]]
            
            # Clean state and district names
            if 'State' in self.df.columns:
                self.df['State'] = self.df['State'].astype(str).str.replace(r'^\d+\.\s*', '', regex=True)
            if 'District' in self.df.columns:
                self.df['District'] = self.df['District'].astype(str).str.replace(r'^\d+\.\s*', '', regex=True)
            
            # Convert Year to numeric where possible
            if 'Year' in self.df.columns:
                self.df['Year'] = pd.to_numeric(self.df['Year'], errors='coerce')
        
        return self.df
    
    def _parse_number(self, text: str) -> Optional[float]:
        """Parse number from text, handling commas and empty strings"""
        if not text or text.strip() == '':
            return None
        try:
            # Remove commas and convert to float
            text = text.replace(',', '').strip()
            return float(text) if text else None
        except (ValueError, AttributeError):
            return None
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the crop dataset"""
        if self.df is None:
            return {}
        
        return {
            'filename': os.path.basename(self.crop_file_path),
            'total_records': len(self.df),
            'states': sorted(self.df['State'].unique().tolist()) if 'State' in self.df.columns else [],
            'districts': len(self.df['District'].unique()) if 'District' in self.df.columns else 0,
            'years': sorted(self.df['Year'].dropna().unique().tolist()) if 'Year' in self.df.columns else [],
            'crops': [c.replace('_area', '').replace('_production', '').replace('_yield', '') 
                     for c in self.df.columns if c.endswith('_area')],
        }

