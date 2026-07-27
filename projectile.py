"""
Projectile: a single bullet fired by the player. Travels in a straight
line at a fixed speed until main.py decides it hit a wall or left the
room, and removes it from the active list.

Position is stored as a pygame.Vector2 (which allows fractional/float
values) rather than a pygame.Rect (which only stores whole pixels) --
that matters here because a slow-ish, precise-feeling bullet needs
smooth sub-pixel movement, not the same integer rounding we accepted for
the player square.

Speed and damage are passed in rather than read from settings directly
(step 19) -- different weapons fire projectiles with different stats, so
the projectile just carries whatever numbers it was given, with no idea
which weapon made it.
"""

import pygame

import settings


class Projectile:
    def __init__(self, world_pos, direction, speed, damage):
        self.pos = pygame.Vector2(world_pos)
        self.velocity = direction * speed
        self.damage = damage

    def update(self, dt):
        self.pos += self.velocity * dt

    def get_rect(self):
        """A small square around the projectile's position, for collision checks."""
        r = settings.PROJECTILE_RADIUS
        return pygame.Rect(self.pos.x - r, self.pos.y - r, r * 2, r * 2)

    def draw(self, screen, camera_x, camera_y):
        screen_pos = (self.pos.x - camera_x, self.pos.y - camera_y)
        pygame.draw.circle(screen, settings.PROJECTILE_COLOR, screen_pos, settings.PROJECTILE_RADIUS)