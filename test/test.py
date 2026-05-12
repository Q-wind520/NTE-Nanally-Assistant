def test():
        

    from core.packages.tools import get_hwnd, get_window

    hwnd = get_hwnd()
    print(f"窗口信息:{get_window(hwnd)}")


















    return 0








if __name__ == '__main__':
    test()
