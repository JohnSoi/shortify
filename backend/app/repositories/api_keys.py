import uuid
from datetime import UTC, datetime
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from app.models import ApiKeyModel

from .base import BaseRepository


class ApiKeyRepository(BaseRepository):
    _MODEL = ApiKeyModel

    async def list_by_user(self, user_id: uuid.UUID) -> list[ApiKeyModel]:
        stmt = (
            select(ApiKeyModel)
            .where(ApiKeyModel.user_id == user_id, ApiKeyModel.is_active.is_(True))
            .order_by(ApiKeyModel.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_by_hash(self, key_hash: str) -> ApiKeyModel | None:
        stmt = (
            select(ApiKeyModel)
            .options(joinedload(ApiKeyModel.user))
            .where(ApiKeyModel.key_hash == key_hash, ApiKeyModel.is_active.is_(True))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def touch_last_used(self, key_id: uuid.UUID) -> None:
        stmt = (
            update(ApiKeyModel)
            .where(ApiKeyModel.id == key_id)
            .values(last_used_at=datetime.now(UTC))
        )
        await self.db.execute(stmt)

    async def revoke(self, key_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = (
            update(ApiKeyModel)
            .where(ApiKeyModel.id == key_id, ApiKeyModel.user_id == user_id, ApiKeyModel.is_active.is_(True))
            .values(is_active=False)
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0
