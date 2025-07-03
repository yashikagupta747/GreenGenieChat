import requests
from typing import List, Dict, Tuple, Optional
import re
import os
import pandas as pd
from datetime import datetime
import numpy as np
from scipy.stats import linregress

class EnvironmentalExpert:
    def __init__(self):
        # Initialize Cohere API with hardcoded API key
        self.api_url = "https://api.cohere.ai/v1/generate"
        self.api_key = "aJcTM8kNrQ31ssI5nQlsWjNIJX0RKVLybvMm4SWg"
        # Debug print to confirm API key in class
        print("API Key in EnvironmentalExpert:", self.api_key if self.api_key else "Not Set")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
        self.last_sources = []
        # Load and preprocess environmental dataset
        self.dataset = self._load_and_preprocess_data()
        # System prompt for the model - adjusted for brevity
        self.system_prompt = """You are an environmental data assistant created by me. Provide very short, factual answers (1-2 lines max) based on environmental insights, without examples or solutions unless asked."""

        # Query handlers for dataset responses
        self.dataset_queries = {
            r'co2|carbon dioxide': self._handle_co2_query,
            r'temperature|temp_anomaly|warming': self._handle_temp_query,
            r'sea level|gmsl|sea-level': self._handle_sea_level_query,
            r'forest|deforestation|vegetation': self._handle_forest_query,
            r'ocean|ph|acidification': self._handle_ocean_query,
            r'ozone': self._handle_ozone_query,
            r'precipitation|rainfall|rain': self._handle_precip_query,
            r'sea ice|arctic ice|ice extent': self._handle_seaice_query,
            r'trend|change over time|historical': self._handle_trend_query,
            r'current|latest|recent': self._handle_current_query,
            r'compare|comparison|difference': self._handle_comparison_query
        }

    def _load_and_preprocess_data(self) -> pd.DataFrame:
        """Load and preprocess the environmental dataset"""
        try:
            df = pd.read_csv('features.csv')
            # Convert year to integer and ensure numeric columns
            df['year'] = df['year'].astype(int)
            numeric_cols = ['co2', 'temp_anomaly', 'gmsl_mm', 'forest_loss_ha',
                            'forest_cover_pct', 'ocean_ph', 'ozone',
                            'precip_anomaly', 'seaice_extent']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            # Add decade column for aggregation
            df['decade'] = (df['year'] // 10) * 10
            return df
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return pd.DataFrame()

    def get_response(self, user_query: str) -> str:
        """Get response to user query, trying dataset first then Cohere model"""
        try:
            self.last_sources = []
            query = user_query.lower().strip()
            # Check for clear requests for examples/explanations
            wants_examples = any(word in query for word in ['example', 'explain', 'detail', 'elaborate'])
            wants_data = any(word in query for word in ['number', 'data', 'statistic', 'value', 'how much'])
            # First try to answer from dataset if appropriate
            if not wants_examples or wants_data:
                dataset_response = self._try_dataset_response(query)
                if dataset_response:
                    return dataset_response
            # Otherwise use the Cohere model
            return self._get_model_response(user_query, wants_examples)
        except Exception as e:
            return f"System error: {str(e)}. Please try again."

    def get_last_sources(self) -> List[str]:
        """Get sources used for last response"""
        return list(set(self.last_sources)) if self.last_sources else ['IPCC', 'NASA', 'NOAA']

    def _try_dataset_response(self, query: str) -> Optional[str]:
        """Try to answer the query from the dataset"""
        # Check for year specification
        year = self._extract_year(query)
        decade = (year // 10) * 10 if year else None
        # Check for dataset patterns
        for pattern, handler in self.dataset_queries.items():
            if re.search(pattern, query, re.IGNORECASE):
                response = handler(query, year, decade)
                if response:
                    self.last_sources.extend(['NASA', 'NOAA', 'IPCC', 'UNEP'])
                    return response
        return None

    def _extract_year(self, query: str) -> Optional[int]:
        """Extract year from query if mentioned"""
        year_match = re.search(r'(?:year|in|during|since)\s*(\d{4})', query)
        if year_match:
            try:
                return int(year_match.group(1))
            except:
                return None
        return None

    def _handle_co2_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle CO2 related queries"""
        if year and year in self.dataset['year'].values:
            co2_data = self.dataset[self.dataset['year'] == year]['co2']
            if not co2_data.empty:
                co2_level = co2_data.mean()
                return f"In {year}, average atmospheric CO₂ concentration was {co2_level:.2f} ppm."
        if decade:
            decade_data = self.dataset[self.dataset['decade'] == decade]
            if not decade_data.empty:
                avg_co2 = decade_data['co2'].mean()
                return f"During {decade}s, average CO₂ was {avg_co2:.2f} ppm."
        latest_co2 = self.dataset['co2'].iloc[-1]
        avg_co2 = self.dataset['co2'].mean()
        trend = self._calculate_trend('co2')
        return (f"Current atmospheric CO₂: {latest_co2:.2f} ppm (historical avg: {avg_co2:.2f} ppm). "
                f"Trend: Increasing by {trend:.2f} ppm/year.")

    def _handle_temp_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle temperature related queries"""
        if year and year in self.dataset['year'].values:
            temp_data = self.dataset[self.dataset['year'] == year]['temp_anomaly']
            if not temp_data.empty:
                temp = temp_data.mean()
                return f"In {year}, global temperature anomaly was {temp:.2f}°C above baseline."
        if decade:
            decade_data = self.dataset[self.dataset['decade'] == decade]
            if not decade_data.empty:
                avg_temp = decade_data['temp_anomaly'].mean()
                return f"During {decade}s, average temperature anomaly was {avg_temp:.2f}°C."
        latest_temp = self.dataset['temp_anomaly'].iloc[-1]
        trend = self._calculate_trend('temp_anomaly')
        return (f"Current global temperature anomaly: {latest_temp:.2f}°C. "
                f"Trend: Warming at {trend:.2f}°C/year.")

    def _handle_sea_level_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle sea level related queries"""
        if year and year in self.dataset['year'].values:
            level_data = self.dataset[self.dataset['year'] == year]['gmsl_mm']
            if not level_data.empty:
                level = level_data.mean()
                return f"In {year}, global mean sea level was {level:.1f} mm above baseline."
        latest_level = self.dataset['gmsl_mm'].iloc[-1]
        trend = self._calculate_trend('gmsl_mm')
        return (f"Current global mean sea level: {latest_level:.1f} mm above baseline. "
                f"Trend: Rising at {trend:.1f} mm/year.")

    def _handle_forest_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle forest/vegetation related queries"""
        if year and year in self.dataset['year'].values:
            year_data = self.dataset[self.dataset['year'] == year]
            if not year_data.empty:
                loss = year_data['forest_loss_ha'].mean()
                cover = year_data['forest_cover_pct'].mean()
                return (f"In {year}: Forest loss {loss:,.0f} ha, "
                        f"cover {cover:.1f}% of land area.")
        avg_loss = self.dataset['forest_loss_ha'].mean()
        avg_cover = self.dataset['forest_cover_pct'].mean()
        trend = self._calculate_trend('forest_cover_pct')
        return (f"Average annual forest loss: {avg_loss:,.0f} ha. "
                f"Average cover: {avg_cover:.1f}% (trend: {trend:.2f}%/year change).")

    def _handle_ocean_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle ocean acidification/ph queries"""
        if year and year in self.dataset['year'].values:
            ph_data = self.dataset[self.dataset['year'] == year]['ocean_ph']
            if not ph_data.empty:
                ph = ph_data.mean()
                return f"In {year}, average ocean pH was {ph:.3f}."
        latest_ph = self.dataset['ocean_ph'].iloc[-1]
        trend = self._calculate_trend('ocean_ph')
        return (f"Current ocean pH: {latest_ph:.3f}. "
                f"Trend: Acidifying at {abs(trend):.3f} pH units/year.")

    def _handle_ozone_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle ozone layer queries"""
        if year and year in self.dataset['year'].values:
            ozone_data = self.dataset[self.dataset['year'] == year]['ozone']
            if not ozone_data.empty:
                ozone = ozone_data.mean()
                return f"In {year}, average ozone concentration was {ozone:.1f} Dobson Units."
        latest_ozone = self.dataset['ozone'].iloc[-1]
        trend = self._calculate_trend('ozone')
        return (f"Current ozone concentration: {latest_ozone:.1f} Dobson Units. "
                f"Trend: {'Increasing' if trend > 0 else 'Decreasing'} at {abs(trend):.2f} Units/year.")

    def _handle_precip_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle precipitation queries"""
        if year and year in self.dataset['year'].values:
            precip_data = self.dataset[self.dataset['year'] == year]['precip_anomaly']
            if not precip_data.empty:
                precip = precip_data.mean()
                return f"In {year}, precipitation anomaly was {precip:.1f} mm from baseline."
        latest_precip = self.dataset['precip_anomaly'].iloc[-1]
        trend = self._calculate_trend('precip_anomaly')
        return (f"Current precipitation anomaly: {latest_precip:.1f} mm. "
                f"Trend: {'Increasing' if trend > 0 else 'Decreasing'} at {abs(trend):.2f} mm/year.")

    def _handle_seaice_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle sea ice extent queries"""
        if year and year in self.dataset['year'].values:
            ice_data = self.dataset[self.dataset['year'] == year]['seaice_extent']
            if not ice_data.empty:
                ice = ice_data.mean()
                return f"In {year}, average sea ice extent was {ice:.2f} million km²."
        latest_ice = self.dataset['seaice_extent'].iloc[-1]
        trend = self._calculate_trend('seaice_extent')
        return (f"Current sea ice extent: {latest_ice:.2f} million km². "
                f"Trend: Declining at {abs(trend):.3f} million km²/year.")

    def _handle_trend_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle trend-related queries"""
        trends = []
        columns = {
            'co2': 'CO₂ (ppm/year)',
            'temp_anomaly': 'Temperature (°C/year)',
            'gmsl_mm': 'Sea Level (mm/year)',
            'forest_cover_pct': 'Forest Cover (%/year)',
            'ocean_ph': 'Ocean pH (units/year)',
            'seaice_extent': 'Sea Ice (million km²/year)'
        }
        for col, label in columns.items():
            trend = self._calculate_trend(col)
            trends.append(f"{label}: {trend:+.3f}")
        return "Current environmental trends:\n" + "\n".join(f"• {t}" for t in trends)

    def _handle_current_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle requests for current/latest data"""
        latest = self.dataset.iloc[-1]
        return (
            f"Latest environmental data (year {latest['year']}):\n"
            f"• CO₂: {latest['co2']:.2f} ppm\n"
            f"• Temp anomaly: {latest['temp_anomaly']:.2f}°C\n"
            f"• Sea level: {latest['gmsl_mm']:.1f} mm\n"
            f"• Forest cover: {latest['forest_cover_pct']:.1f}%\n"
            f"• Ocean pH: {latest['ocean_ph']:.3f}"
        )

    def _handle_comparison_query(self, query: str, year: Optional[int], decade: Optional[int]) -> str:
        """Handle comparison queries between years/periods"""
        year_matches = re.findall(r'\d{4}', query)
        if len(year_matches) >= 2:
            try:
                year1, year2 = map(int, year_matches[:2])
                data1 = self.dataset[self.dataset['year'] == year1].iloc[0]
                data2 = self.dataset[self.dataset['year'] == year2].iloc[0]
                comparisons = []
                for col in ['co2', 'temp_anomaly', 'gmsl_mm', 'forest_cover_pct']:
                    val1 = data1[col]
                    val2 = data2[col]
                    change = ((val2 - val1)/val1 * 100) if val1 != 0 else 0
                    comparisons.append(
                        f"{col.replace('_', ' ').title()}: {val1:.2f} → {val2:.2f} ({change:+.1f}%)"
                    )
                return f"Comparison {year1} vs {year2}:\n" + "\n".join(f"• {c}" for c in comparisons)
            except:
                pass
        # Default comparison: first vs last year in dataset
        first = self.dataset.iloc[0]
        latest = self.dataset.iloc[-1]
        years = latest['year'] - first['year']
        comparisons = []
        for col in ['co2', 'temp_anomaly', 'gmsl_mm']:
            change = (latest[col] - first[col])/years
            comparisons.append(
                f"{col.replace('_', ' ').title()}: {change:+.2f}/year"
            )
        return f"Long-term trends ({first['year']}-{latest['year']}):\n" + "\n".join(f"• {c}" for c in comparisons)

    def _calculate_trend(self, column: str) -> float:
        """Calculate linear trend for a dataset column using linear regression"""
        x = np.arange(len(self.dataset))
        y = self.dataset[column].values
        slope, _, _, _, _ = linregress(x, y)
        return slope

    def _get_model_response(self, user_query: str, wants_examples: bool = False) -> str:
        """Get response from Cohere model with appropriate context"""
        try:
            if not self.api_key:
                return "Cohere API key is not set. Please ensure the key is correctly defined in the code."
            prompt = self._enhance_query(user_query, wants_examples)
            formatted_prompt = self._format_prompt(prompt)
            payload = {
                "model": "command",  # Cohere's default model for text generation
                "prompt": formatted_prompt,
                "max_tokens": 50,  # Reduced to ensure short responses (1-2 lines)
                "temperature": 0.3,  # Lower temperature for factual, concise answers
                "k": 0,
                "p": 0.75,
                "stop_sequences": ["\n\n"],  # Stop at double newline to keep responses short
                "return_likelihoods": "NONE"
            }
            print("Sending request to Cohere API with payload:", payload)
            print("Headers being sent:", {"Authorization": "REDACTED" if self.api_key else "Not Set", "Content-Type": "application/json"})
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            response_data = response.json()
            print("Received response from Cohere API:", response_data)
            if response_data and 'generations' in response_data and len(response_data['generations']) > 0 and 'text' in response_data['generations'][0]:
                return self._process_response(response_data['generations'][0]['text'], wants_examples)
            elif response_data and 'message' in response_data:
                return f"API Error: {response_data['message']}. Please try again later."
            else:
                return "Received unexpected response format from Cohere API. Please try again later."
        except requests.exceptions.RequestException as e:
            return f"Unable to access Cohere API. Error: {str(e)}. As a fallback, I can only answer questions directly related to the environmental dataset for now."
        except Exception as e:
            return f"Analysis error: {str(e)}. Please try again."

    def _enhance_query(self, query: str, wants_examples: bool) -> str:
        """Add context to the query based on keywords and user needs, keeping it minimal"""
        context = []
        if wants_examples:
            context.append("Include brief examples or details only if relevant.")
        # Avoid adding extra context unless explicitly needed
        if context:
            return f"{query} {' '.join(context)}"
        return query

    def _format_prompt(self, user_input: str) -> str:
        """Format the prompt for the model with system instructions"""
        return f"""System: {self.system_prompt}
User: {user_input}
Assistant:"""

    def _process_response(self, text: str, is_detailed: bool) -> str:
        """Clean up and format the model response to ensure brevity and completeness"""
        text = text.strip()
        # Limit to first 1-2 sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        # Join the first two sentences, or just the first if that's all there is
        if len(sentences) >= 2:
            result = '. '.join(sentences[:2]) + '.'
        elif sentences:
            result = sentences[0] + '.'
        else:
            result = text

        # Remove incomplete trailing phrases (like "such as:", "including:", etc.)
        incomplete_phrases = [':', 'such as:', 'including:', 'for example:', 'like:']
        for phrase in incomplete_phrases:
            if result.lower().endswith(phrase):
                result = result[: -len(phrase)].rstrip('. ') + '.'

        # If after trimming, result is empty, use a fallback
        if not result.strip() or len(result.strip()) < 10:
            result = "Climate change is mainly caused by human activities that increase greenhouse gases."

        return result

