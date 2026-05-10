import pyautogui
import time
from core.scripts.DianZhangTeGong._1_1 import *
from core.packages.tools import *


def main():
    # 获取屏幕信息并计算缩放比例
    scale_factor = get_scale()

    # 检测异环是否启动
    is_HTGame_running()

    # 主循环
    while True:
        # 选择菜单
        menu_choice, times = menu()
        # script launcher
        if menu_choice == 'exit':
            break
        elif menu_choice == 'DianZhangTeGong_1-1':
            active_window()
            script_DianZhangTeGong_1_1(times, scale_factor)
        else:pass

    # exit
    print("="*75)
    print("|" + " "*24 + "  NTE Nanally Assistant  " + " "*24 + "|")
    print("="*75)
    print("|" + " "*20 + "version: 0.1.0-beta by Q-wind520 " + " "*20 + "|")
    print("|" + " "*27 + "See You Next Time! " + " "*27 + "|")
    print("="*75)

    time.sleep(2)
    return 0
















if __name__ == '__main__':
    main()
