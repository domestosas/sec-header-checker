"""Цветной отчёт в терминал. Чужие строки печатаются только после очистки."""

from colorama import Fore, Style, init

from seccheck.evaluate import Report
from seccheck.input_guard import sanitize_display

_GRADE_COLOR = {
    "A": Fore.GREEN,
    "B": Fore.GREEN,
    "C": Fore.YELLOW,
    "D": Fore.YELLOW,
    "E": Fore.RED,
    "F": Fore.RED,
}


def _colored(text: str, color: str, width: int) -> str:
    """Красить уже выровненную колонку: коды цвета не должны сдвигать текст."""
    return f"{color}{text:<{width}}{Style.RESET_ALL}"


def render(report: Report) -> str:
    """Собрать текст отчёта с ANSI-цветами."""
    init(autoreset=False)
    grade_color = _GRADE_COLOR[report.grade]
    lines = [
        f"{Style.BRIGHT}Проверка заголовков безопасности{Style.RESET_ALL}",
        f"Запрошен: {sanitize_display(report.requested_url)}",
        f"Итог:     {sanitize_display(report.final_url)}",
        (
            f"Оценка:   {grade_color}{Style.BRIGHT}{report.grade}{Style.RESET_ALL}"
            f"  ({report.present_count}/5)"
        ),
        "",
        f"{'Заголовок':<28} {'Статус':<8} Значение",
        f"{'-' * 28} {'-' * 8} {'-' * 24}",
    ]
    for finding in report.findings:
        if finding.present:
            status = _colored("ЕСТЬ", Fore.GREEN, 8)
            shown = sanitize_display(finding.value, limit=80)
        else:
            status = _colored("НЕТ", Fore.RED, 8)
            shown = f"{Style.DIM}{finding.why}{Style.RESET_ALL}"
        lines.append(f"{finding.name:<28} {status} {shown}")
    lines.append(Style.RESET_ALL)
    return "\n".join(lines)
