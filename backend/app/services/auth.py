import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotFoundError,
)
from app.core.security import (
    create_access_token,
    generate_api_key,
    hash_password,
    verify_password,
)
from app.models import UserModel, ApiKeyModel
from .exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.repositories import ApiKeyRepository, UserRepository
from app.schemas import TokenResponse, UserLogin, UserRegister


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.api_key_repo = ApiKeyRepository(db)

    async def register_user(self, payload: UserRegister) -> UserModel:
        existing = await self.user_repo.get_by_email_or_username(
            email=payload.email,
            username=payload.username,
        )
        if existing:
            raise UserAlreadyExistsError()

        hashed = hash_password(payload.password)
        return await self.user_repo.create({'email': payload.email, 'username': payload.username, 'hashed_password': hashed})

    async def authenticate_user(self, payload: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise InvalidCredentialsError()

        token = create_access_token(user_id=user.id)
        return TokenResponse(access_token=token)

    async def issue_api_key(self, user_id: uuid.UUID, name: str) -> tuple[ApiKeyModel, str]:
        raw_key, prefix, key_hash = generate_api_key()
        api_key = await self.api_key_repo.create(
            {'user_id': user_id, 'name': name, 'key_prefix': prefix, 'key_hash': key_hash}
            )
        return api_key, raw_key

    async def list_api_keys(self, user_id: uuid.UUID) -> list[ApiKeyModel]:
        return await self.api_key_repo.list_by_user(user_id)

    async def revoke_api_key(self, user_id: uuid.UUID, key_id: uuid.UUID) -> None:
        revoked = await self.api_key_repo.revoke(key_id=key_id, user_id=user_id)
        if not revoked:
            raise NotFoundError("API-ключ не найден или уже отозван")
