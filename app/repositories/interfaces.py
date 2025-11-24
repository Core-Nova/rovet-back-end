from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel

from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class IRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Repository interface defining the contract for data access.
    
    All repositories should implement this interface to ensure:
    - Consistent API across repositories
    - Easy mocking for tests
    - Ability to swap implementations
    - Clear separation of concerns
    """

    @abstractmethod
    def get(self, id: Any) -> Optional[ModelType]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_by_condition(self, condition: dict) -> Optional[ModelType]:
        """Get entity by condition."""
        pass

    @abstractmethod
    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """List entities with pagination."""
        pass

    @abstractmethod
    def create(self, schema: CreateSchemaType) -> ModelType:
        """Create new entity."""
        pass

    @abstractmethod
    def update(self, db_obj: ModelType, update_data: Dict[str, Any]) -> ModelType:
        """Update existing entity."""
        pass

    @abstractmethod
    def delete(self, id: int) -> ModelType:
        """Delete entity by ID."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit current transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback current transaction."""
        pass

    @abstractmethod
    def refresh(self, obj: ModelType) -> None:
        """Refresh entity from database."""
        pass

