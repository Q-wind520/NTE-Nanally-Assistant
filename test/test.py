import pyautogui
import pydirectinput
import psutil
import time

# 获取屏幕信息
size_x, size_y = pyautogui.size()
print(f"Info:检测屏幕分辨率为{size_x}×{size_y}")

# 检测游戏是否启动
def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

if not is_process_running('HTGame.exe'):
    print("Error:未检测到异环进程，请确保游戏已启动")
    exit(1)

# 定义坐标位置
'''
position = {
    # _行_列: x, y
    'action': (1712, 1007),
    '_1_1': (125, 994),
    '_1_2': (742, 988),
    '_1_3': (986, 987),
    '_1_4': (1268, 1022),
    '_2_1': (145, 803),
    '_2_2': (653, 798),
    '_3_1': (242, 649),
    '_3_2': (415, 629),
    '_3_3': (1055, 652),
    'exit': (44, 57)
}
'''

# 执行脚本
print("Info:请在5秒钟内切换到游戏界面，脚本将自动执行")
print("Info:请在5秒钟内切换到游戏界面，脚本将自动执行")
print("Info:请在5秒钟内切换到游戏界面，脚本将自动执行")
time.sleep(5)  # 给用户5秒钟时间切换到游戏界面

n = 2
for i in range(n):
    print("Info:正在执行脚本:店长特供1-1")
    time.sleep(2)
    pydirectinput.press('f')
    time.sleep(2)
    print("Info:已键入F")
    pydirectinput.click(1712, 1007)
    time.sleep(6)
    print("Info:已点击营业按钮")

    pydirectinput.click(742, 988)
    time.sleep(0.5)
    pydirectinput.click(986, 987)
    time.sleep(1)
    pydirectinput.click(125, 994)
    time.sleep(1)
    pydirectinput.click(653, 798)
    time.sleep(0.5)
    pydirectinput.click(1268, 1022)
    time.sleep(0.5)
    pydirectinput.click(415, 629)
    time.sleep(0.5)
    pydirectinput.click(145, 803)
    # time=4.5s
    time.sleep(3.5)
    pydirectinput.click(1055, 652)
    # time=8s
    time.sleep(8)
    pydirectinput.click(242, 649)
    time.sleep(0.5)
    pydirectinput.click(44, 57)
    time.sleep(1)
    pydirectinput.click(1169, 835)




