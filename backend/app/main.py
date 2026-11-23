from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core import settings, DbSession


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


@app.get("/api/health", tags=["System"])
async def health_check(session: DbSession):
    status_query = await session.execute(text("Select TRUE"))
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "database_status": status_query.scalar()
    }
