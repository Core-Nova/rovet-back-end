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
            engine = create_engine(
                str(settings.SQLALCHEMY_DATABASE_URI),
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,   # Recycle connections after 1 hour
                connect_args={"connect_timeout": 5}
            )
            engine.connect()
            print("Successfully connected to the database")
            return engine
        except OperationalError as e:
            retries += 1
            if retries == MAX_RETRIES:
                raise Exception(
                    f"Could not connect to the database after {MAX_RETRIES} retries: {str(e)}"
                )
            print(f"Database connection attempt {retries} failed. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 