"""
Step 36: a difficulty-select menu shown once, at startup, before the map
even loads -- a black screen with a title and one button per entry in
settings.DIFFICULTIES (Easy/Mid/Hard/Impossible, in that order). Runs
its own tiny event loop, separate from the main game loop in main.py,
since nothing about the game itself exists yet at this point (no Room,
no Player -- picking a difficulty is what tells create_game_state() what
numbers to build the map's mines/enemies with).

run() blocks until the player clicks a button, then returns that
difficulty's NAME (a key into settings.DIFFICULTIES) -- main() looks
that name up to get the actual {"mines": ..., "castle_enemies": ...,
"map_enemies": ...} numbers. Closing the window here (the X button)
returns None instead, which main() treats as "quit immediately," the
same as closing it mid-game would.
"""

import pygame

import i18n
import settings
import settings_menu


SETTINGS_BUTTON = "__settings__"


def _button_rects(screen):
    """One (name, rect) pair per difficulty, stacked vertically and
    centered on screen, in settings.DIFFICULTIES' own order (a plain
    dict preserves insertion order in Python, so this always comes out
    Easy -> Mid -> Hard -> Impossible)."""
    # The last entry is the Settings button (not a difficulty).
    names = list(settings.DIFFICULTIES.keys()) + [SETTINGS_BUTTON]
    button_height = settings.MENU_BUTTON_HEIGHT
    gap = settings.MENU_BUTTON_GAP
    total_height = len(names) * button_height + (len(names) - 1) * gap
    start_y = screen.get_height() // 2 - total_height // 2
    center_x = screen.get_width() // 2

    rects = []
    y = start_y
    for name in names:
        rect = pygame.Rect(0, 0, settings.MENU_BUTTON_WIDTH, button_height)
        rect.center = (center_x, y + button_height // 2)
        rects.append((name, rect))
        y += button_height + gap
    return rects


def run(screen, clock):
    """Blocks until a difficulty button is clicked. Returns the chosen
    difficulty's name, or None if the window was closed instead."""
    title_font = pygame.font.SysFont(None, settings.MENU_TITLE_FONT_SIZE)
    button_font = pygame.font.SysFont(None, settings.MENU_BUTTON_FONT_SIZE)

    buttons = _button_rects(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in buttons:
                    if rect.collidepoint(event.pos):
                        if name == SETTINGS_BUTTON:
                            if not settings_menu.run(screen, clock):
                                return None
                        else:
                            return name

        mouse_pos = pygame.mouse.get_pos()

        # Text is rendered every frame (cheap) so a language change made in
        # Settings shows up the moment you come back.
        screen.fill(settings.MENU_BG_COLOR)
        title_surface = title_font.render(i18n.t("menu_title"), True, settings.MENU_TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(screen.get_width() // 2, buttons[0][1].top - 90))
        screen.blit(title_surface, title_rect)

        for name, rect in buttons:
            is_hovered = rect.collidepoint(mouse_pos)
            color = settings.MENU_BUTTON_HOVER_COLOR if is_hovered else settings.MENU_BUTTON_COLOR
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, settings.MENU_BUTTON_BORDER_COLOR, rect, 2)

            label = i18n.t("settings") if name == SETTINGS_BUTTON else i18n.t("diff_" + name)
            text_surface = button_font.render(label, True, settings.MENU_BUTTON_TEXT_COLOR)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(settings.FPS)


def run_instructions(screen, clock):
    """Step 37: a black instructions screen shown once, right after the
    difficulty menu, explaining the minefield mechanic and basic controls.
    Blocks until any key is pressed or the mouse is clicked, then returns
    True. Returns False if the window was closed instead, which main()
    treats the same as closing the difficulty menu -- quit immediately."""
    title_font = pygame.font.SysFont(None, settings.INSTRUCTIONS_TITLE_FONT_SIZE)
    line_font = pygame.font.SysFont(None, settings.INSTRUCTIONS_LINE_FONT_SIZE)
    hint_font = pygame.font.SysFont(None, settings.INSTRUCTIONS_HINT_FONT_SIZE)

    title_surface = title_font.render(
        i18n.t("instr_title"), True, settings.INSTRUCTIONS_TITLE_COLOR
    )

    line_surfaces = [
        line_font.render(line, True, settings.INSTRUCTIONS_LINE_COLOR) if line else None
        for line in i18n.lines("instr_lines")
    ]
    # Blank lines (empty strings) render as None -- treated as a spacer
    # the height of a normal line, so paragraph breaks still take up room.
    line_height = line_font.get_height()

    hint_surface = hint_font.render(
        i18n.t("instr_hint"), True, settings.INSTRUCTIONS_HINT_COLOR
    )

    center_x = screen.get_width() // 2
    total_lines_height = len(line_surfaces) * line_height + (len(line_surfaces) - 1) * settings.INSTRUCTIONS_LINE_GAP
    lines_start_y = screen.get_height() // 2 - total_lines_height // 2
    title_rect = title_surface.get_rect(center=(center_x, lines_start_y - 80))
    hint_rect = hint_surface.get_rect(
        center=(center_x, screen.get_height() - settings.INSTRUCTIONS_HINT_MARGIN)
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return True

        screen.fill(settings.MENU_BG_COLOR)
        screen.blit(title_surface, title_rect)

        y = lines_start_y
        for line_surface in line_surfaces:
            if line_surface is not None:
                line_rect = line_surface.get_rect(center=(center_x, y + line_height // 2))
                screen.blit(line_surface, line_rect)
            y += line_height + settings.INSTRUCTIONS_LINE_GAP

        screen.blit(hint_surface, hint_rect)

        pygame.display.flip()
        clock.tick(settings.FPS)


def run_arena_backstory(screen, clock):
    """Step 48: a black backstory screen shown once, after the player
    presses E on the "Press E: Boss Fight" prompt and before main.py
    actually switches the map over to arena.tmx. Identical
    blocks-until-any-key/click pattern as run_instructions above, just
    with its own title/lines/hint text (settings.ARENA_BACKSTORY_*) so
    tweaking one screen's wording/timing never touches the other's.
    Returns True once dismissed, or False if the window was closed
    instead -- main() treats that the same as closing the window
    anywhere else mid-game (stop running)."""
    title_font = pygame.font.SysFont(None, settings.ARENA_BACKSTORY_TITLE_FONT_SIZE)
    line_font = pygame.font.SysFont(None, settings.ARENA_BACKSTORY_LINE_FONT_SIZE)
    hint_font = pygame.font.SysFont(None, settings.ARENA_BACKSTORY_HINT_FONT_SIZE)

    title_surface = title_font.render(
        i18n.t("backstory_title"), True, settings.ARENA_BACKSTORY_TITLE_COLOR
    )

    line_surfaces = [
        line_font.render(line, True, settings.ARENA_BACKSTORY_LINE_COLOR) if line else None
        for line in i18n.lines("backstory_lines")
    ]
    line_height = line_font.get_height()

    hint_surface = hint_font.render(
        i18n.t("backstory_hint"), True, settings.ARENA_BACKSTORY_HINT_COLOR
    )

    center_x = screen.get_width() // 2
    total_lines_height = len(line_surfaces) * line_height + (len(line_surfaces) - 1) * settings.ARENA_BACKSTORY_LINE_GAP
    lines_start_y = screen.get_height() // 2 - total_lines_height // 2
    title_rect = title_surface.get_rect(center=(center_x, lines_start_y - 80))
    hint_rect = hint_surface.get_rect(
        center=(center_x, screen.get_height() - settings.ARENA_BACKSTORY_HINT_MARGIN)
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return True

        screen.fill(settings.MENU_BG_COLOR)
        screen.blit(title_surface, title_rect)

        y = lines_start_y
        for line_surface in line_surfaces:
            if line_surface is not None:
                line_rect = line_surface.get_rect(center=(center_x, y + line_height // 2))
                screen.blit(line_surface, line_rect)
            y += line_height + settings.ARENA_BACKSTORY_LINE_GAP

        screen.blit(hint_surface, hint_rect)

        pygame.display.flip()
        clock.tick(settings.FPS)