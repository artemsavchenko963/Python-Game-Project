"""
Enemy: for now, just a stationary colored square with health. No
movement, no AI, and nothing can damage it yet -- this step is only about
getting an enemy object that exists in the world and draws itself. Chasing
behavior and taking bullet damage are the next two steps.
"""

import pygame

import settings


class Enemy:
    def __init__(self, center):
        self.rect = pygame.Rect(0, 0, settings.ENEMY_SIZE, settings.ENEMY_SIZE)
        self.rect.center = center

        self.max_health = settings.ENEMY_MAX_HEALTH
        self.health = self.max_health

    def draw(self, screen, camera_x, camera_y):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, settings.ENEMY_COLOR, screen_rect)