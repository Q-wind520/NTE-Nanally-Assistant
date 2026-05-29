import time
import pydirectinput as pdi
from core.packages.visual import click, wait_image_appear, scroll
from core.packages.window import get_hwnd, get_window, activate_window


def script_DianZhangTeGong_1_1(times):
    """times:执行次数"""
    activate_window()
    window_info = get_window(get_hwnd())
    base_path = './assets/DZTG_1-1/'

    # 进入
    wait_image_appear(f'{base_path}join.png')
    pdi.press('f')
    wait_image_appear(f'{base_path}start.png')

    # 循环
    for i in range(times):
        print(f"Script: 正在执行脚本: 店长特供_1-1,第{i+1}次")
        pdi.moveTo(window_info.left + 100, window_info.top + 200)
        while wait_image_appear(f'{base_path}level_null.png', confidence=0.95, timeout=0.1) == None:
            scroll(1000)
        click(f'{base_path}level_null.png', confidence=0.9)

        click(f'{base_path}start.png')
        print("Script: 等待倒计时结束")
        wait_image_appear(f'{base_path}time59.png', timeout=6)
        print('Script: 执行准备工作')
        click(f'{base_path}_1_2.png')
        click(f'{base_path}_1_3.png')
        click(f'{base_path}_1_1.png', timesleep=1)
        print("Script: 制作第一个订单")
        click(f'{base_path}_2_2.png')
        click(f'{base_path}_3_2.png')
        print("Script: 完成第一个订单")
        wait_image_appear(f'{base_path}time52.png', timeout=6)
        print("Script: 制作第二个订单")
        click(f'{base_path}_1_4.png')
        click(f'{base_path}_3_3.png')
        print("Script: 完成第二个订单")
        wait_image_appear(f'{base_path}time43.png', timeout=6)
        print("Script: 制作第三个订单")
        click(f'{base_path}_2_1.png')
        click(f'{base_path}_3_1.png')
        print("Script: 完成第三个订单")
        wait_image_appear(f'{base_path}completed.png')
        print("Script: 退出并领取奖励")
        pdi.press('esc')
        click(f'{base_path}reward.png')
    wait_image_appear(f'{base_path}start.png')
    time.sleep(1)
    pdi.press('esc')
