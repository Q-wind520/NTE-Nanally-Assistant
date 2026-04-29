import pyautogui
import keyboard
import time

# 实时检测鼠标位置
# 按下ctrl+enter切换开始/暂停，再次按下ctrl+enter终止程序

detecting = True
print("按下 Ctrl+Enter 切换开始/暂停，再次按下 Ctrl+Enter 终止程序。")

while True:
    if keyboard.is_pressed('ctrl+enter'):
        detecting = not detecting
        if not detecting:
            print('\n检测已暂停，按 Ctrl+Enter 继续或终止。')
        else:
            print('检测已恢复，按 Ctrl+Enter 暂停或终止。')
        # 防止多次触发
        while keyboard.is_pressed('ctrl+enter'):
            time.sleep(0.2)
        if not detecting:
            continue
    if detecting:
        x, y = pyautogui.position()
        print(f"当前鼠标位置: ({x}, {y})", end='\r')
    time.sleep(0.1)
