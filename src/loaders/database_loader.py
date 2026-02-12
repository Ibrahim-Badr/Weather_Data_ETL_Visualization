"""
SQLite-based implementation of IDataLoader.

Responsible for:
- Creating the weather_data table if it doesn't exist
- Inserting WeatherDataModel records
- Querying records back as WeatherDataModel instances
"""

import sqlite3
from typing import List
from pathlib import Path
from datetime import datetime, timezone

from .interface import IDataLoader
from ..models.weather_model import WeatherDataModel


class DatabaseLoader(IDataLoader):
    """
    SQLite implementation of IDataLoader.

    Uses a local SQLite file (e.g., database/weather.db) to store weather data.
    """

    def __init__(self, db_path: str = "database/weather.db"):
        """
        Initialize the loader with a database path.

        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = db_path
        # Make sure parent folder exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # ✅ Track connections for cleanup
        self._connections = []

    def _get_connection(self) -> sqlite3.Connection:
        """
        Create and return a new SQLite connection.

        Returns:
            sqlite3.Connection object.
        """
        conn = sqlite3.connect(self.db_path)
        self._connections.append(conn)
        return conn

    # ✅ Cleanup method
    def close(self) -> None:
        """Close all open database connections."""
        for conn in self._connections:
            try:
                conn.close()
            except sqlite3.Error:
                pass
        self._connections.clear()

    # ✅ Context manager support
    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connections."""
        self.close()

    # ✅ Destructor
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()

    def initialize(self) -> None:
        """
        Create the weather_data table if it does not exist.
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            station_id TEXT NOT NULL,
            station_name TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            rainfall REAL NOT NULL,
            wind_speed REAL,
            pressure REAL,
            timestamp TEXT NOT NULL
        );
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()

    def save(self, records: List[WeatherDataModel]) -> None:
        """
        Save a list of weather records into the database.
        """
        if not records:
            print("No records to save.")
            return

        insert_sql = """
        INSERT INTO weather_data (
            location,
            station_id,
            station_name,
            temperature,
            humidity,
            rainfall,
            wind_speed,
            pressure,
            timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            data_to_insert = []

            for record in records:
                d = record.to_dict()
                data_to_insert.append(
                    (
                        d["location"],
                        d["station_id"],
                        d["station_name"],
                        d["temperature"],
                        d["humidity"],
                        d["rainfall"],
                        d["wind_speed"],
                        d["pressure"],
                        d["timestamp"],  # stored as ISO string
                    )
                )

            cursor.executemany(insert_sql, data_to_insert)
            conn.commit()

        print(f"✓ Saved {len(records)} records into the database.")

    def fetch_all(self) -> List[WeatherDataModel]:
        """
        Fetch all weather records from the database.

        Returns:
            List of WeatherDataModel instances.
        """
        select_sql = """
        SELECT
            location,
            station_id,
            station_name,
            temperature,
            humidity,
            rainfall,
            wind_speed,
            pressure,
            timestamp
        FROM weather_data
        ORDER BY timestamp;
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(select_sql)
            rows = cursor.fetchall()

        return [self._row_to_model(row) for row in rows]

    def fetch_by_station(self, station_id: str) -> List[WeatherDataModel]:
        """
        Fetch records only for a specific station.
        """
        select_sql = """
        SELECT
            location,
            station_id,
            station_name,
            temperature,
            humidity,
            rainfall,
            wind_speed,
            pressure,
            timestamp
        FROM weather_data
        WHERE station_id = ?
        ORDER BY timestamp;
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(select_sql, (station_id,))
            rows = cursor.fetchall()

        return [self._row_to_model(row) for row in rows]

    def _row_to_model(self, row: tuple) -> WeatherDataModel:
        """
        Convert a database row tuple into a WeatherDataModel instance.
        """
        (
            location,
            station_id,
            station_name,
            temperature,
            humidity,
            rainfall,
            wind_speed,
            pressure,
            timestamp_str,
        ) = row

        # FIXED: Always return timezone-aware UTC datetime
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            if timestamp.tzinfo is None:  # Make naive → aware
                timestamp = timestamp.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            timestamp = datetime.now(timezone.utc)  # Always timezone-aware UTC

        return WeatherDataModel(
            location=location,
            station_id=station_id,
            station_name=station_name,
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            wind_speed=wind_speed,
            pressure=pressure,
            timestamp=timestamp,
        )
