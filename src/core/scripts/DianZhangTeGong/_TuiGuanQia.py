from core.packages.visual import click
import pydirectinput as pdi
import time


def script_DianZhangTeGong_TuiGuanQia(times, scale_factor):
    base_path = './assets/DZTG_TuiGuanQia/'
    temp_region = {
        'level': (0, 0, 960, 540),
        'start': (1440, 810, 1919, 1079),
        'hammer': (0, 540, 1920, 1080),
        'exit': (0, 0, 100, 100),
        'stars': (1600, 0, 1920, 360),
        'all': (0, 0, 1920, 1080)
    }

    for i in range(times):
        print(f"\tScript:正在执行脚本:店长特供_推关卡,第{i+1}次")
        pdi.press('f')
        time.sleep(2)

        click(f'{base_path}start.png', temp_region['start'])
        while True:
            click(f'{base_path}hammer.png', temp_region['hammer'])
            time.sleep(0.8)
            if click(f'{base_path}stars.png', region=temp_region['stars'], timeout=5):
                print(f"\tScript:识别到目标完成,退出本关")
                break
        click(f'{base_path}exit.png', temp_region['exit'])
        time.sleep(1.5)
        click(f'{base_path}reward.png', temp_region['all'])
