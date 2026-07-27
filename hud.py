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