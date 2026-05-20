from core.packages.process import wait_for_game_process
from core.packages.window import wait_for_1080p_resolution
from core.packages.menu import run_menu
from core.packages.exit import exit_program
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(2)
# 0	PROCESS_DPI_UNAWARE	不感知，系统自动虚拟化（会导致 Win32 坐标与 MSS 物理像素不匹配）
# 1	PROCESS_SYSTEM_DPI_AWARE	系统级感知
# 2	PROCESS_PER_MONITOR_DPI_AWARE	每显示器感知（Win32 坐标 = 物理像素，与 MSS 一致）


def main():
    # 检测异环是否启动 / 游戏是否窗口化
    wait_for_game_process()
    wait_for_1080p_resolution()

    # 选择菜单
    run_menu(exit_func=exit_program)


if __name__ == '__main__':
    main()
