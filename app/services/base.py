from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

from app.db.session import Base
from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, repository: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
        self.repository = repository

    def get(self, id: int) -> Optional[ModelType]:
        return self.repository.get(id=id)

    def get_by_condition(self, condition: dict) -> Optional[ModelType]:
        return self.repository.get_by_condition(condition)

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.repository.list(skip=skip, limit=limit)

    def create(self, schema: CreateSchemaType) -> ModelType:
        return self.repository.create(schema=schema)

    def update(self, id: int, schema: UpdateSchemaType) -> Optional[ModelType]:
        obj = self.repository.get(id=id)
        if obj:
            return self.repository.update(db_obj=obj, schema=schema)
        return None

    def delete(self, id: int) -> Optional[ModelType]:
        obj = self.repository.get(id=id)
        if obj:
            return self.repository.delete(id=id)
        return None 