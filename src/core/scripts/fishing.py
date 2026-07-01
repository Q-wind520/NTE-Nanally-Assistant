"""钓鱼条控制 — HSV 检测 + A/D 比例控制。"""

from __future__ import annotations

import time
import logging
from typing import Any

import cv2
import numpy as np
import pydirectinput as pdi

from core.packages.window import get_window, get_hwnd
from core.packages.visual._locator import VisualLocator
from core.scripts._base import register, BuiltinContext

logger = logging.getLogger(__name__)

BAR_LEFT = 0.2060
BAR_TOP = 0.05200
BAR_RIGHT = 0.7900
BAR_BOTTOM = 0.0780

GREEN_HSV_LOW = (80, 150, 100)
GREEN_HSV_HIGH = (90, 255, 255)
YELLOW_HSV_LOW = (0, 30, 160)
YELLOW_HSV_HIGH = (30, 160, 255)


def _bar_region(window) -> tuple[int, int, int, int]:
    left = int(window.left + window.width * BAR_LEFT)
    top = int(window.top + window.height * BAR_TOP)
    width = int(window.width * (BAR_RIGHT - BAR_LEFT))
    height = int(window.height * (BAR_BOTTOM - BAR_TOP))
    return (left, top, width, height)


def _detect_bar_state(screenshot: np.ndarray) -> dict[str, Any] | None:
    h, w = screenshot.shape[:2]
    if h == 0 or w == 0:
        return None

    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

    green = cv2.inRange(hsv, np.array(GREEN_HSV_LOW), np.array(GREEN_HSV_HIGH))
    green = cv2.morphologyEx(green, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    green = cv2.morphologyEx(green, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    yellow = cv2.inRange(hsv, np.array(YELLOW_HSV_LOW), np.array(YELLOW_HSV_HIGH))
    yellow = cv2.morphologyEx(yellow, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    yellow = cv2.morphologyEx(yellow, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    g_contours, _ = cv2.findContours(green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    g_contours = sorted(g_contours, key=cv2.contourArea, reverse=True)
    if len(g_contours) < 2:
        return None

    x0, _, w0, _ = cv2.boundingRect(g_contours[0])
    x1, _, w1, _ = cv2.boundingRect(g_contours[1])
    zone_left = min(x0, x1)
    zone_right = max(x0 + w0, x1 + w1)
    zone_center = (zone_left + zone_right) / 2
    zone_width = zone_right - zone_left

    y_contours, _ = cv2.findContours(yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    y_contours = sorted(y_contours, key=cv2.contourArea, reverse=True)
    if not y_contours:
        return None

    px, _, pw, _ = cv2.boundingRect(y_contours[0])
    pointer_center = px + pw / 2
    pointer_width = pw
    in_zone = zone_left <= pointer_center <= zone_right

    return {
        "zone_left": zone_left,
        "zone_right": zone_right,
        "zone_center": zone_center,
        "zone_width": zone_width,
        "image_width": w,
        "pointer_center": pointer_center,
        "pointer_width": pointer_width,
        "in_zone": in_zone,
    }


def _control_tick(state: dict[str, Any], params: dict[str, Any]) -> None:
    deadzone = params.get("deadzone", 0.08) * state["zone_width"]
    tap_multiplier = params.get("tap_multiplier", 1.0)

    error = state["pointer_center"] - state["zone_center"]
    abs_error = abs(error)

    if abs_error <= deadzone:
        return

    key = "d" if error < 0 else "a"

    ratio = min(1.0, abs_error / (state["zone_width"] / 2))
    curve = ratio * ratio * (3 - 2 * ratio)
    hold = (0.01 + curve * 0.18) * tap_multiplier

    pdi.keyDown(key)
    time.sleep(hold)
    pdi.keyUp(key)


def _wait_for_bar(locator: VisualLocator, region: tuple, timeout: float) -> dict[str, Any] | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        shot = locator.capture_screen(region=region)
        state = _detect_bar_state(shot)
        if state is not None:
            return state
        time.sleep(0.1)
    return None


def _run_control_loop(locator: VisualLocator, region: tuple,
                      timeout: float, params: dict[str, Any]) -> bool:
    """Returns True on success, False if fish escaped."""
    deadline = time.time() + timeout
    control_start = time.time()
    sustained_duration = 0.0

    while time.time() < deadline:
        shot = locator.capture_screen(region=region)
        state = _detect_bar_state(shot)

        if state is None:
            elapsed = time.time() - control_start
            return elapsed >= 2.0

        in_zone = state["in_zone"]
        if in_zone:
            sustained_duration += 0.01
        else:
            sustained_duration = max(0.0, sustained_duration - 0.02)

        if sustained_duration >= 5.0:
            return True

        _control_tick(state, params)
        time.sleep(0.01)

    return False


@register("fishing_wait_bar")
def fishing_wait_bar(ctx: BuiltinContext) -> str | None:
    """步骤 L2: 等待钓鱼条出现。

    Returns:
        None — 成功检测到钓鱼条（继续执行后续步骤）
        "break" — 超时未检测到（脚本错误, 退出脚本）
    """
    timeout = ctx.params.get("timeout", 10.0)

    window = get_window(get_hwnd())
    region = _bar_region(window)

    with VisualLocator() as locator:
        state = _wait_for_bar(locator, region, timeout)
        if state is None:
            logger.warning("未检测到钓鱼条 (L2超时)")
            print("Script: 未检测到钓鱼条, 脚本出错")
            return "break"

        logger.info("检测到钓鱼条")
        return None


@register("fishing_control_bar")
def fishing_control_bar(ctx: BuiltinContext) -> str | None:
    """步骤 L3: 控制 A/D 溜鱼。

    Returns:
        None — 钓鱼成功（继续执行后续步骤）
        "retry" — 鱼溜走了（重试本次循环, 回到 L1 按F）
        "break" — 超时/致命错误
    """
    timeout = ctx.params.get("timeout", 30.0)
    tap_multiplier = ctx.params.get("tap_multiplier", 1.0)
    deadzone = ctx.params.get("deadzone", 0.08)

    window = get_window(get_hwnd())
    region = _bar_region(window)

    with VisualLocator() as locator:
        logger.info("开始溜鱼")
        ok = _run_control_loop(locator, region, timeout, {
            "deadzone": deadzone,
            "tap_multiplier": tap_multiplier,
        })

        if ok:
            logger.info("钓鱼成功")
            return None

        logger.info("鱼溜走了")
        print("Script: 鱼溜走了, 重新本次循环")
        return "retry"
