import os
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.models import create_tables
from app.routers import weather, stats
from app.services.ingestion import ingest_weather_data
from app.services.statistics import calculate_weather_statistics
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()  
    yield 
    pass 

app = FastAPI(
    title="Weather Data API",
    description="API for accessing historical weather data and statistics",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(weather.router)
app.include_router(stats.router)

@app.get("/")
def read_root():
    return {"message": "Weather Data API is running"}

@app.post("/api/ingest")
def run_data_ingestion(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger the data ingestion process.
    """
    WEATHER_DATA_DIR = os.getenv("WEATHER_DATA_DIR", "/Users/consultadd/Documents/weatherAPI_FastAPI/Archive/data/wx_data")
    if not os.path.exists(WEATHER_DATA_DIR):
        raise HTTPException(status_code=400, detail=f"Data directory not found: {WEATHER_DATA_DIR}")
    
    background_tasks.add_task(ingest_weather_data, db, WEATHER_DATA_DIR)
    return {"message": "Data ingestion started in background"}

@app.post("/api/calculate-stats")
def run_stats_calculation(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger the statistics calculation process.
    """
    background_tasks.add_task(calculate_weather_statistics, db)
    return {"message": "Statistics calculation started in background"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
