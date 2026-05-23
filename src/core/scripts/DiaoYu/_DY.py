import time
import pydirectinput as pdi
from core.packages.visual import click, wait_image_appear, wait_image_disappear
from core.packages.window import wait_for_1080p_resolution


def script_DiaoYu(times):
    base_path = './assets/DY/'
    wait_for_1080p_resolution()

    wait_image_appear(f'{base_path}DiaoYu.png')
    print("Script: 等待玩家站到钓鱼点")
    pdi.press('f')
    click(f"{base_path}start.png")
    time.sleep(2)
    for i in range(times):
        print(f"Script: 正在执行脚本: 自动钓鱼,第{i+1}次")
        pdi.press('f')
        wait_image_appear(f'{base_path}upfish.png')
        pdi.press('f')
        wait_image_disappear(f'{base_path}disappear.png')
        click(f'{base_path}close.png')
