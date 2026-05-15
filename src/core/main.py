from core.packages.tools import is_HTGame_running, menu, wait_1080
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(0)
# 0	PROCESS_DPI_UNAWARE	不感知，系统自动虚拟化
# 1	PROCESS_SYSTEM_DPI_AWARE	系统级感知
# 2	PROCESS_PER_MONITOR_DPI_AWARE	每显示器感知
def main():

    # 检测异环是否启动 / 游戏是否窗口化
    is_HTGame_running()
    wait_1080()

    # 选择菜单
    menu()




















if __name__ == '__main__':
    main()
