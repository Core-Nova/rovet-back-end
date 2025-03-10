from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_by_condition(self, condition: dict) -> Optional[ModelType]:
        query = self.db.query(self.model)
        for attr, value in condition.items():
            query = query.filter(getattr(self.model, attr) == value)
        return query.first()

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, schema: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(schema)
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, schema: UpdateSchemaType) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = schema.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> ModelType:
        obj = self.db.query(self.model).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj 