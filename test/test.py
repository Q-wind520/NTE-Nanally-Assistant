import pyautogui
import pydirectinput
import psutil
import time
import cv2
import numpy as np
# import win32gui(尝试自动激活游戏窗口，但可能存在兼容性问题，暂时注释掉)

# 寻找模板在屏幕上的位置，返回中心坐标
"""
def find_template_on_screen(template_path, confidence=0.8):
    # 截取屏幕
    screen = pyautogui.screenshot()
    screen_np = np.array(screen)
    screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
    
    # 读取模板
    template = cv2.imread(template_path, 0)
    w, h = template.shape[::-1]
    
    # 模板匹配
    res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    if max_val >= confidence:
        # 返回中心点坐标
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return center_x, center_y, max_val
    return None
"""

# 检测游戏是否启动
def is_HTGame_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'HTGame.exe':
            return True
    print("Error:未检测到异环进程，请确保游戏已启动")
    exit(1)


# 脚本_店长特供_1-1(int执行次数,lib脚本坐标信息)
def script_DianZhangTeGong_1_1(times, actual_position):
    for i in range(times):
        print(f"Info:正在执行脚本:店长特供1-1,第{i}次")
        time.sleep(2)
        pydirectinput.press('f')
        time.sleep(2)
        print("Info:已键入F")
        pydirectinput.click(*actual_position['level'])
        time.sleep(0.5)
        pydirectinput.click(*actual_position['action'])
        print("Info:等待倒计时结束")
        time.sleep(6)
        print("Info:已点击营业按钮")
        print('Info:执行准备工作')
        pydirectinput.click(*actual_position['_1_2'])
        time.sleep(0.5)
        pydirectinput.click(*actual_position['_1_3'])
        time.sleep(1)
        pydirectinput.click(*actual_position['_1_1'])
        time.sleep(1)
        pydirectinput.click(*actual_position['_1_4'])
        time.sleep(0.5)
        pydirectinput.click(*actual_position['_2_2'])
        time.sleep(0.5)
        pydirectinput.click(*actual_position['_3_2'])
        print("Info:完成第一个订单")
        time.sleep(0.5)
        pydirectinput.click(*actual_position['_2_1'])
        # time=4s
        print("Info:等待第二个订单")
        time.sleep(3.5)
        pydirectinput.click(*actual_position['_3_3'])
        print("Info:完成第二个订单")
        # time=7.5s
        print("Info:等待第三个订单")
        time.sleep(7.5)
        pydirectinput.click(*actual_position['_3_1'])
        print("Info:完成第三个订单")
        time.sleep(0.5)
        pydirectinput.click(*actual_position['exit'])
        time.sleep(0.5)
        pydirectinput.click(*actual_position['receive'])


def test():

    # 引入脚本位置坐标
    position_DianZhangTeGong_1_1 = {
        # _行_列: x, y
        'action': (1712, 1007),
        'level': (164, 394),
        '_1_1': (125, 994),
        '_1_2': (742, 988),
        '_1_3': (986, 987),
        '_1_4': (1268, 1022),
        '_2_1': (145, 803),
        '_2_2': (653, 798),
        '_3_1': (242, 649),
        '_3_2': (415, 629),
        '_3_3': (1055, 652),
        'exit': (44, 57),
        'receive': (1169, 835)  # 添加缺失的坐标
    }

    # 获取屏幕信息
    size_x, size_y = pyautogui.size()
    print(f"Info:检测屏幕分辨率为{size_x}×{size_y}")

    # 检测异环是否启动
    is_HTGame_running()

    # 给用户5秒钟时间切换到游戏界面
    print("Info:请在5秒钟内切换到游戏界面，脚本将自动执行\n"*3,end='')
    # win32gui.SetForegroundWindow(win32gui.FindWindow(None, 'HTGame'))
    time.sleep(5)

    # 执行脚本
    script_DianZhangTeGong_1_1(10, position_DianZhangTeGong_1_1)

if __name__ == '__test__':
    test()
