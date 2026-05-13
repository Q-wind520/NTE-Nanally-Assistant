def test():
        

    from core.packages.tools import wait_1080, get_hwnd, get_window, menu

    # while True:
    #     from pyautogui import position
    #     print(position())

    from pyautogui import center, moveTo
    from core.packages.visual import msslocateOnScreen
    region = msslocateOnScreen('./assets/DZTG_1-1/level.png')
    if region == None: return -1
    print(region)
    moveTo(center(region))


    return 0








if __name__ == '__main__':
    test()
