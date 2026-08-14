"""Декоративный квадрат из разноцветных пикселей."""

from __future__ import annotations

import colorsys

from rich.text import Text

_SIZE = 16
_BLOCK = "██"
_BORDER = "#44475a"


def _hsv_to_hex(h: float, s: float, v: float) -> str:
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def logo_text() -> Text:
    """Квадрат из пикселей: тёмная рамка и диагональный градиент внутри."""
    text = Text()
    for y in range(_SIZE):
        for x in range(_SIZE):
            if x in (0, _SIZE - 1) or y in (0, _SIZE - 1):
                text.append(_BLOCK, style=_BORDER)
            else:
                hue = ((x - 1) + (y - 1)) / (2 * (_SIZE - 2))
                text.append(_BLOCK, style=_hsv_to_hex(hue, 0.85, 1.0))
        if y != _SIZE - 1:
            text.append("\n")
    return text
