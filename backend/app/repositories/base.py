from typing import Type, TypeAlias
from uuid import UUID

from app.models import BaseModel
from sqlalchemy import select


from sqlalchemy.ext.asyncio import AsyncSession

ModelType: TypeAlias = Type[BaseModel]


class BaseRepository:
    _MODEL: ModelType

    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    async def get_by_id(self, user_id: UUID) -> BaseModel | None:
        result = await self.db.execute(select(self._MODEL).where(self._MODEL.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, payload: dict) -> BaseModel:
        new_entity: BaseModel = self._MODEL()

        for field_name, field_value in payload.items():
            if not hasattr(self, field_name):
                continue

            setattr(new_entity, field_name, field_value)

        self.db.add(new_entity)
        await self.db.flush()
        await self.db.refresh(new_entity)

        return new_entity
