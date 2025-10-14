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
            # Determine if we're using production (Neon) or development database
            is_production = settings.DATABASE_URL is not None
            environment = "production" if is_production else "development"
            
            print(f"Attempting to connect to {environment} database...")
            
            # Configure connection arguments based on environment
            connect_args = {"connect_timeout": 10}
            
            if is_production:
                # For Neon DB, add SSL requirements
                connect_args.update({
                    "sslmode": "require",
                    "options": "-c default_transaction_isolation=read committed"
                })
                print("Using SSL connection for production database")
            else:
                print(f"Connecting to development database: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
            
            engine = create_engine(
                str(settings.SQLALCHEMY_DATABASE_URI),
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,   # Recycle connections after 1 hour
                pool_size=5,         # Smaller pool size for serverless
                max_overflow=0,      # No overflow connections for serverless
                connect_args=connect_args
            )
            
            # Test the connection
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            print(f"Successfully connected to {environment} database")
            return engine
            
        except Exception as e:
            retries += 1
            print(f"Database connection attempt {retries} failed: {str(e)}")
            if retries == MAX_RETRIES:
                print(f"Could not connect to the database after {MAX_RETRIES} retries")
                print(f"Environment: {environment}")
                if is_production:
                    print(f"Production database URL (masked): {str(settings.SQLALCHEMY_DATABASE_URI)[:50]}...")
                else:
                    print(f"Development database URI: {settings.SQLALCHEMY_DATABASE_URI}")
                raise Exception(
                    f"Could not connect to the {environment} database after {MAX_RETRIES} retries: {str(e)}"
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