import psutil


def is_HTGame_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'HTGame.exe':
            print("Info:已检测到异环进程，继续执行脚本")
            return True
    print("Error:未检测到异环进程，请确保游戏已启动")
    exit(1)

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

