"""
The Settings screen: language (English / Русский) and a volume slider for
every sound group (master, player shots, enemy shots, enemy deaths, player
death, mine explosions, footsteps, ambient static).

run(screen, clock, background=None) blocks until Back / Esc and returns
True, or False if the window was closed (callers treat that as "quit").
`background` is a copy of the current frame when this is opened from the
pause overlay, so the game stays visible (dimmed) behind the panel.

Also here: Interface scale (50%-150% of the default HUD size) and Aim
sensitivity (100% = aim snaps to the cursor, lower = smoother turning).

Changes apply instantly and are saved to saves/preferences.json
(sounds.save_levels / i18n.set_language / prefs.save do the saving).
"""

import pygame

import i18n
import prefs
import settings
import sounds


def _font(size, scale):
    return pygame.font.SysFont(None, max(12, round(size * scale)), bold=True)


def _draw_button(screen, rect, label, font, hovered, active=False):
    if active:
        color = settings.SETTINGS_BUTTON_ACTIVE_COLOR
    elif hovered:
        color = settings.SETTINGS_BUTTON_HOVER_COLOR
    else:
        color = settings.SETTINGS_BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, settings.SETTINGS_BUTTON_BORDER_COLOR, rect, 2, border_radius=10)
    text = font.render(label, True, settings.SETTINGS_TEXT_COLOR)
    screen.blit(text, text.get_rect(center=rect.center))


def _controls():
    """Every slider on the screen, in order: (heading, [control, ...]).
    A control is a dict: key, label (i18n key), lo/hi (value range),
    get(), set(value), release() (called when the player lets go)."""
    sound_controls = [
        {
            "key": group, "label": "vol_" + group, "lo": 0.0, "hi": 1.0,
            "get": (lambda g=group: sounds.get_level(g)),
            "set": (lambda v, g=group: sounds.set_level(g, v)),
            "release": (lambda g=group: (sounds.save_levels(), sounds.preview(g))),
        }
        for group in sounds.GROUPS
    ]

    def set_ui_scale(value):
        settings.apply_ui_scale(value)
        prefs.set_number("ui_scale", settings.UI_SCALE / settings.UI_BASE_SCALE)

    def set_aim(value):
        prefs.set_number("aim_sensitivity", value)

    game_controls = [
        {
            "key": "ui_scale", "label": "interface_scale",
            "lo": settings.UI_SCALE_MIN_FACTOR, "hi": settings.UI_SCALE_MAX_FACTOR,
            "get": lambda: settings.UI_SCALE / settings.UI_BASE_SCALE,
            "set": set_ui_scale, "release": prefs.save,
        },
        {
            "key": "aim", "label": "aim_sensitivity",
            "lo": settings.AIM_SENSITIVITY_MIN, "hi": settings.AIM_SENSITIVITY_MAX,
            "get": lambda: prefs.get_number(
                "aim_sensitivity", settings.AIM_SENSITIVITY_MAX,
                settings.AIM_SENSITIVITY_MIN, settings.AIM_SENSITIVITY_MAX,
            ),
            "set": set_aim, "release": prefs.save,
        },
    ]
    return [("sound", sound_controls), ("game", game_controls)]


def _reset_everything():
    sounds.reset_levels()
    settings.apply_ui_scale(1.0)
    prefs.set_number("ui_scale", 1.0)
    prefs.set_number("aim_sensitivity", settings.AIM_SENSITIVITY_MAX)
    prefs.save()


def _needed_height():
    """Unscaled height of everything, used to shrink the screen to fit."""
    row = settings.SETTINGS_ROW_HEIGHT
    rows = sum(len(controls) for _, controls in _controls())
    headings = len(_controls())
    return 80 + row + 14 + headings * 46 + rows * row + 24 + settings.SETTINGS_BUTTON_HEIGHT + 60


