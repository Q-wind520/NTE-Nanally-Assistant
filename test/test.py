def test():
        

    from core.packages.tools import get_hwnd, get_window

    hwnd = get_hwnd()
    print(f"窗口信息:{get_window(hwnd)}")

    window_info = get_window(get_hwnd())
    if window_info is None:
        print("Warn: 无法获取窗口信息")
        return -1
    if window_info['height'] == 1080:
        print("是1080窗口")
    else:
        print("不是1080窗口")















    return 0








if __name__ == '__main__':
    test()
