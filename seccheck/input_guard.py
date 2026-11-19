"""Проверка пользовательского ввода до сетевого запроса и вывода в терминал."""

import re
from urllib.parse import urlsplit

# Управляющие символы и ANSI-последовательности нельзя ни слать на сервер, ни печатать:
# иначе URL может подменить вывод терминала.
_UNSAFE_CHARS = re.compile(r"[\x00-\x1f\x7f\u202e]")
# Символы, через которые сырой ввод опасен в HTML и в строковых запросах.
_MARKUP_OR_QUOTE = re.compile(r"[<>\"'`\\]")


class InputError(ValueError):
    """Ввод не прошёл базовую проверку."""


def validate_url(raw: str) -> str:
    """Вернуть нормализованный http(s)-URL либо отклонить ввод.

    URL никогда не используется как путь файловой системы и не подставляется
    в SQL или HTML. Разрешены только схемы http и https, без логина и пароля.
    """
    if not isinstance(raw, str):
        raise InputError("URL должен быть строкой")

    candidate = raw.strip()
    if not candidate:
        raise InputError("URL не задан")
    if _UNSAFE_CHARS.search(candidate) or _MARKUP_OR_QUOTE.search(candidate):
        raise InputError("URL содержит недопустимые символы")
    if "%00" in candidate.lower() or ".." in candidate:
        raise InputError("URL похож на попытку подмены пути")

    parts = urlsplit(candidate)
    scheme = parts.scheme.lower()
    if scheme not in {"http", "https"}:
        raise InputError("Допустимы только схемы http и https")
    if parts.username is not None or parts.password is not None:
        raise InputError("Логин и пароль в URL запрещены: не передавайте секреты в адресе")
    if not parts.hostname or parts.hostname in {".", ".."}:
        raise InputError("В URL нет допустимого хоста")

    # Собираем адрес заново из разобранных частей, а не из сырой строки.
    # IPv6 в hostname приходит без скобок — в URL их нужно вернуть.
    host = parts.hostname
    if ":" in host:
        host = f"[{host}]"
    port = f":{parts.port}" if parts.port else ""
    path = parts.path or "/"
    query = f"?{parts.query}" if parts.query else ""
    return f"{scheme}://{host}{port}{path}{query}"


def sanitize_display(value: str, limit: int = 120) -> str:
    """Убрать управляющие символы перед печатью чужого текста в терминал."""
    cleaned = _UNSAFE_CHARS.sub("", value).replace("\n", " ").strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"
