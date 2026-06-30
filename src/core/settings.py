from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".nanally-assistant"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS: dict = {
    "theme_override": None,
    "accent_color": "#6b9fed",
}


def load() -> dict:
    try:
        if CONFIG_FILE.exists():
            raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return {**DEFAULT_SETTINGS, **raw}
    except Exception as exc:
        logger.warning("Failed to load settings: %s", exc)
    return dict(DEFAULT_SETTINGS)


def save(**kwargs) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = load()
        data.update(kwargs)
        CONFIG_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.warning("Failed to save settings: %s", exc)
