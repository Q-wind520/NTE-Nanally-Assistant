"""
全局常量配置

所有可配置的常量集中在此模块，方便统一管理和修改。
"""

import sys
import tomllib
from pathlib import Path


def get_asset_path(*parts: str) -> Path:
    """获取资源路径，兼容 PyInstaller 打包和开发环境。"""
    base = Path(getattr(sys, '_MEIPASS', '.')) if getattr(sys, 'frozen', False) else Path.cwd()
    return base.joinpath(*parts)


def get_version() -> str:
    """从 pyproject.toml 读取版本号。"""
    toml_path = get_asset_path('pyproject.toml')
    with open(toml_path, 'rb') as f:
        data = tomllib.load(f)
    return data['project']['version']

# ==================== 进程检测 ====================
DEFAULT_PROCESS_NAME = "HTGame.exe"
DEFAULT_PROCESS_TIMEOUT = 300        # 等待进程启动超时（秒）
DEFAULT_PROCESS_CHECK_INTERVAL = 2   # 进程检查间隔（秒）

# ==================== 窗口管理 ====================
WINDOW_BORDER_LEFT = 8
WINDOW_BORDER_RIGHT = 8
WINDOW_BORDER_TOP = 30
WINDOW_BORDER_BOTTOM = 9

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
DEFAULT_TITLE = "NTE Nanally Assistant"
DEFAULT_AUTHOR = "Q-wind520"
GITHUB_AUTHOR_URL = "https://github.com/Q-wind520"
GITHUB_REPO_URL = "https://github.com/Q-wind520/NTE-Nanally-Assistant"
GITHUB_ISSUES_URL = "https://github.com/Q-wind520/NTE-Nanally-Assistant/issues"
