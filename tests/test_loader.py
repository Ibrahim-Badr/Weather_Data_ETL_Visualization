"""
Test script for DatabaseLoader.
"""
import sys
import os
from datetime import datetime

# Add project root to path (must be before src imports, but after standard library)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.weather_model import WeatherDataModel
from src.loaders.database_loader import DatabaseLoader


def test_database_loader():
    """
    Test the DatabaseLoader functionality.
    
    This test verifies:
    - Database initialization
    - Saving weather data records
    - Fetching all records
    - Fetching records by station ID
    """
    print("=" * 70)
    print("Testing DatabaseLoader")
    print("=" * 70)

    # Optional: Delete old database for clean test
    db_file = "database/weather.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print("✓ Cleared old database\n")

    loader = DatabaseLoader("database/weather.db")
    loader.initialize()

    # Create some fake models
    records = [
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

    # Save them
    loader.save(records)

    # Fetch all
    all_records = loader.fetch_all()
    print(f"\n✓ Fetched {len(all_records)} records from DB (all):")
    for r in all_records:
        print(f"- {r}")

    # Fetch by station
    station_records = loader.fetch_by_station("24")
    print(f"\n✓ Fetched {len(station_records)} records for station 24:")
    for r in station_records:
        print(f"- {r}")

    print("\nTest completed.")


if __name__ == "__main__":
    test_database_loader()
