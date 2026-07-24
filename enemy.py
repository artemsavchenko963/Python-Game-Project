"""
Enemy: a stationary colored square with health. Bullets can now damage
and destroy it (main.py handles the actual collision check; this class
just knows how to apply damage to itself). Movement/AI is still a later
step.
"""

import pygame

import settings


class Enemy:
    def __init__(self, center):
        self.rect = pygame.Rect(0, 0, settings.ENEMY_SIZE, settings.ENEMY_SIZE)
        self.rect.center = center

        self.max_health = settings.ENEMY_MAX_HEALTH
        self.health = self.max_health

    def take_damage(self, amount):
        """Reduce health by amount. Returns True if this kills the enemy."""
        self.health -= amount
        return self.health <= 0

    def draw(self, screen, camera_x, camera_y):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, settings.ENEMY_COLOR, screen_rect)