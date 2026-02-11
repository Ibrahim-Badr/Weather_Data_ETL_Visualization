"""
Generic API extractor for weather data with HashMap caching.
"""
from typing import List, Dict, Optional
import requests
from .interface import IDataExtractor
from ..config.base_config import IDataSourceConfig
from ..structures.hash_map import HashMap  # ✅ NEW IMPORT

class APIExtractor(IDataExtractor):
    """
    Generic API-based data extractor with HashMap caching.
    
    HashMap provides O(1) average lookup time for cached station metadata.
    """
    
    def __init__(self, config: IDataSourceConfig, timeout: int = 30):
        """
        Initialize API extractor with HashMap cache.
        
        Args:
            config: Data source configuration implementing IDataSourceConfig
            timeout: Request timeout in seconds
        """
        self.config = config
        self.location = config.get_location_name()
        self.timeout = timeout
        
        # ✅ NEW: HashMap for caching station metadata (O(1) lookup)
        self._station_cache = HashMap[str, Dict](capacity=100)
        
        # Keep list cache for backward compatibility
        self._stations_list_cache: Optional[List[Dict]] = None
    
    def get_available_stations(self, force_refresh: bool = False) -> List[Dict]:
        """
        Get list of all available weather stations with HashMap caching.
        """
        if self._stations_list_cache and not force_refresh:
            print(f"Using cached stations data ({len(self._stations_list_cache)} stations)")
            return self._stations_list_cache
      
        print(f"Fetching stations list from {self.location}...")
        
        url = self.config.get_stations_api_url()
        
        try:
            response = requests.get(url, params={"limit": 100}, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            stations = self.config.parse_station_metadata(data)
            
            # Cache list
            self._stations_list_cache = stations
            
            # ✅ NEW: Store each station in HashMap for O(1) lookup
            print(f"Populating HashMap cache with {len(stations)} stations...")
            for station in stations:
                station_id = station['station_id']
                self._station_cache.put(station_id, station)
            
            print(f"✓ HashMap cache populated (size: {self._station_cache.size})")
            print(f"✓ Found {len(stations)} stations in {self.location}")
            
            return stations
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching stations: {e}")
            return []
        except (ValueError, KeyError) as e:
            print(f"✗ Error parsing stations data: {e}")
            return []
    
    # ✅ NEW METHOD: Get single station metadata with O(1) lookup
    def get_station_metadata(self, station_id: str) -> Optional[Dict]:
        """
        Get station metadata with O(1) HashMap lookup.
        
        Args:
            station_id: Station identifier
            
        Returns:
            Station metadata dictionary or None if not found
        """
        # ✅ Check HashMap cache first (O(1) operation)
        cached = self._station_cache.get(station_id)
        if cached:
            print(f"✓ HashMap cache hit for station {station_id}")
            return cached
        
        # Not in cache - fetch all stations to populate cache
        print(f"Cache miss for station {station_id}, fetching all stations...")
        self.get_available_stations(force_refresh=True)
        
        # Try again after populating cache
        return self._station_cache.get(station_id)
    
    # ✅ NEW METHOD: Check if station exists (O(1))
    def station_exists(self, station_id: str) -> bool:
        """
        Check if station exists using HashMap.
        O(1) operation - much faster than searching through list.
        """
        return self._station_cache.contains(station_id)
    
    def extract(self, station_ids: Optional[List[str]] = None, limit: int = 100) -> List[dict]:
        """
        Extract weather data from selected stations.
        """
        all_raw_data = []
        
        # Get all available stations (populates HashMap)
        stations = self.get_available_stations()
        
        # Filter by station_ids if provided
        if station_ids:
            # ✅ NEW: Use HashMap for fast filtering (O(1) per lookup)
            print("Filtering stations using HashMap (O(1) lookup)...")
            filtered_stations = []
            
            for sid in station_ids:
                station = self._station_cache.get(sid)  # O(1) lookup
                if station:
                    filtered_stations.append(station)
                else:
                    print(f"  ⚠ Station {sid} not found in HashMap")
            
            stations = filtered_stations
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
    
    # ✅ NEW METHOD: Get cache statistics
    def get_cache_stats(self) -> Dict:
        """Get HashMap cache statistics."""
        return {
            "cache_size": self._station_cache.size,
            "cache_capacity": self._station_cache.capacity,
            "load_factor": self._station_cache.size / self._station_cache.capacity
        }
    
    def _extract_station_data(self, station_id: str, station_info: Dict, limit: int) -> List[Dict]:
        """Extract weather data from a single station."""
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
