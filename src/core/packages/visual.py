import time


# -----图像识别坐标-----
def template_center(image_path, region=None, scale_factor=1):
    """
    image_path: 传入模板路径
    返回按钮中心坐标
    """

    from PIL import Image
    from pyautogui import locateOnScreen, center

    img = Image.open(image_path)
    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
    img = img.resize(new_size)

    while True:
        temp = locateOnScreen(image_path, confidence=0.8, region=region)
        
        if temp is not None:
            return center(temp)
        else:
            print(f"Warn:未找到按钮图片: {image_path}，正在重试...")
            time.sleep(0.2)


# -----截屏区域缩放-----
def scale_region(temp_region, scale):
    """
    传入: temp_region=1080P区域, scale=缩放比; 
    返回: new_region=当前分辨率的区域
    """
    new_region = {}

    for key, rect in temp_region.items():
        if len(rect) != 4:
            raise ValueError(f"{key}: is uncomplete")
        x, y, width, height = rect
        new_x = int(round(x * scale))
        new_y = int(round(y * scale))
        new_width = int(round(width * scale))
        new_height = int(round(height * scale))
        new_region[key] = (new_x, new_y, new_width, new_height)
    return new_region



