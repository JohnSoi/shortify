from enum import StrEnum


class EnvironmentType(StrEnum):
    PROD = "production"
    TEST = "testing"
    DEV = "development"


NOT_CHANGED_PREFIX: str = "change-me"
SECRET_KEY_MIN_LENGTH: int = 32
API_KEY_PREFIX: str = "sk_live_"
