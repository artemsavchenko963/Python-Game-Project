"""
Player: holds the player's rect (world position + size) and knows how to
move itself (with real wall collision) and draw itself.
"""

import pygame

import settings


class Player:
    def __init__(self, center):
        self.rect = pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE)
        self.rect.center = center

    def handle_movement(self, dt, keys, wall_rects):
        """Read WASD state and move, sliding along any wall_rects we bump into."""
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

        # Move X and Y as two separate steps (rather than one diagonal
        # step), each followed by its own collision check. This is what
        # lets you slide smoothly along a wall when moving into it at an
        # angle, instead of getting fully stopped.
        self.rect.x += dx * settings.PLAYER_SPEED * dt
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if dx > 0:
                    self.rect.right = wall_rect.left
                elif dx < 0:
                    self.rect.left = wall_rect.right

        self.rect.y += dy * settings.PLAYER_SPEED * dt
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if dy > 0:
                    self.rect.bottom = wall_rect.top
                elif dy < 0:
                    self.rect.top = wall_rect.bottom

    def draw(self, screen, camera_x, camera_y):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, settings.PLAYER_COLOR, screen_rect)