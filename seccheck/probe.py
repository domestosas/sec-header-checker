"""Один HTTP-запрос: нужны только заголовки ответа, тело не читается."""

import requests

from seccheck.input_guard import sanitize_display, validate_url

_USER_AGENT = "sec-header-checker/1.0"


class ProbeError(RuntimeError):
    """Сайт не ответил так, чтобы заголовки можно было оценить."""


def fetch_headers(url: str, timeout: float) -> tuple[str, dict[str, str]]:
    """Запросить URL и вернуть итоговый адрес вместе с заголовками ответа."""
    session = requests.Session()
    session.max_redirects = 5
    try:
        response = session.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            stream=True,
            headers={"User-Agent": _USER_AGENT},
        )
    except requests.Timeout as error:
        raise ProbeError(f"Превышен таймаут {timeout:g} с") from error
    except requests.RequestException as error:
        detail = sanitize_display(str(error), limit=200)
        raise ProbeError(f"Не удалось подключиться к сайту: {detail}") from error

    try:
        # Редирект мог увести на другую схему — её тоже проверяем.
        final_url = validate_url(response.url)
        headers = {name: value for name, value in response.headers.items()}
        return final_url, headers
    finally:
        response.close()
        session.close()
