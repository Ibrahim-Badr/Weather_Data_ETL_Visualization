"""
Interface for data transformers.
Defines the contract for all data transformation implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from ..models.weather_model import WeatherDataModel


class IDataTransformer(ABC):
    """
    Abstract base class for data transformers.

    Transforms raw data dictionaries into validated WeatherDataModel objects.
    Follows Interface Segregation Principle - minimal, focused interface.
    """

    @abstractmethod
    def transform(self, raw_data: List[Dict]) -> List[WeatherDataModel]:
        """
        Transform and clean raw data into validated models.

        Args:
            raw_data: List of raw weather data dictionaries from API

        Returns:
            List[WeatherDataModel]: List of validated weather data models
        """
