"""模板匹配结果数据类。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class MatchResult:
    """
    模板匹配结果

    Attributes:
        left: 匹配区域左上角 X 坐标
        top: 匹配区域左上角 Y 坐标
        width: 匹配区域宽度
        height: 匹配区域高度
        confidence: 匹配置信度
    """
    left: int
    top: int
    width: int
    height: int
    confidence: float

    @property
    def center(self) -> Tuple[int, int]:
        """获取匹配区域中心坐标"""
        return (self.left + self.width // 2, self.top + self.height // 2)

    @property
    def right(self) -> int:
        """匹配区域右下角 X 坐标"""
        return self.left + self.width

    @property
    def bottom(self) -> int:
        """匹配区域右下角 Y 坐标"""
        return self.top + self.height

    @property
    def box(self) -> Tuple[int, int, int, int]:
        """获取 (left, top, width, height) 元组"""
        return (self.left, self.top, self.width, self.height)
