"""
Sound effects + ambience (pygame.mixer). Everything loads once in init();
every function is a safe no-op if audio isn't available, so a missing
sound device or file never crashes the game.

    sounds.init()                                  # once at startup
    sounds.start_ambient()                         # looping static, quiet
    sounds.play("attack3", 0.3, "enemy_shot")      # one-shot: base volume, group
    sounds.play_player_shot(0.5)                   # random attack1/attack2
    sounds.set_moving(True/False)                  # footsteps loop, every frame

Volume = base volume (settings.SOUND_VOLUME_*) x the group's slider x the
master slider. The sliders (0.0-1.0, default 1.0) are edited in the Settings
screen and remembered in saves/preferences.json via prefs.py.
"""

import random
import time

import pygame

import prefs
import settings

# Slider order in the Settings screen. "master" scales everything.
GROUPS = [
    "master", "player_shot", "enemy_shot", "enemy_death",
    "player_death", "mine", "move", "ambient",
]

_sounds = {}
_last_played = {}
_levels = {group: 1.0 for group in GROUPS}
_move_channel = None
_ambient_channel = None
_moving = False
_ready = False
_last_player_shot = None


def init():
    global _ready, _move_channel, _ambient_channel
    saved = prefs.data.get("volumes", {})
    for group in GROUPS:
        value = saved.get(group, 1.0)
        if isinstance(value, (int, float)):
            _levels[group] = max(0.0, min(1.0, float(value)))
    try:
        pygame.mixer.init()
        pygame.mixer.set_num_channels(24)
    except pygame.error:
        return
    for name, filename in settings.SOUND_FILES.items():
        try:
            _sounds[name] = pygame.mixer.Sound(settings.SOUND_DIR + filename)
        except (pygame.error, FileNotFoundError):
            pass
    # Two channels reserved for the loops so one-shots never steal them.
    pygame.mixer.set_reserved(2)
    _move_channel = pygame.mixer.Channel(0)
    _ambient_channel = pygame.mixer.Channel(1)
    _ready = True


# --- slider levels (used by the Settings screen) ---

def get_level(group):
    return _levels.get(group, 1.0)


def set_level(group, value):
    """Change a slider (0.0-1.0). Loops update immediately; call save_levels()
    when the player lets go of the slider."""
    _levels[group] = max(0.0, min(1.0, value))
    _refresh_loops()


def reset_levels():
    for group in GROUPS:
        _levels[group] = 1.0
    _refresh_loops()
    save_levels()


def save_levels():
    prefs.data["volumes"] = {group: round(_levels[group], 3) for group in GROUPS}
    prefs.save()


def _volume(base, group):
    return min(1.0, base * _levels[group] * _levels["master"] * settings.SOUND_MASTER_VOLUME)


def _refresh_loops():
    if not _ready:
        return
    _move_channel.set_volume(_volume(settings.SOUND_VOLUME_MOVE, "move"))
    _ambient_channel.set_volume(_volume(settings.SOUND_VOLUME_AMBIENT, "ambient"))


# --- playing ---

def play(name, base_volume=1.0, group="master", max_ms=0):
    if not _ready or name not in _sounds:
        return
    now = time.monotonic()
    if now - _last_played.get(name, 0.0) < settings.SOUND_MIN_REPEAT_SECONDS:
        return
    _last_played[name] = now
    channel = _sounds[name].play(maxtime=max_ms)
    if channel is not None:
        channel.set_volume(_volume(base_volume, group))


def play_player_shot(base_volume=1.0, max_ms=0):
    """Random pick from settings.PLAYER_SHOT_SOUNDS, never the same one
    twice in a row, so firing doesn't sound like a machine."""
    global _last_player_shot
    options = [n for n in settings.PLAYER_SHOT_SOUNDS if n in _sounds]
    if len(options) > 1 and _last_player_shot in options:
        options.remove(_last_player_shot)
    if not options:
        return
    _last_player_shot = random.choice(options)
    play(_last_player_shot, base_volume, "player_shot", max_ms)


def preview(group):
    """A short sample so the player can hear a slider's level when they
    let go of it in the Settings screen."""
    _last_played.clear()
    if group == "player_shot":
        play_player_shot(settings.SOUND_VOLUME_PLAYER_SHOT)
    elif group == "enemy_shot":
        play("attack3", settings.SOUND_VOLUME_ENEMY_SHOT, "enemy_shot")
    elif group == "enemy_death":
        play("death", settings.SOUND_VOLUME_ENEMY_DEATH, "enemy_death")
    elif group == "player_death":
        play("death", settings.SOUND_VOLUME_PLAYER_DEATH, "player_death")
    elif group == "mine":
        play("mine", settings.SOUND_VOLUME_MINE, "mine")
    elif group == "move":
        play("move", settings.SOUND_VOLUME_MOVE, "move", max_ms=900)
    elif group == "ambient":
        play("whitenoise", settings.SOUND_VOLUME_AMBIENT, "ambient", max_ms=900)
    else:  # master: a shot is the most recognisable sound
        play_player_shot(settings.SOUND_VOLUME_PLAYER_SHOT)


# --- loops ---

def start_ambient():
    if not _ready or "whitenoise" not in _sounds:
        return
    _refresh_loops()
    if not _ambient_channel.get_busy():
        _ambient_channel.play(_sounds["whitenoise"], loops=-1)


def set_moving(is_moving):
    """Footsteps loop plays only while True. Safe to call every frame."""
    global _moving
    if not _ready or "move" not in _sounds or is_moving == _moving:
        return
    _moving = is_moving
    if is_moving:
        _refresh_loops()
        _move_channel.play(_sounds["move"], loops=-1, fade_ms=settings.SOUND_MOVE_FADE_MS)
    else:
        _move_channel.fadeout(settings.SOUND_MOVE_FADE_MS)
