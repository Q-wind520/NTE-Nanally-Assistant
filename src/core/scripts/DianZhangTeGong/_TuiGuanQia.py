import time
import pydirectinput as pdi
from core.packages.visual import click, wait_image_appear
from core.packages.window import wait_for_1080p_resolution, get_hwnd, get_window


def script_DianZhangTeGong_TuiGuanQia(times):
    base_path = './assets/DZTG_TuiGuanQia/'
    window_info = get_window(get_hwnd())
    wait_for_1080p_resolution()
    for i in range(times):
        print(f"Script: 正在执行脚本:店长特供_推关卡,第{i+1}次")

    time.sleep(2)
    pdi.press('f')
    print("Script:已键入F")
    time.sleep(2)











