"""
Weather data API endpoints.
"""
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Query, HTTPException, Depends

from src.models.weather_model import WeatherDataModel
from src.loaders.interface import IDataLoader
from ..dependencies import get_db_loader

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/")
async def get_weather_data(
    station_id: str = Query(..., description="Station ID (e.g., '24')"),
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    min_temp: Optional[float] = Query(None, description="Minimum temperature (°C)"),
    max_temp: Optional[float] = Query(None, description="Maximum temperature (°C)"),
    limit: int = Query(100, ge=1, le=1000),
    loader: IDataLoader = Depends(get_db_loader)
) -> dict:
    """
    Get weather data with advanced filtering.

    Parameters:
    - station_id: REQUIRED - Station identifier
    - start_date/end_date: Date range filter (YYYY-MM-DD)
    - min_temp/max_temp: Temperature range filter
    - limit: Maximum records to return (1-1000)
    """
    # Get filtered records
    records = loader.fetch_by_station(station_id)

    if not records:
        raise HTTPException(status_code=404, detail="No data found for this station")

    # Filter by date range
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        # Make timezone-aware if needed
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        records = [r for r in records if r.timestamp >= start_dt]

    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        # Make timezone-aware if needed
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
        records = [r for r in records if r.timestamp <= end_dt]

    # Filter by temperature range
    if min_temp is not None:
        records = [r for r in records if r.temperature >= min_temp]

    if max_temp is not None:
        records = [r for r in records if r.temperature <= max_temp]

    # Convert to dicts and limit
    result = [WeatherDataModel.to_dict(r) for r in records[:limit]]

    return {
        "station_id": station_id,
        "total_records": len(result),
        "filtered_count": len(records),
        "data": result
    }


@router.get("/stats")
async def get_weather_stats(
    station_id: Optional[str] = Query(None),
    loader: IDataLoader = Depends(get_db_loader)
) -> dict:
    """
    Get weather statistics across stations.
    """
    all_records = loader.fetch_all()

    if station_id:
        all_records = [r for r in all_records if r.station_id == station_id]

    if not all_records:
        return {"error": "No data available"}

    temps = [r.temperature for r in all_records]
    return {
        "total_records": len(all_records),
        "avg_temperature": round(sum(temps)/len(temps), 1),
        "min_temperature": min(temps),
        "max_temperature": max(temps),
        "temperature_std": round((sum((x - sum(temps)/len(temps))**2 for x in temps)/len(temps))**0.5, 1),
        "stations_count": len(set(r.station_id for r in all_records))
    }
