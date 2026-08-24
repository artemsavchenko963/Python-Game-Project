"""
HUD (heads-up display): draws on-screen UI that isn't part of the game
world -- starting with the player's health bar in the top-left corner.

This is the first thing we've drawn that does NOT subtract the camera.
Everything else so far (player, room, enemies, projectiles) lives in
world coordinates and needs world_position - camera to land in the right
screen spot. The health bar has no world position at all -- it's always
"20 pixels from the corner of the window," full stop -- so it's drawn
directly in screen coordinates.
"""

import pygame

import settings


def draw_health_bar(screen, player):
    x = settings.HUD_MARGIN
    y = settings.HUD_MARGIN
    width = settings.HEALTH_BAR_WIDTH
    height = settings.HEALTH_BAR_HEIGHT

    background_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, settings.HEALTH_BAR_BG_COLOR, background_rect)

    health_fraction = player.health / player.max_health
    fill_rect = pygame.Rect(x, y, int(width * health_fraction), height)
    pygame.draw.rect(screen, settings.HEALTH_BAR_FILL_COLOR, fill_rect)

    # Border drawn last, on top, so it frames both the background and the
    # fill cleanly regardless of how much health is left.
    pygame.draw.rect(screen, settings.HEALTH_BAR_BORDER_COLOR, background_rect, settings.HEALTH_BAR_BORDER_WIDTH)


def draw_weapon_label(screen, player):
    """Shows which weapon is currently equipped, just below the health bar."""
    font = pygame.font.SysFont(None, settings.WEAPON_LABEL_FONT_SIZE)
    text = f"Weapon: {player.equipped_weapon.name}  (press 1 / 2)"
    surface = font.render(text, True, settings.HUD_TEXT_COLOR)
    x = settings.HUD_MARGIN
    y = settings.HUD_MARGIN + settings.HEALTH_BAR_HEIGHT + 8
    screen.blit(surface, (x, y))


def draw_bases_label(screen, bases_remaining, total_bases):
    """Step 26d: shows how many bases are still standing, just below the
    weapon label. A base counts as "remaining" until its guardian AND
    every one of its regular enemies are dead."""
    font = pygame.font.SysFont(None, settings.BASES_LABEL_FONT_SIZE)
    text = f"Bases: {bases_remaining}/{total_bases}"
    surface = font.render(text, True, settings.HUD_TEXT_COLOR)
    x = settings.HUD_MARGIN
    y = settings.HUD_MARGIN + settings.HEALTH_BAR_HEIGHT + 8 + settings.WEAPON_LABEL_FONT_SIZE + 8
    screen.blit(surface, (x, y))


def draw_game_over(screen):
    """A dark overlay plus centered title/hint text. Fonts are created here
    each call rather than cached -- this screen isn't drawn every frame
    during normal play, only while dead, so it's not worth optimizing."""
    # Sized off the destination surface itself (not the settings screen
    # size) since step 22 draws everything onto a smaller internal
    # surface before it gets scaled up to the real window.
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(settings.GAME_OVER_OVERLAY_ALPHA)
    screen.blit(overlay, (0, 0))

    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2

    title_font = pygame.font.SysFont(None, settings.GAME_OVER_TITLE_FONT_SIZE)
    title_surface = title_font.render("YOU DIED", True, settings.GAME_OVER_TITLE_COLOR)
    title_rect = title_surface.get_rect(center=(center_x, center_y - 20))
    screen.blit(title_surface, title_rect)

    hint_font = pygame.font.SysFont(None, settings.GAME_OVER_HINT_FONT_SIZE)
    hint_surface = hint_font.render("Press R to restart", True, settings.HUD_TEXT_COLOR)
    hint_rect = hint_surface.get_rect(center=(center_x, center_y + 40))
    screen.blit(hint_surface, hint_rect)


def get_pause_button_rect(screen):
    """Where the pause button sits, in real window coordinates. A
    separate function (rather than computing this inline in
    draw_pause_button) so main.py can call the exact same math to test
    mouse clicks against it, without waiting for a draw to happen first."""
    size = settings.PAUSE_BUTTON_SIZE
    margin = settings.PAUSE_BUTTON_MARGIN
    x = screen.get_width() - margin - size
    y = margin
    return pygame.Rect(x, y, size, size)


def draw_pause_button(screen):
    """A small square button in the top-right corner, drawn directly on
    the real window -- not on the zoomed internal game surface -- so it
    stays a fixed, crisp size no matter what ZOOM is set to."""
    rect = get_pause_button_rect(screen)
    pygame.draw.rect(screen, settings.PAUSE_BUTTON_COLOR, rect)
    pygame.draw.rect(screen, settings.HEALTH_BAR_BORDER_COLOR, rect, 2)

    # Two vertical bars -- the universal "pause" icon.
    bar_width = max(2, rect.width // 6)
    bar_height = rect.height - 16
    gap = rect.width // 5
    bar_top = rect.top + 8
    left_bar_x = rect.centerx - gap // 2 - bar_width
    right_bar_x = rect.centerx + gap // 2
    pygame.draw.rect(screen, settings.PAUSE_BUTTON_BAR_COLOR, (left_bar_x, bar_top, bar_width, bar_height))
    pygame.draw.rect(screen, settings.PAUSE_BUTTON_BAR_COLOR, (right_bar_x, bar_top, bar_width, bar_height))


def get_leave_button_rect(screen):
    """Same idea as get_pause_button_rect: main.py needs this exact rect
    to test clicks, so it lives in its own function rather than only
    inside draw_pause_overlay."""
    rect = pygame.Rect(0, 0, settings.PAUSE_LEAVE_BUTTON_WIDTH, settings.PAUSE_LEAVE_BUTTON_HEIGHT)
    rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 30)
    return rect


def draw_pause_overlay(screen):
    """Dark overlay, a "PAUSED" title, and a single Leave button. Drawn
    directly on the real window, same reasoning as the pause button."""
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(settings.PAUSE_OVERLAY_ALPHA)
    screen.blit(overlay, (0, 0))

    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2

    title_font = pygame.font.SysFont(None, settings.PAUSE_TITLE_FONT_SIZE)
    title_surface = title_font.render("PAUSED", True, settings.HUD_TEXT_COLOR)
    title_rect = title_surface.get_rect(center=(center_x, center_y - 60))
    screen.blit(title_surface, title_rect)

    button_rect = get_leave_button_rect(screen)
    pygame.draw.rect(screen, settings.PAUSE_LEAVE_BUTTON_COLOR, button_rect)
    pygame.draw.rect(screen, settings.HEALTH_BAR_BORDER_COLOR, button_rect, 2)

    button_font = pygame.font.SysFont(None, settings.PAUSE_LEAVE_BUTTON_FONT_SIZE)
    button_text = button_font.render("Leave", True, settings.PAUSE_LEAVE_BUTTON_TEXT_COLOR)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)