def _layout(screen):
    """Every rect on the screen, computed from the window size so it works
    at any resolution. Returned as a dict so drawing and clicking share it."""
    width, height = screen.get_size()
    scale = min(1.0, (height - 30) / _needed_height())
    row_h = round(settings.SETTINGS_ROW_HEIGHT * scale)
    slider_w = round(settings.SETTINGS_SLIDER_WIDTH * scale)
    btn_w = round(settings.SETTINGS_BUTTON_WIDTH * scale)
    btn_h = round(settings.SETTINGS_BUTTON_HEIGHT * scale)
    panel_w = round(settings.SETTINGS_PANEL_WIDTH * scale)

    panel_h = round(_needed_height() * scale)
    panel = pygame.Rect(0, 0, panel_w, panel_h)
    panel.center = (width // 2, height // 2)

    y = panel.top + round(30 * scale)
    title_y = y + round(30 * scale)
    y += round(80 * scale)

    language_y = y + row_h // 2
    lang_rects = []
    gap = round(16 * scale)
    total = len(i18n.LANGUAGES) * btn_w + (len(i18n.LANGUAGES) - 1) * gap
    x = panel.right - round(40 * scale) - total
    for code, _ in i18n.LANGUAGES:
        rect = pygame.Rect(x, 0, btn_w, btn_h)
        rect.centery = language_y
        lang_rects.append((code, rect))
        x += btn_w + gap
    y += row_h + round(14 * scale)

    label_x = panel.left + round(40 * scale)
    slider_left = panel.right - round(40 * scale) - round(70 * scale) - slider_w
    headings = []   # (i18n key, center y)
    sliders = []    # (control, bar rect, hit rect, center y)
    for heading_key, controls in _controls():
        headings.append((heading_key, y + round(23 * scale)))
        y += round(46 * scale)
        for control in controls:
            bar = pygame.Rect(slider_left, 0, slider_w, round(settings.SETTINGS_SLIDER_HEIGHT * scale))
            bar.centery = y + row_h // 2
            # Generous invisible hit area so the thin bar is easy to grab.
            hit = bar.inflate(round(24 * scale), round(row_h * 0.8))
            sliders.append((control, bar, hit, y + row_h // 2))
            y += row_h

    y += round(24 * scale)
    back_rect = pygame.Rect(0, y, btn_w, btn_h)
    back_rect.centerx = panel.centerx + btn_w // 2 + round(10 * scale)
    reset_rect = pygame.Rect(0, y, btn_w, btn_h)
    reset_rect.centerx = panel.centerx - btn_w // 2 - round(10 * scale)

    return {
        "scale": scale, "panel": panel, "title_y": title_y, "language_y": language_y,
        "lang_rects": lang_rects, "headings": headings,
        "label_x": label_x, "sliders": sliders,
        "back": back_rect, "reset": reset_rect, "percent_x": panel.right - round(40 * scale),
    }


def _value_from_mouse(control, bar, mouse_x):
    fraction = max(0.0, min(1.0, (mouse_x - bar.left) / bar.width))
    return control["lo"] + fraction * (control["hi"] - control["lo"])


def run(screen, clock, background=None):
    dragging = None  # the control whose slider is being dragged

    while True:
        layout = _layout(screen)
        scale = layout["scale"]
        title_font = _font(settings.SETTINGS_TITLE_FONT_SIZE, scale)
        section_font = _font(settings.SETTINGS_SECTION_FONT_SIZE, scale)
        text_font = _font(settings.SETTINGS_TEXT_FONT_SIZE, scale)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if layout["back"].collidepoint(event.pos):
                    return True
                if layout["reset"].collidepoint(event.pos):
                    _reset_everything()
                    continue
                for code, rect in layout["lang_rects"]:
                    if rect.collidepoint(event.pos):
                        i18n.set_language(code)
                for control, bar, hit, _ in layout["sliders"]:
                    if hit.collidepoint(event.pos):
                        dragging = control
                        control["set"](_value_from_mouse(control, bar, event.pos[0]))
            elif event.type == pygame.MOUSEMOTION and dragging is not None:
                for control, bar, _, _ in layout["sliders"]:
                    if control is dragging or control["key"] == dragging["key"]:
                        control["set"](_value_from_mouse(control, bar, event.pos[0]))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging is not None:
                dragging["release"]()
                dragging = None

        mouse_pos = pygame.mouse.get_pos()

        # --- draw ---
        if background is not None:
            screen.blit(background, (0, 0))
            dim = pygame.Surface(screen.get_size())
            dim.set_alpha(settings.SETTINGS_BG_OVERLAY_ALPHA)
            screen.blit(dim, (0, 0))
        else:
            screen.fill(settings.MENU_BG_COLOR)

        panel = layout["panel"]
        panel_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, settings.SETTINGS_PANEL_COLOR, panel_surface.get_rect(), border_radius=16)
        screen.blit(panel_surface, panel.topleft)
        pygame.draw.rect(screen, settings.SETTINGS_PANEL_BORDER_COLOR, panel, 2, border_radius=16)

        title = title_font.render(i18n.t("settings_title"), True, settings.SETTINGS_TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(panel.centerx, layout["title_y"])))

        label = section_font.render(i18n.t("language"), True, settings.SETTINGS_TITLE_COLOR)
        screen.blit(label, label.get_rect(midleft=(layout["label_x"], layout["language_y"])))
        for code, rect in layout["lang_rects"]:
            name = dict(i18n.LANGUAGES)[code]
            _draw_button(screen, rect, name, text_font, rect.collidepoint(mouse_pos), active=(code == i18n.get_language()))

        for heading_key, heading_y in layout["headings"]:
            heading = section_font.render(i18n.t(heading_key), True, settings.SETTINGS_TITLE_COLOR)
            screen.blit(heading, heading.get_rect(midleft=(layout["label_x"], heading_y)))

        for control, bar, hit, center_y in layout["sliders"]:
            value = control["get"]()
            fraction = (value - control["lo"]) / (control["hi"] - control["lo"])
            name = text_font.render(i18n.t(control["label"]), True, settings.SETTINGS_TEXT_COLOR)
            screen.blit(name, name.get_rect(midleft=(layout["label_x"], center_y)))

            pygame.draw.rect(screen, settings.SETTINGS_SLIDER_BG_COLOR, bar, border_radius=bar.height // 2)
            fill = pygame.Rect(bar.left, bar.top, round(bar.width * fraction), bar.height)
            if fill.width > 0:
                pygame.draw.rect(screen, settings.SETTINGS_SLIDER_FILL_COLOR, fill, border_radius=bar.height // 2)
            knob_x = bar.left + round(bar.width * fraction)
            knob_hot = (dragging is not None and dragging["key"] == control["key"]) or hit.collidepoint(mouse_pos)
            pygame.draw.circle(
                screen, settings.SETTINGS_SLIDER_KNOB_COLOR, (knob_x, bar.centery),
                round(bar.height * (1.0 if knob_hot else 0.8)) + 2,
            )

            percent = text_font.render(f"{round(value * 100)}%", True, settings.SETTINGS_DIM_TEXT_COLOR)
            screen.blit(percent, percent.get_rect(midright=(layout["percent_x"], center_y)))

        _draw_button(screen, layout["reset"], i18n.t("reset"), text_font, layout["reset"].collidepoint(mouse_pos))
        _draw_button(screen, layout["back"], i18n.t("back"), text_font, layout["back"].collidepoint(mouse_pos))

        pygame.display.flip()
        clock.tick(settings.FPS)
