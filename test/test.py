def test():
        


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


    def top_window():
        from win32gui import SetForegroundWindow # type: ignore
        hwnd = get_hwnd_by_process()
        if hwnd:
            SetForegroundWindow(hwnd)
    top_window()
    hwnd = get_hwnd_by_process()
    if hwnd:
        print(f"Found window handle: {hwnd}")


    return 0








if __name__ == '__main__':
    test()
