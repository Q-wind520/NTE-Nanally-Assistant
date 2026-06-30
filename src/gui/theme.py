from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

_theme_override: str | None = None  # None=system, "dark", "light"
_accent_color: str = "#6b9fed"  # default blue


def _is_dark_mode() -> bool:
    if _theme_override == "dark":
        return True
    if _theme_override == "light":
        return False
    cs = QApplication.styleHints().colorScheme()
    return cs == Qt.ColorScheme.Dark


def _card_bg() -> str:
    return "#3c3c3c" if _is_dark_mode() else "#f5f5f5"


def _text_color() -> str:
    return "#e0e0e0" if _is_dark_mode() else "#333333"


def _page_bg() -> str:
    return "#1e1e1e" if _is_dark_mode() else "#f0f0f0"


def _sidebar_style() -> str:
    accent = _accent_color
    if _is_dark_mode():
        return f"""
QPushButton {{
    background: #2b2b2b;
    color: #cccccc;
    border: none;
    border-left: 3px solid transparent;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
}}
QPushButton:hover {{
    background: #3c3c3c;
    color: #ffffff;
}}
QPushButton:checked {{
    background: #353535;
    color: #ffffff;
    border-left: 3px solid {accent};
}}
"""
    return f"""
QPushButton {{
    background: transparent;
    color: #555555;
    border: none;
    border-left: 3px solid transparent;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
}}
QPushButton:hover {{
    background: #c8c8c8;
    color: #000000;
}}
QPushButton:checked {{
    background: #d8d8d8;
    color: #000000;
    border-left: 3px solid {accent};
}}
"""


def _global_qss() -> str:
    accent = _accent_color
    text_col = _text_color()
    if _is_dark_mode():
        return f"""
QLabel {{
    color: #e0e0e0;
}}
QTextEdit {{
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid {accent};
}}
QComboBox {{
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid {accent};
    padding: 4px 8px;
}}
QComboBox QAbstractItemView {{
    background-color: #2d2d2d;
    color: #e0e0e0;
    selection-background-color: #3c3c3c;
}}
QSpinBox {{
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid {accent};
    padding: 4px;
}}
QPushButton {{
    background-color: #3c3c3c;
    color: #e0e0e0;
    border: 1px solid {accent};
    padding: 6px 16px;
    border-radius: 4px;
}}
QPushButton:hover {{
    background-color: #4a4a4a;
}}
QPushButton:disabled {{
    color: #666666;
    background-color: #2d2d2d;
}}
QStatusBar {{
    background-color: {accent};
    color: {text_col};
}}
QLineEdit {{
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid {accent};
    padding: 4px;
}}
"""
    return f"""
QLabel {{
    color: #333333;
}}
QTextEdit {{
    background-color: #ffffff;
    color: #333333;
    border: 1px solid {accent};
}}
QComboBox {{
    background-color: #ffffff;
    color: #333333;
    border: 1px solid {accent};
    padding: 4px 8px;
}}
QComboBox QAbstractItemView {{
    background-color: #ffffff;
    color: #333333;
    selection-background-color: #d0d0d0;
}}
QSpinBox {{
    background-color: #ffffff;
    color: #333333;
    border: 1px solid {accent};
    padding: 4px;
}}
QPushButton {{
    background-color: #ffffff;
    color: #333333;
    border: 1px solid {accent};
    padding: 6px 16px;
    border-radius: 4px;
}}
QPushButton:hover {{
    background-color: #e8e8e8;
}}
QPushButton:disabled {{
    color: #999999;
    background-color: #f5f5f5;
}}
QStatusBar {{
    background-color: {accent};
    color: {text_col};
}}
QLineEdit {{
    background-color: #ffffff;
    color: #333333;
    border: 1px solid {accent};
    padding: 4px;
}}
"""


def set_theme_override(value: str | None) -> None:
    global _theme_override
    _theme_override = value


def set_accent_color(value: str) -> None:
    global _accent_color
    _accent_color = value

