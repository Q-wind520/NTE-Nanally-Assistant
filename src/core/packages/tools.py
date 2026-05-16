import time
import win32gui
import win32process


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
        if int(time.time() - starttime) % 10 == 1:
            print("Warn: 未检测到异环进程，等待游戏启动")
            time.sleep(2)
            continue
        break

# -----菜单选择-----
def menu():
    from core.scripts.DianZhangTeGong._1_1 import script_DianZhangTeGong_1_1
    scripts = {
            "1": "店长特供_1-1" ,
            "2": "店长特供_退关卡" ,
            "0": "退出"
            }
    while True:
        try:
            print("脚本菜单:")
            for key, value in scripts.items():
                print(f"{key}: {value}")
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
def get_hwnd(name: str = "HTGame.exe") -> int:
    """
    通过进程名获取窗口句柄
    
    Args:
        name: 进程名，默认为 HTGame.exe
        
    Returns:
        窗口句柄（整数）
        
    Raises:
        RuntimeError: 找不到进程或窗口时抛出
    """
    from psutil import process_iter
    
    # 查找进程 PID
    pid = None
    for proc in process_iter(['pid', 'name']):
        if proc.info['name'] == name:
            pid = proc.info['pid']
            break
    
    if pid is None:
        raise RuntimeError(f"无法找到进程: {name}")
    
    # 枚举窗口查找属于该进程的可见窗口
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == pid:
                result.append(hwnd)
    
    win32gui.EnumWindows(callback, None)
    
    if not result:
        raise RuntimeError(f"无法找到进程 {name} 的可见窗口")
    
    return result[0]

# -----激活窗口-----
def active_window():
    from win32con import SW_SHOWNORMAL
    
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
    print("|" + " "*20 + "  version: 0.2.0  by Q-wind520   " + " "*20 + "|")
    print("|" + " "*27 + "See You Next Time! " + " "*27 + "|")
    print("="*75)
    time.sleep(1)
    exit(0)

# 窗口边框常量（针对异环游戏窗口）
WINDOW_BORDER_LEFT = 9
WINDOW_BORDER_RIGHT = 9
WINDOW_BORDER_TOP = 37
WINDOW_BORDER_BOTTOM = 10
TARGET_ASPECT_RATIO = 16 / 9  # 16:9 宽高比
TARGET_HEIGHT = 1080


# -----获取窗口信息-----
def get_window(hwnd: int) -> dict:
    """
    获取窗口信息，自动处理窗口边框
    
    Args:
        hwnd: 窗口句柄
        
    Returns:
        窗口信息字典，包含位置和尺寸
        
    Raises:
        ValueError: 窗口句柄无效或窗口尺寸异常
    """
    if not hwnd or not win32gui.IsWindow(hwnd):
        raise ValueError(f"无效的窗口句柄: {hwnd}")
    
    # 获取窗口矩形区域（包含边框）
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    
    # 计算原始尺寸
    raw_width = right - left
    raw_height = bottom - top
    
    if raw_width <= 0 or raw_height <= 0:
        raise ValueError(f"窗口尺寸异常: {raw_width}x{raw_height}")
    
    # 判断是否接近16:9宽高比（允许±5%误差）
    # 使用浮点除法而非整数除法
    actual_ratio = raw_width / raw_height
    is_16_9 = abs(actual_ratio - TARGET_ASPECT_RATIO) < 0.05
    
    # 如果不是标准16:9（窗口模式），减去窗口边框
    if not is_16_9:
        left += WINDOW_BORDER_LEFT
        right -= WINDOW_BORDER_RIGHT
        top += WINDOW_BORDER_TOP
        bottom -= WINDOW_BORDER_BOTTOM
    
    # 计算客户区尺寸
    width = right - left
    height = bottom - top
    
    # 确保客户区尺寸有效
    if width <= 0 or height <= 0:
        raise ValueError(f"窗口客户区尺寸无效: {width}x{height}")
    
    # 计算缩放比例（基于高度）
    scale = TARGET_HEIGHT / height if height > 0 else 1.0
    
    return {
        'left': left,
        'top': top,
        'right': right,
        'bottom': bottom,
        'width': width,
        'height': height,
        'scale': scale
    }


# -----直到1080窗口才继续-----
def wait_1080():
    starttime = time.time()
    while True:
        windowInfo = get_window(get_hwnd())
        if (windowInfo['height'] != 1080) and (windowInfo['width'] // windowInfo['height'] != 16 // 9):
            elapsed = time.time() - starttime
            if elapsed < 5:
                print("Error: 不能执行脚本, 请将游戏窗口化为1920×1080分辨率")
                print("Notice: 正在等待你为其窗口化..." \
                "Notice: 如若已经窗口化为1080问题仍存在，请向开发者反应详细信息")
                time.sleep(5)
            elif elapsed < 300:
                print(f"Notice: 等待窗口化中 ({int(elapsed)}/300s)")
                time.sleep(2)
            else:
                print("FATAL: 长时间未检测到窗口化，异常退出")
                exit(-1)
        else:
            return True









