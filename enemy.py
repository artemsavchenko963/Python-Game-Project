"""
Enemy: a colored square with health that bullets can damage/destroy, and
now chases the player directly. Movement uses the same axis-separated
wall-collision technique as Player.handle_movement -- worth comparing the
two side by side.
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

    def update(self, dt, player, wall_rects):
        """Move straight toward the player, colliding with walls like the player does."""
        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.rect.x += direction.x * settings.ENEMY_SPEED * dt
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if direction.x > 0:
                    self.rect.right = wall_rect.left
                elif direction.x < 0:
                    self.rect.left = wall_rect.right

        self.rect.y += direction.y * settings.ENEMY_SPEED * dt
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if direction.y > 0:
                    self.rect.bottom = wall_rect.top
                elif direction.y < 0:
                    self.rect.top = wall_rect.bottom

    def draw(self, screen, camera_x, camera_y):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, settings.ENEMY_COLOR, screen_rect)