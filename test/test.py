
# 寻找模板在屏幕上的位置，返回中心坐标
"""
def find_template_on_screen(template_path, confidence=0.8):
    # 截取屏幕
    screen = pyautogui.screenshot()
    screen_np = np.array(screen)
    screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
    
    # 读取模板
    template = cv2.imread(template_path, 0)
    w, h = template.shape[::-1]
    
    # 模板匹配
    res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    if max_val >= confidence:
        # 返回中心点坐标
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return center_x, center_y, max_val
    return None
"""

import pyautogui
from ..src.core.packages.tools import get_button_center_position

print(get_button_center_position('../assets/DZTG_1-1/level.png'))
