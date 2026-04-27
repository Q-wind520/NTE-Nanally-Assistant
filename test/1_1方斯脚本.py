'''
第0秒，键入F
截屏到开始营业，点击

# Ready1
截屏到ready，点击 第一行第二个 按钮
等待0.5秒，点击 第一行第三个 按钮

# Ready2
等待1秒，点击 第二行第二个 按钮
等待0.5秒，点击 第一行第四个 按钮

# 制作第一个
等待0.5秒，点击 第三行第二个 按钮

# 制作第二个
截屏到50秒，点击 第三行第三个 按钮

# 制作第三个
等待0.5秒，点击 第一行第一个 按钮
等待1秒，点击 第二行第一个 按钮
截屏到44秒，点击 第三行第一个 按钮

# 退出
等待0.5秒，点击左上角退出按钮
等待1秒，检测到领取按钮并点击
循环
'''

import time
import pyautogui as pa
import cv2
import numpy as np
from PIL import ImageGrab
import keyboard  # 用于键盘输入

x, y = pa.size()
print(x, y)

position = {
    # _行_列: x, y
    '_1_1': (50, 1000),
    '_1_2': (100, 1000),
    '_1_3': (100, 1000),
    '_1_4': (100, 1000),
    '_2_1': (100, 1000),
    '_2_2': (100, 1000),
    '_3_1': (100, 1000),
    '_3_2': (100, 1000),
    '_3_3': (100, 1000)
}



while True:

    print("Info: 正在执行脚本")
    pa.press('f')
    print("Info: 已键入F")
    region_screenshot = pa.screenshot(region=(1800, 980, 1920, 1080))
    print("Info: 正在截屏比较")

'''
def screenshot_and_click(image_path, timeout=10, confidence=0.8):
    """截屏并点击匹配到的图片位置"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 截屏
        screenshot = ImageGrab.grab()
        screenshot_np = np.array(screenshot)

        # 读取模板图片
        template = cv2.imread(image_path)
        if template is None:
            print(f"无法读取图片: {image_path}")
            return False

        # 进行模板匹配
        result = cv2.matchTemplate(screenshot_np, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            # 计算点击位置（中心点）
            h, w = template.shape[:2]
            click_x = max_loc[0] + w // 2
            click_y = max_loc[1] + h // 2

            pyautogui.click(click_x, click_y)
            print(f"点击位置: ({click_x}, {click_y}) - 匹配度: {max_val:.2f}")
            return True

        time.sleep(0.1)

    print(f"未找到图片: {image_path}")
    return False


def click_position(x, y):
    """点击指定坐标"""
    pyautogui.click(x, y)
    time.sleep(0.1)


def click_grid_position(row, col, grid_start_x=100, grid_start_y=100, grid_width=100, grid_height=100):
    """点击网格位置（假设按钮在网格中排列）"""
    x = grid_start_x + (col - 1) * grid_width
    y = grid_start_y + (row - 1) * grid_height
    click_position(x, y)
    print(f"点击网格位置: 第{row}行第{col}列")


def main():
    print("脚本开始运行...")

    # 第0秒，键入F
    print("键入F...")
    keyboard.press_and_release('f')
    time.sleep(0.1)

    # 截屏到开始营业，点击
    print("等待开始营业...")
    screenshot_and_click("start_business.png")  # 需要准备开始营业的截图

    # Ready1: 截屏到ready，点击第一行第二个按钮
    print("等待Ready1...")
    if screenshot_and_click("ready.png"):
        time.sleep(0.5)
        click_grid_position(1, 2)  # 第一行第二个按钮
        time.sleep(0.5)
        click_grid_position(1, 3)  # 第一行第三个按钮

    # Ready2: 等待1秒，点击第二行第二个按钮
    time.sleep(1)
    click_grid_position(2, 2)  # 第二行第二个按钮
    time.sleep(0.5)
    click_grid_position(1, 4)  # 第一行第四个按钮

    # 制作第一个
    time.sleep(0.5)
    click_grid_position(3, 2)  # 第三行第二个按钮

    # 制作第二个: 截屏到50秒，点击第三行第三个按钮
    print("等待50秒条件...")
    if screenshot_and_click("50_seconds.png"):  # 需要准备50秒的截图
        click_grid_position(3, 3)  # 第三行第三个按钮

    # 制作第三个
    time.sleep(0.5)
    click_grid_position(1, 1)  # 第一行第一个按钮
    time.sleep(1)
    click_grid_position(2, 1)  # 第二行第一个按钮

    # 截屏到44秒，点击第三行第一个按钮
    print("等待44秒条件...")
    if screenshot_and_click("44_seconds.png"):  # 需要准备44秒的截图
        click_grid_position(3, 1)  # 第三行第一个按钮

    # 退出
    time.sleep(0.5)
    # 点击左上角退出按钮（假设坐标）
    click_position(50, 50)

    time.sleep(1)

    # 检测到领取按钮并点击
    print("检测领取按钮...")
    if screenshot_and_click("receive_button.png"):  # 需要准备领取按钮的截图
        print("成功领取！")

    print("脚本执行完成！")


if __name__ == "__main__":
    # 等待3秒让用户切换到目标窗口
    print("3秒后开始执行，请切换到目标窗口...")
    time.sleep(3)

    try:
        while True:  # 循环执行
            main()
            print("等待5秒后开始下一次循环...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("脚本被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")
        
'''