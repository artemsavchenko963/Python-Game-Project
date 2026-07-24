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

        # Which way the player is currently facing/aiming, as a unit
        # vector (length 1). Defaults to facing right. This will be the
        # direction projectiles travel once we add shooting next step.
        self.aim_dir = pygame.Vector2(1, 0)

        # Counts down to 0; the player may fire again once it reaches 0.
        # Starts at 0 so you can fire immediately on the very first frame.
        self.fire_cooldown = 0.0

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

    def handle_aim(self, camera_x, camera_y):
        """Point aim_dir from the player's on-screen position toward the mouse."""
        screen_x = self.rect.centerx - camera_x
        screen_y = self.rect.centery - camera_y
        mouse_x, mouse_y = pygame.mouse.get_pos()

        direction = pygame.Vector2(mouse_x - screen_x, mouse_y - screen_y)
        # Guard against the zero-length vector you'd get if the mouse were
        # exactly on top of the player -- normalize() crashes on that.
        if direction.length_squared() > 0:
            self.aim_dir = direction.normalize()

    def tick_cooldown(self, dt):
        """Count the fire cooldown down toward 0. Call this once per frame."""
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

    def can_fire(self):
        return self.fire_cooldown <= 0

    def reset_fire_cooldown(self):
        """Call this every time a shot is actually fired."""
        self.fire_cooldown = settings.FIRE_INTERVAL

    def draw(self, screen, camera_x, camera_y):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, settings.PLAYER_COLOR, screen_rect)

        # A short line from the player's center toward the aim direction --
        # a stand-in for "the gun" until we have real weapon sprites.
        start = pygame.Vector2(screen_rect.center)
        end = start + self.aim_dir * settings.AIM_INDICATOR_LENGTH
        pygame.draw.line(screen, settings.AIM_INDICATOR_COLOR, start, end, 4)