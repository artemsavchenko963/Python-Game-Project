"""
The Settings screen: language (English / Русский) and a volume slider for
every sound group (master, player shots, enemy shots, enemy deaths, player
death, mine explosions, footsteps, ambient static).

run(screen, clock, background=None) blocks until Back / Esc and returns
True, or False if the window was closed (callers treat that as "quit").
`background` is a copy of the current frame when this is opened from the
pause overlay, so the game stays visible (dimmed) behind the panel.

Changes apply instantly and are saved to saves/preferences.json
(sounds.save_levels / i18n.set_language do the saving).
"""

import pygame

import i18n
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


def _layout(screen):
    """Every rect on the screen, computed from the window size so it works
    at any resolution. Returned as a dict so drawing and clicking share it."""
    width, height = screen.get_size()
    scale = min(1.0, height / 840)
    row_h = round(settings.SETTINGS_ROW_HEIGHT * scale)
    slider_w = round(settings.SETTINGS_SLIDER_WIDTH * scale)
    btn_w = round(settings.SETTINGS_BUTTON_WIDTH * scale)
    btn_h = round(settings.SETTINGS_BUTTON_HEIGHT * scale)
    panel_w = round(settings.SETTINGS_PANEL_WIDTH * scale)

    group_count = len(sounds.GROUPS)
    content_h = (
        round(80 * scale)            # title
        + row_h + round(14 * scale)  # language row
        + round(46 * scale)          # "Sound" heading
        + group_count * row_h
        + round(24 * scale) + btn_h  # buttons
    )
    panel_h = content_h + round(60 * scale)
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

    sound_heading_y = y + round(23 * scale)
    y += round(46 * scale)

    sliders = []
    label_x = panel.left + round(40 * scale)
    slider_left = panel.right - round(40 * scale) - round(70 * scale) - slider_w
    for group in sounds.GROUPS:
        bar = pygame.Rect(slider_left, 0, slider_w, round(settings.SETTINGS_SLIDER_HEIGHT * scale))
        bar.centery = y + row_h // 2
        # Generous invisible hit area so the thin bar is easy to grab.
        hit = bar.inflate(round(24 * scale), round(row_h * 0.8))
        sliders.append((group, bar, hit, y + row_h // 2))
        y += row_h

    y += round(24 * scale)
    back_rect = pygame.Rect(0, y, btn_w, btn_h)
    back_rect.centerx = panel.centerx + btn_w // 2 + round(10 * scale)
    reset_rect = pygame.Rect(0, y, btn_w, btn_h)
    reset_rect.centerx = panel.centerx - btn_w // 2 - round(10 * scale)

    return {
        "scale": scale, "panel": panel, "title_y": title_y, "language_y": language_y,
        "lang_rects": lang_rects, "sound_heading_y": sound_heading_y,
        "label_x": label_x, "sliders": sliders,
        "back": back_rect, "reset": reset_rect, "percent_x": panel.right - round(40 * scale),
    }


def _level_from_mouse(bar, mouse_x):
    return max(0.0, min(1.0, (mouse_x - bar.left) / bar.width))


def run(screen, clock, background=None):
    dragging = None  # the group whose slider is being dragged

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
                    sounds.reset_levels()
                    continue
                for code, rect in layout["lang_rects"]:
                    if rect.collidepoint(event.pos):
                        i18n.set_language(code)
                for group, bar, hit, _ in layout["sliders"]:
                    if hit.collidepoint(event.pos):
                        dragging = group
                        sounds.set_level(group, _level_from_mouse(bar, event.pos[0]))
            elif event.type == pygame.MOUSEMOTION and dragging is not None:
                for group, bar, _, _ in layout["sliders"]:
                    if group == dragging:
                        sounds.set_level(group, _level_from_mouse(bar, event.pos[0]))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging is not None:
                sounds.save_levels()
                sounds.preview(dragging)
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

        heading = section_font.render(i18n.t("sound"), True, settings.SETTINGS_TITLE_COLOR)
        screen.blit(heading, heading.get_rect(midleft=(layout["label_x"], layout["sound_heading_y"])))

        for group, bar, hit, center_y in layout["sliders"]:
            level = sounds.get_level(group)
            name = text_font.render(i18n.t("vol_" + group), True, settings.SETTINGS_TEXT_COLOR)
            screen.blit(name, name.get_rect(midleft=(layout["label_x"], center_y)))

            pygame.draw.rect(screen, settings.SETTINGS_SLIDER_BG_COLOR, bar, border_radius=bar.height // 2)
            fill = pygame.Rect(bar.left, bar.top, round(bar.width * level), bar.height)
            if fill.width > 0:
                pygame.draw.rect(screen, settings.SETTINGS_SLIDER_FILL_COLOR, fill, border_radius=bar.height // 2)
            knob_x = bar.left + round(bar.width * level)
            knob_hot = dragging == group or hit.collidepoint(mouse_pos)
            pygame.draw.circle(
                screen, settings.SETTINGS_SLIDER_KNOB_COLOR, (knob_x, bar.centery),
                round(bar.height * (1.0 if knob_hot else 0.8)) + 2,
            )

            percent = text_font.render(f"{round(level * 100)}%", True, settings.SETTINGS_DIM_TEXT_COLOR)
            screen.blit(percent, percent.get_rect(midright=(layout["percent_x"], center_y)))

        _draw_button(screen, layout["reset"], i18n.t("reset"), text_font, layout["reset"].collidepoint(mouse_pos))
        _draw_button(screen, layout["back"], i18n.t("back"), text_font, layout["back"].collidepoint(mouse_pos))

        pygame.display.flip()
        clock.tick(settings.FPS)
