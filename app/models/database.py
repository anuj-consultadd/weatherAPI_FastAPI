from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()

def get_db_url():
    """
    Return the database URL from the engine
    """
    from app.config import DATABASE_URL
    return DATABASE_URL

def get_db():
    db = SessionLocal()
    get_db_url()
    try:
        yield db
    finally:
        db.close()
