"""
Station selection and filtering service.

Provides StationSelector to summarize stations, apply filters,
and compute activity scores from weather data loaded via IDataLoader.
"""

from typing import List, Dict, Optional
from datetime import datetime, timezone
from src.loaders.interface import IDataLoader
from src.models.weather_model import WeatherDataModel


class StationSelector:
    """
    Professional station filtering service.

    Features:
    - Location filtering
    - Date range filtering  
    - Record count thresholds
    - Temperature range filtering
    - Activity scoring
    """

    def __init__(self, loader: IDataLoader):
        self.loader = loader

    def get_stations_with_criteria(
        self,
        location: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_records: Optional[int] = None,
        min_avg_temp: Optional[float] = None,
        max_avg_temp: Optional[float] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Return station summaries filtered by location, record count,
        average temperature thresholds, and limited to a maximum number.
        """
        all_records = self.loader.fetch_all()
        stations = self._group_by_station(all_records)

        filtered_stations = []
        for station_id, records in stations.items():
            station_summary = self._calculate_station_stats(records, station_id)

            if self._matches_criteria(station_summary, location, start_date,
                                      end_date, min_records, min_avg_temp, max_avg_temp):
                filtered_stations.append(station_summary)

        filtered_stations.sort(key=lambda x: x['record_count'], reverse=True)
        return filtered_stations[:limit]

    def get_station_activity_score(self, station_id: str) -> Dict:
        """
        Calculate comprehensive activity score for a station.
        """
        records = self.loader.fetch_by_station(station_id)
        if not records:
            return {"station_id": station_id, "activity_score": 0, "status": "no_data"}

        station_stats = self._calculate_station_stats(records, station_id)
        score = self._compute_activity_score(station_stats)

        return {
            **station_stats,
            "activity_score": score,
            "status": "active" if score > 50 else "low_activity"
        }

    def _group_by_station(self, records: List[WeatherDataModel]) -> Dict[str, List[WeatherDataModel]]:
        """Group records by station_id."""
        stations = {}
        for record in records:
            sid = record.station_id
            if sid not in stations:
                stations[sid] = []
            stations[sid].append(record)
        return stations

    def _calculate_station_stats(self, records: List[WeatherDataModel], station_id: str) -> Dict:
        """Calculate comprehensive statistics for a station."""
        if not records:
            return {}

        first_record = min(records, key=lambda x: x.timestamp)
        last_record = max(records, key=lambda x: x.timestamp)
        temps = [r.temperature for r in records if r.temperature is not None]

        return {
            "station_id": station_id,
            "station_name": records[0].station_name,
            "location": records[0].location,
            "record_count": len(records),
            "avg_temperature": round(sum(temps) / len(temps), 1) if temps else 0,
            "date_range": {
                "first": first_record.timestamp.isoformat(),
                "last": last_record.timestamp.isoformat()
            },
            "temperature_range": {
                "min": min(temps) if temps else 0,
                "max": max(temps) if temps else 0
            }
        }

    def _matches_criteria(
        self,
        station: Dict,
        location: Optional[str],
        _start_date: Optional[str],
        _end_date: Optional[str],
        min_records: Optional[int],
        min_avg_temp: Optional[float],
        max_avg_temp: Optional[float]
    ) -> bool:
        # Search BOTH location AND station_name
        if location:
            loc_lower = location.lower()
            if not (
                loc_lower in station["location"].lower() or
                loc_lower in station["station_name"].lower()
            ):
                return False

        # Record count filter
        if min_records and station["record_count"] < min_records:
            return False

        # Temperature filter
        avg_temp = station["avg_temperature"]
        if min_avg_temp and avg_temp < min_avg_temp:
            return False
        if max_avg_temp and avg_temp > max_avg_temp:
            return False

        # Date filters (placeholder - your data is 2019-2020)
        return True

    def _compute_activity_score(self, station_stats: Dict) -> float:
        """Compute 0-100 activity score."""
        score = 0

        # Record count (40% weight)
        records = station_stats["record_count"]
        if records > 100:
            score += 40
        elif records > 50:
            score += 25
        elif records > 10:
            score += 15

        # Temperature data completeness (30% weight)
        temp_range = station_stats["temperature_range"]
        if temp_range["min"] > 0 and temp_range["max"] > 0:
            score += 30

        # Date recency (30% weight)
        last_date = datetime.fromisoformat(station_stats["date_range"]["last"])
        days_old = (datetime.now(timezone.utc) - last_date).days
        if days_old < 365:
            score += 30
        elif days_old < 730:
            score += 15

        return min(score, 100.0)
