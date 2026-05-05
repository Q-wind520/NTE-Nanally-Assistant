import pyautogui
import time
import scripts.DianZhangTeGong_1_1



def main():
    # 获取屏幕信息
    size_x, size_y = pyautogui.size()
    print(f"Info:检测屏幕分辨率为{size_x}×{size_y}")
    if size_x != 1920 or size_y != 1080:
        print("Warn:当前分辨率非1920x1080，坐标可能不准确，未来将继续适配更多分辨率")

    # 检测异环是否启动
    from tools import is_HTGame_running
    is_HTGame_running()

    # 选择菜单
    from tools import menu
    menu_choice = menu()
    if menu_choice == 'DianZhangTeGong_1-1':
        times = input("请输入要执行的次数: ")
        print("Info:准备执行剧本:店长特供_1-1\n"
              "Notice:请在5秒内切换到游戏界面\n"
              "Notice:请在5秒内切换到游戏界面\n"
              "Notice:请在5秒内切换到游戏界面")
        time.sleep(5)
        scripts.DianZhangTeGong_1_1.script_DianZhangTeGong_1_1(int(times))








    return 0
















if __name__ == '__main__':
    main()
