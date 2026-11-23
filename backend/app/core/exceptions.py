from app.core.consts import SECRET_KEY_MIN_LENGTH


class BadSecretKeyError(ValueError):
    def __init__(self) -> None:
        super().__init__(
            f"В продакшене секретный ключ не может быть пустым или иметь длину менее {SECRET_KEY_MIN_LENGTH} символов"
        )
