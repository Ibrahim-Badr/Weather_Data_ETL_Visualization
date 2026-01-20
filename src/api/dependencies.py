"""
API dependencies - DatabaseLoader injection.
"""
from functools import lru_cache
from src.loaders.database_loader import DatabaseLoader
from src.loaders.interface import IDataLoader


@lru_cache()
def get_db_loader() -> IDataLoader:
    """
    Dependency injection for DatabaseLoader.
    
    Returns a cached DatabaseLoader instance for all requests.
    """
    loader = DatabaseLoader("database/weather.db")
    loader.initialize()  # Ensure table exists
    return loader
