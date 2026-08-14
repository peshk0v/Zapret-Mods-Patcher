"""Модальные окна выбора папки Zapret и ZIP-архива мода."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Static


class _ZapretTree(DirectoryTree):
    """Дерево, показывающее только каталоги."""

    def filter_paths(self, paths: list[Path]) -> list[Path]:
        return [p for p in paths if p.is_dir()]


class _ModTree(DirectoryTree):
    """Дерево, показывающее каталоги и ZIP-архивы."""

    def filter_paths(self, paths: list[Path]) -> list[Path]:
        return [
            p for p in paths
            if p.is_dir() or (p.is_file() and p.suffix.lower() == ".zip")
        ]


class PickerScreen(ModalScreen[Path | None]):
    """Выбор пути с помощью дерева каталогов."""

    BINDINGS = [("escape", "dismiss_popup", "Отмена")]

    CSS = """
    PickerScreen {
        align: center middle;
    }

    .modal-dialog {
        width: 80;
        height: 70%;
        border: round #ff79c6;
        background: #1b1e27;
        padding: 1 2;
        layout: vertical;
    }

    .modal-title {
        text-align: center;
        text-style: bold;
        color: #ff79c6;
        height: 3;
    }

    #picker-tree {
        height: 1fr;
    }

    .modal-actions {
        height: 5;
        align-horizontal: center;
    }

    .modal-actions Button {
        width: 16;
        height: 3;
        margin: 0 1;
    }
    """

    def __init__(self, kind: str, start: str | Path | None = None) -> None:
        super().__init__()
        self.kind = kind
        start = Path(start) if start else Path.cwd()
        self.start = start if start.is_dir() else Path.cwd()

    def _title(self) -> str:
        if self.kind == "zapret":
            return "Выбери папку Zapret"
        return "Выбери ZIP-архив мода"

    def _tree(self) -> DirectoryTree:
        cls = _ZapretTree if self.kind == "zapret" else _ModTree
        return cls(self.start, id="picker-tree")

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-dialog"):
            yield Static(self._title(), classes="modal-title")
            yield self._tree()
            with Horizontal(classes="modal-actions"):
                yield Button("Выбрать", id="picker-ok", variant="primary")
                yield Button("Отмена", id="picker-cancel", variant="default")

    def _is_acceptable(self, path: Path) -> bool:
        if self.kind == "zapret":
            return path.is_dir()
        return path.is_file() and path.suffix.lower() == ".zip"

    def _choose(self, path: Path) -> None:
        if self._is_acceptable(path):
            self.dismiss(path)

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self._choose(event.path)

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        if self.kind == "zapret":
            self._choose(event.path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "picker-cancel":
            self.dismiss(None)
            return
        if event.button.id == "picker-ok":
            node = self.query_one("#picker-tree", DirectoryTree).cursor_node
            if node is None or node.data is None:
                self.notify("Сначала выбери элемент в дереве.", severity="warning")
                return
            if not self._is_acceptable(node.data.path):
                if self.kind == "mod":
                    self.notify("Выбери ZIP-архив мода.", severity="warning")
                return
            self.dismiss(node.data.path)

    def action_dismiss_popup(self) -> None:
        self.dismiss(None)
