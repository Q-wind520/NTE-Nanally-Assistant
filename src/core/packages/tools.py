import time


# -----检测游戏是否运行-----
def is_HTGame_running():
    from psutil import process_iter
    while True:
        for proc in process_iter(['name']):
            if proc.info['name'] == 'HTGame.exe':
                print("Info:已检测到异环进程，继续执行脚本")
                break
        else:
            print("Warn:未检测到异环进程，请确保游戏已启动")
            time.sleep(2)
            continue
        break

# -----菜单选择-----
def menu():
    from core.scripts.DianZhangTeGong._1_1 import script_DianZhangTeGong_1_1
    scripts = {
            "1": "1.店长特供_1-1" ,
            "2": "2.店长特供_退关卡" ,
            "0": "0.退出"
            }
    while True:
        try:
            print("脚本菜单:", scripts)
            choice = input("请输入数字选择脚本: ")     
            if choice == "0":
                exitNA()
            elif choice == "1": 
                times = int(input("请输入执行次数:"))
                time.sleep(1)
                active_window()
                script_DianZhangTeGong_1_1(times)
            else:
                print("Error:无效的选择，请输入有效的数字")
                continue

        except Exception as e:
            print(f"Error:发生异常: {e}")
            continue

# -----通过进程名获取窗口句柄-----
def get_hwnd(name="HTGame.exe"):
        """
        通过进程名获取窗口句柄
        返回第一个匹配的窗口句柄，如果没有找到则返回None
        """
        import win32gui # type: ignore
        import win32process # type: ignore
        from psutil import process_iter
        for proc in process_iter(['pid']):
            if proc.name() == name:
                pid = proc.pid
                break
        else:
            return None

        result = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == pid:
                    result.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return result[0] if result else None

# -----激活窗口-----
def active_window():
    import win32gui # type: ignore
    from win32con import SW_SHOWNORMAL # type: ignore
    
    hwnd = get_hwnd()
    if hwnd:
        try:
            win32gui.ShowWindow(hwnd, SW_SHOWNORMAL)
            win32gui.SetForegroundWindow(hwnd)
            print("Info: 已成功激活游戏窗口")
        except Exception as e:
            print(f"Warn: 激活窗口失败: {e}")

# -----退出娜娜莉助手-----
def exitNA():
    print("="*75)
    print("|" + " "*24 + "  NTE Nanally Assistant  " + " "*24 + "|")
    print("="*75)
    print("|" + " "*20 + "version: 0.1.0-beta by Q-wind520 " + " "*20 + "|")
    print("|" + " "*27 + "See You Next Time! " + " "*27 + "|")
    print("="*75)
    time.sleep(1)
    return 0


def get_window():
    from win32gui import EnumWindows # type: ignore
    windows = []
    EnumWindows(get_hwnd, windows)
    return windows[0] if windows else None

