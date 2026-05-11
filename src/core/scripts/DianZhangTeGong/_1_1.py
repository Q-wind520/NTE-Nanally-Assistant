import pydirectinput as pdi
import time
from core.packages.visual import click

def script_DianZhangTeGong_1_1(times):
    """times:执行次数"""
    base_path = './assets/DZTG_1-1/'
    temp_region = {
        'level': (0, 0, 960, 540),
        'start': (1440, 810, 1919, 1079),
        'table': (0, 540, 1920, 1080),
        'exit': (0, 0, 100, 100)
    }

    for i in range(times):
        print(f"\tScript:正在执行脚本:店长特供_1-1,第{i+1}次")

        time.sleep(2)
        pdi.press('f')
        print("\tScript:已键入F")
        time.sleep(2)

        if i == 0:
            click(f'{base_path}level.png', temp_region['level'])
            time.sleep(0.5)

        click(f'{base_path}start.png', temp_region['start'])
        print("\tScript:已点击营业按钮")
        print("\tScript:等待倒计时结束")
        time.sleep(6) # 必要的等待时长，不可删除

        print('\tScript:执行准备工作')
        click(f'{base_path}_1_2.png', temp_region['table'])
        time.sleep(0.3)
        click(f'{base_path}_1_3.png', temp_region['table'])
        time.sleep(1)
        click(f'{base_path}_1_1.png', temp_region['table'])
        # time=1.3
        print("\tScript:制作第一个订单")
        click(f'{base_path}_2_2.png', temp_region['table'])
        time.sleep(0.3)
        click(f'{base_path}_3_2.png', temp_region['table'])
        time.sleep(0.5)
        print("\tScript:完成第一个订单")
        # time=2.1
        print("\tScript:制作第二个订单")
        click(f'{base_path}_1_4.png', temp_region['table'])
        time.sleep(4.9)
        click(f'{base_path}_3_3.png', temp_region['table'])
        print("\tScript:完成第二个订单")
        # time=7
        print("\tScript:制作第三个订单")
        click(f'{base_path}_2_1.png', temp_region['table'])
        time.sleep(5)
        click(f'{base_path}_3_1.png', temp_region['table'])
        print("\tScript:完成第三个订单")
        # time=12
        print("\tScript:退出并领取奖励")
        click(f'{base_path}exit.png', temp_region['exit'])
        time.sleep(2)
        click(f'{base_path}reward.png')
