"""
进程检测模块 - 检测游戏进程运行状态

提供以下功能：
- 等待游戏进程启动
- 检测进程是否存在
"""

from __future__ import annotations

import time
import logging

from psutil import process_iter
from core.packages.constants import (
    DEFAULT_PROCESS_NAME,
    DEFAULT_PROCESS_TIMEOUT as DEFAULT_TIMEOUT,
    DEFAULT_PROCESS_CHECK_INTERVAL as DEFAULT_CHECK_INTERVAL,
)

logger = logging.getLogger(__name__)

# 默认配置（从 constants 模块导入）
# DEFAULT_PROCESS_NAME, DEFAULT_TIMEOUT, DEFAULT_CHECK_INTERVAL 见上方 import


class ProcessTimeoutError(RuntimeError):
    """进程等待超时异常"""
    pass


def is_process_running(name: str = DEFAULT_PROCESS_NAME) -> bool:
    """
    检测指定进程是否正在运行

    Args:
        name: 进程名

    Returns:
        True-进程正在运行, False-未运行
    """
    for proc in process_iter(['name']):
        if proc.info['name'] == name:
            return True
    return False


def wait_for_game_process(
    name: str = DEFAULT_PROCESS_NAME,
    timeout: float = DEFAULT_TIMEOUT,
    check_interval: float = DEFAULT_CHECK_INTERVAL
) -> None:
    """
    等待游戏进程启动

    循环检测指定进程，直到检测到或超时。

    Args:
        name: 进程名
        timeout: 超时时间（秒），0 表示不超时
        check_interval: 检查间隔（秒）

    Raises:
        ProcessTimeoutError: 超时仍未检测到进程
    """
    start_time = time.time()
    last_warn_time = 0  # 上次打印警告的时间

    while True:
        if is_process_running(name):
            logger.info("已检测到 %s 进程，继续", name)
            return

        elapsed = time.time() - start_time

        if timeout > 0 and elapsed > timeout:
            raise ProcessTimeoutError(
                f"长时间未检测到游戏进程 ({name})，异常退出"
            )

        # 每 10 秒打印一次警告
        current_time = int(elapsed)
        if current_time % 10 == 1 and current_time != last_warn_time:
            last_warn_time = current_time
            logger.warning("未检测到 %s 进程，等待游戏启动 (%ds/%ds)",
                          name, int(elapsed), int(timeout))

        time.sleep(check_interval)
