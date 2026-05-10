# TODO:脚本，推图，识别锤子，每秒点击，3星星结束并领取，下一关，直到完成输入次数
from core.packages.visual import template_center, scale_region
import pydirectinput as pdi
import time
from pyautogui import locateOnScreen
def script_DianZhangTeGong_TuiGuanQia(times, scale_factor):

    # 引入资源路径和模板区域
    base_path = './assets/DZTG_TuiGuanQia/'
    temp_region = {
	'level': (0, 0, 960, 540),
	'start': (1440, 810, 1919, 1079),
	'hammer':(0, 540, 1920, 1080),
    'exit': (0, 0, 100, 100),
    'stars': (1600, 0, 1920, 360),
    'all': (0, 0, 1920, 1080)
    }
    temp_region = scale_region(temp_region, scale_factor)

    # 执行脚本
    for i in range(times):
        print(f"\tScript:正在执行脚本:店长特供_推关卡,第{i+1}次")
        pdi.press('f')
        time.sleep(2)

        pdi.click(*template_center(f'{base_path}start.png', region=temp_region['start']))
        while True:
            pdi.click(*template_center(f'{base_path}hammer.png', region=temp_region['hammer']))
            time.sleep(0.8)
            if locateOnScreen(f'{base_path}stars.png', confidence=0.8, region=temp_region['stars']):
                print(f"\tScript:识别到目标完成,退出本关")
                break
        pdi.click(*template_center(f'{base_path}exit.png', region=temp_region['exit']))
        time.sleep(1.5)
        pdi.click(*template_center(f'{base_path}reward.png', region=temp_region['all']))
        # 点击下一关
