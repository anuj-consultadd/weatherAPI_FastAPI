from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.models.database import get_db
from app.models import models, schemas
from sqlalchemy import extract

router = APIRouter(
    prefix="/api/weather/stats",
    tags=["weather stats"],
)

@router.get("/", response_model=schemas.PaginatedWeatherStats) 
def get_weather_stats(
        db: Session = Depends(get_db),
        station_id: Optional[str] = None,
        year: Optional[int] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000)
):
    """
    Get weather statistics with optional filtering by station ID and year
    Optimized for partitioned queries
    """
    query = db.query(models.WeatherStats)

    if station_id:
        query = query.filter(models.WeatherStats.station_id == station_id)
    if year:
        query = query.filter(models.WeatherStats.year == year)

    total = query.count()
    
    query = query.order_by(models.WeatherStats.year.desc(), models.WeatherStats.station_id)
    query = query.offset((page - 1) * page_size).limit(page_size)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": query.all()
    }

@router.get("/{station_id}", response_model=schemas.PaginatedWeatherStats)
def get_weather_stats_by_station(
        station_id: str,
        db: Session = Depends(get_db),
        year: Optional[int] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000)
):
    """
    Get weather statistics for a specific station with optional year filtering
    Optimized for partitioned queries
    """
    station = db.query(models.Station).filter(models.Station.station_id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail=f"Station {station_id} not found")

    return get_weather_stats(db, station_id, year, page, page_size)
