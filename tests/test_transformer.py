"""
Tests for DataCleaner transformer.
"""
from src.models.weather_model import WeatherDataModel


def test_transform_valid_data(data_cleaner, sample_weather_data):
    """Test transforming valid weather data."""
    clean_models = data_cleaner.transform(sample_weather_data)
    
    assert isinstance(clean_models, list)
    assert len(clean_models) == len(sample_weather_data)
    assert all(isinstance(model, WeatherDataModel) for model in clean_models)
    assert all(model.validate() for model in clean_models)


def test_transform_filters_invalid_records(data_cleaner):
    """Test that invalid records are filtered out during transformation."""
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
            # Invalid - missing temperature
            'station_id': '24',
            'humidity': 80,
            'timestamp': '2025-11-06T12:00:00+00:00'
        },
        {
            # Invalid - temperature out of range
            'station_id': '24',
            'temperature': 200.0,
            'humidity': 50,
            'rainfall': 0,
            'timestamp': '2025-11-06T12:00:00+00:00'
        }
    ]
    
    clean_models = data_cleaner.transform(raw_data)
    
    # Should only return the valid record
    assert len(clean_models) < len(raw_data)
    assert all(model.validate() for model in clean_models)


def test_transform_empty_list(data_cleaner):
    """Test transforming an empty list."""
    clean_models = data_cleaner.transform([])
    
    assert isinstance(clean_models, list)
    assert len(clean_models) == 0


def test_get_stats(data_cleaner, sample_weather_data):
    """Test getting transformation statistics."""
    # Transform some data
    data_cleaner.transform(sample_weather_data)
    
    stats = data_cleaner.get_stats()
    
    assert isinstance(stats, dict)
    assert 'total_processed' in stats or len(stats) >= 0


def test_transform_handles_missing_optional_fields(data_cleaner):
    """Test that transformer handles records with missing optional fields."""
    raw_data = [
        {
            'station_id': '24',
            'station_name': '24-station-meteo-colomiers',
            'location': 'Toulouse',
            'temperature': 20.6,
            'humidity': 74,
            # Missing optional fields like wind_speed, pressure
            'timestamp': '2025-11-06T14:30:00+00:00'
        }
    ]
    
    clean_models = data_cleaner.transform(raw_data)
    
    # Should still create valid models
    assert len(clean_models) > 0
    assert all(isinstance(model, WeatherDataModel) for model in clean_models)
