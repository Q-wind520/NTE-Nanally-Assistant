"""
视觉识别模块 - 基于 OpenCV 和 MSS 的图像识别与交互

提供以下功能：
- 屏幕截图与模板匹配
- 自动点击识别到的目标
- 等待目标出现/消失
- 多目标匹配
"""

from __future__ import annotations

import time
from typing import Optional, Tuple, List, Callable

import win32api
import win32con

from core.packages.constants import (
    DEFAULT_CONFIDENCE,
    DEFAULT_TIMEOUT,
    DEFAULT_INTERVAL,
    MULTI_SCALE_MIN,
    MULTI_SCALE_MAX,
    MULTI_SCALE_STEPS,
    MULTI_SCALE_EARLY_EXIT,
)
from core.packages.visual._types import MatchResult
from core.packages.visual._locator import VisualLocator, _load_image
from core.packages.visual._interactor import VisualInteractor

# Re-export
__all__ = [
    "MatchResult",
    "VisualLocator",
    "VisualInteractor",
    "_load_image",
    "click",
    "wait_image_appear",
    "wait_image_disappear",
    "scroll",
    "find_all_images",
]


# 便捷函数

def click(
    image_path: str,
    timeout: float = DEFAULT_TIMEOUT,
    confidence: float = DEFAULT_CONFIDENCE,
    timesleep: float = 0.5,
    on_failure: Optional[Callable[[], None]] = None,
    multi_scale: bool = True,
    scale_min: float = MULTI_SCALE_MIN,
    scale_max: float = MULTI_SCALE_MAX,
    scale_steps: int = MULTI_SCALE_STEPS,
    multi_scale_early_exit: float = MULTI_SCALE_EARLY_EXIT,
) -> bool:
    """
    在屏幕上查找模板图片并点击其中心位置（向后兼容）

    Args:
        image_path: 模板图片路径
        timeout: 查找超时时间（秒）
        confidence: 匹配置信度
        timesleep: 点击前的等待时间（默认0.5秒）
        on_failure: 失败时的回调函数
        multi_scale: 是否启用多尺度匹配
        scale_min: 多尺度匹配的最小缩放比例
        scale_max: 多尺度匹配的最大缩放比例
        scale_steps: 多尺度匹配的单侧步数
        multi_scale_early_exit: 多尺度匹配早期退出阈值

    Returns:
        True-成功点击, False-失败/超时
    """
    with VisualInteractor() as interactor:
        time.sleep(timesleep)
        return interactor.click_when_found(
            image_path,
            timeout=timeout,
            confidence=confidence,
            on_timeout=on_failure,
            multi_scale=multi_scale,
            scale_min=scale_min,
            scale_max=scale_max,
            scale_steps=scale_steps,
            multi_scale_early_exit=multi_scale_early_exit,
        )


def wait_image_appear(
    image_path: str,
    timeout: float = DEFAULT_TIMEOUT,
    confidence: float = DEFAULT_CONFIDENCE,
    multi_scale: bool = False,
    scale_min: float = MULTI_SCALE_MIN,
    scale_max: float = MULTI_SCALE_MAX,
    scale_steps: int = MULTI_SCALE_STEPS,
    multi_scale_early_exit: float = MULTI_SCALE_EARLY_EXIT,
) -> Optional[MatchResult]:
    """
    等待图片出现在屏幕上

    Args:
        image_path: 模板图片路径
        timeout: 超时时间（秒）
        confidence: 匹配置信度
        multi_scale: 是否启用多尺度匹配
        scale_min: 多尺度匹配的最小缩放比例
        scale_max: 多尺度匹配的最大缩放比例
        scale_steps: 多尺度匹配的单侧步数
        multi_scale_early_exit: 多尺度匹配早期退出阈值

    Returns:
        匹配结果或 None
    """
    with VisualLocator(confidence=confidence) as locator:
        return locator.wait_for_template(
            image_path, timeout=timeout,
            multi_scale=multi_scale, scale_min=scale_min,
            scale_max=scale_max, scale_steps=scale_steps,
            multi_scale_early_exit=multi_scale_early_exit,
        )


def wait_image_disappear(
    image_path: str,
    timeout: float = DEFAULT_TIMEOUT,
    confidence: float = DEFAULT_CONFIDENCE,
    multi_scale: bool = True,
    scale_min: float = MULTI_SCALE_MIN,
    scale_max: float = MULTI_SCALE_MAX,
    scale_steps: int = MULTI_SCALE_STEPS,
    multi_scale_early_exit: float = MULTI_SCALE_EARLY_EXIT,
) -> bool:
    """
    等待图片从屏幕上消失

    Args:
        image_path: 模板图片路径
        timeout: 超时时间（秒）
        confidence: 匹配置信度
        multi_scale: 是否启用多尺度匹配
        scale_min: 多尺度匹配的最小缩放比例
        scale_max: 多尺度匹配的最大缩放比例
        scale_steps: 多尺度匹配的单侧步数
        multi_scale_early_exit: 多尺度匹配早期退出阈值

    Returns:
        True-成功消失, False-超时
    """
    with VisualLocator(confidence=confidence) as locator:
        return locator.wait_for_template_disappear(
            image_path, timeout=timeout,
            multi_scale=multi_scale, scale_min=scale_min,
            scale_max=scale_max, scale_steps=scale_steps,
            multi_scale_early_exit=multi_scale_early_exit,
        )


def scroll(amount: int) -> None:
    """
    鼠标滚轮滚动

    Args:
        amount: 滚动量，正数向上滚动，负数向下滚动
    """
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, amount, 0)


def find_all_images(
    image_path: str,
    confidence: float = DEFAULT_CONFIDENCE,
    max_results: int = 10,
    multi_scale: bool = True,
    scale_min: float = MULTI_SCALE_MIN,
    scale_max: float = MULTI_SCALE_MAX,
    scale_steps: int = MULTI_SCALE_STEPS,
    multi_scale_early_exit: float = MULTI_SCALE_EARLY_EXIT,
) -> List[MatchResult]:
    """
    查找屏幕上所有匹配的图片

    Args:
        image_path: 模板图片路径
        confidence: 匹配置信度
        max_results: 最大结果数
        multi_scale: 是否启用多尺度匹配
        scale_min: 多尺度匹配的最小缩放比例
        scale_max: 多尺度匹配的最大缩放比例
        scale_steps: 多尺度匹配的单侧步数
        multi_scale_early_exit: 多尺度匹配早期退出阈值

    Returns:
        匹配结果列表
    """
    with VisualLocator(confidence=confidence) as locator:
        return locator.find_all_templates(
            image_path, max_results=max_results,
            multi_scale=multi_scale, scale_min=scale_min,
            scale_max=scale_max, scale_steps=scale_steps,
            multi_scale_early_exit=multi_scale_early_exit,
        )
