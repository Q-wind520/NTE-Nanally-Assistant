"""视觉交互器 — 基于图像识别的点击与鼠标操作。"""

from __future__ import annotations

import logging
from typing import Optional, Tuple, Union, Callable

import pydirectinput as pdi

from core.packages.constants import (
    DEFAULT_CONFIDENCE,
    DEFAULT_TIMEOUT,
    DEFAULT_INTERVAL,
    DEFAULT_CLICK_OFFSET,
    MULTI_SCALE_MIN,
    MULTI_SCALE_MAX,
    MULTI_SCALE_STEPS,
    MULTI_SCALE_EARLY_EXIT,
)
from core.packages.visual._types import MatchResult
from core.packages.visual._locator import VisualLocator

logger = logging.getLogger(__name__)


class VisualInteractor:
    """
    视觉交互器 - 封装基于图像识别的交互操作
    """

    def __init__(self, locator: Optional[VisualLocator] = None):
        """
        初始化视觉交互器

        Args:
            locator: 视觉定位器实例，None 则创建新实例
        """
        self.locator = locator or VisualLocator()
        self._own_locator = locator is None

    def __enter__(self) -> VisualInteractor:
        """上下文管理器入口"""
        if isinstance(self.locator, VisualLocator):
            self.locator.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口"""
        self.close()

    def close(self) -> None:
        """释放资源"""
        if self._own_locator and isinstance(self.locator, VisualLocator):
            self.locator.close()

    def _resolve_target(
        self, target: Union[str, MatchResult, Tuple[int, int]]
    ) -> Optional[Tuple[int, int]]:
        """将目标解析为 (x, y) 坐标。模板未找到时返回 None。"""
        if isinstance(target, str):
            result = self.locator.find_template(target)
            if result is None:
                return None
            return result.center
        elif isinstance(target, MatchResult):
            return target.center
        else:
            return target

    def click(
        self,
        target: Union[str, MatchResult, Tuple[int, int]],
        offset: Tuple[int, int] = DEFAULT_CLICK_OFFSET,
        button: str = "left",
        clicks: int = 1,
        interval: float = 0.0
    ) -> bool:
        """点击目标位置。支持模板路径、匹配结果或坐标元组。"""
        coords = self._resolve_target(target)
        if coords is None:
            logger.warning(f"点击失败，未找到模板: {target}")
            return False
        x, y = coords
        x += offset[0]
        y += offset[1]

        try:
            pdi.click(x, y, button=button, clicks=clicks, interval=interval)
            logger.info(f"已点击: ({x}, {y}), 按钮: {button}")
            return True
        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False

    def click_when_found(
        self,
        template_path: str,
        timeout: float = DEFAULT_TIMEOUT,
        check_interval: float = DEFAULT_INTERVAL,
        click_offset: Tuple[int, int] = DEFAULT_CLICK_OFFSET,
        confidence: Optional[float] = None,
        on_timeout: Optional[Callable[[], None]] = None,
        multi_scale: bool = True,
        scale_min: float = MULTI_SCALE_MIN,
        scale_max: float = MULTI_SCALE_MAX,
        scale_steps: int = MULTI_SCALE_STEPS,
        multi_scale_early_exit: float = MULTI_SCALE_EARLY_EXIT,
    ) -> bool:
        """
        等待并点击模板图片

        Args:
            template_path: 模板图片路径
            timeout: 查找超时时间
            check_interval: 查找检查间隔
            click_offset: 点击偏移量
            confidence: 匹配置信度
            on_timeout: 超时回调函数
            multi_scale: 是否启用多尺度匹配
            scale_min: 多尺度匹配的最小缩放比例
            scale_max: 多尺度匹配的最大缩放比例
            scale_steps: 多尺度匹配的单侧步数
            multi_scale_early_exit: 多尺度匹配早期退出阈值

        Returns:
            True-成功点击, False-超时
        """
        result = self.locator.wait_for_template(
            template_path,
            timeout=timeout,
            interval=check_interval,
            confidence=confidence,
            multi_scale=multi_scale,
            scale_min=scale_min,
            scale_max=scale_max,
            scale_steps=scale_steps,
            multi_scale_early_exit=multi_scale_early_exit,
        )

        if result is None:
            logger.warning(f"点击失败，查找超时: {template_path}")
            if on_timeout:
                on_timeout()
            return False

        return self.click(result, offset=click_offset)

    def move_to(
        self,
        target: Union[str, MatchResult, Tuple[int, int]],
        offset: Tuple[int, int] = DEFAULT_CLICK_OFFSET
    ) -> bool:
        """移动鼠标到目标位置。支持模板路径、匹配结果或坐标元组。"""
        coords = self._resolve_target(target)
        if coords is None:
            return False
        x, y = coords
        x += offset[0]
        y += offset[1]

        try:
            pdi.moveTo(x, y)
            return True
        except Exception as e:
            logger.error(f"移动鼠标失败: {e}")
            return False
