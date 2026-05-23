"""
窗口管理模块 - 游戏窗口的检测、激活和信息获取

提供以下功能：
- 通过进程名获取窗口句柄
- 获取窗口位置和尺寸信息
- 激活游戏窗口
- 等待窗口调整为 1080p 分辨率
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass
from typing import Optional

import win32gui
import win32process
from win32con import SW_SHOWNORMAL

from psutil import process_iter
from core.packages.constants import (
    WINDOW_BORDER_LEFT,
    WINDOW_BORDER_RIGHT,
    WINDOW_BORDER_TOP,
    WINDOW_BORDER_BOTTOM,
    TARGET_ASPECT_RATIO,
    TARGET_HEIGHT,
    ASPECT_RATIO_TOLERANCE,
    DEFAULT_PROCESS_NAME,
)

logger = logging.getLogger(__name__)

@dataclass
class WindowInfo:
    """
    窗口信息

    Attributes:
        left: 窗口客户区左上角 X 坐标
        top: 窗口客户区左上角 Y 坐标
        right: 窗口客户区右下角 X 坐标
        bottom: 窗口客户区右下角 Y 坐标
        width: 窗口客户区宽度
        height: 窗口客户区高度
        scale: 缩放比例（相对于 1080p）
    """
    left: int
    top: int
    right: int
    bottom: int
    width: int
    height: int
    scale: float


# 异常类

class WindowNotFoundError(RuntimeError):
    """窗口未找到异常"""
    pass


class WindowInvalidError(ValueError):
    """窗口无效异常"""
    pass


class WindowResolutionTimeoutError(RuntimeError):
    """窗口分辨率等待超时异常"""
    pass


# ==================== 核心函数 ====================

def get_hwnd(name: str = DEFAULT_PROCESS_NAME) -> int:
    """
    通过进程名获取窗口句柄

    Args:
        name: 进程名

    Returns:
        窗口句柄（整数）

    Raises:
        WindowNotFoundError: 找不到进程或窗口时抛出
    """
    # 查找进程 PID
    pid = None
    for proc in process_iter(['pid', 'name']):
        if proc.info['name'] == name:
            pid = proc.info['pid']
            break

    if pid is None:
        raise WindowNotFoundError(f"无法找到进程: {name}")

    # 枚举窗口查找属于该进程的可见窗口
    result: list[int] = []

    def callback(hwnd: int, _: object) -> None:
        if win32gui.IsWindowVisible(hwnd):
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == pid and win32gui.GetWindowText(hwnd):
                result.append(hwnd)

    win32gui.EnumWindows(callback, None)

    if not result:
        raise WindowNotFoundError(f"无法找到进程 {name} 的可见窗口")

    return result[0]


def get_window(hwnd: int) -> WindowInfo:
    """
    获取窗口信息，自动处理窗口边框

    Args:
        hwnd: 窗口句柄

    Returns:
        窗口信息对象

    Raises:
        WindowInvalidError: 窗口句柄无效或窗口尺寸异常
    """
    if not hwnd or not win32gui.IsWindow(hwnd):
        raise WindowInvalidError(f"无效的窗口句柄: {hwnd}")

    # 获取窗口矩形区域（包含边框）
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    # 计算原始尺寸
    raw_width = right - left
    raw_height = bottom - top

    if raw_width <= 0 or raw_height <= 0:
        raise WindowInvalidError(f"窗口尺寸异常: {raw_width}x{raw_height}")

    # 判断是否接近 16:9 宽高比（允许 ±5% 误差）
    actual_ratio = raw_width / raw_height
    is_16_9 = abs(actual_ratio - TARGET_ASPECT_RATIO) < ASPECT_RATIO_TOLERANCE

    # 如果不是标准 16:9（窗口模式），减去窗口边框
    if not is_16_9:
        left += WINDOW_BORDER_LEFT
        right -= WINDOW_BORDER_RIGHT
        top += WINDOW_BORDER_TOP
        bottom -= WINDOW_BORDER_BOTTOM

    # 计算客户区尺寸
    width = right - left
    height = bottom - top

    # 确保客户区尺寸有效
    if width <= 0 or height <= 0:
        raise WindowInvalidError(f"窗口客户区尺寸无效: {width}x{height}")

    # 计算缩放比例（基于高度）
    scale = TARGET_HEIGHT / height if height > 0 else 1.0

    return WindowInfo(
        left=left,
        top=top,
        right=right,
        bottom=bottom,
        width=width,
        height=height,
        scale=scale
    )


def activate_window(hwnd: Optional[int] = None) -> None:
    """
    激活窗口（置顶并显示）

    Args:
        hwnd: 窗口句柄，None 则自动查找游戏窗口

    Raises:
        WindowNotFoundError: 找不到窗口
    """
    if hwnd is None:
        hwnd = get_hwnd()

    try:
        win32gui.ShowWindow(hwnd, SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(hwnd)
        logger.info("已成功激活游戏窗口")
    except Exception as e:
        logger.warning("激活窗口失败: %s", e)
        raise


def wait_for_1080p_resolution(
    timeout: float = 300,
    check_interval: float = 2,
    process_name: str = DEFAULT_PROCESS_NAME
) -> WindowInfo:
    """
    等待游戏窗口调整为 1920×1080 分辨率

    循环检测窗口分辨率，直到满足 1080p 或超时。

    Args:
        timeout: 超时时间（秒）
        check_interval: 检查间隔（秒）
        process_name: 进程名

    Returns:
        符合 1080p 要求的窗口信息

    Raises:
        WindowResolutionTimeoutError: 超时仍未检测到 1080p 分辨率
    """
    start_time = time.time()

    while True:
        try:
            hwnd = get_hwnd(process_name)
            window_info = get_window(hwnd)
        except (WindowNotFoundError, WindowInvalidError) as e:
            logger.warning("获取窗口信息失败: %s", e)
            window_info = None

        if window_info is not None:
            is_1080p = (
                window_info.height == TARGET_HEIGHT and
                abs(window_info.width / window_info.height - TARGET_ASPECT_RATIO) < ASPECT_RATIO_TOLERANCE
            )

            if is_1080p:
                logger.info("检测到 1080p 窗口分辨率")
                return window_info

        elapsed = time.time() - start_time

        if elapsed < 5:
            logger.warning("不能执行脚本，请将游戏窗口化为 1920×1080 分辨率")
            logger.info("正在等待你为其窗口化...")
            time.sleep(5)
        elif elapsed < timeout:
            logger.info("等待窗口化中 (%ds/%ds)", int(elapsed), int(timeout))
            time.sleep(check_interval)
        else:
            raise WindowResolutionTimeoutError(
                f"长时间未检测到窗口化 ({timeout}s)，异常退出"
            )
