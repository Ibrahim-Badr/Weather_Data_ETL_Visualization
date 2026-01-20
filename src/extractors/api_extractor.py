"""
Generic API extractor for weather data.
Works with any data source configuration following the Strategy Pattern.
"""
from typing import List, Dict, Optional
import requests
from .interface import IDataExtractor
from ..config.base_config import IDataSourceConfig

class APIExtractor(IDataExtractor):
    """
    Generic API-based data extractor.
    
    This class demonstrates:
    - Dependency Inversion: Depends on IDataSourceConfig abstraction
    - Single Responsibility: Only handles API communication
    - Strategy Pattern: Behavior changes based on injected config
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
            
            self._stations_cache = stations
            
            print(f"✓ Found {len(stations)} stations in {self.location}")
            return stations
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching stations: {e}")
            return []
        except (ValueError, KeyError) as e:
            print(f"✗ Error parsing stations data: {e}")
            return []
    
    def extract(self, station_ids: Optional[List[str]] = None, limit: int = 100) -> List[dict]:
        """
        Extract weather data from selected stations.
        
        Args:
            station_ids: List of station IDs to extract from (None = all)
            limit: Maximum records per station
            
        Returns:
            List[dict]: Raw weather data records
        """
        all_raw_data = []
        
        # Get all available stations
        stations = self.get_available_stations()
        
        # Filter by station_ids if provided
        if station_ids:
            stations = [s for s in stations if s['station_id'] in station_ids]
            print(f"Extracting data from {len(stations)} selected stations.")
        else:
            print(f"No specific stations selected. Extracting from all {len(stations)} active stations.")
        
        # Extract from each station
        for station in stations:
            station_id = station['station_id']
            station_name = station['station_name']
            
            print(f"Extracting data from station {station_id} ({station_name})...")
            
            records = self._extract_station_data(station_id, station, limit)
            
            if records:
                print(f"  ✓ Extracted {len(records)} records from station {station_id}")
                all_raw_data.extend(records)
            else:
                print(f"  ✗ No data available for station {station_id}")
        
        print("\n" + "="*60)
        print(f"Total extracted: {len(all_raw_data)} weather records")
        print("="*60)
        
        return all_raw_data
    
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
        dataset_id = station_info.get('dataset_id')
        url = self.config.get_station_data_url(station_id, dataset_id)
        
        params = {"limit": limit}
        
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
        except (ValueError, KeyError) as e:
            print(f"    Error: Data parsing failed - {e}")
            return []

    def get_location(self) -> str:
        """Get the location name for this extractor."""
        return self.location
