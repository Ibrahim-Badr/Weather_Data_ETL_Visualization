"""
Data cleaner and transformer.
Cleans, normalizes, and validates raw weather data.
"""
from typing import List, Dict, Optional
from datetime import datetime
from .interface import IDataTransformer
from ..models.weather_model import WeatherDataModel


class DataCleaner(IDataTransformer):
    """
    Data cleaning and transformation implementation.

    Responsibilities:
    - Remove null/invalid values
    - Normalize data formats
    - Validate data quality
    - Convert to WeatherDataModel objects

    Demonstrates Single Responsibility Principle - only handles data cleaning.
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize data cleaner.

        Args:
            strict_mode: If True, rejects records with any missing optional fields
        """
        self.strict_mode = strict_mode
        self.stats = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'null_removed': 0
        }

    def transform(self, raw_data: List[Dict]) -> List[WeatherDataModel]:
        """
        Transform raw data into validated models.

        Args:
            raw_data: List of raw weather dictionaries from API

        Returns:
            List of validated WeatherDataModel objects
        """
        self.stats['total_records'] = len(raw_data)
        cleaned_models = []

        print("\n🔄 Starting data cleaning and transformation...")
        print(f"   Input: {len(raw_data)} raw records")

        for idx, record in enumerate(raw_data):
            # Step 1: Remove nulls and clean
            cleaned_record = self._remove_nulls(record)

            # Step 2: Normalize values
            normalized_record = self._normalize_values(cleaned_record)

            # Step 3: Convert to model
            model = self._to_model(normalized_record)

            # Step 4: Validate
            if model and model.validate():
                cleaned_models.append(model)
                self.stats['valid_records'] += 1
            else:
                self.stats['invalid_records'] += 1
                if idx < 3:  # Only print first 3 errors
                    print(f"   ⚠ Record {idx} rejected: invalid data")

        print(f"   Output: {len(cleaned_models)} clean records")
        print(f"   Rejected: {self.stats['invalid_records']} invalid records")
        success_rate = (len(cleaned_models)/len(raw_data)*100) if raw_data else 0
        print(f"   Success rate: {success_rate:.1f}%\n")

        return cleaned_models

    def _remove_nulls(self, record: Dict) -> Dict:
        """
        Remove null values and empty strings from record.

        Args:
            record: Raw data dictionary

        Returns:
            Dictionary with nulls removed
        """
        cleaned = {}
        for key, value in record.items():
            if value is not None and value != '':
                cleaned[key] = value
            else:
                self.stats['null_removed'] += 1

        return cleaned

    def _normalize_values(self, record: Dict) -> Dict:
        """
        Normalize and standardize data values.

        Args:
            record: Cleaned dictionary

        Returns:
            Normalized dictionary
        """
        normalized = record.copy()

        # Normalize temperature (ensure it's float)
        if 'temperature' in normalized:
            try:
                normalized['temperature'] = float(normalized['temperature'])
            except (ValueError, TypeError):
                del normalized['temperature']

        # Normalize humidity (ensure 0-100 range)
        if 'humidity' in normalized:
            try:
                humidity = float(normalized['humidity'])
                # Some APIs return humidity as 0-1, convert to 0-100
                if 0 <= humidity <= 1:
                    humidity = humidity * 100
                normalized['humidity'] = humidity
            except (ValueError, TypeError):
                del normalized['humidity']

        # Normalize rainfall (ensure non-negative)
        if 'rainfall' in normalized:
            try:
                rainfall = float(normalized['rainfall'])
                normalized['rainfall'] = max(0, rainfall)  # Cannot be negative
            except (ValueError, TypeError):
                normalized['rainfall'] = 0.0  # Default to 0

        # Normalize wind_speed
        if 'wind_speed' in normalized:
            try:
                wind_speed = float(normalized['wind_speed'])
                normalized['wind_speed'] = max(0, wind_speed)  # Cannot be negative
            except (ValueError, TypeError):
                normalized['wind_speed'] = None

        # Normalize pressure
        if 'pressure' in normalized:
            try:
                normalized['pressure'] = float(normalized['pressure'])
            except (ValueError, TypeError):
                normalized['pressure'] = None

        # Normalize timestamp
        if 'timestamp' in normalized:
            normalized['timestamp'] = self._parse_timestamp(normalized['timestamp'])

        return normalized

    def _parse_timestamp(self, timestamp) -> datetime:
        """
        Parse timestamp from various formats.

        Args:
            timestamp: Timestamp in various formats

        Returns:
            datetime object
        """
        if isinstance(timestamp, datetime):
            return timestamp

        if isinstance(timestamp, str):
            try:
                # Try ISO format (most common)
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try common date format
                    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        # Try without seconds
                        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                    except ValueError:
                        pass

        # Default to now if parsing fails
        return datetime.now()

    def _to_model(self, record: Dict) -> Optional[WeatherDataModel]:
        """
        Convert normalized dictionary to WeatherDataModel.

        Args:
            record: Normalized data dictionary

        Returns:
            WeatherDataModel instance or None if conversion fails
        """
        try:
            # Check required fields
            required_fields = ['station_id', 'temperature', 'humidity', 'timestamp']
            if not all(field in record for field in required_fields):
                return None

            # Use from_dict for robust conversion
            model = WeatherDataModel.from_dict(record)

            return model

        except (ValueError, TypeError, KeyError, AttributeError):
            # Silent fail - validation will catch it
            return None

    def get_stats(self) -> Dict:
        """
        Get cleaning statistics.

        Returns:
            Dictionary with cleaning stats
        """
        return self.stats.copy()

    def reset_stats(self):
        """Reset statistics counters."""
        self.stats = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'null_removed': 0
        }
