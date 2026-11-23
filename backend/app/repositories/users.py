import uuid
from sqlalchemy import or_, select
from app.models import UserModel
from .base import BaseRepository


class UserRepository(BaseRepository):
    _MODEL = UserModel

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.db.execute(select(UserModel).where(UserModel.email == email.lower()))
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, email: str, username: str) -> UserModel | None:
        stmt = select(UserModel).where(
            or_(UserModel.email == email.lower(), UserModel.username == username)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()