from typing import Literal
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .consts import EnvironmentType, NOT_CHANGED_PREFIX, SECRET_KEY_MIN_LENGTH
from .exceptions import BadSecretKeyError


class Settings(BaseSettings):
    ENVIRONMENT: Literal["development", "testing", "production"] = EnvironmentType.DEV
    DEBUG: bool = False
    BASE_URL: str = "http://localhost:5173"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Database & Redis
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"

    # GeoIP
    GEOIP_DB_PATH: str = "/app/geoip/GeoLite2-City.mmdb"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == EnvironmentType.PROD

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        env = info.data.get("ENVIRONMENT", EnvironmentType.DEV)

        if env == EnvironmentType.PROD and (len(v) < SECRET_KEY_MIN_LENGTH or NOT_CHANGED_PREFIX in v):
            raise BadSecretKeyError()

        return v


settings = Settings()
