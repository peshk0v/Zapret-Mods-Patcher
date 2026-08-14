"""Точка входа ZMP.

Без аргументов открывается интерактивный TUI.
С двумя аргументами (ZAPRET_PATH и MOD_PATH) мод применяется сразу в консоли.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from zmp import patcher
from zmp.app import ZMPApp
from zmp.art import logo_text


def _run_console(zapret_path: str, mod_path: str) -> int:
    console = Console()

    console.print(logo_text(), justify="center")
    console.print(
        Panel.fit(
            "Zapret Modifications Patcher",
            style="bold cyan",
            border_style="cyan",
        ),
        justify="center",
    )
    console.print()

    try:
        p = patcher.Patcher(zapret_path)
    except Exception as e:
        console.print(
            Panel(f"[red]{e}[/]", title="Ошибка", border_style="red")
        )
        return 1

    arch = p.define()
    if arch is None:
        console.print(
            Panel.fit(
                "Не удалось определить архитектуру Zapret по указанному пути:\n"
                f"{Path(zapret_path).resolve()}",
                title="Ошибка",
                border_style="red",
            )
        )
        return 1

    lists = p.get_lists()
    if lists is None:
        console.print(
            Panel.fit(
                f"Архитектура «{arch}» определена, но каталог с листами не найден.",
                title="Ошибка",
                border_style="red",
            )
        )
        return 1

    console.print(
        Panel.fit(
            f"[bold]Архитектура:[/] {arch}\n"
            f"[bold]Найдено листов:[/] {len(lists)}",
            title="Обнаружено",
            border_style="cyan",
        )
    )
    console.print()

    error: str | None = None
    with console.status("[bold cyan]Применяю мод…[/]"):
        try:
            p.patchMod(mod_path)
        except FileNotFoundError as e:
            error = str(e)
        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = f"Неожиданная ошибка: {e}"

    if error is not None:
        console.print(Panel(f"[red]{error}[/]", title="Ошибка", border_style="red"))
        return 1

    console.print(
        Panel.fit(
            "[bold green]Мод успешно установлен![/]\n\n"
            f"[bold]Архитектура:[/] {arch}\n"
            f"[bold]Мод:[/] {Path(mod_path).name}",
            title="Готово",
            border_style="green",
        )
    )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zmp",
        description="Zapret Modifications Patcher — кросплатформенный TUI "
        "для установки модов на Zapret.",
        epilog=(
            "Запусти без аргументов, чтобы открыть интерактивный интерфейс, "
            "или укажи сразу оба пути, чтобы применить мод без TUI."
        ),
    )
    parser.add_argument(
        "zapret_path",
        nargs="?",
        metavar="ZAPRET_PATH",
        help="путь к папке с Zapret",
    )
    parser.add_argument(
        "mod_path",
        nargs="?",
        metavar="MOD_PATH",
        help="путь к ZIP-архиву мода",
    )
    return parser


def cli() -> None:
    parser = _parser()
    args = parser.parse_args()

    if bool(args.zapret_path) != bool(args.mod_path):
        console = Console()
        console.print(
            Panel(
                "[yellow]Укажи либо оба пути сразу, либо ни одного.[/]\n\n"
                "Без аргументов откроется интерактивный интерфейс.",
                title="Неверные аргументы",
                border_style="yellow",
            )
        )
        console.print()
        parser.print_help()
        raise SystemExit(1)

    if args.zapret_path and args.mod_path:
        raise SystemExit(_run_console(args.zapret_path, args.mod_path))

    ZMPApp().run()


if __name__ == "__main__":
    cli()
