"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest
from datetime import datetime

from src.config.toulouse_config import ToulouseConfig
from src.extractors.api_extractor import APIExtractor
from src.transformers.data_cleaner import DataCleaner
from src.loaders.database_loader import DatabaseLoader
from src.models.weather_model import WeatherDataModel


@pytest.fixture
def toulouse_config():
    """Provide ToulouseConfig instance."""
    return ToulouseConfig()


@pytest.fixture
def api_extractor(toulouse_config):  # pylint: disable=redefined-outer-name
    """Provide APIExtractor instance with ToulouseConfig."""
    return APIExtractor(toulouse_config)


@pytest.fixture
def data_cleaner():
    """Provide DataCleaner instance."""
    return DataCleaner()


@pytest.fixture
def test_db_path(tmp_path):
    """Provide a temporary database path for testing."""
    return str(tmp_path / "test_weather.db")


@pytest.fixture
def database_loader(test_db_path):  # pylint: disable=redefined-outer-name
    """Provide DatabaseLoader instance with test database."""
    loader = DatabaseLoader(test_db_path)
    loader.initialize()
    return loader


@pytest.fixture
def sample_weather_data():
    """Provide sample weather data dictionaries."""
    return [
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
        }
    ]


@pytest.fixture
def sample_weather_models():
    """Provide sample WeatherDataModel instances."""
    return [
        WeatherDataModel(
            location="Toulouse",
            station_id="24",
            station_name="24-station-meteo-colomiers",
            temperature=20.6,
            humidity=74.0,
            rainfall=0.0,
            wind_speed=4.0,
            pressure=99100.0,
            timestamp=datetime.now(),
        ),
        WeatherDataModel(
            location="Toulouse",
            station_id="24",
            station_name="24-station-meteo-colomiers",
            temperature=11.7,
            humidity=93.0,
            rainfall=0.5,
            wind_speed=1.0,
            pressure=99200.0,
            timestamp=datetime.now(),
        ),
    ]
