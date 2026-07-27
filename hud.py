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


def draw_game_over(screen):
    """A dark overlay plus centered title/hint text. Fonts are created here
    each call rather than cached -- this screen isn't drawn every frame
    during normal play, only while dead, so it's not worth optimizing."""
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(settings.GAME_OVER_OVERLAY_ALPHA)
    screen.blit(overlay, (0, 0))

    center_x = settings.SCREEN_WIDTH // 2
    center_y = settings.SCREEN_HEIGHT // 2

    title_font = pygame.font.SysFont(None, settings.GAME_OVER_TITLE_FONT_SIZE)
    title_surface = title_font.render("YOU DIED", True, settings.GAME_OVER_TITLE_COLOR)
    title_rect = title_surface.get_rect(center=(center_x, center_y - 20))
    screen.blit(title_surface, title_rect)

    hint_font = pygame.font.SysFont(None, settings.GAME_OVER_HINT_FONT_SIZE)
    hint_surface = hint_font.render("Press R to restart", True, settings.HUD_TEXT_COLOR)
    hint_rect = hint_surface.get_rect(center=(center_x, center_y + 40))
    screen.blit(hint_surface, hint_rect)