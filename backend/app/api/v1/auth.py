from fastapi import APIRouter, status
from app.api.deps import AuthServiceDep, CurrentUser
from app.schemas import TokenResponse, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, auth_service: AuthServiceDep):
    return await auth_service.register_user(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, auth_service: AuthServiceDep):
    return await auth_service.authenticate_user(payload)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return current_user
