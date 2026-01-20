"""
Interface for data loaders.
Defines the contract for all data loading implementations.
"""
from abc import ABC, abstractmethod
from typing import List
from ..models.weather_model import WeatherDataModel


class IDataLoader(ABC):
    """
    Abstract base class for data loaders.

    Responsible for persisting and retrieving WeatherDataModel objects
    to/from a storage system (e.g., SQLite).
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the storage (e.g., create tables if they do not exist).
        """

    @abstractmethod
    def save(self, records: List[WeatherDataModel]) -> None:
        """
        Save a list of weather records into storage.

        Args:
            records: List of validated WeatherDataModel objects.
        """

    @abstractmethod
    def fetch_all(self) -> List[WeatherDataModel]:
        """
        Fetch all weather records from storage.

        Returns:
            List of WeatherDataModel objects.
        """

    @abstractmethod
    def fetch_by_station(self, station_id: str) -> List[WeatherDataModel]:
        """
        Fetch weather records for a specific station.

        Args:
            station_id: Station identifier.

        Returns:
            List of WeatherDataModel objects for that station.
        """
