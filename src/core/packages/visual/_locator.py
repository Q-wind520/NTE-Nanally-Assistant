"""视觉定位器 — 屏幕截图与模板匹配。"""

from __future__ import annotations

import time
import logging
from functools import lru_cache
from typing import Optional, Tuple, List

import mss
import cv2
import numpy as np
import win32gui

from core.packages.window import get_window, get_hwnd, WindowInfo
from core.packages.constants import (
    DEFAULT_CONFIDENCE,
    DEFAULT_TIMEOUT,
    DEFAULT_INTERVAL,
    DEFAULT_SCREEN_INDEX,
    MULTI_SCALE_MIN,
    MULTI_SCALE_MAX,
    MULTI_SCALE_STEPS,
    MULTI_SCALE_EARLY_EXIT,
)
from core.packages.visual._types import MatchResult

logger = logging.getLogger(__name__)


# 图像缓存

@lru_cache(maxsize=32)
def _load_image(image_path: str) -> np.ndarray:
    """加载并缓存图片。已通过 lru_cache 自动缓存。"""
    # cv2.imread 不支持 Windows 非 ASCII 路径，用 imdecode 替代
    data = np.fromfile(image_path, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"图片未找到或无法读取: {image_path}")
    logger.debug(f"已加载图片: {image_path}, 尺寸: {image.shape[1]}x{image.shape[0]}")
    return image


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
        region: Optional[Tuple[int, int, int, int]] = None,
        multi_scale: bool = True,
        scale_min: float = MULTI_SCALE_MIN,
        scale_max: float = MULTI_SCALE_MAX,
        scale_steps: int = MULTI_SCALE_STEPS,
        multi_scale_early_exit: float = MULTI_SCALE_EARLY_EXIT,
    ) -> Optional[MatchResult]:
        """
        在屏幕上查找单个模板图片

        Args:
            template_path: 模板图片路径
            confidence: 匹配置信度阈值，None 使用默认值
            region: 搜索区域，None 则使用窗口区域
            multi_scale: 是否启用多尺度匹配
            scale_min: 多尺度匹配的最小缩放比例
            scale_max: 多尺度匹配的最大缩放比例
            scale_steps: 多尺度匹配的单侧步数
            multi_scale_early_exit: 多尺度匹配早期退出阈值，
                超过此置信度直接返回不再尝试剩余尺度。设为 1.0 可禁用。

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

        if multi_scale:
            return self._find_template_multi_scale(
                screenshot, template, tpl_w, tpl_h,
                confidence, region, scale_min, scale_max, scale_steps,
                early_exit=multi_scale_early_exit,
            )

        # 单尺度模板匹配（原有逻辑）
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < confidence:
            return None

        left, top, width, height = self._to_absolute_coords(
            max_loc[0], max_loc[1], tpl_w, tpl_h, region
        )
        return MatchResult(left, top, width, height, max_val)

    def _find_template_multi_scale(
        self,
        screenshot: np.ndarray,
        template: np.ndarray,
        tpl_w: int,
        tpl_h: int,
        confidence: float,
        region: Optional[Tuple[int, int, int, int]],
        scale_min: float,
        scale_max: float,
        scale_steps: int,
        early_exit: float = MULTI_SCALE_EARLY_EXIT,
    ) -> Optional[MatchResult]:
        """
        多尺度模板匹配的内部实现

        Args:
            early_exit: 高置信度早期退出阈值。当某尺度匹配置信度超过此值时，
                        直接返回结果不再尝试剩余尺度。设为 1.0 可禁用早期退出。
        """
        scales = self._generate_scale_factors(scale_min, scale_max, scale_steps)
        best_val = -1.0
        best_loc = None
        best_w = tpl_w
        best_h = tpl_h

        for scale in scales:
            if abs(scale - 1.0) < 1e-6:
                scaled_tpl = template
                sw, sh = tpl_w, tpl_h
            else:
                sw = max(1, int(tpl_w * scale))
                sh = max(1, int(tpl_h * scale))
                interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
                scaled_tpl = cv2.resize(template, (sw, sh), interpolation=interp)

            # 跳过比截图还大的模板
            if sh > screenshot.shape[0] or sw > screenshot.shape[1]:
                continue

            result = cv2.matchTemplate(screenshot, scaled_tpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_w, best_h = sw, sh

            # 早期退出：已找到极高置信度的匹配，跳过剩余尺度
            # 使用 > 确保 early_exit=1.0 可完全禁用（TM_CCOEFF_NORMED 最大值为 1.0）
            if best_val > early_exit:
                logger.debug(
                    "多尺度匹配早期退出: scale=%.4f, 置信度=%.4f > %.4f",
                    scale, best_val, early_exit,
                )
                break

        if best_val < confidence or best_loc is None:
            return None

        logger.debug(
            "多尺度匹配: %s, 最佳缩放=%.4f, 置信度=%.4f",
            "template",
            best_w / tpl_w,
            best_val,
        )

        left, top, width, height = self._to_absolute_coords(
            best_loc[0], best_loc[1], best_w, best_h, region
        )
        return MatchResult(left, top, width, height, best_val)

    def find_all_templates(
        self,
        template_path: str,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        max_results: int = 10,
        multi_scale: bool = True,
        scale_min: float = MULTI_SCALE_MIN,
        scale_max: float = MULTI_SCALE_MAX,
        scale_steps: int = MULTI_SCALE_STEPS,
        multi_scale_early_exit: float = MULTI_SCALE_EARLY_EXIT,
    ) -> List[MatchResult]:
        """
        在屏幕上查找所有匹配的模板图片

        Args:
            template_path: 模板图片路径
            confidence: 匹配置信度阈值
            region: 搜索区域
            max_results: 最大返回结果数
            multi_scale: 是否启用多尺度匹配
            scale_min: 多尺度匹配的最小缩放比例
            scale_max: 多尺度匹配的最大缩放比例
            scale_steps: 多尺度匹配的单侧步数
            multi_scale_early_exit: 多尺度匹配早期退出阈值

        Returns:
            匹配结果列表
        """
        if confidence is None:
            confidence = self.confidence

        template = _load_image(template_path)
        tpl_h, tpl_w = template.shape[:2]
        screenshot = self.capture_screen(region)

        if multi_scale:
            return self._find_all_templates_multi_scale(
                screenshot, template, tpl_w, tpl_h,
                confidence, region, max_results,
                scale_min, scale_max, scale_steps,
            )

        # 单尺度模板匹配（原有逻辑）
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

    def _find_all_templates_multi_scale(
        self,
        screenshot: np.ndarray,
        template: np.ndarray,
        tpl_w: int,
        tpl_h: int,
        confidence: float,
        region: Optional[Tuple[int, int, int, int]],
        max_results: int,
        scale_min: float,
        scale_max: float,
        scale_steps: int,
    ) -> List[MatchResult]:
        """多尺度查找所有模板匹配的内部实现"""
        scales = self._generate_scale_factors(scale_min, scale_max, scale_steps)
        all_matches: List[MatchResult] = []

        for scale in scales:
            if abs(scale - 1.0) < 1e-6:
                scaled_tpl = template
                sw, sh = tpl_w, tpl_h
            else:
                sw = max(1, int(tpl_w * scale))
                sh = max(1, int(tpl_h * scale))
                interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
                scaled_tpl = cv2.resize(template, (sw, sh), interpolation=interp)

            if sh > screenshot.shape[0] or sw > screenshot.shape[1]:
                continue

            result = cv2.matchTemplate(screenshot, scaled_tpl, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= confidence)

            for pt in zip(*locations[::-1]):
                conf = float(result[pt[1], pt[0]])

                left, top, width, height = self._to_absolute_coords(
                    pt[0], pt[1], sw, sh, region
                )
                all_matches.append(MatchResult(left, top, width, height, conf))

                # 提前截断以防候选爆炸，NMS 会进一步精简
                if len(all_matches) >= max_results * 5:
                    break

            if len(all_matches) >= max_results * 5:
                break

        return self._nms(all_matches, threshold=0.3)[:max_results]

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

    @staticmethod
    def _generate_scale_factors(
        scale_min: float = MULTI_SCALE_MIN,
        scale_max: float = MULTI_SCALE_MAX,
        scale_steps: int = MULTI_SCALE_STEPS,
    ) -> List[float]:
        """
        生成多尺度匹配的缩放因子列表，包含 1.0

        Args:
            scale_min: 最小缩放比例
            scale_max: 最大缩放比例
            scale_steps: 单侧步数，总尺度数为 2*steps+1

        Returns:
            对称的缩放因子列表，如 [0.95, 0.967, 0.983, 1.0, 1.017, 1.033, 1.05]
        """
        if scale_steps <= 0:
            return [1.0]
        return np.linspace(scale_min, scale_max, 2 * scale_steps + 1).tolist()

    def wait_for_template(
        self,
        template_path: str,
        timeout: float = DEFAULT_TIMEOUT,
        interval: float = DEFAULT_INTERVAL,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        multi_scale: bool = True,
        scale_min: float = MULTI_SCALE_MIN,
        scale_max: float = MULTI_SCALE_MAX,
        scale_steps: int = MULTI_SCALE_STEPS,
        multi_scale_early_exit: float = MULTI_SCALE_EARLY_EXIT,
    ) -> Optional[MatchResult]:
        """
        等待模板图片出现在屏幕上

        Args:
            template_path: 模板图片路径
            timeout: 超时时间（秒）
            interval: 检查间隔（秒）
            confidence: 匹配置信度
            region: 搜索区域
            multi_scale: 是否启用多尺度匹配
            scale_min: 多尺度匹配的最小缩放比例
            scale_max: 多尺度匹配的最大缩放比例
            scale_steps: 多尺度匹配的单侧步数
            multi_scale_early_exit: 多尺度匹配早期退出阈值

        Returns:
            匹配结果，超时返回 None
        """
        start_time = time.time()

        while True:
            result = self.find_template(
                template_path, confidence, region,
                multi_scale=multi_scale, scale_min=scale_min,
                scale_max=scale_max, scale_steps=scale_steps,
                multi_scale_early_exit=multi_scale_early_exit,
            )
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
        region: Optional[Tuple[int, int, int, int]] = None,
        multi_scale: bool = True,
        scale_min: float = MULTI_SCALE_MIN,
        scale_max: float = MULTI_SCALE_MAX,
        scale_steps: int = MULTI_SCALE_STEPS,
        multi_scale_early_exit: float = MULTI_SCALE_EARLY_EXIT,
    ) -> bool:
        """
        等待模板图片从屏幕上消失

        Args:
            template_path: 模板图片路径
            timeout: 超时时间（秒）
            interval: 检查间隔（秒）
            confidence: 匹配置信度
            region: 搜索区域
            multi_scale: 是否启用多尺度匹配
            scale_min: 多尺度匹配的最小缩放比例
            scale_max: 多尺度匹配的最大缩放比例
            scale_steps: 多尺度匹配的单侧步数
            multi_scale_early_exit: 多尺度匹配早期退出阈值

        Returns:
            True-成功消失, False-超时仍未消失
        """
        start_time = time.time()

        while True:
            result = self.find_template(
                template_path, confidence, region,
                multi_scale=multi_scale, scale_min=scale_min,
                scale_max=scale_max, scale_steps=scale_steps,
                multi_scale_early_exit=multi_scale_early_exit,
            )
            if result is None:
                logger.info(f"模板已消失: {template_path}")
                return True

            if timeout > 0 and time.time() - start_time > timeout:
                logger.warning(f"等待模板消失超时({timeout}s): {template_path}")
                return False

            time.sleep(interval)
