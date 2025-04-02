from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class StationBase(BaseModel):
    station_id: str

class Station(StationBase):
    class Config:
        orm_mode = True

class WeatherDataBase(BaseModel):
    station_id: str
    record_date: date
    max_temp_celsius: Optional[float] = None
    min_temp_celsius: Optional[float] = None
    precipitation_cm: Optional[float] = None

class WeatherData(WeatherDataBase):

    class Config:
        orm_mode = True

class WeatherStatsBase(BaseModel):
    station_id: str
    year: int
    avg_max_temp_celsius: Optional[float] = None
    avg_min_temp_celsius: Optional[float] = None
    total_precipitation_cm: Optional[float] = None
    record_count: int

class WeatherStats(WeatherStatsBase):
    class Config:
        orm_mode = True

class PaginatedWeatherData(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[WeatherData]

class PaginatedWeatherStats(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[WeatherStats]
