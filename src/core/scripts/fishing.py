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

# 钓鱼条区域（比例坐标，相对于 720p 参考）
BAR_LEFT = 0.2060
BAR_TOP = 0.05200
BAR_RIGHT = 0.7900
BAR_BOTTOM = 0.0780

# HSV 范围
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


def _control_tick_discrete(state: dict[str, Any], params: dict[str, Any]) -> None:
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


@register("fishing_bar_control")
def fishing_bar_control(ctx: BuiltinContext) -> None:
    """
    全自动钓鱼条控制。

    检测钓鱼条（绿色目标区 + 黄色指针），用 A/D 键将指针维持在目标区内。

    Params:
        timeout (float): 单次溜鱼超时（秒，默认 30）
        tap_multiplier (float): 点按时长系数（默认 0.5）
        deadzone (float): 死区占 zone_width 比例（默认 0.08）
        bar_wait (float): 等待 bar 出现的最长时间（秒，默认 3.0）
    """
    params = ctx.params
    timeout = params.get("timeout", 30.0)
    tap_multiplier = params.get("tap_multiplier", 0.5)
    deadzone = params.get("deadzone", 0.08)
    bar_wait = params.get("bar_wait", 3.0)

    window = get_window(get_hwnd())
    region = _bar_region(window)

    with VisualLocator() as locator:
        deadline = time.time() + bar_wait
        bar_found = False
        while time.time() < deadline:
            shot = locator.capture_screen(region=region)
            state = _detect_bar_state(shot)
            if state is not None:
                bar_found = True
                break
            time.sleep(0.1)

        if not bar_found:
            logger.info("未检测到钓鱼条，跳过溜鱼")
            return

        logger.info("检测到钓鱼条，开始溜鱼")
        deadline = time.time() + timeout

        while time.time() < deadline:
            shot = locator.capture_screen(region=region)
            state = _detect_bar_state(shot)

            if state is None:
                logger.info("钓鱼条消失，结束溜鱼")
                return

            _control_tick_discrete(state, {
                "deadzone": deadzone,
                "tap_multiplier": tap_multiplier,
            })
            time.sleep(0.01)

    logger.info("溜鱼结束")
