import time


# -----图像识别坐标-----
def template_center(image_path):
    """
    image_path: 传入模板路径
    返回按钮中心坐标
    """
    # TODO:兼容分辨率，通过图像缩放
    # 图像缩放
    def scale_image(image_path, scale_factor):
        """传入图片路径和缩放因子，缩放图片并覆盖原图"""
        from PIL import Image
        img = Image.open(image_path)
        new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
        img = img.resize(new_size)
        img.save(image_path)

    from pyautogui import locateOnScreen, center
    for i in range(3):
        template = locateOnScreen(image_path, confidence=0.8)
        if template is not None: return center(template)
        else:
            print(f"Warn:未找到按钮图片: {image_path}，正在重试...({i+1}/3)")
            time.sleep(0.2)
    print(f"Error:未找到按钮图片: {image_path}，请确保分辨率为1920x1080")
    exit(1)
