from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class IDataSourceConfig(ABC):
    """
    Abstract base class for data source configurations.
    """

    @abstractmethod
    def get_stations_api_url(self) -> str:
        """Get the API URL for retrieving the list of all stations."""

    @abstractmethod
    def get_station_data_url(self, station_id: str, dataset_id: Optional[str] = None) -> str:
        """
        Get the API URL for retrieving weather data from a specific station.

        Args:
            station_id: Unique identifier of the weather station
            dataset_id: Optional full dataset identifier (can be None)

        Returns:
            str: URL endpoint for station weather data
        """

    @abstractmethod
    def get_location_name(self) -> str:
        """Get the human-readable location name."""

    @abstractmethod
    def parse_station_metadata(self, api_response: dict) -> List[Dict]:
        """Parse API response to extract station metadata."""

    @abstractmethod
    def parse_weather_data(self, api_response: dict, station_id: str) -> List[Dict]:
        """Parse API response to extract weather data records."""
