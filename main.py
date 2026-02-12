"""
Weather Data ETL Application - Main Entry Point

This application extracts weather data from Toulouse Metropole Open Data API,
cleans and validates it, then stores it in a SQLite database.

**Data Structures Used:**
- LinkedList: Tracks processing history chronologically
- Queue: Manages station processing order (FIFO)
- HashMap: Caches station metadata for O(1) lookup

Usage:
    python main.py                    # Run for all stations (limited)
    python main.py --stations 24      # Run for specific station
    python main.py --stations 24 36   # Run for multiple stations
    python main.py --limit 50         # Change record limit per station
    python main.py --list-stations    # List all available stations
    python main.py --show-structures  # Demonstrate data structures
"""

import sys
import traceback
import argparse
from datetime import datetime

from src.pipeline.etl_pipeline import ETLPipeline
from src.config.toulouse_config import ToulouseConfig
from src.extractors.api_extractor import APIExtractor
from src.transformers.data_cleaner import DataCleaner
from src.loaders.database_loader import DatabaseLoader


def demonstrate_data_structures(extractor: APIExtractor, pipeline: ETLPipeline):
    """
    Demonstrate the three data structures used in the project.
    
    1. HashMap: Station metadata caching (O(1) lookup)
    2. Queue: Station processing order (FIFO)
    3. LinkedList: Processing history tracking
    """
    print("\n" + "="*70)
    print("📚 DATA STRUCTURES DEMONSTRATION")
    print("="*70)
    
    # ✅ 1. HashMap Demonstration
    print("\n🗺️  HASHMAP (src/extractors/api_extractor.py)")
    print("-" * 70)
    print("Purpose: Cache station metadata for fast O(1) lookup")
    print("Implementation: Separate chaining for collision handling")
    
    cache_stats = extractor.get_cache_stats()
    print("\nHashMap Statistics:")
    print(f"  • Cache size: {cache_stats['cache_size']} stations")
    print(f"  • Cache capacity: {cache_stats['cache_capacity']}")
    print(f"  • Load factor: {cache_stats['load_factor']:.1%}")
    
    # Test O(1) lookup
    if cache_stats['cache_size'] > 0:
        test_station_id = "24"
        
        # Check if exists (O(1))
        if extractor.station_exists(test_station_id):
            print(f"\n✓ HashMap.contains('{test_station_id}'): True (O(1) operation)")
            
            # Get metadata (O(1))
            station = extractor.get_station_metadata(test_station_id)
            if station:
                print(f"✓ HashMap.get('{test_station_id}'): (O(1) operation)")
                print(f"  └─ Station: {station['station_name']}")
                print(f"  └─ Location: {station['location']}")
        
        print("\nBenefit: O(1) average lookup vs O(n) list search")
    
    # ✅ 2. Queue Demonstration
    print("\n\n📋 QUEUE (src/pipeline/etl_pipeline.py)")
    print("-" * 70)
    print("Purpose: Manage station processing order (FIFO - First In, First Out)")
    print("Implementation: Deque-based queue with enqueue/dequeue operations")
    
    queue_status = pipeline.get_queue_status()
    print("\nQueue Status:")
    print(f"  • Remaining stations: {queue_status['remaining_stations']}")
    print(f"  • Is empty: {queue_status['is_empty']}")
    
    if queue_status['next_station']:
        print(f"  • Next in queue: {queue_status['next_station']}")
    
    print("\nProcessing Flow:")
    print("  1. Enqueue station IDs → [24, 25, 26]")
    print("  2. Dequeue → Process 24 (FIFO)")
    print("  3. Dequeue → Process 25")
    print("  4. Dequeue → Process 26")
    print("  5. Queue empty → Processing complete")
    print("\nBenefit: Ensures deterministic, ordered processing")
    
    # ✅ 3. LinkedList Demonstration
    print("\n\n🔗 LINKEDLIST (src/pipeline/etl_pipeline.py)")
    print("-" * 70)
    print("Purpose: Track processing history in chronological order")
    print("Implementation: Singly linked list with Node structure")
    
    history = pipeline.get_processing_history()
    print("\nProcessing History (LinkedList):")
    print(f"  • Total events tracked: {len(history)}")
    
    if history:
        print("  • Events:")
        for i, event in enumerate(history[:5], 1):  # Show first 5
            time_str = event.timestamp.strftime('%H:%M:%S')
            status_emoji = {
                'success': '✓',
                'failed': '✗',
                'skipped': '⊘',
                'no_data': '⚠'
            }.get(event.status, '?')
            
            print(f"      {i}. [{time_str}] {status_emoji} Station {event.station_id}: "
                  f"{event.status} ({event.record_count} records)")
        
        if len(history) > 5:
            print(f"      ... and {len(history) - 5} more events")
    else:
        print("  • (Run pipeline first to see history)")
    
    print("\nBenefit: Maintains insertion order, easy traversal, efficient append")
    
    print("\n" + "="*70)
    print("✅ All three data structures demonstrated!")
    print("="*70 + "\n")


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
    parser.add_argument(
        '--show-structures',
        action='store_true',
        help='Demonstrate data structures (HashMap, Queue, LinkedList)'
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
    print("📚 Data Structures: HashMap, Queue, LinkedList")
    print("="*70)
    
    # Initialize configuration
    config = ToulouseConfig()
    extractor = APIExtractor(config)
    
    # Handle --list-stations flag
    if args.list_stations:
        print("\n📋 Fetching available stations...")
        
        stations = extractor.get_available_stations()
        
        if stations:
            print(f"\n✓ Found {len(stations)} active weather stations:\n")
            for station in stations[:10]:
                print(f"  • ID: {station['station_id']:3} | "
                      f"Name: {station['station_name']:40} | "
                      f"Location: {station['location']}")
            
            if len(stations) > 10:
                print(f"\n  ... and {len(stations) - 10} more stations")
            
            # Show HashMap cache stats
            cache_stats = extractor.get_cache_stats()
            print(f"\n🗺️  HashMap Cache: {cache_stats['cache_size']} stations cached")
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
    print("  • HashMap: Station caching (O(1) lookup)")
    print("  • Queue: Station processing order (FIFO)")
    print("  • LinkedList: History tracking")
    
    # Prepare station list
    station_ids = args.stations
    
    if station_ids:
        print(f"\n🎯 Target: Stations {', '.join(station_ids)}")
    else:
        print("\n🎯 Target: First 3 active stations (demo)")
        # Limit to 3 stations for demo
        all_stations = extractor.get_available_stations()
        if all_stations:
            station_ids = [s['station_id'] for s in all_stations[:3]]
    
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
            print(f"  Extracted: {stats.get('raw_records_extracted', 0)} records")
            print(f"  Transformed: {stats.get('valid_records_cleaned', 0)} records")
            print(f"  Loaded: {stats.get('records_saved', 0)} records")
            print(f"  Stations processed: {stats.get('stations_processed', 0)}")
            print(f"  Stations failed: {stats.get('stations_failed', 0)}")
        
        # ✅ Handle --show-structures flag OR auto-show after pipeline
        if args.show_structures or True:  # Always show for demonstration
            demonstrate_data_structures(extractor, pipeline)

    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        
        # Still show what we've done so far
        print("\n📊 Partial Results:")
        demonstrate_data_structures(extractor, pipeline)
        
        return 1

    except (OSError, ValueError) as e:
        print(f"\n\n❌ Unexpected error: {e}")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n\n❌ An unhandled exception occurred: {e}")
        traceback.print_exc()
        raise  # Re-raise to avoid swallowing unexpected exceptions

    return 0


if __name__ == "__main__":
    sys.exit(main())
