"""
Tests for WeatherDataModel.
"""
import pytest
from datetime import datetime
from src.models.weather_model import WeatherDataModel


def test_create_valid_model():
    """Test creating a valid weather model."""
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
    
    assert model is not None
    assert model.location == "Toulouse"
    assert model.station_id == "24"
    assert model.temperature == 20.6
    assert model.validate() is True


def test_model_to_dict():
    """Test converting model to dictionary."""
    model = WeatherDataModel(
        location="Toulouse",
        station_id="24",
        station_name="Test Station",
        temperature=20.0,
        humidity=74.0,
        rainfall=0.0,
        timestamp=datetime.now()
    )
    
    model_dict = model.to_dict()
    
    assert isinstance(model_dict, dict)
    assert 'location' in model_dict
    assert 'station_id' in model_dict
    assert 'temperature' in model_dict
    assert model_dict['location'] == "Toulouse"


def test_model_from_dict():
    """Test creating model from dictionary."""
    data = {
        'location': 'Toulouse',
        'station_id': '24',
        'station_name': '24-station-meteo-colomiers',
        'temperature': 20.6,
        'humidity': 74,
        'rainfall': 0,
        'wind_speed': 4,
        'pressure': 99100,
        'timestamp': '2025-11-06T14:30:00+00:00'
    }
    
    model = WeatherDataModel.from_dict(data)
    
    assert model is not None
    assert model.location == 'Toulouse'
    assert model.station_id == '24'
    assert model.temperature == 20.6
    assert model.validate() is True


def test_invalid_temperature():
    """Test validation fails for invalid temperature."""
    model = WeatherDataModel(
        location="Toulouse",
        station_id="24",
        station_name="Test Station",
        temperature=150.0,  # Too high!
        humidity=74.0,
        rainfall=0.0,
        timestamp=datetime.now()
    )
    
    assert model.validate() is False


def test_invalid_humidity():
    """Test validation fails for invalid humidity."""
    model = WeatherDataModel(
        location="Toulouse",
        station_id="24",
        station_name="Test Station",
        temperature=20.0,
        humidity=150.0,  # Over 100%!
        rainfall=0.0,
        timestamp=datetime.now()
    )
    
    assert model.validate() is False


def test_negative_rainfall():
    """Test validation fails for negative rainfall."""
    model = WeatherDataModel(
        location="Toulouse",
        station_id="24",
        station_name="Test Station",
        temperature=20.0,
        humidity=74.0,
        rainfall=-5.0,  # Negative!
        timestamp=datetime.now()
    )
    
    assert model.validate() is False


def test_valid_edge_case_values():
    """Test model with edge case but valid values."""
    model = WeatherDataModel(
        location="Toulouse",
        station_id="24",
        station_name="Test Station",
        temperature=-50.0,  # Cold but valid
        humidity=0.0,       # Dry but valid
        rainfall=0.0,       # No rain, valid
        wind_speed=0.0,     # No wind, valid
        timestamp=datetime.now()
    )
    
    assert model.validate() is True


def test_model_string_representation():
    """Test that model has a string representation."""
    model = WeatherDataModel(
        location="Toulouse",
        station_id="24",
        station_name="Test Station",
        temperature=20.0,
        humidity=74.0,
        rainfall=0.0,
        timestamp=datetime.now()
    )
    
    str_repr = str(model)
    assert isinstance(str_repr, str)
    assert len(str_repr) > 0
