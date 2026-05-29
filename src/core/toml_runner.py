"""TOML 外置脚本执行引擎 — 读取并执行声明式 TOML 脚本。"""

from __future__ import annotations

import time
import tomllib
from pathlib import Path
from typing import Any

import pydirectinput as pdi

from core.packages.visual import click, wait_image_appear, wait_image_disappear, scroll
from core.packages.window import activate_window, get_hwnd, get_window


def run_toml_script(toml_path: str, times: int) -> None:
    """执行 TOML 格式的外置脚本。

    Args:
        toml_path: TOML 脚本文件的绝对路径
        times: 循环执行次数
    """
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    meta = data.get("meta", {})
    setup = data.get("setup", {})
    enter_steps = data.get("enter", [])
    loop_steps = data.get("loop", [])
    exit_steps = data.get("exit", [])

    base_path = setup.get("base_path", ".")

    if setup.get("activate_window", True):
        activate_window()

    window_info = get_window(get_hwnd())

    def resolve(image: str) -> str:
        return str(Path(base_path) / image)

    _execute_steps(enter_steps, resolve, window_info)

    for i in range(times):
        print(f"Script: 正在执行脚本: {meta.get('name', 'Unknown')}, 第{i+1}次")
        result = _execute_steps(loop_steps, resolve, window_info)
        if result == "break":
            break

    _execute_steps(exit_steps, resolve, window_info)


def _execute_steps(
    steps: list[dict[str, Any]],
    resolve: Any,
    window_info: Any,
) -> str | None:
    """执行步骤列表。返回 "break" 或 "continue" 以控制循环流程。"""
    for step in steps:
        action = step.get("type", "")

        if action == "wait":
            img = resolve(step["image"])
            wait_image_appear(
                img,
                timeout=step.get("timeout", 10.0),
                confidence=step.get("confidence", 0.8),
            )

        elif action == "wait_disappear":
            img = resolve(step["image"])
            wait_image_disappear(
                img,
                timeout=step.get("timeout", 10.0),
                confidence=step.get("confidence", 0.8),
            )

        elif action == "click":
            img = resolve(step["image"])
            click(
                img,
                timeout=step.get("timeout", 10.0),
                confidence=step.get("confidence", 0.8),
                timesleep=step.get("timesleep", 0.5),
            )

        elif action == "press":
            pdi.press(step["key"])

        elif action == "move_to":
            x = window_info.left + step.get("x", 0)
            y = window_info.top + step.get("y", 0)
            pdi.moveTo(x, y)

        elif action == "sleep":
            time.sleep(step.get("duration", 1.0))

        elif action == "scroll":
            scroll(step.get("amount", 1000))

        elif action == "scroll_until":
            img = resolve(step["image"])
            confidence = step.get("confidence", 0.8)
            scroll_amount = step.get("scroll", 1000)
            while (
                wait_image_appear(img, timeout=0.1, confidence=confidence) is None
            ):
                scroll(scroll_amount)

        elif action == "print":
            print(step.get("text", ""))

        elif action == "break_if":
            img = resolve(step["image"])
            msg = step.get("message", "")
            if (
                wait_image_appear(
                    img,
                    timeout=step.get("timeout", 1.0),
                    confidence=step.get("confidence", 0.8),
                )
                is not None
            ):
                if msg:
                    print(msg)
                return "break"

        elif action == "continue_if_not":
            img = resolve(step["image"])
            msg = step.get("message", "")
            if (
                wait_image_appear(
                    img,
                    timeout=step.get("timeout", 10.0),
                    confidence=step.get("confidence", 0.8),
                )
                is None
            ):
                if msg:
                    print(msg)
                return "continue"

        elif action == "click_at":
            pdi.click()

    return None
