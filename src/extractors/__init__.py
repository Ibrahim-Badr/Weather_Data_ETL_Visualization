"""Data extraction package."""
from .interface import IDataExtractor
from .api_extractor import APIExtractor

__all__ = ['IDataExtractor', 'APIExtractor']
