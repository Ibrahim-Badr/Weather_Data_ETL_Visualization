"""Data loading package."""
from .interface import IDataLoader
from .database_loader import DatabaseLoader

__all__ = ["IDataLoader", "DatabaseLoader"]
