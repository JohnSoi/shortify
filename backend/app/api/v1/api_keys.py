import uuid
from fastapi import APIRouter, status
from app.api.deps import AuthServiceDep, CurrentUser
from app.schemas import ApiKeyCreate, ApiKeyCreatedResponse, ApiKeyResponse

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.get("/", response_model=list[ApiKeyResponse])
async def list_keys(current_user: CurrentUser, auth_service: AuthServiceDep):
    return await auth_service.list_api_keys(current_user.id)


@router.post("/", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_key(
    payload: ApiKeyCreate,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
):
    api_key, raw_key = await auth_service.issue_api_key(
        user_id=current_user.id,
        name=payload.name,
    )
    return ApiKeyCreatedResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        is_active=api_key.is_active,
        last_used_at=api_key.last_used_at,
        created_at=api_key.created_at,
        raw_key=raw_key,
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_key(
    key_id: uuid.UUID,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
):
    await auth_service.revoke_api_key(user_id=current_user.id, key_id=key_id)
