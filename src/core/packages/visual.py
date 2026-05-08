import time


# -----图像识别坐标-----
def template_center(image_path, region=None):
    """
    image_path: 传入模板路径
    返回按钮中心坐标
    """
    # 图像缩放
    def scale_screenshop(image_path, scale_factor):
        """TODO - 通过缩放图像适配不同分辨率，scale_factor:缩放比例"""
        from PIL import Image
        img = Image.open(image_path)
        new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
        img = img.resize(new_size)
        img.save(image_path)

    from pyautogui import locateOnScreen, center
    while True:
        template = locateOnScreen(image_path, confidence=0.8, region=region)
        if template is not None:
            return center(template)
        else:
            print(f"Warn:未找到按钮图片: {image_path}，正在重试...")
            time.sleep(0.2)


# -----jiepingquyusuofang-----
def scale_region(temp_region, scale):
    """
    参数:
    temp_region: dict
    scale: float
    返回:
    new_region: dict
    """
    new_region = {}

    for key, rect in temp_region.items():
        if len(rect) != 4:
            raise ValueError(f"{key}: is uncomplete")
        x, y, width, height = rect
        scaled_x = int(round(x * scale))
        scaled_y = int(round(y * scale))
        scaled_width = int(round(width * scale))
        scaled_height = int(round(height * scale))
        new_region[key] = (scaled_x, scaled_y, scaled_width, scaled_height)
    return new_region

