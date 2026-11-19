"""Настройки запуска. Секретов нет: ключи и пароли утилита не использует."""

import os

from dotenv import load_dotenv

from seccheck.input_guard import InputError

_DEFAULT_TIMEOUT = 10.0
_MIN_TIMEOUT = 1.0
_MAX_TIMEOUT = 60.0


def request_timeout(cli_value: float | None) -> float:
    """Таймаут запроса: флаг командной строки важнее переменной REQUEST_TIMEOUT."""
    load_dotenv()
    if cli_value is not None:
        return _check_timeout(cli_value)

    raw = os.environ.get("REQUEST_TIMEOUT", "").strip()
    if not raw:
        return _DEFAULT_TIMEOUT
    try:
        return _check_timeout(float(raw))
    except ValueError as error:
        raise InputError("REQUEST_TIMEOUT должен быть числом секунд") from error


def _check_timeout(value: float) -> float:
    if value < _MIN_TIMEOUT or value > _MAX_TIMEOUT:
        raise InputError(
            f"Таймаут должен быть от {_MIN_TIMEOUT:g} до {_MAX_TIMEOUT:g} секунд"
        )
    return value
