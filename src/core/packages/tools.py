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
    scripts = {
            "_1": "1.xxxx_1-1" ,
            "_2": "2.xxxx_tuiguanqia" ,
            "_0": "0.exit"
            }
    while True:
        try:
            print("请选择要执行的脚本:")
            print(scripts)
            choice = input("请输入数字选择脚本: ")     
            if choice == "_0":
                return 'exit', None
            elif choice == "_1":
                times = input("please input times:")
                return 'DianZhangTeGong_1-1', int(times)
            else:
                print("Error:无效的选择，请输入有效的数字")

        except Exception as e:
            print(f"Error:发生异常: {e}")

# -----获取游戏窗口信息并计算缩放比例-----
def get_scale():
    """判断分辨率是否适配，返回缩放比例"""
    from pyautogui import size
    x, y = size()
    if x == 1920 and y == 1080:
        scale_factor = 1
    elif (x != 1920 or y != 1080) and (x // y == 16 // 9):
        print("Warn:当前分辨率非1920x1080，坐标可能不准确")
        scale_factor = x / 1920
    else:
        print("Error:当前分辨率非16:9，坐标不适配,请调整分辨率为16:9")
        exit(1)
    return scale_factor

# -----通过进程名获取窗口句柄-----
def get_hwnd_by_process(name="HTGame.exe"):
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
    from win32gui import SetForegroundWindow # type: ignore
    hwnd = get_hwnd_by_process()
    if hwnd:
        SetForegroundWindow(hwnd)