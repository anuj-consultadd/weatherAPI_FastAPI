import os
import glob
import logging
import multiprocessing
from functools import partial
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from tqdm import tqdm
from sqlalchemy.sql import exists
from app.models.models import Station, WeatherData
from app.models.database import get_db_url

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_station_file(file_path, db_url, existing_stations, batch_size=10000):
    """
    Process a single weather station file in a separate process
    
    Args:
        file_path: Path to the station data file
        db_url: Database connection URL
        existing_stations: Set of station IDs that already exist in the database
        batch_size: Number of records to insert in each batch
        
    Returns:
        tuple: (total_records_processed, new_records_inserted)
    """
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        station_id = os.path.basename(file_path).split('.')[0]
        total_records = 0
        new_records = 0
        
        if station_id not in existing_stations:
            db.add(Station(station_id=station_id))
            db.commit()
        
        existing_dates = set()
        for date_tuple in db.query(WeatherData.record_date).filter(
            WeatherData.station_id == station_id
        ).all():
            existing_dates.add(date_tuple[0])
        
        batch_records = []
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) != 4:
                    continue
                
                date_str, max_temp, min_temp, precip = parts
                try:
                    record_date = datetime.strptime(date_str, "%Y%m%d").date()
                except ValueError:
                    continue
                
                if record_date in existing_dates:
                    continue
                
                max_temp_celsius = None if int(max_temp) == -9999 else float(int(max_temp)) / 10.0
                min_temp_celsius = None if int(min_temp) == -9999 else float(int(min_temp)) / 10.0
                precipitation_cm = None if int(precip) == -9999 else float(int(precip)) / 100.0
                
                batch_records.append({
                    "station_id": station_id,
                    "record_date": record_date,
                    "max_temp_celsius": max_temp_celsius,
                    "min_temp_celsius": min_temp_celsius,
                    "precipitation_cm": precipitation_cm
                })
                
                if len(batch_records) >= batch_size:
                    if batch_records:
                        db.bulk_insert_mappings(WeatherData, batch_records)
                        db.commit()
                        new_records += len(batch_records)
                    total_records += len(batch_records)
                    batch_records = []
        
        if batch_records:
            db.bulk_insert_mappings(WeatherData, batch_records)
            db.commit()
            new_records += len(batch_records)
            total_records += len(batch_records)
            
        return total_records, new_records
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        db.rollback()
        return 0, 0
    finally:
        db.close()

def ingest_weather_data(db: Session, data_dir: str):
    """
    Ingest weather data from text files into the database using parallel processing.
    Skip already existing records.
    """
    start_time = datetime.now()
    logger.info(f"Starting parallel data ingestion at {start_time}")
    
    from app.config import DATABASE_URL
    db_url = DATABASE_URL
    
    log_url = db_url.replace("://", "://***:***@") if "://" in db_url else db_url
    logger.info(f"Using database connection: {log_url}")
    

    file_paths = glob.glob(os.path.join(data_dir, "*.txt"))
    logger.info(f"Found {len(file_paths)} station files to process")
    
    existing_stations = set()
    for station_tuple in db.query(Station.station_id).all():
        existing_stations.add(station_tuple[0])
    
    try:
        logger.info("Disabling keys...")
        db.execute(text("ALTER TABLE weather_data DISABLE KEYS"))
        
        num_processes = min(multiprocessing.cpu_count(), len(file_paths))
        logger.info(f"Using {num_processes} parallel processes")
        
        total_records = 0
        new_records = 0
        
        with multiprocessing.Pool(processes=num_processes) as pool:
            process_func = partial(
                process_station_file, 
                db_url=db_url, 
                existing_stations=existing_stations,
                batch_size=10000
            )
            
            results = list(tqdm(
                pool.imap(process_func, file_paths),
                total=len(file_paths),
                desc="Processing station files"
            ))
            
            for result in results:
                file_total, file_new = result
                total_records += file_total
                new_records += file_new
        
        logger.info(f"Processed {total_records} records, {new_records} new records inserted")
        
    finally:
        logger.info("Re-enabling keys...")
        db.execute(text("ALTER TABLE weather_data ENABLE KEYS"))
    
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Parallel data ingestion completed at {end_time}")
    logger.info(f"Total duration: {duration}")
    
    return total_records