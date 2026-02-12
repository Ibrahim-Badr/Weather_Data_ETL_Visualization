"""
API dependencies - DatabaseLoader injection.
"""
import os
from functools import lru_cache
from src.loaders.database_loader import DatabaseLoader
from src.loaders.interface import IDataLoader

# ✅ Use environment variable for DB path
DATABASE_PATH = os.getenv("DATABASE_PATH", "database/weather.db")

@lru_cache()
def get_db_loader() -> IDataLoader:
    """
    Dependency injection for DatabaseLoader.
    
    Returns a cached DatabaseLoader instance for all requests.
    """
    loader = DatabaseLoader(DATABASE_PATH)
    loader.initialize()  # Ensure table exists
    return loader
