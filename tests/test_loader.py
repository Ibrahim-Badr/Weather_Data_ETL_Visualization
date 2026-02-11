"""
Tests for DatabaseLoader.
"""

def test_database_initialization(database_loader):
    """Test that database initializes correctly."""
    # The fixture already initializes, so we just verify it exists
    assert database_loader is not None


def test_save_weather_data(database_loader, sample_weather_models):
    """Test saving weather data records to database."""
    # Save records
    database_loader.save(sample_weather_models)
    
    # Fetch all records
    all_records = database_loader.fetch_all()
    
    assert len(all_records) >= len(sample_weather_models)
    assert all(hasattr(record, 'station_id') for record in all_records)


def test_fetch_all_records(database_loader, sample_weather_models):
    """Test fetching all records from database."""
    # Save some records first
    database_loader.save(sample_weather_models)
    
    # Fetch all
    all_records = database_loader.fetch_all()
    
    assert isinstance(all_records, list)
    assert len(all_records) > 0


def test_fetch_by_station_id(database_loader, sample_weather_models):
    """Test fetching records filtered by station ID."""
    # Save records
    database_loader.save(sample_weather_models)
    
    # Fetch by station
    station_id = sample_weather_models[0].station_id
    station_records = database_loader.fetch_by_station(station_id)
    
    assert isinstance(station_records, list)
    assert len(station_records) > 0
    assert all(record.station_id == station_id for record in station_records)


def test_save_empty_list(database_loader):
    """Test that saving an empty list doesn't cause errors."""
    database_loader.save([])
    
    # Should not raise any exceptions


def test_fetch_nonexistent_station(database_loader):
    """Test fetching data for a station that doesn't exist."""
    records = database_loader.fetch_by_station("999999")
    
    assert isinstance(records, list)
    assert len(records) == 0
