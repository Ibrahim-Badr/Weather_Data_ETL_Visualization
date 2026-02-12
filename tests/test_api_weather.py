"""
Tests for API weather endpoints - Integration tests using production database.
"""
# pylint: disable=redefined-outer-name
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Provide FastAPI test client."""
    return TestClient(app)


def test_get_weather_data_basic(client):
    """Test basic GET /weather endpoint with required station_id."""
    response = client.get("/weather/?station_id=24")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["station_id"] == "24"
    assert "total_records" in data
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_weather_data_missing_station_id(client):
    """Test GET /weather without required station_id parameter."""
    response = client.get("/weather/")
    
    assert response.status_code == 422  # Validation error


def test_get_weather_data_nonexistent_station(client):
    """Test GET /weather for non-existent station (should return 404)."""
    response = client.get("/weather/?station_id=99999")
    
    assert response.status_code == 404


def test_get_weather_data_with_limit(client):
    """Test GET /weather with limit parameter."""
    response = client.get("/weather/?station_id=24&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["data"]) <= 10


def test_get_weather_data_with_date_range(client):
    """Test GET /weather with start_date and end_date filters."""
    response = client.get(
        "/weather/?station_id=24&start_date=2023-01-01&end_date=2023-12-31"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should filter by date range
    from datetime import datetime, timezone
    for record in data["data"]:
        record_date = datetime.fromisoformat(record["timestamp"])
        assert datetime(2023, 1, 1, tzinfo=timezone.utc) <= record_date
        assert record_date <= datetime(2023, 12, 31, 23, 59, 59, tzinfo=timezone.utc)


def test_get_weather_data_with_start_date_only(client):
    """Test GET /weather with only start_date filter."""
    response = client.get("/weather/?station_id=24&start_date=2023-06-01")
    
    assert response.status_code == 200
    data = response.json()
    
    from datetime import datetime, timezone
    for record in data["data"]:
        record_date = datetime.fromisoformat(record["timestamp"])
        assert record_date >= datetime(2023, 6, 1, tzinfo=timezone.utc)


def test_get_weather_data_with_min_temp(client):
    """Test GET /weather with min_temp filter."""
    response = client.get("/weather/?station_id=24&min_temp=15.0")
    
    assert response.status_code == 200
    data = response.json()
    
    for record in data["data"]:
        assert record["temperature"] >= 15.0


def test_get_weather_data_with_max_temp(client):
    """Test GET /weather with max_temp filter."""
    response = client.get("/weather/?station_id=24&max_temp=20.0")
    
    assert response.status_code == 200
    data = response.json()
    
    for record in data["data"]:
        assert record["temperature"] <= 20.0


def test_get_weather_data_with_temp_range(client):
    """Test GET /weather with both min_temp and max_temp filters."""
    response = client.get("/weather/?station_id=24&min_temp=10.0&max_temp=25.0")
    
    assert response.status_code == 200
    data = response.json()
    
    for record in data["data"]:
        assert 10.0 <= record["temperature"] <= 25.0


def test_get_weather_data_structure(client):
    """Test that weather data has correct structure."""
    response = client.get("/weather/?station_id=24&limit=1")
    
    assert response.status_code == 200
    data = response.json()
    
    if len(data["data"]) > 0:
        record = data["data"][0]
        
        required_fields = [
            "station_id", "station_name", "location",
            "timestamp", "temperature", "humidity",
            "wind_speed"
        ]
        
        for field in required_fields:
            assert field in record, f"Missing required field: {field}"


def test_get_weather_stats_all_stations(client):
    """Test GET /weather/stats for all stations."""
    response = client.get("/weather/stats")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_records" in data
    assert "avg_temperature" in data
    assert "min_temperature" in data
    assert "max_temperature" in data
    assert "temperature_std" in data
    assert "stations_count" in data


def test_get_weather_stats_single_station(client):
    """Test GET /weather/stats for a specific station."""
    response = client.get("/weather/stats?station_id=24")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["stations_count"] == 1
    assert data["total_records"] > 0


def test_get_weather_stats_nonexistent_station(client):
    """Test GET /weather/stats for non-existent station."""
    response = client.get("/weather/stats?station_id=99999")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "error" in data


def test_get_weather_limit_validation(client):
    """Test GET /weather with invalid limit values."""
    # Limit too low
    response = client.get("/weather/?station_id=24&limit=0")
    assert response.status_code == 422
    
    # Limit too high
    response = client.get("/weather/?station_id=24&limit=1001")
    assert response.status_code == 422


def test_get_weather_filtered_count(client):
    """Test that filtered_count in response is accurate."""
    response = client.get("/weather/?station_id=24&min_temp=15.0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    
    # total_records should be after limit, filtered_count before limit
    assert data["total_records"] <= 10
    assert data["filtered_count"] >= data["total_records"]


def test_weather_temperature_statistics(client):
    """Test that temperature stats are calculated correctly."""
    response = client.get("/weather/stats?station_id=24")
    
    assert response.status_code == 200
    data = response.json()
    
    # Logical validations
    assert data["min_temperature"] <= data["avg_temperature"]
    assert data["avg_temperature"] <= data["max_temperature"]
    assert data["temperature_std"] >= 0


def test_weather_combined_filters(client):
    """Test GET /weather with multiple combined filters."""
    response = client.get(
        "/weather/?station_id=24&start_date=2023-01-01&min_temp=10&max_temp=25&limit=20"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)


def test_weather_response_metadata(client):
    """Test that weather response includes all metadata fields."""
    response = client.get("/weather/?station_id=24&limit=5")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "station_id" in data
    assert "total_records" in data
    assert "filtered_count" in data
    assert "data" in data
