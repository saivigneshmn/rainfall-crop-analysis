
import re
from typing import Dict, List, Optional, Any
from query_engine import QueryEngine


class NLQueryParser:
    """Parse natural language questions and map to query functions"""
    
    def __init__(self, query_engine: QueryEngine):
        """
        Initialize parser with query engine
        
        Args:
            query_engine: QueryEngine instance
        """
        self.query_engine = query_engine
        
        # Patterns for different question types
        self.patterns = {
            'single_rainfall': [
                r'what.*is.*average.*annual.*rainfall.*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'what.*is.*average.*rainfall.*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'average.*annual.*rainfall.*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'average.*rainfall.*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            ],
            'compare_rainfall': [
                r'compare.*average.*annual.*rainfall.*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+and\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'compare.*rainfall.*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+and\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'rainfall.*comparison.*between\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+and\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'compare.*average.*rainfall.*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+and\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            ],
            'top_crops': [
                r'top\s+(\d+).*crop[s]?\s+in\s+([^,?]+)',
                r'most\s+produced\s+crop[s]?\s+in\s+([^,?]+)',
                r'list.*top\s+(\d+).*crop[s]?\s+in\s+([^,?]+)',
            ],
            'district_production': [
                r'identify.*district.*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+with.*highest.*production.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'what.*is.*highest.*production.*district.*for\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'highest.*production.*district.*for\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'district.*with.*highest.*production.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'district.*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+with.*highest.*production.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'highest.*production.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'lowest.*production.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            ],
            'trend_analysis': [
                r'analyze.*trend.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'analyze.*production.*trend.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'trend.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'production.*trend.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'decade.*trend.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'decadal.*trend.*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            ],
            'correlation': [
                r'correlate.*trend.*with.*climate.*data',
                r'correlate.*production.*with.*climate.*data',
                r'correlate.*(\w+).*with.*rainfall.*in\s+([^,?]+)',
                r'correlate.*(\w+).*with.*climate.*data',
                r'relationship.*between.*(\w+).*and.*climate.*in\s+([^,?]+)',
            ],
            'crop_comparison': [
                r'promote\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+over\s+([A-Za-z]+(?:\s+[A-Za-z]+)*).*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'arguments.*for\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+vs\s+([A-Za-z]+(?:\s+[A-Za-z]+)*).*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'compare\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+and\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+vs\s+([A-Za-z]+(?:\s+[A-Za-z]+)*).*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            ],
        }
    
    def parse(self, question: str) -> Dict[str, Any]:
        """
        Parse natural language question and return query parameters
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with parsed parameters and suggested function call
        """
        question_lower = question.lower().strip()
        question_original = question.strip()
        
        # Extract years if mentioned
        years = self._extract_years(question)
        
        # Try to match patterns
        result: Dict[str, Any] = {
            'original_question': question,
            'parsed': False,
            'query_type': None,
            'parameters': {},
            'function_suggestion': None,
            'error': None
        }
        
        # Check for single state rainfall queries (before comparison)
        for pattern in self.patterns['single_rainfall']:
            match = re.search(pattern, question_original, re.IGNORECASE)
            if match:
                state = match.group(1).strip()
                # Clean up - remove common trailing words
                words = state.split()
                while words and words[-1].lower() in ['the', 'for', 'in', 'of', 'and', 'most', 'recent', 'year', 'available', 'last', 'available']:
                    words = words[:-1]
                state_clean = ' '.join(words) if words else state
                
                result.update({
                    'parsed': True,
                    'query_type': 'single_rainfall',
                    'parameters': {
                        'state_name': state_clean,
                        'years': years
                    },
                    'function_suggestion': f"query_engine.get_avg_rainfall('{state_clean}', years={years})"
                })
                return result
        
        # Check for rainfall comparison
        # Use original question for better state name preservation
        for pattern in self.patterns['compare_rainfall']:
            match = re.search(pattern, question_original, re.IGNORECASE)
            if match:
                states = [s.strip() for s in match.groups()]
                # Clean up - remove common trailing words
                cleaned_states: List[str] = []
                for state in states:
                    # Remove common trailing words
                    words = state.split()
                    while words and words[-1].lower() in ['the', 'for', 'in', 'of', 'and']:
                        words = words[:-1]
                    if words:
                        cleaned_states.append(' '.join(words))
                    else:
                        cleaned_states.append(state)
                
                result.update({
                    'parsed': True,
                    'query_type': 'compare_rainfall',
                    'parameters': {
                        'state_names': cleaned_states,
                        'years': years
                    },
                    'function_suggestion': f"query_engine.compare_rainfall({cleaned_states}, years={years})"
                })
                return result
        
        # Check for top crops
        for pattern in self.patterns['top_crops']:
            match = re.search(pattern, question_lower, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    top_n = int(groups[0]) if groups[0].isdigit() else 10
                    state = groups[1].strip()
                    result.update({
                        'parsed': True,
                        'query_type': 'top_crops',
                        'parameters': {
                            'state_name': state,
                            'top_n': top_n,
                            'years': years
                        },
                        'function_suggestion': f"query_engine.get_top_crops('{state}', years={years}, top_n={top_n})"
                    })
                    return result
        
        # Check for cross-state district comparison (e.g., highest in State1 vs lowest in State2)
        # Pattern: "identify district in State1 with highest production of Crop... compare... lowest production of Crop in State2"
        cross_state_match = re.search(
            r'identify.*district.*in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+with.*highest.*production.*of\s+([A-Za-z]+)\s+[^.]*compare.*lowest.*production.*of\s+([A-Za-z]+)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            question_original, re.IGNORECASE
        )
        if not cross_state_match:
            # Try simpler pattern - extract crop name and both states separately
            # "highest production of Crop in State1... compare... lowest production of Crop in State2"
            crop_match = re.search(r'(?:highest|district.*with.*highest).*production.*of\s+([A-Za-z]+)', question_original, re.IGNORECASE)
            state1_match = re.search(r'highest.*production.*of\s+[A-Za-z]+\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)', question_original, re.IGNORECASE)
            state2_match = re.search(r'lowest.*production.*of\s+[A-Za-z]+\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)', question_original, re.IGNORECASE)
            
            if crop_match and state1_match and state2_match:
                crop = crop_match.group(1).strip()
                state1 = state1_match.group(1).strip()
                state2 = state2_match.group(1).strip()
                
                # Clean state names
                state1_clean = state1.split()
                state2_clean = state2.split()
                stop_words = ['the', 'for', 'in', 'of', 'and', 'most', 'recent', 'year', 'available']
                while state1_clean and state1_clean[-1].lower() in stop_words:
                    state1_clean = state1_clean[:-1]
                while state2_clean and state2_clean[-1].lower() in stop_words:
                    state2_clean = state2_clean[:-1]
                state1 = ' '.join(state1_clean) if state1_clean else state1
                state2 = ' '.join(state2_clean) if state2_clean else state2
                
                # Clean crop name
                crop_clean = crop.split()
                indian_states = ['Andhra Pradesh', 'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Kerala']
                crop_final = []
                for word in crop_clean:
                    is_state = any(word.lower() in s.lower() for s in indian_states)
                    if not is_state:
                        crop_final.append(word)
                crop = ' '.join(crop_final) if crop_final else crop_clean[0] if crop_clean else crop
                
                result.update({
                    'parsed': True,
                    'query_type': 'district_comparison_cross_state',
                    'parameters': {
                        'crop_name': crop,
                        'state1': state1,
                        'state2': state2,
                        'highest_state': state1,
                        'lowest_state': state2
                    }
                })
                return result
        
        if cross_state_match:
            # This is a cross-state comparison
            groups = cross_state_match.groups()
            if len(groups) >= 4:
                # Pattern has: state1, crop1, crop2, state2
                state1 = groups[0].strip()
                crop = groups[1].strip()  # Use first crop mention
                state2 = groups[3].strip()
            elif len(groups) == 3:
                # Alternative: crop, state1, state2
                crop = groups[0].strip()
                state1 = groups[1].strip()
                state2 = groups[2].strip()
            
            # Clean state names
            state1_clean = state1.split()
            state2_clean = state2.split()
            stop_words = ['the', 'for', 'in', 'of', 'and', 'most', 'recent', 'year', 'available', 'and']
            while state1_clean and state1_clean[-1].lower() in stop_words:
                state1_clean = state1_clean[:-1]
            while state2_clean and state2_clean[-1].lower() in stop_words:
                state2_clean = state2_clean[:-1]
            state1 = ' '.join(state1_clean) if state1_clean else state1
            state2 = ' '.join(state2_clean) if state2_clean else state2
            
            # Clean crop name - remove any trailing state name
            crop_clean = crop.split()
            indian_states = ['Andhra Pradesh', 'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Kerala']
            crop_final = []
            for word in crop_clean:
                is_state = any(word.lower() in s.lower() for s in indian_states)
                if not is_state:
                    crop_final.append(word)
            crop = ' '.join(crop_final) if crop_final else crop_clean[0] if crop_clean else crop
            
            result.update({
                'parsed': True,
                'query_type': 'district_comparison_cross_state',
                'parameters': {
                    'crop_name': crop,
                    'state1': state1,
                    'state2': state2,
                    'highest_state': state1,
                    'lowest_state': state2
                }
            })
            return result
        
        # Check for district production - use original question (single state)
        for idx, pattern in enumerate(self.patterns['district_production']):
            match = re.search(pattern, question_original, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    # First pattern has "identify district in State with production of Crop" - state first, crop second
                    if idx == 0:
                        location = groups[0].strip()
                        crop = groups[1].strip()
                        # Clean crop name - might have trailing text like "in Karnataka"
                        crop_words = crop.split()
                        if len(crop_words) > 1 and crop_words[-1].lower() in ['in', 'and']:
                            crop = crop_words[0]  # Just take first word as crop name
                    else:
                        # For other patterns, crop is usually first, state second
                        crop = groups[0].strip()
                        location = groups[1].strip()
                    
                    # Clean up state name - remove trailing words
                    location_words = location.split()
                    stop_words = ['the', 'for', 'in', 'of', 'and', 'most', 'recent', 'year', 'available']
                    while location_words and location_words[-1].lower() in stop_words:
                        location_words = location_words[:-1]
                    location = ' '.join(location_words) if location_words else location
                    
                    # Clean crop name - remove state name if accidentally captured
                    crop_words = crop.split()
                    indian_states = ['Andhra Pradesh', 'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Kerala', 
                                    'Punjab', 'Gujarat', 'West Bengal', 'Rajasthan', 'Uttar Pradesh',
                                    'Madhya Pradesh', 'Bihar', 'Odisha', 'Telangana', 'Assam']
                    # If crop name contains a state name, remove it
                    crop_clean = []
                    for word in crop_words:
                        is_state = False
                        for state in indian_states:
                            if word.lower() in state.lower():
                                is_state = True
                                break
                        if not is_state:
                            crop_clean.append(word)
                    crop = ' '.join(crop_clean) if crop_clean else crop
                    
                    # Determine if highest or lowest
                    ascending = 'lowest' in question_lower
                    
                    result.update({
                        'parsed': True,
                        'query_type': 'district_production',
                        'parameters': {
                            'crop_name': crop,
                            'state_name': location,
                            'ascending': ascending,
                            'top_n': 1
                        },
                        'function_suggestion': f"query_engine.get_crop_production_by_district('{crop}', state_name='{location}', ascending={ascending}, top_n=1)"
                    })
                    return result
        
        # Check for trend analysis - use original question
        for pattern in self.patterns['trend_analysis']:
            match = re.search(pattern, question_original, re.IGNORECASE)
            if match:
                groups = match.groups()
                crop = groups[0].strip()
                state = groups[1].strip() if len(groups) > 1 else None
                
                # Clean up state name if present - remove trailing phrases
                if state:
                    state_words = state.split()
                    # Remove common trailing phrases
                    stop_words = ['the', 'for', 'in', 'of', 'and', 'over', 'last', 'decade', 'period', 'same', 'during']
                    while state_words and state_words[-1].lower() in stop_words:
                        state_words = state_words[:-1]
                    # Also remove if it starts with "over" or "during"
                    while state_words and state_words[0].lower() in stop_words:
                        state_words = state_words[1:]
                    state = ' '.join(state_words) if state_words else state
                
                result.update({
                    'parsed': True,
                    'query_type': 'trend_analysis',
                    'parameters': {
                        'crop_name': crop,
                        'state_name': state,
                        'years': years
                    },
                    'function_suggestion': f"query_engine.analyze_trends('{crop}', state_name='{state}', years={years})"
                })
                return result
        
        # Check for correlation
        for pattern in self.patterns['correlation']:
            match = re.search(pattern, question_lower, re.IGNORECASE)
            if match:
                groups = match.groups()
                crop = groups[0].strip()
                state = groups[1].strip()
                result.update({
                    'parsed': True,
                    'query_type': 'correlation',
                    'parameters': {
                        'crop_name': crop,
                        'state_name': state,
                        'years': years
                    },
                    'function_suggestion': f"query_engine.correlate_rainfall_production('{crop}', '{state}', years={years})"
                })
                return result
        
        # Check for crop comparison - use original question to preserve case
        for pattern in self.patterns['crop_comparison']:
            match = re.search(pattern, question_original, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    crop_a = groups[0].strip()
                    crop_b = groups[1].strip()
                    state = groups[2].strip()
                    
                    # Clean up state name - remove trailing phrases
                    state_words = state.split()
                    stop_words = ['the', 'for', 'in', 'of', 'and', 'based', 'on', 'historical', 'data', 'from']
                    while state_words and state_words[-1].lower() in stop_words:
                        state_words = state_words[:-1]
                    state = ' '.join(state_words) if state_words else state
                    
                    result.update({
                        'parsed': True,
                        'query_type': 'crop_comparison',
                        'parameters': {
                            'crop_a': crop_a,
                            'crop_b': crop_b,
                            'state_name': state,
                            'year': years[0] if years and len(years) > 0 else None,
                            'years': years
                        },
                        'function_suggestion': f"query_engine.compare_crops('{crop_a}', '{crop_b}', '{state}', years={years})"
                    })
                    return result
        
        # If no pattern matched, return suggestion to use specific functions
        result['error'] = "Could not automatically parse question. Please use specific query functions."
        result['suggested_functions'] = [
            "compare_rainfall(state_names, years)",
            "get_top_crops(state_name, years, top_n)",
            "get_crop_production_by_district(crop_name, state_name, year, ascending, top_n)",
            "analyze_trends(crop_name, state_name, years)",
            "correlate_rainfall_production(crop_name, state_name, years)",
            "compare_crops(crop_a, crop_b, state_name, year)"
        ]
        
        return result
    
    def _extract_years(self, text: str) -> Optional[List[int]]:
        """Extract years mentioned in text"""
        # Look for year ranges
        range_pattern = r'(\d{4})\s*[-–]\s*(\d{4})'
        match = re.search(range_pattern, text)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            return list(range(start, end + 1))
        
        # Look for "last N years" (with optional words like "available" in between)
        last_n_pattern = r'last\s+(\d+)\s+(?:available\s+)?year[s]?'
        match = re.search(last_n_pattern, text.lower())
        if match:
            n = int(match.group(1))
            # Get most recent N years from available data
            if hasattr(self.query_engine.crop_loader, 'df') and self.query_engine.crop_loader.df is not None:  # type: ignore
                if 'Year' in self.query_engine.crop_loader.df.columns:  # type: ignore
                    all_years = sorted(self.query_engine.crop_loader.df['Year'].dropna().unique().astype(int).tolist())  # type: ignore
                    return all_years[-n:] if len(all_years) >= n else all_years
            return None
        
        # Look for individual years
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        if years:
            return [int(y) for y in years]
        
        return None
    
    def _normalize_state_capture(self, captured_state: str) -> str:
        """
        Normalize captured state name to standard format
        
        Args:
            captured_state: State name as captured by regex
            
        Returns:
            Standardized state name
        """
        captured = captured_state.strip()
        # Remove extra whitespace and normalize
        captured_normalized = re.sub(r'\s+', '', captured.lower())
        
        # Map all known variations to standard names
        state_mapping = {
            'tamilnadu': 'Tamil Nadu',
            'westbengal': 'West Bengal',
            'madhyapradesh': 'Madhya Pradesh',
            'andhrapradesh': 'Andhra Pradesh',
            'uttarpradesh': 'Uttar Pradesh',
            'karnataka': 'Karnataka',
            'maharashtra': 'Maharashtra',
            'kerala': 'Kerala',
            'punjab': 'Punjab',
            'gujarat': 'Gujarat',
            'rajasthan': 'Rajasthan',
            'bihar': 'Bihar',
            'odisha': 'Odisha',
            'telangana': 'Telangana',
            'assam': 'Assam',
        }
        
        if captured_normalized in state_mapping:
            return state_mapping[captured_normalized]
        
        # If no mapping found, try to match by checking against known states
        standard_states = [
            'Andhra Pradesh', 'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Kerala',
            'Punjab', 'Gujarat', 'West Bengal', 'Rajasthan', 'Uttar Pradesh',
            'Madhya Pradesh', 'Bihar', 'Odisha', 'Telangana', 'Assam'
        ]
        
        for state in standard_states:
            if re.sub(r'\s+', '', state.lower()) == captured_normalized:
                return state
        
        # Last resort: return capitalized version with proper spacing
        return captured.title()
    
    def execute_query(self, question: str) -> Dict[str, Any]:
        """
        Parse question and execute corresponding query
        Handles multi-part questions (e.g., rainfall comparison + top crops)
        
        Args:
            question: Natural language question
            
        Returns:
            Query result dictionary
        """
        # Check for combined trend + correlation questions
        if ('trend' in question.lower() or 'analyze' in question.lower()) and 'correlate' in question.lower():
            return self._execute_trend_correlation_query(question)
        
        # Check for multi-part questions
        if self._is_multi_part_question(question):
            return self._execute_multi_part_query(question)
        
        parsed = self.parse(question)
        
        if not parsed['parsed']:
            return {
                'error': parsed.get('error', 'Could not parse question'),
                'parsed_info': parsed,
                'result': None
            }
        
        try:
            query_type = parsed['query_type']
            params = parsed['parameters']
            
            if query_type == 'single_rainfall':
                result = self.query_engine.get_avg_rainfall(
                    params['state_name'],
                    params.get('years')
                )
            elif query_type == 'compare_rainfall':
                result = self.query_engine.compare_rainfall(
                    params['state_names'],
                    params.get('years')
                )
            elif query_type == 'top_crops':
                result = self.query_engine.get_top_crops(
                    params['state_name'],
                    params.get('years'),
                    params.get('top_n', 10)
                )
            elif query_type == 'district_comparison_cross_state':
                # Handle cross-state district comparison
                # Get most recent year
                year = None
                if hasattr(self.query_engine.crop_loader, 'df') and self.query_engine.crop_loader.df is not None:  # type: ignore
                    if 'Year' in self.query_engine.crop_loader.df.columns:  # type: ignore
                        year = int(self.query_engine.crop_loader.df['Year'].max())  # type: ignore
                
                # Get highest in state1
                highest_result = self.query_engine.get_crop_production_by_district(
                    params['crop_name'],
                    params['state1'],
                    year,
                    1,
                    False  # ascending=False for highest
                )
                
                # Get lowest in state2
                lowest_result = self.query_engine.get_crop_production_by_district(
                    params['crop_name'],
                    params['state2'],
                    year,
                    1,
                    True  # ascending=True for lowest
                )
                
                # Combine results
                result = {
                    'query_type': 'district_comparison_cross_state',
                    'crop': params['crop_name'],
                    'highest_state': params['state1'],
                    'lowest_state': params['state2'],
                    'year': year or "Most recent",
                    'highest_district': highest_result,
                    'lowest_district': lowest_result,
                    'citation': highest_result.get('citation', '') + '\n' + lowest_result.get('citation', '')
                }
            elif query_type == 'district_production':
                # Handle "most recent year"
                year = params.get('year')
                if year is None and 'most recent' in question.lower():
                    # Get most recent year from crop data
                    if hasattr(self.query_engine.crop_loader, 'df') and self.query_engine.crop_loader.df is not None:  # type: ignore
                        if 'Year' in self.query_engine.crop_loader.df.columns:  # type: ignore
                            year = int(self.query_engine.crop_loader.df['Year'].max())  # type: ignore
                            params['year'] = year
                
                result = self.query_engine.get_crop_production_by_district(
                    params['crop_name'],
                    params.get('state_name'),
                    params.get('year'),
                    params.get('top_n', 10),
                    params.get('ascending', False)
                )
            elif query_type == 'trend_analysis':
                result = self.query_engine.analyze_trends(
                    params['crop_name'],
                    params.get('state_name'),
                    params.get('years')
                )
            elif query_type == 'correlation':
                result = self.query_engine.correlate_rainfall_production(
                    params['crop_name'],
                    params['state_name'],
                    params.get('years')
                )
            elif query_type == 'crop_comparison':
                # Extract years if mentioned (e.g., "last 3 years")
                years_param = params.get('years')
                year_param = params.get('year')
                
                # If "last N years" is mentioned, calculate years
                years_to_use = None
                if years_param:
                    years_to_use = years_param
                elif 'last' in question.lower() and any(char.isdigit() for char in question):
                    # Try to extract "last N years"
                    last_n_match = re.search(r'last\s+(\d+)\s+year', question.lower())
                    if last_n_match:
                        n = int(last_n_match.group(1))
                        if hasattr(self.query_engine.crop_loader, 'df') and self.query_engine.crop_loader.df is not None:  # type: ignore
                            if 'Year' in self.query_engine.crop_loader.df.columns:  # type: ignore
                                all_years = sorted(self.query_engine.crop_loader.df['Year'].dropna().unique().astype(int).tolist())  # type: ignore
                                years_to_use = all_years[-n:] if len(all_years) >= n else all_years
                
                result = self.query_engine.compare_crops(
                    params['crop_a'],
                    params['crop_b'],
                    params['state_name'],
                    year_param,
                    years_to_use
                )
            else:
                result = {'error': f'Unknown query type: {query_type}'}
            
            return {
                'parsed_info': parsed,
                'result': result
            }
            
        except Exception as e:
            return {
                'error': f"Error executing query: {str(e)}",
                'parsed_info': parsed,
                'result': None
            }
    
    def _is_multi_part_question(self, question: str) -> bool:
        """Check if question has multiple parts (e.g., rainfall + crops)"""
        lower_q = question.lower()
        has_rainfall = any(word in lower_q for word in ['rainfall', 'precipitation', 'climate'])
        has_crops = any(word in lower_q for word in ['crop', 'production', 'agriculture'])
        has_parallel = 'parallel' in lower_q or 'in parallel' in lower_q or 'also' in lower_q
        has_list = 'list' in lower_q and has_crops
        
        # Only treat as multi-part if explicitly asking for multiple things
        # Simple rainfall comparison should NOT be multi-part
        return (has_rainfall and has_crops and has_parallel) or (has_list and has_rainfall)
    
    def _execute_multi_part_query(self, question: str) -> Dict[str, Any]:
        """Execute queries with multiple parts"""
        results: Dict[str, Any] = {}
        errors: List[str] = []
        
        # Extract years if mentioned
        years = self._extract_years(question)
        
        # Extract states mentioned - better pattern to avoid capturing phrases
        # Match common Indian state names
        indian_states = [
            'Andhra Pradesh', 'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Kerala',
            'Punjab', 'Gujarat', 'West Bengal', 'Rajasthan', 'Uttar Pradesh',
            'Madhya Pradesh', 'Bihar', 'Odisha', 'Telangana', 'Assam'
        ]
        states = []
        for state_name in indian_states:
            # Normalize state name for matching (handle both spaced and non-spaced variants)
            normalized_state = state_name.lower().replace(' ', '')
            normalized_question = question.lower().replace(' ', '')
            if normalized_state in normalized_question:
                states.append(state_name)
        
        # Normalize state names for regex matching
        def normalize_state_name(state: str) -> str:
            """Normalize state name to handle spaces"""
            return state.replace(' ', r'\s*')
        
        # Build state pattern once for use in all regex patterns
        states_pattern = '|'.join([normalize_state_name(s) for s in indian_states])
        
        # Try to parse rainfall comparison part
        if 'rainfall' in question.lower() or 'precipitation' in question.lower():
            # Look for "compare rainfall in State_X and State_Y"
            rf_match = re.search(rf'rainfall.*in\s+({states_pattern})\s+and\s+({states_pattern})', question, re.IGNORECASE)
            if rf_match:
                state1, state2 = rf_match.groups()
                # Clean up captured state names to use standard format
                state1 = self._normalize_state_capture(state1)
                state2 = self._normalize_state_capture(state2)
                try:
                    rf_result = self.query_engine.compare_rainfall([state1, state2], years)
                    results['rainfall_comparison'] = rf_result
                except Exception as e:
                    errors.append(f"Rainfall comparison error: {str(e)}")
        
        # Try to parse top crops part
        if 'top' in question.lower() and 'crop' in question.lower():
            # Look for "top M crops in State_X and State_Y" or "in each of those states"
            # Use same state pattern as rainfall comparison for consistency
            top_match = re.search(rf'top\s+(\d+).*crop.*in\s+({states_pattern})(?:\s+and\s+({states_pattern}))?', question, re.IGNORECASE)
            if top_match:
                top_n = int(top_match.group(1))
                state1 = self._normalize_state_capture(top_match.group(2).strip())
                state2 = self._normalize_state_capture(top_match.group(3).strip()) if top_match.group(3) else None
                
                # If "each of those states" is mentioned, use states from rainfall comparison
                if 'each of those states' in question.lower() or 'each state' in question.lower():
                    # Extract states from rainfall comparison part
                    rf_states = []
                    if 'rainfall_comparison' in results:
                        # Use normalized states that were already extracted earlier
                        rf_states = states[:2] if states else []
                    
                    if rf_states:
                        # Get top crops for each state mentioned in rainfall comparison
                        for state in rf_states[:2]:
                            try:
                                crops_result = self.query_engine.get_top_crops(state, years=years, top_n=top_n)
                                results[f'top_crops_{state.replace(" ", "_")}'] = crops_result
                            except Exception as e:
                                errors.append(f"Top crops for {state} error: {str(e)}")
                    else:
                        # Fallback to states found earlier
                        for state in states[:2]:
                            try:
                                crops_result = self.query_engine.get_top_crops(state, years=years, top_n=top_n)
                                results[f'top_crops_{state.replace(" ", "_")}'] = crops_result
                            except Exception as e:
                                errors.append(f"Top crops for {state} error: {str(e)}")
                else:
                    # Explicit state names provided
                    try:
                        if state1:
                            crops_result = self.query_engine.get_top_crops(state1, years=years, top_n=top_n)
                            results[f'top_crops_{state1.replace(" ", "_")}'] = crops_result
                        if state2:
                            crops_result = self.query_engine.get_top_crops(state2, years=years, top_n=top_n)
                            results[f'top_crops_{state2.replace(" ", "_")}'] = crops_result
                    except Exception as e:
                        errors.append(f"Top crops error: {str(e)}")
            elif states:
                # Default to top 10 if no number specified
                for state in states[:2]:  # Limit to first 2 states
                    # Clean state name
                    state_clean = state.strip()
                    for word in ['during', 'the', 'same', 'period', 'each', 'of', 'those', 'states']:
                        if state_clean.lower().endswith(' ' + word):
                            state_clean = state_clean.rsplit(' ' + word, 1)[0].strip()
                    if state_clean:
                        try:
                            crops_result = self.query_engine.get_top_crops(state_clean, years=years, top_n=10)
                            results[f'top_crops_{state_clean.replace(" ", "_")}'] = crops_result
                        except Exception as e:
                            errors.append(f"Top crops for {state_clean} error: {str(e)}")
        
        return {
            'parsed_info': {
                'original_question': question,
                'query_type': 'multi_part',
                'parts_executed': list(results.keys())
            },
            'result': results if results else None,
            'errors': errors if errors else None
        }
    
    def _execute_trend_correlation_query(self, question: str) -> Dict[str, Any]:
        """Execute combined trend analysis and correlation query"""
        results: Dict[str, Any] = {}
        errors: List[str] = []
        
        # Extract crop and state from question
        # Pattern: "Analyze production trend of Crop in State"
        trend_match = re.search(r'(?:analyze|production.*trend).*of\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)', question, re.IGNORECASE)
        if trend_match:
            crop = trend_match.group(1).strip()
            state = trend_match.group(2).strip()
            
            # Clean state name
            state_words = state.split()
            stop_words = ['the', 'for', 'in', 'of', 'and', 'over', 'last', 'decade', 'period', 'same', 'during']
            while state_words and state_words[-1].lower() in stop_words:
                state_words = state_words[:-1]
            state = ' '.join(state_words) if state_words else state
            
            # Execute trend analysis
            try:
                trend_result = self.query_engine.analyze_trends(crop, state)
                results['trend_analysis'] = trend_result
            except Exception as e:
                errors.append(f"Trend analysis error: {str(e)}")
            
            # Execute correlation
            try:
                corr_result = self.query_engine.correlate_rainfall_production(crop, state)
                results['correlation'] = corr_result
            except Exception as e:
                errors.append(f"Correlation error: {str(e)}")
        
        return {
            'parsed_info': {
                'original_question': question,
                'query_type': 'trend_correlation',
                'parts_executed': list(results.keys())
            },
            'result': results if results else None,
            'errors': errors if errors else None
        }

