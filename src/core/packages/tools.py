"""
工具模块 - 兼容层（向后兼容）

此模块保留所有原始函数名以确保向后兼容性。
新代码应直接导入各子模块：
  - core.packages.process: 进程检测
  - core.packages.window: 窗口管理
  - core.packages.menu: 菜单系统
  - core.packages.exit: 退出程序
"""

from __future__ import annotations

import warnings
from typing import Callable, Optional

# ==================== 进程检测（来自 process.py） ====================

from core.packages.process import (
    is_process_running,
    wait_for_game_process,
    ProcessTimeoutError,
)

# 向后兼容别名
is_HTGame_running = wait_for_game_process


# ==================== 窗口管理（来自 window.py） ====================

from core.packages.window import (
    WindowInfo,
    get_hwnd,
    get_window,
    activate_window,
    wait_for_1080p_resolution,
    WindowNotFoundError,
    WindowInvalidError,
    WindowResolutionTimeoutError,
)

# 向后兼容别名
active_window = activate_window
wait_1080 = wait_for_1080p_resolution


# ==================== 菜单系统（来自 menu.py） ====================

from core.packages.menu import (
    ScriptInfo,
    ScriptRegistry,
    get_registry,
    register_script,
    get_positive_int,
    display_menu,
    run_menu,
)

# 向后兼容别名
menu = run_menu


# ==================== 退出程序（来自 exit.py） ====================

from core.packages.exit import (
    show_farewell,
    exit_program,
)

# 向后兼容别名
exitNA = exit_program


# ==================== 窗口边框常量（来自 window.py） ====================

from core.packages.window import (
    WINDOW_BORDER_LEFT,
    WINDOW_BORDER_RIGHT,
    WINDOW_BORDER_TOP,
    WINDOW_BORDER_BOTTOM,
    TARGET_ASPECT_RATIO,
    TARGET_HEIGHT,
)


# ==================== 废弃警告 ====================

def __getattr__(name: str):
    """对已移除的旧名称给出废弃警告"""
    _deprecated_names = {
        "_get_scripts": "请使用 core.packages.menu.ScriptRegistry",
    }
    if name in _deprecated_names:
        warnings.warn(
            f"'{name}' 已废弃，{_deprecated_names[name]}",
            DeprecationWarning,
            stacklevel=2
        )
    raise AttributeError(f"module 'core.packages.tools' has no attribute '{name}'")
