from fastapi import status

from app.core import DomainError


class UserAlreadyExistsError(DomainError):
    def __init__(self, message: str = "Пользователь с таким email или логином уже существует") -> None:
        super().__init__(message, status.HTTP_409_CONFLICT)


class InvalidCredentialsError(DomainError):
    def __init__(self, message: str = "Неверный email или пароль") -> None:
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)
