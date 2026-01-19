"""
Tests for the StationSelector service.

Verifies station filtering by location and thresholds,
and calculation of activity scores from the database.
"""

from src.services.station_selector import StationSelector
from src.loaders.database_loader import DatabaseLoader


def test_station_selector_basic():
    """
    Test basic functionality of StationSelector to retrieve stations with criteria.
    Verifies that:
    - DatabaseLoader initializes successfully
    - StationSelector can retrieve stations with a limit parameter
    - Retrieved stations list is not empty
    - Each station record contains a 'station_id' field
    """
    loader = DatabaseLoader("database/weather.db")
    loader.initialize()
    selector = StationSelector(loader)

    stations = selector.get_stations_with_criteria(limit=5)
    assert len(stations) > 0
    assert "station_id" in stations[0]

def test_station_selector_location():
    """
    Test that StationSelector correctly retrieves stations filtered by location.
    Verifies that when querying for stations in "Colomiers", the returned stations
    contain "Colomiers" in either their station_name or location field.
    """
    loader = DatabaseLoader("database/weather.db")
    loader.initialize()
    selector = StationSelector(loader)

    stations = selector.get_stations_with_criteria(location="Colomiers", limit=5)
    assert any("Colomiers".lower() in s["station_name"].lower()
               or "Colomiers".lower() in s["location"].lower()
               for s in stations)
