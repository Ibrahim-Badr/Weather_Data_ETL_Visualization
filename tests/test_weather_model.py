"""
Test script for WeatherDataModel.
"""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.weather_model import WeatherDataModel


def test_valid_model():
    """Test creating a valid weather model."""
    print("="*70)
    print("Test 1: Creating a valid WeatherDataModel")
    print("="*70)
    
    model = WeatherDataModel(
        location="Toulouse",
        station_id="24",
        station_name="24-station-meteo-colomiers-zi-enjacca",
        temperature=20.6,
        humidity=74.0,
        rainfall=0.0,
        wind_speed=4.0,
        pressure=99100.0,
        timestamp=datetime.now()
    )
    
    print(f"\n✓ Model created: {model}")
    print(f"\n✓ Validation result: {model.validate()}")
    
    # Test to_dict
    print(f"\n✓ Dictionary representation:")
    print(model.to_dict())


def test_invalid_models():
    """Test validation with invalid data."""
    print("\n" + "="*70)
    print("Test 2: Testing validation with invalid data")
    print("="*70)
    
    # Invalid temperature
    invalid_temp = WeatherDataModel(
        location="Toulouse",
        station_id="24",
        station_name="Test Station",
        temperature=150.0,  # Too high!
        humidity=74.0,
        rainfall=0.0,
        timestamp=datetime.now()
    )
    print(f"\n✗ Invalid temperature (150°C): {invalid_temp.validate()}")
    
    # Invalid humidity
    invalid_humidity = WeatherDataModel(
        location="Toulouse",
        station_id="24",
        station_name="Test Station",
        temperature=20.0,
        humidity=150.0,  # Over 100%!
        rainfall=0.0,
        timestamp=datetime.now()
    )
    print(f"✗ Invalid humidity (150%): {invalid_humidity.validate()}")
    
    # Negative rainfall
    invalid_rainfall = WeatherDataModel(
        location="Toulouse",
        station_id="24",
        station_name="Test Station",
        temperature=20.0,
        humidity=74.0,
        rainfall=-5.0,  # Negative!
        timestamp=datetime.now()
    )
    print(f"✗ Negative rainfall (-5mm): {invalid_rainfall.validate()}")


def test_from_dict():
    """Test creating model from dictionary."""
    print("\n" + "="*70)
    print("Test 3: Creating model from dictionary")
    print("="*70)
    
    data = {
        'location': 'Toulouse',
        'station_id': '24',
        'station_name': '24-station-meteo-colomiers-zi-enjacca',
        'temperature': 20.6,
        'humidity': 74,
        'rainfall': 0,
        'wind_speed': 4,
        'pressure': 99100,
        'timestamp': '2025-11-06T14:30:00+00:00'
    }
    
    model = WeatherDataModel.from_dict(data)
    print(f"\n✓ Model from dict: {model}")
    print(f"✓ Is valid: {model.validate()}")


if __name__ == "__main__":
    test_valid_model()
    test_invalid_models()
    test_from_dict()
    
    print("\n" + "="*70)
    print("All model tests completed!")
    print("="*70)
