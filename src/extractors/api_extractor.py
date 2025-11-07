"""
Generic API extractor for weather data.
Works with any data source configuration following the Strategy Pattern.
"""
import requests
from typing import List, Dict, Optional
import time
from .interface import IDataExtractor
from ..config.base_config import IDataSourceConfig


class APIExtractor(IDataExtractor):
    """
    Generic API-based data extractor.
    
    This class demonstrates:
    - Dependency Inversion: Depends on IDataSourceConfig abstraction
    - Single Responsibility: Only handles API communication
    - Strategy Pattern: Behavior changes based on injected config
    
    Attributes:
        config: Data source configuration strategy
        location: Location name from config
        _stations_cache: Cached list of available stations
    """
    
    def __init__(self, config: IDataSourceConfig, timeout: int = 30):
        """
        Initialize API extractor with configuration.
        
        Args:
            config: Data source configuration implementing IDataSourceConfig
            timeout: Request timeout in seconds
        """
        self.config = config
        self.location = config.get_location_name()
        self.timeout = timeout
        self._stations_cache: Optional[List[Dict]] = None
    
    def get_available_stations(self, force_refresh: bool = False) -> List[Dict]:
        """
        Get list of all available weather stations.
        
        Uses caching to avoid repeated API calls.
        
        Args:
            force_refresh: If True, bypasses cache and fetches fresh data
            
        Returns:
            List[Dict]: List of station metadata
        """
        # Return cached data if available and not forcing refresh
        if self._stations_cache and not force_refresh:
            print(f"Using cached stations data ({len(self._stations_cache)} stations)")
            return self._stations_cache
        
        print(f"Fetching stations list from {self.location}...")
        
        url = self.config.get_stations_api_url()
        
        try:
            response = requests.get(url, params={"limit": 100}, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            stations = self.config.parse_station_metadata(data)
            
            # Cache the results
            self._stations_cache = stations
            
            print(f"✓ Found {len(stations)} stations in {self.location}")
            return stations
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching stations: {e}")
            return []
        except Exception as e:
            print(f"✗ Error parsing stations data: {e}")
            return []
    
    def extract(self, station_ids: Optional[List[str]] = None, limit: int = 100) -> List[Dict]:
        """
        Extract weather data from specified stations.
        
        Args:
            station_ids: List of station IDs to extract. If None, extracts all.
            limit: Maximum records per station
            
        Returns:
            List[Dict]: Raw weather data dictionaries
        """
        # Get available stations
        all_stations = self.get_available_stations()
        
        if not all_stations:
            print("No stations available for extraction")
            return []
        
        # If no specific stations requested, use all active stations
        if station_ids is None:
            station_ids = [s['station_id'] for s in all_stations if s.get('active', True)]
            print(f"No specific stations selected. Extracting from all {len(station_ids)} active stations.")
        
        # Extract data from each station
        all_weather_data = []
        
        for station_id in station_ids:
            # Find station info
            station_info = next(
                (s for s in all_stations if s['station_id'] == station_id),
                None
            )
            
            if not station_info:
                print(f"⚠ Station {station_id} not found in available stations. Skipping.")
                continue
            
            print(f"Extracting data from station {station_id} ({station_info['station_name']})...")
            
            # Extract station data
            station_data = self._extract_station_data(station_id, station_info, limit)
            
            if station_data:
                all_weather_data.extend(station_data)
                print(f"  ✓ Extracted {len(station_data)} records from station {station_id}")
            else:
                print(f"  ✗ No data available for station {station_id}")
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        print(f"\n{'='*60}")
        print(f"Total extracted: {len(all_weather_data)} weather records")
        print(f"{'='*60}\n")
        
        return all_weather_data
    
    def _extract_station_data(self, station_id: str, station_info: Dict, limit: int) -> List[Dict]:
        """
        Extract weather data from a single station.
        
        Args:
            station_id: Station identifier
            station_info: Station metadata
            limit: Maximum number of records
            
        Returns:
            List[Dict]: Weather data records for this station
        """
        # Get the full dataset_id from station_info
        dataset_id: Optional[str] = station_info.get('dataset_id')
        
        # Build URL with full dataset name
        url = self.config.get_station_data_url(station_id, dataset_id)
        
        # Toulouse API doesn't support order_by parameter
        params = {
            "limit": limit
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            weather_records = self.config.parse_weather_data(data, station_id)
            
            # Enrich with station metadata
            for record in weather_records:
                record['location'] = self.location
                record['station_name'] = station_info['station_name']
            
            return weather_records
            
        except requests.exceptions.RequestException as e:
            print(f"    Error: API request failed - {e}")
            return []
        except Exception as e:
            print(f"    Error: Data parsing failed - {e}")
            return []

    def get_location(self) -> str:
        """Get the location name for this extractor."""
        return self.location
