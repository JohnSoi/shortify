from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token, hash_api_key
from app.models import UserModel
from app.repositories import ApiKeyRepository, UserRepository
from app.services import AuthService

DbSession = Annotated[AsyncSession, Depends(get_db)]

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)],
) -> UserModel:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация (Bearer token)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истекший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    return user


async def get_optional_actor(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)],
    raw_api_key: Annotated[str | None, Security(api_key_header)],
) -> UserModel | None:
    """
    Определяет пользователя по JWT или X-API-Key.
    Если заголовки не переданы — возвращает None (гостевой режим).
    Если переданы, но невалидны — выбрасывает 401.
    """
    if credentials:
        user_id = decode_access_token(credentials.credentials)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный JWT-токен",
            )
        user = await UserRepository(db).get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
        return user

    if raw_api_key:
        key_repo = ApiKeyRepository(db)
        api_key = await key_repo.get_active_by_hash(hash_api_key(raw_api_key))
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный или отозванный API-ключ",
            )
        await key_repo.touch_last_used(api_key.id)
        return api_key.user

    return None


async def get_required_actor(
    actor: Annotated[UserModel | None, Depends(get_optional_actor)],
) -> UserModel:
    """Требует валидный JWT или X-API-Key."""
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется JWT-токен или заголовок X-API-Key",
        )
    return actor


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
OptionalActor = Annotated[UserModel | None, Depends(get_optional_actor)]
RequiredActor = Annotated[UserModel, Depends(get_required_actor)]
