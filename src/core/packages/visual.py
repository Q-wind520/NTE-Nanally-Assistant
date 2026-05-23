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
import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Tuple, List, Union, Callable

import mss
import cv2
import numpy as np
import pydirectinput as pdi
import win32gui

from core.packages.window import get_window, get_hwnd, WindowInfo
from core.packages.constants import (
    DEFAULT_CONFIDENCE,
    DEFAULT_TIMEOUT,
    DEFAULT_INTERVAL,
    DEFAULT_SCREEN_INDEX,
    DEFAULT_CLICK_OFFSET,
)

# 配置日志
logger = logging.getLogger(__name__)


# 数据类

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


# 图像缓存

@lru_cache(maxsize=32)
def _load_image(image_path: str) -> np.ndarray:
    """加载并缓存图片。已通过 lru_cache 自动缓存。"""
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"图片未找到或无法读取: {image_path}")
    logger.debug(f"已加载图片: {image_path}, 尺寸: {image.shape[1]}x{image.shape[0]}")
    return image


# 核心类

class VisualLocator:
    """
    视觉定位器 - 封装图像识别相关功能
    
    提供基于 MSS 的屏幕截图和 OpenCV 模板匹配功能
    """
    
    def __init__(
        self,
        screen_index: int = DEFAULT_SCREEN_INDEX,
        confidence: float = DEFAULT_CONFIDENCE
    ):
        """
        初始化视觉定位器
        
        Args:
            screen_index: MSS 屏幕索引（0=所有屏幕, 1=主屏, 2=副屏...）
            confidence: 默认匹配置信度阈值
        """
        self.screen_index = screen_index
        self.confidence = confidence
        self._mss: Optional[mss.MSS] = None
        self._window_info: Optional[WindowInfo] = None
        self._window_hwnd: Optional[int] = None
    
    def __enter__(self) -> VisualLocator:
        """上下文管理器入口"""
        self._mss = mss.mss()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口"""
        self.close()
    
    def close(self) -> None:
        """释放资源"""
        if self._mss:
            self._mss.close()
            self._mss = None
        logger.debug("VisualLocator 资源已释放")
    
    @property
    def mss_instance(self):
        """获取或创建 MSS 实例"""
        if self._mss is None:
            self._mss = mss.mss()
        return self._mss
    
    def _get_window_info(self) -> WindowInfo:
        """获取并缓存窗口信息，自动检测窗口重建"""
        if self._window_info is not None and self._window_hwnd is not None:
            if not win32gui.IsWindow(self._window_hwnd):
                logger.debug("窗口已失效，刷新缓存")
                self._window_info = None
                self._window_hwnd = None

        if self._window_info is None:
            hwnd = get_hwnd()
            info = get_window(hwnd)
            if info is None:
                raise RuntimeError("无法获取窗口信息")

            self._window_info = info
            self._window_hwnd = hwnd
        return self._window_info

    def refresh_window_info(self) -> None:
        """刷新窗口信息缓存"""
        self._window_info = None
        self._window_hwnd = None
        logger.debug("窗口信息缓存已刷新")
    
    def capture_screen(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        scale: Optional[float] = None
    ) -> np.ndarray:
        """
        捕获屏幕截图
        
        Args:
            region: 截图区域 (left, top, width, height)，None 则使用窗口区域
            scale: 缩放比例，None 则使用窗口默认缩放
            
        Returns:
            BGR 格式的截图数组
        """
        window = self._get_window_info()
        
        if region is None:
            region = (window.left, window.top, window.width, window.height)
        if scale is None:
            scale = window.scale
        
        mss_inst = self.mss_instance
        if mss_inst is None:
            raise RuntimeError("MSS 实例未初始化")
        
        mon = mss_inst.monitors[self.screen_index]
        x, y, w, h = region

        # 将虚拟屏幕坐标转换为相对当前监控器的坐标
        grab_left = x - mon["left"]
        grab_top = y - mon["top"]

        # 验证截图区域是否在监控器范围内，否则回退到虚拟桌面
        if (grab_left < 0 or grab_top < 0 or
                grab_left + w > mon["width"] or grab_top + h > mon["height"]):
            logger.debug(
                "截图区域超出监控器 %d 范围，回退到虚拟桌面 (screen_index=0)", self.screen_index
            )
            mon = mss_inst.monitors[0]
            grab_left = x - mon["left"]
            grab_top = y - mon["top"]

        grab_region = {
            "left": grab_left,
            "top": grab_top,
            "width": w,
            "height": h
        }
        
        shot = mss_inst.grab(grab_region)
        img = np.array(shot)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # 应用缩放
        if scale != 1.0:
            img_bgr = cv2.resize(
                img_bgr,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_AREA
            )

        return img_bgr
    
    def _to_absolute_coords(
        self, match_x: int, match_y: int, tpl_w: int, tpl_h: int,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Tuple[int, int, int, int]:
        """将模板匹配坐标转换为绝对屏幕坐标"""
        window = self._get_window_info()
        scale = window.scale
        if scale != 1.0:
            left = int(match_x / scale)
            top = int(match_y / scale)
            width = int(tpl_w / scale)
            height = int(tpl_h / scale)
        else:
            left, top = match_x, match_y
            width, height = tpl_w, tpl_h
        if region:
            left += region[0]
            top += region[1]
        else:
            left += window.left
            top += window.top
        return left, top, width, height

    def find_template(
        self,
        template_path: str,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[MatchResult]:
        """
        在屏幕上查找单个模板图片
        
        Args:
            template_path: 模板图片路径
            confidence: 匹配置信度阈值，None 使用默认值
            region: 搜索区域，None 则使用窗口区域
            
        Returns:
            匹配结果，未找到返回 None
        """
        if confidence is None:
            confidence = self.confidence
        
        # 加载模板
        template = _load_image(template_path)
        tpl_h, tpl_w = template.shape[:2]
        
        # 捕获屏幕
        screenshot = self.capture_screen(region)
        
        # 模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val < confidence:
            return None

        left, top, width, height = self._to_absolute_coords(
            max_loc[0], max_loc[1], tpl_w, tpl_h, region
        )
        return MatchResult(left, top, width, height, max_val)
    
    def find_all_templates(
        self,
        template_path: str,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        max_results: int = 10
    ) -> List[MatchResult]:
        """
        在屏幕上查找所有匹配的模板图片
        
        Args:
            template_path: 模板图片路径
            confidence: 匹配置信度阈值
            region: 搜索区域
            max_results: 最大返回结果数
            
        Returns:
            匹配结果列表
        """
        if confidence is None:
            confidence = self.confidence
        
        template = _load_image(template_path)
        tpl_h, tpl_w = template.shape[:2]
        screenshot = self.capture_screen(region)
        
        # 模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        
        # 使用阈值获取所有匹配位置
        locations = np.where(result >= confidence)
        
        matches: List[MatchResult] = []

        for pt in zip(*locations[::-1]):
            if len(matches) >= max_results:
                break

            conf = float(result[pt[1], pt[0]])

            left, top, width, height = self._to_absolute_coords(
                pt[0], pt[1], tpl_w, tpl_h, region
            )

            matches.append(MatchResult(left, top, width, height, conf))
        
        # 非极大值抑制，去除重叠框
        matches = self._nms(matches, threshold=0.3)
        
        return matches
    
    @staticmethod
    def _nms(matches: List[MatchResult], threshold: float = 0.3) -> List[MatchResult]:
        """
        非极大值抑制
        
        去除重叠的匹配结果
        
        Args:
            matches: 匹配结果列表
            threshold: IoU 阈值
            
        Returns:
            过滤后的匹配结果
        """
        if not matches:
            return []
        
        # 按置信度排序
        sorted_matches = sorted(matches, key=lambda x: x.confidence, reverse=True)
        keep: List[MatchResult] = []
        
        for match in sorted_matches:
            should_keep = True
            for kept in keep:
                # 计算 IoU
                iou = VisualLocator._calculate_iou(match, kept)
                if iou > threshold:
                    should_keep = False
                    break
            
            if should_keep:
                keep.append(match)
        
        return keep
    
    @staticmethod
    def _calculate_iou(a: MatchResult, b: MatchResult) -> float:
        """计算两个矩形的 IoU"""
        x_left = max(a.left, b.left)
        y_top = max(a.top, b.top)
        x_right = min(a.right, b.right)
        y_bottom = min(a.bottom, b.bottom)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area_a = a.width * a.height
        area_b = b.width * b.height
        union = area_a + area_b - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def wait_for_template(
        self,
        template_path: str,
        timeout: float = DEFAULT_TIMEOUT,
        interval: float = DEFAULT_INTERVAL,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[MatchResult]:
        """
        等待模板图片出现在屏幕上
        
        Args:
            template_path: 模板图片路径
            timeout: 超时时间（秒）
            interval: 检查间隔（秒）
            confidence: 匹配置信度
            region: 搜索区域
            
        Returns:
            匹配结果，超时返回 None
        """
        start_time = time.time()
        
        while True:
            result = self.find_template(template_path, confidence, region)
            if result is not None:
                logger.info(f"找到模板: {template_path}, 置信度: {result.confidence:.3f}")
                return result
            
            if timeout > 0 and time.time() - start_time > timeout:
                logger.warning(f"等待模板超时({timeout}s): {template_path}")
                return None
            
            time.sleep(interval)
    
    def wait_for_template_disappear(
        self,
        template_path: str,
        timeout: float = DEFAULT_TIMEOUT,
        interval: float = DEFAULT_INTERVAL,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> bool:
        """
        等待模板图片从屏幕上消失
        
        Args:
            template_path: 模板图片路径
            timeout: 超时时间（秒）
            interval: 检查间隔（秒）
            confidence: 匹配置信度
            region: 搜索区域
            
        Returns:
            True-成功消失, False-超时仍未消失
        """
        start_time = time.time()
        
        while True:
            result = self.find_template(template_path, confidence, region)
            if result is None:
                logger.info(f"模板已消失: {template_path}")
                return True
            
            if timeout > 0 and time.time() - start_time > timeout:
                logger.warning(f"等待模板消失超时({timeout}s): {template_path}")
                return False
            
            time.sleep(interval)


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
        on_timeout: Optional[Callable[[], None]] = None
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
            
        Returns:
            True-成功点击, False-超时
        """
        result = self.locator.wait_for_template(
            template_path,
            timeout=timeout,
            interval=check_interval,
            confidence=confidence
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

# 便捷函数

def click(
    image_path: str,
    timeout: float = DEFAULT_TIMEOUT,
    confidence: float = DEFAULT_CONFIDENCE,
    timesleep: float = 0.5,
    on_failure: Optional[Callable[[], None]] = None
) -> bool:
    """
    在屏幕上查找模板图片并点击其中心位置（向后兼容）
    
    Args:
        image_path: 模板图片路径
        timeout: 查找超时时间（秒）
        confidence: 匹配置信度
        timesleep: 点击前的等待时间（默认0.5秒）
        on_failure: 失败时的回调函数
        
    Returns:
        True-成功点击, False-失败/超时
    """
    with VisualInteractor() as interactor:
        time.sleep(timesleep)
        return interactor.click_when_found(
            image_path,
            timeout=timeout,
            confidence=confidence,
            on_timeout=on_failure
        )


# 高级功能函数

def wait_image_appear(
    image_path: str,
    timeout: float = DEFAULT_TIMEOUT,
    confidence: float = DEFAULT_CONFIDENCE
) -> Optional[MatchResult]:
    """
    等待图片出现在屏幕上
    
    Args:
        image_path: 模板图片路径
        timeout: 超时时间（秒）
        confidence: 匹配置信度
        
    Returns:
        匹配结果或 None
    """
    with VisualLocator(confidence=confidence) as locator:
        return locator.wait_for_template(image_path, timeout=timeout)


def wait_image_disappear(
    image_path: str,
    timeout: float = DEFAULT_TIMEOUT,
    confidence: float = DEFAULT_CONFIDENCE
) -> bool:
    """
    等待图片从屏幕上消失
    
    Args:
        image_path: 模板图片路径
        timeout: 超时时间（秒）
        confidence: 匹配置信度
        
    Returns:
        True-成功消失, False-超时
    """
    with VisualLocator(confidence=confidence) as locator:
        return locator.wait_for_template_disappear(image_path, timeout=timeout)


def find_all_images(
    image_path: str,
    confidence: float = DEFAULT_CONFIDENCE,
    max_results: int = 10
) -> List[MatchResult]:
    """
    查找屏幕上所有匹配的图片
    
    Args:
        image_path: 模板图片路径
        confidence: 匹配置信度
        max_results: 最大结果数
        
    Returns:
        匹配结果列表
    """
    with VisualLocator(confidence=confidence) as locator:
        return locator.find_all_templates(image_path, max_results=max_results)


