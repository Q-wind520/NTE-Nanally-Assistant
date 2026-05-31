import time
import pydirectinput as pdi
from core.packages.constants import get_asset_path as gap
from core.packages.visual import click, wait_image_appear
from core.packages.window import activate_window


def next_level():
    pass

def script_DianZhangTeGong_TuiGuanQia(times):
    activate_window()
    base_tg = gap('assets', 'DZTG_TuiGuanQia')
    base_1_1 = gap('assets', 'DZTG_1-1')
    for i in range(times):
        print(f"Script: 正在执行脚本:店长特供_推关卡,第{i+1}次")

        time.sleep(2)
        pdi.press('f')
        print("Script:已键入F")
        time.sleep(2)
        next_level()# 选关卡
        click(str(base_1_1 / 'start.png'))
        wait_image_appear(str(base_1_1 / 'time59.png'))
        while not wait_image_appear(str(base_1_1 / 'completed.png')):
            click(str(base_tg / 'hammer.png'))
        click(str(base_1_1 / 'exit.png'))
        click(str(base_1_1 / 'reward.png'))










