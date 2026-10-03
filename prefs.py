"""
Player preferences (language + sound volumes), remembered between runs in
saves/preferences.json next to the game. Everything is wrapped so a missing
or broken file just means "use the defaults" -- it can never crash the game.
"""

import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves", "preferences.json")

data = {}


def load():
    global data
    try:
        with open(_PATH, "r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        data = loaded if isinstance(loaded, dict) else {}
    except (OSError, ValueError):
        data = {}


def save():
    try:
        os.makedirs(os.path.dirname(_PATH), exist_ok=True)
        with open(_PATH, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
    except OSError:
        pass


def get_number(key, default, low, high):
    """A saved numeric preference, clamped to [low, high]."""
    value = data.get(key, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        value = default
    return max(low, min(high, float(value)))


def set_number(key, value):
    data[key] = round(float(value), 3)
