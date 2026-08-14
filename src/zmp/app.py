"""Интерактивный TUI на базе Textual."""

from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Label, Static
from textual.worker import Worker, WorkerState

from zmp import patcher
from zmp.art import logo_text
from zmp.browser import PickerScreen


class ZMPApp(App[None]):
    """Главный экран приложения."""

    TITLE = "ZMP — Zapret Modifications Patcher"
    SUB_TITLE = "Установка модов на Zapret"

    CSS = """
    Screen {
        background: #0f1116;
    }

    #logo {
        margin: 1 0 0 0;
        text-align: center;
    }

    #main {
        align: center middle;
        padding: 0 2;
    }

    #form {
        width: 100%;
        max-width: 84;
    }

    Label {
        color: #f8f8f2;
        margin-top: 1;
    }

    .path-row {
        height: 3;
        margin-top: 1;
    }

    .path-row Input {
        width: 1fr;
        height: 3;
    }

    .path-row Button {
        width: 12;
        height: 3;
        margin-left: 1;
    }

    #status {
        margin-top: 1;
        color: #bd93f9;
        height: 2;
    }

    #actions {
        margin-top: 2;
        height: 7;
        align-horizontal: center;
    }

    #actions Button {
        width: 24;
        height: 5;
        margin: 0 1;
    }

    #patch {
        background: #50fa7b;
        color: #10141d;
        text-style: bold;
    }

    #patch:disabled {
        background: #3a7a54;
        color: #d0d8e0;
    }

    #quit {
        background: #ff5555;
        color: #10141d;
        text-style: bold;
    }

    #quit:disabled {
        background: #7a3a3a;
        color: #d0d8e0;
    }

    #log {
        width: 100%;
        max-width: 84;
        height: 5;
        margin-top: 1;
        padding: 1;
        background: #191a21;
        color: #f8f8f2;
        border: round #6272a4;
    }
    """

    BINDINGS = [
        ("p", "patch", "Применить мод"),
        ("z", "browse_zapret", "Папка Zapret"),
        ("m", "browse_mod", "ZIP-архив"),
        ("q", "quit", "Выход"),
    ]

    def __init__(
        self, zapret_path: str | None = None, mod_path: str | None = None
    ) -> None:
        super().__init__()
        self._zapret_path = zapret_path
        self._mod_path = mod_path
        self._patching = False

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="main"):
            yield Static(logo_text(), id="logo")
            with Vertical(id="form"):
                yield Label("Путь к папке Zapret")
                with Horizontal(classes="path-row"):
                    yield Input(
                        placeholder="Например: C:\\zapret  или  /home/user/zapret",
                        id="zapret-path",
                    )
                    yield Button("Обзор…", id="browse-zapret")
                yield Label("ZIP-архив мода")
                with Horizontal(classes="path-row"):
                    yield Input(
                        placeholder="Например: mod.zip",
                        id="mod-path",
                    )
                    yield Button("Обзор…", id="browse-mod")
                yield Static("", id="status")
            with Horizontal(id="actions"):
                yield Button("PATCH", id="patch", variant="primary")
                yield Button("Выход", id="quit", variant="error")
            yield Static("", id="log")
        yield Footer()

    def on_mount(self) -> None:
        if self._zapret_path:
            self.query_one("#zapret-path", Input).value = self._zapret_path
        if self._mod_path:
            self.query_one("#mod-path", Input).value = self._mod_path
        self._update_status()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._update_status()

    def _update_status(self) -> None:
        zapret = self.query_one("#zapret-path", Input).value.strip()
        status = self.query_one("#status", Static)

        if not zapret:
            status.update("Укажи путь к папке Zapret, чтобы определить архитектуру")
            return

        try:
            p = patcher.Patcher(zapret)
            arch = p.define()
        except Exception:
            status.update("[red]Не удалось прочитать указанный путь[/]")
            return

        if arch is None:
            status.update("[red]Не удалось определить архитектуру Zapret по этому пути[/]")
            return

        lists = p.get_lists()
        n = len(lists) if lists else 0
        status.update(f"[green]✓ Архитектура: {arch}[/] · [cyan]найдено листов: {n}[/]")

    def _set_patching(self, patching: bool) -> None:
        self._patching = patching
        self.query_one("#patch", Button).disabled = patching
        self.query_one("#quit", Button).disabled = patching
        self.query_one("#browse-zapret", Button).disabled = patching
        self.query_one("#browse-mod", Button).disabled = patching
        self.query_one("#zapret-path", Input).disabled = patching
        self.query_one("#mod-path", Input).disabled = patching

    def action_patch(self) -> None:
        if self._patching:
            return

        zapret = self.query_one("#zapret-path", Input).value.strip()
        mod = self.query_one("#mod-path", Input).value.strip()

        if not zapret or not mod:
            self.notify(
                "Укажи и путь к Zapret, и путь к моду.",
                severity="warning",
                title="Не хватает данных",
            )
            return

        self._set_patching(True)
        self.run_patch(zapret, mod)

    def action_browse_zapret(self) -> None:
        self._open_picker("zapret")

    def action_browse_mod(self) -> None:
        self._open_picker("mod")

    def _open_picker(self, kind: str) -> None:
        if self._patching:
            return

        current = self.query_one("#zapret-path" if kind == "zapret" else "#mod-path", Input).value
        start = current if current else Path.cwd()

        def on_result(path: Path | None) -> None:
            if path is not None:
                self.query_one(
                    "#zapret-path" if kind == "zapret" else "#mod-path", Input
                ).value = str(path)

        self.push_screen(PickerScreen(kind=kind, start=start), callback=on_result)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "patch":
                self.action_patch()
            case "quit":
                self.action_quit()
            case "browse-zapret":
                self.action_browse_zapret()
            case "browse-mod":
                self.action_browse_mod()

    @work(name="patch", thread=True, exit_on_error=False)
    def run_patch(self, zapret: str, mod: str) -> str:
        p = patcher.Patcher(zapret)
        p.patchMod(mod)
        return f"Мод «{Path(mod).name}» успешно установлен"

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != "patch":
            return

        log = self.query_one("#log", Static)

        if event.state is WorkerState.RUNNING:
            self._set_patching(True)
            log.update("[cyan]⏳ Применяю мод…[/]")
        elif event.state is WorkerState.SUCCESS:
            self._set_patching(False)
            message = str(event.worker.result or "Готово")
            log.update(f"[green]✓ {message}[/]")
            self.notify(message, severity="information", title="Готово")
        elif event.state is WorkerState.ERROR:
            self._set_patching(False)
            error = event.worker.error or Exception("Неизвестная ошибка")
            log.update(f"[red]✗ {error}[/]")
            self.notify(str(error), severity="error", title="Ошибка")
