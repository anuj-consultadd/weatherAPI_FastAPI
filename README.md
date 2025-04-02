# Weather Data API

## Overview
A high-performance FastAPI application for ingesting, storing, and analyzing historical weather data with optimized database techniques.

### Features
- Efficiently ingests large volumes of historical weather data.
- High-performance querying of weather records.
- Computes weather statistics across years and stations.
- Uses partitioned data storage for optimized query performance.

## Quick Start
### 1. Clone the Repository
```bash
git clone https://github.com/anuj-consultadd/weatherAPI_FastAPI.git
cd weatherAPI_FastAPI   
```
### 2. Extract the Archive
```bash
unzip Archive.zip -d ./Archive
```
### 3. Set Up a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
### 4. Configure Environment Variables
Create a `.env` file and set the necessary environment variables:
```bash
echo "DATABASE_URL=mysql+pymysql://username:password@localhost/weather_db" > .env
echo "WEATHER_DATA_DIR=/path/to/weatherAPI_FastAPI/Archive/data/wx_data" >> .env
```
### 5. Run the Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
### 6. Access the API Documentation
Visit [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Data Ingestion
To trigger data ingestion, execute:
```bash
curl -X POST "http://localhost:8000/api/ingest"
```

---

## Configuration
### Required Environment Variables
- `DATABASE_URL`: MySQL connection string (e.g., `mysql+pymysql://username:password@localhost/weather_db`)
- `WEATHER_DATA_DIR`: Path to the `wx_data` directory containing weather data files (extracted from `Archive.zip`).

---

## Directory Structure
```
project-root/
├── app/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── config.py
│   ├── main.py
├── .env
├── requirements.txt
├── README.md
```

---

## Advanced Database Techniques
### 1. Table Partitioning by Year
Improves query efficiency by partitioning data per year.
```sql
CREATE TABLE weather_data (
    station_id VARCHAR(20),
    record_date DATE,
    max_temp_celsius FLOAT,
    min_temp_celsius FLOAT,
    precipitation_cm FLOAT
) PARTITION BY RANGE (YEAR(record_date));
```
### 2. Optimized Indexing
Indexes balance read and write performance.
```sql
-- Composite index for station+date queries
CREATE INDEX idx_weather_station_date ON weather_data(station_id, record_date);
-- Index for year-based calculations
CREATE INDEX idx_weather_year ON weather_data((YEAR(record_date)));
```
### 3. Parallel Processing
Utilizes multi-process ingestion for better CPU utilization.

### 4. Strategic Key Disabling
Temporarily disables indexes during bulk inserts for efficiency.
```sql
ALTER TABLE weather_data DISABLE KEYS;
-- Bulk inserts
ALTER TABLE weather_data ENABLE KEYS;
```
### 5. Batch Inserts
Uses `bulk_insert_mappings` with optimized batch sizes.

### 6. Efficient Duplicate Handling
Avoids unnecessary database lookups via in-memory tracking.

---

## Setting Up Table Partitioning
Before ingesting data, you need to partition the `weather_data` table by year for optimized query performance.
Run the following SQL script **after starting your server**:
```sql
ALTER TABLE weather_data
PARTITION BY RANGE (YEAR(record_date)) (
  PARTITION p1985 VALUES LESS THAN (1986),
  PARTITION p1986 VALUES LESS THAN (1987),
  PARTITION p1987 VALUES LESS THAN (1988),
  PARTITION p1988 VALUES LESS THAN (1989),
  PARTITION p1989 VALUES LESS THAN (1990),
  PARTITION p1990 VALUES LESS THAN (1991),
  PARTITION p1991 VALUES LESS THAN (1992),
  PARTITION p1992 VALUES LESS THAN (1993),
  PARTITION p1993 VALUES LESS THAN (1994),
  PARTITION p1994 VALUES LESS THAN (1995),
  PARTITION p1995 VALUES LESS THAN (1996),
  PARTITION p1996 VALUES LESS THAN (1997),
  PARTITION p1997 VALUES LESS THAN (1998),
  PARTITION p1998 VALUES LESS THAN (1999),
  PARTITION p1999 VALUES LESS THAN (2000),
  PARTITION p2000 VALUES LESS THAN (2001),
  PARTITION p2001 VALUES LESS THAN (2002),
  PARTITION p2002 VALUES LESS THAN (2003),
  PARTITION p2003 VALUES LESS THAN (2004),
  PARTITION p2004 VALUES LESS THAN (2005),
  PARTITION p2005 VALUES LESS THAN (2006),
  PARTITION p2006 VALUES LESS THAN (2007),
  PARTITION p2007 VALUES LESS THAN (2008),
  PARTITION p2008 VALUES LESS THAN (2009),
  PARTITION p2009 VALUES LESS THAN (2010),
  PARTITION p2010 VALUES LESS THAN (2011),
  PARTITION p2011 VALUES LESS THAN (2012),
  PARTITION p2012 VALUES LESS THAN (2013),
  PARTITION p2013 VALUES LESS THAN (2014),
  PARTITION p2014 VALUES LESS THAN (2015)
);
```
### Verifying Partitions
To check if the partitions have been created successfully, run:
```sql
SELECT 
  PARTITION_NAME, 
  TABLE_ROWS, 
  PARTITION_EXPRESSION, 
  PARTITION_DESCRIPTION 
FROM 
  INFORMATION_SCHEMA.PARTITIONS 
WHERE 
  TABLE_NAME = 'weather_data';
```
### Query Performance Check
To see how partitioning improves query efficiency, execute:
```sql
EXPLAIN SELECT * FROM weather_data WHERE record_date = '2010-01-01';
```

---

## Performance
- **Data Ingestion**: ~10 seconds for large datasets.
- **Query Performance**: Sub-second response time for most queries.
- **Statistics Calculation**: Optimized aggregation via partitioned queries.

---

## Data Model
The weather data consists of three main entities:
- **Station**: Weather stations with unique identifiers.
- **WeatherData**: Daily weather readings partitioned by year.
- **WeatherStats**: Pre-calculated annual statistics for each station.

---

## API Documentation
| Endpoint                | Method | Description                  |
|-------------------------|--------|------------------------------|
| `/`                     | GET    | API status check             |
| `/api/ingest`           | POST   | Trigger data ingestion       |
| `/api/calculate-stats`  | POST   | Calculate weather statistics |
| `/api/weather/stats`    | GET    | Query weather statistics     |
| `/api/weather/records`  | GET    | Query weather records        |

For complete API details, visit `/docs`.

---