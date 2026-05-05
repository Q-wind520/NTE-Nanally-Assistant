import pydirectinput
import time

# 脚本_店长特供_1-1(int执行次数)
def script_DianZhangTeGong_1_1(times):
    # 引入脚本位置坐标
    actual_position = {
        # _行_列: x, y
        'action': (1712, 1007),
        'level': (164, 394),
        '_1_1': (125, 994),
        '_1_2': (742, 988),
        '_1_3': (986, 987),
        '_1_4': (1268, 1022),
        '_2_1': (145, 803),
        '_2_2': (653, 798),
        '_3_1': (242, 649),
        '_3_2': (415, 629),
        '_3_3': (1055, 652),
        'exit': (44, 57),
        'receive': (1169, 835)
    }

    # 执行脚本
    for i in range(times):
        print(f"Script:正在执行脚本:店长特供_1-1,第{i+1}次")
        time.sleep(2)
        pydirectinput.press('f')
        time.sleep(2)
        print("Script:已键入F")
        pydirectinput.click(*actual_position['level'])
        time.sleep(0.5)
        pydirectinput.click(*actual_position['action'])
        print("Script:等待倒计时结束")
        time.sleep(6)
        print("Script:已点击营业按钮")
        print('Script:执行准备工作')
        pydirectinput.click(*actual_position['_1_2'])
        time.sleep(0.5)
        pydirectinput.click(*actual_position['_1_3'])
        time.sleep(1)
        pydirectinput.click(*actual_position['_1_1'])
        time.sleep(1)
        pydirectinput.click(*actual_position['_1_4'])
        time.sleep(0.5)
        pydirectinput.click(*actual_position['_2_2'])
        time.sleep(0.5)
        pydirectinput.click(*actual_position['_3_2'])
        print("Script:完成第一个订单")
        time.sleep(0.5)
        pydirectinput.click(*actual_position['_2_1'])
        # time=4s
        print("Script:等待第二个订单")
        time.sleep(3.5)
        pydirectinput.click(*actual_position['_3_3'])
        print("Script:完成第二个订单")
        # time=7.5s
        print("Script:等待第三个订单")
        time.sleep(7.5)
        pydirectinput.click(*actual_position['_3_1'])
        print("Script:完成第三个订单")
        time.sleep(0.5)
        pydirectinput.click(*actual_position['exit'])
        time.sleep(0.5)
        pydirectinput.click(*actual_position['receive'])





