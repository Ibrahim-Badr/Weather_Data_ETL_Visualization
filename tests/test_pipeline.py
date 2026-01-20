"""
Test script for ETL Pipeline.
Tests the complete Extract → Transform → Load flow.
"""

from src.config.toulouse_config import ToulouseConfig
from src.extractors.api_extractor import APIExtractor
from src.transformers.data_cleaner import DataCleaner
from src.loaders.database_loader import DatabaseLoader
from src.pipeline.etl_pipeline import ETLPipeline



def test_etl_pipeline():
    """Test the complete ETL pipeline."""
    print("="*70)
    print("Testing Complete ETL Pipeline")
    print("="*70)
    
    # Step 1: Initialize all components
    print("\n🔧 Initializing components...")
    
    # Config
    config = ToulouseConfig()
    
    # Extractor
    extractor = APIExtractor(config)
    
    # Transformer
    transformer = DataCleaner()
    
    # Loader
    loader = DatabaseLoader("database/weather.db")
    loader.initialize()
    
    # Pipeline
    pipeline = ETLPipeline(
        extractor=extractor,
        transformer=transformer,
        loader=loader
    )
    
    print("✓ All components initialized")
    
    # Step 2: Run pipeline for one station with small limit
    print("\n🚀 Running pipeline for station 24 (3 records)...")
    
    pipeline.run(
        station_ids=["24"],  # Just one station for testing
        limit_per_station=3   # Small limit for testing
    )
    
    # Step 3: Verify data was saved
    print("\n🔍 Verifying data in database...")
    saved_records = loader.fetch_by_station("24")
    print(f"✓ Database contains {len(saved_records)} records for station 24")
    
    # Show a sample
    if saved_records:
        print("\n📊 Sample record from database:")
        print(saved_records[-1])  # Show the last one
    
    print("\n✅ Pipeline test completed successfully!")


if __name__ == "__main__":
    test_etl_pipeline()
