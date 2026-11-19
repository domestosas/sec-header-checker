"""Консольная проверка критических HTTP-заголовков безопасности."""

import argparse
import sys

from seccheck.config import request_timeout
from seccheck.evaluate import evaluate
from seccheck.input_guard import InputError, validate_url
from seccheck.probe import ProbeError, fetch_headers
from seccheck.report import render


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Проверяет критические заголовки безопасности и ставит оценку от A до F."
    )
    parser.add_argument("url", help="Адрес сайта, например https://example.com")
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Таймаут запроса в секундах (1–60). Иначе берётся REQUEST_TIMEOUT или 10",
    )
    args = parser.parse_args(argv)

    try:
        url = validate_url(args.url)
        timeout = request_timeout(args.timeout)
        final_url, headers = fetch_headers(url, timeout)
    except InputError as error:
        print(f"Ошибка ввода: {error}", file=sys.stderr)
        return 2
    except ProbeError as error:
        print(f"Ошибка запроса: {error}", file=sys.stderr)
        return 1

    report = evaluate(url, final_url, headers)
    print(render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
