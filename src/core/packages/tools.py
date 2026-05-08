import time


# -----检测游戏是否运行-----
def is_HTGame_running():
    import psutil
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'HTGame.exe':
            print("Info:已检测到异环进程，继续执行脚本")
    print("Error:未检测到异环进程，请确保游戏已启动")
    exit(1)

# -----菜单选择-----
def menu():
    try:
        print("请选择要执行的脚本:")
        print("1. 店长特供_1-1")
        choice = input("请输入数字选择脚本: ")
        if choice == '1':
            return 'DianZhangTeGong_1-1'
        else:
            print("Error:无效的选择，请输入有效的数字")
            exit(1)

    except Exception as e:
        print(f"Error:发生异常: {e}")
        exit(1)

# -----获取游戏窗口信息并计算缩放比例-----
def ScreenInfo():
    """判断分辨率是否适配，返回缩放比例"""
    from pyautogui import size
    x, y = size()
    print(f"Info:检测屏幕分辨率为{x}×{y}")
    if x == 1920 and y == 1080:
        scale_factor = 1
    elif (x != 1920 or y != 1080) and (x // y == 16 // 9):
        print("Warn:当前分辨率非1920x1080，坐标可能不准确")
        scale_factor = x / 1920 if x < 1920 else 1920 / x
    else:
        print("Error:当前分辨率非16:9，坐标不适配,请调整分辨率为16:9的常见分辨率（如1920x1080、1600x900、1366x768等）")
        exit(1)
    return scale_factor

