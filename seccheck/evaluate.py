"""Оценка наличия критических заголовков и буква защиты."""

from dataclasses import dataclass

# Порядок фиксирован: так отчёт всегда выглядит одинаково.
REQUIRED_HEADERS: tuple[str, ...] = (
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
)

_GRADES: dict[int, str] = {5: "A", 4: "B", 3: "C", 2: "D", 1: "E", 0: "F"}

_WHY: dict[str, str] = {
    "Content-Security-Policy": "ограничивает источники скриптов и других ресурсов",
    "Strict-Transport-Security": "удерживает браузер на HTTPS",
    "X-Frame-Options": "мешает встроить страницу во фрейм",
    "X-Content-Type-Options": "запрещает браузеру угадывать MIME-тип",
    "Referrer-Policy": "ограничивает, какой Referer уходит на другие сайты",
}


@dataclass(frozen=True)
class HeaderFinding:
    name: str
    present: bool
    value: str
    why: str


@dataclass(frozen=True)
class Report:
    requested_url: str
    final_url: str
    findings: tuple[HeaderFinding, ...]
    present_count: int
    grade: str


def evaluate(requested_url: str, final_url: str, headers: dict[str, str]) -> Report:
    """Сопоставить ответ со списком критических заголовков."""
    folded = {name.lower(): value for name, value in headers.items()}
    findings: list[HeaderFinding] = []
    for name in REQUIRED_HEADERS:
        raw = folded.get(name.lower(), "")
        value = raw.strip()
        findings.append(
            HeaderFinding(
                name=name,
                present=bool(value),
                value=value,
                why=_WHY[name],
            )
        )
    present_count = sum(item.present for item in findings)
    return Report(
        requested_url=requested_url,
        final_url=final_url,
        findings=tuple(findings),
        present_count=present_count,
        grade=_GRADES[present_count],
    )
