
import pyautogui
import time
import os
from typing import Optional, Tuple, Union


############ 分区域比较截图 ############
def region_compare(region_num: int, # 区域编号(0:全屏, 1-6:屏幕区域)
                   image_path: str, # 比较图像路径
                   timeout: float = 60.0) -> Union[bool, Tuple[int, int]]:


    # 验证图片文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在{image_path}")
        return False

    # 获取屏幕尺寸
    screen_width, screen_height = pyautogui.size()

    # 计算区域边界
    def get_region_coordinates(num: int) -> Tuple[int, int, int, int]: # (left, top, width, height)

        if num == 0:  # 全屏
            return 0, 0, screen_width, screen_height

        # 计算6个等大区域的网格
        # 2行3列的网格
        rows = 2
        cols = 3

        region_width = screen_width // cols
        region_height = screen_height // rows

        # 计算区域索引（从1开始）
        num -= 1
        row = num // cols
        col = num % cols

        left = col * region_width
        top = row * region_height

        # 确保最后一个区域能覆盖到屏幕边缘
        if col == cols - 1:
            region_width = screen_width - left
        if row == rows - 1:
            region_height = screen_height - top

        return left, top, region_width, region_height

    # 开始时间
    start_time = time.time()

    # 循环查找图片
    while time.time() - start_time < timeout:
        try:
            # 获取对应区域
            region_coords = get_region_coordinates(region_num)

            # 在指定区域内查找图片
            location = pyautogui.locateOnScreen(
                image_path,
                region=region_coords,
                confidence=0.9,  # 可调整的置信度
                grayscale=False
            )

            # 如果找到图片
            if location:
                center_point = pyautogui.center(location)

                print(f"Info: 找到图片: {image_path} 在区域 {region_num}")
                print(f"位置: {location}")
                return Union[True, center_point]

        except pyautogui.ImageNotFoundException:
            # 没找到图片，继续循环
            pass
        except Exception as e:
            print(f"Error: 查找图片时发生错误: {e}")
            return False

        # 短暂等待后继续查找
        time.sleep(0.5)

    # 超时
    print(f"Error: 未找到图片 {image_path}")
    return False

# 包含函数
'''
######### 获取区域信息 #########
def get_region_info(region_num: int) -> Tuple[int, int, int, int]:


    screen_width, screen_height = pyautogui.size()

    if region_num == 0:  # 全屏
        return 0, 0, screen_width, screen_height

    # 计算6个等大区域的网格
    rows = 2
    cols = 3

    region_width = screen_width // cols
    region_height = screen_height // rows

    # 计算区域索引（从1开始）
    num = region_num - 1
    row = num // cols
    col = num % cols

    left = col * region_width
    top = row * region_height

    # 确保最后一个区域能覆盖到屏幕边缘
    if col == cols - 1:
        region_width = screen_width - left
    if row == rows - 1:
        region_height = screen_height - top

    return left, top, region_width, region_height


######### 截取指定区域 #########
def capture_region(region_num: int, save_path: Optional[str] = None) -> Optional[pyautogui.Image]:

    try:
        region_coords = get_region_info(region_num)
        screenshot = pyautogui.screenshot(region=region_coords)

        if save_path:
            screenshot.save(save_path)
            print(f"截图已保存到: {save_path}")

        return screenshot
    except Exception as e:
        print(f"截图失败: {e}")
        return None
'''


# test
print("\n"+"="*30)
print()
result = region_compare(0, 'D:\project\\NTE NA\\test\屏幕截图 2026-04-27 123405.png')

if result:
    x, y = result
    pyautogui.moveTo(x, y)
    pyautogui.click()
    print("True")
else:
    print("False")
