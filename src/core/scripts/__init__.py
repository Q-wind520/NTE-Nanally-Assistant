"""内置脚本 — 供 TOML runner 通过 `call` 动作调用。"""

from core.scripts import movement, combat, interaction, fishing  # noqa: F401 — 触发 @register
