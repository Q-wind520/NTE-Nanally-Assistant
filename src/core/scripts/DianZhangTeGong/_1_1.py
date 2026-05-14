import pydirectinput as pdi
import time
from core.packages.visual import click
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)


def script_DianZhangTeGong_1_1(times):
    from core.packages.tools import get_hwnd, get_window
    windowInfo = get_window(get_hwnd())
    """times:执行次数"""
    base_path = './assets/DZTG_1-1/'

    for i in range(times):
        print(f"Script:正在执行脚本:店长特供_1-1,第{i+1}次")

        time.sleep(2)
        pdi.press('f')
        print("Script:已键入F")
        time.sleep(2)

        if i == 0:
            try:
                click(f'{base_path}level.png')
            except:
                pdi.moveTo(windowInfo['left']+100, windowInfo['top']+200)
                pdi.scroll(1000)
                time.sleep(0.2)
                click(f'{base_path}level_null.png')
            time.sleep(0.2)

        click(f'{base_path}start.png')
        print("Script:已点击营业按钮")
        print("Script:等待倒计时结束")
        time.sleep(5.5) # 必要的等待时长，不可删除
        # time=60
        if msslocateOnScreen() != None:
            print('Script:执行准备工作')
            click(f'{base_path}_1_2.png')
            click(f'{base_path}_1_3.png')
            click(f'{base_path}_1_1.png')
        # time=55
        if msslocateOnScreen() != None:
            print("Script:制作第一个订单")
            click(f'{base_path}_2_2.png')
            click(f'{base_path}_3_2.png')
            print("Script:完成第一个订单")
        # time=50
        if msslocateOnScreen() != None:
            print("Script:制作第二个订单")
            click(f'{base_path}_1_4.png')
            click(f'{base_path}_3_3.png')
            print("Script:完成第二个订单")
        # time=45
        if msslocateOnScreen() != None:
            print("Script:制作第三个订单")
            click(f'{base_path}_2_1.png')
            click(f'{base_path}_3_1.png')
            print("Script:完成第三个订单")
        # time=4
        if msslocateOnScreen() != None:
            print("Script:退出并领取奖励")
            click(f'{base_path}exit.png')
            time.sleep(1.2)
            click(f'{base_path}reward.png')
