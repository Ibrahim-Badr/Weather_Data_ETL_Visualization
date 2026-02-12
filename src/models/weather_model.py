"""
Weather data model.
Represents a single weather observation record with validation.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class WeatherDataModel:
    """
    Immutable data model for weather observations.

    Follows Single Responsibility Principle - only handles data structure
    and validation logic.

    Attributes:
        location: City/region name (e.g., "Toulouse", "Colomiers")
        station_id: Unique station identifier (e.g., "24")
        station_name: Human-readable station name
        temperature: Temperature in Celsius
        humidity: Relative humidity percentage (0-100)
        rainfall: Precipitation in millimeters
        timestamp: Observation datetime
        wind_speed: Wind speed in m/s (optional)
        pressure: Atmospheric pressure in Pascal (optional)
    """

    location: str
    station_id: str
    station_name: str
    temperature: float
    humidity: float
    rainfall: float
    timestamp: datetime
    wind_speed: Optional[float] = None
    pressure: Optional[float] = None

    def validate(self) -> bool:
        """
        Validate weather data against realistic constraints.

        Returns:
            bool: True if data is valid, False otherwise
        """
        # Check required fields are not empty
        if not self.station_id or not self.location:
            return False

        # Temperature range check (-60°C to 60°C covers extreme Earth temperatures)
        if not (-60 <= self.temperature <= 60):
            return False

        # Humidity must be percentage (0-100)
        if not (0 <= self.humidity <= 100):
            return False

        # Rainfall cannot be negative
        if self.rainfall < 0:
            return False

        # Optional: Wind speed cannot be negative
        if self.wind_speed is not None and self.wind_speed < 0:
            return False

        # Optional: Pressure check (reasonable atmospheric range in Pascal)
        # Normal range: 87000-108000 Pa (870-1080 hPa)
        if self.pressure is not None and not (80000 <= self.pressure <= 110000):
            return False

        return True

    def to_dict(self) -> dict:
        """
        Convert model to dictionary for serialization.

        Returns:
            dict: Dictionary representation of the model
        """
        data = asdict(self)
        # Convert datetime to ISO format string for JSON serialization
        data['timestamp'] = self.timestamp.isoformat() if isinstance(
            self.timestamp, datetime) else str(self.timestamp)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'WeatherDataModel':
        """
        Create model instance from dictionary.

        Args:
            data: Dictionary with weather data

        Returns:
            WeatherDataModel: New instance

        Raises:
            ValueError: If required fields are missing
        """
        # Handle timestamp conversion
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            # Try to parse ISO format
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                # If parsing fails, use current time
                timestamp = datetime.now()
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.now()

        # Convert wind_speed and pressure, handling None values
        wind_speed = data.get('wind_speed')
        if wind_speed is not None:
            wind_speed = float(wind_speed)

        pressure = data.get('pressure')
        if pressure is not None:
            pressure = float(pressure)

        return cls(
            location=data.get('location', ''),
            station_id=data.get('station_id', ''),
            station_name=data.get('station_name', ''),
            temperature=float(data.get('temperature', 0)),
            humidity=float(data.get('humidity', 0)),
            rainfall=float(data.get('rainfall', 0)),
            wind_speed=wind_speed,
            pressure=pressure,
            timestamp=timestamp
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"WeatherDataModel(station={self.station_id}, "
                f"temp={self.temperature}°C, "
                f"humidity={self.humidity}%, "
                f"time={self.timestamp.strftime('%Y-%m-%d %H:%M') if isinstance(self.timestamp, datetime) else self.timestamp})")

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (f"{self.station_name} ({self.station_id}) - {self.location}\n"
                f"  Temperature: {self.temperature}°C\n"
                f"  Humidity: {self.humidity}%\n"
                f"  Rainfall: {self.rainfall}mm\n"
                f"  Wind Speed: {self.wind_speed if self.wind_speed else 'N/A'} m/s\n"
                f"  Pressure: {self.pressure if self.pressure else 'N/A'} Pa\n"
                f"  Time: {self.timestamp}")
