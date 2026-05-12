def test():
        
    from core.packages.tools import get_hwnd
    from win32gui import EnumWindows


    windows = []
    EnumWindows(get_hwnd, windows)
    return windows[0] if windows else None

    return 0








if __name__ == '__main__':
    test()
