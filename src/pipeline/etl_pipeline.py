"""
ETL Pipeline orchestration.
Coordinates the Extract → Transform → Load process.
"""
from typing import List, Optional
from datetime import datetime
import time

from ..extractors.interface import IDataExtractor
from ..transformers.interface import IDataTransformer
from ..loaders.interface import IDataLoader
from ..models.weather_model import WeatherDataModel


class ETLPipeline:
    """
    ETL Pipeline orchestrator.
    
    Coordinates the complete data flow:
    1. Extract: Get raw data from API via extractor
    2. Transform: Clean and validate via transformer
    3. Load: Save to database via loader
    
    Demonstrates Dependency Injection and Single Responsibility principles.
    """
    
    def __init__(
        self,
        extractor: IDataExtractor,
        transformer: IDataTransformer,
        loader: IDataLoader
    ):
        """
        Initialize pipeline with dependencies.
        
        Args:
            extractor: Implementation of IDataExtractor
            transformer: Implementation of IDataTransformer
            loader: Implementation of IDataLoader
        """
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
        
        # Statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'raw_records_extracted': 0,
            'valid_records_cleaned': 0,
            'records_saved': 0,
            'stations_processed': 0
        }
    
    def run(
        self,
        station_ids: Optional[List[str]] = None,
        limit_per_station: int = 100
    ) -> dict:
        """
        Run the complete ETL pipeline.
        
        Args:
            station_ids: List of station IDs to process. If None, process all.
            limit_per_station: Maximum records to extract per station
            
        Returns:
            dict: Pipeline execution statistics
        """
        print("\n" + "="*70)
        print("🚀 Starting ETL Pipeline")
        print("="*70)
        
        self.stats['start_time'] = datetime.now()
        start_time = time.time()
        
        try:
            # Step 1: EXTRACT
            print("\n📥 Step 1: EXTRACT - Getting raw data from API...")
            raw_data = self.extractor.extract(
                station_ids=station_ids,
                limit=limit_per_station
            )
            self.stats['raw_records_extracted'] = len(raw_data)
            print(f"   ✓ Extracted {len(raw_data)} raw records")
            
            if not raw_data:
                print("\n⚠ No data extracted. Pipeline stopped.")
                return self.stats
            
            # Step 2: TRANSFORM
            print("\n🔄 Step 2: TRANSFORM - Cleaning and validating data...")
            clean_data = self.transformer.transform(raw_data)
            self.stats['valid_records_cleaned'] = len(clean_data)
            print(f"   ✓ Cleaned {len(clean_data)} valid records")
            
            if not clean_data:
                print("\n⚠ No valid data after cleaning. Pipeline stopped.")
                return self.stats
            
            # Step 3: LOAD
            print("\n💾 Step 3: LOAD - Saving to database...")
            self.loader.save(clean_data)
            self.stats['records_saved'] = len(clean_data)
            
            # Count unique stations
            unique_stations = len(set(record.station_id for record in clean_data))
            self.stats['stations_processed'] = unique_stations
            
            # Calculate duration
            self.stats['end_time'] = datetime.now()
            self.stats['duration_seconds'] = round(time.time() - start_time, 2)
            
            # Print summary
            self._print_summary()
            
            return self.stats
            
        except Exception as e:
            print(f"\n❌ Pipeline failed with error: {e}")
            self.stats['end_time'] = datetime.now()
            self.stats['duration_seconds'] = round(time.time() - start_time, 2)
            raise
    
    def _print_summary(self):
        """Print pipeline execution summary."""
        print("\n" + "="*70)
        print("✅ ETL Pipeline Completed Successfully")
        print("="*70)
        print(f"⏱  Duration: {self.stats['duration_seconds']} seconds")
        print(f"📊 Records extracted: {self.stats['raw_records_extracted']}")
        print(f"✨ Records cleaned: {self.stats['valid_records_cleaned']}")
        print(f"💾 Records saved: {self.stats['records_saved']}")
        print(f"🏢 Stations processed: {self.stats['stations_processed']}")
        
        # Calculate success rate
        if self.stats['raw_records_extracted'] > 0:
            success_rate = (
                self.stats['valid_records_cleaned'] / 
                self.stats['raw_records_extracted'] * 100
            )
            print(f"📈 Data quality: {success_rate:.1f}% valid records")
        
        print("="*70 + "\n")
    
    def get_stats(self) -> dict:
        """
        Get pipeline statistics.
        
        Returns:
            dict: Pipeline execution statistics
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset pipeline statistics."""
        self.stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'raw_records_extracted': 0,
            'valid_records_cleaned': 0,
            'records_saved': 0,
            'stations_processed': 0
        }
