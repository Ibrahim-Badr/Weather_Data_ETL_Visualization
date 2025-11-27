"""
Configuration for Toulouse Metropole Open Data API.
"""
from typing import List, Dict, Optional
import json
from .base_config import IDataSourceConfig


class ToulouseConfig(IDataSourceConfig):
    """
    Configuration strategy for Toulouse Metropole weather data.
    
    Implements the IDataSourceConfig interface for accessing
    Toulouse's open data platform.
    """
    
    BASE_URL = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets"
    
    def __init__(self):
        """Initialize Toulouse configuration."""
        self.location = "Toulouse"
    
    def get_stations_api_url(self) -> str:
        """Get URL for all weather stations metadata."""
        return f"{self.BASE_URL}/stations-meteo-en-place/records"
    
    def get_station_data_url(self, station_id: str, dataset_id: Optional[str] = None) -> str:
        """
        Get URL for specific station weather data.
        
        Args:
            station_id: Station number (e.g., "24")
            dataset_id: Full dataset identifier (e.g., "24-station-meteo-colomiers-zi-enjacca")
        
        Returns:
            Complete API URL for station data
        """
        if dataset_id:
            return f"{self.BASE_URL}/{dataset_id}/records"
        return f"{self.BASE_URL}/{station_id}-station-meteo/records"
    
    def get_location_name(self) -> str:
        """Return location name."""
        return self.location
    
    def parse_station_metadata(self, api_response: dict) -> List[Dict]:
        """
        Parse Toulouse API response for station metadata.
        
        Args:
            api_response: JSON response from stations API
            
        Returns:
            List of standardized station dictionaries
        """
        stations = []
        results = api_response.get('results', [])
        
        print(f"Debug: Found {len(results)} raw records in API response")
        
        for idx, record in enumerate(results):
            try:
                if 'fields' in record:
                    fields = record['fields']
                elif 'record' in record and 'fields' in record['record']:
                    fields = record['record']['fields']
                else:
                    fields = record
                
                if idx == 0:
                    print("\nDebug: First record fields:")
                    print(json.dumps(fields, indent=2, ensure_ascii=False)[:500])
                
                station_id = fields.get('id_numero')
                station_name = fields.get('id_nom', 'Unknown')
                location = fields.get('ville', '')
                latitude = fields.get('latitude')
                longitude = fields.get('longitude')
                
                if station_id is not None:
                    station_id = str(station_id).zfill(2)
                else:
                    continue
                
                station = {
                    'station_id': station_id,
                    'station_name': station_name,
                    'location': location,
                    'latitude': latitude,
                    'longitude': longitude,
                    'active': True,
                    'dataset_id': fields.get('id_nom', '')
                }
                
                if station['station_id'] != '00':
                    stations.append(station)
                    
            except (KeyError, ValueError, TypeError) as e:
                print(f"Warning: Could not parse station record {idx}: {e}")
                continue
        
        print(f"Debug: Successfully parsed {len(stations)} stations\n")
        return stations
    
    def parse_weather_data(self, api_response: dict, station_id: str) -> List[Dict]:
        """
        Parse Toulouse API response for weather data.
        
        Args:
            api_response: JSON response from weather data API
            station_id: Station identifier
            
        Returns:
            List of standardized weather data dictionaries
        """
        weather_records = []
        results = api_response.get('results', [])
        
        for idx, record in enumerate(results):
            try:
                fields = record
                
                if idx == 0:
                    print(f"    Debug: Weather data fields: {list(fields.keys())[:10]}")
                
                weather_data = {
                    'station_id': station_id,
                    'timestamp': (
                        fields.get('heure_de_paris') or 
                        fields.get('heure_utc') or
                        fields.get('date') or 
                        fields.get('datetime')
                    ),
                    'temperature': (
                        fields.get('temperature_en_degre_c') or
                        fields.get('temperature') or 
                        fields.get('temp')
                    ),
                    'humidity': (
                        fields.get('humidite') or 
                        fields.get('humidity')
                    ),
                    'rainfall': (
                        fields.get('pluie') or 
                        fields.get('rainfall') or 
                        fields.get('precipitation') or
                        0
                    ),
                    'wind_speed': (
                        fields.get('force_moyenne_du_vecteur_vent') or
                        fields.get('force_rafale_max') or
                        fields.get('vitesse_vent') or 
                        fields.get('wind_speed')
                    ),
                    'pressure': (
                        fields.get('pression') or 
                        fields.get('pressure')
                    ),
                }
                
                if weather_data['timestamp'] and weather_data['temperature'] is not None:
                    weather_records.append(weather_data)
                    
            except (KeyError, ValueError, TypeError) as e:
                if idx == 0:
                    print(f"    Warning: Could not parse weather record: {e}")
                continue
        
        return weather_records
