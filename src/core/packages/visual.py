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
