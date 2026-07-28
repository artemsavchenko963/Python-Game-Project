"""
WeaponPickup: an item lying in a room that grants the player a new
weapon when walked over. Visually just a small green square for now --
same placeholder-shape approach as the player/enemy squares, so real
sprites can replace it later without touching any of this logic.

Each pickup holds an actual Weapon object (built with its real stats when
the pickup is placed) rather than just a name -- main.py hands that exact
object to player.add_weapon() on collection, no separate lookup needed.
"""

import pygame

import settings


class WeaponPickup:
    def __init__(self, center, weapon):
        self.weapon = weapon
        self.rect = pygame.Rect(0, 0, settings.PICKUP_SIZE, settings.PICKUP_SIZE)
        self.rect.center = center

    def draw(self, screen, camera_x, camera_y):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, settings.PICKUP_COLOR, screen_rect)
        pygame.draw.rect(screen, settings.PICKUP_BORDER_COLOR, screen_rect, 3)