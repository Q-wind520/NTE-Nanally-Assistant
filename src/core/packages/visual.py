import time
import mss
import cv2
import numpy as np
import pydirectinput as pdi
from core.packages.tools import wait_1080, get_window, get_hwnd


# -----mss查找模板图片-----
def msslocateOnScreen(
    image_path,
    confidence=0.8,
    screen_index=0
):
    """
    在指定屏幕中查找图片

    :param image_path: 模板图片路径
    :param confidence: 匹配阈值 0~1
    :param screen_index: mss 屏幕索引（1=主屏, 2=副屏...）
    :param region: (x, y, w, h) 限定区域
    :param scale: 截图缩放比例，用于将高分辨率截图缩小后匹配低分辨率模板
    :return: (left, top, width, height) or None
    """
    
    # 窗口信息[region],[scale]
    hwnd = get_hwnd()
    windowInfo = get_window(hwnd)
    if windowInfo is None:
        print("Warn: 无法获取窗口信息")
        return None
    region = (windowInfo['left'], windowInfo['top'], windowInfo['width'], windowInfo['height'])
    scale = windowInfo['scale']
    template = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if template is None:
        raise FileNotFoundError(f"图片未找到: {image_path}")

    tpl_h, tpl_w = template.shape[:2]

    with mss.mss() as sct:
        mon = sct.monitors[screen_index]

        if region:
            x, y, w, h = region
            shot = sct.grab({
                "left": mon["left"] + x,
                "top": mon["top"] + y,
                "width": w,
                "height": h
            })
            offset_x, offset_y = mon["left"] + x, mon["top"] + y
        else:
            shot = sct.grab(mon)
            offset_x, offset_y = mon["left"], mon["top"]

        img = np.array(shot)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # 如果需要缩放，将截图缩小
    if scale != 1.0:
        img_bgr = cv2.resize(img_bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    # 模板匹配
    res = cv2.matchTemplate(img_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val < confidence:
        return None

    top_left = max_loc
    # 如果缩放了，需要将匹配位置还原到原始坐标
    if scale != 1.0:
        left = int(top_left[0] / scale) + offset_x
        top = int(top_left[1] / scale) + offset_y
        width = int(tpl_w / scale)
        height = int(tpl_h / scale)
    else:
        left = top_left[0] + offset_x
        top = top_left[1] + offset_y
        width, height = tpl_w, tpl_h

    return (left, top, width, height)


# -----点击模板图片-----
def click(image_path):
    """
    在屏幕上查找模板图片并点击其中心位置
    image_path: 模板图片路径
    找到后点击并返回，未找到则继续查找直到超时
    """
    timeout, confidence = 10, 0.8

    starttime = time.time()
    while True:
        if timeout > 0 and time.time() - starttime > timeout:
            print(f"Warn: 查找超时({timeout}s)，未找到模板图片: {image_path}")
            # TODO: 超时的备选脚本
            return False

        # 查找模板图片
        temp = msslocateOnScreen(image_path, confidence=confidence)
        if temp is not None:
            left, top, width, height = temp
            center_x, center_y = left + width // 2, top + height // 2
            pdi.click(center_x, center_y)
            print(f"Info: 已点击模板图片: {image_path}，位置: ({center_x}, {center_y})")
            return True
        time.sleep(0.5)











