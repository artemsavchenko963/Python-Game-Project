"""
Player: holds the player's rect (world position + size) and knows how to
move itself and draw itself.

Pulled out of main.py so that main.py doesn't need to know HOW movement
math works -- it just creates a Player and calls handle_movement()/draw()
on it. This is also where health, inventory, and XP will live once we get
to those steps -- this class is the natural home for "everything about
the player" going forward.
"""

import pygame

import settings


class Player:
    def __init__(self, center):
        self.rect = pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE)
        self.rect.center = center

    def handle_movement(self, dt, keys, bounds_rect):
        """Read WASD state, move, and stay inside bounds_rect (e.g. the room's floor area)."""
        dx = 0
        dy = 0
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1

        self.rect.x += dx * settings.PLAYER_SPEED * dt
        self.rect.y += dy * settings.PLAYER_SPEED * dt
        self.rect.clamp_ip(bounds_rect)

    def draw(self, screen, camera_x, camera_y):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, settings.PLAYER_COLOR, screen_rect)