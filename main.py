"""
Weather Data ETL Application - Main Entry Point

This application extracts weather data from Toulouse Metropole Open Data API,
cleans and validates it, then stores it in a SQLite database.

Usage:
    python main.py                    # Run for all stations (limited)
    python main.py --stations 24      # Run for specific station
    python main.py --stations 24 36   # Run for multiple stations
    python main.py --limit 50         # Change record limit per station
"""
import sys
import argparse
from datetime import datetime

from src.config.toulouse_config import ToulouseConfig
from src.extractors.api_extractor import APIExtractor
from src.transformers.data_cleaner import DataCleaner
from src.loaders.database_loader import DatabaseLoader
from src.pipeline.etl_pipeline import ETLPipeline


def main():
    """Main application entry point."""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Weather Data ETL Pipeline - Extract, Transform, Load weather data"
    )
    parser.add_argument(
        '--stations',
        nargs='+',
        help='Specific station IDs to process (e.g., --stations 24 36)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Maximum records to extract per station (default: 100)'
    )
    parser.add_argument(
        '--list-stations',
        action='store_true',
        help='List all available stations and exit'
    )
    
    args = parser.parse_args()

    # Validate limit
    if args.limit > 100:
        print("\n⚠️  Warning: Toulouse API maximum limit is 100 records per station.")
        print("   Adjusting limit to 100...\n")
        args.limit = 100
    
    # Display header
    print("\n" + "="*70)
    print("🌤️  Weather Data ETL Application")
    print("="*70)
    print(f"📅 Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📍 Location: Toulouse, France")
    print("="*70)
    
    # Initialize configuration
    config = ToulouseConfig()
    extractor = APIExtractor(config)
    
    # Handle --list-stations flag
    if args.list_stations:
        print("\n📋 Fetching available stations...")
        
        # Use extractor's public method to get stations
        try:
            # Extract with limit=0 to get stations only
            raw_data = extractor.extract(station_ids=None, limit=0)
            stations = raw_data if raw_data else []
        except (ConnectionError, ValueError, KeyError):
            stations = []
        
        if stations:
            print(f"\n✓ Found {len(stations)} active weather stations:\n")
            for station in stations[:10]:
                print(f"  • ID: {station['station_id']:3} | "
                    f"Name: {station['station_name']:40} | "
                    f"Location: {station['location']}")
            
            if len(stations) > 10:
                print(f"\n  ... and {len(stations) - 10} more stations")
        else:
            print("❌ No stations found. Check API connection.")
        
        print("\nUse --stations <ID> to process specific stations")
        return 0


    # Initialize ETL components
    print("\n🔧 Initializing ETL components...")
    
    transformer = DataCleaner()
    loader = DatabaseLoader("database/weather.db")
    loader.initialize()
    
    pipeline = ETLPipeline(
        extractor=extractor,
        transformer=transformer,
        loader=loader
    )
    
    print("✓ Components initialized")
    
    # Prepare station list
    station_ids = args.stations
    
    if station_ids:
        print(f"\n🎯 Target: Stations {', '.join(station_ids)}")
    else:
        print("\n🎯 Target: All active stations")
    
    print(f"📊 Limit: {args.limit} records per station")
    
    # Run the pipeline
    try:
        stats = pipeline.run(
            station_ids=station_ids,
            limit_per_station=args.limit
        )
        
        # Display results
        if stats:
            print("\n✓ Pipeline completed successfully")
            print(f"  Extracted: {stats.get('extracted', 0)} records")
            print(f"  Transformed: {stats.get('transformed', 0)} records")
            print(f"  Loaded: {stats.get('loaded', 0)} records")

    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        return 1

    except RuntimeError as e:
        print(f"\n\n❌ Runtime error: {e}")
        return 1

    except (ConnectionError, ValueError, KeyError, IOError) as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
