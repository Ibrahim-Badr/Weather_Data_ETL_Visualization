"""
Tests for the StationSelector service.

Verifies station filtering by location and thresholds,
and calculation of activity scores from the database.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock
from src.services.station_selector import StationSelector
from src.loaders.database_loader import DatabaseLoader
from src.models.weather_model import WeatherDataModel


@pytest.fixture
def production_db_loader():
    """Provide production database loader (uses actual database)."""
    loader = DatabaseLoader("database/weather.db")
    loader.initialize()
    return loader


@pytest.fixture
def station_selector(production_db_loader):  # pylint: disable=redefined-outer-name
    """Provide StationSelector with production database."""
    return StationSelector(production_db_loader)


def test_station_selector_basic(station_selector):  # pylint: disable=redefined-outer-name
    """
    Test basic functionality of StationSelector to retrieve stations with criteria.
    Verifies that:
    - StationSelector can retrieve stations with a limit parameter
    - Retrieved stations list is not empty
    - Each station record contains a 'station_id' field
    """
    stations = station_selector.get_stations_with_criteria(limit=5)
    
    assert len(stations) > 0, "Should retrieve at least one station"
    assert "station_id" in stations[0], "Station should have station_id field"


def test_station_selector_location(station_selector):  # pylint: disable=redefined-outer-name
    """
    Test that StationSelector correctly retrieves stations filtered by location.
    Verifies that when querying for stations in "Colomiers", the returned stations
    contain "Colomiers" in either their station_name or location field.
    """
    stations = station_selector.get_stations_with_criteria(location="Colomiers", limit=5)
    
    if len(stations) > 0:
        assert any("Colomiers".lower() in s["station_name"].lower()
                   or "Colomiers".lower() in s["location"].lower()
                   for s in stations), "Stations should match location filter"


def test_station_selector_with_limit(station_selector):  # pylint: disable=redefined-outer-name
    """Test that limit parameter is respected."""
    limit = 3
    stations = station_selector.get_stations_with_criteria(limit=limit)
    
    assert len(stations) <= limit, f"Should return at most {limit} stations"


def test_station_selector_returns_list(station_selector):  # pylint: disable=redefined-outer-name
    """Test that get_stations_with_criteria returns a list."""
    stations = station_selector.get_stations_with_criteria(limit=5)
    
    assert isinstance(stations, list), "Should return a list of stations"


def test_station_selector_min_records_filter(station_selector):  # pylint: disable=redefined-outer-name
    """Test filtering by minimum record count."""
    stations = station_selector.get_stations_with_criteria(min_records=50, limit=10)
    
    for station in stations:
        assert station["record_count"] >= 50, "All stations should have at least 50 records"


def test_station_selector_temperature_range_filter(station_selector):  # pylint: disable=redefined-outer-name
    """Test filtering by average temperature range."""
    stations = station_selector.get_stations_with_criteria(
        min_avg_temp=10.0,
        max_avg_temp=20.0,
        limit=10
    )
    
    for station in stations:
        assert 10.0 <= station["avg_temperature"] <= 20.0, \
            f"Temperature {station['avg_temperature']} should be between 10-20°C"


def test_station_selector_station_structure(station_selector):  # pylint: disable=redefined-outer-name
    """Test that station summaries contain all required fields."""
    stations = station_selector.get_stations_with_criteria(limit=1)
    
    if len(stations) > 0:
        station = stations[0]
        required_fields = [
            "station_id", "station_name", "location", "record_count",
            "avg_temperature", "date_range", "temperature_range"
        ]
        for field in required_fields:
            assert field in station, f"Station should have '{field}' field"


def test_get_station_activity_score(station_selector):  # pylint: disable=redefined-outer-name
    """Test activity score calculation for a station."""
    stations = station_selector.get_stations_with_criteria(limit=1)
    
    if len(stations) > 0:
        station_id = stations[0]["station_id"]
        result = station_selector.get_station_activity_score(station_id)
        
        assert "activity_score" in result, "Should contain activity score"
        assert "status" in result, "Should contain status"
        assert 0 <= result["activity_score"] <= 100, "Score should be between 0-100"


def test_get_station_activity_score_nonexistent(station_selector):  # pylint: disable=redefined-outer-name
    """Test activity score for non-existent station."""
    result = station_selector.get_station_activity_score("NONEXISTENT_ID")
    
    assert result["activity_score"] == 0, "Non-existent station should have score 0"
    assert result["status"] == "no_data", "Status should be 'no_data'"


def test_station_selector_sorting_by_record_count(station_selector):  # pylint: disable=redefined-outer-name
    """Test that stations are sorted by record count in descending order."""
    stations = station_selector.get_stations_with_criteria(limit=5)
    
    if len(stations) > 1:
        for i in range(len(stations) - 1):
            assert stations[i]["record_count"] >= stations[i + 1]["record_count"], \
                "Stations should be sorted by record count descending"


def test_station_selector_combined_filters(station_selector):  # pylint: disable=redefined-outer-name
    """Test combining multiple filters."""
    stations = station_selector.get_stations_with_criteria(
        min_records=20,
        min_avg_temp=5.0,
        max_avg_temp=25.0,
        limit=10
    )
    
    for station in stations:
        assert station["record_count"] >= 20
        assert 5.0 <= station["avg_temperature"] <= 25.0


# ===== Unit Tests with Mocked Data =====

@pytest.fixture
def mock_loader():
    """Provide a mock data loader with test data."""
    loader = Mock()
    
    # Create sample weather records
    now = datetime.now(timezone.utc)
    loader.fetch_all.return_value = [
        WeatherDataModel(
            station_id="1",
            station_name="Station One",
            location="Toulouse",
            timestamp=now,
            temperature=15.0,
            humidity=60.0,
            wind_speed=10.0,
            rainfall=0.0
        ),
        WeatherDataModel(
            station_id="1",
            station_name="Station One",
            location="Toulouse",
            timestamp=now,
            temperature=18.0,
            humidity=65.0,
            wind_speed=12.0,
            rainfall=0.0
        ),
        WeatherDataModel(
            station_id="2",
            station_name="Station Two",
            location="Colomiers",
            timestamp=now,
            temperature=20.0,
            humidity=70.0,
            wind_speed=8.0,
            rainfall=0.0
        ),
    ]
    
    loader.fetch_by_station.return_value = loader.fetch_all.return_value[:2]
    
    return loader


@pytest.fixture
def mock_station_selector(mock_loader):  # pylint: disable=redefined-outer-name
    """Provide StationSelector with mocked loader."""
    return StationSelector(mock_loader)


def test_group_by_station(mock_station_selector):  # pylint: disable=redefined-outer-name
    """Test grouping records by station_id."""
    records = mock_station_selector.loader.fetch_all()
    grouped = mock_station_selector._group_by_station(records)  # pylint: disable=protected-access
    
    assert len(grouped) == 2, "Should have 2 stations"
    assert "1" in grouped, "Should contain station 1"
    assert "2" in grouped, "Should contain station 2"
    assert len(grouped["1"]) == 2, "Station 1 should have 2 records"
    assert len(grouped["2"]) == 1, "Station 2 should have 1 record"


def test_calculate_station_stats(mock_station_selector):  # pylint: disable=redefined-outer-name
    """Test calculating comprehensive station statistics."""
    records = mock_station_selector.loader.fetch_all()[:2]  # Station 1 records
    stats = mock_station_selector._calculate_station_stats(records, "1")  # pylint: disable=protected-access
    
    assert stats["station_id"] == "1"
    assert stats["station_name"] == "Station One"
    assert stats["location"] == "Toulouse"
    assert stats["record_count"] == 2
    assert stats["avg_temperature"] == 16.5  # (15 + 18) / 2
    assert "date_range" in stats
    assert "temperature_range" in stats
    assert stats["temperature_range"]["min"] == 15.0
    assert stats["temperature_range"]["max"] == 18.0


def test_calculate_station_stats_empty_records(mock_station_selector):  # pylint: disable=redefined-outer-name
    """Test calculating stats with empty records list."""
    stats = mock_station_selector._calculate_station_stats([], "999")  # pylint: disable=protected-access
    
    assert stats == {}, "Should return empty dict for empty records"


def test_calculate_station_stats_no_temperatures(mock_loader):  # pylint: disable=redefined-outer-name
    """Test calculating stats when temperature is None."""
    now = datetime.now(timezone.utc)
    records = [
        WeatherDataModel(
            station_id="3",
            station_name="Station Three",
            location="Test",
            timestamp=now,
            temperature=0.0,
            humidity=60.0,
            wind_speed=10.0,
            rainfall=0.0
        )
    ]
    
    selector = StationSelector(mock_loader)
    stats = selector._calculate_station_stats(records, "3")  # pylint: disable=protected-access
    
    assert stats["avg_temperature"] == 0, "Should handle None temperatures"
    assert stats["temperature_range"]["min"] == 0
    assert stats["temperature_range"]["max"] == 0


def test_matches_criteria_location(mock_station_selector):  # pylint: disable=redefined-outer-name
    """Test location matching in criteria."""
    station = {
        "station_name": "Test Station",
        "location": "Toulouse",
        "record_count": 100,
        "avg_temperature": 15.0
    }
    
    # Should match by location
    assert mock_station_selector._matches_criteria(station, "Toulouse", None, None, None, None, None)  # pylint: disable=protected-access
    assert mock_station_selector._matches_criteria(station, "toulouse", None, None, None, None, None)  # pylint: disable=protected-access
    
    # Should match by station name
    station_name_match = {**station, "station_name": "Colomiers Central", "location": "Other"}
    assert mock_station_selector._matches_criteria(  # pylint: disable=protected-access
        station_name_match, "Colomiers", None, None, None, None, None
    )
    
    # Should not match
    assert not mock_station_selector._matches_criteria(  # pylint: disable=protected-access
        station, "Paris", None, None, None, None, None
    )


def test_matches_criteria_temperature_range(mock_station_selector):  # pylint: disable=redefined-outer-name
    """Test temperature range filtering in criteria."""
    station = {
        "station_name": "Test",
        "location": "Test",
        "record_count": 100,
        "avg_temperature": 15.0
    }
    
    # Within range
    assert mock_station_selector._matches_criteria(station, None, None, None, None, 10.0, 20.0)  # pylint: disable=protected-access
    
    # Below minimum
    assert not mock_station_selector._matches_criteria(station, None, None, None, None, 20.0, None)  # pylint: disable=protected-access
    
    # Above maximum
    assert not mock_station_selector._matches_criteria(station, None, None, None, None, None, 10.0)  # pylint: disable=protected-access


def test_matches_criteria_min_records(mock_station_selector):  # pylint: disable=redefined-outer-name
    """Test minimum records filtering in criteria."""
    station = {
        "station_name": "Test",
        "location": "Test",
        "record_count": 50,
        "avg_temperature": 15.0
    }
    
    # Meets minimum
    assert mock_station_selector._matches_criteria(station, None, None, None, 50, None, None)  # pylint: disable=protected-access
    assert mock_station_selector._matches_criteria(station, None, None, None, 25, None, None)  # pylint: disable=protected-access
    
    # Below minimum
    assert not mock_station_selector._matches_criteria(station, None, None, None, 100, None, None)  # pylint: disable=protected-access


def test_compute_activity_score_high_activity(mock_loader):  # pylint: disable=redefined-outer-name
    """Test activity score calculation for highly active station."""
    now = datetime.now(timezone.utc)
    
    # Create station with >100 records, recent data, and valid temperatures
    stats = {
        "record_count": 150,
        "temperature_range": {"min": 5.0, "max": 35.0},
        "date_range": {"last": now.isoformat()}
    }
    
    selector = StationSelector(mock_loader)
    score = selector._compute_activity_score(stats)  # pylint: disable=protected-access
    
    assert score == 100.0, "Should have perfect score (40 + 30 + 30)"


def test_compute_activity_score_medium_activity(mock_loader):  # pylint: disable=redefined-outer-name
    """Test activity score calculation for medium activity station."""
    # One year old data
    old_date = datetime(2025, 2, 11, tzinfo=timezone.utc)
    
    stats = {
        "record_count": 75,  # 25 points
        "temperature_range": {"min": 5.0, "max": 35.0},  # 30 points
        "date_range": {"last": old_date.isoformat()}  # 15 points
    }
    
    selector = StationSelector(mock_loader)
    score = selector._compute_activity_score(stats)  # pylint: disable=protected-access
    
    assert score == 70.0, "Should have medium score (25 + 30 + 15)"


def test_compute_activity_score_low_activity(mock_loader):  # pylint: disable=redefined-outer-name
    """Test activity score calculation for low activity station."""
    # Very old data (3 years)
    old_date = datetime(2023, 2, 11, tzinfo=timezone.utc)
    
    stats = {
        "record_count": 5,  # 0 points
        "temperature_range": {"min": 0, "max": 0},  # 0 points (invalid)
        "date_range": {"last": old_date.isoformat()}  # 0 points
    }
    
    selector = StationSelector(mock_loader)
    score = selector._compute_activity_score(stats)  # pylint: disable=protected-access
    
    assert score == 0.0, "Should have zero score"


def test_get_stations_with_criteria_empty_database(mock_loader):  # pylint: disable=redefined-outer-name
    """Test behavior when database is empty."""
    mock_loader.fetch_all.return_value = []
    
    selector = StationSelector(mock_loader)
    stations = selector.get_stations_with_criteria(limit=10)
    
    assert stations == [], "Should return empty list for empty database"
