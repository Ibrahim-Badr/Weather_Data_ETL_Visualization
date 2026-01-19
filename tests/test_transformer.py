"""
Test script for DataCleaner transformer.
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.transformers.data_cleaner import DataCleaner


def test_data_cleaner():
    """Test DataCleaner with sample data."""
    print("="*70)
    print("Testing DataCleaner Transformer")
    print("="*70)
    
    # Sample raw data (like from API)
    raw_data = [
        {
            'station_id': '24',
            'station_name': '24-station-meteo-colomiers',
            'location': 'Toulouse',
            'temperature': 20.6,
            'humidity': 74,
            'rainfall': 0,
            'wind_speed': 4,
            'pressure': 99100,
            'timestamp': '2025-11-06T14:30:00+00:00'
        },
        {
            'station_id': '24',
            'station_name': '24-station-meteo-colomiers',
            'location': 'Toulouse',
            'temperature': 11.7,
            'humidity': 93,
            'rainfall': 0.5,
            'wind_speed': 1,
            'pressure': 99200,
            'timestamp': '2025-11-06T05:45:00+00:00'
        },
        {
            # Invalid record - missing temperature
            'station_id': '24',
            'humidity': 80,
            'timestamp': '2025-11-06T12:00:00+00:00'
        },
        {
            # Invalid record - temperature out of range
            'station_id': '24',
            'temperature': 200.0,  # Too high!
            'humidity': 50,
            'rainfall': 0,
            'timestamp': '2025-11-06T12:00:00+00:00'
        }
    ]
    
    # Create cleaner
    cleaner = DataCleaner()
    
    # Transform data
    clean_models = cleaner.transform(raw_data)
    
    # Display results
    print("\n✓ Cleaned models:")
    for i, model in enumerate(clean_models, 1):
        print(f"\n{i}. {model}")
    
    # Show statistics
    print("\n📊 Cleaning Statistics:")
    stats = cleaner.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    test_data_cleaner()
