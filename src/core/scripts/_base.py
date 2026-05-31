"""内置脚本基类 — 注册与调度。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
import logging

import pydirectinput as pdi

from core.packages.visual import click, wait_image_appear, wait_image_disappear, scroll
from core.packages.window import WindowInfo

logger = logging.getLogger(__name__)

_registry: dict[str, Callable] = {}


@dataclass
class BuiltinContext:
    """传递给内置脚本的上下文。"""
    resolve: Callable[[str], str]   # 将相对路径解析为绝对路径
    params: dict[str, Any] = field(default_factory=dict)
    window_info: WindowInfo | None = None

    def press(self, key: str) -> None:
        pdi.press(key)

    def click(self, image: str, **kw: Any) -> bool:
        return click(self.resolve(image), **kw)

    def wait(self, image: str, **kw: Any) -> Optional[Any]:
        return wait_image_appear(self.resolve(image), **kw)

    def wait_disappear(self, image: str, **kw: Any) -> bool:
        return wait_image_disappear(self.resolve(image), **kw)

    def scroll(self, amount: int) -> None:
        scroll(amount)


def register(name: str) -> Callable:
    """装饰器：将函数注册为内置脚本。"""
    def decorator(func: Callable) -> Callable:
        _registry[name] = func
        return func
    return decorator


def get_builtin(name: str) -> Callable | None:
    return _registry.get(name)


def list_builtins() -> list[str]:
    return list(_registry.keys())
