"""Terminal rendering helpers for GameForge."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Mapping


CYBER_WIDTH = 76
LOGO_WIDTH = 18
RESET = "\033[0m"
CYAN = "\033[38;5;51m"
MAGENTA = "\033[38;5;201m"
GREEN = "\033[38;5;82m"
YELLOW = "\033[38;5;220m"
RED = "\033[38;5;203m"
DIM = "\033[2m"
BRIGHT = "\033[1m"


def show_title(title: str, subtitle: str | None = None) -> None:
    print()
    print(f"{CYAN}╔" + "═" * CYBER_WIDTH + f"╗{RESET}")
    logo_lines = _logo_lines()
    banner_rows = [
        _split_banner_line(logo_lines[0], " " * (CYBER_WIDTH - LOGO_WIDTH)),
        _center_row(title.upper(), BRIGHT + MAGENTA),
        _split_banner_line(logo_lines[1], " " * (CYBER_WIDTH - LOGO_WIDTH)),
        _split_banner_line(logo_lines[2], " " * (CYBER_WIDTH - LOGO_WIDTH)),
        _split_banner_line(logo_lines[3], " " * (CYBER_WIDTH - LOGO_WIDTH)),
        _center_row(subtitle or "", DIM) if subtitle else _split_banner_line(logo_lines[4], " " * (CYBER_WIDTH - LOGO_WIDTH)),
        _split_banner_line(logo_lines[5], " " * (CYBER_WIDTH - LOGO_WIDTH)),
    ]

    for row in banner_rows:
        print(row)
    print(f"{CYAN}╠" + "═" * CYBER_WIDTH + f"╣{RESET}")


def show_menu(options: Iterable[str]) -> None:
    for index, option in enumerate(options, start=1):
        print(f"{CYAN}{index:>2}.{RESET} {option}")
    print(f"{CYAN}╚" + "═" * CYBER_WIDTH + f"╝{RESET}")


def show_message(label: str, message: str) -> None:
    print(f"{GREEN}[ {label.upper()} ]{RESET} {message}")


def show_error(message: str) -> None:
    print(f"{RED}[ ERROR ]{RESET} {message}")


def show_empty(message: str) -> None:
    print(f"{YELLOW}[ VOID ]{RESET} {message}")


def show_record(title: str, record: Mapping[str, Any]) -> None:
    show_panel(title.upper(), [f"{format_key(key)}: {format_value(value)}" for key, value in record.items()])


def show_records(title: str, records: Iterable[Mapping[str, Any]]) -> None:
    records = list(records)
    if not records:
        show_empty("No records found.")
        return
    print(f"{MAGENTA}⟦ {title.upper()} ⟧{RESET}")
    for index, record in enumerate(records, start=1):
        print(f"{CYAN}◆ ENTRY {index}{RESET}")
        for key, value in record.items():
            print(f"  ▸ {format_key(key)}: {format_value(value)}")
        print("  " + f"{DIM}" + "·" * (CYBER_WIDTH - 2) + f"{RESET}")


def show_stats(title: str, stats: Mapping[str, Any]) -> None:
    show_panel(title.upper(), [f"{format_key(key)}: {format_value(value)}" for key, value in stats.items()])


def show_panel(title: str, lines: Iterable[str]) -> None:
    print(f"{CYAN}╔" + "═" * CYBER_WIDTH + f"╗{RESET}")
    print(_center_line(f"{BRIGHT}{MAGENTA}{title}{RESET}"))
    print(f"{CYAN}╠" + "═" * CYBER_WIDTH + f"╣{RESET}")
    for line in lines:
        print(f"{CYAN}▸{RESET} {line}")
    print(f"{CYAN}╚" + "═" * CYBER_WIDTH + f"╝{RESET}")


def show_progress(label: str, value: float | int, max_value: float | int = 100) -> None:
    max_value = max(max_value, 1)
    ratio = max(0.0, min(float(value) / float(max_value), 1.0))
    filled = int(ratio * 24)
    bar = f"{GREEN}{'█' * filled}{DIM}{'░' * (24 - filled)}{RESET}"
    print(f"{CYAN}{label:<18}{RESET} [{bar}] {ratio * 100:5.1f}%")


def show_chip(label: str, value: Any, tone: str = CYAN) -> None:
    print(f"{tone}[ {label.upper()} ]{RESET} {format_value(value)}")


def format_key(value: str) -> str:
    return value.replace("_", " ").title()


def format_value(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return "YES" if value else "NO"
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, list):
        return ", ".join(format_value(item) for item in value) or "N/A"
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{k}: {format_value(v)}" for k, v in value.items()) + " }"
    return str(value)


def _center_line(text: str) -> str:
    usable_width = CYBER_WIDTH
    inner = f" {text} "
    if len(inner) > usable_width:
        inner = inner[:usable_width]
    padding = usable_width - len(inner)
    left = padding // 2
    right = padding - left
    return f"║{' ' * left}{inner}{' ' * right}║"


def _split_banner_line(left: str, right: str) -> str:
    left_block = left.ljust(LOGO_WIDTH)
    right_block = right[: CYBER_WIDTH - LOGO_WIDTH].ljust(CYBER_WIDTH - LOGO_WIDTH)
    return f"║{left_block}{right_block}║"


def _center_row(text: str, style: str = "") -> str:
    inner = text.strip()
    padding = CYBER_WIDTH - len(inner)
    left = max(0, padding // 2)
    right = max(0, padding - left)
    content = f"{' ' * left}{inner}{' ' * right}"
    if style:
        return f"║{style}{content}{RESET}║"
    return f"║{content}║"


def _logo_lines() -> list[str]:
    return [
        r"   ▄███████▄   ",
        r"  ▄█░░░░░░░░█▄  ",
        r" ▄█░  ▄██▄  ░█▄ ",
        r" █▀░  █  █  ░▀█ ",
        r" █░   ▀██▀   ░█ ",
        r" ▀█▄░      ░▄█▀ ",
        r"   ▀████████▀   ",
    ]