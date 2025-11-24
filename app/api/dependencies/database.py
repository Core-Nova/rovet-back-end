"""
Database dependencies.

Provides database session management for dependency injection.
"""

from typing import Generator

from app.db.session import SessionLocal


def get_db() -> Generator:
    """
    Provide database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Note:
        Session is automatically closed after request completion
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

