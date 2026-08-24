"""
Enemy: a colored square with health that bullets can damage/destroy.

Step 26a: two flavors now exist, both built from this one class:

- Regular enemies (is_guardian=False): chase the player, but only once
  the player gets within settings.AGGRO_RADIUS -- outside that range
  they just stand still. This is what lets you approach a base
  carefully instead of every enemy on the map swarming you at once.
- Base guardians (is_guardian=True): bigger, far tankier, hit harder,
  and NEVER move at all -- being stationary is what makes a "base" feel
  like an actual structure to storm rather than just another wandering
  monster.

Movement (for non-guardians) uses the same axis-separated wall-collision
technique as Player.handle_movement -- worth comparing the two side by
side.

Step 27: guardians now shoot. update() returns None most frames, but for
a guardian that just fired, it returns a brand new Projectile -- main.py
is what actually appends that into its own enemy_projectiles list and
moves/collides it each frame, same division of responsibility as the
player's own projectiles (Enemy/Player never own a projectile list
themselves, main.py does).
"""

import pygame

import settings
from projectile import Projectile


class Enemy:
    def __init__(self, center, is_guardian=False):
        self.is_guardian = is_guardian

        size = settings.GUARDIAN_SIZE if is_guardian else settings.ENEMY_SIZE
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = center

        # Same reasoning as Player.pos -- see the note in
        # Player.handle_movement for why rect.x/y alone isn't enough.
        self.pos = pygame.Vector2(self.rect.topleft)

        self.max_health = settings.GUARDIAN_MAX_HEALTH if is_guardian else settings.ENEMY_MAX_HEALTH
        self.health = self.max_health

        # Read once here instead of main.py using one fixed constant for
        # every enemy -- a guardian hits noticeably harder than a regular
        # one on touch.
        self.touch_damage = settings.GUARDIAN_TOUCH_DAMAGE if is_guardian else settings.ENEMY_TOUCH_DAMAGE

        # Only ever used by guardians (step 27) -- counts down to 0,
        # same shape as Player.fire_cooldown. Starts at 0 so a guardian's
        # first shot isn't delayed.
        self.fire_cooldown = 0.0

    def take_damage(self, amount):
        """Reduce health by amount. Returns True if this kills the enemy."""
        self.health -= amount
        return self.health <= 0

    def update(self, dt, player, wall_rects):
        """Move straight toward the player, colliding with walls like the
        player does -- unless this is a guardian (never moves, full
        stop, but may fire instead -- see _guardian_shoot), or the
        player is still outside AGGRO_RADIUS (stands still until
        approached).

        Returns None most of the time. The one exception: a guardian
        that just fired returns a brand new Projectile aimed at the
        player -- main.py is responsible for actually tracking/moving/
        drawing it from there, same as it already does for the player's
        own projectiles.
        """
        if self.is_guardian:
            return self._guardian_shoot(dt, player)

        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        distance = direction.length()
        if distance > settings.AGGRO_RADIUS:
            return None
        if distance > 0:
            direction = direction.normalize()

        self.pos.x += direction.x * settings.ENEMY_SPEED * dt
        self.rect.x = round(self.pos.x)
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if direction.x > 0:
                    self.rect.right = wall_rect.left
                elif direction.x < 0:
                    self.rect.left = wall_rect.right
                self.pos.x = self.rect.x

        self.pos.y += direction.y * settings.ENEMY_SPEED * dt
        self.rect.y = round(self.pos.y)
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if direction.y > 0:
                    self.rect.bottom = wall_rect.top
                elif direction.y < 0:
                    self.rect.top = wall_rect.bottom
                self.pos.y = self.rect.y

        return None

    def _guardian_shoot(self, dt, player):
        """Guardians never move, but periodically fire a projectile
        straight at the player once they're within GUARDIAN_SHOOT_RANGE.
        Returns the new Projectile, or None if it's not time to fire yet
        (or the player is out of range)."""
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        distance = direction.length()
        if distance > settings.GUARDIAN_SHOOT_RANGE or self.fire_cooldown > 0:
            return None

        self.fire_cooldown = settings.GUARDIAN_FIRE_INTERVAL
        if distance > 0:
            direction = direction.normalize()
        return Projectile(
            self.rect.center, direction, settings.GUARDIAN_PROJECTILE_SPEED, settings.GUARDIAN_PROJECTILE_DAMAGE
        )

    def draw(self, screen, camera_x, camera_y):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        color = settings.GUARDIAN_COLOR if self.is_guardian else settings.ENEMY_COLOR
        pygame.draw.rect(screen, color, screen_rect)