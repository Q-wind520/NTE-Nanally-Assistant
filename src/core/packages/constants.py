"""
全局常量配置

所有可配置的常量集中在此模块，方便统一管理和修改。
"""

# ==================== 进程检测 ====================
DEFAULT_PROCESS_NAME = "HTGame.exe"
DEFAULT_PROCESS_TIMEOUT = 300        # 等待进程启动超时（秒）
DEFAULT_PROCESS_CHECK_INTERVAL = 2   # 进程检查间隔（秒）

# ==================== 窗口管理 ====================
WINDOW_BORDER_LEFT = 9
WINDOW_BORDER_RIGHT = 9
WINDOW_BORDER_TOP = 37
WINDOW_BORDER_BOTTOM = 10

TARGET_ASPECT_RATIO = 16.0 / 9.0    # 16:9 宽高比
TARGET_HEIGHT = 720
ASPECT_RATIO_TOLERANCE = 0.05        # 宽高比容差

# ==================== 视觉识别 ====================
DEFAULT_CONFIDENCE = 0.8             # 默认模板匹配置信度
DEFAULT_TIMEOUT = 10.0               # 默认查找超时（秒）
DEFAULT_INTERVAL = 0.5               # 默认查找检查间隔（秒）
DEFAULT_SCREEN_INDEX = 0             # MSS 屏幕索引
DEFAULT_CLICK_OFFSET = (0, 0)        # 点击偏移量

# ==================== 退出/UI ====================
DEFAULT_WIDTH = 75
DEFAULT_TITLE = "NTE Nanally Assistant"
DEFAULT_VERSION = "0.4.0"
DEFAULT_AUTHOR = "Q-wind520"
DEFAULT_MESSAGE = "See You Next Time!"
DEFAULT_DELAY = 1.0
DEFAULT_BORDER_CHAR = "="
DEFAULT_SIDE_CHAR = "|"
