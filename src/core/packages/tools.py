import time


# -----检测游戏是否运行-----
def is_HTGame_running():
    from psutil import process_iter
    starttime = time.time()
    while True:
        for proc in process_iter(['name']):
            if proc.info['name'] == 'HTGame.exe':
                print("Info: 已检测到异环进程，继续")
                break
        if time.time() - starttime > 300:
            print("FATAL: 长时间未检测到游戏进程，异常退出")
            exit(-1)
        if int(time.time() - starttime) % 10 == 0:
            print("Warn: 未检测到异环进程，等待游戏启动")
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
    exit(0)

# -----获取窗口信息-----
def get_window(hwnd):
    """
    hwnd: 窗口句柄
    返回: 窗口信息字典，包含位置和尺寸
    {
        'left': 窗口左上角X坐标,
        'top': 窗口左上角Y坐标,
        'right': 窗口右下角X坐标,
        'bottom': 窗口右下角Y坐标,
        'width': 窗口宽度,
        'height': 窗口高度
    }
    """
    import win32gui
    import ctypes
    
    if not hwnd:
        return None
    
    from pyautogui import size
    screen_width, screen_height = size()

    
    # 获取窗口矩形区域
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    
    # 非全屏时减去窗口边框
    height = bottom - top
    if height < screen_height:
        left += 9; right -= 9; top += 37; bottom -= 10

    
    # 计算宽度和高度
    width = right - left
    height = bottom - top
    
    return {
        'left': left,
        'top': top,
        'right': right,
        'bottom': bottom,
        'width': width,
        'height': height
    }


# -----直到1080窗口才继续-----
def wait_1080():
    # -----是1080吗-----
    def is_1080():
        window_info = get_window(get_hwnd())
        if window_info is None:
            print("Warn: 无法获取窗口信息")
            return False
        if window_info['height'] == 1080:
            return True
        return False
    
    starttime = time.time()
    while True:
        if not is_1080():
            elapsed = time.time() - starttime
            if elapsed < 5:
                print("Error: 请将游戏窗口化为1920×1080分辨率，不能执行脚本")
                print("Notice: 正在等柠窗口化...")
                time.sleep(5)
            elif elapsed < 300:
                print(f"Notice: 等待窗口化中 ({int(elapsed)}s)")
                time.sleep(2)
            else:
                print("FATAL: 长时间未检测到窗口化，异常退出")
                exit(-1)
        else:
            print("Info: 检测到已窗口化为1080，继续")
            break
        




