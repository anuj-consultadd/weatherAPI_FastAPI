from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Float,
    Index,
    text,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship, foreign
from app.models.database import Base, engine, SessionLocal


class Station(Base):
    __tablename__ = "stations"

    station_id = Column(String(20), primary_key=True)

    weather_data = relationship(
        "WeatherData",
        back_populates="station",
        viewonly=True,
        primaryjoin="Station.station_id == foreign(WeatherData.station_id)",  
    )

    weather_stats = relationship(
        "WeatherStats",
        back_populates="station",
        viewonly=True,
        primaryjoin="Station.station_id == foreign(WeatherStats.station_id)", 
    )

    def __repr__(self):
        return f"<Station {self.station_id}>"


class WeatherData(Base):
    __tablename__ = "weather_data"

    station_id = Column(String(20), primary_key=True)
    record_date = Column(Date, primary_key=True)
    max_temp_celsius = Column(Float, nullable=True)
    min_temp_celsius = Column(Float, nullable=True)
    precipitation_cm = Column(Float, nullable=True)

    station = relationship(
        "Station",
        back_populates="weather_data",
        viewonly=True,
        primaryjoin="Station.station_id == foreign(WeatherData.station_id)",
    )

    __table_args__ = (
        UniqueConstraint(
            "station_id", "record_date", name="uq_weather_data_station_date"
        ),
        Index("ix_weather_data_date", "record_date"),
        Index("ix_weather_data_station_date", "station_id", "record_date"),
    )

    def __repr__(self):
        return f"<WeatherData {self.station_id} {self.record_date}>"


class WeatherStats(Base):
    __tablename__ = "weather_stats"

    station_id = Column(String(20), primary_key=True)  
    year = Column(Integer, primary_key=True)         
    avg_max_temp_celsius = Column(Float, nullable=True)
    avg_min_temp_celsius = Column(Float, nullable=True)
    total_precipitation_cm = Column(Float, nullable=True)
    record_count = Column(Integer, nullable=False, default=0)

    station = relationship(
        "Station",
        back_populates="weather_stats",
        viewonly=True,
        primaryjoin="Station.station_id == foreign(WeatherStats.station_id)",
    )

    def __repr__(self):
        return f"<WeatherStats {self.station_id} {self.year}>"



def create_tables():
    Base.metadata.create_all(bind=engine)



def validate_station_exists(session, station_id):
    station = session.query(Station).filter(Station.station_id == station_id).first()
    if not station:
        raise ValueError(f"Invalid station_id: {station_id} does not exist.")
