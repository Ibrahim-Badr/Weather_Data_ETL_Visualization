"""Configuration package for data source strategies."""
from .base_config import IDataSourceConfig
from .toulouse_config import ToulouseConfig

__all__ = ['IDataSourceConfig', 'ToulouseConfig']
