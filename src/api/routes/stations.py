"""
Stations API endpoints with StationSelector service.
"""
from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from src.models.weather_model import WeatherDataModel
from src.loaders.interface import IDataLoader
from src.services.station_selector import StationSelector  # ✅ NEW IMPORT
from ..dependencies import get_db_loader

router = APIRouter(prefix="/stations", tags=["stations"])

@router.get("")
async def get_stations(
    location: Optional[str] = Query(None, description="Filter by location"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    min_records: Optional[int] = Query(None, description="Minimum records"),
    min_avg_temp: Optional[float] = Query(None, description="Min avg temp (°C)"),
    max_avg_temp: Optional[float] = Query(None, description="Max avg temp (°C)"),
    limit: int = Query(50, ge=1, le=100, description="Max stations to return"),
    loader: IDataLoader = Depends(get_db_loader)
) -> List[dict]:
    """
    Get list of weather stations with advanced filtering.
    
    Query parameters:
    - location: Filter by city/region (e.g., "Toulouse")
    - start_date/end_date: Date range (YYYY-MM-DD)
    - min_records: Minimum records per station
    - min_avg_temp/max_avg_temp: Temperature range (°C)
    - limit: Maximum stations (1-100)
    """
    # ✅ USE StationSelector instead of inline logic
    selector = StationSelector(loader)
    return selector.get_stations_with_criteria(
        location=location,
        start_date=start_date,
        end_date=end_date,
        min_records=min_records,
        min_avg_temp=min_avg_temp,
        max_avg_temp=max_avg_temp,
        limit=limit
    )

@router.get("/{station_id}")
async def get_station_details(
    station_id: str,
    loader: IDataLoader = Depends(get_db_loader)
) -> dict:
    """
    Get detailed information for a specific station.
    """
    records = loader.fetch_by_station(station_id)
    
    if not records:
        return {"error": "Station not found or no data available"}
    
    station = {
        "station_id": station_id,
        "station_name": records[0].station_name,
        "location": records[0].location,
        "total_records": len(records),
        "avg_temperature": round(sum(r.temperature for r in records)/len(records), 1),
        "temperature_range": {
            "min": min(r.temperature for r in records),
            "max": max(r.temperature for r in records)
        },
        "date_range": {
            "first": min(records, key=lambda x: x.timestamp).timestamp.isoformat(),
            "last": max(records, key=lambda x: x.timestamp).timestamp.isoformat()
        },
        "latest_record": WeatherDataModel.to_dict(max(records, key=lambda x: x.timestamp))
    }
    
    return station

# ✅ NEW ACTIVITY ENDPOINT - ADD THIS
@router.get("/{station_id}/activity")
async def get_station_activity(
    station_id: str,
    loader: IDataLoader = Depends(get_db_loader)
) -> dict:
    """
    Get detailed activity score for a station (0-100).
    """
    selector = StationSelector(loader)
    return selector.get_station_activity_score(station_id)
