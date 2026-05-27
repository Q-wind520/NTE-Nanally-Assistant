import time
import pydirectinput as pdi
from core.packages.visual import click, wait_image_appear, wait_image_disappear
from core.packages.window import wait_for_target_resolution, activate_window


def script_DiaoYu(times):
    activate_window()
    base_path = './assets/DY/'
    wait_for_target_resolution()

    print("Script: 等待玩家站到钓鱼点")
    while True:
        if wait_image_appear(f'{base_path}DiaoYu.png') != None: break
    pdi.press('f')
    click(f"{base_path}start.png")
    if wait_image_appear(f'{base_path}lacking.png', timeout=1):
            print("Script: 鱼饵已耗尽")
            pdi.press('esc')
            return -1
    time.sleep(2)
    for i in range(times):
        print(f"Script: 正在执行脚本: 自动钓鱼,第{i+1}次")
        time.sleep(1)
        pdi.press('f')
        if wait_image_appear(f'{base_path}lacking.png', timeout=1):
            print("Script: 鱼饵已耗尽")
            break

        # 上鱼
        try:
            wait_image_appear(f'{base_path}upfish.png', timeout=20, confidence=0.7)
        except:
            print("Script: 鱼儿逃走了")
            i -= 1
            continue
        pdi.press('f')
        time.sleep(2)
        wait_image_appear(f'{base_path}close.png', timeout=20, confidence=0.7)
        time.sleep(0.5)
        pdi.click()
    pdi.press('esc')
    time.sleep(1)
    pdi.press('esc')
