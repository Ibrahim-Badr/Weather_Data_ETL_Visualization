"""
Test script for API extractor.
"""
import sys
import os
import json

# Add src to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from src
from src.config.toulouse_config import ToulouseConfig
from src.extractors.api_extractor import APIExtractor


def main():
    print("="*70)
    print("Testing Weather Data Extractor")
    print("="*70)
    
    # Create configuration and extractor
    config = ToulouseConfig()
    extractor = APIExtractor(config)
    
    # Test 1: List all available stations
    print("\n[TEST 1] Getting available stations...")
    stations = extractor.get_available_stations()
    
    if stations:
        print(f"\n✓ Found {len(stations)} stations:")
        for station in stations[:5]:  # Show first 5
            print(f"  • ID: {station['station_id']:>2} | "
                  f"Name: {station['station_name']:<30} | "
                  f"Location: {station['location']}")
        
        if len(stations) > 5:
            print(f"  ... and {len(stations) - 5} more stations")
    else:
        print("✗ No stations found!")
        return
    
    # Test 2: Extract weather data from first station
    if stations:
        first_station = stations[0]
        station_id = first_station['station_id']
        
        print(f"\n[TEST 2] Extracting weather data for station {station_id}...")
        weather_data = extractor.extract(station_ids=[station_id], limit=3)
        
        if weather_data:
            print(f"\n✓ Successfully extracted {len(weather_data)} records:")
            print("\nSample data (pretty printed):")
            print(json.dumps(weather_data[:2], indent=2, ensure_ascii=False, default=str))
        else:
            print(f"✗ No weather data found for station {station_id}")
    
    print("\n" + "="*70)
    print("Test completed!")
    print("="*70)


if __name__ == "__main__":
    main()
