"""
Tests for API stations endpoints - Integration tests using production database.
"""
# pylint: disable=redefined-outer-name
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Provide FastAPI test client."""
    return TestClient(app)


def test_get_stations_basic(client):
    """Test basic GET /stations endpoint."""
    response = client.get("/stations")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_stations_with_location_filter(client):
    """Test GET /stations with location filter."""
    response = client.get("/stations?location=Toulouse")
    
    assert response.status_code == 200
    data = response.json()
    
    # All results should match location filter
    for station in data:
        assert (
            "toulouse" in station["location"].lower() or 
            "toulouse" in station["station_name"].lower()
        )


def test_get_stations_with_limit(client):
    """Test GET /stations with limit parameter."""
    response = client.get("/stations?limit=5")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5


def test_get_stations_with_min_records(client):
    """Test GET /stations with min_records filter."""
    response = client.get("/stations?min_records=100")
    
    assert response.status_code ==200
    data = response.json()
    
    for station in data:
        assert station["record_count"] >= 100


def test_get_stations_with_temperature_range(client):
    """Test GET /stations with temperature range filters."""
    response = client.get("/stations?min_avg_temp=10&max_avg_temp=15")
    
    assert response.status_code == 200
    data = response.json()
    
    for station in data:
        assert 10.0 <= station["avg_temperature"] <= 15.0


def test_get_stations_invalid_limit(client):
    """Test GET /stations with invalid limit (should fail validation)."""
    response = client.get("/stations?limit=0")
    
    assert response.status_code == 422  # Validation error


def test_get_stations_limit_exceeds_max(client):
    """Test GET /stations with limit exceeding maximum (101)."""
    response =client.get("/stations?limit=101")
    
    assert response.status_code == 422  # Validation error


def test_get_station_details_existing(client):
    """Test GET /stations/{stationid} for existing station."""
    response = client.get("/stations/24")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["station_id"] == "24"
    assert "station_name" in data
    assert "location" in data
    assert "total_records" in data
    assert "avg_temperature" in data
    assert "temperature_range" in data
    assert "date_range" in data
    assert "latest_record" in data


def test_get_station_details_nonexistent(client):
    """Test GET /stations/{station_id} for non-existent station."""
    response = client.get("/stations/99999")
    
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


def test_get_station_activity_existing(client):
    """Test GET /stations/{station_id}/activity for existing station."""
    response = client.get("/stations/24/activity")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "activity_score" in data
    assert "status" in data
    assert 0 <= data["activity_score"] <= 100


def test_get_station_activity_nonexistent(client):
    """Test GET /stations/{station_id}/activity for non-existent station."""
    response = client.get("/stations/99999/activity")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "no_data"
    assert data["score"] == 0


def test_stations_endpoint_structure(client):
    """Test that stations endpoint returns properly structured data."""
    response = client.get("/stations?limit=1")
    
    assert response.status_code == 200
    data = response.json()
    
    if len(data) > 0:
        station = data[0]
        
        # Verify required fields
        required_fields = [
            "station_id", "station_name", "location",
            "record_count", "avg_temperature",
            "date_range", "temperature_range"
        ]
        
        for field in required_fields:
            assert field in station, f"Missing required field: {field}"


def test_stations_sorted_by_record_count(client):
    """Test that stations are sorted by record count descending."""
    response = client.get("/stations?limit=10")
    
    assert response.status_code == 200
    data = response.json()
    
    if len(data) > 1:
        for i in range(len(data) - 1):
            assert data[i]["record_count"] >= data[i + 1]["record_count"]


def test_stations_date_range_format(client):
    """Test that date ranges are properly formatted ISO strings."""
    response = client.get("/stations?limit=1")
    
    assert response.status_code == 200
    data = response.json()
    
    if len(data) > 0:
        date_range = data[0]["date_range"]
        
        # Verify ISO format
        assert "first" in date_range
        assert "last" in date_range
        
        # Should be parseable as ISO
        from datetime import datetime
        datetime.fromisoformat(date_range["first"])
        datetime.fromisoformat(date_range["last"])


def test_stations_with_multiple_filters(client):
    """Test GET /stations with multiple combined filters."""
    response = client.get(
        "/stations?location=Toulouse&min_records=50&min_avg_temp=5&limit=10"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_temperature_range_structure(client):
    """Test that temperature_range has min and max values."""
    response = client.get("/stations?limit=1")
    
    assert response.status_code == 200
    data = response.json()
    
    if len(data) > 0:
        temp_range = data[0]["temperature_range"]
        assert "min" in temp_range
        assert "max" in temp_range
        assert temp_range["max"] >= temp_range["min"]
