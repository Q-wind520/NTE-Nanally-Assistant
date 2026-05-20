"""
菜单系统模块 - 脚本注册表与交互式菜单

提供以下功能：
- 脚本信息数据类
- 脚本注册与管理
- 交互式菜单选择
- 用户输入验证
"""

from __future__ import annotations

import time
import logging
import traceback
from dataclasses import dataclass
from typing import Callable, Optional

from core.packages.constants import DEFAULT_VERSION
from core.packages.window import activate_window, WindowNotFoundError

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


def _register_exit_script(exit_func: Callable[[], None]) -> None:
    """注册退出脚本"""
    register_script("0", ScriptInfo(
        name="退出",
        description="退出程序",
        runner=exit_func,
        need_times_param=False
    ))


# ==================== 用户交互 ====================

def get_positive_int(
    prompt: str,
    min_val: int = 1,
    max_val: int = 9999
) -> int:
    """
    获取用户输入的正整数

    Args:
        prompt: 输入提示
        min_val: 最小值
        max_val: 最大值

    Returns:
        有效的正整数
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                print("Error: 输入不能为空")
                continue
            num = int(value)
            if num < min_val:
                print(f"Error: 输入值必须大于等于 {min_val}")
                continue
            if num > max_val:
                print(f"Error: 输入值必须小于等于 {max_val}")
                continue
            return num
        except ValueError:
            print("Error: 请输入有效的整数")


def display_menu(scripts: dict[str, ScriptInfo]) -> None:
    """
    显示菜单

    Args:
        scripts: 脚本字典
    """
    print("\n" + "=" * 40)
    print(f"NTE Nanally Assistant v{DEFAULT_VERSION}")
    print("脚本菜单:")
    print("-" * 40)
    for key, info in scripts.items():
        marker = "  " if key != "0" else "* "
        print(f"{marker}{key}: {info.name:<15} - {info.description}")
    print("=" * 40)


def run_menu(exit_func: Callable[[], None]) -> None:
    """
    运行交互式脚本菜单

    提供脚本选择、参数输入和执行功能。

    Args:
        exit_func: 退出程序时调用的函数
    """
    # 注册内置脚本
    _register_builtin_scripts()
    _register_exit_script(exit_func)

    scripts = _registry.get_all()

    while True:
        try:
            display_menu(scripts)
            choice = input("请输入数字选择脚本: ").strip()

            if choice not in scripts:
                print(f"Error: 无效的选择 '{choice}'，请输入有效的数字")
                continue

            script = scripts[choice]

            # 执行退出
            if choice == "0":
                script.run()
                return

            # 获取执行次数（如果需要）
            times = None
            if script.need_times_param:
                times = get_positive_int("请输入执行次数: ", min_val=1, max_val=9999)

            # 准备执行
            print(f"\n准备执行: {script.name}")
            time.sleep(0.5)

            # 激活窗口（非退出操作）
            try:
                activate_window()
            except WindowNotFoundError as e:
                print(f"Warn: 窗口激活失败，继续执行: {e}")

            # 执行脚本
            if times is not None:
                script.run(times)
            else:
                script.run()

            print(f"\n脚本 '{script.name}' 执行完成\n")

        except KeyboardInterrupt:
            print("\n\n用户取消操作，返回菜单...")
            continue
        except Exception as e:
            print(f"\nError: 执行异常: {e}")
            traceback.print_exc()
            print("\n按回车键继续...")
            input()
