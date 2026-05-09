import time


# -----检测游戏是否运行-----
def is_HTGame_running():
    import psutil
    while True:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'HTGame.exe':
                print("Info:已检测到异环进程，继续执行脚本")
        print("Warn:未检测到异环进程，请确保游戏已启动")

# -----菜单选择-----
def menu():
    scripts = {
            _1: "1.xxxx_1-1" 
            _2: "2.xxxx_tuiguanqia" 
            _0: "0.editting..."
            }
    while True:
        try:
            print("请选择要执行的脚本:")
            print(scripts)
            choice = input("请输入数字选择脚本: ")     
            if choice == '1':
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
        scale_factor = x / 1920 if x < 1920 else 1920 / x
    else:
        print("Error:当前分辨率非16:9，坐标不适配,请调整分辨率为16:9")
        exit(1)
    return scale_factor

