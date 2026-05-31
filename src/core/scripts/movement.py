"""移动类内置脚本。"""

from core.scripts._base import register, BuiltinContext


@register("map_teleport")
def map_teleport(ctx: BuiltinContext) -> None:
    """打开地图并传送到指定位置。"""
    ctx.press("m")
    # TODO: 实现地图选择和传送逻辑


@register("dash")
def dash(ctx: BuiltinContext) -> None:
    """闪避/冲刺。"""
    count = ctx.params.get("count", 1)
    for _ in range(count):
        ctx.press("shift")
