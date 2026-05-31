"""战斗类内置脚本。"""

import time

from core.scripts._base import register, BuiltinContext


@register("support_skill")
def support_skill(ctx: BuiltinContext) -> None:
    """援护技。"""
    ctx.press("1")


@register("parry")
def parry(ctx: BuiltinContext) -> None:
    """弹刀 / 极限闪避后的反击。"""
    ctx.press("j")


@register("skill_short_e")
def skill_short_e(ctx: BuiltinContext) -> None:
    """短按 E 技能。"""
    ctx.press("e")


@register("skill_long_e")
def skill_long_e(ctx: BuiltinContext) -> None:
    """长按 E 技能。"""
    import pydirectinput as pdi
    pdi.keyDown("e")
    hold = ctx.params.get("hold", 2.0)
    time.sleep(hold)
    pdi.keyUp("e")


@register("skill_q")
def skill_q(ctx: BuiltinContext) -> None:
    """Q 大招 / 终结技。"""
    ctx.press("q")
