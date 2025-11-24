from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

from app.db.session import Base
from app.repositories.interfaces import IRepository

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(IRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository implementation using SQLAlchemy.
    
    Provides common CRUD operations and transaction management.
    All database operations are encapsulated here - services should
    never access the database session directly.
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        """Get entity by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_by_condition(self, condition: dict) -> Optional[ModelType]:
        """Get entity by condition."""
        query = self.db.query(self.model)
        for attr, value in condition.items():
            query = query.filter(getattr(self.model, attr) == value)
        return query.first()

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """List entities with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, schema: CreateSchemaType) -> ModelType:
        """
        Create new entity.
        
        Note: Does NOT auto-commit. Use commit() explicitly or in a transaction context.
        """
        obj_in_data = jsonable_encoder(schema)
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, update_data: Dict[str, Any]) -> ModelType:
        """
        Update existing entity with provided data.
        
        Args:
            db_obj: Entity to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated entity
            
        Note: Does NOT auto-commit. Use commit() explicitly or in a transaction context.
        """
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        return db_obj

    def delete(self, id: int) -> ModelType:
        """
        Delete entity by ID.
        
        Note: Does NOT auto-commit. Use commit() explicitly or in a transaction context.
        """
        obj = self.db.query(self.model).get(id)
        if obj:
            self.db.delete(obj)
        return obj

    def commit(self) -> None:
        """Commit current transaction."""
        self.db.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        self.db.rollback()

    def refresh(self, obj: ModelType) -> None:
        """Refresh entity from database."""
        self.db.refresh(obj) 