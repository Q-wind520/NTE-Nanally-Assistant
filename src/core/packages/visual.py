import time
from pyautogui import locateOnScreen, center
from pydirectinput import click as pclick
from core.packages.tools import get_window


def click(image_path, region=None, timeout=10, confidence=0.8):
    """
    在屏幕上查找模板图片并点击其中心位置
    image_path: 模板图片路径
    region: 搜索区域 (left, top, right, bottom)，默认为全屏
    timeout: 超时时间(秒)，默认10秒
    confidence: 匹配置信度，默认0.8
    找到后点击并返回，未找到则继续查找直到超时
    """
    start_time = time.time()
    while True:
        # 检查是否超时
        if timeout > 0 and time.time() - start_time > timeout:
            print(f"Warn: 查找超时({timeout}s)，未找到模板图片: {image_path}")
            return False
        
        # 查找模板图片
        temp = locateOnScreen(image_path, confidence=confidence, region=region)
        if temp is not None:
            # 计算中心坐标
            center_x, center_y = center(temp)
            # 点击中心位置
            pclick(center_x, center_y)
            print(f"Info: 已点击模板图片: {image_path}，位置: ({center_x}, {center_y})")
            return True
        # 未找到，短暂等待后继续查找
        time.sleep(0.1)


def is_image_exist(image_path, region=None, confidence=0.8):
    """
    检查模板图片是否存在
    返回True或False
    """
    if locateOnScreen(image_path, confidence=confidence, region=region):
        return True
    return False









