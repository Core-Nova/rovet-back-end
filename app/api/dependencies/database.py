from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Provides a database session using the standard FastAPI generator pattern.
    The session is automatically closed after the request completes.
    
    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            # Use db here
            return items
    """
    if SessionLocal is None:
        raise Exception("Database connection not available")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

