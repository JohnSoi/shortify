from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.consts import SECRET_KEY_MIN_LENGTH


class BadSecretKeyError(ValueError):
    def __init__(self) -> None:
        super().__init__(
            f"В продакшене секретный ключ не может быть пустым или иметь длину менее {SECRET_KEY_MIN_LENGTH} символов"
        )

class DomainError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(DomainError):
    def __init__(self, message: str = "Ресурс не найден") -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
