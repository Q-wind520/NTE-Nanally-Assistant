"""交互类内置脚本。"""

import time

from core.scripts._base import register, BuiltinContext


@register("find_interact")
def find_interact(ctx: BuiltinContext) -> None:
    """查找屏幕上的交互选项并点击。"""
    target = ctx.params.get("image", "interact.png")
    ctx.wait(target, timeout=ctx.params.get("timeout", 5.0))
    ctx.press("f")


@register("skip_cutscene")
def skip_cutscene(ctx: BuiltinContext) -> None:
    """跳过剧情 / 对话。"""
    target = ctx.params.get("image", "skip.png")
    if ctx.wait(target, timeout=1.0):
        ctx.click(target)
        time.sleep(0.3)
    ctx.press("esc")
