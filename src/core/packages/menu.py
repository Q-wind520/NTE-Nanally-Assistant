"""
脚本注册表模块

提供以下功能：
- 脚本信息数据类
- 脚本注册与管理
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Optional

logger = logging.getLogger(__name__)


# ==================== 数据类 ====================

@dataclass
class ScriptInfo:
    """
    脚本信息

    Attributes:
        name: 脚本名称
        description: 脚本描述
        runner: 脚本执行函数
        need_times_param: 是否需要执行次数参数
    """
    name: str
    description: str
    runner: Callable[..., None]
    need_times_param: bool = False

    def run(self, times: Optional[int] = None) -> None:
        """
        执行脚本

        Args:
            times: 执行次数（当 need_times_param=True 时必须提供）

        Raises:
            ValueError: 需要次数参数但未提供或参数无效
        """
        if self.need_times_param:
            if times is None or times <= 0:
                raise ValueError("执行次数必须为正整数")
            self.runner(times)
        else:
            self.runner()


# ==================== 脚本注册表 ====================

class ScriptRegistry:
    """
    脚本注册表

    管理所有可用脚本的注册和查找。
    """

    def __init__(self) -> None:
        self._scripts: dict[str, ScriptInfo] = {}

    def register(self, key: str, script: ScriptInfo) -> None:
        """
        注册脚本

        Args:
            key: 脚本键值
            script: 脚本信息
        """
        self._scripts[key] = script

    def unregister(self, key: str) -> None:
        """注销脚本"""
        self._scripts.pop(key, None)

    def get(self, key: str) -> Optional[ScriptInfo]:
        """获取脚本"""
        return self._scripts.get(key)

    def get_all(self) -> dict[str, ScriptInfo]:
        """获取所有脚本"""
        return dict(self._scripts)

    def has_key(self, key: str) -> bool:
        """检查键是否存在"""
        return key in self._scripts


# 全局脚本注册表实例
_registry = ScriptRegistry()


def get_registry() -> ScriptRegistry:
    """获取全局脚本注册表"""
    return _registry


def register_script(key: str, script: ScriptInfo) -> None:
    """注册脚本到全局注册表"""
    _registry.register(key, script)


# ==================== 内置脚本注册 ====================

def _register_builtin_scripts() -> None:
    """注册内置脚本（延迟导入避免循环依赖）"""
    from core.scripts.DianZhangTeGong._1_1 import script_DianZhangTeGong_1_1
    from core.scripts.DianZhangTeGong._TuiGuanQia import script_DianZhangTeGong_TuiGuanQia

    register_script("1", ScriptInfo(
        name="店长特供_1-1",
        description="执行店长特供1-1关卡脚本",
        runner=script_DianZhangTeGong_1_1,
        need_times_param=True
    ))

    register_script("2", ScriptInfo(
        name="店长特供_推关卡",
        description="使用娜娜莉和白藏的都市特技无脑推关卡",
        runner=script_DianZhangTeGong_TuiGuanQia,
        need_times_param=True
    ))


