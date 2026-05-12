from core.packages.tools import is_HTGame_running, menu, wait_1080


def main():

    # 检测异环是否启动 / 游戏是否窗口化
    is_HTGame_running()
    wait_1080()

    # 选择菜单
    menu()




















if __name__ == '__main__':
    main()
