import pyautogui
import time
from core.scripts.DianZhangTeGong._1_1 import *
from core.packages.tools import *



def main():
    # 获取屏幕信息并计算缩放比例
    scale_factor = get_scale()

    # 检测异环是否启动
    is_HTGame_running()
    while True:
        # 选择菜单
        menu_choice, times = menu()
        # script launcher
        if menu_choice == 'exit':
            break
        elif menu_choice == 'DianZhangTeGong_1-1':
            print("Info:准备执行剧本:店长特供_1-1\n"
                "Notice:请在5秒内切换到游戏界面\n"
                "Notice:请在5秒内切换到游戏界面\n"
                "Notice:请在5秒内切换到游戏界面")
            time.sleep(5)
            script_DianZhangTeGong_1_1(times, scale_factor)
        else:
            pass
    # exit
    print("=======================")
    print(" NTE Nanally Assistant ")
    print("=======================")
    print("        See You        ")
    print("=======================")

    time.sleep(2)
    return 0
















if __name__ == '__main__':
    main()
