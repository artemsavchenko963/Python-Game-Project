"""
English / Russian text. Every player-facing string lives in STRINGS below,
looked up with i18n.t("key") at draw time -- so switching the language in
Settings changes the whole game instantly, no restart.

    i18n.t("towers", remaining=3, total=10)   # -> "Towers: 3/10" / "Башни: 3/10"
    i18n.lines("instr_lines")                 # a list of lines (blank = spacer)
    i18n.set_language("ru")

A missing key falls back to English, then to the key itself, so a typo
shows up on screen instead of crashing.
"""

import prefs

LANGUAGES = [("en", "English"), ("ru", "Русский")]
DEFAULT_LANGUAGE = "en"

_current = DEFAULT_LANGUAGE

STRINGS = {
    "en": {
        # menus
        "menu_title": "Dark Rooms",
        "diff_Easy": "Easy", "diff_Mid": "Mid", "diff_Hard": "Hard", "diff_Impossible": "Impossible",
        "settings": "Settings",
        "back": "Back",
        "instr_title": "How to Survive",
        "instr_lines": [
            "The whole map outside the castle is full of hidden mines.",
            "Mines are invisible until you scan for them -- press E to pulse-scan",
            "the area around you; any mines caught in that pulse light up for a",
            "few seconds, then fade back to invisible (they're still there, and",
            "still lethal, the whole time -- only the drawing is affected).",
            "Scanning has a short cooldown before you can scan again.",
            "",
            "Walking into a mine -- revealed or not -- damages you and destroys it.",
            "Press F near a mine you've just revealed to defuse it safely instead.",
            "",
            "WASD / arrow keys to move, mouse to aim, left click to fire.",
            "Clear every enemy base to win. Good luck.",
        ],
        "instr_hint": "Press any key or click to continue",
        "backstory_title": "THE RIFT OPENS",
        "backstory_lines": [
            "With the last base silenced, the castle floor splits open beneath",
            "the throne room -- whatever ruled this place was never IN these walls.",
            "",
            "It waited below, coiled in a scorched, blood-red arena, for someone",
            "strong enough to actually reach it.",
            "",
            "There are no mines past this point. No shadows left to hide in.",
            "Just you, and whatever is still alive down there.",
            "",
            "Once you step through, it doesn't end until one of you does.",
        ],
        "backstory_hint": "Press any key or click to enter the arena",
        # settings screen
        "settings_title": "Settings",
        "language": "Language",
        "sound": "Sound",
        "vol_master": "Master volume",
        "vol_player_shot": "Player shots",
        "vol_enemy_shot": "Enemy shots",
        "vol_enemy_death": "Enemy deaths",
        "vol_player_death": "Player death",
        "vol_mine": "Mine explosions",
        "vol_move": "Footsteps",
        "vol_ambient": "Ambient static",
        "game": "Game",
        "interface_scale": "Interface scale",
        "aim_sensitivity": "Aim sensitivity",
        "reset": "Reset",
        # HUD
        "level_short": "LV.",
        "max": "MAX",
        "towers": "Towers: {remaining}/{total}",
        "scanner_ready": "Scanner: Ready (E)   Defuse (F)",
        "scanner_cooldown": "Scanner: {seconds}s   Defuse (F)",
        "hp": "HP",
        "boss_prompt": "Press E: Boss Fight",
        "tower_intro": "Destroy all {count} towers",
        "boss_label": "BOSS",
        "boss_rage": "ENRAGED",
        "shop_title": "SHOP",
        "shop_owned": "Owned",
        "shop_speed": "+30% Speed",
        "shop_damage": "+50% Damage",
        "shop_health": "+40% Max HP",
        "shop_relic": "??? Relic",
        "stats_title": "PLAYER STATS",
        "stat_level": "Level",
        "stat_health": "Health",
        "stat_damage": "Damage",
        "stat_attack_speed": "Attack speed",
        "stat_move_speed": "Move speed",
        "stat_souls": "Souls",
        "per_second": "/s",
        "game_over_title": "YOU DIED",
        "game_over_hint": "Press R to restart",
        "victory_title": "VICTORY",
        "victory_hint": "All bases cleared -- press R to play again",
        "paused": "PAUSED",
        "continue": "Continue",
        "leave": "Leave",
    },
    "ru": {
        "menu_title": "Dark Rooms",
        "diff_Easy": "Легко", "diff_Mid": "Средне", "diff_Hard": "Сложно", "diff_Impossible": "Невозможно",
        "settings": "Настройки",
        "back": "Назад",
        "instr_title": "Как выжить",
        "instr_lines": [
            "Вся карта за пределами замка усыпана скрытыми минами.",
            "Мины невидимы, пока вы их не просканируете -- нажмите E для импульса:",
            "все мины в радиусе импульса подсветятся на несколько секунд,",
            "а потом снова исчезнут (но останутся на месте и по-прежнему",
            "смертельны -- меняется только отображение).",
            "У сканирования есть короткая перезарядка.",
            "",
            "Наступив на мину -- видимую или нет -- вы получите урон, и она взорвётся.",
            "Нажмите F рядом с только что подсвеченной миной, чтобы безопасно её обезвредить.",
            "",
            "WASD / стрелки -- движение, мышь -- прицел, левая кнопка -- огонь.",
            "Уничтожьте все вражеские базы, чтобы победить. Удачи.",
        ],
        "instr_hint": "Нажмите любую клавишу или кликните, чтобы продолжить",
        "backstory_title": "РАЗЛОМ ОТКРЫВАЕТСЯ",
        "backstory_lines": [
            "Когда последняя база затихла, пол замка раскололся под тронным залом --",
            "то, что правило этим местом, никогда не жило В этих стенах.",
            "",
            "Оно ждало внизу, свернувшись на раскалённой кроваво-красной арене,",
            "того, кто достаточно силён, чтобы добраться до него.",
            "",
            "За этой чертой нет мин. Не осталось теней, чтобы спрятаться.",
            "Только вы и всё, что ещё живо там, внизу.",
            "",
            "Стоит шагнуть вперёд -- и это не кончится, пока не падёт один из вас.",
        ],
        "backstory_hint": "Нажмите любую клавишу или кликните, чтобы войти на арену",
        "settings_title": "Настройки",
        "language": "Язык",
        "sound": "Звук",
        "vol_master": "Общая громкость",
        "vol_player_shot": "Выстрелы игрока",
        "vol_enemy_shot": "Выстрелы врагов",
        "vol_enemy_death": "Смерть врагов",
        "vol_player_death": "Смерть игрока",
        "vol_mine": "Взрывы мин",
        "vol_move": "Шаги",
        "vol_ambient": "Фоновый шум",
        "game": "Игра",
        "interface_scale": "Масштаб интерфейса",
        "aim_sensitivity": "Чувствительность прицела",
        "reset": "Сброс",
        "level_short": "УР.",
        "max": "МАКС",
        "towers": "Башни: {remaining}/{total}",
        "scanner_ready": "Сканер: готов (E)   Обезвр. (F)",
        "scanner_cooldown": "Сканер: {seconds}с   Обезвр. (F)",
        "hp": "ЗДР",
        "boss_prompt": "Нажми E: бой с боссом",
        "tower_intro": "Уничтожьте башни: {count}",
        "boss_label": "БОСС",
        "boss_rage": "В ЯРОСТИ",
        "shop_title": "МАГАЗИН",
        "shop_owned": "Куплено",
        "shop_speed": "+30% скорости",
        "shop_damage": "+50% урона",
        "shop_health": "+40% макс. ЗДР",
        "shop_relic": "??? Реликвия",
        "stats_title": "ХАРАКТЕРИСТИКИ",
        "stat_level": "Уровень",
        "stat_health": "Здоровье",
        "stat_damage": "Урон",
        "stat_attack_speed": "Скор. атаки",
        "stat_move_speed": "Скорость",
        "stat_souls": "Души",
        "per_second": "/с",
        "game_over_title": "ВЫ ПОГИБЛИ",
        "game_over_hint": "Нажмите R, чтобы начать заново",
        "victory_title": "ПОБЕДА",
        "victory_hint": "Все базы уничтожены -- нажмите R, чтобы сыграть снова",
        "paused": "ПАУЗА",
        "continue": "Продолжить",
        "leave": "Выйти",
    },
}


def load():
    """Read the saved language (call once at startup, after prefs.load())."""
    code = prefs.data.get("language", DEFAULT_LANGUAGE)
    set_language(code, save=False)


def get_language():
    return _current


def set_language(code, save=True):
    global _current
    if code not in STRINGS:
        code = DEFAULT_LANGUAGE
    _current = code
    if save:
        prefs.data["language"] = code
        prefs.save()


def _lookup(key):
    value = STRINGS[_current].get(key)
    if value is None:
        value = STRINGS[DEFAULT_LANGUAGE].get(key, key)
    return value


def t(key, **values):
    text = _lookup(key)
    return text.format(**values) if values else text


def lines(key):
    return list(_lookup(key))
