"""
Tests for ETL Pipeline.
Tests the complete Extract → Transform → Load flow.
"""
from src.pipeline.etl_pipeline import ETLPipeline


def test_pipeline_initialization(api_extractor, data_cleaner, database_loader):
    """Test that ETL pipeline initializes correctly with all components."""
    pipeline = ETLPipeline(
        extractor=api_extractor,
        transformer=data_cleaner,
        loader=database_loader
    )
    
    assert pipeline is not None
    assert pipeline.extractor is not None
    assert pipeline.transformer is not None
    assert pipeline.loader is not None


def test_pipeline_run_single_station(api_extractor, data_cleaner, database_loader):
    """Test running the complete ETL pipeline for a single station."""
    pipeline = ETLPipeline(
        extractor=api_extractor,
        transformer=data_cleaner,
        loader=database_loader
    )
    
    # Run pipeline with small limit for testing
    pipeline.run(
        station_ids=["24"],
        limit_per_station=3
    )
    
    # Verify data was saved
    saved_records = database_loader.fetch_by_station("24")
    assert len(saved_records) > 0, "Pipeline should have saved records to database"


def test_pipeline_run_multiple_stations(api_extractor, data_cleaner, database_loader):
    """Test running the ETL pipeline for multiple stations."""
    pipeline = ETLPipeline(
        extractor=api_extractor,
        transformer=data_cleaner,
        loader=database_loader
    )
    
    # Run pipeline for multiple stations
    pipeline.run(
        station_ids=["24", "25"],
        limit_per_station=2
    )
    
    # Verify data was saved for both stations
    all_records = database_loader.fetch_all()
    assert len(all_records) > 0, "Pipeline should have saved records"


def test_pipeline_extract_transform_load_flow(api_extractor, data_cleaner, database_loader):
    """Test that data flows through Extract → Transform → Load correctly."""
    pipeline = ETLPipeline(
        extractor=api_extractor,
        transformer=data_cleaner,
        loader=database_loader
    )
    
    # Get initial record count
    initial_count = len(database_loader.fetch_all())
    
    # Run pipeline
    pipeline.run(station_ids=["24"], limit_per_station=2)
    
    # Verify new records were added
    final_count = len(database_loader.fetch_all())
    assert final_count >= initial_count, "Pipeline should add records to database"
