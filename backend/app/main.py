from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from fastapi import APIRouter, status

from app.core import settings, DbSession, register_exception_handlers
from app.api.v1 import api_router, auth_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup: initialize Redis pool / GeoIP reader
    yield
    # Shutdown: close connections


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs" if not settings.is_production else None,
    redoc_url="/api/redoc" if not settings.is_production else None,
    openapi_url="/api/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.BASE_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(api_router)

app.include_router(api_v1_router)


@app.get("/api/health", tags=["System"])
async def health_check(session: DbSession):
    status_query = await session.execute(text("Select TRUE"))
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "database_status": status_query.scalar()
    }
