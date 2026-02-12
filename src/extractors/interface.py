"""
Interface for data extractors.
Defines the contract for all data extraction implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class IDataExtractor(ABC):
    """
    Abstract base class for data extractors.

    Implements Interface Segregation Principle - minimal, focused interface.
    Follows Open/Closed Principle - open for extension, closed for modification.
    """

    @abstractmethod
    def get_available_stations(self) -> List[Dict]:
        """
        Retrieve list of all available weather stations.

        Returns:
            List[Dict]: List of station metadata dictionaries
        """

    @abstractmethod
    def extract(self, station_ids: Optional[List[str]] = None, limit: int = 100) -> List[Dict]:
        """
        Extract weather data from specified stations.

        Args:
            station_ids: List of station IDs to extract. If None, extracts all stations.
            limit: Maximum number of records per station

        Returns:
            List[Dict]: List of raw weather data dictionaries
        """
