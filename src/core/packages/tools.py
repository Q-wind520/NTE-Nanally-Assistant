import time


# -----检测游戏是否运行-----
def is_HTGame_running():
    import psutil
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'HTGame.exe':
            print("Info:已检测到异环进程，继续执行脚本")
            return True
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

# -----图像识别坐标-----
def get_button_center_position(image_path):
    """
    传入按钮图片路径
    3次全屏搜索该图片
    返回按钮中心坐标
    """
    from pyautogui import locateOnScreen, center
    for i in range(3):
        template = locateOnScreen(image_path, confidence=0.8)
        if template is not None: return center(template)
        else:
            print(f"Warn:未找到按钮图片: {image_path}，正在重试...({i+1}/3)")
            time.sleep(0.2)
    print(f"Error:未找到按钮图片: {image_path}，请确保分辨率为1920x1080")
    exit(1)

# TODO:兼容分辨率，通过图像缩放



