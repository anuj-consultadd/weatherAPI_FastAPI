from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.models.database import get_db
from app.models import models, schemas
from sqlalchemy import extract

router = APIRouter(
    prefix="/api/weather",
    tags=["weather"],
)

@router.get("/", response_model=schemas.PaginatedWeatherData)
def get_weather_data(
        db: Session = Depends(get_db),
        station_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000)
):
    """
    Get weather data with optional filtering by station ID and date range
    """
    query = db.query(models.WeatherData)

    # Apply filters
    if station_id:
        query = query.filter(models.WeatherData.station_id == station_id)
    if date_from:
        query = query.filter(models.WeatherData.record_date >= date_from)
    if date_to:
        query = query.filter(models.WeatherData.record_date <= date_to)

    # Count total matching records
    total = query.count()

    # Apply pagination
    query = query.order_by(models.WeatherData.record_date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": query.all()
    }

@router.get("/{station_id}", response_model=schemas.PaginatedWeatherData)
def get_weather_data_by_station(
        station_id: str,
        db: Session = Depends(get_db),
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000)
):
    """
    Get weather data for a specific station with optional date filtering
    """
    # Check if station exists
    station = db.query(models.Station).filter(models.Station.station_id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail=f"Station {station_id} not found")

    return get_weather_data(db, station_id, date_from, date_to, page, page_size)
