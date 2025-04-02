import logging
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from app.models.models import WeatherData, WeatherStats, Station

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_weather_statistics(db: Session):
    """
    Calculate yearly weather statistics for each station with partition-aware queries. 
    """
    logger.info("Starting statistics calculation")

    db.query(WeatherStats).delete()
    db.commit()

    station_ids = db.query(WeatherData.station_id).distinct().all()
    total_stats = 0

    for station_id_tuple in station_ids:
        station_id = station_id_tuple[0]
        logger.info(f"Calculating statistics for station {station_id}")

        stats_query = db.query(
            extract('year', WeatherData.record_date).label('year'),
            func.avg(WeatherData.max_temp_celsius).label('avg_max_temp'),
            func.avg(WeatherData.min_temp_celsius).label('avg_min_temp'),
            func.sum(WeatherData.precipitation_cm).label('total_precip'),
            func.count().label('record_count')
        ).filter(
            WeatherData.station_id == station_id
        ).group_by(
            extract('year', WeatherData.record_date)
        )

        weather_stats = [
            WeatherStats(
                station_id=station_id,
                year=stat.year,
                avg_max_temp_celsius=stat.avg_max_temp,
                avg_min_temp_celsius=stat.avg_min_temp,
                total_precipitation_cm=stat.total_precip,
                record_count=stat.record_count
            ) for stat in stats_query
        ]

        batch_size = 50
        for i in range(0, len(weather_stats), batch_size):
            batch = weather_stats[i:i+batch_size]
            db.bulk_save_objects(batch)
            db.commit()
            total_stats += len(batch)

    logger.info(f"Statistics calculation completed. Total statistics records: {total_stats}")
    return total_stats
