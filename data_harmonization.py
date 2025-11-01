

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Optional
import warnings


class StateDistrictMapper:
    """Map geographical coordinates to states and districts"""
    
    # Approximate bounding boxes for Indian states (lon_min, lon_max, lat_min, lat_max)
    STATE_BOUNDS = {
        'Andhra Pradesh': (76.0, 84.0, 12.0, 20.0),
        'Arunachal Pradesh': (91.0, 97.0, 26.0, 30.0),
        'Assam': (89.0, 96.0, 24.0, 28.0),
        'Bihar': (83.0, 88.0, 24.0, 28.0),
        'Chhattisgarh': (80.0, 85.0, 17.0, 24.0),
        'Goa': (73.5, 74.5, 14.5, 15.5),
        'Gujarat': (68.0, 75.0, 20.0, 25.0),
        'Haryana': (74.0, 78.0, 28.0, 31.0),
        'Himachal Pradesh': (75.0, 79.0, 30.0, 33.0),
        'Jharkhand': (83.0, 88.0, 22.0, 25.0),
        'Karnataka': (74.0, 78.5, 11.5, 18.5),
        'Kerala': (74.5, 77.5, 8.0, 12.5),
        'Madhya Pradesh': (73.0, 82.0, 21.0, 27.0),
        'Maharashtra': (72.0, 81.0, 15.0, 22.0),
        'Manipur': (93.0, 95.0, 23.0, 25.0),
        'Meghalaya': (89.0, 93.0, 25.0, 26.5),
        'Mizoram': (92.0, 93.5, 22.0, 24.5),
        'Nagaland': (93.0, 95.5, 25.0, 27.0),
        'Odisha': (81.0, 88.0, 17.0, 22.5),
        'Punjab': (73.5, 77.0, 29.5, 32.5),
        'Rajasthan': (69.0, 78.5, 23.0, 30.5),
        'Sikkim': (88.0, 89.0, 27.0, 28.5),
        'Tamil Nadu': (76.0, 80.5, 8.0, 13.5),
        'Telangana': (77.0, 81.0, 15.5, 20.0),
        'Tripura': (91.0, 92.5, 22.5, 24.5),
        'Uttar Pradesh': (77.0, 85.0, 24.0, 31.0),
        'Uttarakhand': (77.0, 81.0, 28.5, 31.5),
        'West Bengal': (86.0, 90.0, 21.5, 27.5),
        'Andaman and Nicobar Islands': (92.0, 94.0, 6.0, 14.0),
        'Delhi': (76.8, 77.4, 28.4, 28.9),
        'Puducherry': (79.7, 79.9, 11.8, 12.1),
        'Jammu and Kashmir': (73.0, 80.0, 32.0, 37.0),
        'Ladakh': (75.0, 80.0, 32.0, 36.0),
    }
    
    def __init__(self, lon: np.ndarray, lat: np.ndarray):
        """
        Initialize mapper with longitude and latitude arrays
        
        Args:
            lon: Longitude array from NetCDF
            lat: Latitude array from NetCDF
        """
        self.lon = lon
        self.lat = lat
        self.lon_grid, self.lat_grid = np.meshgrid(lon, lat)
    
    def get_state_bounds(self, state_name: str) -> Optional[Tuple[float, float, float, float]]:
        """
        Get bounding box for a state
        
        Args:
            state_name: Name of the state
            
        Returns:
            Tuple of (lon_min, lon_max, lat_min, lat_max) or None
        """
        # Try exact match first
        if state_name in self.STATE_BOUNDS:
            return self.STATE_BOUNDS[state_name]
        
        # Try case-insensitive match
        state_lower = state_name.lower().strip()
        for state, bounds in self.STATE_BOUNDS.items():
            if state.lower() == state_lower:
                return bounds
        
        # Try partial match
        for state, bounds in self.STATE_BOUNDS.items():
            if state_lower in state.lower() or state.lower() in state_lower:
                return bounds
        
        return None
    
    def get_grid_indices_for_state(self, state_name: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get grid cell indices for a given state
        
        Args:
            state_name: Name of the state
            
        Returns:
            Tuple of (lat_indices, lon_indices) arrays
        """
        bounds = self.get_state_bounds(state_name)
        if bounds is None:
            warnings.warn(f"State bounds not found for: {state_name}")
            return np.array([]), np.array([])
        
        lon_min, lon_max, lat_min, lat_max = bounds
        
        # Find indices within bounds
        lon_mask = (self.lon >= lon_min) & (self.lon <= lon_max)
        lat_mask = (self.lat >= lat_min) & (self.lat <= lat_max)
        
        lon_indices = np.where(lon_mask)[0]
        lat_indices = np.where(lat_mask)[0]
        
        return lat_indices, lon_indices
    
    def aggregate_rainfall_for_state(self, rainfall_data: np.ndarray, 
                                     state_name: str, 
                                     time_indices: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Aggregate rainfall data for a state
        
        Args:
            rainfall_data: Rainfall data array (time, lat, lon) or (lat, lon)
            state_name: Name of the state
            time_indices: Optional time indices to filter
            
        Returns:
            Aggregated rainfall values (mean across grid cells)
        """
        lat_indices, lon_indices = self.get_grid_indices_for_state(state_name)
        
        if len(lat_indices) == 0 or len(lon_indices) == 0:
            return np.array([])
        
        # Handle different data shapes
        if rainfall_data.ndim == 3:  # (time, lat, lon)
            if time_indices is not None:
                data_subset = rainfall_data[np.ix_(time_indices, lat_indices, lon_indices)]
            else:
                data_subset = rainfall_data[:, lat_indices, :][:, :, lon_indices]
            
            # Copy to ensure array is writable (NetCDF arrays can be read-only)
            # Use .copy() method and ensure contiguous array
            data_subset = np.ascontiguousarray(np.array(data_subset, copy=True))
            
            # Aggregate across spatial dimensions (mean of grid cells)
            aggregated = np.nanmean(data_subset, axis=(1, 2))
            # Ensure returned array is writable
            return np.array(aggregated, copy=True)
        elif rainfall_data.ndim == 2:  # (lat, lon)
            data_subset = rainfall_data[np.ix_(lat_indices, lon_indices)]
            
            # Copy to ensure array is writable (NetCDF arrays can be read-only)
            data_subset = np.ascontiguousarray(np.array(data_subset, copy=True))
            
            aggregated = np.nanmean(data_subset)
            # Return as writable array
            return np.array([aggregated], dtype=np.float64)
        else:
            raise ValueError(f"Unsupported rainfall data shape: {rainfall_data.shape}")


class TemporalHarmonizer:
    """Harmonize temporal data between rainfall and crop datasets"""
    
    def __init__(self, rainfall_years: Optional[List[int]] = None, 
                 crop_years: Optional[List[int]] = None):
        """
        Initialize temporal harmonizer
        
        Args:
            rainfall_years: Available years in rainfall data
            crop_years: Available years in crop data
        """
        self.rainfall_years = rainfall_years or []
        self.crop_years = crop_years or []
        self.common_years = self._find_common_years()
    
    def _find_common_years(self) -> List[int]:
        """Find years common to both datasets"""
        return sorted(set(self.rainfall_years) & set(self.crop_years))
    
    def get_overlapping_years(self, start_year: Optional[int] = None, 
                             end_year: Optional[int] = None) -> List[int]:
        """
        Get overlapping years within a range
        
        Args:
            start_year: Start year (inclusive)
            end_year: End year (inclusive)
            
        Returns:
            List of common years in the range
        """
        years = self.common_years
        
        if start_year:
            years = [y for y in years if y >= start_year]
        if end_year:
            years = [y for y in years if y <= end_year]
        
        return years
    
    def convert_year_to_time_index(self, year: int, 
                                   time_array: Optional[np.ndarray] = None) -> Optional[int]:
        """
        Convert year to time index in NetCDF
        
        Args:
            year: Year to convert
            time_array: Time array from NetCDF (if available)
            
        Returns:
            Time index or None if not found
        """
        if time_array is None:
            return None
        
        # Try to find matching year in time array
        # Time array might be in different formats (days since epoch, year, etc.)
        for idx, t in enumerate(time_array):
            # Try converting to year if it's a numeric value
            try:
                if isinstance(t, (int, float)):
                    # Assume time might be in years (e.g., 2022.0) or days since epoch
                    if t > 1900 and t < 2100:  # Likely a year
                        if int(t) == year:
                            return idx
            except:
                pass
        
        return None

