import pydirectinput as pdi
import time
from core.packages.visual import template_center

# 脚本_店长特供_1-1(int执行次数)
def script_DianZhangTeGong_1_1(times):
    """times:执行次数"""

    # 执行脚本
    for i in range(times):
        print(f"\tScript:正在执行脚本:店长特供_1-1,第{i+1}次")
        time.sleep(2)
        pdi.press('f')
        print("\tScript:已键入F")
        time.sleep(2)
        # 关卡1-1 && 开始营业 && 等待
        pdi.click(*(template_center('./assets/DZTG_1-1/level.png')))
        time.sleep(0.5)
        pdi.click(*(template_center('./assets/DZTG_1-1/start.png')))
        print("\tScript:已点击营业按钮")
        print("\tScript:等待倒计时结束")
        time.sleep(6)
        # 开始做饭
        print('\tScript:执行准备工作')
        pdi.click(*template_center('./assets/DZTG_1-1/_1_2.png'))
        time.sleep(0.5)
        pdi.click(*(template_center('./assets/DZTG_1-1/_1_3.png')))
        time.sleep(1)
        pdi.click(*(template_center('./assets/DZTG_1-1/_1_1.png')))
        time.sleep(1)
        print("\tScript:制作第一个订单")
        pdi.click(*(template_center('./assets/DZTG_1-1/_2_2.png')))
        time.sleep(0.5)
        pdi.click(*(template_center('./assets/DZTG_1-1/_3_2.png')))
        time.sleep(0.5)
        print("\tScript:完成第一个订单")
        print("\tScript:制作第二个订单")
        pdi.click(*(template_center('./assets/DZTG_1-1/_1_4.png')))
        time.sleep(3.5)
        # time=7s
        pdi.click(*(template_center('./assets/DZTG_1-1/_3_3.png')))
        print("\tScript:完成第二个订单")
        print("\tScript:制作第三个订单")
        pdi.click(*(template_center('./assets/DZTG_1-1/_2_1.png')))
        time.sleep(8.5)
        # time=16s
        pdi.click(*(template_center('./assets/DZTG_1-1/_3_1.png')))
        print("\tScript:完成第三个订单")
        print("\tScript:退出并领取奖励")
        time.sleep(0.5)
        pdi.click(*(template_center('./assets/DZTG_1-1/exit.png')))
        time.sleep(1.5)
        pdi.click(*(template_center('./assets/DZTG_1-1/reward.png')))





