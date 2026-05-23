import time
import pydirectinput as pdi
from core.packages.visual import click, wait_image_appear
from core.packages.window import activate_window


def next_level():
    pass

def script_DianZhangTeGong_TuiGuanQia(times):
    activate_window()
    base_path = './assets/DZTG_TuiGuanQia/'
    for i in range(times):
        print(f"Script: 正在执行脚本:店长特供_推关卡,第{i+1}次")

        time.sleep(2)
        pdi.press('f')
        print("Script:已键入F")
        time.sleep(2)
        next_level()# 选关卡
        click('./assets/DZTG_1-1/start.png')
        wait_image_appear('./assets/DZTG_1-1/time59.png')
        while not wait_image_appear('./assets/DZTG_1-1/completed.png'):
            click(f'{base_path}hammer.png')
        click('./assets/DZTG_1-1/exit.png')
        click('./assets/DZTG_1-1/reward.png')










