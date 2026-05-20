"""
退出模块 - 程序退出与告别信息显示

提供以下功能：
- 显示优雅的退出告别信息
"""

from __future__ import annotations

import sys
import time
import logging
from core.packages.constants import (
    DEFAULT_WIDTH,
    DEFAULT_TITLE,
    DEFAULT_VERSION,
    DEFAULT_AUTHOR,
    DEFAULT_MESSAGE,
    DEFAULT_DELAY,
    DEFAULT_BORDER_CHAR,
    DEFAULT_SIDE_CHAR,
)

logger = logging.getLogger(__name__)

# 常量已迁移至 core.packages.constants，此处通过 import 获取


def _center_text(text: str, total_width: int, fill_char: str = " ") -> str:
    """将文本居中，两侧填充指定字符"""
    if len(text) >= total_width - 2:
        return text[:total_width - 2]
    left_pad = (total_width - len(text) - 2) // 2
    right_pad = total_width - len(text) - 2 - left_pad
    return fill_char * left_pad + text + fill_char * right_pad


def show_farewell(
    width: int = DEFAULT_WIDTH,
    title: str = DEFAULT_TITLE,
    version: str = DEFAULT_VERSION,
    author: str = DEFAULT_AUTHOR,
    message: str = DEFAULT_MESSAGE,
    delay: float = DEFAULT_DELAY,
    border_char: str = DEFAULT_BORDER_CHAR,
    side_char: str = DEFAULT_SIDE_CHAR
) -> None:
    """
    显示优雅的退出告别信息

    Args:
        width: 边框宽度
        title: 程序标题
        version: 版本号
        author: 作者名
        message: 告别语
        delay: 退出前延迟（秒）
        border_char: 边框字符
        side_char: 侧边字符
    """
    # 构建输出行
    border_line = border_char * width
    empty_line = side_char + " " * (width - 2) + side_char

    lines = [
        border_line,
        side_char + _center_text(title, width) + side_char,
        border_line,
        side_char + _center_text(f"version: {version}  by {author}", width) + side_char,
        side_char + _center_text(message, width) + side_char,
        border_line
    ]

    # 输出
    print("\n".join(lines))

    if delay > 0:
        time.sleep(delay)


def exit_program(
    width: int = DEFAULT_WIDTH,
    title: str = DEFAULT_TITLE,
    version: str = DEFAULT_VERSION,
    author: str = DEFAULT_AUTHOR,
    message: str = DEFAULT_MESSAGE,
    delay: float = DEFAULT_DELAY,
    border_char: str = DEFAULT_BORDER_CHAR,
    side_char: str = DEFAULT_SIDE_CHAR
) -> None:
    """
    显示告别信息并退出程序

    Args:
        width: 边框宽度
        title: 程序标题
        version: 版本号
        author: 作者名
        message: 告别语
        delay: 退出前延迟（秒）
        border_char: 边框字符
        side_char: 侧边字符
    """
    show_farewell(
        width=width,
        title=title,
        version=version,
        author=author,
        message=message,
        delay=delay,
        border_char=border_char,
        side_char=side_char
    )
    sys.exit(0)
