import time
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError
from app.core.config import settings

class Base(DeclarativeBase):
    pass

MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds

def create_db_engine():
    retries = 0
    while retries < MAX_RETRIES:
        try:
            print(f"Attempting to connect to database: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
            engine = create_engine(
                str(settings.SQLALCHEMY_DATABASE_URI),
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,   # Recycle connections after 1 hour
                connect_args={"connect_timeout": 10}  # Increased timeout
            )
            # Test the connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print("Successfully connected to the database")
            return engine
        except Exception as e:
            retries += 1
            print(f"Database connection attempt {retries} failed: {str(e)}")
            if retries == MAX_RETRIES:
                print(f"Could not connect to the database after {MAX_RETRIES} retries")
                print(f"Database URI: {settings.SQLALCHEMY_DATABASE_URI}")
                raise Exception(
                    f"Could not connect to the database after {MAX_RETRIES} retries: {str(e)}"
                )
            print(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)

# Try to create the engine, but don't fail if database is not available
try:
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("Database engine and session created successfully")
except Exception as e:
    print(f"Warning: Could not initialize database connection: {e}")
    print("Application will start but database features will not be available")
    engine = None
    SessionLocal = None


def get_db() -> Generator:
    if SessionLocal is None:
        raise Exception("Database connection not available")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 